# RANCANGAN PERUBAHAN ALUR KERJA
## Asisten PPK Offline v3.1

---

## DAFTAR ISI

1. [Ringkasan Perubahan](#1-ringkasan-perubahan)
2. [Penambahan Rancangan Kontrak](#2-penambahan-rancangan-kontrak)
3. [Pemisahan Alur LS Berdasarkan Nilai](#3-pemisahan-alur-ls-berdasarkan-nilai)
4. [Diagram Alur Baru](#4-diagram-alur-baru)
5. [Dokumen per Alur](#5-dokumen-per-alur)
6. [Implementasi Teknis](#6-implementasi-teknis)

---

## 1. RINGKASAN PERUBAHAN

### A. Penambahan Rancangan Kontrak di Tahap Persiapan

| Aspek | Sebelum | Sesudah |
|-------|---------|---------|
| Posisi | Tidak ada di tahap persiapan | Ditambahkan setelah HPS |
| Dokumen | - | Rancangan SPK / Surat Perjanjian |
| Tujuan | - | PPK menyiapkan draft kontrak sebelum dikirim ke PP |

### B. Pemisahan Alur LS Berdasarkan Nilai Pengadaan

| Kategori | Nilai | Alur |
|----------|-------|------|
| **LS Mikro** | ≤ Rp 10 juta | Bukti Pembelian / Kuitansi |
| **LS Kecil** | > Rp 10 juta s.d. Rp 50 juta | SPK Sederhana |
| **LS Standar** | > Rp 50 juta s.d. Rp 200 juta | SPK Lengkap |
| **Kontrak** | > Rp 200 juta | Surat Perjanjian |

---

## 2. PENAMBAHAN RANCANGAN KONTRAK

### 2.1 Posisi dalam Workflow

```
TAHAP PERSIAPAN (Baru):
┌─────────────────────────────────────────────────────────────────┐
│  1. Spesifikasi Teknis                                          │
│  2. Survey Harga (3 sumber)                                     │
│  3. HPS (Harga Perkiraan Sendiri)                               │
│  4. KAK (Kerangka Acuan Kerja)                                  │
│  5. ★ RANCANGAN KONTRAK (BARU) ★                                │
│     └─ Draft SPK / Surat Perjanjian                             │
│     └─ SSUK (Syarat-Syarat Umum Kontrak)                        │
│     └─ SSKK (Syarat-Syarat Khusus Kontrak)                      │
│  6. Nota Dinas ke Pejabat Pengadaan                             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Dokumen Rancangan Kontrak

#### A. Untuk Nilai ≤ 50 Juta (SPK Sederhana)

| Dokumen | Keterangan |
|---------|------------|
| **Rancangan SPK** | Draft Surat Perintah Kerja |
| **Daftar Kuantitas dan Harga** | Lampiran harga per item |

#### B. Untuk Nilai > 50 Juta (SPK Lengkap / Surat Perjanjian)

| Dokumen | Keterangan |
|---------|------------|
| **Rancangan SPK / Surat Perjanjian** | Draft kontrak utama |
| **SSUK** | Syarat-Syarat Umum Kontrak |
| **SSKK** | Syarat-Syarat Khusus Kontrak |
| **Daftar Kuantitas dan Harga** | Lampiran harga per item |
| **Spesifikasi Teknis** | Lampiran spesifikasi |
| **Gambar (jika ada)** | Untuk konstruksi |

### 2.3 Placeholder Baru untuk Rancangan Kontrak

```python
'rancangan_kontrak': {
    # Ketentuan Umum
    'lingkup_pekerjaan': 'Lingkup Pekerjaan',
    'jangka_waktu_pelaksanaan': 'Jangka Waktu Pelaksanaan',
    'tanggal_mulai_rencana': 'Tanggal Mulai (Rencana)',
    'tanggal_selesai_rencana': 'Tanggal Selesai (Rencana)',

    # Pembayaran
    'cara_pembayaran': 'Cara Pembayaran',  # Sekaligus/Termin
    'jumlah_termin': 'Jumlah Termin',
    'uang_muka_persen': 'Uang Muka (%)',
    'retensi_persen': 'Retensi (%)',

    # Jaminan
    'jaminan_pelaksanaan': 'Jaminan Pelaksanaan',
    'jaminan_pemeliharaan': 'Jaminan Pemeliharaan',
    'masa_pemeliharaan': 'Masa Pemeliharaan',

    # Denda & Sanksi
    'denda_keterlambatan': 'Denda Keterlambatan per Hari',
    'denda_maksimal': 'Denda Maksimal (%)',

    # Penyelesaian Perselisihan
    'penyelesaian_sengketa': 'Penyelesaian Perselisihan',
}
```

---

## 3. PEMISAHAN ALUR LS BERDASARKAN NILAI

### 3.1 Alur LS Mikro (≤ Rp 10 Juta)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALUR LS MIKRO (≤ 10 Juta)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PERSIAPAN           PELAKSANAAN           PEMBAYARAN           │
│  ──────────          ───────────           ──────────           │
│                                                                 │
│  ┌─────────┐         ┌─────────┐           ┌─────────┐          │
│  │Spesifi- │         │ Bukti   │           │Kuitansi │          │
│  │kasi     │────────▶│Pembelian│──────────▶│   +     │          │
│  │Teknis   │         │ /Nota   │           │SSP PPh  │          │
│  └─────────┘         └─────────┘           └─────────┘          │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────┐                                                    │
│  │  HPS    │  (Opsional untuk nilai < 10 juta)                  │
│  │Sederhana│                                                    │
│  └─────────┘                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

DOKUMEN YANG DIHASILKAN:
1. Spesifikasi Teknis (Sederhana)
2. HPS Sederhana (opsional)
3. Bukti Pembelian / Nota / Faktur
4. Kuitansi
5. SSP PPh (jika kena pajak)
```

### 3.2 Alur LS Kecil (> Rp 10 Juta s.d. Rp 50 Juta)

```
┌─────────────────────────────────────────────────────────────────┐
│               ALUR LS KECIL (10 - 50 Juta)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PERSIAPAN                                                      │
│  ──────────                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐           │
│  │Spesifi- │─▶│ Survey  │─▶│   HPS   │─▶│Rancangan │           │
│  │kasi     │  │  Harga  │  │         │  │   SPK    │           │
│  └─────────┘  └─────────┘  └─────────┘  └──────────┘           │
│                                              │                  │
│  ┌───────────────────────────────────────────┘                  │
│  ▼                                                              │
│  PEMILIHAN (Disederhanakan)                                     │
│  ──────────────────────────                                     │
│  ┌─────────────────────────────────────────┐                    │
│  │  Permintaan Penawaran ke Penyedia       │                    │
│  │  (Bisa langsung tanpa melalui PP)       │                    │
│  └─────────────────────────────────────────┘                    │
│                     │                                           │
│  ┌──────────────────┘                                           │
│  ▼                                                              │
│  KONTRAK & PELAKSANAAN                                          │
│  ─────────────────────                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │   SPK   │─▶│  SPMK   │─▶│  BAHP   │─▶│  BAST   │            │
│  │Sederhana│  │         │  │         │  │         │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│                                              │                  │
│  ┌───────────────────────────────────────────┘                  │
│  ▼                                                              │
│  PEMBAYARAN                                                     │
│  ──────────                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│  │Kuitansi │─▶│ SPP-LS  │─▶│SSP PPN  │                          │
│  │         │  │  DRPP   │  │SSP PPh  │                          │
│  └─────────┘  └─────────┘  └─────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

DOKUMEN YANG DIHASILKAN:
PERSIAPAN:
  1. Spesifikasi Teknis
  2. Survey Harga (3 sumber)
  3. HPS
  4. Rancangan SPK (BARU)

KONTRAK:
  5. SPK Sederhana (tanpa SSUK/SSKK)
  6. SPMK

SERAH TERIMA:
  7. BAHP
  8. BAST

PEMBAYARAN:
  9. Kuitansi
  10. SPP-LS
  11. DRPP
  12. SSP PPN (jika PKP)
  13. SSP PPh
```

### 3.3 Alur LS Standar (> Rp 50 Juta s.d. Rp 200 Juta)

```
┌─────────────────────────────────────────────────────────────────┐
│               ALUR LS STANDAR (50 - 200 Juta)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PERSIAPAN                                                      │
│  ──────────                                                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │Spesifi-│▶│ Survey │▶│  HPS   │▶│  KAK   │▶│Ranc.   │        │
│  │kasi    │ │ Harga  │ │        │ │        │ │Kontrak │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
│                                                   │             │
│  ┌────────────────────────────────────────────────┘             │
│  ▼                                                              │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Nota Dinas ke Pejabat Pengadaan                   │         │
│  └────────────────────────────────────────────────────┘         │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  PEMILIHAN (Melalui Pejabat Pengadaan)                         │
│  ─────────────────────────────────────                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │Undangan │─▶│Evaluasi │─▶│Negosiasi│─▶│Penetapan│            │
│  │   PL    │  │ Harga   │  │  Harga  │  │Penyedia │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│                                              │                  │
│  ┌───────────────────────────────────────────┘                  │
│  ▼                                                              │
│  KONTRAK & PELAKSANAAN                                          │
│  ─────────────────────                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │  SPK    │─▶│  SPMK   │─▶│  BAHP   │─▶│  BAST   │            │
│  │ Lengkap │  │         │  │         │  │         │            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│       │                                                         │
│       └─── Dengan SSUK + SSKK                                   │
│                                              │                  │
│  ┌───────────────────────────────────────────┘                  │
│  ▼                                                              │
│  PEMBAYARAN                                                     │
│  ──────────                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│  │Kuitansi │─▶│ SPP-LS  │─▶│SSP PPN  │                          │
│  │   BAP   │  │  DRPP   │  │SSP PPh  │                          │
│  └─────────┘  └─────────┘  └─────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

DOKUMEN YANG DIHASILKAN:
PERSIAPAN:
  1. Spesifikasi Teknis
  2. Survey Harga (3 sumber)
  3. BA Survey Harga
  4. HPS
  5. KAK
  6. Rancangan Kontrak (SPK + SSUK + SSKK) (BARU)
  7. Nota Dinas ke PP

PEMILIHAN:
  8. Undangan Pengadaan Langsung
  9. BA Evaluasi Harga
  10. BA Negosiasi
  11. BAHPL (Berita Acara Hasil Pengadaan Langsung)
  12. Surat Penetapan Penyedia

KONTRAK:
  13. SPK Lengkap + SSUK + SSKK
  14. SPMK

SERAH TERIMA:
  15. BAHP
  16. BAST

PEMBAYARAN:
  17. Kuitansi
  18. BAP (Berita Acara Pembayaran)
  19. SPP-LS
  20. DRPP
  21. SSP PPN (jika PKP)
  22. SSP PPh
```

### 3.4 Alur Kontrak (> Rp 200 Juta)

```
┌─────────────────────────────────────────────────────────────────┐
│               ALUR KONTRAK (> 200 Juta)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PERSIAPAN (Lengkap)                                            │
│  ───────────────────                                            │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │Spesifi-│▶│ Survey │▶│  HPS   │▶│  KAK   │▶│Ranc.   │        │
│  │kasi    │ │ Harga  │ │        │ │        │ │Kontrak │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
│                                                   │             │
│       ┌───────────────────────────────────────────┘             │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ Rancangan Surat Perjanjian + SSUK + SSKK + Lampiran │        │
│  └─────────────────────────────────────────────────────┘        │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  PEMILIHAN                                                      │
│  ─────────                                                      │
│  [Sama dengan LS Standar, atau Tender jika diperlukan]          │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  KONTRAK                                                        │
│  ───────                                                        │
│  ┌───────────────────────────────────────────────────┐          │
│  │  SURAT PERJANJIAN (Kontrak Formal)                │          │
│  │  + SSUK + SSKK                                    │          │
│  │  + Lampiran (Spesifikasi, Gambar, BOQ)            │          │
│  └───────────────────────────────────────────────────┘          │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  ┌─────────┐  ┌─────────────────────────────────────┐           │
│  │  SPMK   │─▶│ Jaminan Pelaksanaan (5% nilai kontrak)│         │
│  └─────────┘  └─────────────────────────────────────┘           │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  PELAKSANAAN                                                    │
│  ───────────                                                    │
│  [Progress Report, Adendum jika ada perubahan]                  │
│                          │                                      │
│  ┌───────────────────────┘                                      │
│  ▼                                                              │
│  SERAH TERIMA                                                   │
│  ────────────                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                          │
│  │  BAHP   │─▶│  BAST   │─▶│Jaminan  │                          │
│  │         │  │         │  │Pemeliha-│                          │
│  │         │  │         │  │raan     │                          │
│  └─────────┘  └─────────┘  └─────────┘                          │
│                                                                 │
│  PEMBAYARAN (bisa Termin)                                       │
│  ────────────────────────                                       │
│  [Termin 1] ─▶ [Termin 2] ─▶ [Termin Akhir - Retensi]          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. DIAGRAM ALUR BARU

### 4.1 Perbandingan Alur Lama vs Baru

```
ALUR LAMA (Semua Nilai Sama):
═══════════════════════════════

Persiapan ─▶ Pemilihan ─▶ Kontrak ─▶ Pelaksanaan ─▶ Serah Terima ─▶ Pembayaran
    │
    └── Tidak ada Rancangan Kontrak
    └── Semua nilai pakai alur yang sama


ALUR BARU (Berdasarkan Nilai):
══════════════════════════════

                    ┌─────────────────────────────────────┐
                    │     Buat Paket Baru                 │
                    │     Input Nilai Pagu                │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │         Deteksi Nilai               │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────┬───────────┼───────────┬───────────────┐
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
     ≤ 10 Juta      10-50 Juta   50-200 Juta  > 200 Juta      Konstruksi
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
    ┌─────────┐     ┌─────────┐ ┌─────────┐ ┌─────────┐     ┌─────────┐
    │LS MIKRO │     │LS KECIL │ │LS STANDAR│ │ KONTRAK │     │KONSTRUKSI│
    └─────────┘     └─────────┘ └─────────┘ └─────────┘     └─────────┘
          │               │           │           │               │
          │               │           │           │               │
          ▼               ▼           ▼           ▼               ▼
    ┌─────────┐     ┌─────────┐ ┌─────────┐ ┌─────────┐     ┌─────────┐
    │Bukti    │     │SPK      │ │SPK +    │ │Surat    │     │SPK/Perj.│
    │Pembelian│     │Sederhana│ │SSUK+SSKK│ │Perjanjian│    │+ Jaminan│
    └─────────┘     └─────────┘ └─────────┘ └─────────┘     └─────────┘
```

### 4.2 Decision Tree untuk Penentuan Alur

```python
def tentukan_alur(nilai_pagu: float, jenis_pengadaan: str) -> str:
    """
    Menentukan alur pengadaan berdasarkan nilai dan jenis

    Returns:
        'LS_MIKRO'    - Nilai ≤ 10 juta
        'LS_KECIL'    - Nilai > 10 juta s.d. 50 juta
        'LS_STANDAR'  - Nilai > 50 juta s.d. 200 juta
        'KONTRAK'     - Nilai > 200 juta
        'KONSTRUKSI'  - Jika jenis = Konstruksi (apapun nilainya)
    """
    # Konstruksi selalu punya alur khusus
    if jenis_pengadaan == 'Pekerjaan Konstruksi':
        if nilai_pagu <= 200_000_000:
            return 'KONSTRUKSI_KECIL'
        else:
            return 'KONSTRUKSI_BESAR'

    # Barang dan Jasa Lainnya
    if nilai_pagu <= 10_000_000:
        return 'LS_MIKRO'
    elif nilai_pagu <= 50_000_000:
        return 'LS_KECIL'
    elif nilai_pagu <= 200_000_000:
        return 'LS_STANDAR'
    else:
        return 'KONTRAK'
```

---

## 5. DOKUMEN PER ALUR

### 5.1 Tabel Perbandingan Dokumen

| No | Dokumen | LS Mikro | LS Kecil | LS Standar | Kontrak |
|----|---------|:--------:|:--------:|:----------:|:-------:|
| **PERSIAPAN** |
| 1 | Spesifikasi Teknis | Sederhana | Ya | Ya | Ya |
| 2 | Survey Harga | Opsional | Ya (3) | Ya (3) | Ya (3) |
| 3 | BA Survey Harga | - | - | Ya | Ya |
| 4 | HPS | Opsional | Ya | Ya | Ya |
| 5 | KAK | - | - | Ya | Ya |
| 6 | **Rancangan Kontrak** | - | **Ya (Baru)** | **Ya (Baru)** | **Ya (Baru)** |
| 7 | SSUK | - | - | Ya | Ya |
| 8 | SSKK | - | - | Ya | Ya |
| 9 | Nota Dinas ke PP | - | - | Ya | Ya |
| **PEMILIHAN** |
| 10 | Undangan PL | - | - | Ya | Ya |
| 11 | BA Evaluasi | - | - | Ya | Ya |
| 12 | BA Negosiasi | - | - | Ya | Ya |
| 13 | BAHPL | - | - | Ya | Ya |
| 14 | Penetapan Penyedia | - | - | Ya | Ya |
| **KONTRAK** |
| 15 | Bukti Pembelian | Ya | - | - | - |
| 16 | SPK Sederhana | - | Ya | - | - |
| 17 | SPK Lengkap | - | - | Ya | - |
| 18 | Surat Perjanjian | - | - | - | Ya |
| 19 | SPMK | - | Ya | Ya | Ya |
| 20 | Jaminan Pelaksanaan | - | - | - | Ya (5%) |
| **SERAH TERIMA** |
| 21 | BAHP | - | Ya | Ya | Ya |
| 22 | BAST | - | Ya | Ya | Ya |
| 23 | Jaminan Pemeliharaan | - | - | - | Opsional |
| **PEMBAYARAN** |
| 24 | Kuitansi | Ya | Ya | Ya | Ya |
| 25 | BAP | - | - | Ya | Ya |
| 26 | SPP-LS | - | Ya | Ya | Ya |
| 27 | DRPP | - | Ya | Ya | Ya |
| 28 | SSP PPN | Jika PKP | Jika PKP | Jika PKP | Jika PKP |
| 29 | SSP PPh | Ya | Ya | Ya | Ya |

### 5.2 Jumlah Dokumen per Alur

| Alur | Jumlah Dokumen | Keterangan |
|------|----------------|------------|
| **LS Mikro** | 3-5 dokumen | Paling sederhana |
| **LS Kecil** | 12-14 dokumen | Disederhanakan |
| **LS Standar** | 20-22 dokumen | Lengkap |
| **Kontrak** | 22-25 dokumen | Paling lengkap |

---

## 6. IMPLEMENTASI TEKNIS

### 6.1 Perubahan pada Database

```sql
-- Tambah kolom untuk menentukan alur
ALTER TABLE paket ADD COLUMN alur_pengadaan TEXT DEFAULT 'LS_STANDAR';
-- Nilai: 'LS_MIKRO', 'LS_KECIL', 'LS_STANDAR', 'KONTRAK', 'KONSTRUKSI_KECIL', 'KONSTRUKSI_BESAR'

-- Tambah tabel untuk rancangan kontrak
CREATE TABLE IF NOT EXISTS rancangan_kontrak (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paket_id INTEGER NOT NULL,

    -- Ketentuan Umum
    lingkup_pekerjaan TEXT,
    cara_pembayaran TEXT DEFAULT 'SEKALIGUS',  -- SEKALIGUS / TERMIN
    jumlah_termin INTEGER DEFAULT 1,
    uang_muka_persen REAL DEFAULT 0,
    retensi_persen REAL DEFAULT 0,

    -- Jaminan
    jaminan_pelaksanaan_persen REAL DEFAULT 0,
    jaminan_pemeliharaan_persen REAL DEFAULT 0,
    masa_pemeliharaan_hari INTEGER DEFAULT 0,

    -- Denda
    denda_keterlambatan_persen REAL DEFAULT 0.1,  -- per hari
    denda_maksimal_persen REAL DEFAULT 5,

    -- Penyelesaian Perselisihan
    penyelesaian_sengketa TEXT DEFAULT 'MUSYAWARAH',

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (paket_id) REFERENCES paket(id)
);
```

### 6.2 Perubahan pada config.py

```python
# Tambah konstanta batas nilai
BATAS_NILAI = {
    'LS_MIKRO': 10_000_000,      # ≤ 10 juta
    'LS_KECIL': 50_000_000,      # ≤ 50 juta
    'LS_STANDAR': 200_000_000,   # ≤ 200 juta
    'KONTRAK': float('inf'),     # > 200 juta
}

# Tambah workflow stages untuk rancangan kontrak
WORKFLOW_STAGES_NEW = [
    # ... existing stages ...
    {
        'id': 5,  # insert before NOTA_DINAS_PP
        'code': 'RANCANGAN_KONTRAK',
        'name': 'Rancangan Kontrak',
        'description': 'Penyusunan rancangan SPK/Surat Perjanjian',
        'template_type': 'word',
        'template_file': 'rancangan_kontrak.docx',
        'required': True,
        'min_nilai': 10_000_000,  # Hanya untuk nilai > 10 juta
        'outputs': ['RANCANGAN_SPK', 'SSUK', 'SSKK'],
    },
    # ... rest of stages ...
]

# Dokumen per alur
DOKUMEN_PER_ALUR = {
    'LS_MIKRO': [
        'SPESIFIKASI_SEDERHANA',
        'BUKTI_PEMBELIAN',
        'KUITANSI',
        'SSP_PPH',
    ],
    'LS_KECIL': [
        'SPESIFIKASI',
        'SURVEY_HARGA',
        'HPS',
        'RANCANGAN_SPK',
        'SPK_SEDERHANA',
        'SPMK',
        'BAHP',
        'BAST',
        'KUITANSI',
        'SPP_LS',
        'DRPP',
        'SSP_PPN',
        'SSP_PPH',
    ],
    'LS_STANDAR': [
        'SPESIFIKASI',
        'SURVEY_HARGA',
        'BA_SURVEY',
        'HPS',
        'KAK',
        'RANCANGAN_KONTRAK',
        'SSUK',
        'SSKK',
        'NOTA_DINAS_PP',
        'UNDANGAN_PL',
        'BA_EVALUASI',
        'BA_NEGOSIASI',
        'BAHPL',
        'PENETAPAN_PENYEDIA',
        'SPK',
        'SPMK',
        'BAHP',
        'BAST',
        'KUITANSI',
        'BAP',
        'SPP_LS',
        'DRPP',
        'SSP_PPN',
        'SSP_PPH',
    ],
    'KONTRAK': [
        # ... sama dengan LS_STANDAR + Jaminan
    ],
}
```

### 6.3 Perubahan pada UI (Dashboard)

```python
# Tampilkan indikator alur di dashboard
def get_alur_badge(alur: str) -> dict:
    """Return badge info untuk alur pengadaan"""
    BADGES = {
        'LS_MIKRO': {'text': 'Mikro', 'color': '#28a745', 'icon': '💵'},
        'LS_KECIL': {'text': 'Kecil', 'color': '#17a2b8', 'icon': '📋'},
        'LS_STANDAR': {'text': 'Standar', 'color': '#ffc107', 'icon': '📑'},
        'KONTRAK': {'text': 'Kontrak', 'color': '#dc3545', 'icon': '📜'},
    }
    return BADGES.get(alur, {'text': alur, 'color': '#6c757d', 'icon': '📄'})
```

---

## 7. TEMPLATE BARU YANG DIPERLUKAN

### 7.1 Daftar Template Baru

| No | Template | Format | Untuk Alur |
|----|----------|--------|------------|
| 1 | `rancangan_spk_sederhana.docx` | Word | LS Kecil |
| 2 | `rancangan_spk.docx` | Word | LS Standar |
| 3 | `rancangan_surat_perjanjian.docx` | Word | Kontrak |
| 4 | `ssuk.docx` | Word | LS Standar, Kontrak |
| 5 | `sskk.docx` | Word | LS Standar, Kontrak |
| 6 | `spk_sederhana.docx` | Word | LS Kecil |
| 7 | `bukti_pembelian.docx` | Word | LS Mikro |
| 8 | `spesifikasi_sederhana.docx` | Word | LS Mikro |
| 9 | `hps_sederhana.xlsx` | Excel | LS Mikro (opsional) |

---

## 8. TIMELINE IMPLEMENTASI

### Fase 1: Rancangan Kontrak
- [ ] Buat tabel database `rancangan_kontrak`
- [ ] Buat template `rancangan_spk.docx`
- [ ] Buat template `ssuk.docx` dan `sskk.docx`
- [ ] Update workflow stages
- [ ] Buat UI form untuk rancangan kontrak

### Fase 2: Pemisahan Alur
- [ ] Tambah kolom `alur_pengadaan` di tabel `paket`
- [ ] Implementasi fungsi `tentukan_alur()`
- [ ] Update dashboard untuk menampilkan badge alur
- [ ] Filter dokumen berdasarkan alur
- [ ] Buat template untuk LS Mikro dan LS Kecil

### Fase 3: Testing & Refinement
- [ ] Testing semua alur
- [ ] Validasi dokumen yang dihasilkan
- [ ] User acceptance testing
- [ ] Dokumentasi pengguna

---

*Dokumen ini dibuat sebagai panduan rancangan perubahan alur kerja Asisten PPK Offline.*

*Versi: 1.0*
*Tanggal: Januari 2026*
