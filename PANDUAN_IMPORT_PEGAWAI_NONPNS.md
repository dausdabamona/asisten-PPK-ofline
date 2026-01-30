# Format Data Pegawai Non-PNS untuk Import

## Panduan Import Data Pegawai Non-PNS

### Cara Menggunakan

1. **Siapkan file CSV** dengan nama: `pegawai_nonpns.csv`
2. **Lokasi file**: `e:\gdrive\0. 2026\suplier\pegawai_nonpns.csv`
3. **Format encoding**: UTF-8
4. **Delimiter**: Koma (,) atau Semicolon (;)

### Format Kolom CSV

| Kolom | Tipe | Wajib | Contoh | Keterangan |
|-------|------|-------|--------|-----------|
| NMPPPNPN | Text | ✅ | AGUSTINUS LADO CARVALO | Nama lengkap pegawai |
| NIKPPNPN | Text | ✅ | 9271031202860003 | ID/NIK pegawai |
| NPWP | Text | ❌ | 70189533695100 | Nomor NPWP |
| STATUS | Text | ❌ | 1102 | Status pegawai (optional) |
| NOREK | Text | ❌ | 4124000 | Nomor rekening bank |
| BANK | Text | ❌ | BRI | Nama bank |
| JABATAN | Text | ❌ | Teknisi | Jabatan pegawai (default: Non-PNS) |
| UNIT_KERJA | Text | ❌ | Teknik Mesin | Unit/Bagian kerja (default: Umum) |
| EMAIL | Text | ❌ | pegawai@polsorong.ac.id | Email pegawai |
| TELEPON | Text | ❌ | 081234567890 | Nomor telepon |

### Contoh File CSV

**Nama file**: `pegawai_nonpns.csv`

```csv
NMPPPNPN,NIKPPNPN,NPWP,STATUS,NOREK,BANK,JABATAN,UNIT_KERJA,EMAIL,TELEPON
AGUSTINUS LADO CARVALO,9271031202860003,70189533695100,1102,4124000,BRI,Teknisi,Teknik Mesin,agustinus@polsorong.ac.id,081234567890
ANDI AMRI,9271031680200023,70189539951000,1000,3749000,MANDIRI,Teknisi,Teknik Mekanika,andi@polsorong.ac.id,081234567891
DARWIS MASSE,00000000095100,1000,3749000,BRI,Teknisi,Teknik Mesin,,
ELISABET RIMAHORPEN,7689093076951000,1000,3749000,BRI,Instruktur,Teknik Mesin,,
IRWAN WARFANDU,7689103095100,1102,3749000,BRI,Teknisi,Teknik Kapal,,
```

### Cara Menjalankan Import

**Opsi 1: Double-click batch file**
```
Double-click: import_pegawai_nonpns.bat
```

**Opsi 2: Dari command prompt**
```bash
cd e:\gdrive\aplikasi
python import_pegawai_nonpns.py
```

### Output yang Diharapkan

Setelah import sukses, akan menampilkan:

```
======================================================================
IMPORT DATA PEGAWAI NON-PNS
======================================================================

📂 Membaca file: e:/gdrive/0. 2026/suplier/pegawai_nonpns.csv
======================================================================
  ⏳ Progress: 10 pegawai non-PNS...
  ⏳ Progress: 20 pegawai non-PNS...

======================================================================
✅ IMPORT SELESAI
======================================================================
✓ Berhasil diimpor: 25 pegawai Non-PNS
⚠️  Duplikat (skip): 2
❌ Gagal: 0
======================================================================
📊 Statistik Database:
   • Total Pegawai Non-PNS: 25
   • Total Pegawai (semua): 150
======================================================================

📋 Data Non-PNS terbaru (sample):
  • AGUSTINUS LADO CARVALO
    └─ ID: 9271031202860003 | Jabatan: Teknisi | Unit: Teknik Mesin
  • ANDI AMRI
    └─ ID: 9271031680200023 | Jabatan: Teknisi | Unit: Teknik Mekanika
  ...
```

### Troubleshooting

**❌ Error: "File CSV tidak ditemukan"**
- Pastikan file berada di: `e:\gdrive\0. 2026\suplier\pegawai_nonpns.csv`
- Periksa nama file (case-sensitive pada Linux, case-insensitive pada Windows)

**❌ Error: "Kolom tidak ditemukan"**
- Pastikan CSV memiliki header (baris pertama): NMPPPNPN, NIKPPNPN, NPWP, etc
- Periksa spelling nama kolom (harus sesuai persis)

**❌ Error: "Database connection error"**
- Pastikan aplikasi tidak sedang berjalan
- Tutup semua koneksi ke database `ppk_workflow.db`

**⚠️ Banyak duplikat**
- Data dengan nama yang sama sudah ada di database
- Hapus data lama terlebih dahulu atau update yang ada

### Data yang Akan Disimpan

Setiap pegawai Non-PNS akan disimpan dengan field:

```python
{
  'nip': 'NIKPPNPN dari CSV',
  'nama': 'Nama lengkap',
  'jabatan': 'Dari CSV atau default "Non-PNS"',
  'golongan': 'Non-PNS (fixed)',
  'pangkat': 'Non-PNS (fixed)',
  'unit_kerja': 'Dari CSV atau default "Umum"',
  'email': 'Email pegawai',
  'telepon': 'No telepon',
  'npwp': 'Nomor NPWP',
  'no_rekening': 'Nomor rekening bank',
  'nama_bank': 'Nama bank',
  'is_ppk': False (default),
  'is_ppspm': False (default),
  'is_bendahara': False (default),
  'is_pemeriksa': False (default),
  'is_pejabat_pengadaan': False (default),
  'is_active': True
}
```

### Edit Role Pegawai Non-PNS

Setelah import, Anda bisa edit role pegawai Non-PNS di aplikasi:
- Jalankan aplikasi: `python main.py` atau `main.exe`
- Menu: Pegawai Manager
- Pilih pegawai Non-PNS
- Edit role: PPK, PPSPM, Bendahara, dll sesuai kebutuhan

---

**Status**: ✅ Ready to use  
**Version**: 1.0  
**Last Updated**: January 30, 2026
