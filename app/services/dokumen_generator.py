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
        return "nol"

    satuan = ["", "satu", "dua", "tiga", "empat", "lima",
              "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]

    n = int(n)

    def _terbilang_internal(num: int) -> str:
        """Internal recursive function."""
        if num == 0:
            return ""
        elif num < 0:
            return "minus " + _terbilang_internal(-num)
        elif num < 12:
            return satuan[num]
        elif num < 20:
            return satuan[num - 10] + " belas"
        elif num < 100:
            sisa = num % 10
            return satuan[num // 10] + " puluh" + (" " + satuan[sisa] if sisa > 0 else "")
        elif num < 200:
            sisa = _terbilang_internal(num - 100)
            return "seratus" + (" " + sisa if sisa else "")
        elif num < 1000:
            sisa = _terbilang_internal(num % 100)
            return satuan[num // 100] + " ratus" + (" " + sisa if sisa else "")
        elif num < 2000:
            sisa = _terbilang_internal(num - 1000)
            return "seribu" + (" " + sisa if sisa else "")
        elif num < 1000000:
            sisa = _terbilang_internal(num % 1000)
            return _terbilang_internal(num // 1000) + " ribu" + (" " + sisa if sisa else "")
        elif num < 1000000000:
            sisa = _terbilang_internal(num % 1000000)
            return _terbilang_internal(num // 1000000) + " juta" + (" " + sisa if sisa else "")
        elif num < 1000000000000:
            sisa = _terbilang_internal(num % 1000000000)
            return _terbilang_internal(num // 1000000000) + " miliar" + (" " + sisa if sisa else "")
        else:
            sisa = _terbilang_internal(num % 1000000000000)
            return _terbilang_internal(num // 1000000000000) + " triliun" + (" " + sisa if sisa else "")

    result = _terbilang_internal(n)
    # Clean up multiple spaces
    return ' '.join(result.split())


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

    def generate_nomor_dokumen(self, kode_dokumen: str, tahun: int = None, bulan: int = None) -> str:
        """
        Generate nomor dokumen auto-increment.
        Format: NNN-KODE/BB/YYYY (e.g., 001-LBR_REQ/01/2026)

        Args:
            kode_dokumen: Kode jenis dokumen (LBR_REQ, KUIT_UM, etc.)
            tahun: Tahun (default: tahun sekarang)
            bulan: Bulan (default: bulan sekarang)

        Returns:
            Nomor dokumen yang sudah diformat
        """
        from datetime import datetime

        now = datetime.now()
        tahun = tahun or now.year
        bulan = bulan or now.month

        # Get or create counter from database
        try:
            from app.core.database_v4 import get_db_manager_v4
            db = get_db_manager_v4()

            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Get current counter for this doc_type and year
                cursor.execute("""
                    SELECT counter FROM doc_counter
                    WHERE doc_type = ? AND tahun = ?
                """, (kode_dokumen, tahun))

                row = cursor.fetchone()

                if row:
                    counter = row[0] + 1
                    cursor.execute("""
                        UPDATE doc_counter
                        SET counter = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE doc_type = ? AND tahun = ?
                    """, (counter, kode_dokumen, tahun))
                else:
                    counter = 1
                    cursor.execute("""
                        INSERT INTO doc_counter (doc_type, tahun, counter)
                        VALUES (?, ?, ?)
                    """, (kode_dokumen, tahun, counter))

                conn.commit()

        except Exception as e:
            print(f"Error generating nomor dokumen: {e}")
            counter = 1

        # Format: NNN-KODE/BB/YYYY
        nomor = f"{counter:03d}-{kode_dokumen}/{bulan:02d}/{tahun}"
        return nomor

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
        data['kode_transaksi'] = transaksi.get('kode', '')
        data['nama_kegiatan'] = transaksi.get('nama_kegiatan', '')
        data['kode_akun'] = transaksi.get('kode_akun', '')
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

        # Data satker
        if satker:
            data['satker_nama'] = satker.get('nama', '')
            data['satker_kode'] = satker.get('kode', '')
            data['satker_alamat'] = satker.get('alamat', '')
            data['satker_kota'] = satker.get('kota', '')
            data['kementerian'] = satker.get('kementerian', '')
            data['unit_organisasi'] = satker.get('unit_organisasi', '')
            data['lokasi'] = satker.get('kota', '')

        # Data penerima/pegawai
        if pegawai:
            data['penerima_nama'] = pegawai.get('nama', transaksi.get('penerima_nama', ''))
            data['penerima_nip'] = pegawai.get('nip', transaksi.get('penerima_nip', ''))
            data['penerima_jabatan'] = pegawai.get('jabatan', transaksi.get('penerima_jabatan', ''))
        else:
            data['penerima_nama'] = transaksi.get('penerima_nama', '')
            data['penerima_nip'] = transaksi.get('penerima_nip', '')
            data['penerima_jabatan'] = transaksi.get('penerima_jabatan', '')

        # Data PPK dari satker
        if satker:
            data['ppk_nama'] = satker.get('ppk_nama', '')
            data['ppk_nip'] = satker.get('ppk_nip', '')
            data['kpa_nama'] = satker.get('kpa_nama', '')
            data['kpa_nip'] = satker.get('kpa_nip', '')
            data['bendahara_nama'] = satker.get('bendahara_nama', '')
            data['bendahara_nip'] = satker.get('bendahara_nip', '')

        # Rincian items
        if rincian:
            data['rincian_items'] = rincian
            total_rincian = sum(item.get('jumlah', 0) for item in rincian)
            data['total_rincian'] = total_rincian
            data['total'] = total_rincian  # Also set 'total' for template compatibility
            data['jumlah_item'] = len(rincian)

            # Formatted subtotal
            data['subtotal'] = format_rupiah(total_rincian)

            # PPN calculation (11%)
            ppn_persen = transaksi.get('ppn_persen', 0)
            if ppn_persen > 0:
                data['ppn_persen'] = ppn_persen
                ppn_nilai = total_rincian * ppn_persen / 100
                data['ppn_nilai'] = format_rupiah(ppn_nilai)
                total_dengan_ppn = total_rincian + ppn_nilai
                data['total_dengan_ppn'] = format_rupiah(total_dengan_ppn)
                data['grand_total'] = total_dengan_ppn
            else:
                data['ppn_persen'] = 0
                data['ppn_nilai'] = format_rupiah(0)
                data['total_dengan_ppn'] = format_rupiah(total_rincian)
                data['grand_total'] = total_rincian

            # Uang muka calculation (80% or 90% options)
            uang_muka_persen = transaksi.get('uang_muka_persen', 100)
            data['uang_muka_persen'] = uang_muka_persen
            uang_muka_nilai = data['grand_total'] * uang_muka_persen / 100
            data['uang_muka_nilai'] = format_rupiah(uang_muka_nilai)
            data['nilai_diterima'] = format_rupiah(uang_muka_nilai)

            # Terbilang for the final amount
            final_amount = uang_muka_nilai if uang_muka_persen < 100 else data['grand_total']
            data['terbilang'] = terbilang(final_amount).title() + " Rupiah"

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

    def _remove_rincian_tables(self, doc):
        """Remove tables containing RINCIAN from document (for summary-only documents)."""
        tables_to_remove = []

        for table in doc.tables:
            # Check if any cell contains RINCIAN
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.upper()
                    if 'RINCIAN' in cell_text:
                        tables_to_remove.append(table)
                        break
                else:
                    continue
                break

        # Also remove paragraphs containing RINCIAN header
        paragraphs_to_clear = []
        for para in doc.paragraphs:
            if 'RINCIAN' in para.text.upper():
                paragraphs_to_clear.append(para)

        # Remove marked tables
        for table in tables_to_remove:
            tbl_element = table._tbl
            tbl_element.getparent().remove(tbl_element)

        # Clear rincian header paragraphs
        for para in paragraphs_to_clear:
            para.clear()

    def _normalize_paragraph_spacing(self, doc):
        """
        Normalize paragraph spacing to single line spacing (1.0) without
        extra space before/after paragraphs.
        """
        from docx.shared import Pt, Twips
        from docx.enum.text import WD_LINE_SPACING

        def normalize_para(para):
            """Apply single line spacing to a paragraph."""
            para_format = para.paragraph_format
            # Set single line spacing (1.0)
            para_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            para_format.line_spacing = 1.0
            # Remove spacing before and after
            para_format.space_before = Pt(0)
            para_format.space_after = Pt(0)

        # Process all paragraphs in document body
        for para in doc.paragraphs:
            normalize_para(para)

        # Process paragraphs in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        normalize_para(para)

        # Process headers and footers
        for section in doc.sections:
            if section.header:
                for para in section.header.paragraphs:
                    normalize_para(para)
            if section.footer:
                for para in section.footer.paragraphs:
                    normalize_para(para)

    def _process_table(self, table, data: Dict[str, Any]):
        """Process a table to replace placeholders, including rincian rows."""
        from copy import deepcopy
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        rincian_items = data.get('rincian_items', [])
        rincian_row_idx = None

        # First pass: identify rincian row
        for idx, row in enumerate(table.rows):
            row_text = ''.join(cell.text for cell in row.cells)
            if '{{rincian_' in row_text:
                rincian_row_idx = idx
                break

        # If there's a rincian row, handle it specially
        if rincian_row_idx is not None and rincian_items:
            template_row = table.rows[rincian_row_idx]
            template_row_xml = template_row._tr

            # Get cells template text for cloning
            template_cells_text = []
            for cell in template_row.cells:
                cell_texts = []
                for para in cell.paragraphs:
                    cell_texts.append(para.text)
                template_cells_text.append(cell_texts)

            # Process rows before rincian
            for idx, row in enumerate(table.rows):
                if idx < rincian_row_idx:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            self._process_paragraph(paragraph, data)

            # Insert rows for all rincian items
            inserted_rows = []
            for item_idx, item in enumerate(rincian_items):
                harga = item.get('harga_satuan', 0)
                jumlah = item.get('jumlah', 0)
                item_data = {
                    'rincian_no': item_idx + 1,
                    'rincian_uraian': item.get('uraian', ''),
                    'rincian_volume': item.get('volume', 1),
                    'rincian_satuan': item.get('satuan', ''),
                    'rincian_harga': format_rupiah(harga),
                    'rincian_jumlah': format_rupiah(jumlah),
                }
                merged_data = {**data, **item_data}

                if item_idx == 0:
                    # Use existing template row for first item
                    for cell in template_row.cells:
                        for paragraph in cell.paragraphs:
                            self._process_paragraph(paragraph, merged_data)
                else:
                    # Create new row by copying XML
                    new_tr = deepcopy(template_row_xml)
                    # Insert after template row (or last inserted row)
                    template_row_xml.addnext(new_tr)

                    # Get the new row object
                    new_row_idx = rincian_row_idx + item_idx
                    new_row = table.rows[new_row_idx]

                    # Fill in the data
                    for cell_idx, cell in enumerate(new_row.cells):
                        for para_idx, paragraph in enumerate(cell.paragraphs):
                            if para_idx < len(template_cells_text[cell_idx]):
                                src_text = template_cells_text[cell_idx][para_idx]
                                new_text = self._replace_placeholder(src_text, merged_data)
                                paragraph.text = new_text

            # Process rows after rincian (need to recalculate indices)
            rows_after_start = rincian_row_idx + len(rincian_items)
            for idx in range(rows_after_start, len(table.rows)):
                row = table.rows[idx]
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._process_paragraph(paragraph, data)
        else:
            # No rincian rows, process normally
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self._process_paragraph(paragraph, data)

    def merge_word_document(self, template_path: Path, data: Dict[str, Any],
                           output_path: Path, remove_rincian_table: bool = False) -> bool:
        """Merge data into Word document template."""
        try:
            doc = Document(str(template_path))

            # Remove rincian tables if requested (for KUIT_RAMP summary-only)
            if remove_rincian_table:
                self._remove_rincian_tables(doc)

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

            # Normalize paragraph spacing to single line (1.0) without extra spacing
            self._normalize_paragraph_spacing(doc)

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

        # Add nomor_dokumen auto-generated
        if not data.get('nomor_dokumen'):
            data['nomor_dokumen'] = self.generate_nomor_dokumen(kode_dokumen)

        # Add tanggal_dokumen formatted
        tanggal_dokumen_raw = data.get('tanggal_dokumen') or datetime.now().strftime("%Y-%m-%d")
        data['tanggal_dokumen'] = format_tanggal(tanggal_dokumen_raw)

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
        # For KUIT_RAMP, remove rincian tables (summary only)
        remove_rincian = kode_dokumen == 'KUIT_RAMP'

        if ext.lower() == '.docx':
            success = self.merge_word_document(template_path, data, output_path, remove_rincian_table=remove_rincian)
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

    def get_document_checklist(self, transaksi: Dict[str, Any], fase: int = None) -> List[Dict[str, Any]]:
        """
        Get checklist of required documents and their upload status.

        Args:
            transaksi: Data transaksi
            fase: Specific fase to check (optional, checks all if None)

        Returns:
            List of document items with status
        """
        from ..config.workflow_config import get_workflow

        mekanisme = transaksi.get('mekanisme', 'UP')
        jenis_kegiatan = transaksi.get('jenis_kegiatan', '')
        workflow = get_workflow(mekanisme)

        if not workflow:
            return []

        # Get output folder
        output_folder = self.get_output_folder(transaksi=transaksi)

        # Get all files in output folder
        existing_files = []
        if output_folder.exists():
            existing_files = [f.name for f in output_folder.iterdir() if f.is_file()]

        checklist = []
        fases = [fase] if fase else list(workflow.get('fase', {}).keys())

        for f in fases:
            fase_config = workflow.get('fase', {}).get(f, {})

            # Get all dokumen lists for this fase
            dokumen_lists = ['dokumen', 'dokumen_dengan_sk', 'dokumen_kepanitiaan',
                           'dokumen_rapat', 'dokumen_jamuan', 'dokumen_kontrak',
                           'dokumen_surat_tugas', 'dokumen_rapat_jamuan', 'dokumen_lainnya']

            for list_name in dokumen_lists:
                for dok in fase_config.get(list_name, []):
                    # Filter by jenis_kegiatan if specified
                    dok_jenis = dok.get('jenis_kegiatan', [])
                    if dok_jenis and jenis_kegiatan not in dok_jenis:
                        continue

                    kode = dok.get('kode', '')
                    kategori = dok.get('kategori', 'opsional')

                    # Check if document exists (by kode prefix in filename)
                    is_uploaded = any(f.startswith(kode) for f in existing_files)
                    file_path = None
                    if is_uploaded:
                        for ef in existing_files:
                            if ef.startswith(kode):
                                file_path = str(output_folder / ef)
                                break

                    checklist.append({
                        'fase': f,
                        'fase_nama': fase_config.get('nama', f'Fase {f}'),
                        'kode': kode,
                        'nama': dok.get('nama', kode),
                        'kategori': kategori,
                        'deskripsi': dok.get('deskripsi', ''),
                        'template': dok.get('template'),
                        'is_uploaded': is_uploaded,
                        'file_path': file_path,
                        'is_required': kategori == 'wajib',
                    })

        return checklist

    def get_missing_documents(self, transaksi: Dict[str, Any], fase: int = None) -> List[Dict[str, Any]]:
        """Get list of required documents that haven't been uploaded."""
        checklist = self.get_document_checklist(transaksi, fase)
        return [doc for doc in checklist if doc['is_required'] and not doc['is_uploaded']]

    def get_completion_status(self, transaksi: Dict[str, Any], fase: int = None) -> Dict[str, Any]:
        """
        Get document completion status.

        Returns:
            Dict with total, uploaded, required, missing counts and percentage
        """
        checklist = self.get_document_checklist(transaksi, fase)

        total = len(checklist)
        uploaded = sum(1 for d in checklist if d['is_uploaded'])
        required = sum(1 for d in checklist if d['is_required'])
        missing = sum(1 for d in checklist if d['is_required'] and not d['is_uploaded'])

        return {
            'total': total,
            'uploaded': uploaded,
            'required': required,
            'missing': missing,
            'percentage': (uploaded / total * 100) if total > 0 else 0,
            'is_complete': missing == 0,
        }

    def generate_rekap_pdf(self, transaksi: Dict[str, Any],
                          output_filename: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a single PDF that combines all documents for a transaction.

        Args:
            transaksi: Data transaksi
            output_filename: Custom output filename (optional)

        Returns:
            Tuple of (output_path, error_message)
        """
        try:
            from pypdf import PdfWriter, PdfReader
            from PIL import Image
            import io
        except ImportError:
            return None, "Library pypdf atau PIL tidak tersedia. Install dengan: pip install pypdf pillow"

        output_folder = self.get_output_folder(transaksi=transaksi)
        if not output_folder.exists():
            return None, "Folder transaksi tidak ditemukan"

        # Get all files sorted by name
        all_files = sorted([f for f in output_folder.iterdir() if f.is_file()])
        if not all_files:
            return None, "Tidak ada dokumen untuk direkap"

        # Create PDF writer
        pdf_writer = PdfWriter()

        # Process each file
        for file_path in all_files:
            ext = file_path.suffix.lower()

            try:
                if ext == '.pdf':
                    # Add PDF directly
                    pdf_reader = PdfReader(str(file_path))
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                elif ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    # Convert image to PDF page
                    img = Image.open(str(file_path))
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')

                    # Create PDF from image
                    img_pdf = io.BytesIO()
                    img.save(img_pdf, format='PDF')
                    img_pdf.seek(0)

                    pdf_reader = PdfReader(img_pdf)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                elif ext == '.docx':
                    # Convert Word to PDF (requires additional libraries)
                    # For now, skip Word files or use a fallback
                    print(f"Skipping Word file: {file_path.name}")

                elif ext == '.xlsx':
                    # Skip Excel files for now
                    print(f"Skipping Excel file: {file_path.name}")

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")
                continue

        if len(pdf_writer.pages) == 0:
            return None, "Tidak ada dokumen PDF atau gambar yang berhasil diproses"

        # Generate output filename
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            kode = transaksi.get('kode', 'REKAP')
            output_filename = f"REKAP_TRANSAKSI_{kode}_{timestamp}.pdf"

        output_path = output_folder / output_filename

        # Save combined PDF
        with open(str(output_path), 'wb') as f:
            pdf_writer.write(f)

        return str(output_path), None

    def get_document_summary_html(self, transaksi: Dict[str, Any]) -> str:
        """
        Generate HTML summary of document checklist for display.

        Returns:
            HTML string with document checklist
        """
        checklist = self.get_document_checklist(transaksi)
        status = self.get_completion_status(transaksi)

        html = f"""
        <div style="font-family: sans-serif; padding: 10px;">
            <h3>Status Kelengkapan Dokumen</h3>
            <p>Progress: {status['uploaded']} / {status['total']} ({status['percentage']:.0f}%)</p>

            <div style="background: #f0f0f0; border-radius: 5px; height: 20px; margin: 10px 0;">
                <div style="background: {'#27ae60' if status['is_complete'] else '#3498db'};
                            width: {status['percentage']}%; height: 100%; border-radius: 5px;"></div>
            </div>
        """

        if status['missing'] > 0:
            html += f"""
            <div style="background: #fadbd8; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <b>Peringatan:</b> {status['missing']} dokumen wajib belum diupload!
            </div>
            """

        # Group by fase
        current_fase = None
        for doc in checklist:
            if doc['fase'] != current_fase:
                if current_fase is not None:
                    html += "</ul>"
                current_fase = doc['fase']
                html += f"<h4>{doc['fase_nama']}</h4><ul>"

            status_icon = '✅' if doc['is_uploaded'] else ('❌' if doc['is_required'] else '⬜')
            required_badge = '<span style="color: red; font-size: 10px;">[WAJIB]</span>' if doc['is_required'] else ''

            html += f"""
            <li style="margin: 5px 0;">
                {status_icon} {doc['nama']} {required_badge}
            </li>
            """

        html += "</ul></div>"
        return html


# Singleton instance
_generator_instance = None

def get_dokumen_generator(db=None) -> DokumenGenerator:
    """Get singleton instance of DokumenGenerator."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = DokumenGenerator(db)
    return _generator_instance
