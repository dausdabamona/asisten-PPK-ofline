# Refactoring Plan - Manager Files

## Executive Summary

Analisis terhadap 6 file manager besar (total ~346KB, ~10,000+ lines) menunjukkan adanya **duplikasi kode yang signifikan** dan **pattern UI yang berulang**. Refactoring dapat mengurangi ~40-50% lines of code dan meningkatkan maintainability.

---

## 1. Files Analyzed

| File | Size | Lines | Description |
|------|------|-------|-------------|
| `pembayaran_lainnya_manager.py` | 83KB | ~2,200 | Manager pembayaran umum |
| `harga_lifecycle_manager.py` | 66KB | ~1,800 | Manager lifecycle harga barang |
| `item_barang_manager.py` | 57KB | ~1,600 | Manager item/BOQ |
| `swakelola_manager.py` | 48KB | ~1,300 | Manager kegiatan swakelola |
| `pjlp_manager.py` | 47KB | ~1,300 | Manager PJLP |
| `perjalanan_dinas_manager.py` | 45KB | ~1,200 | Manager perjalanan dinas |

---

## 2. Common Patterns Identified

### 2.1 CurrencySpinBox (DUPLIKAT 100%)

**Ditemukan di:** `swakelola_manager.py`, `pjlp_manager.py`, `perjalanan_dinas_manager.py`

```python
class CurrencySpinBox(QDoubleSpinBox):
    """Custom SpinBox for Indonesian currency with thousand separator"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999999999)
        self.setDecimals(0)
        self.setSingleStep(100000)
        locale = QLocale(QLocale.Indonesian, QLocale.Indonesia)
        self.setLocale(locale)

    def textFromValue(self, value: float) -> str:
        return f"Rp {value:,.0f}".replace(",", ".")

    def valueFromText(self, text: str) -> float:
        clean = text.replace("Rp ", "").replace(".", "").replace(",", "").strip()
        try:
            return float(clean) if clean else 0
        except ValueError:
            return 0
```

**Rekomendasi:** Extract ke `app/ui/widgets/currency_spinbox.py`

**Estimasi pengurangan:** ~60 lines x 3 files = **~180 lines**

---

### 2.2 format_rupiah Function (DUPLIKAT 100%)

**Ditemukan di:** `item_barang_manager.py`, `pembayaran_lainnya_manager.py`, dan lainnya

```python
def format_rupiah(value):
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")
```

**Rekomendasi:** Sudah ada di `app/templates/engine.py`, gunakan import konsisten

**Estimasi pengurangan:** ~5 lines x 6 files = **~30 lines**

---

### 2.3 Pegawai ComboBox Loading Pattern

**Ditemukan di:** SEMUA manager files

```python
def load_pegawai_combo(self, combo: QComboBox):
    combo.clear()
    combo.addItem("-- Pilih Pegawai --", None)
    try:
        pegawai_list = self.db.get_all_pegawai(active_only=True)
        for p in pegawai_list:
            nama = p.get('nama', '')
            if p.get('gelar_depan'):
                nama = f"{p['gelar_depan']} {nama}"
            if p.get('gelar_belakang'):
                nama = f"{nama}, {p['gelar_belakang']}"
            combo.addItem(nama, p)
    except Exception as e:
        print(f"Error loading pegawai: {e}")

def load_ppk_combo(self):
    # Same pattern, different role filter

def load_bendahara_combo(self):
    # Same pattern, different role filter
```

**Rekomendasi:** Extract ke `app/ui/widgets/pegawai_combobox.py` dengan PegawaiComboBox widget

```python
class PegawaiComboBox(QComboBox):
    def __init__(self, role_filter=None, parent=None):
        super().__init__(parent)
        self.role_filter = role_filter
        self.load_pegawai()

    def load_pegawai(self):
        # Unified loading logic
```

**Estimasi pengurangan:** ~40 lines x 6 files = **~240 lines**

---

### 2.4 Pegawai Selection Handler Pattern

**Ditemukan di:** SEMUA manager files

```python
def on_ppk_selected(self, index):
    data = self.cmb_ppk.currentData()
    if data and isinstance(data, dict):
        nama = data.get('nama', '')
        if data.get('gelar_depan'):
            nama = f"{data['gelar_depan']} {nama}"
        if data.get('gelar_belakang'):
            nama = f"{nama}, {data['gelar_belakang']}"
        self.txt_ppk_nama.setText(nama)
        self.txt_ppk_nip.setText(data.get('nip', '') or '')

def _fill_pegawai_fields(self, data, nama_field, nip_field, jabatan_field=None):
    # Helper that exists in swakelola_manager.py
```

**Rekomendasi:** Gunakan `_fill_pegawai_fields` helper di base class

**Estimasi pengurangan:** ~25 lines x 6 files = **~150 lines**

---

### 2.5 _set_combo_by_id Helper

**Ditemukan di:** `swakelola_manager.py`, `pjlp_manager.py`, `perjalanan_dinas_manager.py`

```python
def _set_combo_by_id(self, combo: QComboBox, pegawai_id: int):
    if not pegawai_id:
        return
    for i in range(combo.count()):
        data = combo.itemData(i)
        if data and isinstance(data, dict) and data.get('id') == pegawai_id:
            combo.setCurrentIndex(i)
            return
```

**Rekomendasi:** Extract ke `app/ui/widgets/pegawai_combobox.py`

**Estimasi pengurangan:** ~10 lines x 3 files = **~30 lines**

---

### 2.6 Manager Dialog Structure

**Ditemukan di:** SEMUA files

Semua dialog mengikuti pattern yang sama:
1. `__init__` dengan data parameter
2. `setup_ui()` method
3. `load_data()` untuk edit mode
4. `get_data()` untuk collect form values
5. `save()` untuk validation dan persist

**Rekomendasi:** Create `BaseEntityDialog` class

```python
class BaseEntityDialog(QDialog):
    def __init__(self, entity_data=None, parent=None):
        super().__init__(parent)
        self.entity_data = entity_data
        self.db = get_db_manager_v4()
        self.setup_ui()
        if entity_data:
            self.load_data()

    @abstractmethod
    def setup_ui(self): pass

    @abstractmethod
    def load_data(self): pass

    @abstractmethod
    def get_data(self) -> dict: pass

    @abstractmethod
    def validate(self) -> bool: pass

    def save(self):
        if not self.validate():
            return
        data = self.get_data()
        try:
            self._persist_data(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {str(e)}")
```

**Estimasi pengurangan:** ~30 lines x 6 files = **~180 lines**

---

### 2.7 Manager List Structure

**Ditemukan di:** SEMUA files

Semua list manager memiliki struktur sama:
1. Header dengan title dan filter
2. Toolbar dengan Add/Edit/Delete/Generate buttons
3. Table dengan columns
4. Summary section
5. `load_data()`, `filter_data()`, `display_data()` methods

**Rekomendasi:** Create `BaseManagerDialog` class

```python
class BaseManagerDialog(QDialog):
    data_changed = Signal()

    # Define in subclass
    title: str
    columns: List[tuple]  # (name, width, stretch)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = get_db_manager_v4()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self._create_header()
        self._create_toolbar()
        self._create_table()
        self._create_summary()

    @abstractmethod
    def load_data(self): pass

    @abstractmethod
    def add_entity(self): pass

    @abstractmethod
    def edit_entity(self): pass
```

**Estimasi pengurangan:** ~100 lines x 6 files = **~600 lines**

---

### 2.8 GroupBox Styling Pattern

**Ditemukan di:** SEMUA files

```python
self.setStyleSheet("""
    QGroupBox {
        font-weight: bold;
        border: 1px solid #d0d0d0;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    QPushButton#btnSuccess {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 4px;
        font-weight: bold;
    }
""")
```

**Rekomendasi:** Sudah ada di `app/ui/styles/`, ensure consistent import

**Estimasi pengurangan:** ~20 lines x 6 files = **~120 lines**

---

### 2.9 Excel Template Generator Pattern

**Ditemukan di:** `item_barang_manager.py`

`ExcelTemplateGenerator` class dengan `create_upload_template()` and `parse_upload_file()` methods.

**Rekomendasi:** Extract ke `app/utils/excel_utils.py` atau `app/templates/excel/`

**Estimasi pengurangan:** Keep as utility, but centralize

---

### 2.10 Tab-based Form Layout

**Ditemukan di:** `swakelola_manager.py`, `pjlp_manager.py`, `perjalanan_dinas_manager.py`

Semua menggunakan pattern:
1. ScrollArea wrapping TabWidget
2. Multiple GroupBoxes per tab
3. FormLayout inside GroupBox

**Rekomendasi:** Create `TabbedFormDialog` base class dengan helper methods

---

## 3. Komponen yang Bisa Di-reuse

### 3.1 New Widgets (app/ui/widgets/)

| Widget | Description | Used By |
|--------|-------------|---------|
| `CurrencySpinBox` | Rupiah formatted spinbox | 4+ managers |
| `PegawaiComboBox` | Auto-load pegawai dengan role filter | 6 managers |
| `PejabatGroup` | GroupBox dengan PPK/Bendahara fields | 5 managers |
| `AnggaranGroup` | GroupBox dengan sumber dana, akun fields | 4 managers |
| `DateRangeWidget` | Tanggal mulai/selesai pair | 4 managers |
| `SearchableTable` | Table dengan filter bawaan | 6 managers |

### 3.2 New Base Classes (app/ui/base/)

| Class | Description |
|-------|-------------|
| `BaseEntityDialog` | Base untuk Add/Edit dialogs |
| `BaseManagerDialog` | Base untuk List managers |
| `TabbedFormDialog` | Dialog dengan tabs dan ScrollArea |

### 3.3 Utility Functions (app/utils/)

| Function | Description |
|----------|-------------|
| `format_nama_lengkap(pegawai)` | Format nama dengan gelar |
| `parse_currency(text)` | Parse Rupiah string ke number |
| `format_currency(value)` | Format number ke Rupiah string |

---

## 4. Rekomendasi Refactoring per File

### 4.1 pembayaran_lainnya_manager.py (83KB)

**Current:** Monolithic file dengan multiple payment types

**Recommendation:**
- Split ke folder `app/ui/pembayaran/`:
  - `base_pembayaran.py` - Base classes
  - `honorarium_manager.py`
  - `jamuan_manager.py`
  - `pembayaran_list.py` - Main list view
- Use common widgets untuk form fields

**Estimated reduction:** ~35% (~750 lines)

---

### 4.2 harga_lifecycle_manager.py (66KB)

**Current:** Complex lifecycle tracking dengan multiple stages

**Recommendation:**
- Split ke folder `app/ui/harga/`:
  - `harga_base.py` - Base classes
  - `survey_toko_widget.py` - Survey harga component
  - `hps_calculator.py` - HPS calculation logic
  - `lifecycle_manager.py` - Main manager

**Estimated reduction:** ~30% (~540 lines)

---

### 4.3 item_barang_manager.py (57KB)

**Current:** BOQ management dengan Excel import

**Recommendation:**
- Extract `ExcelTemplateGenerator` ke `app/utils/excel_utils.py`
- Use `CurrencySpinBox` widget
- Split `ItemBarangDialog` dan `ItemBarangManager` ke separate files

**Estimated reduction:** ~25% (~400 lines)

---

### 4.4 swakelola_manager.py (48KB)

**Current:** Swakelola activity management

**Recommendation:**
- Use `BaseEntityDialog` for `SwakelolaDialog`
- Use `BaseManagerDialog` for `SwakelolaManager`
- Use common widgets (`CurrencySpinBox`, `PegawaiComboBox`, `PejabatGroup`)

**Estimated reduction:** ~40% (~520 lines)

---

### 4.5 pjlp_manager.py (47KB)

**Current:** PJLP contract dan payment management

**Recommendation:**
- Split: `PJLPDialog`, `PembayaranPJLPDialog`, `PJLPManager`
- Use `BaseEntityDialog` dan `BaseManagerDialog`
- Use common widgets

**Estimated reduction:** ~40% (~520 lines)

---

### 4.6 perjalanan_dinas_manager.py (45KB)

**Current:** Travel management dengan cost calculation

**Recommendation:**
- Use `BaseEntityDialog` for `PerjalananDinasDialog`
- Use `BaseManagerDialog` for `PerjalananDinasManager`
- Use common widgets
- Extract cost calculation ke separate utility

**Estimated reduction:** ~40% (~480 lines)

---

## 5. Estimated Total Reduction

| Category | Lines Saved |
|----------|-------------|
| CurrencySpinBox extraction | 180 |
| format_rupiah consolidation | 30 |
| PegawaiComboBox extraction | 240 |
| Pegawai handlers consolidation | 150 |
| _set_combo_by_id extraction | 30 |
| BaseEntityDialog | 180 |
| BaseManagerDialog | 600 |
| StyleSheet consolidation | 120 |
| **Total** | **~1,530 lines** |

**Percentage reduction:** ~15% of total (~10,000 lines)

Dengan refactoring lebih dalam (splitting files, removing dead code):
**Estimated total reduction:** ~3,500-4,000 lines (**~35-40%**)

---

## 6. Implementation Priority

### Phase 1: Quick Wins (Low Risk)
1. Extract `CurrencySpinBox` ke `app/ui/widgets/currency_spinbox.py`
2. Consolidate `format_rupiah` imports
3. Move common styles ke `app/ui/styles/`

### Phase 2: Common Widgets (Medium Risk)
1. Create `PegawaiComboBox` widget
2. Create `PejabatGroup` widget
3. Create `AnggaranGroup` widget

### Phase 3: Base Classes (Higher Risk)
1. Create `BaseEntityDialog`
2. Create `BaseManagerDialog`
3. Migrate existing dialogs one by one

### Phase 4: File Splitting (Major Refactor)
1. Split `pembayaran_lainnya_manager.py`
2. Split `harga_lifecycle_manager.py`
3. Update all imports

---

## 7. Testing Strategy

1. **Before refactoring:** Create integration tests untuk setiap manager
2. **During refactoring:** Run tests after each change
3. **After refactoring:** Full regression test

---

## 8. Notes

- Semua manager menggunakan `get_db_manager_v4()` - consistent
- Signal `data_changed` digunakan untuk refresh parent
- Pattern Tab + ScrollArea + GroupBox sangat konsisten
- Sudah ada base classes di `app/ui/base/` yang bisa di-extend
