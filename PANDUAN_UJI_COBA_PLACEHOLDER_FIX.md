PANDUAN UJI COBA - PERBAIKAN PLACEHOLDER REPLACEMENT
====================================================

LATAR BELAKANG MASALAH:
-----------------------
Sebelumnya, ketika generate lembar permintaan, dokumen yang dihasilkan masih menampilkan
placeholder template seperti {{item_2_no}}, {{item_2_nama}}, {{nama_ppk}}, dll
bukan data yang sebenarnya dari form.

Sekarang sudah diperbaiki! Semua placeholder akan diganti dengan data aktual.

BAGAIMANA CARA MENGETES:
------------------------

OPSI 1: Menggunakan Test Script
================================
1. Buka PowerShell di folder aplikasi
2. Jalankan perintah:
   
   .\.venv\Scripts\python.exe test_full_integration.py

3. Output akan menunjukkan:
   ✓ Merge successful
   ✓ NO UNREPLACED PLACEHOLDERS!
   ✓ 9 of 9 values verified

4. Buka file hasil di: output/dokumen/test_full_integration.docx
   Verify bahwa semua field terisi dengan benar


OPSI 2: Menggunakan GUI Aplikasi (REKOMENDASI)
===============================================
1. Jalankan aplikasi: python main.py
2. Masuk ke menu untuk generate dokumen
3. Isi form dengan data:
   - Nama Kegiatan: "Test Lembar Permintaan"
   - Tanggal: Pilih tanggal hari ini
   - Penerima: Pilih nama pegawai
   - Rincian: Tambahkan 2-3 item dengan data berikut:
     
     Item 1:
       - Uraian: Kertas A4 Putih
       - Volume: 10
       - Satuan: rim
       - Harga: 50000

     Item 2:
       - Uraian: Tinta Printer
       - Volume: 5
       - Satuan: buah
       - Harga: 80000

     Item 3:
       - Uraian: Ballpoint
       - Volume: 100
       - Satuan: buah
       - Harga: 2000

4. Klik "Generate Dokumen"
5. Klik "Buka Dokumen" untuk membuka hasil
6. Verify semua data terisi:
   
   HEADER (Di atas):
   ✓ Hari/Tanggal: "15 Januari 2024" (bukan placeholder)
   ✓ Unit Kerja: "Dinas Pendidikan" (bukan placeholder)
   ✓ Sumber Dana: "APBD 2024" (bukan placeholder)
   
   TABEL RINCIAN:
   ✓ Row 1: Kertas A4 Putih | 10 | rim | Rp 50.000 | Rp 500.000
   ✓ Row 2: Tinta Printer | 5 | buah | Rp 80.000 | Rp 400.000
   ✓ Row 3: Ballpoint | 100 | buah | Rp 2.000 | Rp 200.000
   ✓ Row 4-5: KOSONG (bukan placeholder kosong, benar-benar kosong)
   ✓ Subtotal: Rp 1.100.000
   ✓ PPN 10%: Rp 110.000
   ✓ TOTAL: Rp 1.210.000
   
   PENANDATANGAN (Di bawah):
   ✓ Pengajuan: [Nama Penerima]
   ✓ Verifikator: [Nama PPK dari Data Satker]
   ✓ PPK: [Nama PPK]
   ✓ Atasan: [Nama Pimpinan/KPA]
   ✓ KPA: [Nama KPA]

EXPECTED BEHAVIOR SETELAH PERBAIKAN:
-----------------------------------

SEBELUM PERBAIKAN:
- Dokumen menampilkan: {{item_2_no}} {{item_2_nama}} {{item_2_harga}}
- Header menampilkan: : (colon tanpa value)
- Penandatangan menampilkan: {{nama_ppk}} {{nama_kpa}}

SESUDAH PERBAIKAN:
- Dokumen menampilkan: [nilai yang sebenarnya dari form]
- Header menampilkan: "Dinas Pendidikan Kota" bukan colon
- Penandatangan menampilkan: nama-nama yang sebenarnya dari database

APA YANG BERUBAH DI CODE:
------------------------

File 1: app/services/dokumen_generator.py
-----------------------------------------
1. Tambah method _flatten_rincian_items():
   - Mengubah rincian_items[list] menjadi item_1_no, item_1_nama, dll
   - Sehingga template placeholder {{item_1_no}} bisa match dengan data key 'item_1_no'

2. Modify merge_word_document():
   - Panggil _flatten_rincian_items() di awal
   - Ini memastikan semua indexed placeholders ter-replace

File 2: app/ui/dialogs/dokumen_dialog.py
---------------------------------------
1. Update _collect_data():
   - Tambah field 'hari_tanggal' dengan format Indonesia
   - Tambah field 'unit_kerja' dari satker
   - Tambah field 'sumber_dana' dari satker
   - Tambah field penandatangan dari satker
   - Hitung subtotal, ppn, total dengan benar

2. Tambah method _format_tanggal_indonesia():
   - Format QDate ke "15 Januari 2024" format

TESTING CHECKLIST:
------------------
[] Test 1: Run test_full_integration.py - harus NO UNREPLACED PLACEHOLDERS
[] Test 2: Generate dokumen via UI dengan 3 items
[] Test 3: Buka dokumen hasil dan cek:
   - Header fields terisi (tidak ada colon kosong)
   - Rincian items terisi dengan benar
   - Item 4-5 kosong bersih (tidak ada placeholder)
   - Subtotal/PPN/Total benar
   - Penandatangan terisi semua
[] Test 4: Database - cek dokumen tersimpan di database

JIKA ADA MASALAH:
-----------------
Jika placeholder masih muncul di dokumen:
1. Check template file di templates/word/lembar_permintaan.docx
2. Verify placeholder format adalah {{nama}} bukan [nama] atau {nama}
3. Cek data key match dengan placeholder name
4. Run debug_placeholders.py untuk list semua placeholder di template
5. Run test_placeholder_merge.py untuk test replacement

CATATAN PENTING:
----------------
- Perbaikan ini HANYA berlaku untuk dokumen yang menggunakan template dengan indexed placeholders
- Template lain yang menggunakan {{placeholder}} format akan tetap bekerja normal
- Database integration sudah berjalan sebelumnya, tidak ada perubahan di database layer
