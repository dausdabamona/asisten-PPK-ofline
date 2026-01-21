# Asisten PPK Offline

Aplikasi desktop untuk membantu administrasi Pejabat Pembuat Komitmen (PPK) dalam pembuatan dokumen-dokumen yang diperlukan.

## Fitur

### 1. Jamuan Tamu / Rapat
- Generate template **Daftar Hadir** untuk kegiatan jamuan tamu atau rapat
- Input informasi kegiatan (nama, tanggal, waktu, tempat)
- Kustomisasi jumlah peserta
- Otomatis generate dokumen Word (.docx)

### 2. Swakelola
- Generate template **Daftar Hadir** untuk kegiatan swakelola
- Input informasi paket pekerjaan dan kegiatan
- Mendukung tahun anggaran
- Otomatis generate dokumen Word (.docx)

## Instalasi

### Prasyarat
- Python 3.8 atau lebih baru
- pip (Python package installer)

### Langkah Instalasi

1. Clone repository ini:
```bash
git clone https://github.com/dausdabamona/asisten-PPK-ofline.git
cd asisten-PPK-ofline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:
```bash
python run.py
```

## Struktur Proyek

```
asisten-PPK-ofline/
├── src/
│   ├── __init__.py
│   ├── main.py              # GUI aplikasi utama
│   └── document_generator.py # Modul generate dokumen
├── output/                   # Folder output dokumen
├── templates/               # Template dokumen (future)
├── assets/                  # Asset gambar/icon (future)
├── requirements.txt         # Dependencies Python
├── run.py                   # Script untuk menjalankan aplikasi
└── README.md
```

## Penggunaan

1. Jalankan aplikasi dengan `python run.py`
2. Pilih menu yang diinginkan:
   - **Jamuan Tamu / Rapat** - untuk membuat daftar hadir jamuan
   - **Swakelola** - untuk membuat daftar hadir swakelola
3. Isi form yang tersedia
4. Klik "Generate Dokumen"
5. Dokumen akan tersimpan di folder `output/`

## Output Dokumen

Dokumen yang dihasilkan berformat Microsoft Word (.docx) dan dapat langsung dicetak atau diedit lebih lanjut.

## Lisensi

MIT License

## Kontributor

- dausdabamona
