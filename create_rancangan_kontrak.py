"""
Script untuk membuat template Rancangan Kontrak:
1. SPK Barang
2. SPK Jasa Lainnya  
3. SPK Konstruksi
4. Surat Perjanjian Barang
5. Surat Perjanjian Jasa Lainnya
6. Surat Perjanjian Konstruksi

Karakteristik berbeda sesuai jenis pengadaan
"""

import os
from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEMPLATES_DIR = "templates/word"


def add_heading(doc, text, level=1):
    """Add heading with proper formatting"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    if level == 1:
        run.font.size = Pt(12)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        run.font.size = Pt(11)
    return p


def add_pasal(doc, nomor, judul):
    """Add pasal heading"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Pasal {nomor}")
    run.bold = True
    
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run(judul)
    run2.bold = True
    
    return p, p2


def add_ayat(doc, nomor, text):
    """Add numbered paragraph (ayat)"""
    p = doc.add_paragraph()
    p.add_run(f"({nomor}) ").bold = True
    p.add_run(text)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0.75)
    return p


def add_huruf(doc, huruf, text):
    """Add lettered sub-item"""
    p = doc.add_paragraph()
    p.add_run(f"{huruf}. ")
    p.add_run(text)
    p.paragraph_format.left_indent = Cm(1.5)
    return p


# =============================================================================
# SPK BARANG
# =============================================================================
def create_spk_barang():
    """Create SPK template for Pengadaan Barang"""
    doc = Document()
    
    # Set margins
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERINTAH KERJA (SPK)").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PENGADAAN BARANG").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_spk}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Info table
    info = doc.add_paragraph()
    info.add_run("Pada hari ini {{hari_spk}} tanggal {{tanggal_spk_terbilang}} bulan {{bulan_spk}} tahun {{tahun_spk_terbilang}} ({{tanggal_spk_fmt}}), kami yang bertanda tangan di bawah ini:")
    
    doc.add_paragraph()
    
    # PPK Info
    ppk_table = doc.add_table(rows=4, cols=3)
    ppk_data = [
        ("Nama", ":", "{{ppk_nama}}"),
        ("NIP", ":", "{{ppk_nip}}"),
        ("Jabatan", ":", "Pejabat Pembuat Komitmen"),
        ("Alamat", ":", "{{satker_nama}}, {{satker_alamat}}"),
    ]
    for i, (label, sep, val) in enumerate(ppk_data):
        ppk_table.rows[i].cells[0].text = label
        ppk_table.rows[i].cells[1].text = sep
        ppk_table.rows[i].cells[2].text = val
    
    p_ppk = doc.add_paragraph()
    p_ppk.add_run("selanjutnya disebut sebagai ").italic = True
    p_ppk.add_run("PIHAK KESATU").bold = True
    
    doc.add_paragraph()
    
    # Penyedia Info  
    penyedia_table = doc.add_table(rows=5, cols=3)
    penyedia_data = [
        ("Nama Perusahaan", ":", "{{penyedia_nama}}"),
        ("Nama Direktur", ":", "{{direktur_nama}}"),
        ("Alamat", ":", "{{penyedia_alamat}}"),
        ("NPWP", ":", "{{penyedia_npwp}}"),
        ("Rekening", ":", "{{penyedia_rekening}} - {{penyedia_bank}}"),
    ]
    for i, (label, sep, val) in enumerate(penyedia_data):
        penyedia_table.rows[i].cells[0].text = label
        penyedia_table.rows[i].cells[1].text = sep
        penyedia_table.rows[i].cells[2].text = val
    
    p_penyedia = doc.add_paragraph()
    p_penyedia.add_run("selanjutnya disebut sebagai ").italic = True
    p_penyedia.add_run("PIHAK KEDUA").bold = True
    
    doc.add_paragraph()
    
    # Isi SPK
    doc.add_paragraph("PIHAK KESATU dan PIHAK KEDUA secara bersama-sama disebut PARA PIHAK, sepakat dan setuju untuk mengikatkan diri dalam Surat Perintah Kerja Pengadaan Barang dengan ketentuan sebagai berikut:")
    
    doc.add_paragraph()
    
    # Pasal 1 - Lingkup Pekerjaan
    add_pasal(doc, 1, "LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PIHAK KESATU memberikan pekerjaan kepada PIHAK KEDUA dan PIHAK KEDUA menerima pekerjaan tersebut, yaitu:")
    
    lingkup_table = doc.add_table(rows=3, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Lokasi Pekerjaan", "{{lokasi_pekerjaan}}"),
        ("c.", "Kode RUP", "{{kode_rup}}"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    add_ayat(doc, 2, "Rincian barang yang harus disediakan oleh PIHAK KEDUA adalah sebagaimana tercantum dalam Lampiran SPK ini yang merupakan bagian tidak terpisahkan dari SPK.")
    
    doc.add_paragraph()
    
    # Pasal 2 - Nilai Kontrak
    add_pasal(doc, 2, "NILAI KONTRAK")
    add_ayat(doc, 1, "Nilai Kontrak termasuk PPN adalah sebesar:")
    
    nilai_table = doc.add_table(rows=3, cols=2)
    nilai_table.style = 'Table Grid'
    nilai_table.rows[0].cells[0].text = "Nilai Kontrak"
    nilai_table.rows[0].cells[1].text = "{{nilai_kontrak_fmt}}"
    nilai_table.rows[1].cells[0].text = "Terbilang"
    nilai_table.rows[1].cells[1].text = "{{nilai_kontrak_terbilang}}"
    nilai_table.rows[2].cells[0].text = "Sudah Termasuk"
    nilai_table.rows[2].cells[1].text = "PPN 11%, ongkos kirim, biaya pemasangan (jika ada)"
    
    add_ayat(doc, 2, "Nilai kontrak sudah memperhitungkan keuntungan, biaya umum (overhead), dan pajak-pajak yang berlaku.")
    
    doc.add_paragraph()
    
    # Pasal 3 - Jangka Waktu
    add_pasal(doc, 3, "JANGKA WAKTU PELAKSANAAN")
    add_ayat(doc, 1, "Jangka waktu pelaksanaan/penyerahan barang adalah selama {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Tanggal mulai: {{tanggal_mulai_fmt}}")
    add_ayat(doc, 3, "Tanggal selesai: {{tanggal_selesai_fmt}}")
    add_ayat(doc, 4, "PIHAK KEDUA harus menyerahkan seluruh barang dalam kondisi baik dan sesuai spesifikasi paling lambat pada tanggal selesai.")
    
    doc.add_paragraph()
    
    # Pasal 4 - Cara Pembayaran
    add_pasal(doc, 4, "CARA PEMBAYARAN")
    add_ayat(doc, 1, "Pembayaran dilakukan setelah barang diterima dengan lengkap dan sesuai spesifikasi.")
    add_ayat(doc, 2, "Pembayaran dilakukan secara Langsung (LS) ke rekening PIHAK KEDUA setelah:")
    add_huruf(doc, "a", "Barang diterima dan diperiksa oleh Pejabat Penerima Hasil Pekerjaan (PPHP);")
    add_huruf(doc, "b", "Berita Acara Serah Terima (BAST) ditandatangani;")
    add_huruf(doc, "c", "Dokumen tagihan lengkap dan benar.")
    add_ayat(doc, 3, "Pembayaran dipotong pajak sesuai ketentuan perpajakan yang berlaku.")
    
    doc.add_paragraph()
    
    # Pasal 5 - Garansi
    add_pasal(doc, 5, "GARANSI/JAMINAN")
    add_ayat(doc, 1, "PIHAK KEDUA menjamin bahwa barang yang diserahkan adalah baru, asli, dan sesuai spesifikasi teknis.")
    add_ayat(doc, 2, "Masa garansi barang adalah {{masa_garansi}} bulan sejak BAST ditandatangani.")
    add_ayat(doc, 3, "Selama masa garansi, PIHAK KEDUA bertanggung jawab memperbaiki atau mengganti barang yang rusak/cacat tanpa biaya tambahan.")
    
    doc.add_paragraph()
    
    # Pasal 6 - Sanksi/Denda
    add_pasal(doc, 6, "SANKSI DAN DENDA")
    add_ayat(doc, 1, "Apabila PIHAK KEDUA terlambat menyerahkan barang, dikenakan denda keterlambatan sebesar 1/1000 (satu per seribu) dari nilai kontrak untuk setiap hari keterlambatan.")
    add_ayat(doc, 2, "Denda maksimal adalah 5% (lima persen) dari nilai kontrak.")
    add_ayat(doc, 3, "Apabila keterlambatan melebihi 50 (lima puluh) hari kalender, PIHAK KESATU dapat memutuskan kontrak secara sepihak.")
    
    doc.add_paragraph()
    
    # Pasal 7 - Penyelesaian Perselisihan
    add_pasal(doc, 7, "PENYELESAIAN PERSELISIHAN")
    add_ayat(doc, 1, "Apabila terjadi perselisihan, PARA PIHAK sepakat menyelesaikan secara musyawarah untuk mufakat.")
    add_ayat(doc, 2, "Apabila musyawarah tidak tercapai, penyelesaian melalui Pengadilan Negeri {{satker_kota}}.")
    
    doc.add_paragraph()
    
    # Pasal 8 - Lain-lain
    add_pasal(doc, 8, "KETENTUAN LAIN-LAIN")
    add_ayat(doc, 1, "Hal-hal yang belum diatur dalam SPK ini akan ditetapkan kemudian oleh PARA PIHAK.")
    add_ayat(doc, 2, "SPK ini dibuat dalam rangkap 2 (dua), masing-masing mempunyai kekuatan hukum yang sama.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Tanda tangan
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PIHAK KEDUA"
    ttd_table.rows[0].cells[1].text = "PIHAK KESATU"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Bold dan underline nama
    for para in ttd_table.rows[4].cells[0].paragraphs:
        for run in para.runs:
            run.bold = True
            run.underline = True
    for para in ttd_table.rows[4].cells[1].paragraphs:
        for run in para.runs:
            run.bold = True
            run.underline = True
    
    # Save
    filepath = os.path.join(TEMPLATES_DIR, "spk_barang.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# SPK JASA LAINNYA
# =============================================================================
def create_spk_jasa_lainnya():
    """Create SPK template for Jasa Lainnya"""
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERINTAH KERJA (SPK)").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PENGADAAN JASA LAINNYA").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_spk}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Pembukaan
    doc.add_paragraph("Pada hari ini {{hari_spk}} tanggal {{tanggal_spk_terbilang}} bulan {{bulan_spk}} tahun {{tahun_spk_terbilang}} ({{tanggal_spk_fmt}}), kami yang bertanda tangan di bawah ini:")
    
    doc.add_paragraph()
    
    # PPK Info
    ppk_table = doc.add_table(rows=4, cols=3)
    ppk_data = [
        ("Nama", ":", "{{ppk_nama}}"),
        ("NIP", ":", "{{ppk_nip}}"),
        ("Jabatan", ":", "Pejabat Pembuat Komitmen"),
        ("Alamat", ":", "{{satker_nama}}, {{satker_alamat}}"),
    ]
    for i, (label, sep, val) in enumerate(ppk_data):
        ppk_table.rows[i].cells[0].text = label
        ppk_table.rows[i].cells[1].text = sep
        ppk_table.rows[i].cells[2].text = val
    
    doc.add_paragraph("selanjutnya disebut sebagai PIHAK KESATU")
    doc.add_paragraph()
    
    # Penyedia Info
    penyedia_table = doc.add_table(rows=5, cols=3)
    penyedia_data = [
        ("Nama Perusahaan", ":", "{{penyedia_nama}}"),
        ("Nama Direktur", ":", "{{direktur_nama}}"),
        ("Alamat", ":", "{{penyedia_alamat}}"),
        ("NPWP", ":", "{{penyedia_npwp}}"),
        ("Rekening", ":", "{{penyedia_rekening}} - {{penyedia_bank}}"),
    ]
    for i, (label, sep, val) in enumerate(penyedia_data):
        penyedia_table.rows[i].cells[0].text = label
        penyedia_table.rows[i].cells[1].text = sep
        penyedia_table.rows[i].cells[2].text = val
    
    doc.add_paragraph("selanjutnya disebut sebagai PIHAK KEDUA")
    doc.add_paragraph()
    
    doc.add_paragraph("PARA PIHAK sepakat mengikatkan diri dalam SPK Pengadaan Jasa Lainnya dengan ketentuan:")
    doc.add_paragraph()
    
    # Pasal 1 - Lingkup Pekerjaan
    add_pasal(doc, 1, "LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PIHAK KEDUA berkewajiban melaksanakan pekerjaan:")
    
    lingkup_table = doc.add_table(rows=3, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Lokasi Pekerjaan", "{{lokasi_pekerjaan}}"),
        ("c.", "Ruang Lingkup", "Sebagaimana tercantum dalam KAK/Spesifikasi Teknis"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    add_ayat(doc, 2, "Output/deliverable yang harus diserahkan:")
    add_huruf(doc, "a", "Laporan pelaksanaan pekerjaan;")
    add_huruf(doc, "b", "Dokumentasi kegiatan;")
    add_huruf(doc, "c", "Hasil pekerjaan sesuai spesifikasi dalam KAK.")
    
    doc.add_paragraph()
    
    # Pasal 2 - Nilai Kontrak
    add_pasal(doc, 2, "NILAI KONTRAK")
    add_ayat(doc, 1, "Nilai Kontrak adalah sebesar {{nilai_kontrak_fmt}} ({{nilai_kontrak_terbilang}}) termasuk PPN 11%.")
    add_ayat(doc, 2, "Nilai tersebut sudah termasuk seluruh biaya yang diperlukan untuk menyelesaikan pekerjaan.")
    
    doc.add_paragraph()
    
    # Pasal 3 - Jangka Waktu
    add_pasal(doc, 3, "JANGKA WAKTU PELAKSANAAN")
    add_ayat(doc, 1, "Jangka waktu pelaksanaan pekerjaan adalah {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Waktu pelaksanaan:")
    add_huruf(doc, "a", "Tanggal mulai: {{tanggal_mulai_fmt}}")
    add_huruf(doc, "b", "Tanggal selesai: {{tanggal_selesai_fmt}}")
    add_ayat(doc, 3, "PIHAK KEDUA wajib menyerahkan seluruh hasil pekerjaan paling lambat pada tanggal selesai.")
    
    doc.add_paragraph()
    
    # Pasal 4 - Cara Pembayaran (Khusus Jasa - bisa termin)
    add_pasal(doc, 4, "CARA PEMBAYARAN")
    add_ayat(doc, 1, "Pembayaran dilakukan dengan cara:")
    add_huruf(doc, "a", "Pembayaran 100% setelah pekerjaan selesai seluruhnya; ATAU")
    add_huruf(doc, "b", "Pembayaran secara bertahap (termin) sesuai progres pekerjaan.")
    add_ayat(doc, 2, "Pembayaran dilakukan setelah:")
    add_huruf(doc, "a", "Hasil pekerjaan diperiksa dan diterima oleh PPHP;")
    add_huruf(doc, "b", "BAST ditandatangani;")
    add_huruf(doc, "c", "Dokumen tagihan lengkap.")
    
    doc.add_paragraph()
    
    # Pasal 5 - Hak dan Kewajiban
    add_pasal(doc, 5, "HAK DAN KEWAJIBAN")
    add_ayat(doc, 1, "Hak PIHAK KEDUA:")
    add_huruf(doc, "a", "Menerima pembayaran sesuai kontrak;")
    add_huruf(doc, "b", "Memperoleh informasi yang diperlukan untuk pelaksanaan pekerjaan.")
    add_ayat(doc, 2, "Kewajiban PIHAK KEDUA:")
    add_huruf(doc, "a", "Melaksanakan pekerjaan sesuai spesifikasi dan jadwal;")
    add_huruf(doc, "b", "Menyerahkan laporan kemajuan pekerjaan;")
    add_huruf(doc, "c", "Menjaga kerahasiaan informasi yang diperoleh;")
    add_huruf(doc, "d", "Bertanggung jawab atas kualitas hasil pekerjaan.")
    
    doc.add_paragraph()
    
    # Pasal 6 - Sanksi
    add_pasal(doc, 6, "SANKSI DAN DENDA")
    add_ayat(doc, 1, "Keterlambatan penyelesaian pekerjaan dikenakan denda 1/1000 per hari dari nilai kontrak.")
    add_ayat(doc, 2, "Denda maksimal 5% dari nilai kontrak.")
    add_ayat(doc, 3, "Pemutusan kontrak dapat dilakukan jika PIHAK KEDUA tidak mampu menyelesaikan pekerjaan.")
    
    doc.add_paragraph()
    
    # Pasal 7 - Penyelesaian Perselisihan
    add_pasal(doc, 7, "PENYELESAIAN PERSELISIHAN")
    add_ayat(doc, 1, "Perselisihan diselesaikan secara musyawarah.")
    add_ayat(doc, 2, "Jika tidak tercapai, melalui Pengadilan Negeri {{satker_kota}}.")
    
    doc.add_paragraph()
    
    # Pasal 8 - Penutup
    add_pasal(doc, 8, "PENUTUP")
    add_ayat(doc, 1, "SPK ini mulai berlaku sejak tanggal ditandatangani.")
    add_ayat(doc, 2, "Dibuat dalam rangkap 2 (dua) dengan kekuatan hukum yang sama.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TTD
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PIHAK KEDUA"
    ttd_table.rows[0].cells[1].text = "PIHAK KESATU"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    filepath = os.path.join(TEMPLATES_DIR, "spk_jasa_lainnya.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# SPK KONSTRUKSI
# =============================================================================
def create_spk_konstruksi():
    """Create SPK template for Konstruksi"""
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERINTAH KERJA (SPK)").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PEKERJAAN KONSTRUKSI").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_spk}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Pembukaan
    doc.add_paragraph("Pada hari ini {{hari_spk}} tanggal {{tanggal_spk_terbilang}} bulan {{bulan_spk}} tahun {{tahun_spk_terbilang}} ({{tanggal_spk_fmt}}), kami yang bertanda tangan di bawah ini:")
    
    doc.add_paragraph()
    
    # PPK
    ppk_table = doc.add_table(rows=4, cols=3)
    ppk_data = [
        ("Nama", ":", "{{ppk_nama}}"),
        ("NIP", ":", "{{ppk_nip}}"),
        ("Jabatan", ":", "Pejabat Pembuat Komitmen"),
        ("Alamat", ":", "{{satker_nama}}, {{satker_alamat}}"),
    ]
    for i, (label, sep, val) in enumerate(ppk_data):
        ppk_table.rows[i].cells[0].text = label
        ppk_table.rows[i].cells[1].text = sep
        ppk_table.rows[i].cells[2].text = val
    
    doc.add_paragraph("selanjutnya disebut sebagai PIHAK KESATU")
    doc.add_paragraph()
    
    # Penyedia
    penyedia_table = doc.add_table(rows=6, cols=3)
    penyedia_data = [
        ("Nama Perusahaan", ":", "{{penyedia_nama}}"),
        ("Nama Direktur", ":", "{{direktur_nama}}"),
        ("Alamat", ":", "{{penyedia_alamat}}"),
        ("NPWP", ":", "{{penyedia_npwp}}"),
        ("Rekening", ":", "{{penyedia_rekening}} - {{penyedia_bank}}"),
        ("Kualifikasi", ":", "{{kualifikasi_penyedia}}"),
    ]
    for i, (label, sep, val) in enumerate(penyedia_data):
        penyedia_table.rows[i].cells[0].text = label
        penyedia_table.rows[i].cells[1].text = sep
        penyedia_table.rows[i].cells[2].text = val
    
    doc.add_paragraph("selanjutnya disebut sebagai PIHAK KEDUA")
    doc.add_paragraph()
    
    doc.add_paragraph("PARA PIHAK sepakat mengikatkan diri dalam SPK Pekerjaan Konstruksi dengan ketentuan:")
    doc.add_paragraph()
    
    # Pasal 1 - Lingkup Pekerjaan
    add_pasal(doc, 1, "LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PIHAK KEDUA berkewajiban melaksanakan pekerjaan:")
    
    lingkup_table = doc.add_table(rows=4, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Lokasi Pekerjaan", "{{lokasi_pekerjaan}}"),
        ("c.", "Jenis Pekerjaan", "{{jenis_pekerjaan_konstruksi}}"),
        ("d.", "Volume Pekerjaan", "Sesuai Bill of Quantity (BOQ) terlampir"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    add_ayat(doc, 2, "Lingkup pekerjaan meliputi penyediaan tenaga kerja, bahan/material, peralatan, dan metode pelaksanaan sesuai spesifikasi teknis.")
    
    doc.add_paragraph()
    
    # Pasal 2 - Nilai Kontrak
    add_pasal(doc, 2, "NILAI KONTRAK")
    add_ayat(doc, 1, "Nilai Kontrak adalah sebesar {{nilai_kontrak_fmt}} ({{nilai_kontrak_terbilang}}) termasuk PPN 11%.")
    add_ayat(doc, 2, "Jenis kontrak adalah {{jenis_kontrak_konstruksi}}:")
    add_huruf(doc, "a", "Lump Sum: harga tetap tidak berubah; ATAU")
    add_huruf(doc, "b", "Unit Price: berdasarkan harga satuan dan volume terpasang.")
    
    doc.add_paragraph()
    
    # Pasal 3 - Jangka Waktu
    add_pasal(doc, 3, "JANGKA WAKTU PELAKSANAAN")
    add_ayat(doc, 1, "Jangka waktu pelaksanaan adalah {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Waktu pelaksanaan:")
    add_huruf(doc, "a", "Tanggal mulai kerja: {{tanggal_mulai_fmt}}")
    add_huruf(doc, "b", "Tanggal selesai: {{tanggal_selesai_fmt}}")
    add_ayat(doc, 3, "PIHAK KEDUA wajib membuat jadwal pelaksanaan (time schedule) dan kurva S.")
    add_ayat(doc, 4, "Keterlambatan yang bukan kesalahan PIHAK KEDUA dapat diberikan perpanjangan waktu (addendum).")
    
    doc.add_paragraph()
    
    # Pasal 4 - Cara Pembayaran (Konstruksi - Termin & Retensi)
    add_pasal(doc, 4, "CARA PEMBAYARAN")
    add_ayat(doc, 1, "Pembayaran dilakukan secara bertahap (termin) berdasarkan progres fisik pekerjaan:")
    add_huruf(doc, "a", "Termin I: ... % setelah progres fisik mencapai ... %")
    add_huruf(doc, "b", "Termin II: ... % setelah progres fisik mencapai ... %")
    add_huruf(doc, "c", "Termin terakhir: setelah pekerjaan selesai 100%")
    add_ayat(doc, 2, "Setiap pembayaran dipotong retensi sebesar 5% (lima persen) sebagai jaminan pemeliharaan.")
    add_ayat(doc, 3, "Retensi dikembalikan setelah masa pemeliharaan berakhir dan tidak ada cacat/kerusakan.")
    add_ayat(doc, 4, "Pembayaran setelah:")
    add_huruf(doc, "a", "Progres pekerjaan diverifikasi oleh Pengawas/Konsultan Pengawas;")
    add_huruf(doc, "b", "Berita Acara Kemajuan Pekerjaan ditandatangani;")
    add_huruf(doc, "c", "Dokumen tagihan lengkap.")
    
    doc.add_paragraph()
    
    # Pasal 5 - Masa Pemeliharaan (Khusus Konstruksi)
    add_pasal(doc, 5, "MASA PEMELIHARAAN")
    add_ayat(doc, 1, "Masa pemeliharaan adalah {{masa_pemeliharaan}} ({{masa_pemeliharaan_terbilang}}) bulan sejak Serah Terima Pertama (PHO).")
    add_ayat(doc, 2, "Selama masa pemeliharaan, PIHAK KEDUA wajib:")
    add_huruf(doc, "a", "Memperbaiki kerusakan yang terjadi bukan karena kesalahan PIHAK KESATU;")
    add_huruf(doc, "b", "Menanggung biaya perbaikan tersebut.")
    add_ayat(doc, 3, "Setelah masa pemeliharaan berakhir, dilakukan Serah Terima Akhir (FHO).")
    
    doc.add_paragraph()
    
    # Pasal 6 - Tenaga Kerja dan K3
    add_pasal(doc, 6, "TENAGA KERJA DAN K3")
    add_ayat(doc, 1, "PIHAK KEDUA wajib mempekerjakan tenaga kerja yang kompeten dan bersertifikat sesuai kebutuhan.")
    add_ayat(doc, 2, "PIHAK KEDUA wajib menerapkan Sistem Manajemen Keselamatan dan Kesehatan Kerja (SMK3).")
    add_ayat(doc, 3, "PIHAK KEDUA bertanggung jawab atas keselamatan seluruh pekerja di lokasi proyek.")
    add_ayat(doc, 4, "Pelanggaran K3 yang menyebabkan kecelakaan kerja menjadi tanggung jawab PIHAK KEDUA.")
    
    doc.add_paragraph()
    
    # Pasal 7 - Sanksi
    add_pasal(doc, 7, "SANKSI DAN DENDA")
    add_ayat(doc, 1, "Keterlambatan dikenakan denda 1/1000 per hari dari nilai kontrak.")
    add_ayat(doc, 2, "Denda maksimal 5% dari nilai kontrak.")
    add_ayat(doc, 3, "Kegagalan bangunan dalam masa pemeliharaan menjadi tanggung jawab PIHAK KEDUA.")
    add_ayat(doc, 4, "Pemutusan kontrak dapat dilakukan jika pekerjaan tidak dapat diselesaikan.")
    
    doc.add_paragraph()
    
    # Pasal 8 - Penyelesaian Perselisihan
    add_pasal(doc, 8, "PENYELESAIAN PERSELISIHAN")
    add_ayat(doc, 1, "Perselisihan diselesaikan secara musyawarah.")
    add_ayat(doc, 2, "Jika tidak tercapai, melalui Badan Arbitrase atau Pengadilan Negeri {{satker_kota}}.")
    
    doc.add_paragraph()
    
    # Pasal 9 - Penutup
    add_pasal(doc, 9, "PENUTUP")
    add_ayat(doc, 1, "SPK ini berlaku sejak tanggal ditandatangani sampai dengan berakhirnya masa pemeliharaan.")
    add_ayat(doc, 2, "Dibuat dalam rangkap 2 (dua) dengan kekuatan hukum yang sama.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TTD
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PIHAK KEDUA"
    ttd_table.rows[0].cells[1].text = "PIHAK KESATU"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    filepath = os.path.join(TEMPLATES_DIR, "spk_konstruksi.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# SURAT PERJANJIAN BARANG (untuk nilai > 200 juta)
# =============================================================================
def create_surat_perjanjian_barang():
    """Create Surat Perjanjian template for Pengadaan Barang (nilai besar)"""
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERJANJIAN").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PENGADAAN BARANG").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_kontrak}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Pembukaan
    p1 = doc.add_paragraph()
    p1.add_run("Surat Perjanjian ini berikut semua lampirannya (selanjutnya disebut \"Kontrak\") dibuat dan ditandatangani di {{satker_kota}} pada hari {{hari_kontrak}} tanggal {{tanggal_kontrak_terbilang}} bulan {{bulan_kontrak}} tahun {{tahun_kontrak_terbilang}} ({{tanggal_kontrak_fmt}}), antara:")
    
    doc.add_paragraph()
    
    # PPK
    doc.add_paragraph("I. {{ppk_nama}}, {{ppk_jabatan}} {{satker_nama}}, yang bertindak untuk dan atas nama {{satker_nama}}, berkedudukan di {{satker_alamat}}, berdasarkan Surat Keputusan {{sk_ppk}}, selanjutnya disebut \"PIHAK KESATU\".")
    
    doc.add_paragraph()
    
    # Penyedia
    doc.add_paragraph("II. {{direktur_nama}}, Direktur {{penyedia_nama}}, yang bertindak untuk dan atas nama {{penyedia_nama}}, berkedudukan di {{penyedia_alamat}}, NPWP {{penyedia_npwp}}, selanjutnya disebut \"PIHAK KEDUA\".")
    
    doc.add_paragraph()
    
    # Mengingat
    doc.add_paragraph("MENGINGAT BAHWA:")
    
    mengingat = [
        "PIHAK KESATU telah meminta PIHAK KEDUA untuk menyediakan barang sebagaimana diterangkan dalam Kontrak ini;",
        "PIHAK KEDUA sebagaimana dinyatakan kepada PIHAK KESATU, memiliki keahlian profesional, personil, dan sumber daya teknis, serta telah menyetujui untuk menyediakan barang sesuai dengan persyaratan dan ketentuan dalam Kontrak ini;",
        "PIHAK KESATU dan PIHAK KEDUA menyatakan memiliki kewenangan untuk menandatangani Kontrak ini, dan mengikat pihak yang diwakili;",
        "PIHAK KESATU dan PIHAK KEDUA mengakui dan menyatakan bahwa sehubungan dengan penandatanganan Kontrak ini masing-masing pihak telah membaca dan memahami isi Kontrak, dan sepakat untuk terikat dengan ketentuan dalam Kontrak.",
    ]
    
    for i, m in enumerate(mengingat, 1):
        p = doc.add_paragraph()
        p.add_run(f"({i}) ")
        p.add_run(m)
        p.paragraph_format.left_indent = Cm(0.5)
    
    doc.add_paragraph()
    
    doc.add_paragraph("MAKA OLEH KARENA ITU, PIHAK KESATU dan PIHAK KEDUA (selanjutnya disebut \"PARA PIHAK\") dengan ini bersepakat dan menyetujui hal-hal sebagai berikut:")
    
    doc.add_paragraph()
    
    # Pasal 1 - Istilah dan Ungkapan
    add_pasal(doc, 1, "ISTILAH DAN UNGKAPAN")
    doc.add_paragraph("Istilah dan ungkapan dalam Kontrak ini memiliki arti dan makna yang sama seperti yang tercantum dalam Syarat-Syarat Umum Kontrak (SSUK).")
    
    doc.add_paragraph()
    
    # Pasal 2 - Ruang Lingkup
    add_pasal(doc, 2, "RUANG LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PIHAK KEDUA menyediakan barang kepada PIHAK KESATU sesuai dengan ketentuan Kontrak.")
    add_ayat(doc, 2, "Uraian pekerjaan yang harus dilaksanakan:")
    
    lingkup_table = doc.add_table(rows=4, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Kode RUP", "{{kode_rup}}"),
        ("c.", "Lokasi Pengiriman", "{{lokasi_pekerjaan}}"),
        ("d.", "Rincian Barang", "Sebagaimana tercantum dalam Lampiran"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    doc.add_paragraph()
    
    # Pasal 3 - Nilai Kontrak
    add_pasal(doc, 3, "HARGA KONTRAK")
    add_ayat(doc, 1, "PIHAK KESATU membayar kepada PIHAK KEDUA atas pelaksanaan pekerjaan berdasarkan Kontrak sebesar {{nilai_kontrak_fmt}} ({{nilai_kontrak_terbilang}}).")
    add_ayat(doc, 2, "Harga Kontrak telah memperhitungkan keuntungan dan biaya overhead serta pajak.")
    add_ayat(doc, 3, "Rincian Harga Kontrak tercantum dalam Lampiran.")
    
    doc.add_paragraph()
    
    # Pasal 4 - Jangka Waktu
    add_pasal(doc, 4, "JANGKA WAKTU PELAKSANAAN")
    add_ayat(doc, 1, "PIHAK KEDUA wajib menyelesaikan pengiriman barang dalam jangka waktu {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Kontrak ini berlaku efektif sejak {{tanggal_mulai_fmt}} sampai dengan {{tanggal_selesai_fmt}}.")
    add_ayat(doc, 3, "Apabila PIHAK KEDUA tidak dapat menyelesaikan pekerjaan sesuai jadwal, maka PIHAK KEDUA dikenakan sanksi sesuai ketentuan SSUK.")
    
    doc.add_paragraph()
    
    # Pasal 5 - Dokumen Kontrak
    add_pasal(doc, 5, "DOKUMEN KONTRAK")
    add_ayat(doc, 1, "Dokumen-dokumen berikut merupakan satu kesatuan dan bagian yang tidak terpisahkan dari Kontrak ini:")
    add_huruf(doc, "a", "Surat Perjanjian;")
    add_huruf(doc, "b", "Surat Penawaran beserta lampirannya;")
    add_huruf(doc, "c", "Syarat-Syarat Umum Kontrak (SSUK);")
    add_huruf(doc, "d", "Syarat-Syarat Khusus Kontrak (SSKK);")
    add_huruf(doc, "e", "Spesifikasi Teknis;")
    add_huruf(doc, "f", "Gambar/Brosur (jika ada);")
    add_huruf(doc, "g", "Daftar Kuantitas dan Harga;")
    add_huruf(doc, "h", "Dokumen lain yang menjadi bagian dari Kontrak.")
    add_ayat(doc, 2, "Jika terdapat pertentangan, urutan pemberlakuan mengikuti urutan dokumen di atas.")
    
    doc.add_paragraph()
    
    # Pasal 6 - Jaminan
    add_pasal(doc, 6, "JAMINAN")
    add_ayat(doc, 1, "PIHAK KEDUA menyerahkan Jaminan Pelaksanaan sebesar {{nilai_jaminan_pelaksanaan_fmt}} ({{persen_jaminan_pelaksanaan}}% dari nilai kontrak).")
    add_ayat(doc, 2, "Jaminan Pelaksanaan dikembalikan setelah pekerjaan selesai dan BAST ditandatangani.")
    add_ayat(doc, 3, "Masa berlaku jaminan sesuai dengan masa kontrak ditambah {{masa_klaim_jaminan}} hari.")
    
    doc.add_paragraph()
    
    # Pasal 7 - Korespondensi
    add_pasal(doc, 7, "KORESPONDENSI")
    doc.add_paragraph("Semua pemberitahuan, permohonan, persetujuan dan korespondensi disampaikan secara tertulis kepada:")
    
    korespondensi = doc.add_table(rows=4, cols=2)
    korespondensi.style = 'Table Grid'
    korespondensi.rows[0].cells[0].text = "PIHAK KESATU"
    korespondensi.rows[0].cells[1].text = "PIHAK KEDUA"
    korespondensi.rows[1].cells[0].text = "{{ppk_nama}}"
    korespondensi.rows[1].cells[1].text = "{{direktur_nama}}"
    korespondensi.rows[2].cells[0].text = "{{satker_alamat}}"
    korespondensi.rows[2].cells[1].text = "{{penyedia_alamat}}"
    korespondensi.rows[3].cells[0].text = "Telp: {{satker_telepon}}"
    korespondensi.rows[3].cells[1].text = "Telp: {{penyedia_telepon}}"
    
    doc.add_paragraph()
    
    # Pasal 8 - Penutup
    add_pasal(doc, 8, "PENUTUP")
    doc.add_paragraph("Kontrak ini mulai berlaku efektif terhitung sejak tanggal yang ditetapkan. Kontrak ditandatangani oleh PARA PIHAK.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TTD
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PIHAK KEDUA"
    ttd_table.rows[0].cells[1].text = "PIHAK KESATU"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    filepath = os.path.join(TEMPLATES_DIR, "surat_perjanjian_barang.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# SURAT PERJANJIAN JASA LAINNYA
# =============================================================================
def create_surat_perjanjian_jasa():
    """Create Surat Perjanjian template for Jasa Lainnya"""
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERJANJIAN").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PENGADAAN JASA LAINNYA").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_kontrak}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Pembukaan
    doc.add_paragraph("Surat Perjanjian ini berikut semua lampirannya (selanjutnya disebut \"Kontrak\") dibuat dan ditandatangani di {{satker_kota}} pada hari {{hari_kontrak}} tanggal {{tanggal_kontrak_fmt}}, antara:")
    
    doc.add_paragraph()
    
    doc.add_paragraph("I. {{ppk_nama}}, {{ppk_jabatan}} {{satker_nama}}, berkedudukan di {{satker_alamat}}, selanjutnya disebut \"PIHAK KESATU\".")
    doc.add_paragraph()
    doc.add_paragraph("II. {{direktur_nama}}, Direktur {{penyedia_nama}}, berkedudukan di {{penyedia_alamat}}, NPWP {{penyedia_npwp}}, selanjutnya disebut \"PIHAK KEDUA\".")
    
    doc.add_paragraph()
    doc.add_paragraph("PARA PIHAK sepakat dan menyetujui hal-hal sebagai berikut:")
    doc.add_paragraph()
    
    # Pasal 1
    add_pasal(doc, 1, "RUANG LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PIHAK KEDUA berkewajiban melaksanakan pekerjaan jasa:")
    
    lingkup_table = doc.add_table(rows=3, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Ruang Lingkup", "Sesuai KAK/Spesifikasi Teknis"),
        ("c.", "Output/Deliverable", "Sesuai KAK terlampir"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    add_ayat(doc, 2, "Rincian ruang lingkup, metodologi, dan jadwal pelaksanaan tercantum dalam KAK yang merupakan bagian tidak terpisahkan dari Kontrak.")
    
    doc.add_paragraph()
    
    # Pasal 2
    add_pasal(doc, 2, "HARGA KONTRAK DAN CARA PEMBAYARAN")
    add_ayat(doc, 1, "Harga Kontrak adalah {{nilai_kontrak_fmt}} ({{nilai_kontrak_terbilang}}) termasuk pajak.")
    add_ayat(doc, 2, "Pembayaran dilakukan secara:")
    add_huruf(doc, "a", "Sekaligus 100% setelah pekerjaan selesai; ATAU")
    add_huruf(doc, "b", "Bertahap sesuai progres/milestone yang disepakati")
    add_ayat(doc, 3, "Pembayaran dipotong pajak sesuai ketentuan yang berlaku.")
    
    doc.add_paragraph()
    
    # Pasal 3
    add_pasal(doc, 3, "JANGKA WAKTU")
    add_ayat(doc, 1, "Jangka waktu pelaksanaan adalah {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Tanggal mulai: {{tanggal_mulai_fmt}}")
    add_ayat(doc, 3, "Tanggal selesai: {{tanggal_selesai_fmt}}")
    
    doc.add_paragraph()
    
    # Pasal 4
    add_pasal(doc, 4, "HAK KEKAYAAN INTELEKTUAL")
    add_ayat(doc, 1, "Seluruh hasil pekerjaan menjadi milik PIHAK KESATU.")
    add_ayat(doc, 2, "PIHAK KEDUA tidak berhak menggunakan hasil pekerjaan untuk kepentingan pihak lain tanpa persetujuan tertulis.")
    add_ayat(doc, 3, "PIHAK KEDUA menjamin hasil pekerjaan tidak melanggar hak kekayaan intelektual pihak ketiga.")
    
    doc.add_paragraph()
    
    # Pasal 5
    add_pasal(doc, 5, "KERAHASIAAN")
    add_ayat(doc, 1, "PIHAK KEDUA wajib menjaga kerahasiaan seluruh informasi yang diperoleh dalam pelaksanaan pekerjaan.")
    add_ayat(doc, 2, "Kewajiban kerahasiaan tetap berlaku meskipun Kontrak telah berakhir.")
    
    doc.add_paragraph()
    
    # Pasal 6
    add_pasal(doc, 6, "DOKUMEN KONTRAK")
    add_ayat(doc, 1, "Dokumen Kontrak terdiri dari:")
    add_huruf(doc, "a", "Surat Perjanjian;")
    add_huruf(doc, "b", "SSUK dan SSKK;")
    add_huruf(doc, "c", "Kerangka Acuan Kerja (KAK);")
    add_huruf(doc, "d", "Surat Penawaran;")
    add_huruf(doc, "e", "Daftar Harga;")
    add_huruf(doc, "f", "Dokumen lain yang relevan.")
    
    doc.add_paragraph()
    
    # Pasal 7
    add_pasal(doc, 7, "SANKSI DAN DENDA")
    add_ayat(doc, 1, "Keterlambatan dikenakan denda 1/1000 per hari dari nilai kontrak, maksimal 5%.")
    add_ayat(doc, 2, "Hasil pekerjaan yang tidak sesuai spesifikasi wajib diperbaiki tanpa biaya tambahan.")
    
    doc.add_paragraph()
    
    # Pasal 8
    add_pasal(doc, 8, "PENYELESAIAN PERSELISIHAN")
    add_ayat(doc, 1, "Perselisihan diselesaikan secara musyawarah.")
    add_ayat(doc, 2, "Jika tidak tercapai, melalui Pengadilan Negeri {{satker_kota}}.")
    
    doc.add_paragraph()
    
    # Pasal 9
    add_pasal(doc, 9, "PENUTUP")
    doc.add_paragraph("Kontrak ini ditandatangani oleh PARA PIHAK pada tanggal tersebut di atas dalam rangkap 2 (dua) yang masing-masing mempunyai kekuatan hukum yang sama.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TTD
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PIHAK KEDUA"
    ttd_table.rows[0].cells[1].text = "PIHAK KESATU"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    filepath = os.path.join(TEMPLATES_DIR, "surat_perjanjian_jasa_lainnya.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# SURAT PERJANJIAN KONSTRUKSI
# =============================================================================
def create_surat_perjanjian_konstruksi():
    """Create Surat Perjanjian template for Konstruksi"""
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2)
    
    # Header
    title = doc.add_paragraph()
    title.add_run("SURAT PERJANJIAN").bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle.add_run("PEKERJAAN KONSTRUKSI").bold = True
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    nomor = doc.add_paragraph()
    nomor.add_run("Nomor: {{nomor_kontrak}}")
    nomor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()
    
    # Pembukaan
    doc.add_paragraph("Surat Perjanjian untuk melaksanakan Pekerjaan Konstruksi ini berikut semua lampirannya (selanjutnya disebut \"Kontrak\") dibuat dan ditandatangani di {{satker_kota}} pada hari {{hari_kontrak}} tanggal {{tanggal_kontrak_fmt}}, antara:")
    
    doc.add_paragraph()
    doc.add_paragraph("I. {{ppk_nama}}, {{ppk_jabatan}} {{satker_nama}}, berkedudukan di {{satker_alamat}}, selanjutnya disebut \"PENGGUNA JASA\".")
    doc.add_paragraph()
    doc.add_paragraph("II. {{direktur_nama}}, Direktur {{penyedia_nama}}, berkedudukan di {{penyedia_alamat}}, NPWP {{penyedia_npwp}}, Kualifikasi {{kualifikasi_penyedia}}, selanjutnya disebut \"PENYEDIA JASA\".")
    
    doc.add_paragraph()
    doc.add_paragraph("PARA PIHAK sepakat dan menyetujui hal-hal sebagai berikut:")
    doc.add_paragraph()
    
    # Pasal 1
    add_pasal(doc, 1, "LINGKUP PEKERJAAN")
    add_ayat(doc, 1, "PENYEDIA JASA berkewajiban melaksanakan pekerjaan konstruksi:")
    
    lingkup_table = doc.add_table(rows=5, cols=3)
    lingkup_table.style = 'Table Grid'
    lingkup_data = [
        ("a.", "Nama Paket", "{{nama_paket}}"),
        ("b.", "Lokasi Pekerjaan", "{{lokasi_pekerjaan}}"),
        ("c.", "Jenis Pekerjaan", "{{jenis_pekerjaan_konstruksi}}"),
        ("d.", "Klasifikasi", "{{klasifikasi_konstruksi}}"),
        ("e.", "Volume", "Sesuai BOQ terlampir"),
    ]
    for i, (no, label, val) in enumerate(lingkup_data):
        lingkup_table.rows[i].cells[0].text = no
        lingkup_table.rows[i].cells[1].text = label
        lingkup_table.rows[i].cells[2].text = val
    
    add_ayat(doc, 2, "Pekerjaan meliputi penyediaan tenaga kerja, bahan, peralatan, dan semua yang diperlukan.")
    add_ayat(doc, 3, "Gambar teknis, spesifikasi, dan BOQ tercantum dalam Lampiran.")
    
    doc.add_paragraph()
    
    # Pasal 2
    add_pasal(doc, 2, "HARGA KONTRAK")
    add_ayat(doc, 1, "Harga Kontrak adalah {{nilai_kontrak_fmt}} ({{nilai_kontrak_terbilang}}) termasuk PPN.")
    add_ayat(doc, 2, "Jenis Kontrak: {{jenis_kontrak_konstruksi}}")
    add_huruf(doc, "a", "Lump Sum: Harga tetap dan pasti;")
    add_huruf(doc, "b", "Unit Price: Berdasarkan harga satuan dan volume terpasang;")
    add_huruf(doc, "c", "Gabungan Lump Sum dan Unit Price.")
    add_ayat(doc, 3, "Harga sudah memperhitungkan keuntungan, overhead, dan risiko.")
    
    doc.add_paragraph()
    
    # Pasal 3
    add_pasal(doc, 3, "JANGKA WAKTU PELAKSANAAN")
    add_ayat(doc, 1, "Jangka waktu pelaksanaan: {{jangka_waktu}} ({{jangka_waktu_terbilang}}) hari kalender.")
    add_ayat(doc, 2, "Tanggal mulai kerja: {{tanggal_mulai_fmt}}")
    add_ayat(doc, 3, "Tanggal Serah Terima I (PHO): {{tanggal_selesai_fmt}}")
    add_ayat(doc, 4, "Masa Pemeliharaan: {{masa_pemeliharaan}} bulan")
    add_ayat(doc, 5, "PENYEDIA JASA wajib membuat time schedule dan kurva S.")
    
    doc.add_paragraph()
    
    # Pasal 4
    add_pasal(doc, 4, "CARA PEMBAYARAN")
    add_ayat(doc, 1, "Pembayaran dilakukan secara termin berdasarkan progres fisik:")
    
    termin_table = doc.add_table(rows=5, cols=3)
    termin_table.style = 'Table Grid'
    termin_table.rows[0].cells[0].text = "Termin"
    termin_table.rows[0].cells[1].text = "Progres Fisik"
    termin_table.rows[0].cells[2].text = "Pembayaran"
    termin_table.rows[1].cells[0].text = "I"
    termin_table.rows[1].cells[1].text = "{{progres_termin1}}%"
    termin_table.rows[1].cells[2].text = "{{pembayaran_termin1}}%"
    termin_table.rows[2].cells[0].text = "II"
    termin_table.rows[2].cells[1].text = "{{progres_termin2}}%"
    termin_table.rows[2].cells[2].text = "{{pembayaran_termin2}}%"
    termin_table.rows[3].cells[0].text = "III"
    termin_table.rows[3].cells[1].text = "{{progres_termin3}}%"
    termin_table.rows[3].cells[2].text = "{{pembayaran_termin3}}%"
    termin_table.rows[4].cells[0].text = "IV (Final)"
    termin_table.rows[4].cells[1].text = "100%"
    termin_table.rows[4].cells[2].text = "Sisa"
    
    add_ayat(doc, 2, "Setiap pembayaran dipotong retensi 5% sebagai jaminan pemeliharaan.")
    add_ayat(doc, 3, "Retensi dikembalikan setelah FHO dan tidak ada cacat.")
    
    doc.add_paragraph()
    
    # Pasal 5
    add_pasal(doc, 5, "JAMINAN-JAMINAN")
    add_ayat(doc, 1, "PENYEDIA JASA wajib menyerahkan:")
    add_huruf(doc, "a", "Jaminan Pelaksanaan sebesar {{persen_jaminan_pelaksanaan}}% dari nilai kontrak;")
    add_huruf(doc, "b", "Jaminan Uang Muka (jika ada uang muka) sebesar 100% dari uang muka;")
    add_huruf(doc, "c", "Jaminan Pemeliharaan sebesar 5% dari nilai kontrak atau dapat diganti dengan retensi.")
    add_ayat(doc, 2, "Jaminan dari Bank Umum atau Perusahaan Asuransi yang memiliki izin.")
    
    doc.add_paragraph()
    
    # Pasal 6
    add_pasal(doc, 6, "MASA PEMELIHARAAN")
    add_ayat(doc, 1, "Masa Pemeliharaan adalah {{masa_pemeliharaan}} bulan sejak PHO.")
    add_ayat(doc, 2, "Selama masa pemeliharaan, PENYEDIA JASA wajib:")
    add_huruf(doc, "a", "Memperbaiki kerusakan yang bukan kesalahan PENGGUNA JASA;")
    add_huruf(doc, "b", "Melakukan perawatan rutin sesuai spesifikasi;")
    add_huruf(doc, "c", "Menanggung biaya perbaikan.")
    add_ayat(doc, 3, "Setelah masa pemeliharaan berakhir dan tidak ada cacat, dilakukan FHO.")
    
    doc.add_paragraph()
    
    # Pasal 7
    add_pasal(doc, 7, "TENAGA AHLI DAN PERALATAN")
    add_ayat(doc, 1, "PENYEDIA JASA wajib menyediakan tenaga ahli sesuai yang ditawarkan:")
    add_huruf(doc, "a", "{{tenaga_ahli_1}}")
    add_huruf(doc, "b", "{{tenaga_ahli_2}}")
    add_huruf(doc, "c", "Tenaga teknis lainnya sesuai kebutuhan")
    add_ayat(doc, 2, "Penggantian tenaga ahli harus mendapat persetujuan PENGGUNA JASA.")
    add_ayat(doc, 3, "PENYEDIA JASA wajib menyediakan peralatan yang memadai.")
    
    doc.add_paragraph()
    
    # Pasal 8
    add_pasal(doc, 8, "KESELAMATAN DAN KESEHATAN KERJA (K3)")
    add_ayat(doc, 1, "PENYEDIA JASA wajib menerapkan SMK3 Konstruksi.")
    add_ayat(doc, 2, "PENYEDIA JASA bertanggung jawab penuh atas keselamatan di lokasi proyek.")
    add_ayat(doc, 3, "Kecelakaan kerja menjadi tanggung jawab PENYEDIA JASA.")
    add_ayat(doc, 4, "PENYEDIA JASA wajib mengasuransikan tenaga kerja dan pihak ketiga.")
    
    doc.add_paragraph()
    
    # Pasal 9
    add_pasal(doc, 9, "KEGAGALAN BANGUNAN")
    add_ayat(doc, 1, "PENYEDIA JASA bertanggung jawab atas kegagalan bangunan selama umur konstruksi.")
    add_ayat(doc, 2, "Pertanggungjawaban meliputi:")
    add_huruf(doc, "a", "Perbaikan/penggantian;")
    add_huruf(doc, "b", "Ganti rugi;")
    add_huruf(doc, "c", "Tuntutan pidana sesuai peraturan perundang-undangan.")
    
    doc.add_paragraph()
    
    # Pasal 10
    add_pasal(doc, 10, "SANKSI DAN DENDA")
    add_ayat(doc, 1, "Keterlambatan dikenakan denda 1/1000 per hari, maksimal 5%.")
    add_ayat(doc, 2, "Keterlambatan >50 hari dapat dilakukan pemutusan kontrak.")
    add_ayat(doc, 3, "Pekerjaan tidak sesuai mutu wajib diperbaiki tanpa biaya tambahan.")
    
    doc.add_paragraph()
    
    # Pasal 11
    add_pasal(doc, 11, "PENYELESAIAN PERSELISIHAN")
    add_ayat(doc, 1, "Musyawarah mufakat;")
    add_ayat(doc, 2, "Mediasi/konsiliasi;")
    add_ayat(doc, 3, "Arbitrase melalui BANI; atau")
    add_ayat(doc, 4, "Pengadilan Negeri {{satker_kota}}.")
    
    doc.add_paragraph()
    
    # Pasal 12
    add_pasal(doc, 12, "DOKUMEN KONTRAK")
    add_ayat(doc, 1, "Dokumen Kontrak terdiri dari:")
    add_huruf(doc, "a", "Surat Perjanjian;")
    add_huruf(doc, "b", "SSUK dan SSKK;")
    add_huruf(doc, "c", "Spesifikasi Teknis;")
    add_huruf(doc, "d", "Gambar-gambar;")
    add_huruf(doc, "e", "Bill of Quantity (BOQ);")
    add_huruf(doc, "f", "Surat Penawaran;")
    add_huruf(doc, "g", "Daftar Harga Satuan;")
    add_huruf(doc, "h", "Dokumen lain yang relevan.")
    
    doc.add_paragraph()
    
    # Pasal 13
    add_pasal(doc, 13, "PENUTUP")
    doc.add_paragraph("Kontrak ini ditandatangani PARA PIHAK pada tanggal tersebut di atas, dibuat dalam rangkap 2 (dua) bermaterai cukup yang masing-masing mempunyai kekuatan hukum yang sama.")
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TTD
    ttd_table = doc.add_table(rows=6, cols=2)
    ttd_table.rows[0].cells[0].text = "PENYEDIA JASA"
    ttd_table.rows[0].cells[1].text = "PENGGUNA JASA"
    ttd_table.rows[1].cells[0].text = "{{penyedia_nama}}"
    ttd_table.rows[1].cells[1].text = "Pejabat Pembuat Komitmen"
    ttd_table.rows[4].cells[0].text = "{{direktur_nama}}"
    ttd_table.rows[4].cells[1].text = "{{ppk_nama}}"
    ttd_table.rows[5].cells[0].text = "Direktur"
    ttd_table.rows[5].cells[1].text = "NIP. {{ppk_nip}}"
    
    for row in ttd_table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    filepath = os.path.join(TEMPLATES_DIR, "surat_perjanjian_konstruksi.docx")
    doc.save(filepath)
    print(f"✅ Created: {filepath}")
    return filepath


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    print("=" * 60)
    print("MEMBUAT TEMPLATE RANCANGAN KONTRAK")
    print("=" * 60)
    print()
    
    print("📋 SPK (Surat Perintah Kerja) - untuk nilai s.d. 200 juta:")
    create_spk_barang()
    create_spk_jasa_lainnya()
    create_spk_konstruksi()
    
    print()
    print("📋 Surat Perjanjian - untuk nilai > 200 juta:")
    create_surat_perjanjian_barang()
    create_surat_perjanjian_jasa()
    create_surat_perjanjian_konstruksi()
    
    print()
    print("=" * 60)
    print("SELESAI!")
    print("=" * 60)
    print()
    print("KARAKTERISTIK PERBEDAAN TEMPLATE:")
    print()
    print("BARANG:")
    print("  - Fokus: Spesifikasi, pengiriman, garansi")
    print("  - Pembayaran: Sekaligus setelah barang diterima")
    print("  - Garansi: Jaminan kualitas barang")
    print()
    print("JASA LAINNYA:")
    print("  - Fokus: Ruang lingkup, output/deliverable, timeline")
    print("  - Pembayaran: Sekaligus atau termin sesuai progres")
    print("  - Khusus: Hak kekayaan intelektual, kerahasiaan")
    print()
    print("KONSTRUKSI:")
    print("  - Fokus: Gambar teknis, BOQ, tenaga ahli, K3")
    print("  - Pembayaran: Termin berdasarkan progres fisik")
    print("  - Jaminan: Pelaksanaan, Uang Muka, Pemeliharaan")
    print("  - Khusus: Masa pemeliharaan, PHO/FHO, Retensi 5%")
    print("  - Tanggung jawab: Kegagalan bangunan")
