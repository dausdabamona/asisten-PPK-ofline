"""
Dokumentasi DIPA Selector - Data Struktur dan Tampilan
========================================================

DIPA Selector adalah fitur untuk memilih data DIPA dan secara otomatis
menghitung Estimasi Biaya dan MAK (Mata Anggaran Kegiatan).

1. KOMPONEN UTAMA
================

A. DipaSelectorDialog (Dialog Modal)
   Tempat user memilih item DIPA dengan fitur:
   
   Input:
   - Search/Filter: Cari berdasarkan kode akun, kode detail, atau uraian
   - Filter Level: Pilih Level 7 (Akun) atau Level 8 (Detail)
   
   Output Table Columns:
   - Checkbox: Untuk multi-select
   - Kode Akun: Kode rekening anggaran (misal: 5.1.01.05.01)
   - Kode Detail: Nomor detail akun (misal: 001, 002)
   - MAK: Mata Anggaran Kegiatan (Kode Akun.Kode Detail)
   - Uraian: Deskripsi item anggaran
   - Jumlah: Besaran anggaran dalam Rupiah
   - Level: Level hierarki (Level 7 atau Level 8)
   
   Summary Display:
   - Total Biaya: Jumlah total dari semua item yang dipilih (auto-calculated)
   - MAK Terpilih: Daftar kode MAK yang dipilih (comma-separated)
   - Jumlah Item: Berapa banyak item yang dipilih


B. DipaSelectionWidget (Widget dalam Form)
   Widget embedded dalam Transaksi Form (UP/TUP):
   
   Main Button:
   - "📋 Pilih dari DIPA": Buka dialog untuk memilih DIPA items
   
   Selected Items Table:
   - MAK: Kode MAK terpilih
   - Uraian: Deskripsi kegiatan
   - Jumlah: Besaran biaya (format Rupiah)
   - Persentase: % dari total biaya
   - Tombol Hapus: Remove item dari selection
   
   Summary Section:
   - Total Estimasi Biaya: Auto-filled dari DIPA (read-only)
     Format: Rp X.XXX.XXX (separator dengan titik)
   - Kode MAK: Auto-filled dari DIPA (read-only)
     Format: MAK1, MAK2, MAK3 (comma-separated)


2. DATA YANG DITAMPILKAN
=======================

Pada Informasi Keuangan Form (Setelah Integrasi):

Input Fields:
┌─────────────────────────────────────────────────────────┐
│ [📋 Pilih dari DIPA]                                    │
│                                                         │
│ Selected Items:                                         │
│ ┌─────────────┬──────────────┬──────────┬────────────┐ │
│ │ MAK         │ Uraian       │ Jumlah   │ Persentase │ │
│ ├─────────────┼──────────────┼──────────┼────────────┤ │
│ │ 5.1.01.02   │ Gaji/Upah    │ Rp 50M   │ 60.0%      │ │
│ │ 5.1.01.03   │ Tunjangan    │ Rp 30M   │ 35.0%      │ │
│ │ 5.1.01.04   │ Insentif     │ Rp 5M    │ 5.0%       │ │
│ └─────────────┴──────────────┴──────────┴────────────┘ │
│                                                         │
│ Summary DIPA:                                           │
│ Total Estimasi Biaya *        [Rp 85,000,000 ]        │
│ Kode MAK/Akun *               [5.1.01.02, 5.1.01.03] │
│ Uraian Kegiatan (MAK)         [Text area...]          │
│                                                         │
│ Tanggal Kegiatan:                                       │
│ Mulai: [YYYY-MM-DD] Selesai: [YYYY-MM-DD]            │
└─────────────────────────────────────────────────────────┘


3. FITUR UTAMA
==============

A. Multi-Selection DIPA
   - User bisa memilih beberapa item DIPA sekaligus
   - Total biaya akan dijumlahkan otomatis
   - MAK akan dikompilasi dari semua item terpilih

B. Auto-Calculate Total Biaya
   - Formula: SUM(jumlah untuk setiap item terpilih)
   - Display format: Rp X.XXX.XXX dengan separator titik
   - Validasi: Untuk UP, maksimal Rp 50 juta

C. Auto-Extract MAK Codes
   - Setiap item DIPA memiliki MAK unik
   - Jika multiple items dengan MAK sama, hanya tampil sekali
   - Format display: Comma-separated list
   - Duplikasi MAK dihilangkan otomatis

D. Detail Breakdown
   - Setiap selected item ditampilkan dengan detail
   - Percentage calculation: (Item Biaya / Total Biaya) × 100%
   - Uraian dari setiap item disimpan untuk reference


4. DATA SOURCES
===============

Database Table: pagu_anggaran
├─ id: Database record ID
├─ tahun_anggaran: Tahun anggaran (2026, 2027, dst)
├─ kode_akun: Kode rekening anggaran (5 digit + separator)
├─ kode_detail: Nomor detail per akun (biasanya 3 digit)
├─ nomor_mak: MAK = Mata Anggaran Kegiatan (kode_akun.kode_detail)
├─ uraian: Deskripsi/nama kegiatan
├─ jumlah: Nominal anggaran dalam Rupiah
├─ level_kode: Level hierarki (7=Akun, 8=Detail, dll)
├─ parent_id: Reference ke parent node
└─ sumber_dana: Jenis sumber dana (RM, PNBP, BLU, dll)


5. WORKFLOW PENGGUNAAN
======================

Step 1: User membuka Form UP/TUP
        ↓
Step 2: User klik tombol "📋 Pilih dari DIPA"
        ↓
Step 3: Dialog DipaSelectorDialog terbuka menampilkan:
        - Daftar semua DIPA items untuk tahun berjalan
        - Filter dan search box
        ↓
Step 4: User melakukan:
        - Filter by level (Akun vs Detail)
        - Search berdasarkan kode atau uraian
        - Multi-select items yang diinginkan
        ↓
Step 5: System automatically menampilkan:
        - Total Biaya (jumlah dari selected items)
        - MAK Terpilih (list kode dari selected items)
        - Item Count
        ↓
Step 6: User klik "Gunakan Pilihan"
        ↓
Step 7: Widget DipaSelectionWidget update dengan:
        - Tabel selected items dengan breakdown
        - Persentase per item
        ↓
Step 8: Form fields auto-fill:
        - estimasi_input = Total dari DIPA
        - kode_mak_input = MAK codes
        - ket_mak_input = Uraian dari items
        ↓
Step 9: User bisa:
        - Menambah/mengurangi items
        - Edit field lain (nama kegiatan, tanggal, dll)
        - Submit form
        ↓
Step 10: Data tersimpan dengan struktur:
         {
           'mekanisme': 'UP',
           'estimasi_biaya': 85000000,    (dari DIPA)
           'kode_mak': '5.1.01.02, 5.1.01.03',  (dari DIPA)
           'nama_kegiatan': 'Gaji Operasional',
           'dipa_items': [
             {'dipa_id': 123, 'nomor_mak': '5.1.01.02', 'jumlah': 50000000},
             {'dipa_id': 124, 'nomor_mak': '5.1.01.03', 'jumlah': 30000000},
             ...
           ],
           ...
         }


6. VALIDASI DATA
================

A. Pada DIPA Selection Dialog:
   - Harus select minimal 1 item (error: "Pilih minimal 1 item DIPA!")
   - Hanya items dengan jumlah > 0 yang ditampilkan
   - Filter hanya untuk tahun anggaran saat ini

B. Pada Form Level (UP/TUP):
   - Estimasi biaya dari DIPA tidak boleh exceed batas UP (Rp 50 juta)
   - MAK code wajib terisi (tidak boleh kosong)
   - Tanggal kegiatan harus valid

C. Consistency Checks:
   - Jika user ubah estimasi_biaya manual, warning mungkin ditampilkan
   - MAK codes tidak boleh berisi duplikasi


7. INTEGRASI DENGAN SISTEM
===========================

A. Database Relationship:
   pencairan_transaksi
   ├─ estimasi_biaya (dari DIPA.jumlah)
   ├─ kode_mak (dari DIPA.nomor_mak)
   ├─ keterangan_kegiatan (dari DIPA.uraian)
   └─ dipa_references (junction table untuk tracking)
       ├─ transaksi_id
       ├─ pagu_anggaran_id
       └─ jumlah_allocation

B. Document Generation:
   MAK code akan digunakan dalam pembuatan dokumen:
   - Surat Pertanggungjawaban (SPJ)
   - Nota Dinas
   - Kuitansi
   - Berita Acara

C. Reporting:
   - Realisasi dapat ditrack per MAK
   - Analisis spending per kode akun
   - Validasi anggaran vs realisasi


8. CONTOH DATA DIPA
===================

Hierarki DIPA:
Level 1: Program (5)
  Level 2: Kegiatan (5.1)
    Level 3: KRO (5.1.01)
      Level 4: RO (5.1.01.01)
        Level 5: Komponen (5.1.01.01.1)
          Level 6: SubKomponen (5.1.01.01.1.1)
            Level 7: Akun (5.1.01.01.1.1.01)
              ├─ MAK 5.1.01.01.1.1.01.001: Gaji PNS          = Rp 1,200,000,000
              ├─ MAK 5.1.01.01.1.1.01.002: Tunjangan         = Rp 450,000,000
              └─ MAK 5.1.01.01.1.1.01.003: BPJS             = Rp 300,000,000
            Level 8: Detail (contoh MAK detail)
              └─ MAK 5.1.01.01.1.1.01.001.A: Gaji Regular   = Rp 800,000,000

User memilih:
- MAK 5.1.01.01.1.1.01.001: Rp 1,200,000,000 (60%)
- MAK 5.1.01.01.1.1.01.002: Rp 450,000,000   (22.5%)
- MAK 5.1.01.01.1.1.01.003: Rp 300,000,000   (15%)

Result:
- Total Estimasi: Rp 1,950,000,000
- MAK Codes: 5.1.01.01.1.1.01.001, 5.1.01.01.1.1.01.002, 5.1.01.01.1.1.01.003
- Breakdown detail untuk setiap item tersimpan


9. FUTURE ENHANCEMENTS
======================

- Batch import multiple DIPA selections
- Template untuk common DIPA combinations
- History/recommendation based on previous selections
- Budget remaining indicator per MAK
- Approval workflow based on MAK codes
"""

# === TECHNICAL REFERENCE ===

"""
Database Query untuk DIPA Data:

SELECT 
    id, kode_akun, kode_detail, uraian, jumlah, 
    level_kode, nomor_mak
FROM pagu_anggaran
WHERE tahun_anggaran = :tahun
    AND level_kode IN (7, 8)    -- Akun dan Detail levels
    AND jumlah > 0               -- Only non-zero budgets
ORDER BY kode_akun, kode_detail, uraian

Hasil untuk tahun 2026:
id | kode_akun   | kode_detail | uraian              | jumlah      | level | nomor_mak
---|-------------|-------------|---------------------|-------------|-------|------------------
1  | 5.1.01.05   | 01          | Gaji Pegawai       | 50000000    | 8     | 5.1.01.05.01
2  | 5.1.01.05   | 02          | Tunjangan Hari Tua  | 30000000    | 8     | 5.1.01.05.02
3  | 5.1.01.06   | 01          | Perjalanan Dinas   | 15000000    | 8     | 5.1.01.06.01
...
"""
