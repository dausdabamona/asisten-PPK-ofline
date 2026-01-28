# PANDUAN KUITANSI UNTUK SPM LAINNYA

## Daftar Isi
1. [Pengenalan](#pengenalan)
2. [Jenis Kuitansi](#jenis-kuitansi)
3. [Placeholder yang Digunakan](#placeholder-yang-digunakan)
4. [Langkah Pembuatan Kuitansi](#langkah-pembuatan-kuitansi)
5. [Contoh Penggunaan](#contoh-penggunaan)
6. [Catatan Penting](#catatan-penting)

---

## Pengenalan

Kuitansi untuk SPM Lainnya adalah dokumen bukti penerimaan uang yang digunakan untuk pengajuan SPM (Surat Permintaan Pembayaran) dalam kategori pembayaran yang tidak termasuk dalam swakelola, kontrak barang/jasa, atau konstruksi.

Template ini mendukung berbagai jenis pembayaran seperti:
- **Honorarium** (Narasumber, Moderator, Panitia, Tim Kerja, dll)
- **Jamuan Tamu**
- **PJLP** (Pegawai Jumlah Lumpsum Pembayaran)
- **Perjalanan Dinas**
- **Lainnya** (Pembayaran ad-hoc lainnya)

---

## Jenis Kuitansi

### 1. Kuitansi Uang Muka (kuitansi_uang_muka_spm_lainnya.docx)

**Tujuan**: Bukti penerimaan uang muka untuk pembayaran jenis SPM Lainnya.

**Digunakan ketika**:
- Ada pembayaran yang harus didahului dengan uang muka
- Penerima menerima dana sebelum melakukan/menyelesaikan kegiatan
- Memerlukan pertanggungjawaban sisa uang muka dalam kuitansi rampung

**Struktur dokumen**:
- A. Data DIPA (satker, akun, kegiatan)
- B. Data Kuitansi (nomor, jumlah uang muka, terbilang)
- C. Data Penerima (nama, NIP, jabatan)
- D. Dasar Pembayaran (SK KPA, dasar hukum)
- E. Pengesahan Pembayaran (TTD PPK, Bendahara, Penerima)

### 2. Kuitansi Rampung (kuitansi_rampung_spm_lainnya.docx)

**Tujuan**: Bukti pembayaran final/rampung untuk SPM Lainnya.

**Digunakan ketika**:
- Penerima telah menyelesaikan kegiatan dan menyerahkan laporan
- Ada pembayaran tambahan atau penyesuaian dari rencana awal
- Memperhitungkan uang muka yang telah diterima sebelumnya
- Menentukan sisa pembayaran yang masih harus dibayarkan

**Struktur dokumen**:
- A. Data DIPA
- B. Data Penerima Pembayaran
- C. Rincian Pembayaran (uang muka, biaya tambahan, total)
- D. Ringkasan Pembayaran (total - uang muka = pembayaran rampung)
- E. Dasar Pembayaran
- F. Pengesahan Pembayaran

---

## Placeholder yang Digunakan

### Data Satker/DIPA
| Placeholder | Deskripsi | Contoh |
|---|---|---|
| `{{kementerian}}` | Nama kementerian | Kementerian Pertanian |
| `{{eselon1}}` | Eselon 1 | Dirjen Peternakan |
| `{{satker_nama}}` | Nama satuan kerja | Dinas Peternakan Provinsi Jawa Tengah |
| `{{satker_kode}}` | Kode satker | 123.456.789.001 |
| `{{satker_alamat}}` | Alamat satker | Jln. Pemuda No. 123 |
| `{{satker_kota}}` | Kota satker | Semarang |
| `{{tahun_anggaran}}` | Tahun anggaran | 2026 |
| `{{sumber_dana}}` | Sumber dana | APBN/APBD |
| `{{kode_akun}}` | Kode akun/MAK | 5.2.1.01.01 |

### Data Pembayaran
| Placeholder | Deskripsi | Contoh |
|---|---|---|
| `{{jenis_pembayaran_nama}}` | Jenis pembayaran | Honorarium Narasumber |
| `{{perihal}}` | Perihal/keperluan | Honorarium Narasumber Workshop Perternakan |
| `{{nomor_kuitansi}}` | Nomor kuitansi | KTN-2026/001 |
| `{{nomor_sk_kpa}}` | Nomor SK KPA | SK-KPA/001/2026 |
| `{{tanggal_sk_kpa}}` | Tanggal SK KPA | 5 Januari 2026 |
| `{{dasar_pembayaran}}` | Dasar hukum pembayaran | Permendagri No. 12 Tahun 2023 |

### Data Uang/Biaya
| Placeholder | Deskripsi | Format |
|---|---|---|
| `{{uang_muka_format}}` | Jumlah uang muka | Rp 50.000.000,00 |
| `{{uang_muka_terbilang}}` | Uang muka dalam kata-kata | Lima puluh juta rupiah |
| `{{biaya_tambahan_format}}` | Biaya tambahan/pengganti | Rp 10.000.000,00 |
| `{{total_biaya_format}}` | Total biaya keseluruhan | Rp 60.000.000,00 |
| `{{pembayaran_rampung_format}}` | Pembayaran rampung | Rp 10.000.000,00 |
| `{{pembayaran_rampung_terbilang}}` | Pembayaran rampung dalam kata-kata | Sepuluh juta rupiah |

### Data Penerima
| Placeholder | Deskripsi | Contoh |
|---|---|---|
| `{{penerima_nama}}` | Nama penerima | Budi Santoso, S.P. |
| `{{penerima_nip}}` | NIP/Identitas penerima | 19800115 200801 1 001 |
| `{{penerima_jabatan}}` | Jabatan penerima | Narasumber |

### Data Penandatangan
| Placeholder | Deskripsi | Contoh |
|---|---|---|
| `{{ppk_nama}}` | Nama PPK | Rina Wijaya, S.H. |
| `{{ppk_nip}}` | NIP PPK | 19850220 201001 2 002 |
| `{{bendahara_nama}}` | Nama bendahara | Ahmad Riyanto, A.Md. |
| `{{bendahara_nip}}` | NIP bendahara | 19800605 200501 1 001 |

### Data Tanggal
| Placeholder | Deskripsi | Format |
|---|---|---|
| `{{tanggal_kuitansi}}` | Tanggal kuitansi | 10 Januari 2026 |
| `{{tanggal_sk_kpa}}` | Tanggal SK KPA | 5 Januari 2026 |

---

## Langkah Pembuatan Kuitansi

### Melalui Aplikasi GUI

**Untuk Honorarium, Jamuan Tamu, atau PJLP**:
1. Buka **Pembayaran Lainnya Manager**
2. Pilih tab sesuai jenis pembayaran (Honorarium/Jamuan Tamu/PJLP)
3. Isi data penerima dan jumlah pembayaran
4. Pada bagian "Dokumen Pembayaran", centang:
   - ✓ Kuitansi Uang Muka
   - ✓ Kuitansi Rampung
5. Klik **Buat Dokumen**
6. Template akan di-generate otomatis dengan data terisi

### Manual (Jika diperlukan)

1. Copy template dari `templates/word/kuitansi_uang_muka_spm_lainnya.docx`
2. Buka di Microsoft Word
3. Ganti placeholder dengan data aktual:
   - Gunakan Find & Replace (Ctrl+H)
   - Cari: `{{placeholder}}`
   - Ganti dengan: `nilai aktual`
4. Simpan dengan nama: `Kuitansi_UM_[Jenis]_[Nama].docx`
5. Lakukan hal yang sama untuk kuitansi rampung

---

## Contoh Penggunaan

### Contoh 1: Honorarium Narasumber

**Data yang diisi**:
```
Jenis Pembayaran: Honorarium Narasumber
Perihal: Workshop Pengembangan Ternak Sapi Pedaging
Penerima: Dr. Bambang Sutrisno, S.Pt., M.Sc.
NIP: 19750830 199203 1 001
Jabatan: Narasumber/Dosen

SK KPA: SK-KPA/HONOR/001/2026, tanggal 5 Januari 2026
Dasar: Permendagri No. 12 Tahun 2023 tentang Honorarium

Uang Muka: Rp 5.000.000,00 (lima juta rupiah)
Honorarium Total: Rp 7.500.000,00
Pembayaran Rampung: Rp 2.500.000,00 (dua juta lima ratus ribu rupiah)
```

**Output**:
- Kuitansi_UM_Honorarium_Bambang_Sutrisno.docx
- Kuitansi_Rampung_Honorarium_Bambang_Sutrisno.docx

---

### Contoh 2: Jamuan Tamu

**Data yang diisi**:
```
Jenis Pembayaran: Jamuan Tamu
Perihal: Jamuan Tamu Rapat Koordinasi Peternakan Regional
Penerima: Satker (Atas Nama Kepala)
NIP: 19800115 200801 1 001
Jabatan: Kepala Dinas

SK KPA: SK-KPA/JAMUAN/001/2026, tanggal 10 Januari 2026
Dasar: PP No. 14 Tahun 2015 tentä Jamuan

Uang Muka: Rp 10.000.000,00
Biaya Realisasi: Rp 9.500.000,00
Pembayaran Rampung (Sisa): Rp -500.000,00 (kelebihan bayar dikembalikan)
```

---

## Catatan Penting

### ⚠️ Validasi Data

Sebelum menandatangani kuitansi, pastikan:

1. **Data DIPA**
   - ✓ Kode satker sesuai SK Satker
   - ✓ Tahun anggaran sesuai perioda
   - ✓ Kode akun/MAK sesuai DIPA yang disetujui
   - ✓ Kegiatan/perihal sesuai RENCANA KERJA

2. **Data Kuitansi**
   - ✓ Nomor kuitansi unik dan terurut
   - ✓ Jumlah uang muka sesuai dengan SPP yang disetujui
   - ✓ Terbilang sama dengan jumlah nominal
   - ✓ Penerima sudah ditunjuk melalui SK KPA

3. **Data Penerima**
   - ✓ Nama penerima sesuai SK/SPPD
   - ✓ NIP/identitas valid
   - ✓ Jabatan sesuai penunjukan
   - ✓ Tanda tangan penerima lengkap

4. **Pengesahan**
   - ✓ PPK sudah menyetujui
   - ✓ Bendahara sudah mengalokasikan dana
   - ✓ Semua TTD lengkap dengan tinta hitam/biru
   - ✓ Terjadi di tempat sesuai SPPD (jika ada)

### 📋 Dokumen Pendukung

Setiap kuitansi harus didukung oleh:
- **Kuitansi Uang Muka**: SK KPA + SPP Uang Muka
- **Kuitansi Rampung**: SK KPA + SPP Rampung + Laporan Pelaksanaan/LPJ
- **Tanda bukti**: Daftar hadir, notulen rapat (jika ada)

### 💾 Penamaan File

Gunakan konvensi penamaan untuk kemudahan identifikasi:

```
Kuitansi_UM_[JenisPembayaran]_[Tanggal].docx
Kuitansi_Rampung_[JenisPembayaran]_[Tanggal].docx

Contoh:
- Kuitansi_UM_Honorarium_20260110.docx
- Kuitansi_Rampung_Honorarium_20260110.docx
- Kuitansi_UM_JamuanTamu_20260115.docx
- Kuitansi_Rampung_JamuanTamu_20260115.docx
```

### 🔄 Alur Pembayaran

```
┌─────────────────────────────────────────┐
│ 1. SK KPA diterbitkan                   │
│    (Penunjukan penerima)                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 2. SPP Uang Muka dibuat                 │
│    (Persetujuan dana)                   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 3. Kuitansi Uang Muka dibuat            │
│    (Bukti penerimaan uang muka)         │
└────────────────┬────────────────────────┘
                 │
        [KEGIATAN/LAYANAN]
                 │
┌────────────────▼────────────────────────┐
│ 4. Laporan Pelaksanaan disiapkan        │
│    (Bukti pelaksanaan kegiatan)         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 5. SPP Rampung dibuat                   │
│    (Persetujuan pembayaran sisa)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 6. Kuitansi Rampung dibuat              │
│    (Bukti pembayaran final)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│ 7. Dokumen ke Arsip & Sistem            │
└─────────────────────────────────────────┘
```

### ❓ FAQ

**Q: Apakah kedua kuitansi harus ada?**  
A: Tidak selalu. Jika pembayaran dilakukan sekaligus (tanpa uang muka), hanya kuitansi rampung yang diperlukan.

**Q: Bagaimana jika ada perubahan nominal?**  
A: Buat kuitansi rampung baru dengan nominal yang sesuai. Jangan diragukan di kuitansi uang muka yang sudah ditandatangani.

**Q: Siapa yang bisa menjadi penerima kuitansi?**  
A: Penerima adalah pihak yang telah ditunjuk melalui SK KPA, bisa perorangan atau institusi.

**Q: Apakah kuitansi ini berlaku untuk semua satker?**  
A: Ya, template dapat digunakan untuk semua satker dengan menyesuaikan data DIPA dan penandatangan.

---

## File Terkait

- `create_kuitansi_spm_lainnya.py` - Script pembuat template
- `templates/word/kuitansi_uang_muka_spm_lainnya.docx` - Template uang muka
- `templates/word/kuitansi_rampung_spm_lainnya.docx` - Template rampung
- `app/ui/pembayaran_lainnya_manager.py` - UI manager pembayaran
- `app/templates/engine.py` - Template engine untuk merge data

---

**Versi**: 1.0  
**Tanggal**: Januari 2026  
**Status**: Ready for Production
