# Panduan Menjalankan Workflow Pencairan Dana

## Quick Start

### 1. Install Dependencies (jika belum)
```bash
pip install -r requirements.txt
```

### 2. Run Workflow UI
```bash
python test_workflow_ui.py
```

Atau import langsung:
```python
from PySide6.QtWidgets import QApplication
from app.ui.workflow_main_window import WorkflowMainWindow
import sys

app = QApplication(sys.argv)
window = WorkflowMainWindow()
window.show()
sys.exit(app.exec())
```

---

## Fitur-Fitur

### 1. **UP (Uang Persediaan)**
- ✅ Create transaksi baru (form validation)
- ✅ List semua UP transaksi (filter & search)
- ✅ Detail view dengan 5-phase workflow
- ✅ Phase navigation (klik stepper step atau tombol "Lanjut Fase")
- ✅ Document checklist per fase
- ✅ Auto-calculation di Fase 4 (selisih = realisasi - uang_muka)

**Karakteristik:**
- Tidak ada deadline (unlimited time)
- Max value: Rp 50 juta
- Warna: Hijau (#27ae60)

### 2. **TUP (Tambahan Uang Persediaan)**
- ✅ Sama seperti UP
- ✅ PLUS: Real-time 30-day countdown timer di Fase 4
- ✅ Warning levels:
  - 🟢 Green: >5 hari remaining (masih cukup)
  - 🟠 Orange: 1-5 hari remaining (perhatian)
  - 🔴 Red: <1 hari atau sudah lewat (urgent/deadline passed)

**Karakteristik:**
- HARUS diselesaikan dalam 30 hari
- Value: >Rp 50 juta
- Warna: Orange (#f39c12)

### 3. **LS (Pembayaran Langsung)**
- ✅ Untuk pembayaran langsung ke contractor
- ✅ Sama struktur seperti UP & TUP
- ✅ TANPA countdown (tidak ada deadline)

**Karakteristik:**
- Contractor payment workflow
- Dokumen: Invoice, Faktur, Pajak, etc.
- Warna: Biru (#3498db)

---

## 5-Phase Workflow

Setiap mekanisme (UP, TUP, LS) memiliki 5 fase wajib yang harus dilalui secara berurutan:

### Fase 1: Persiapan
- Dokumen persiapan (RKA, RKAP, SPK, etc.)
- Status: Menunggu persiapan lengkap

### Fase 2: Validasi
- Validasi dokumen oleh bagian keuangan
- Dokumen: Surat validasi, Berita acara, etc.

### Fase 3: Persetujuan
- Persetujuan dari pejabat pembuat komitmen
- Dokumen: SPP, Nota dinas, etc.

### Fase 4: Pertanggungjawaban
- **UP/TUP**: Pemasukan realisasi belanja → auto-hitung selisih
  - Selisih < 0: LEBIH BAYAR (harus kembalikan)
  - Selisih > 0: KURANG BAYAR (harus bayar kekurangan)
  - Selisih = 0: PAS/NIHIL (selesai)
- **TUP**: PLUS countdown timer 30 hari dari SP2D
- **LS**: Sama seperti UP

### Fase 5: Penyelesaian
- Final dokumen (SPJ, SSBP, Laporan, etc.)
- Status: Transaksi selesai

---

## UI Navigation

### Sidebar Menu
```
┌─────────────────────┐
│   PENCAIRAN DANA    │
├─────────────────────┤
│ 📊 Dashboard        │
│ 💚 UP               │  ← List all UP
│ 🧡 TUP              │  ← List all TUP
│ 💙 LS               │  ← List all LS
├─────────────────────┤
│ 📦 Pengadaan        │
│ 👥 Pengguna         │
│ ⚙️  Pengaturan       │
└─────────────────────┘
```

### Page Navigation Flow
```
Sidebar (UP clicked)
    ↓
UP List Page
    ├─ [Double-click row] → UP Detail Page
    ├─ [Tombol "Buat Baru"] → UP Form Page
    └─ [Sidebar menu] → Back to list
    
UP Detail Page
    ├─ [Click fase stepper step] → Change fase
    ├─ [Fase 4] → KalkulasiWidget appears
    └─ [Tombol "Kembali"] → Back to UP List Page

UP Form Page
    ├─ [Fill form] → Validation
    └─ [Click "Simpan"] → Create transaksi → UP Detail Page
```

---

## Data Entry Examples

### Creating UP Transaction
1. Click "💚 UP" di sidebar
2. Click "Buat Baru" button
3. Fill form:
   - **Nama Kegiatan**: "Pembelian Buku Administrasi"
   - **Jenis Belanja**: "Alat Tulis & Kantor (ATK)"
   - **Estimasi Biaya**: 25,000,000
   - **Dasar Hukum**: "Peraturan Menteri..."
   - **Penerima Dana**: Nama pegawai
   - **Kode Akun**: "5.1.02.02.0001"
   - **Tanggal Mulai**: 2025-01-01
   - **Tanggal Selesai**: 2025-06-30
4. Click "Simpan"
5. → Transaksi created, akan membuka Detail Page (Fase 1)

### Fase 4 - Pertanggungjawaban (UP)
1. Click "Lanjut ke Fase 4"
2. Widget muncul:
   ```
   Uang Muka: Rp 25,000,000
   Total Realisasi: [input field]
   
   Selisih: Rp (calculated)
   
   Hasil: [color-coded]
   Terbilang: "....... rupiah"
   ```
3. Enter realisasi amount: 25,000,000
4. → Sistem auto-hitung:
   - Selisih = 25,000,000 - 25,000,000 = 0
   - Hasil: "PAS/NIHIL" (green)
   - Terbilang: "Nol rupiah"
5. Click "Simpan Realisasi"

### TUP - 30-Day Countdown (Fase 4)
1. Create TUP transaksi
2. Navigasi ke Fase 4
3. Dua widget muncul:
   - **KalkulasiWidget**: Sama seperti UP
   - **CountdownWidget**: 
     ```
     Tanggal SP2D: 2025-01-15
     
     Hari: 25 | Jam: 14 | Menit: 32
     [========= Progress Bar 83% =========]
     
     Status: ✅ Masih Cukup (Green)
     ```
4. Countdown updates real-time setiap detik
5. Ketika kurang dari 5 hari:
   - Color berubah orange
   - Text: "⚠️ Perhatian - Deadline mendekat"
6. Ketika kurang dari 1 hari:
   - Color berubah red
   - Text: "🔴 URGENT - Deadline sangat dekat!"

---

## Database Integration

### PencairanDanaManager Usage
```python
from app.models.pencairan_models import get_pencairan_manager

mgr = get_pencairan_manager()

# Create transaksi
data = {
    'mekanisme': 'UP',
    'nama_kegiatan': 'Test Kegiatan',
    'jenis_belanja': 'Honorarium',
    'estimasi_biaya': 10000000,
    'jenis_dasar': 'Peraturan Menteri',
    'nomor_dasar': 'PM-001/2025',
    'tanggal_dasar': datetime.date(2025, 1, 15),
    'penerima_nama': 'John Doe',
    'penerima_nip': '123456789',
    'penerima_jabatan': 'Kepala Bagian',
    'kode_akun': '5.1.02.01',
    'nama_akun': 'Honorarium',
    'tanggal_mulai': datetime.date(2025, 1, 15),
    'tanggal_selesai': datetime.date(2025, 12, 31),
}
transaksi_id = mgr.create_transaksi(data)

# Get transaksi
transaksi = mgr.get_transaksi(transaksi_id)

# List transaksi
all_up = mgr.list_transaksi(mekanisme='UP')
draft_up = mgr.list_transaksi(mekanisme='UP', status='draft')

# Phase transition
mgr.pindah_fase(transaksi_id, fase_berikutnya=2, aksi='Approved', catatan='Dokumen lengkap')

# Get phase log
phase_log = mgr.get_fase_log(transaksi_id)
```

---

## QSS Styling

Global stylesheet tersimpan di: `app/ui/styles/main.qss`

### Color Scheme
- **Primary Blue**: #3498db (buttons, focus states)
- **Success Green**: #27ae60 (UP, approved status)
- **Warning Orange**: #f39c12 (TUP, warning states)
- **Danger Red**: #e74c3c (errors, urgent)
- **Dark**: #2c3e50 (sidebar, headers)
- **Light**: #f5f6fa (background)

### Component Styling
- **Buttons**: Blue background, hover darker, disabled gray
- **Inputs**: White background, 1px border, focus blue border
- **Tables**: White bg, striped rows, blue selection
- **GroupBox**: White box dengan border, bold title
- **Headers**: Dark background, white text

---

## Troubleshooting

### Issue: Database not found
**Solution:** 
- Database akan auto-create saat first run
- Check `app.core.config.DATABASE_PATH`
- Ensure write permissions di folder app/

### Issue: Pages tidak muncul
**Solution:**
- Check imports di `app/ui/pages/pencairan/__init__.py`
- Verify all page files exist
- Check console untuk import errors

### Issue: Countdown tidak update di TUP
**Solution:**
- Ensure QTimer is running (check countdown_widget.py line ~150)
- Verify tanggal_sp2d is set correctly
- Check system time is correct

### Issue: Components tidak styled
**Solution:**
- Ensure main.qss is loaded in test_workflow_ui.py
- Check stylesheet path is correct
- Verify QApplication.setStyleSheet() called

---

## Performance Tips

1. **Large datasets**: 
   - Table akan auto-scroll untuk 1000+ rows
   - Implement pagination untuk >5000 transaksi

2. **Real-time countdown**:
   - Countdown QTimer uses ~1% CPU per widget
   - Only active when TUP Detail Fase 4 visible

3. **Database queries**:
   - list_transaksi() menggunakan indexed kode_transaksi
   - Consider caching untuk frequently-accessed data

---

## Future Enhancements

### Phase 2 (Coming soon)
- [ ] Pengadaan workflow pages
- [ ] Dashboard dengan statistics
- [ ] User management & login
- [ ] PDF/Excel export

### Phase 3 (Later)
- [ ] Multi-user support
- [ ] Audit trail
- [ ] API for external integration
- [ ] Mobile-friendly responsive design

---

## File Structure Reference

```
app/
├── models/
│   └── pencairan_models.py ← Database CRUD
├── config/
│   └── workflow_config.py ← Workflow definitions
├── ui/
│   ├── components/
│   │   ├── fase_stepper.py
│   │   ├── dokumen_checklist.py
│   │   ├── kalkulasi_widget.py
│   │   ├── countdown_widget.py
│   │   └── __init__.py
│   ├── pages/
│   │   └── pencairan/
│   │       ├── up_*.py
│   │       ├── tup_*.py
│   │       ├── ls_*.py
│   │       └── __init__.py
│   ├── sidebar.py
│   ├── workflow_main_window.py
│   ├── styles/
│   │   └── main.qss
│   └── __init__.py
└── templates/
    └── engine.py ← Template system
```

---

**Ready to use!** 🚀

Contact: [Your Name]
Date: January 2025
Version: 1.0.0
