"""
Konfigurasi workflow untuk setiap mekanisme pencairan.
Mendefinisikan fase, dokumen wajib/opsional, dan validasi per fase.
"""

# ============================================================================
# WORKFLOW UP (UANG PERSEDIAAN)
# ============================================================================

UP_WORKFLOW = {
    "kode": "UP",
    "nama": "Uang Persediaan",
    "deskripsi": "Pencairan dana untuk belanja operasional ≤ Rp 50 juta",
    "batas_maksimal": 50000000,
    "icon": "📗",
    "color": "#27ae60",
    
    "fase": {
        1: {
            "nama": "Inisiasi & SK",
            "deskripsi": "Persiapan awal dan penerbitan SK/Dasar Hukum",
            "icon": "📋",
            "dokumen": [
                {"kode": "ND_REQ", "nama": "Nota Dinas Permintaan", "kategori": "wajib", "template": "nota_dinas_permintaan.docx"},
                {"kode": "SK_KPA", "nama": "SK KPA / Surat Tugas", "kategori": "wajib", "template": "sk_kpa.docx"},
                {"kode": "RAB", "nama": "Rencana Anggaran Biaya", "kategori": "wajib", "template": "rab.xlsx"},
                {"kode": "TOR", "nama": "TOR/KAK (jika kegiatan)", "kategori": "opsional", "template": "tor_kak.docx"},
                {"kode": "UND", "nama": "Undangan (jika rapat/workshop)", "kategori": "opsional", "template": "undangan.docx"},
            ],
            "validasi": [
                {"field": "nomor_dasar", "rule": "required", "message": "Nomor SK/Surat Tugas wajib diisi"},
                {"field": "tanggal_dasar", "rule": "required", "message": "Tanggal SK wajib diisi"},
                {"field": "estimasi_biaya", "rule": "max:50000000", "message": "Estimasi biaya UP maksimal Rp 50 juta"},
            ],
            "next_condition": "Semua dokumen wajib sudah dibuat dan SK sudah ditandatangani",
            "syarat_lanjut": ["SK KPA diterbitkan", "Estimasi biaya ≤ Rp 50 juta", "Kegiatan jelas"]
        },
        
        2: {
            "nama": "Pencairan Uang Muka",
            "deskripsi": "Pengajuan dan pencairan uang muka dari UP",
            "icon": "💵",
            "dokumen": [
                {"kode": "KUIT_UM", "nama": "Kuitansi Uang Muka", "kategori": "wajib", "template": "kuitansi_uang_muka_spm_lainnya.docx"},
                {"kode": "BST_UM", "nama": "Bukti Serah Terima Uang", "kategori": "wajib", "template": "bukti_serah_terima_um.docx"},
            ],
            "validasi": [
                {"field": "uang_muka", "rule": "required", "message": "Jumlah uang muka wajib diisi"},
                {"field": "uang_muka", "rule": "max_percent:70", "message": "Uang muka maksimal 70% dari estimasi"},
                {"field": "penerima_nama", "rule": "required", "message": "Nama penerima wajib diisi"},
            ],
            "catatan": "Uang muka maksimal 70% dari estimasi biaya",
            "next_condition": "Uang muka sudah dicairkan dan diterima penerima",
            "syarat_lanjut": ["Uang muka diterbitkan", "Penerima menandatangani kuitansi UM"]
        },
        
        3: {
            "nama": "Pelaksanaan Kegiatan",
            "deskripsi": "Kegiatan dilaksanakan dan bukti dikumpulkan",
            "icon": "🔨",
            "dokumen": [
                {"kode": "DH", "nama": "Daftar Hadir", "kategori": "wajib", "template": "daftar_hadir.docx"},
                {"kode": "DOK_FOTO", "nama": "Dokumentasi Foto", "kategori": "wajib", "template": None},
                {"kode": "NOTULEN", "nama": "Notulen Rapat", "kategori": "opsional", "template": "notulen.docx"},
                {"kode": "LAP_KEG", "nama": "Laporan Kegiatan", "kategori": "opsional", "template": "laporan_kegiatan.docx"},
                {"kode": "NOTA_BLJ", "nama": "Nota/Faktur Belanja", "kategori": "upload", "template": None},
                {"kode": "KWIT_TOKO", "nama": "Kwitansi Toko", "kategori": "upload", "template": None},
            ],
            "validasi": [
                {"field": "dokumen_dh", "rule": "required", "message": "Daftar hadir wajib ada"},
                {"field": "dokumen_foto", "rule": "required", "message": "Dokumentasi foto wajib ada"},
            ],
            "next_condition": "Kegiatan selesai dan semua bukti terkumpul",
            "syarat_lanjut": ["Kegiatan 100% selesai", "Daftar hadir terkumpul", "Bukti pengeluaran lengkap"]
        },
        
        4: {
            "nama": "Pertanggungjawaban",
            "deskripsi": "Membuat dokumen pertanggungjawaban dan perhitungan tambah/kurang",
            "icon": "📊",
            "dokumen": [
                {"kode": "KUIT_RAMP", "nama": "Kuitansi Rampung", "kategori": "wajib", "template": "kuitansi_rampung_spm_lainnya.docx"},
                {"kode": "HITUNG_TK", "nama": "Perhitungan Tambah/Kurang", "kategori": "wajib", "template": "perhitungan_tambah_kurang.xlsx"},
                {"kode": "REKAP_BKT", "nama": "Rekap Bukti Pengeluaran", "kategori": "wajib", "template": "rekap_bukti_pengeluaran.xlsx"},
                {"kode": "LPJ", "nama": "LPJ Kegiatan", "kategori": "opsional", "template": "lpj.docx"},
            ],
            "kalkulasi": {
                "formula": "selisih = realisasi - uang_muka",
                "hasil_positif": {"label": "KURANG BAYAR", "aksi": "Ajukan pembayaran tambahan", "color": "#e74c3c"},
                "hasil_negatif": {"label": "LEBIH BAYAR", "aksi": "Kembalikan kelebihan ke kas", "color": "#f39c12"},
                "hasil_nol": {"label": "PAS / NIHIL", "aksi": "Lanjut ke SPBY", "color": "#27ae60"},
            },
            "validasi": [
                {"field": "realisasi", "rule": "required", "message": "Total realisasi wajib diisi"},
                {"field": "dokumen_kuit_ramp", "rule": "required", "message": "Kuitansi rampung wajib dibuat"},
            ],
            "next_condition": "Perhitungan selesai dan dokumen pertanggungjawaban lengkap",
            "syarat_lanjut": ["Realisasi biaya dihitung", "Perhitungan tambah/kurang selesai", "Kuitansi rampung dibuat"]
        },
        
        5: {
            "nama": "SPBY & Penyelesaian",
            "deskripsi": "Pembuatan SPBY dan arsip dokumen final",
            "icon": "✅",
            "dokumen": [
                {"kode": "SPBY", "nama": "Surat Pernyataan Tanggung Jawab Belanja", "kategori": "wajib", "template": "spby.docx"},
                {"kode": "REKAP_FINAL", "nama": "Rekap Final Transaksi", "kategori": "wajib", "template": "rekap_final.xlsx"},
            ],
            "aksi_tambahan": [
                "Upload ke SAKTI/Aplikasi Keuangan",
                "Arsip ke folder tahun berjalan",
                "Update sisa UP tersedia",
            ],
            "validasi": [
                {"field": "dokumen_spby", "rule": "required", "message": "SPBY wajib dibuat"},
                {"field": "dokumen_spby", "rule": "signed", "message": "SPBY wajib sudah ditandatangani"},
            ],
            "next_condition": "Transaksi selesai dan semua dokumen diarsipkan",
            "syarat_lanjut": ["SPBY dibuat dan ditandatangani", "Semua dokumen diarsipkan"]
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
    "icon": "📙",
    "color": "#f39c12",
    
    "fase": {
        1: {
            "nama": "Pengajuan TUP",
            "deskripsi": "Mengajukan kebutuhan TUP ke KPPN",
            "icon": "📝",
            "dokumen": [
                {"kode": "SP_TUP", "nama": "Surat Permohonan TUP", "kategori": "wajib", "template": "surat_permohonan_tup.docx"},
                {"kode": "RINCI_TUP", "nama": "Rincian Penggunaan TUP", "kategori": "wajib", "template": "rincian_tup.xlsx"},
                {"kode": "REK_KORAN", "nama": "Rekening Koran/Saldo UP", "kategori": "wajib", "template": None},
            ],
            "syarat": [
                "UP yang ada tidak mencukupi",
                "Kebutuhan mendesak dan tidak dapat ditunda",
                "Rincian penggunaan jelas dan terukur",
            ],
            "validasi": [
                {"field": "estimasi_biaya", "rule": "required", "message": "Nilai TUP yang diajukan wajib diisi"},
            ],
            "next_condition": "Surat permohonan diajukan ke KPPN",
            "syarat_lanjut": ["Surat permohonan disiapkan", "Rincian penggunaan detail"]
        },
        
        2: {
            "nama": "Persetujuan KPPN",
            "deskripsi": "Menunggu persetujuan TUP dari Kepala KPPN",
            "icon": "⏳",
            "dokumen": [
                {"kode": "APPR_TUP", "nama": "Surat Persetujuan TUP dari KPPN", "kategori": "upload", "template": None},
            ],
            "catatan": "Proses persetujuan biasanya 1-3 hari kerja",
            "validasi": [
                {"field": "dokumen_appr_tup", "rule": "required", "message": "Surat persetujuan dari KPPN wajib ada"},
            ],
            "next_condition": "TUP disetujui oleh Kepala KPPN",
            "syarat_lanjut": ["Surat persetujuan dari KPPN diterima"]
        },
        
        3: {
            "nama": "Pencairan TUP",
            "deskripsi": "Dana TUP dicairkan ke rekening bendahara",
            "icon": "💰",
            "dokumen": [
                {"kode": "SP2D_TUP", "nama": "SP2D TUP", "kategori": "upload", "template": None},
            ],
            "validasi": [
                {"field": "dokumen_sp2d_tup", "rule": "required", "message": "SP2D TUP wajib ada"},
            ],
            "catatan": "Catat tanggal SP2D untuk menghitung batas 1 bulan",
            "next_condition": "Dana TUP sudah masuk ke rekening bendahara",
            "syarat_lanjut": ["SP2D diterima", "Dana TUP masuk ke rekening"]
        },
        
        4: {
            "nama": "Penggunaan TUP (Max 30 Hari)",
            "deskripsi": "Menggunakan TUP sesuai rincian yang diajukan - WAJIB SELESAI 1 BULAN",
            "icon": "🔨",
            "dokumen": [
                {"kode": "DH", "nama": "Daftar Hadir", "kategori": "wajib", "template": "daftar_hadir.docx"},
                {"kode": "DOK_FOTO", "nama": "Dokumentasi Foto", "kategori": "wajib", "template": None},
                {"kode": "NOTA_BLJ", "nama": "Nota/Faktur Belanja", "kategori": "upload", "template": None},
            ],
            "catatan": "⚠️ WAJIB selesai dalam 1 BULAN sejak SP2D diterbitkan",
            "countdown": True,
            "max_hari": 30,
            "validasi": [
                {"field": "penggunaan", "rule": "sesuai_rincian", "message": "Penggunaan harus sesuai rincian yang diajukan"},
            ],
            "next_condition": "Semua dana TUP sudah digunakan atau batas waktu tercapai",
            "syarat_lanjut": ["Penggunaan 100% sesuai rincian", "Bukti lengkap terkumpul"]
        },
        
        5: {
            "nama": "Pertanggungjawaban TUP",
            "deskripsi": "Mempertanggungjawabkan penggunaan TUP, sisa dikembalikan",
            "icon": "✅",
            "dokumen": [
                {"kode": "SPBY_TUP", "nama": "SPBY TUP", "kategori": "wajib", "template": "spby_tup.docx"},
                {"kode": "REKAP_TUP", "nama": "Rekap Penggunaan TUP", "kategori": "wajib", "template": "rekap_tup.xlsx"},
                {"kode": "SSBP", "nama": "SSBP Pengembalian (jika ada sisa)", "kategori": "kondisional", "template": "ssbp.xlsx"},
                {"kode": "BUKTI_SETOR", "nama": "Bukti Setor Pengembalian", "kategori": "kondisional", "template": None},
            ],
            "kalkulasi": {
                "formula": "sisa = nilai_tup - total_penggunaan",
                "jika_sisa": "Wajib setor kembali ke kas negara via SSBP",
            },
            "validasi": [
                {"field": "dokumen_spby_tup", "rule": "required", "message": "SPBY TUP wajib dibuat"},
                {"field": "sisa_tup", "rule": "dikembalikan", "message": "Sisa TUP wajib disetor kembali"},
            ],
            "next_condition": "TUP nihil atau sisa sudah dikembalikan ke kas negara",
            "syarat_lanjut": ["SPBY TUP dibuat dan ditandatangani", "Sisa TUP dikembalikan (jika ada)"]
        }
    }
}

# ============================================================================
# WORKFLOW LS (LANGSUNG)
# ============================================================================

LS_WORKFLOW = {
    "kode": "LS",
    "nama": "Pembayaran Langsung",
    "deskripsi": "Pembayaran langsung ke penyedia via KPPN untuk kontrak/SPK",
    "icon": "📘",
    "color": "#3498db",
    
    "fase": {
        1: {
            "nama": "Kontrak/SPK",
            "deskripsi": "Penandatanganan kontrak dengan penyedia barang/jasa",
            "icon": "📑",
            "dokumen": [
                {"kode": "SPK", "nama": "Surat Perjanjian Kerja", "kategori": "wajib", "template": "spk.docx"},
                {"kode": "SSUK", "nama": "Syarat-Syarat Umum Kontrak", "kategori": "wajib", "template": "ssuk.docx"},
                {"kode": "SSKK", "nama": "Syarat-Syarat Khusus Kontrak", "kategori": "wajib", "template": "sskk.docx"},
                {"kode": "SPMK", "nama": "Surat Perintah Mulai Kerja", "kategori": "wajib", "template": "spmk.docx"},
                {"kode": "JAM_PELAKS", "nama": "Jaminan Pelaksanaan", "kategori": "kondisional", "template": None},
                {"kode": "JAM_UM", "nama": "Jaminan Uang Muka (jika ada UM kontrak)", "kategori": "kondisional", "template": None},
            ],
            "validasi": [
                {"field": "nomor_kontrak", "rule": "required", "message": "Nomor kontrak/SPK wajib diisi"},
                {"field": "nilai_kontrak", "rule": "required", "message": "Nilai kontrak wajib diisi"},
                {"field": "penyedia_id", "rule": "required", "message": "Penyedia wajib dipilih"},
            ],
            "next_condition": "Kontrak ditandatangani kedua belah pihak",
            "syarat_lanjut": ["Kontrak ditandatangani", "Penyedia ditetapkan", "SPMK diterbitkan"]
        },
        
        2: {
            "nama": "Pelaksanaan Pekerjaan",
            "deskripsi": "Penyedia melaksanakan pekerjaan sesuai kontrak",
            "icon": "🔧",
            "dokumen": [
                {"kode": "LAP_PROG", "nama": "Laporan Progress Pekerjaan", "kategori": "wajib", "template": "laporan_progress.docx"},
                {"kode": "BA_MC", "nama": "BA Monthly Certificate (jika termin)", "kategori": "kondisional", "template": "ba_mc.docx"},
                {"kode": "MONEV", "nama": "Laporan Monitoring & Evaluasi", "kategori": "opsional", "template": "monev.docx"},
            ],
            "validasi": [
                {"field": "progress", "rule": "updated", "message": "Progress pekerjaan harus di-update"},
            ],
            "next_condition": "Pekerjaan selesai 100%",
            "syarat_lanjut": ["Pekerjaan 100% selesai", "Progress report lengkap"]
        },
        
        3: {
            "nama": "Serah Terima",
            "deskripsi": "Pemeriksaan dan serah terima hasil pekerjaan",
            "icon": "🤝",
            "dokumen": [
                {"kode": "BA_PMR", "nama": "BA Pemeriksaan Pekerjaan", "kategori": "wajib", "template": "ba_pemeriksaan.docx"},
                {"kode": "BAST", "nama": "Berita Acara Serah Terima", "kategori": "wajib", "template": "bast.docx"},
                {"kode": "BA_PHO", "nama": "BA Provisional Hand Over (PHO)", "kategori": "wajib", "template": "ba_pho.docx"},
                {"kode": "BA_FHO", "nama": "BA Final Hand Over (konstruksi)", "kategori": "kondisional", "template": "ba_fho.docx"},
            ],
            "validasi": [
                {"field": "dokumen_bast", "rule": "required", "message": "BAST wajib dibuat"},
                {"field": "dokumen_bast", "rule": "signed", "message": "BAST wajib ditandatangani kedua pihak"},
            ],
            "next_condition": "BAST ditandatangani",
            "syarat_lanjut": ["BAST ditandatangani kedua pihak", "Pekerjaan diterima"]
        },
        
        4: {
            "nama": "Pengajuan Tagihan SPM",
            "deskripsi": "Penyedia mengajukan tagihan, PPK memproses SPP/SPM",
            "icon": "📄",
            "dokumen": [
                {"kode": "INVOICE", "nama": "Invoice/Tagihan dari Penyedia", "kategori": "upload", "template": None},
                {"kode": "FAKTUR_PJK", "nama": "Faktur Pajak", "kategori": "upload", "template": None},
                {"kode": "SPP_LS", "nama": "Surat Permintaan Pembayaran", "kategori": "wajib", "template": "spp_ls.docx"},
                {"kode": "SPM_LS", "nama": "Surat Perintah Membayar", "kategori": "wajib", "template": "spm_ls.docx"},
                {"kode": "KUIT_LS", "nama": "Kuitansi Pembayaran LS", "kategori": "wajib", "template": "kuitansi_ls.docx"},
                {"kode": "SSP_PPN", "nama": "SSP PPN", "kategori": "wajib", "template": "ssp.xlsx"},
                {"kode": "SSP_PPH", "nama": "SSP PPh", "kategori": "wajib", "template": "ssp.xlsx"},
            ],
            "kelengkapan": [
                "Resume Kontrak",
                "Ringkasan Kontrak", 
                "Copy SPK",
                "Copy BAST",
                "Faktur Pajak",
                "NPWP Penyedia",
                "Copy Rekening Penyedia",
            ],
            "validasi": [
                {"field": "dokumen_spm", "rule": "required", "message": "SPM wajib dibuat"},
                {"field": "pajak", "rule": "calculated", "message": "Pajak wajib dihitung"},
            ],
            "next_condition": "SPM diajukan ke KPPN",
            "syarat_lanjut": ["Invoice penyedia diterima", "SPM dibuat dan lengkap dokumen"]
        },
        
        5: {
            "nama": "SP2D & Penyelesaian",
            "deskripsi": "KPPN menerbitkan SP2D, dana masuk ke rekening penyedia",
            "icon": "✅",
            "dokumen": [
                {"kode": "SP2D_LS", "nama": "Surat Perintah Pencairan Dana", "kategori": "upload", "template": None},
                {"kode": "BUKTI_TRF", "nama": "Bukti Transfer ke Penyedia", "kategori": "upload", "template": None},
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
            "next_condition": "Transaksi selesai dan pembayaran diterima penyedia",
            "syarat_lanjut": ["SP2D diterima dari KPPN", "Dana transfer ke penyedia terkonfirmasi"]
        }
    }
}

# ============================================================================
# JENIS BELANJA
# ============================================================================

JENIS_BELANJA = [
    {"kode": "honorarium", "nama": "Honorarium", "icon": "💰", "akun_default": "5.2.1.01"},
    {"kode": "jamuan", "nama": "Jamuan Tamu / Konsumsi Rapat", "icon": "🍽️", "akun_default": "5.2.2.03"},
    {"kode": "perdin", "nama": "Perjalanan Dinas", "icon": "✈️", "akun_default": "5.2.4.01"},
    {"kode": "pjlp", "nama": "PJLP (Tenaga Kontrak)", "icon": "👷", "akun_default": "5.2.1.02"},
    {"kode": "atk", "nama": "Belanja ATK / Perlengkapan", "icon": "🛒", "akun_default": "5.2.2.01"},
    {"kode": "lainnya", "nama": "Belanja Lainnya", "icon": "📦", "akun_default": "5.2.2.99"},
]

# ============================================================================
# KONSTANTA
# ============================================================================

BATAS_UP_MAKSIMAL = 50000000  # Rp 50 juta
BATAS_TUP_HARI = 30  # 1 bulan untuk pertanggungjawaban TUP
PERSENTASE_UANG_MUKA_MAX = 70  # Maksimal 70% dari estimasi

# ============================================================================
# EXPORT
# ============================================================================

ALL_WORKFLOWS = {
    "UP": UP_WORKFLOW,
    "TUP": TUP_WORKFLOW,
    "LS": LS_WORKFLOW,
}

def get_workflow(mekanisme: str) -> dict:
    """Get workflow configuration by mekanisme"""
    return ALL_WORKFLOWS.get(mekanisme.upper())

def get_fase_config(mekanisme: str, fase: int) -> dict:
    """Get konfigurasi fase tertentu"""
    workflow = get_workflow(mekanisme)
    if workflow and fase in workflow.get("fase", {}):
        return workflow["fase"][fase]
    return {}

def get_dokumen_fase(mekanisme: str, fase: int) -> list:
    """Get daftar dokumen untuk fase tertentu"""
    fase_config = get_fase_config(mekanisme, fase)
    return fase_config.get("dokumen", [])
