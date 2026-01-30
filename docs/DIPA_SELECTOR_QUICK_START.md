"""
DIPA SELECTOR - QUICK START GUIDE
==================================

Ringkasan singkat implementasi DIPA Selector untuk estimasi biaya 
dan ekstraksi MAK (Mata Anggaran Kegiatan).


📋 WHAT'S NEW?
==============

Sebelumnya:
- User mengisi Estimasi Biaya secara manual
- Kode MAK tidak tersedia/diisi manual
- Tidak ada validasi dengan data anggaran

Sekarang:
- User memilih items dari DIPA (database anggaran)
- Estimasi Biaya otomatis dijumlahkan
- MAK codes otomatis dikumpulkan dan dideduplikasi
- Full breakdown dengan percentage per item
- Validasi dengan data anggaran real-time


🎯 KEY FEATURES
================

1. Multi-Select DIPA Items
   ✓ Pilih beberapa item sekaligus
   ✓ Search dan filter berdasarkan kode/uraian
   ✓ Filter by level (Akun vs Detail)

2. Auto-Calculate Total Biaya
   ✓ Total = Sum(jumlah dari selected items)
   ✓ Display format: Rp X.XXX.XXX
   ✓ Real-time update saat selection berubah

3. Auto-Extract MAK Codes
   ✓ MAK = Mata Anggaran Kegiatan
   ✓ Format: kode_akun.kode_detail
   ✓ Auto-deduplicate jika ada double

4. Item Breakdown Table
   ✓ Setiap item ditampilkan detail
   ✓ Percentage per item
   ✓ Bisa remove item dari selection

5. Summary Display
   ✓ Total biaya (read-only, dari DIPA)
   ✓ MAK codes (read-only, dari DIPA)
   ✓ Uraian kegiatan (dari selected items)


📊 USER INTERFACE
=================

Sebelum (Lama):
┌──────────────────────────────┐
│ Estimasi Biaya *             │
│ [Input manual: Rp ______]    │
│                              │
│ Tanggal Kegiatan:            │
│ Mulai: [____] Selesai: [____]│
└──────────────────────────────┘

Sekarang (Baru):
┌─────────────────────────────────────────────────────┐
│ [📋 Pilih dari DIPA]                                │
│                                                     │
│ Selected Items:                                     │
│ ┌──────────┬──────────────┬──────────┬──────────┐ │
│ │ MAK      │ Uraian       │ Jumlah   │ % Biaya  │ │
│ ├──────────┼──────────────┼──────────┼──────────┤ │
│ │ 5.1.01.02│ Gaji/Upah    │ Rp 50M   │ 60.0%    │ │
│ │ 5.1.01.03│ Tunjangan    │ Rp 30M   │ 35.0%    │ │
│ │ 5.1.01.04│ Insentif     │ Rp 5M    │ 5.0%     │ │
│ └──────────┴──────────────┴──────────┴──────────┘ │
│                                                     │
│ Summary DIPA:                                       │
│ Total Estimasi Biaya *      [Rp 85,000,000]       │
│ Kode MAK/Akun *             [5.1.01.02, 5.1.01.03]│
│ Uraian Kegiatan             [Text...]             │
│                                                     │
│ Tanggal Kegiatan:                                   │
│ Mulai: [____] Selesai: [____]                      │
└─────────────────────────────────────────────────────┘

Dialog Pemilihan DIPA:
┌────────────────────────────────────────────────────────┐
│ Pilih Item DIPA untuk Estimasi Biaya                  │
│                                                        │
│ Cari: [_______]  Level: [Semua Level ▼]              │
│                                                        │
│ ┌─┬────────┬────────┬────────┬────────┬───────────┐  │
│ │✓│ K.Akun │K.Detail│ MAK    │ Uraian │ Jumlah   │  │
│ ├─┼────────┼────────┼────────┼────────┼───────────┤  │
│ │ │5.1.01 │  01    │5.1.01.01│Gaji   │ Rp 50M   │  │
│ │ │5.1.02 │  02    │5.1.02.02│Tunjg  │ Rp 30M   │  │
│ │ │5.1.03 │  01    │5.1.03.01│Travel │ Rp 15M   │  │
│ │ │5.1.04 │  03    │5.1.04.03│Travel │ Rp 5M    │  │
│ └─┴────────┴────────┴────────┴────────┴───────────┘  │
│                                                        │
│ Summary Pilihan:                                       │
│ Total Biaya:    [Rp 100,000,000]                     │
│ MAK Terpilih:   [5.1.01.01, 5.1.02.02, ...]         │
│ Jumlah Item:    [3 item dipilih]                     │
│                                                        │
│ [Bersihkan] [Batal]  [✓ Gunakan Pilihan]            │
└────────────────────────────────────────────────────────┘


💾 DATA STRUCTURE
=================

Input Database (pagu_anggaran table):
├─ id: 1
├─ tahun_anggaran: 2026
├─ kode_akun: "5.1.01.05"
├─ kode_detail: "01"
├─ nomor_mak: "5.1.01.05.01"
├─ uraian: "Gaji Pegawai"
├─ jumlah: 50000000
└─ level_kode: 8

DipaItem Object (saat dipilih):
├─ dipa_id: 1
├─ kode_akun: "5.1.01.05"
├─ kode_detail: "01"
├─ nomor_mak: "5.1.01.05.01"
├─ uraian: "Gaji Pegawai"
└─ jumlah: 50000000

Form Output (saat disimpan):
├─ mekanisme: "UP"
├─ estimasi_biaya: 85000000 (auto-calculated)
├─ kode_mak: "5.1.01.05.01, 5.1.01.06.02" (auto-extracted)
├─ dipa_items: [
│  ├─ {dipa_id: 1, nomor_mak: "5.1.01.05.01", jumlah: 50000000}
│  ├─ {dipa_id: 2, nomor_mak: "5.1.01.06.02", jumlah: 30000000}
│  └─ {dipa_id: 3, nomor_mak: "5.1.01.07.01", jumlah: 5000000}
│  ]
└─ ... (other form fields)


🔧 WORKFLOW
===========

Workflow Old (Manual):
┌─────────┐
│ Open    │
│ UP Form │
└────┬────┘
     │
     ▼
┌──────────────────┐      "Berapa estimasi biaya?"
│ Input Estimasi   │───► Manual entry error prone
│ Biaya Manual     │      Tidak ter-validasi
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Input Kode MAK   │      "MAK code apa?"
│ Manual (Optional)│───► Sering lupa/salah
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Save Transaksi   │
└──────────────────┘

Workflow New (DIPA-Based):
┌─────────┐
│ Open    │
│ UP Form │
└────┬────┘
     │
     ▼
┌─────────────────────┐
│ Click              │
│ "📋 Pilih dari DIPA"│
└────┬────────────────┘
     │
     ▼
┌──────────────────────────────┐
│ DipaSelectorDialog Opens     │      Browse DIPA
│ ├─ Show all DIPA items       │      Search/Filter
│ ├─ User select items (multi) │      Multi-select
│ └─ Show summary              │
└────┬───────────────────────────┘
     │ User clicks "Gunakan Pilihan"
     ▼
┌──────────────────────────────┐
│ Form Auto-Update:           │      Auto-fill:
│ ├─ Estimasi Biaya = ✓       │      - Total dari selected items
│ ├─ Kode MAK = ✓             │      - MAK dari selected items
│ └─ Uraian = ✓               │      - Uraian dari items
└────┬───────────────────────────┘
     │
     ▼
┌──────────────────────────┐
│ User review & edit       │     Can override if needed
│ other form fields        │
└────┬─────────────────────┘
     │
     ▼
┌──────────────────────┐
│ Save Transaksi      │     Data consistent with DIPA
└──────────────────────┘


📈 DATA DISPLAYED SUMMARY
=========================

Field Name               Source          Type        Format
─────────────────────────────────────────────────────────────
Estimasi Biaya          DIPA selection  Computed    Rp X.XXX.XXX
Kode MAK/Akun           DIPA selection  Computed    MAK1, MAK2, MAK3
Uraian Kegiatan         DIPA items      Text        Multi-line text

Per Selected Item:
├─ MAK                  pagu_anggaran   Text        X.X.XX.XX.XX
├─ Uraian               pagu_anggaran   Text        Item description
├─ Jumlah               pagu_anggaran   Numeric     Rp X.XXX.XXX
└─ Persentase           Calculated      Percentage  XX.X%

Dialog Summary:
├─ Total Biaya          Sum formula     Numeric     Rp X.XXX.XXX
├─ MAK Terpilih         List merge      Text        MAK1, MAK2
└─ Jumlah Item          Count           Integer     N items dipilih


⚙️ CONFIGURATION
=================

Database Connection:
- Source: app.core.config.DATABASE_PATH
- Table: pagu_anggaran
- Year: app.core.config.TAHUN_ANGGARAN

Query Criteria:
- Level: 7 (Akun) dan 8 (Detail) - detail breakdown items
- Status: jumlah > 0 - hanya active budgets
- Year: tahun_anggaran = TAHUN_ANGGARAN

Validation Rules:
- Min items: 1 (user harus pilih minimal 1)
- Max biaya UP: Rp 50,000,000
- MAK deduplication: Auto remove duplikasi
- Percentage sum: ≈ 100% (allow rounding error)


📱 RESPONSIVE BEHAVIOR
======================

Dialog Ukuran:
- Width: 1000px (adjustable)
- Height: 600px (adjustable)
- Modal: Yes (blocks parent)

Widget Ukuran:
- Auto height
- Embedded dalam form layout
- Selected items table max 150px (scrollable)

Table Columns:
- Checkbox: Auto-size
- Numeric columns: Right-aligned
- Text columns: Stretch
- All responsive to window size


🚀 IMPLEMENTATION CHECKLIST
===========================

Setup:
☑ Copy file: app/ui/components/dipa_selector.py
☑ Update imports in transaksi_form.py
☑ Verify database schema has pagu_anggaran table
☑ Test syntax: python -m py_compile

Integration:
☑ Form now uses DipaSelectionWidget
☑ _on_dipa_selection_changed() handler working
☑ Auto-fill: estimasi_input, kode_mak_input
☑ Data saved to database correctly

Testing:
☑ Open UP/TUP form
☑ Click "Pilih dari DIPA" button
☑ Dialog shows DIPA items
☑ Multi-select items
☑ Total biaya updates
☑ MAK codes populate
☑ Selected items displayed
☑ Can remove/edit items
☑ Form save successful
☑ Data retrieved correctly on edit

Documentation:
☑ DIPA_SELECTOR_DOCUMENTATION.md created
☑ DIPA_SELECTOR_IMPLEMENTATION.md created
☑ This QUICK_START.md created


📖 FILES REFERENCE
==================

New Files:
📄 app/ui/components/dipa_selector.py (500+ lines)
   └─ DipaItem, DipaSelectorDialog, DipaSelectionWidget

Modified Files:
📄 app/ui/pages/pencairan/transaksi_form.py
   └─ _create_financial_section_up()
   └─ _on_dipa_selection_changed()

Documentation:
📄 docs/DIPA_SELECTOR_DOCUMENTATION.md
📄 docs/DIPA_SELECTOR_IMPLEMENTATION.md
📄 docs/DIPA_SELECTOR_QUICK_START.md (this file)


💡 TIPS & TRICKS
================

1. Search Tips:
   - Search "5.1.01" untuk find semua akun dalam kategori
   - Search "gaji" untuk find semua yang related to gaji
   - Search partial text, e.g., "peng" untuk pengadaan

2. Selection Tips:
   - Use Ctrl+Click untuk select multiple rows
   - Use Shift+Click untuk select range
   - Column sort dengan click header (ascending/descending)

3. Bulk Operations:
   - Select all dengan Ctrl+A (if table focused)
   - Bersihkan semua dengan tombol "Bersihkan Pilihan"
   - Remove individual item dengan tombol Hapus per row

4. Debugging:
   - Check database: SELECT * FROM pagu_anggaran LIMIT 10
   - Test search functionality dengan opening/closing dialog
   - Verify calculations dengan manual sum
   - Enable debug logging untuk trace execution

5. Performance:
   - Load times acceptable untuk <10,000 items
   - Filter reduces displayed rows dramatically
   - Percentage recalc only on selection change
   - UI responsive even with large datasets


❓ FAQ
======

Q: Bagaimana jika saya ingin manual input estimasi biaya?
A: Klik tombol "📋 Pilih dari DIPA" skip dan form tetap bisa diisi
   manual. Untuk override, implementasi set_editable_biaya(True).

Q: Biaya menjadi Rp 0 setelah select, kenapa?
A: Pastikan selected items memiliki nilai jumlah > 0 di database.
   Cek: SELECT id, uraian, jumlah FROM pagu_anggaran WHERE jumlah <= 0

Q: MAK codes tidak muncul?
A: Verify nomor_mak field terisi di database. Jika kosong, 
   format: kode_akun + "." + kode_detail

Q: Bisa select item dari tahun anggaran berbeda?
A: Tidak, dialog hanya show items untuk tahun_anggaran saat ini.
   To change year, modify TAHUN_ANGGARAN di config.

Q: Database jumlah field dalam format text, bisa?
A: Tidak recommended. Convert ke REAL/NUMERIC untuk better accuracy.
   Query: ALTER TABLE pagu_anggaran MODIFY jumlah REAL;

Q: Gimana jika DIPA items sangat banyak (>50,000)?
A: Filter/search menjadi penting. Implementasi pagination option
   atau lazy-load untuk performa lebih baik.


🔄 VERSION HISTORY
===================

v1.0 (Current - January 2026)
├─ Multi-select DIPA items
├─ Auto-calculate total biaya
├─ Auto-extract MAK codes
├─ Search and filter
├─ Item breakdown with percentages
└─ Documentation complete

v1.1 (Planned)
├─ Batch import/export
├─ Selection templates
├─ Selection history
├─ Budget remaining indicator
└─ Approval workflow

v2.0 (Future)
├─ Custom MAK mapping
├─ Advanced reporting
├─ Budget analytics
└─ Integration with e-spp


🤝 SUPPORT
===========

For issues or questions:
1. Check documentation files
2. Review implementation code
3. Check test cases
4. Debug with print/logging
5. Contact development team

Documentation Files:
- docs/DIPA_SELECTOR_DOCUMENTATION.md - Detailed specs
- docs/DIPA_SELECTOR_IMPLEMENTATION.md - Technical guide
- docs/DIPA_SELECTOR_QUICK_START.md - This file


✅ NEXT STEPS
=============

1. Review this guide completely
2. Read DIPA_SELECTOR_DOCUMENTATION.md
3. Review source code in dipa_selector.py
4. Test the feature with UP/TUP form
5. Verify database integration
6. Test with multiple DIPA items
7. Check form saving/loading
8. Deploy to production

Ready to use! 🎉
"""
