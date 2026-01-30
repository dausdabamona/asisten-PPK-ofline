"""
PPK DOCUMENT FACTORY - Dokumen Generator Service
=================================================
Service untuk generate dokumen dari template untuk workflow pencairan.

Features:
- Generate dokumen Word/Excel dari template
- Replace placeholder dengan data transaksi
- Simpan ke folder terstruktur per transaksi
- Track status dokumen di database
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from docx import Document
from docx.shared import Pt
import openpyxl

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output" / "dokumen"


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah."""
    if value is None:
        return "Rp 0"
    return f"Rp {value:,.0f}".replace(",", ".")


def terbilang(n: float) -> str:
    """Konversi angka ke terbilang dalam Bahasa Indonesia."""
    if n == 0:
        return "nol rupiah"

    satuan = ["", "satu", "dua", "tiga", "empat", "lima",
              "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]

    n = int(n)

    if n < 0:
        return "minus " + terbilang(-n)
    elif n < 12:
        return satuan[n]
    elif n < 20:
        return satuan[n - 10] + " belas"
    elif n < 100:
        return satuan[n // 10] + " puluh " + satuan[n % 10]
    elif n < 200:
        return "seratus " + terbilang(n - 100)
    elif n < 1000:
        return satuan[n // 100] + " ratus " + terbilang(n % 100)
    elif n < 2000:
        return "seribu " + terbilang(n - 1000)
    elif n < 1000000:
        return terbilang(n // 1000) + " ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        return terbilang(n // 1000000) + " juta " + terbilang(n % 1000000)
    elif n < 1000000000000:
        return terbilang(n // 1000000000) + " miliar " + terbilang(n % 1000000000)
    else:
        return terbilang(n // 1000000000000) + " triliun " + terbilang(n % 1000000000000)


def format_tanggal(date_str: str) -> str:
    """Format tanggal ke format Indonesia."""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, datetime):
            dt = date_str
        else:
            dt = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")

        bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                 "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        return f"{dt.day} {bulan[dt.month]} {dt.year}"
    except:
        return str(date_str)


class DokumenGenerator:
    """Service untuk generate dokumen dari template."""

    # Mapping format functions
    FORMATTERS = {
        'rupiah': format_rupiah,
        'terbilang': lambda x: terbilang(x).title() + " Rupiah",
        'tanggal': format_tanggal,
        'tanggal_panjang': format_tanggal,  # Alias for tanggal
        'upper': lambda x: str(x).upper() if x else "",
        'lower': lambda x: str(x).lower() if x else "",
        'title': lambda x: str(x).title() if x else "",
    }

    def __init__(self, db=None):
        """Initialize generator with optional database connection."""
        self.db = db
        self._ensure_directories()

    def _ensure_directories(self):
        """Pastikan folder output ada."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _sanitize_folder_name(self, name: str) -> str:
        """Sanitize folder name - remove invalid characters."""
        if not name:
            return "unnamed"
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        # Remove leading/trailing spaces and dots
        name = name.strip('. ')
        # Limit length
        if len(name) > 50:
            name = name[:50]
        return name or "unnamed"

    def get_output_folder(self, transaksi: Dict[str, Any] = None,
                          mekanisme: str = None, nama_kegiatan: str = None) -> Path:
        """
        Get atau buat folder output untuk transaksi.

        Format folder: output/dokumen/{MEKANISME}/{BULAN_TAHUN}/{NAMA_KEGIATAN}/
        Contoh: output/dokumen/UP/Januari_2026/Belanja_ATK_Kantor/

        Args:
            transaksi: Dictionary data transaksi (opsional)
            mekanisme: Jenis pembayaran (UP, TUP, LS)
            nama_kegiatan: Nama kegiatan
        """
        # Get values from transaksi if provided
        if transaksi:
            mekanisme = mekanisme or transaksi.get('mekanisme', 'LAINNYA')
            nama_kegiatan = nama_kegiatan or transaksi.get('nama_kegiatan', 'Kegiatan')

        # Default values
        mekanisme = mekanisme or 'LAINNYA'
        nama_kegiatan = nama_kegiatan or 'Kegiatan'

        # Get current month and year in Indonesian
        now = datetime.now()
        bulan_names = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                       "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        bulan_tahun = f"{bulan_names[now.month]}_{now.year}"

        # Sanitize nama kegiatan for folder name
        nama_folder = self._sanitize_folder_name(nama_kegiatan)

        # Build folder path: MEKANISME/BULAN_TAHUN/NAMA_KEGIATAN
        folder = OUTPUT_DIR / mekanisme.upper() / bulan_tahun / nama_folder
        folder.mkdir(parents=True, exist_ok=True)

        return folder

    def get_output_folder_legacy(self, transaksi_kode: str) -> Path:
        """Get folder output berdasarkan kode transaksi (legacy method)."""
        folder = OUTPUT_DIR / transaksi_kode
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get path template file."""
        if not template_name:
            return None

        # Check in word folder first
        word_path = TEMPLATES_DIR / "word" / template_name
        if word_path.exists():
            return word_path

        # Check in excel folder
        excel_path = TEMPLATES_DIR / "excel" / template_name
        if excel_path.exists():
            return excel_path

        # Check root templates folder
        root_path = TEMPLATES_DIR / template_name
        if root_path.exists():
            return root_path

        return None

    def prepare_data(self, transaksi: Dict[str, Any], satker: Dict[str, Any] = None,
                     pegawai: Dict[str, Any] = None, rincian: List[Dict] = None) -> Dict[str, Any]:
        """Prepare data dictionary for template merging."""
        data = {}

        # Data transaksi
        data['kode_transaksi'] = transaksi.get('kode', transaksi.get('kode_transaksi', ''))
        data['nomor_kuitansi'] = data['kode_transaksi']  # Alias for kuitansi template
        data['nama_kegiatan'] = transaksi.get('nama_kegiatan', '')
        data['kode_akun'] = transaksi.get('kode_akun', '')
        data['sumber_dana'] = transaksi.get('sumber_dana', transaksi.get('kode_akun', ''))
        data['unit_kerja'] = transaksi.get('unit_kerja', '')
        data['estimasi_biaya'] = transaksi.get('estimasi_biaya', 0)
        data['uang_muka'] = transaksi.get('uang_muka', 0)
        data['realisasi'] = transaksi.get('realisasi', 0)
        data['selisih'] = data['realisasi'] - data['uang_muka']
        data['mekanisme'] = transaksi.get('mekanisme', '')
        data['jenis_kegiatan'] = transaksi.get('jenis_kegiatan', '')

        # Tanggal
        data['tanggal_pengajuan'] = transaksi.get('tanggal_pengajuan', '')
        data['tanggal_pencairan'] = transaksi.get('tanggal_pencairan', '')
        data['tanggal_selesai'] = transaksi.get('tanggal_selesai', '')
        data['tanggal_hari_ini'] = datetime.now().strftime("%Y-%m-%d")
        data['tanggal_dokumen'] = transaksi.get('tanggal_dokumen', datetime.now().strftime("%Y-%m-%d"))

        # Data satker
        if satker:
            data['satker_nama'] = satker.get('nama', '')
            data['satker_kode'] = satker.get('kode', '')
            data['satker_alamat'] = satker.get('alamat', '')
            data['satker_kota'] = satker.get('kota', '')
            data['kementerian'] = satker.get('kementerian', '')
            data['unit_organisasi'] = satker.get('unit_organisasi', '')
            data['lokasi'] = satker.get('kota', '')

        # Data penerima/pegawai (Yang Mengajukan)
        if pegawai:
            data['penerima_nama'] = pegawai.get('nama', transaksi.get('penerima_nama', ''))
            data['penerima_nip'] = pegawai.get('nip', transaksi.get('penerima_nip', ''))
            data['penerima_jabatan'] = pegawai.get('jabatan', transaksi.get('penerima_jabatan', ''))
        else:
            data['penerima_nama'] = transaksi.get('penerima_nama', '')
            data['penerima_nip'] = transaksi.get('penerima_nip', '')
            data['penerima_jabatan'] = transaksi.get('penerima_jabatan', '')

        # Alias for template compatibility
        data['yang_mengajukan_nama'] = data['penerima_nama']
        data['yang_mengajukan_nip'] = data['penerima_nip']
        data['yang_mengajukan_jabatan'] = data['penerima_jabatan']

        # Data PPK, PPSPM, KPA dari satker
        if satker:
            data['ppk_nama'] = satker.get('ppk_nama', '')
            data['ppk_nip'] = satker.get('ppk_nip', '')
            data['kpa_nama'] = satker.get('kpa_nama', '')
            data['kpa_nip'] = satker.get('kpa_nip', '')
            data['bendahara_nama'] = satker.get('bendahara_nama', '')
            data['bendahara_nip'] = satker.get('bendahara_nip', '')
            # PPSPM sebagai Verifikator
            data['ppspm_nama'] = satker.get('ppspm_nama', '')
            data['ppspm_nip'] = satker.get('ppspm_nip', '')
            data['ppspm_jabatan'] = satker.get('ppspm_jabatan', '')
            data['verifikator_nama'] = satker.get('ppspm_nama', '')
            data['verifikator_nip'] = satker.get('ppspm_nip', '')

        # Override verifikator from transaksi if provided
        if transaksi.get('verifikator_nama'):
            data['verifikator_nama'] = transaksi.get('verifikator_nama', '')
            data['verifikator_nip'] = transaksi.get('verifikator_nip', '')
            data['ppspm_nama'] = transaksi.get('verifikator_nama', '')
            data['ppspm_nip'] = transaksi.get('verifikator_nip', '')

        # Override bendahara from transaksi if provided (untuk kuitansi)
        if transaksi.get('bendahara_nama'):
            data['bendahara_nama'] = transaksi.get('bendahara_nama', '')
            data['bendahara_nip'] = transaksi.get('bendahara_nip', '')

        # Data kuitansi uang muka
        data['uang_muka'] = transaksi.get('uang_muka', 0)
        data['persentase_um'] = transaksi.get('persentase_um', '100%')

        # Rincian items
        if rincian:
            data['rincian_items'] = rincian
            data['total_rincian'] = sum(item.get('jumlah', 0) for item in rincian)
            data['jumlah_item'] = len(rincian)

        # Data khusus Lembar Permintaan (LBR_REQ) - PPn calculation
        if transaksi.get('subtotal') is not None:
            data['subtotal'] = transaksi.get('subtotal', 0)
            data['ppn_rate'] = transaksi.get('ppn_rate', 0)
            data['ppn_amount'] = transaksi.get('ppn_amount', 0)
            data['ppn_persen'] = transaksi.get('ppn_persen', '0%')
            data['grand_total'] = transaksi.get('grand_total', 0)
        elif rincian:
            # Calculate from rincian if not provided
            data['subtotal'] = data['total_rincian']
            data['ppn_rate'] = 0
            data['ppn_amount'] = 0
            data['ppn_persen'] = '0%'
            data['grand_total'] = data['total_rincian']

        # Override KPA from transaksi if provided (untuk Lembar Permintaan)
        if transaksi.get('kpa_nama'):
            data['kpa_nama'] = transaksi.get('kpa_nama', '')
            data['kpa_nip'] = transaksi.get('kpa_nip', '')

        # Data Mengetahui (untuk Lembar Permintaan - 4 tanda tangan)
        data['mengetahui_nama'] = transaksi.get('mengetahui_nama', '')
        data['mengetahui_nip'] = transaksi.get('mengetahui_nip', '')
        data['jabatan_mengetahui'] = transaksi.get('jabatan_mengetahui', '')

        # Prepare rincian placeholders for template (up to 10 items)
        if rincian:
            for i, item in enumerate(rincian[:10], 1):
                data[f'rincian_{i}_nama'] = item.get('nama_barang', item.get('uraian', ''))
                data[f'rincian_{i}_spek'] = item.get('spesifikasi', '')
                data[f'rincian_{i}_vol'] = str(item.get('volume', ''))
                data[f'rincian_{i}_satuan'] = item.get('satuan', '')
                data[f'rincian_{i}_harga'] = item.get('harga_satuan', 0)
                data[f'rincian_{i}_total'] = item.get('jumlah', 0)

            # Clear unused placeholders
            for i in range(len(rincian) + 1, 11):
                data[f'rincian_{i}_nama'] = ''
                data[f'rincian_{i}_spek'] = ''
                data[f'rincian_{i}_vol'] = ''
                data[f'rincian_{i}_satuan'] = ''
                data[f'rincian_{i}_harga'] = ''
                data[f'rincian_{i}_total'] = ''

        return data

    def _apply_format(self, value: Any, format_type: str) -> str:
        """Apply format to value."""
        if format_type in self.FORMATTERS:
            try:
                return self.FORMATTERS[format_type](value)
            except:
                return str(value) if value else ""
        return str(value) if value else ""

    def _replace_placeholder(self, text: str, data: Dict[str, Any]) -> str:
        """Replace all {{placeholder}} or {{placeholder:format}} in text."""
        if not text or '{{' not in text:
            return text

        import re
        pattern = r'\{\{(\w+)(?::(\w+))?\}\}'

        def replacer(match):
            key = match.group(1)
            fmt = match.group(2)
            value = data.get(key, '')

            if fmt:
                return self._apply_format(value, fmt)
            return str(value) if value else ""

        return re.sub(pattern, replacer, text)

    def _process_paragraph(self, paragraph, data: Dict[str, Any]):
        """Process a paragraph to replace placeholders."""
        if not paragraph.text or '{{' not in paragraph.text:
            return

        # Get full text and replace
        full_text = paragraph.text
        new_text = self._replace_placeholder(full_text, data)

        if full_text != new_text:
            # Clear runs and set new text
            for run in paragraph.runs:
                run.text = ""
            if paragraph.runs:
                paragraph.runs[0].text = new_text

    def _process_table(self, table, data: Dict[str, Any]):
        """Process a table to replace placeholders."""
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    self._process_paragraph(paragraph, data)

    def merge_word_document(self, template_path: Path, data: Dict[str, Any],
                           output_path: Path) -> bool:
        """Merge data into Word document template."""
        try:
            doc = Document(str(template_path))

            # Process all paragraphs
            for paragraph in doc.paragraphs:
                self._process_paragraph(paragraph, data)

            # Process all tables
            for table in doc.tables:
                self._process_table(table, data)

            # Process headers and footers
            for section in doc.sections:
                if section.header:
                    for paragraph in section.header.paragraphs:
                        self._process_paragraph(paragraph, data)
                if section.footer:
                    for paragraph in section.footer.paragraphs:
                        self._process_paragraph(paragraph, data)

            # Save
            doc.save(str(output_path))
            return True

        except Exception as e:
            print(f"Error merging Word document: {e}")
            return False

    def merge_excel_document(self, template_path: Path, data: Dict[str, Any],
                            output_path: Path) -> bool:
        """Merge data into Excel document template."""
        try:
            wb = openpyxl.load_workbook(str(template_path))

            for sheet in wb.worksheets:
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.value and isinstance(cell.value, str) and '{{' in cell.value:
                            cell.value = self._replace_placeholder(cell.value, data)

            wb.save(str(output_path))
            return True

        except Exception as e:
            print(f"Error merging Excel document: {e}")
            return False

    def generate_document(self, transaksi: Dict[str, Any], kode_dokumen: str,
                         template_name: str, satker: Dict[str, Any] = None,
                         pegawai: Dict[str, Any] = None,
                         rincian: List[Dict] = None,
                         additional_data: Dict[str, Any] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate dokumen dari template.

        Args:
            transaksi: Data transaksi
            kode_dokumen: Kode dokumen (e.g., LBR_REQ, KUIT_UM)
            template_name: Nama file template
            satker: Data satuan kerja
            pegawai: Data pegawai/penerima
            rincian: List rincian barang/jasa
            additional_data: Data tambahan untuk merge

        Returns:
            Tuple of (output_path, error_message)
        """
        # Get template
        template_path = self.get_template_path(template_name)
        if not template_path:
            return None, f"Template '{template_name}' tidak ditemukan"

        # Prepare data
        data = self.prepare_data(transaksi, satker, pegawai, rincian)

        # Add additional data
        if additional_data:
            data.update(additional_data)

        # Create output folder with new naming: MEKANISME/BULAN_TAHUN/NAMA_KEGIATAN
        output_folder = self.get_output_folder(transaksi=transaksi)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = template_path.suffix
        output_filename = f"{kode_dokumen}_{timestamp}{ext}"
        output_path = output_folder / output_filename

        # Merge document
        if ext.lower() == '.docx':
            success = self.merge_word_document(template_path, data, output_path)
        elif ext.lower() == '.xlsx':
            success = self.merge_excel_document(template_path, data, output_path)
        else:
            return None, f"Format template '{ext}' tidak didukung"

        if success:
            return str(output_path), None
        else:
            return None, "Gagal generate dokumen"

    def open_document(self, filepath: str) -> bool:
        """Open document with default application."""
        import subprocess
        import platform

        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
            return True
        except Exception as e:
            print(f"Error opening document: {e}")
            return False

    def open_folder(self, transaksi: Dict[str, Any] = None,
                    mekanisme: str = None, nama_kegiatan: str = None) -> bool:
        """Open output folder for transaksi."""
        folder = self.get_output_folder(transaksi, mekanisme, nama_kegiatan)
        return self.open_document(str(folder))


# Singleton instance
_generator_instance = None

def get_dokumen_generator(db=None) -> DokumenGenerator:
    """Get singleton instance of DokumenGenerator."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = DokumenGenerator(db)
    return _generator_instance
