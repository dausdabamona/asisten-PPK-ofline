# PPK DOCUMENT FACTORY v5.0
## SISTEM PENDAMPING PPK - DESAIN PRAKTIS
### "Membantu, Bukan Menghalangi"

---

## FILOSOFI SISTEM

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   ✅ SISTEM INI ADALAH:                    ❌ SISTEM INI BUKAN:                 │
│   ─────────────────────                    ────────────────────                 │
│   • Pendamping PPK                         • Sistem audit                       │
│   • Penata dokumen otomatis                • Sistem penolakan                   │
│   • Pengingat urutan regulasi              • Compliance policing                │
│   • Pemercepat penyusunan                  • Hard blocking system               │
│   • Generator dokumen cerdas               • Validator ketat                    │
│                                                                                 │
│   PRINSIP: "Bimbing dengan lembut, ingatkan dengan sopan, bantu dengan cepat"  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. LIFECYCLE PENGADAAN - VERSI PRAKTIS PPK

### A. Status Pekerjaan (State Flow)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              ALUR STATUS PAKET PENGADAAN                                       │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐     ┌────────────┐
  │  DRAFT   │────►│ PERSIAPAN  │────►│  DIKIRIM │────►│ PEMILIHAN│────►│  PENYEDIA  │
  │          │     │            │     │  KE PP   │     │          │     │ DITETAPKAN │
  └──────────┘     └────────────┘     └──────────┘     └──────────┘     └─────┬──────┘
       │                │                  │                │                 │
       │           Dokumen            Nota Dinas       PP Proses          Penetapan
       │           persiapan          terkirim         pemilihan          Penyedia
       │           mulai dibuat                                               │
       │                                                                      ▼
       │                                                              ┌────────────┐
       │          ┌──────────┐     ┌────────────┐     ┌──────────┐   │  KONTRAK   │
       │          │ SELESAI  │◄────│SERAH TERIMA│◄────│PELAKSANA-│◄──│   AKTIF    │
       │          │          │     │            │     │   AN     │   │            │
       │          └──────────┘     └────────────┘     └──────────┘   └────────────┘
       │               │                 │                 │               │
       │          Pembayaran         BAST dibuat       SPMK terbit     SPK/Kontrak
       │          selesai                                              ditandatangani
       │
       └──────────────────────────────────────────────────────────────────────────►
                                    DIBATALKAN (dari status manapun)


STATUS CODES:
┌──────────────────┬──────┬─────────────────────────────────────────────────────────┐
│ Status           │ Kode │ Deskripsi                                               │
├──────────────────┼──────┼─────────────────────────────────────────────────────────┤
│ DRAFT            │  00  │ Paket baru dibuat, data dasar                           │
│ PERSIAPAN        │  10  │ Sedang menyusun dokumen persiapan                       │
│ DIKIRIM_KE_PP    │  20  │ Nota dinas sudah dikirim ke Pejabat Pengadaan           │
│ PEMILIHAN        │  30  │ Proses pemilihan oleh PP                                │
│ PENYEDIA_OK      │  40  │ Penyedia sudah ditetapkan                               │
│ KONTRAK_AKTIF    │  50  │ SPK/Kontrak sudah ditandatangani                        │
│ PELAKSANAAN      │  60  │ Pekerjaan sedang berjalan                               │
│ SERAH_TERIMA     │  70  │ Pemeriksaan dan BAST                                    │
│ SELESAI          │  99  │ Pembayaran selesai, arsip                               │
│ DIBATALKAN       │  -1  │ Paket dibatalkan                                        │
└──────────────────┴──────┴─────────────────────────────────────────────────────────┘
```

### B. Visual Flow Per Fase

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE A: PERSIAPAN PENGADAAN                                                          [PPK]     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│   │ 1.SPEK/ │───►│ 2.VOLUME│───►│ 3.SURVEY│───►│  4.RAB  │───►│  5.HPS  │───►│6.RANC.  │       │
│   │   KAK   │    │   BOQ   │    │  HARGA  │    │         │    │         │    │ KONTRAK │       │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └────┬────┘       │
│        │              │              │              │              │              │            │
│        ▼              ▼              ▼              ▼              ▼              ▼            │
│   [Spesifikasi]  [Item BOQ]    [Min 3 sumber] [Auto-calc]   [Dari Survey]   [SSUK/SSKK]       │
│   [KAK]          [Detail]      [3 Toko/Web]   [Dari BOQ]    [+ Overhead]    [Draft SPK]       │
│                                                                                    │            │
│                                                              ┌─────────────────────┘            │
│                                                              ▼                                  │
│                                                        ┌───────────┐                           │
│                                                        │ 7.NOTA    │                           │
│                                                        │ DINAS PP  │──► [KIRIM KE PP]          │
│                                                        └───────────┘                           │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • Spesifikasi Teknis        • RAB                    • SSUK / SSKK             │           │
│   │ • KAK (Kerangka Acuan)      • HPS                    • Rancangan Kontrak       │           │
│   │ • Tabel Survey Harga        • BA Survey Harga        • Nota Dinas ke PP        │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
│   ⚠️ SOFT RULES (Warning, bukan Block):                                                        │
│   • HPS sebelum Survey? → "💡 Sebaiknya survey harga diinput dulu untuk konsistensi"           │
│   • RAB sebelum BOQ? → "💡 Lengkapi item BOQ terlebih dahulu"                                  │
│   • Tanggal tidak urut? → "💡 Perhatikan urutan tanggal dokumen"                               │
│                                                                                                 │
│   🔲 FIELD TERSEMBUNYI (Belum Muncul):                                                         │
│   • Penyedia (muncul setelah pemilihan)                                                        │
│   • Nilai Kontrak (muncul setelah negosiasi)                                                   │
│   • SPMK, BAST, Pembayaran (muncul setelah kontrak)                                            │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE B: PEMILIHAN PENYEDIA                                              [PEJABAT PENGADAAN]    │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│   │ TERIMA   │───►│ UNDANGAN │───►│ EVALUASI │───►│ NEGOSIASI│───►│ PENETAPAN│                 │
│   │ BERKAS   │    │          │    │          │    │          │    │ PENYEDIA │                 │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘                 │
│        │               │               │               │               │                       │
│        ▼               ▼               ▼               ▼               ▼                       │
│   [Verifikasi]    [Pengumuman/   [Admin/Teknis/   [Harga Final]   [BA Penetapan]              │
│   [HPS & Dok]      Langsung]       Harga]                          [Surat Penetapan]          │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • Undangan Pemilihan          • BA Evaluasi Harga                              │           │
│   │ • BA Evaluasi Administrasi    • BA Klarifikasi/Negosiasi                       │           │
│   │ • BA Evaluasi Teknis          • BAHP Pemilihan                                 │           │
│   │                               • Surat Penetapan Penyedia                       │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
│   ✅ TRIGGER SETELAH PENETAPAN:                                                                │
│   • Field Penyedia → MUNCUL & dapat diisi                                                      │
│   • Nilai Kontrak → MUNCUL (= Harga Negosiasi)                                                 │
│   • Modul Kontrak → AKTIF                                                                      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE C: KONTRAK                                                           [PPK + PENYEDIA]     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                                 │
│   │   SPK    │───►│   SPMK   │───►│ JAMINAN  │───►│  JADWAL  │                                 │
│   │ KONTRAK  │    │          │    │ PELAKS.  │    │ PELAKS.  │                                 │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘                                 │
│        │               │               │               │                                       │
│        ▼               ▼               ▼               ▼                                       │
│   [Nilai =        [Tgl ≥ Tgl     [Jika nilai      [Time Schedule]                             │
│    Negosiasi]      Kontrak]       > threshold]                                                 │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • SPK / Surat Perjanjian      • Jaminan Pelaksanaan                            │           │
│   │ • SPMK                        • Jadwal Pelaksanaan                             │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
│   💡 SOFT VALIDATION:                                                                          │
│   • Tgl SPMK < Tgl SPK? → "💡 Tanggal SPMK sebaiknya setelah tanggal SPK"                      │
│   • Jangka waktu terlalu pendek? → "💡 Pastikan jangka waktu realistis"                        │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE D: PELAKSANAAN & ADENDUM                                             [PPK + PENYEDIA]     │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐        │
│   │                            PEKERJAAN BERJALAN                                     │        │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐                                   │        │
│   │   │ PROGRESS │───►│ LAPORAN  │───►│ MONITORING│                                   │        │
│   │   │    %     │    │ KEMAJUAN │    │          │                                   │        │
│   │   └──────────┘    └──────────┘    └──────────┘                                   │        │
│   └───────────────────────────────────────────────────────────────────────────────────┘        │
│                           │                                                                    │
│                           │ Ada perubahan?                                                     │
│                           ▼                                                                    │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐        │
│   │                            MODUL ADENDUM (Opsional)                               │        │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐                                   │        │
│   │   │JUSTIFIKASI───►│ ADENDUM  │───►│ADENDUM   │                                   │        │
│   │   │PERUBAHAN │    │ KONTRAK  │    │  SPMK    │                                   │        │
│   │   └──────────┘    └──────────┘    └──────────┘                                   │        │
│   │                                                                                   │        │
│   │   Jenis Adendum: □ Waktu  □ Volume  □ Nilai  □ Spesifikasi                       │        │
│   │   Nomor Adendum: Auto-increment (01, 02, 03...)                                  │        │
│   └───────────────────────────────────────────────────────────────────────────────────┘        │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • Laporan Kemajuan Pekerjaan  • Adendum SPMK                                   │           │
│   │ • Justifikasi Perubahan       • BA Perubahan                                   │           │
│   │ • Adendum Kontrak             • CCO (Contract Change Order)                    │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE E: PEMERIKSAAN & SERAH TERIMA                                      [PPHP + PPK]           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   CHECKLIST VISUAL (bukan gerbang keras):                                                      │
│                                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐          │
│   │                                                                                 │          │
│   │   ☐ PEMERIKSAAN              ☐ BAHP                    ☐ BAST                  │          │
│   │   ─────────────              ─────                     ─────                   │          │
│   │   Pekerjaan 100%             Hasil OK?                 Serah terima            │          │
│   │   PPHP memeriksa             Buat BAHP                 resmi                   │          │
│   │                                  │                                              │          │
│   │                                  ├─► OK ──────► BAST                           │          │
│   │                                  │                                              │          │
│   │                                  └─► TIDAK OK ──► BA Perbaikan ──► Perbaiki    │          │
│   │                                                                     ──► Loop   │          │
│   │                                                                                 │          │
│   └─────────────────────────────────────────────────────────────────────────────────┘          │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • Laporan Penyelesaian Pekerjaan   • BAST (Berita Acara Serah Terima)          │           │
│   │ • Checklist Pemeriksaan            • BA Perbaikan (jika ada)                   │           │
│   │ • BAHP (BA Hasil Pemeriksaan)                                                  │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
│   💡 SOFT REMINDER:                                                                            │
│   • BAST tanpa BAHP? → "💡 Sebaiknya buat BAHP terlebih dahulu"                                │
│   • Tanggal BAST < BAHP? → "💡 Perhatikan urutan tanggal"                                      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FASE F: PEMBAYARAN                                            [PPK + BENDAHARA + PPSPM]        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│   │ KUITANSI │───►│   SSP    │───►│ SPP-LS   │───►│   SPM    │───►│  SP2D    │                 │
│   │          │    │  PAJAK   │    │          │    │          │    │          │                 │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘                 │
│        │               │               │               │               │                       │
│        ▼               ▼               ▼               ▼               ▼                       │
│   [Nilai =        [PPh + PPN]     [PPK ajukan]    [PPSPM]         [KPPN/Bank]                 │
│    Kontrak]                                                                                    │
│                                                                                                 │
│   📋 DOKUMEN FASE INI:                                                                         │
│   ┌────────────────────────────────────────────────────────────────────────────────┐           │
│   │ • Kuitansi                    • SPM                                            │           │
│   │ • Faktur Pajak (jika PKP)     • SP2D                                           │           │
│   │ • SSP PPh & PPN               • Bukti Transfer                                 │           │
│   │ • SPP-LS                                                                       │           │
│   └────────────────────────────────────────────────────────────────────────────────┘           │
│                                                                                                 │
│   💡 SOFT REMINDER:                                                                            │
│   • SPP tanpa BAST? → "💡 Pastikan BAST sudah dibuat untuk kelengkapan"                        │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. MATRIKS DOKUMEN PER FASE

### Tabel Ketersediaan Dokumen

| No | Dokumen | Draft | Persiapan | Dikirim | Pemilihan | Penyedia OK | Kontrak | Pelaksanaan | Serah Terima | Selesai |
|----|---------|:-----:|:---------:|:-------:|:---------:|:-----------:|:-------:|:-----------:|:------------:|:-------:|
| 1 | Spesifikasi Teknis | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 | KAK | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 | Survey Harga | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | RAB | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | HPS | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | Rancangan Kontrak | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 7 | Nota Dinas PP | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8 | Undangan | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9 | BA Evaluasi | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 10 | BAHP Pemilihan | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 11 | Penetapan Penyedia | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 12 | SPK / Kontrak | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ |
| 13 | SPMK | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ | ✅ |
| 14 | Adendum | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ | ✅ |
| 15 | BAHP Hasil | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ |
| 16 | BAST | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ |
| 17 | Kuitansi | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ |
| 18 | SPP | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ |
| 19 | SSP | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | 🔲 | ✅ | ✅ |

**Legenda:**
- ✅ Tersedia & dapat dibuat
- 🔲 Belum tersedia (tersembunyi)

---

## 3. LOGIKA KAPAN FIELD MUNCUL

### A. Visibility Rules (Bukan Lock Rules!)

```python
FIELD_VISIBILITY_RULES = {
    # =================================================================
    # FIELD PENYEDIA
    # =================================================================
    'penyedia_id': {
        'visible_when': 'status >= PENYEDIA_OK',  # Muncul setelah penetapan
        'hidden_message': None,  # Tidak perlu pesan, field memang belum waktunya
    },
    
    # =================================================================
    # FIELD NILAI KONTRAK
    # =================================================================
    'nilai_kontrak': {
        'visible_when': 'status >= PENYEDIA_OK',
        'auto_fill_from': 'nilai_negosiasi',  # Otomatis dari negosiasi
    },
    
    # =================================================================
    # FIELD NILAI NEGOSIASI
    # =================================================================
    'nilai_negosiasi': {
        'visible_when': 'status >= PEMILIHAN',
        'validation': {
            'type': 'soft',  # Soft validation = warning only
            'rule': 'nilai_negosiasi <= nilai_hps',
            'message': '💡 Nilai negosiasi melebihi HPS, pastikan sudah sesuai'
        }
    },
    
    # =================================================================
    # MODUL KONTRAK (SPK, SPMK, dll)
    # =================================================================
    'modul_kontrak': {
        'visible_when': 'status >= PENYEDIA_OK',
    },
    
    # =================================================================
    # MODUL ADENDUM
    # =================================================================
    'modul_adendum': {
        'visible_when': 'status >= KONTRAK_AKTIF',
    },
    
    # =================================================================
    # MODUL SERAH TERIMA
    # =================================================================
    'modul_serah_terima': {
        'visible_when': 'status >= PELAKSANAAN',
    },
    
    # =================================================================
    # MODUL PEMBAYARAN
    # =================================================================
    'modul_pembayaran': {
        'visible_when': 'status >= SERAH_TERIMA',
    },
}
```

### B. Field Visibility Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              KAPAN FIELD / MODUL MUNCUL                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

          DRAFT    PERSIAPAN   DIKIRIM   PEMILIHAN   PENYEDIA   KONTRAK   PELAKS   SERAH   SELESAI
            │          │          │          │          │          │         │        │        │
            ▼          ▼          ▼          ▼          ▼          ▼         ▼        ▼        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Data Dasar Paket                                                                               │
│ ████████████████████████████████████████████████████████████████████████████████████████████   │
│ [Selalu terlihat dari awal]                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Item BOQ & Spesifikasi                                                                         │
│ ████████████████████████████████████████████████████████████████████████████████████████████   │
│ [Selalu terlihat dari awal]                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Survey Harga                                                                                   │
│ ████████████████████████████████████████████████████████████████████████████████████████████   │
│ [Selalu terlihat dari awal]                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HPS & RAB                                                                                      │
│ ████████████████████████████████████████████████████████████████████████████████████████████   │
│ [Selalu terlihat dari awal]                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Field Penyedia                                                                                 │
│                                            ███████████████████████████████████████████████████ │
│                                            [Muncul setelah PENYEDIA_OK]                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Nilai Kontrak                                                                                  │
│                                            ███████████████████████████████████████████████████ │
│                                            [Muncul setelah PENYEDIA_OK, auto-fill]             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Modul Kontrak (SPK, SPMK)                                                                      │
│                                            ███████████████████████████████████████████████████ │
│                                            [Muncul setelah PENYEDIA_OK]                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Modul Adendum                                                                                  │
│                                                       ████████████████████████████████████████ │
│                                                       [Muncul setelah KONTRAK_AKTIF]           │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Modul Serah Terima (BAHP, BAST)                                                                │
│                                                                ███████████████████████████████ │
│                                                                [Muncul setelah PELAKSANAAN]    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Modul Pembayaran (SPP, SSP, Kuitansi)                                                          │
│                                                                        ███████████████████████ │
│                                                                        [Muncul setelah BAST]   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. SOFT VALIDATION SYSTEM

### A. Jenis Validasi

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SISTEM VALIDASI RAMAH PPK                                         │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 1. INFO (💡) - Saran/Rekomendasi                                          │
│    ─────────────────────────────────                                      │
│    • Tidak memblokir                                                      │
│    • Hanya memberikan saran                                               │
│    • Warna: Biru muda                                                     │
│    • Icon: 💡                                                             │
│                                                                           │
│    Contoh:                                                                │
│    ┌─────────────────────────────────────────────────────────────┐       │
│    │ 💡 Sebaiknya survey harga diinput terlebih dahulu untuk     │       │
│    │    konsistensi perhitungan HPS                              │       │
│    └─────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 2. WARNING (⚠️) - Peringatan                                              │
│    ───────────────────────────                                            │
│    • Tidak memblokir                                                      │
│    • Mengingatkan ketidaksesuaian                                         │
│    • Warna: Kuning/Orange                                                 │
│    • Icon: ⚠️                                                             │
│                                                                           │
│    Contoh:                                                                │
│    ┌─────────────────────────────────────────────────────────────┐       │
│    │ ⚠️ Tanggal SPMK lebih awal dari tanggal SPK                 │       │
│    │    Pastikan urutan tanggal sudah benar                      │       │
│    └─────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 3. INCOMPLETE (🔲) - Belum Lengkap                                        │
│    ─────────────────────────────────                                      │
│    • Tidak memblokir                                                      │
│    • Menunjukkan item yang perlu dilengkapi                               │
│    • Warna: Abu-abu                                                       │
│    • Icon: 🔲                                                             │
│                                                                           │
│    Contoh:                                                                │
│    ┌─────────────────────────────────────────────────────────────┐       │
│    │ 🔲 Survey Harga: 2 dari 3 sumber terisi                     │       │
│    │    Tambahkan 1 sumber lagi untuk kelengkapan                │       │
│    └─────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 4. COMPLETE (✅) - Lengkap                                                │
│    ─────────────────────────                                              │
│    • Indikator positif                                                    │
│    • Menunjukkan item sudah selesai                                       │
│    • Warna: Hijau                                                         │
│    • Icon: ✅                                                             │
│                                                                           │
│    Contoh:                                                                │
│    ┌─────────────────────────────────────────────────────────────┐       │
│    │ ✅ Survey Harga: Lengkap (3 sumber)                         │       │
│    └─────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ 5. BLOCKED (🚫) - Hard Block (SANGAT JARANG)                              │
│    ───────────────────────────────────────────                            │
│    • HANYA untuk logika fatal yang tidak masuk akal                       │
│    • Warna: Merah                                                         │
│    • Icon: 🚫                                                             │
│                                                                           │
│    Contoh hard block (sangat terbatas):                                   │
│    • Nilai kontrak negatif                                                │
│    • Tanggal selesai sebelum tanggal mulai                                │
│    • Volume = 0 atau negatif                                              │
│                                                                           │
│    ┌─────────────────────────────────────────────────────────────┐       │
│    │ 🚫 Volume tidak boleh kosong atau negatif                   │       │
│    └─────────────────────────────────────────────────────────────┘       │
└───────────────────────────────────────────────────────────────────────────┘
```

### B. Validation Rules

```python
SOFT_VALIDATION_RULES = {
    # =================================================================
    # SURVEY & HPS
    # =================================================================
    'hps_before_survey': {
        'type': 'INFO',
        'condition': 'hps_filled AND survey_count < 3',
        'message': '💡 Sebaiknya survey harga diinput terlebih dahulu untuk konsistensi'
    },
    
    'survey_incomplete': {
        'type': 'INCOMPLETE',
        'condition': 'survey_count > 0 AND survey_count < 3',
        'message': '🔲 Survey Harga: {count} dari 3 sumber terisi'
    },
    
    # =================================================================
    # TIMELINE
    # =================================================================
    'spmk_before_spk': {
        'type': 'WARNING',
        'condition': 'tanggal_spmk < tanggal_spk',
        'message': '⚠️ Tanggal SPMK lebih awal dari tanggal SPK'
    },
    
    'bast_before_bahp': {
        'type': 'WARNING',
        'condition': 'tanggal_bast < tanggal_bahp',
        'message': '⚠️ Tanggal BAST lebih awal dari tanggal BAHP'
    },
    
    'kontrak_before_penetapan': {
        'type': 'WARNING',
        'condition': 'tanggal_kontrak < tanggal_penetapan_penyedia',
        'message': '⚠️ Tanggal Kontrak lebih awal dari tanggal Penetapan Penyedia'
    },
    
    # =================================================================
    # NILAI
    # =================================================================
    'negosiasi_exceeds_hps': {
        'type': 'WARNING',
        'condition': 'nilai_negosiasi > nilai_hps',
        'message': '⚠️ Nilai negosiasi melebihi HPS'
    },
    
    'kontrak_exceeds_pagu': {
        'type': 'WARNING',
        'condition': 'nilai_kontrak > nilai_pagu',
        'message': '⚠️ Nilai kontrak melebihi pagu anggaran'
    },
    
    # =================================================================
    # KELENGKAPAN DOKUMEN
    # =================================================================
    'spk_without_penetapan': {
        'type': 'INFO',
        'condition': 'creating_spk AND NOT exists_penetapan_penyedia',
        'message': '💡 Pastikan surat penetapan penyedia sudah dibuat'
    },
    
    'spp_without_bast': {
        'type': 'INFO',
        'condition': 'creating_spp AND NOT exists_bast',
        'message': '💡 Pastikan BAST sudah dibuat untuk kelengkapan pembayaran'
    },
    
    # =================================================================
    # HARD BLOCK (sangat terbatas!)
    # =================================================================
    'volume_zero': {
        'type': 'BLOCKED',
        'condition': 'volume <= 0',
        'message': '🚫 Volume tidak boleh kosong atau negatif'
    },
    
    'end_before_start': {
        'type': 'BLOCKED',
        'condition': 'tanggal_selesai < tanggal_mulai',
        'message': '🚫 Tanggal selesai tidak boleh sebelum tanggal mulai'
    },
}
```

---

## 5. TIMELINE INPUT OTOMATIS

### A. Auto-Sequence Dates

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              TIMELINE INPUT TANGGAL OTOMATIS                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

Sistem akan MENYARANKAN tanggal berurutan, bukan MEMAKSA:

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                 │
│  FASE PERSIAPAN                                                                                 │
│  ══════════════                                                                                 │
│                                                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Tgl Spesifikasi  │───►│ Tgl Survey       │───►│ Tgl HPS          │───►│ Tgl Nota Dinas   │  │
│  │ [01/01/2026]     │    │ [05/01/2026]     │    │ [10/01/2026]     │    │ [12/01/2026]     │  │
│  │                  │    │ Auto: ≥ Spek     │    │ Auto: ≥ Survey   │    │ Auto: ≥ HPS      │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│                                                                                                 │
│  FASE PEMILIHAN                                                                                 │
│  ══════════════                                                                                 │
│                                                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐                          │
│  │ Tgl Undangan     │───►│ Tgl Evaluasi     │───►│ Tgl Penetapan    │                          │
│  │ [15/01/2026]     │    │ [20/01/2026]     │    │ [25/01/2026]     │                          │
│  │ Auto: ≥ ND       │    │ Auto: ≥ Undangan │    │ Auto: ≥ Evaluasi │                          │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘                          │
│                                                                                                 │
│  FASE KONTRAK                                                                                   │
│  ════════════                                                                                   │
│                                                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐                          │
│  │ Tgl Kontrak      │───►│ Tgl SPMK         │───►│ Tgl Mulai Kerja  │                          │
│  │ [28/01/2026]     │    │ [29/01/2026]     │    │ [30/01/2026]     │                          │
│  │ Auto: ≥ Penetapan│    │ Auto: ≥ Kontrak  │    │ Auto: ≥ SPMK     │                          │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘                          │
│                                                                                                 │
│  FASE SERAH TERIMA & PEMBAYARAN                                                                 │
│  ══════════════════════════════                                                                 │
│                                                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Tgl Selesai Kerja│───►│ Tgl BAHP         │───►│ Tgl BAST         │───►│ Tgl SPP          │  │
│  │ [28/02/2026]     │    │ [01/03/2026]     │    │ [03/03/2026]     │    │ [05/03/2026]     │  │
│  │ = Mulai + Jangka │    │ Auto: ≥ Selesai  │    │ Auto: ≥ BAHP     │    │ Auto: ≥ BAST     │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘    └──────────────────┘  │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### B. Auto-Suggest Logic

```python
DATE_AUTO_SUGGEST = {
    # Saat input tanggal, sistem akan suggest default berdasarkan tanggal sebelumnya
    
    'tanggal_survey': {
        'suggest_from': 'tanggal_spesifikasi',
        'offset_days': 3,  # Suggest 3 hari setelah
        'message': 'Suggested: 3 hari setelah tanggal spesifikasi'
    },
    
    'tanggal_hps': {
        'suggest_from': 'tanggal_survey_selesai',
        'offset_days': 2,
        'message': 'Suggested: 2 hari setelah survey selesai'
    },
    
    'tanggal_nota_dinas': {
        'suggest_from': 'tanggal_hps',
        'offset_days': 1,
    },
    
    'tanggal_undangan': {
        'suggest_from': 'tanggal_nota_dinas',
        'offset_days': 2,
    },
    
    'tanggal_penetapan_penyedia': {
        'suggest_from': 'tanggal_evaluasi',
        'offset_days': 3,
    },
    
    'tanggal_kontrak': {
        'suggest_from': 'tanggal_penetapan_penyedia',
        'offset_days': 1,
    },
    
    'tanggal_spmk': {
        'suggest_from': 'tanggal_kontrak',
        'offset_days': 1,
    },
    
    'tanggal_mulai_kerja': {
        'suggest_from': 'tanggal_spmk',
        'offset_days': 1,
    },
    
    'tanggal_selesai_kerja': {
        'suggest_from': 'tanggal_mulai_kerja',
        'offset_days': 'jangka_waktu',  # Dynamic from jangka waktu
    },
    
    'tanggal_bahp': {
        'suggest_from': 'tanggal_selesai_kerja',
        'offset_days': 3,
    },
    
    'tanggal_bast': {
        'suggest_from': 'tanggal_bahp',
        'offset_days': 2,
    },
    
    'tanggal_spp': {
        'suggest_from': 'tanggal_bast',
        'offset_days': 2,
    },
}
```

---

## 6. RELASI DOKUMEN (PARENT-CHILD)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              RELASI ANTAR DOKUMEN                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                 │
│  PAKET (ROOT)                                                                                   │
│  ├── Spesifikasi Teknis                                                                         │
│  │   └── [source: item_barang.spesifikasi]                                                      │
│  │                                                                                              │
│  ├── KAK (Kerangka Acuan Kerja)                                                                 │
│  │   └── [source: paket.* + item summary]                                                       │
│  │                                                                                              │
│  ├── Survey Harga                                                                               │
│  │   ├── Tabel Survey Per Item                                                                  │
│  │   │   └── [source: survey_harga.*]                                                           │
│  │   └── BA Survey Harga                                                                        │
│  │       └── [source: survey_harga summary]                                                     │
│  │                                                                                              │
│  ├── RAB                                                                                        │
│  │   └── [source: item_barang.* + harga_dasar]                                                  │
│  │                                                                                              │
│  ├── HPS                                                                                        │
│  │   └── [source: item_barang.harga_hps + overhead]                                             │
│  │                                                                                              │
│  ├── Rancangan Kontrak                                                                          │
│  │   ├── SSUK                                                                                   │
│  │   └── SSKK                                                                                   │
│  │                                                                                              │
│  ├── Nota Dinas ke PP                                                                           │
│  │   └── [source: paket summary + HPS]                                                          │
│  │                                                                                              │
│  ├── [AFTER PEMILIHAN]                                                                          │
│  │   ├── Undangan Pemilihan                                                                     │
│  │   ├── BA Evaluasi                                                                            │
│  │   ├── BAHP Pemilihan                                                                         │
│  │   │   └── [source: hasil evaluasi]                                                           │
│  │   └── Surat Penetapan Penyedia                                                               │
│  │       └── [source: penyedia terpilih]                                                        │
│  │                                                                                              │
│  ├── [AFTER PENYEDIA OK]                                                                        │
│  │   ├── SPK / Surat Perjanjian                                                                 │
│  │   │   └── [source: paket + penyedia + nilai_kontrak]                                         │
│  │   ├── SPMK                                                                                   │
│  │   │   └── [parent: SPK]                                                                      │
│  │   └── Jaminan Pelaksanaan                                                                    │
│  │                                                                                              │
│  ├── [AFTER KONTRAK]                                                                            │
│  │   └── Adendum (jika ada)                                                                     │
│  │       ├── Adendum Kontrak                                                                    │
│  │       │   └── [parent: SPK]                                                                  │
│  │       └── Adendum SPMK                                                                       │
│  │           └── [parent: SPMK]                                                                 │
│  │                                                                                              │
│  ├── [AFTER PELAKSANAAN]                                                                        │
│  │   ├── BAHP Hasil Pekerjaan                                                                   │
│  │   │   └── [source: checklist pemeriksaan]                                                    │
│  │   └── BAST                                                                                   │
│  │       └── [parent: BAHP, source: SPK]                                                        │
│  │                                                                                              │
│  └── [AFTER BAST]                                                                               │
│      ├── Kuitansi                                                                               │
│      │   └── [source: nilai_kontrak]                                                            │
│      ├── Faktur Pajak                                                                           │
│      │   └── [source: nilai + pajak]                                                            │
│      ├── SSP                                                                                    │
│      │   └── [source: kalkulasi pajak]                                                          │
│      ├── SPP-LS                                                                                 │
│      │   └── [source: BAST + Kuitansi + SSP]                                                    │
│      ├── SPM                                                                                    │
│      │   └── [parent: SPP]                                                                      │
│      └── SP2D                                                                                   │
│          └── [parent: SPM]                                                                      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Document Inheritance (Auto-Fill)

```python
DOCUMENT_INHERITANCE = {
    'SPK': {
        'inherit_from': ['paket', 'penyedia', 'item_barang'],
        'auto_fields': {
            'nilai_kontrak': 'paket.nilai_negosiasi',
            'penyedia_nama': 'penyedia.nama',
            'penyedia_alamat': 'penyedia.alamat',
            'items': 'item_barang WHERE paket_id = current',
        }
    },
    
    'SPMK': {
        'inherit_from': ['SPK'],
        'auto_fields': {
            'nomor_spk': 'SPK.nomor',
            'tanggal_spk': 'SPK.tanggal',
            'nilai': 'SPK.nilai',
            'jangka_waktu': 'paket.jangka_waktu',
        }
    },
    
    'BAST': {
        'inherit_from': ['SPK', 'BAHP'],
        'auto_fields': {
            'nomor_spk': 'SPK.nomor',
            'tanggal_spk': 'SPK.tanggal',
            'nilai': 'SPK.nilai',
            'penyedia': 'SPK.penyedia',
            'tanggal_bahp': 'BAHP.tanggal',
        }
    },
    
    'ADENDUM_SPK': {
        'inherit_from': ['SPK'],
        'auto_fields': {
            'nomor_spk_asal': 'SPK.nomor',
            'tanggal_spk_asal': 'SPK.tanggal',
            'nilai_asal': 'SPK.nilai',
            'nomor_adendum': 'AUTO_INCREMENT',
        }
    },
    
    'KUITANSI': {
        'inherit_from': ['SPK', 'BAST'],
        'auto_fields': {
            'nilai': 'paket.nilai_kontrak',
            'terbilang': 'AUTO_TERBILANG(nilai)',
            'penerima': 'penyedia.pemilik_rekening',
        }
    },
    
    'SSP': {
        'inherit_from': ['paket', 'penyedia'],
        'auto_fields': {
            'nilai_dasar': 'paket.nilai_kontrak / 1.11',  # Before PPN
            'ppn': 'nilai_dasar * 0.11',
            'pph': 'AUTO_CALC_PPH(nilai_dasar, jenis_pph)',
        }
    },
    
    'SPP': {
        'inherit_from': ['BAST', 'KUITANSI', 'SSP'],
        'auto_fields': {
            'nomor_bast': 'BAST.nomor',
            'nilai_tagihan': 'paket.nilai_kontrak',
            'potongan_pajak': 'SSP.pph',
            'nilai_bersih': 'nilai_tagihan - potongan_pajak',
        }
    },
}
```

---

## 7. REKOMENDASI UI UNTUK OPERATOR PPK

### A. Dashboard Cepat

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              DASHBOARD PPK - TAMPILAN CEPAT                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📊 RINGKASAN PAKET 2026                                                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ PERSIAPAN   │  │  PEMILIHAN  │  │   KONTRAK   │  │ PELAKSANAAN │  │   SELESAI   │           │
│  │     12      │  │      5      │  │      8      │  │     15      │  │     45      │           │
│  │   paket     │  │   paket     │  │   paket     │  │   paket     │  │   paket     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚡ AKSI CEPAT                                                                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  [➕ Paket Baru]   [📋 Generate Dokumen]   [📤 Export Laporan]   [🔄 Refresh]                  │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 PAKET PERLU TINDAKAN                                                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ 🟡 PKP-001 | Pengadaan ATK | Survey: 2/3 | 💡 Lengkapi survey harga                    │   │
│  │    [📝 Isi Survey] [📄 Lihat Detail]                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ 🟢 PKP-002 | Jasa Konsultan | Penyedia OK | 💡 Buat SPK                                 │   │
│  │    [📝 Buat SPK] [📄 Lihat Detail]                                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │ 🔵 PKP-003 | Alat Lab | Selesai Kerja | 💡 Buat BAHP & BAST                             │   │
│  │    [📝 Buat BAHP] [📝 Buat BAST] [📄 Lihat Detail]                                      │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### B. Paket Detail dengan Progress Visual

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DETAIL PAKET: PKP-001-2026 | Pengadaan Alat Tulis Kantor                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  PROGRESS TIMELINE                                                                              │
│  ════════════════════════════════════════════════════════════════════════════════════════════  │
│                                                                                                 │
│  ✅────────✅────────🔄────────⬜────────⬜────────⬜────────⬜────────⬜                        │
│  SPEK     SURVEY    HPS      KIRIM    PILIH    KONTRAK  PELAKS   SELESAI                       │
│  01/01    05/01    (proses)                                                                    │
│                                                                                                 │
│  KELENGKAPAN DOKUMEN                                                                           │
│  ═══════════════════                                                                           │
│                                                                                                 │
│  FASE PERSIAPAN:                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │ ✅ Spesifikasi Teknis        [📄 Lihat] [📝 Edit] [🖨️ Cetak]                        │      │
│  │ ✅ KAK                       [📄 Lihat] [📝 Edit] [🖨️ Cetak]                        │      │
│  │ 🔲 Survey Harga (2/3)        [📄 Lihat] [📝 Lengkapi]                               │      │
│  │ 🔲 RAB                       [📝 Buat]                                              │      │
│  │ 🔲 HPS                       [📝 Buat] 💡 Lengkapi survey dulu                      │      │
│  │ 🔲 Nota Dinas                [📝 Buat]                                              │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  FASE PEMILIHAN: (Belum aktif - selesaikan Persiapan)                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │ 🔒 Undangan                  [Tersedia setelah Nota Dinas]                           │      │
│  │ 🔒 BA Evaluasi               [Tersedia setelah Nota Dinas]                           │      │
│  │ 🔒 Penetapan Penyedia        [Tersedia setelah Nota Dinas]                           │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  AKSI CEPAT:                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │ [📝 Lengkapi Survey] [📊 Hitung HPS Otomatis] [📋 Generate Semua Dok Persiapan]     │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### C. Form Input Cepat dengan Auto-Fill

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ GENERATE DOKUMEN: SPK                                                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  DATA OTOMATIS (dari Paket & Penyedia):                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │ Nama Paket      : Pengadaan Alat Tulis Kantor                            [Auto] ✅   │      │
│  │ Kode Paket      : PKP-001-2026                                           [Auto] ✅   │      │
│  │ Penyedia        : CV Maju Jaya                                           [Auto] ✅   │      │
│  │ Nilai Kontrak   : Rp 45.500.000                                          [Auto] ✅   │      │
│  │ Jangka Waktu    : 30 hari                                                [Auto] ✅   │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  DATA PERLU INPUT:                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │ Nomor SPK       : [001/SPK/PKP-SRG/I/2026_______] 🔢 Auto-generate                  │      │
│  │ Tanggal SPK     : [28/01/2026_] 📅 Suggested: setelah Penetapan (25/01)             │      │
│  │                                                                                      │      │
│  │ 💡 Tanggal disarankan setelah Penetapan Penyedia (25/01/2026)                       │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  PREVIEW DOKUMEN:                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │                                                                                      │      │
│  │  ┌────────────────────────────────────────────────────────────────────────────────┐ │      │
│  │  │                        SURAT PERINTAH KERJA                                    │ │      │
│  │  │                         Nomor: 001/SPK/PKP-SRG/I/2026                          │ │      │
│  │  │                                                                                │ │      │
│  │  │  Yang bertanda tangan di bawah ini:                                            │ │      │
│  │  │  Nama    : Firdaus Dabamona                                                    │ │      │
│  │  │  Jabatan : PPK pada Politeknik KP Sorong                                       │ │      │
│  │  │  ...                                                                           │ │      │
│  │  └────────────────────────────────────────────────────────────────────────────────┘ │      │
│  │                                                                                      │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  [❌ Batal]                                              [💾 Simpan] [🖨️ Simpan & Cetak]      │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### D. Batch Generate Multiple Documents

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 GENERATE BATCH DOKUMEN                                                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  Paket: PKP-001-2026 | Pengadaan Alat Tulis Kantor                                             │
│                                                                                                 │
│  Pilih dokumen yang akan di-generate:                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐      │
│  │                                                                                      │      │
│  │  FASE PERSIAPAN:                                                                     │      │
│  │  ☑️ Spesifikasi Teknis                                                               │      │
│  │  ☑️ KAK                                                                              │      │
│  │  ☑️ Tabel Survey Harga                                                               │      │
│  │  ☑️ BA Survey Harga                                                                  │      │
│  │  ☑️ RAB                                                                              │      │
│  │  ☑️ HPS                                                                              │      │
│  │  ☑️ Nota Dinas ke PP                                                                 │      │
│  │                                                                                      │      │
│  │  FASE KONTRAK: (Aktif jika Penyedia OK)                                              │      │
│  │  ☑️ SPK                                                                              │      │
│  │  ☑️ SPMK                                                                             │      │
│  │                                                                                      │      │
│  │  FASE SERAH TERIMA: (Aktif jika Pelaksanaan selesai)                                 │      │
│  │  ☐ BAHP                                                                              │      │
│  │  ☐ BAST                                                                              │      │
│  │                                                                                      │      │
│  │  FASE PEMBAYARAN: (Aktif jika BAST ada)                                              │      │
│  │  ☐ Kuitansi                                                                          │      │
│  │  ☐ SSP                                                                               │      │
│  │  ☐ SPP                                                                               │      │
│  │                                                                                      │      │
│  └──────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                 │
│  [☑️ Pilih Semua yang Tersedia] [☐ Batal Pilih Semua]                                         │
│                                                                                                 │
│  Output Format: ○ Word (.docx)  ○ PDF  ● Keduanya                                              │
│                                                                                                 │
│  [❌ Batal]                                    [📋 Generate 7 Dokumen Terpilih]                │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. DATABASE SCHEMA (Simplified)

```sql
-- Tabel utama dengan status workflow
CREATE TABLE paket (
    id INTEGER PRIMARY KEY,
    kode TEXT UNIQUE,
    tahun INTEGER,
    nama TEXT NOT NULL,
    jenis_pengadaan TEXT,
    metode_pengadaan TEXT,
    
    -- Nilai (visibility based on status)
    nilai_pagu REAL,
    nilai_hps REAL,
    nilai_negosiasi REAL,      -- Muncul setelah PEMILIHAN
    nilai_kontrak REAL,         -- Muncul setelah PENYEDIA_OK (auto = negosiasi)
    
    -- Foreign Keys (visibility based on status)
    penyedia_id INTEGER,        -- Muncul setelah PENYEDIA_OK
    ppk_id INTEGER,
    pp_id INTEGER,              -- Pejabat Pengadaan
    
    -- Status & Workflow
    status TEXT DEFAULT 'DRAFT',  -- DRAFT, PERSIAPAN, DIKIRIM, PEMILIHAN, PENYEDIA_OK, KONTRAK_AKTIF, PELAKSANAAN, SERAH_TERIMA, SELESAI
    status_code INTEGER DEFAULT 0,
    
    -- Tanggal (auto-suggest enabled)
    tanggal_spesifikasi DATE,
    tanggal_survey_selesai DATE,
    tanggal_hps DATE,
    tanggal_nota_dinas DATE,
    tanggal_penetapan_penyedia DATE,
    tanggal_kontrak DATE,
    tanggal_spmk DATE,
    tanggal_mulai_kerja DATE,
    tanggal_selesai_kerja DATE,
    tanggal_bahp DATE,
    tanggal_bast DATE,
    
    -- Jangka waktu
    jangka_waktu INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Item barang dengan survey
CREATE TABLE item_barang (
    id INTEGER PRIMARY KEY,
    paket_id INTEGER REFERENCES paket(id),
    nomor_urut INTEGER,
    uraian TEXT,
    spesifikasi TEXT,
    volume REAL,
    satuan TEXT,
    
    -- Survey harga (soft validation: min 3)
    harga_survey1 REAL,
    sumber_survey1 TEXT,
    harga_survey2 REAL,
    sumber_survey2 TEXT,
    harga_survey3 REAL,
    sumber_survey3 TEXT,
    
    -- Calculated
    harga_rata REAL,
    harga_hps REAL,
    harga_negosiasi REAL,
    harga_kontrak REAL,
    
    -- Status
    survey_complete INTEGER DEFAULT 0  -- 1 if >= 3 surveys
);

-- Dokumen timeline
CREATE TABLE dokumen (
    id INTEGER PRIMARY KEY,
    paket_id INTEGER REFERENCES paket(id),
    jenis TEXT,              -- SPEK, KAK, SURVEY, RAB, HPS, SPK, SPMK, BAHP, BAST, etc
    nomor TEXT,
    tanggal DATE,
    keterangan TEXT,
    file_path TEXT,
    status TEXT DEFAULT 'DRAFT',
    parent_dokumen_id INTEGER,  -- For inheritance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Validation warnings log (soft validation)
CREATE TABLE validation_log (
    id INTEGER PRIMARY KEY,
    paket_id INTEGER,
    validation_type TEXT,    -- INFO, WARNING, INCOMPLETE
    field_name TEXT,
    message TEXT,
    is_resolved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## RINGKASAN IMPLEMENTASI

### Prinsip Utama:
1. **SHOW, DON'T BLOCK** - Tampilkan field sesuai fase, jangan kunci keras
2. **SUGGEST, DON'T FORCE** - Sarankan tanggal/nilai, jangan paksa
3. **WARN, DON'T REJECT** - Peringatkan ketidaksesuaian, jangan tolak input
4. **AUTO-FILL, DON'T REPEAT** - Isi otomatis dari data yang ada

### Perubahan dari Versi Sebelumnya:
| Aspek | Versi Lama (Audit Style) | Versi Baru (Helper Style) |
|-------|--------------------------|---------------------------|
| Field Lock | Hard lock berdasarkan status | Hide/Show berdasarkan fase |
| Validation | Block jika tidak sesuai | Warning dengan saran |
| Timeline | Hard sequential | Auto-suggest dengan override |
| HPS | Block sebelum survey | Warning jika survey belum 3 |
| Error | 🚫 Merah, tidak bisa lanjut | 💡 Info, ⚠️ Warning |

### File yang Perlu Diupdate:
1. `app/core/database.py` - Simplify schema, remove hard locks
2. `app/ui/dashboard.py` - Progressive disclosure UI
3. `app/ui/harga_lifecycle_manager.py` - Soft validation
4. `app/templates/engine.py` - Auto-fill from relationships
5. `app/workflow/engine.py` - Status-based visibility

---

*Document Version: 5.0 - PPK Friendly Edition*
*Philosophy: "Membantu PPK, bukan mengaudit PPK"*
*Last Updated: 17 Januari 2026*
