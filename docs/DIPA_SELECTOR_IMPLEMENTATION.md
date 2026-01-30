"""
DIPA SELECTOR - IMPLEMENTATION GUIDE
====================================

Panduan lengkap untuk mengimplementasikan dan menggunakan DIPA Selector
dalam aplikasi PPK Document Factory.


1. FILES YANG DIBUAT/DIMODIFIKASI
==================================

A. File Baru:
   📄 app/ui/components/dipa_selector.py
   
   Berisi 3 class utama:
   
   1. DipaItem (Model)
      - Menyimpan data single DIPA item yang dipilih
      - Properties: dipa_id, kode_akun, kode_detail, nomor_mak, uraian, jumlah
      - Method: to_dict() untuk convert ke dictionary
   
   2. DipaSelectorDialog (Modal Dialog)
      - Dialog untuk memilih DIPA items
      - Features:
        * Browse daftar DIPA dari database
        * Multi-select items
        * Search/filter functionality
        * Auto-calculate total biaya
        * Auto-compile MAK codes
        * Real-time summary display
      - Signal: items_selected(list) - emitted saat user konfirmasi selection
   
   3. DipaSelectionWidget (Widget Embedded)
      - Widget untuk ditampilkan dalam form
      - Features:
        * Button untuk buka selector dialog
        * Table untuk display selected items dengan breakdown
        * Summary section dengan total biaya dan MAK codes
        * Fungsi remove/edit items
        * Read-only mode untuk database display
      - Signal: data_changed() - emitted saat selection berubah

B. File Dimodifikasi:
   📄 app/ui/pages/pencairan/transaksi_form.py
   
   Changes:
   - Import: Tambah import DipaSelectionWidget
   - Method: Modifikasi _create_financial_section_up()
     * Ganti input estimasi_biaya manual dengan DIPA selector
     * Tambah field kode_mak_input (read-only)
     * Tambah field ket_mak_input untuk uraian kegiatan
   - Method: Tambah handler _on_dipa_selection_changed()
     * Update estimasi_input saat DIPA selection berubah
     * Update kode_mak_input dengan MAK codes
     * Update ket_mak_input dengan uraian dari items


2. INSTALASI & SETUP
====================

Step 1: Copy file dipa_selector.py
   Location: e:\\gdrive\\aplikasi\\app\\ui\\components\\dipa_selector.py

Step 2: Verifikasi imports di transaksi_form.py
   ```python
   from ...components.dipa_selector import DipaSelectionWidget
   from app.core.config import DATABASE_PATH, TAHUN_ANGGARAN
   ```

Step 3: Rebuild aplikasi
   ```bash
   cd e:\\gdrive\\aplikasi
   python build_exe.py
   ```

Step 4: Test dengan menjalankan:
   ```bash
   python main.py
   ```


3. USAGE IN CODE
================

A. Menggunakan DipaSelectionWidget dalam form:

   ```python
   # Di dalam form initialization
   from app.ui.components.dipa_selector import DipaSelectionWidget
   from app.core.config import DATABASE_PATH, TAHUN_ANGGARAN
   
   # Create widget
   self.dipa_selector = DipaSelectionWidget(
       db_path=DATABASE_PATH,
       tahun_anggaran=TAHUN_ANGGARAN,
       parent=self
   )
   
   # Connect signal
   self.dipa_selector.data_changed.connect(self._on_dipa_changed)
   
   # Add to layout
   layout.addWidget(self.dipa_selector)
   ```

B. Handle selection changes:

   ```python
   def _on_dipa_changed(self):
       total = self.dipa_selector.get_total_biaya()
       mak_codes = self.dipa_selector.get_mak_codes()
       
       # Update form fields
       self.estimasi_input.setValue(total)
       self.kode_mak_input.setText(", ".join(mak_codes))
   ```

C. Get selected data:

   ```python
   # Get total biaya
   total_biaya = self.dipa_selector.get_total_biaya()  # float
   
   # Get MAK codes list
   mak_list = self.dipa_selector.get_mak_codes()  # List[str]
   
   # Get MAK as comma-separated string
   mak_string = self.dipa_selector.get_mak_string()  # str
   
   # Get selected items (DipaItem objects)
   items = self.dipa_selector.selected_items  # List[DipaItem]
   
   # Convert items to dict for storage
   items_data = [item.to_dict() for item in items]
   ```

D. Manual control:

   ```python
   # Clear selection
   self.dipa_selector.clear_selection()
   
   # Set editable biaya (allow manual override)
   self.dipa_selector.set_editable_biaya(True)
   
   # Get current biaya value
   biaya = self.dipa_selector.total_input.value()
   ```


4. DATABASE INTEGRATION
=======================

A. Expected Database Schema:

   Table: pagu_anggaran
   ┌─────────────┬──────────────┬──────────┐
   │ Column      │ Type         │ Required │
   ├─────────────┼──────────────┼──────────┤
   │ id          │ INTEGER PK   │ Yes      │
   │ tahun_angga │ INTEGER      │ Yes      │
   │ kode_akun   │ TEXT         │ Yes      │
   │ kode_detail │ TEXT         │ No       │
   │ nomor_mak   │ TEXT         │ No       │
   │ uraian      │ TEXT         │ Yes      │
   │ jumlah      │ REAL         │ Yes      │
   │ level_kode  │ INTEGER      │ No       │
   └─────────────┴──────────────┴──────────┘

B. Sample Data Query:

   SELECT id, kode_akun, kode_detail, nomor_mak, uraian, jumlah
   FROM pagu_anggaran
   WHERE tahun_anggaran = 2026
     AND level_kode IN (7, 8)
     AND jumlah > 0
   ORDER BY kode_akun;

C. Storing DIPA References:

   Recommended: Create junction table untuk track which DIPA items
   digunakan dalam setiap transaksi:
   
   ```sql
   CREATE TABLE transaksi_dipa_items (
       id INTEGER PRIMARY KEY,
       transaksi_id INTEGER NOT NULL,
       pagu_anggaran_id INTEGER NOT NULL,
       jumlah_allocation REAL,
       created_at TIMESTAMP,
       UNIQUE(transaksi_id, pagu_anggaran_id),
       FOREIGN KEY(transaksi_id) REFERENCES pencairan_transaksi(id),
       FOREIGN KEY(pagu_anggaran_id) REFERENCES pagu_anggaran(id)
   );
   ```


5. DATA DISPLAY DETAILS
=======================

A. DipaSelectorDialog Main Table:

   Column 0: ✓ (Checkbox)
   Column 1: Kode Akun        (e.g., "5.1.01.05")
   Column 2: Kode Detail      (e.g., "01", "02")
   Column 3: MAK              (e.g., "5.1.01.05.01")
   Column 4: Uraian           (e.g., "Gaji Pegawai")
   Column 5: Jumlah           (formatted as "Rp X.XXX.XXX")
   Column 6: Level            (e.g., "Level 7", "Level 8")
   Column 7: ID               (hidden - database record ID)

   Features:
   - Multi-select dengan Ctrl+Click atau Shift+Click
   - Alternating row colors untuk readability
   - Sortable columns (klik header untuk sort)
   - Hidden ID column untuk backend reference

B. DipaSelectionWidget Table:

   Column 0: MAK              (e.g., "5.1.01.05.01")
   Column 1: Uraian           (deskripsi kegiatan)
   Column 2: Jumlah           (formatted as "Rp X.XXX.XXX")
   Column 3: Persentase       (e.g., "60.0%")
   Column 4: Tombol Hapus     (remove button)

   Features:
   - Max height 150px (scrollable jika banyak items)
   - Right-aligned numbers untuk alignment
   - Percentage auto-calculated
   - Remove button per row

C. Summary Section:

   Total Estimasi Biaya:
   - Type: QDoubleSpinBox (read-only by default)
   - Format: Prefix "Rp ", group separator, 0 decimals
   - Style: Bold green text (#27ae60), gray background
   - Range: 0 to 999,999,999,999

   Kode MAK/Akun:
   - Type: QLineEdit (read-only by default)
   - Format: Comma-separated list
   - Placeholder: "MAK akan terisi otomatis dari DIPA..."
   - Auto-deduplicated (no duplicate MAK codes)

   Uraian Kegiatan:
   - Type: QTextEdit
   - Display: One uraian per line dari selected items
   - Max height: 80px
   - Editable untuk detail notes


6. VALIDATION RULES
===================

A. Input Validation:
   
   ✓ Minimal 1 item harus dipilih
   ✓ Hanya items dengan jumlah > 0 ditampilkan
   ✓ Total biaya tidak boleh negative (by default)
   ✓ Untuk UP: total maksimal Rp 50,000,000
   ✓ Tahun anggaran harus match dengan system TAHUN_ANGGARAN

B. Data Integrity:

   ✓ Duplicate MAK codes automatically removed
   ✓ Duplicate items in selection prevented
   ✓ Total biaya always recalculated from items
   ✓ Percentage sum = 100% (or close due to rounding)

C. Error Handling:

   Error Scenarios:
   1. Database connection error
      → QMessageBox.critical("Error", "Gagal load DIPA: {error}")
   
   2. No DIPA items found
      → Dialog shows empty table
   
   3. No items selected
      → "Pilih minimal 1 item DIPA!" warning
   
   4. Invalid DIPA data
      → Logging to console/file
      → User sees partial data or error message


7. CONFIGURATION
================

A. Constants in Code:

   Format Rupiah:
   ```python
   def format_rupiah(value: float) -> str:
       return f"Rp {int(value):,.0f}".replace(",", ".")
   ```

   Color Scheme:
   - Primary: #3498db (blue buttons)
   - Success: #27ae60 (green totals)
   - Warning: #f39c12 (orange labels)
   - Dark: #2c3e50 (headers)
   - Light: #ecf0f1 (backgrounds)

B. Database Configuration:

   database_path: From app.core.config.DATABASE_PATH
   tahun_anggaran: From app.core.config.TAHUN_ANGGARAN

C. UI Sizing:

   DipaSelectorDialog:
   - Width: 1000px
   - Height: 600px
   - Modal: Yes (blocks parent)

   DipaSelectionWidget:
   - Embedded in form
   - Selected items table max-height: 150px
   - Summary group: Dynamic height

   Main Table:
   - Column widths: Auto-resize based on content
   - Column 0 (checkbox): ResizeToContents
   - Column 4 (uraian): Stretch


8. STYLING & THEME
==================

A. Default Color Scheme:

   Button (Select):
   - Background: #3498db (blue)
   - Hover: #2980b9 (darker blue)
   - Text: white, bold

   Button (Confirm/OK):
   - Background: #27ae60 (green)
   - Hover: #229954 (darker green)
   - Text: white, bold

   Input Fields:
   - Background: #ffffff (white, editable)
   - Background: #ecf0f1 (gray, read-only)
   - Border: #dcdfe6 (light gray)
   - Focus Border: #3498db (blue)

   Labels:
   - Headers: #2c3e50 (dark gray), bold, 14px
   - Warnings: #f39c12 (orange), italic, 11px
   - Totals: #27ae60 (green), bold, 12px

B. Customization:

   Untuk customize style, edit QSS strings di:
   - DipaSelectorDialog._setup_ui() line ~180
   - DipaSelectionWidget._setup_ui() line ~400


9. TROUBLESHOOTING
==================

Problem 1: Database connection error
Solution:
- Verify DATABASE_PATH in app.core.config
- Check database file exists and is readable
- Check tahun_anggaran matches database records

Problem 2: No DIPA items displayed
Solution:
- Verify pagu_anggaran table has data for current year
- Check if jumlah field has values > 0
- Check level_kode is 7 or 8

Problem 3: MAK codes not combining correctly
Solution:
- Verify each DIPA item has unique nomor_mak
- Check kode_akun and kode_detail not null
- Verify format in database matches expected pattern

Problem 4: Total biaya calculation wrong
Solution:
- Check all selected items are included in calculation
- Verify jumlah field values in database
- Check floating point precision in calculations

Problem 5: Form fields not updating
Solution:
- Verify _on_dipa_selection_changed() is called
- Check signal connection: dipa_selector.data_changed.connect(...)
- Verify form field names match (estimasi_input, kode_mak_input, etc.)


10. TESTING
===========

Unit Test Template:

```python
import pytest
from app.ui.components.dipa_selector import DipaItem, DipaSelectionWidget

def test_dipa_item_creation():
    item = DipaItem(
        dipa_id=1,
        kode_akun="5.1.01.05",
        kode_detail="01",
        uraian="Test Item",
        jumlah=1000000,
        level=8
    )
    assert item.nomor_mak == "5.1.01.05.01"
    assert item.to_dict()['jumlah'] == 1000000

def test_dipa_selector_dialog():
    # Test multi-select functionality
    # Test total calculation
    # Test MAK deduplication
    pass

def test_dipa_selection_widget():
    # Test selected items display
    # Test summary update
    # Test remove functionality
    pass
```

Integration Test:
- Open Form UP/TUP
- Click "Pilih dari DIPA"
- Select multiple items
- Verify form fields auto-filled
- Save transaksi
- Verify DIPA items stored correctly
- Edit transaksi
- Verify DIPA selection restored


11. PERFORMANCE NOTES
====================

A. Optimization Tips:

   1. Database Query:
      - Uses indexed columns: tahun_anggaran, level_kode, jumlah
      - Limit to 2 levels (7, 8) to reduce data volume
      - Consider adding WHERE jumlah > 0 in query

   2. UI Updates:
      - Summary updates only when selection changes
      - Table display limits to visible rows
      - Percentage calculation done only once per update

   3. Memory Usage:
      - Store only necessary DipaItem objects
      - Clear selection when dialog closed (if not confirmed)
      - Use setMaximumHeight on tables to prevent DOM bloat

B. Expected Load Times:

   - Load DIPA items: ~500ms - 2s (depends on DB size)
   - Filter/search: ~100ms - 500ms
   - Calculate total: <10ms
   - UI render: ~200ms - 1s


12. VERSIONING & CHANGELOG
==========================

Version 1.0 (Current):
- Multi-select DIPA items
- Auto-calculate total biaya
- Auto-extract MAK codes
- Search and filter functionality
- Summary display with percentages

Future Enhancements (v1.1):
- Batch import/export DIPA selections
- DIPA selection templates
- History of previous selections
- Budget remaining indicator
- Approval workflow integration
- Custom MAK mapping
"""
