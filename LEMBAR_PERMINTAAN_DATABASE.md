# Lembar Permintaan - Database Integration

## Ringkasan

Fitur **Lembar Permintaan** telah diupdate untuk otomatis menyimpan data ke database saat dokumen di-generate. Sebelumnya, hanya dokumen Word yang disimpan. Sekarang, semua data (header, item barang, penandatangan) tersimpan terstruktur di database SQLite.

## Database Schema

### Table `lembar_permintaan`

Menyimpan data header lembar permintaan:

```sql
CREATE TABLE IF NOT EXISTS lembar_permintaan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_dokumen TEXT UNIQUE,
    kode_transaksi TEXT,                    -- Link ke transaksi_pencairan
    hari_tanggal DATE NOT NULL,
    unit_kerja TEXT NOT NULL,
    sumber_dana TEXT,
    
    -- Detail Keuangan
    subtotal REAL DEFAULT 0,
    ppn REAL DEFAULT 0,
    total REAL DEFAULT 0,
    
    -- Penandatangan
    nama_pengajuan TEXT,
    nama_verifikator TEXT,
    nama_ppk TEXT,
    nama_atasan TEXT,
    nama_kpa TEXT,
    
    -- Status dan File
    status TEXT DEFAULT 'draft',            -- draft, final, signed, uploaded
    file_path TEXT,                         -- Path ke dokumen Word
    
    -- Metadata
    tahun_anggaran INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT
);
```

### Table `lembar_permintaan_item`

Menyimpan rincian barang/jasa dalam lembar permintaan:

```sql
CREATE TABLE IF NOT EXISTS lembar_permintaan_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lembar_permintaan_id INTEGER NOT NULL,
    item_no INTEGER NOT NULL,
    nama_barang TEXT NOT NULL,
    spesifikasi TEXT,
    volume REAL,
    satuan TEXT,
    harga_satuan REAL,
    total_item REAL,
    keterangan TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (lembar_permintaan_id) REFERENCES lembar_permintaan(id) ON DELETE CASCADE
);
```

## API - Penggunaan

### 1. Generate Lembar Permintaan Manual

```python
from create_lembar_permintaan import create_lembar_permintaan
from datetime import datetime

items = [
    {
        'item_no': 1,
        'nama_barang': 'Kertas A4',
        'spesifikasi': '80 gsm, 500 lembar',
        'volume': 10,
        'satuan': 'rim',
        'harga_satuan': 50000,
        'total_item': 500000,
        'keterangan': 'Untuk kantor',
    },
    {
        'item_no': 2,
        'nama_barang': 'Tinta Printer',
        'spesifikasi': 'Black, original',
        'volume': 2,
        'satuan': 'botol',
        'harga_satuan': 150000,
        'total_item': 300000,
        'keterangan': '',
    }
]

signatures = {
    'nama_pengajuan': 'Budi Santoso',
    'nama_verifikator': 'Eka Prasetya',
    'nama_ppk': 'Siti Nurhaliza',
    'nama_atasan': 'Ahmad Rahman',
    'nama_kpa': 'Drs. Hendra Kusuma',
}

lembar_id, doc_path, error = create_lembar_permintaan(
    hari_tanggal=datetime.now().strftime('%Y-%m-%d'),
    unit_kerja='Bagian Keuangan',
    sumber_dana='DIPA 2026 - Kegiatan Operasional',
    items=items,
    signatures=signatures,
    created_by='admin'
)

if error:
    print(f"Error: {error}")
else:
    print(f"Lembar Permintaan {lembar_id} created at {doc_path}")
```

### 2. Generate dari Transaksi Pencairan

```python
from create_lembar_permintaan import create_lembar_permintaan_from_transaksi

# Generate lembar dari transaksi_pencairan yang sudah ada
lembar_id, doc_path, error = create_lembar_permintaan_from_transaksi(transaksi_id=5)
```

### 3. Database Manager Methods

```python
from app.models.pencairan_models import PencairanManager

db = PencairanManager()

# Create lembar permintaan
lembar_id = db.create_lembar_permintaan({
    'hari_tanggal': '2026-01-31',
    'unit_kerja': 'Bagian Keuangan',
    'sumber_dana': 'DIPA 2026',
    'subtotal': 800000,
    'ppn': 80000,
    'total': 880000,
    'status': 'draft',
    'created_by': 'admin'
})

# Add item
item_id = db.add_lembar_permintaan_item(lembar_id, {
    'item_no': 1,
    'nama_barang': 'Kertas A4',
    'volume': 10,
    'satuan': 'rim',
    'harga_satuan': 50000,
    'total_item': 500000,
})

# Get lembar permintaan
lembar = db.get_lembar_permintaan(lembar_id)
print(f"Unit Kerja: {lembar['unit_kerja']}")
print(f"Total: Rp {lembar['total']:,.0f}")

# Get items
items = db.get_lembar_permintaan_items(lembar_id)
for item in items:
    print(f"- {item['nama_barang']}: Rp {item['total_item']:,.0f}")

# Update lembar
db.update_lembar_permintaan(lembar_id, {
    'status': 'final',
    'nama_pengajuan': 'Budi Santoso'
})

# List all lembar permintaan
all_docs = db.list_lembar_permintaan(tahun=2026, limit=50)
```

## Command Line Usage

### Generate Template Saja
```bash
python create_lembar_permintaan.py --template
```

### Generate dari Transaksi
```bash
python create_lembar_permintaan.py --transaksi-id 5
```

### Interactive Mode
```bash
python create_lembar_permintaan.py
# Akan meminta input: hari_tanggal, unit_kerja, sumber_dana, items
```

## Status Workflow

Lembar Permintaan memiliki status sebagai berikut:

| Status | Deskripsi |
|--------|-----------|
| `draft` | Baru dibuat, belum final |
| `final` | Data lengkap, siap untuk ditandatangani |
| `signed` | Sudah ditandatangani (soft copy) |
| `uploaded` | Sudah diupload ke sistem pusat |

## Integrasi dengan Transaksi Pencairan

Lembar Permintaan dapat di-link ke `transaksi_pencairan` melalui field `kode_transaksi`:

```python
# Create lembar dari transaksi yang sudah ada
lembar_id = db.create_lembar_permintaan({
    'kode_transaksi': 'UP/001/2026',     # Link ke transaksi_pencairan
    'hari_tanggal': '2026-01-31',
    'unit_kerja': 'Bagian Keuangan',
    # ... fields lainnya
})
```

Query untuk mendapatkan lembar dari kode transaksi:
```python
lembar = db.get_lembar_permintaan_by_kode_transaksi('UP/001/2026')
```

## File yang Dimodifikasi

1. **app/models/pencairan_models.py**
   - Added `SCHEMA_LEMBAR_PERMINTAAN` dengan 2 tables
   - Added methods: `create_lembar_permintaan`, `add_lembar_permintaan_item`, `get_lembar_permintaan`, `get_lembar_permintaan_items`, `update_lembar_permintaan`, `list_lembar_permintaan`

2. **app/services/dokumen_generator.py**
   - Added `save_lembar_permintaan_to_db()` - save data to database
   - Added `generate_and_save_lembar_permintaan()` - generate dokumen + save data
   - Added `generate_document_from_template()` - helper untuk template processing

3. **create_lembar_permintaan.py**
   - Refactored dengan database integration
   - Added `create_lembar_permintaan()` - main function dengan DB save
   - Added `create_lembar_permintaan_from_transaksi()` - create dari transaksi
   - Added CLI dengan argparse untuk berbagai mode

## Keuntungan

✅ **Data Tersentralisasi** - Semua data lembar permintaan tersimpan terstruktur di database
✅ **Query & Reporting** - Mudah membuat laporan, filter, dan analisis
✅ **Audit Trail** - Track siapa yang membuat, kapan, dan perubahan apa
✅ **Integrasi** - Link ke transaksi_pencairan untuk workflow lengkap
✅ **Status Tracking** - Follow status dokumen dari draft hingga uploaded
✅ **Backward Compatible** - Tetap generate dokumen Word seperti sebelumnya

## Contoh Query

```sql
-- Total belanja per unit kerja
SELECT unit_kerja, COUNT(*) as jumlah, SUM(total) as total_nilai
FROM lembar_permintaan
WHERE tahun_anggaran = 2026
GROUP BY unit_kerja
ORDER BY total_nilai DESC;

-- Barang yang paling sering dipesan
SELECT nama_barang, COUNT(*) as frequency, SUM(volume) as total_volume
FROM lembar_permintaan_item
GROUP BY nama_barang
ORDER BY frequency DESC
LIMIT 10;

-- Lembar permintaan yang belum ditandatangani
SELECT id, unit_kerja, hari_tanggal, total
FROM lembar_permintaan
WHERE status IN ('draft', 'final')
ORDER BY hari_tanggal DESC;
```

## Troubleshooting

**Q: Database connection error**
A: Pastikan `DATABASE_PATH` sudah dikonfigurasi di `app/core/config.py`

**Q: Template file tidak ditemukan**
A: Pastikan file template ada di `templates/word/lembar_permintaan.docx`

**Q: Items tidak tersimpan**
A: Pastikan items dict memiliki semua required fields: item_no, nama_barang, total_item

## Future Enhancements

- [ ] Nomor dokumen auto-generated dengan format customizable
- [ ] Digital signature support
- [ ] PDF export
- [ ] Email notification saat dokumen dibuat
- [ ] Approval workflow dengan multiple signatories
- [ ] Attachment upload untuk supporting documents
