# PANDUAN PLACEHOLDER TEMPLATE
## PPK Document Factory v3.0

---

## 📋 FORMAT PLACEHOLDER

### Format Dasar
```
{{nama_placeholder}}
```

### Format dengan Formatter
```
{{placeholder:format}}
```

### Formatter yang Tersedia

| Format | Contoh Input | Hasil Output |
|--------|--------------|--------------|
| `rupiah` | 150000000 | Rp 150.000.000 |
| `angka` | 150000000 | 150.000.000 |
| `terbilang` | 150000000 | seratus lima puluh juta rupiah |
| `tanggal_long` | 2026-01-15 | 15 Januari 2026 |
| `tanggal_short` | 2026-01-15 | 15/01/2026 |
| `tanggal_full` | 2026-01-15 | Rabu, 15 Januari 2026 |
| `nip` | 197201031995031001 | 19720103 199503 1 001 |
| `npwp` | 012345678951000 | 01.234.567.8-951.000 |
| `upper` | teks | TEKS |
| `lower` | TEKS | teks |
| `title` | teks contoh | Teks Contoh |

---

## 📄 PLACEHOLDER PER TEMPLATE

### 1. SPESIFIKASI TEKNIS (spesifikasi_teknis.docx)

**Header/Kop Surat:**
- `{{satker_kementerian}}` - Nama kementerian
- `{{satker_eselon1}}` - Nama unit eselon 1
- `{{satker_nama}}` - Nama satuan kerja
- `{{satker_alamat}}` - Alamat satker
- `{{satker_kota}}` - Kota satker
- `{{satker_telepon}}` - Telepon satker
- `{{satker_email}}` - Email satker

**Isi Dokumen:**
- `{{nama_paket}}` - Nama pekerjaan
- `{{latar_belakang}}` - Latar belakang pekerjaan
- `{{maksud_tujuan}}` - Maksud dan tujuan
- `{{target_sasaran}}` - Target/sasaran
- `{{ruang_lingkup}}` - Ruang lingkup pekerjaan
- `{{spesifikasi_teknis}}` - Detail spesifikasi teknis
- `{{jangka_waktu}}` - Jangka waktu (angka)
- `{{jangka_waktu_terbilang}}` - Jangka waktu (terbilang)
- `{{sumber_dana}}` - Sumber dana (DIPA/APBN)
- `{{tahun_anggaran}}` - Tahun anggaran
- `{{kode_akun}}` - Kode akun/MAK

**Item Barang (tabel):**
- `{{item.nama_item}}` - Nama barang/jasa
- `{{item.spesifikasi}}` - Spesifikasi item
- `{{item.satuan}}` - Satuan
- `{{item.volume}}` - Volume/jumlah
- `{{item.keterangan}}` - Keterangan

**Tanda Tangan:**
- `{{tanggal_dokumen:tanggal_long}}` - Tanggal dokumen
- `{{ppk_nama}}` - Nama PPK
- `{{ppk_nip:nip}}` - NIP PPK

---

### 2. KERANGKA ACUAN KERJA (kak.docx)

**Tambahan dari Spesifikasi:**
- `{{nilai_pagu:rupiah}}` - Nilai pagu anggaran
- `{{nilai_pagu:terbilang}}` - Nilai pagu terbilang
- `{{maksud_pekerjaan}}` - Maksud pekerjaan
- `{{tujuan_pekerjaan}}` - Tujuan pekerjaan
- `{{output_pekerjaan}}` - Output/keluaran
- `{{tenaga_pelaksana}}` - Tenaga ahli/pelaksana
- `{{peralatan}}` - Peralatan yang digunakan
- `{{metode_pelaksanaan}}` - Metode pelaksanaan
- `{{ketentuan_laporan}}` - Ketentuan pelaporan

---

### 3. SURAT PERINTAH KERJA (spk.docx)

**Nomor Dokumen:**
- `{{nomor_spk}}` - Nomor SPK

**Pihak Pertama (PPK):**
- `{{ppk_nama}}` - Nama PPK
- `{{ppk_nip:nip}}` - NIP PPK
- `{{satker_alamat}}` - Alamat satker
- `{{satker_kota}}` - Kota

**Pihak Kedua (Penyedia):**
- `{{penyedia_nama}}` - Nama perusahaan
- `{{direktur_nama}}` - Nama direktur
- `{{direktur_jabatan}}` - Jabatan (Direktur/Direktur Utama)
- `{{penyedia_alamat}}` - Alamat perusahaan
- `{{penyedia_kota}}` - Kota

**Detail Pekerjaan:**
- `{{nama_paket}}` - Nama pekerjaan
- `{{ruang_lingkup}}` - Lingkup pekerjaan
- `{{nilai_kontrak:rupiah}}` - Nilai kontrak (DPP)
- `{{nilai_kontrak:terbilang}}` - Nilai kontrak terbilang
- `{{nilai_ppn:rupiah}}` - PPN 11%
- `{{nilai_bruto:rupiah}}` - Total (DPP + PPN)
- `{{nilai_bruto:terbilang}}` - Total terbilang
- `{{sumber_dana}}` - Sumber dana
- `{{tahun_anggaran}}` - Tahun anggaran
- `{{kode_akun}}` - Kode akun
- `{{jangka_waktu}}` - Jangka waktu (hari)
- `{{tanggal_mulai:tanggal_long}}` - Tanggal mulai
- `{{tanggal_selesai:tanggal_long}}` - Tanggal selesai

---

### 4. SURAT PERINTAH MULAI KERJA (spmk.docx)

**Referensi SPK:**
- `{{nomor_spmk}}` - Nomor SPMK
- `{{nomor_spk}}` - Nomor SPK referensi
- `{{tanggal_spk:tanggal_long}}` - Tanggal SPK

**Penyedia:**
- `{{penyedia_nama}}` - Nama perusahaan
- `{{direktur_nama}}` - Nama direktur
- `{{penyedia_alamat}}` - Alamat
- `{{penyedia_kota}}` - Kota
- `{{penyedia_npwp:npwp}}` - NPWP penyedia

**Penerima SPMK:**
- `{{tanggal_terima_spmk:tanggal_long}}` - Tanggal terima SPMK

---

### 5. BERITA ACARA HASIL PEMERIKSAAN (bahp.docx)

**Header:**
- `{{nomor_bahp}}` - Nomor BAHP
- `{{hari_pemeriksaan}}` - Hari pemeriksaan
- `{{tanggal_bahp:tanggal_long}}` - Tanggal pemeriksaan

**Tim Pemeriksa:**
- `{{pemeriksa1_nama}}` - Nama pemeriksa 1 (Ketua)
- `{{pemeriksa1_nip:nip}}` - NIP pemeriksa 1
- `{{pemeriksa2_nama}}` - Nama pemeriksa 2 (Sekretaris)
- `{{pemeriksa2_nip:nip}}` - NIP pemeriksa 2
- `{{pemeriksa3_nama}}` - Nama pemeriksa 3 (Anggota)
- `{{pemeriksa3_nip:nip}}` - NIP pemeriksa 3

**Hasil:**
- `{{hasil_pemeriksaan}}` - Narasi hasil pemeriksaan
- `{{kesimpulan_pemeriksaan}}` - Kesimpulan
- `{{lokasi_pekerjaan}}` - Lokasi pekerjaan

**Rincian Item:**
- `{{item.nama_item}}` - Nama item
- `{{item.satuan}}` - Satuan
- `{{item.volume}}` - Volume SPK
- `{{item.volume_diterima}}` - Volume diterima
- `{{item.keterangan}}` - Keterangan

---

### 6. BERITA ACARA SERAH TERIMA (bast.docx)

**Header:**
- `{{nomor_bast}}` - Nomor BAST
- `{{hari_serah_terima}}` - Hari serah terima
- `{{tanggal_bast:tanggal_long}}` - Tanggal BAST

**Referensi:**
- `{{nomor_spk}}` - Nomor SPK
- `{{tanggal_spk:tanggal_long}}` - Tanggal SPK
- `{{nomor_bahp}}` - Nomor BAHP
- `{{tanggal_bahp:tanggal_long}}` - Tanggal BAHP

**Rincian Item:**
- `{{item.nama_item}}` - Nama barang/jasa
- `{{item.satuan}}` - Satuan
- `{{item.volume}}` - Volume
- `{{item.kondisi}}` - Kondisi (Baik/Lengkap)

---

### 7. SPP-LS (spp_ls.docx)

**Header:**
- `{{nomor_spp}}` - Nomor SPP
- `{{tanggal_spp:tanggal_long}}` - Tanggal SPP

**Rincian Pembayaran:**
- `{{nilai_kontrak:rupiah}}` - Nilai DPP
- `{{nilai_ppn:rupiah}}` - PPN 11%
- `{{nilai_bruto:rupiah}}` - Nilai Bruto
- `{{jenis_pph}}` - Jenis PPh (PPh 22/23/21)
- `{{tarif_pph_persen}}` - Tarif PPh (1.5/2/5)
- `{{nilai_pph:rupiah}}` - Nilai PPh
- `{{nilai_bersih:rupiah}}` - Nilai Bersih
- `{{nilai_bersih:terbilang}}` - Terbilang

**Rekening Tujuan:**
- `{{penyedia_bank}}` - Nama bank
- `{{penyedia_rekening}}` - Nomor rekening
- `{{penyedia_nama_rekening}}` - Nama rekening
- `{{penyedia_npwp:npwp}}` - NPWP

**Tanda Tangan:**
- `{{ppspm_nama}}` - Nama PPSPM
- `{{ppspm_nip:nip}}` - NIP PPSPM

---

### 8. DRPP (drpp.docx)

**Header:**
- `{{nomor_drpp}}` - Nomor DRPP

**Tabel:**
- Sama dengan SPP-LS

---

### 9. KUITANSI (kuitansi.docx)

**Header:**
- `{{nomor_kuitansi}}` - Nomor kuitansi
- `{{tanggal_kuitansi:tanggal_long}}` - Tanggal kuitansi

**Tanda Tangan:**
- `{{bendahara_nama}}` - Nama bendahara
- `{{bendahara_nip:nip}}` - NIP bendahara

---

### 10. SURVEY HARGA (survey_harga.xlsx)

**Header:**
- `{{tanggal_survey:tanggal_long}}` - Tanggal survey

**Lokasi Survey:**
- `{{survey1_toko}}` - Nama toko 1
- `{{survey1_alamat}}` - Alamat toko 1
- `{{survey2_toko}}` - Nama toko 2
- `{{survey2_alamat}}` - Alamat toko 2
- `{{survey3_toko}}` - Nama toko 3
- `{{survey3_alamat}}` - Alamat toko 3

**Item Survey:**
- `{{item.nama_item}}` - Nama barang
- `{{item.spesifikasi}}` - Spesifikasi
- `{{item.satuan}}` - Satuan
- `{{item.volume}}` - Volume
- `{{item.harga_survey1}}` - Harga toko 1
- `{{item.harga_survey2}}` - Harga toko 2
- `{{item.harga_survey3}}` - Harga toko 3
- `{{item.harga_rata}}` - Harga rata-rata
- `{{item.jumlah}}` - Jumlah (volume x harga rata)
- `{{total_survey}}` - Total survey

**Surveyor:**
- `{{surveyor_nama}}` - Nama surveyor
- `{{surveyor_nip:nip}}` - NIP surveyor

---

### 11. HPS (hps.xlsx)

**Header:**
- `{{tanggal_hps:tanggal_long}}` - Tanggal HPS

**Item HPS:**
- `{{item.nama_item}}` - Nama barang/jasa
- `{{item.spesifikasi}}` - Spesifikasi
- `{{item.satuan}}` - Satuan
- `{{item.volume}}` - Volume
- `{{item.harga_satuan}}` - Harga satuan
- `{{item.jumlah}}` - Jumlah

**Total:**
- `{{subtotal_hps}}` - Subtotal sebelum PPN
- `{{ppn_hps}}` - PPN 11%
- `{{nilai_hps}}` - Total HPS
- `{{nilai_hps:terbilang}}` - Terbilang

---

### 12. SSP PPN & PPh (ssp.xlsx)

**Sheet 1 - SSP PPN:**
- `{{satker_npwp:npwp}}` - NPWP Satker (pemotong)
- `{{bulan_pajak}}` - Masa pajak (Januari, Februari, dst)
- `{{nilai_kontrak:rupiah}}` - DPP
- `{{nilai_ppn:rupiah}}` - Jumlah PPN
- `{{nilai_ppn:terbilang}}` - Terbilang

**Sheet 2 - SSP PPh:**
- `{{jenis_pph}}` - Jenis PPh
- `{{kode_akun_pph}}` - Kode akun PPh
- `{{kode_jenis_setoran_pph}}` - Kode jenis setoran
- `{{tarif_pph_persen}}` - Tarif PPh (%)
- `{{nilai_pph:rupiah}}` - Jumlah PPh
- `{{nilai_pph:terbilang}}` - Terbilang

---

## 🔧 CARA MENGGUNAKAN

### Di Template Word:
1. Buka file .docx dengan Microsoft Word
2. Ketik placeholder di posisi yang diinginkan
3. Contoh: Ketik `{{nama_paket}}` di bagian judul
4. Simpan file

### Di Template Excel:
1. Buka file .xlsx dengan Microsoft Excel
2. Ketik placeholder di cell yang diinginkan
3. Untuk angka, gunakan format: `{{nilai_kontrak}}`
4. Untuk format rupiah: `{{nilai_kontrak:rupiah}}`
5. Simpan file

### Upload Template:
1. Buka aplikasi PPK Document Factory
2. Masuk ke **Tools → Template Manager**
3. Pilih jenis dokumen
4. Browse file template
5. Klik **Upload**
6. Template lama otomatis di-backup

---

## ⚠️ CATATAN PENTING

1. **Penulisan Placeholder:**
   - Harus menggunakan kurung kurawal ganda: `{{...}}`
   - Case-sensitive: `{{Nama_Paket}}` ≠ `{{nama_paket}}`
   - Tidak boleh ada spasi: `{{ nama_paket }}` ❌

2. **Placeholder Item (untuk tabel):**
   - Gunakan prefix `item.`: `{{item.nama_item}}`
   - Baris akan di-duplikasi sesuai jumlah item

3. **Format Tanggal:**
   - Input harus format ISO: `YYYY-MM-DD`
   - Contoh: `2026-01-15`

4. **Format Angka:**
   - Input harus angka murni: `150000000`
   - Gunakan formatter untuk format tampilan

---

**PPK Document Factory v3.0** - Template-Driven Procurement Workflow System
