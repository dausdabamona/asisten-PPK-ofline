#!/usr/bin/env python3
"""
PPK DOCUMENT FACTORY v4.0 - Build EXE Script (Workflow Edition)
================================================================
Script untuk membuat file executable (.exe)

Versi ini menggunakan UI workflow-based untuk pencairan dana (UP/TUP/LS)

Cara penggunaan:
    python build_exe.py

Prasyarat:
    1. Install PyInstaller: pip install pyinstaller
    2. Install semua dependensi: pip install -r requirements.txt
"""

import os
import sys
import shutil
import subprocess

# Direktori aplikasi
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(APP_DIR, 'dist')
BUILD_DIR = os.path.join(APP_DIR, 'build')
SPEC_FILE = os.path.join(APP_DIR, 'ppk_factory.spec')


def check_pyinstaller():
    """Periksa apakah PyInstaller sudah terinstall"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller versi {PyInstaller.__version__} ditemukan")
        return True
    except ImportError:
        print("[ERROR] PyInstaller tidak ditemukan!")
        print("Install dengan: pip install pyinstaller")
        return False


def check_dependencies():
    """Periksa dependensi yang diperlukan"""
    dependencies = [
        ('PySide6', 'PySide6'),
        ('docx', 'python-docx'),
        ('openpyxl', 'openpyxl'),
        ('PIL', 'Pillow'),
    ]

    missing = []
    for module, package in dependencies:
        try:
            __import__(module)
            print(f"[OK] {package} ditemukan")
        except ImportError:
            print(f"[MISSING] {package} tidak ditemukan")
            missing.append(package)

    if missing:
        print(f"\nInstall dependensi yang hilang dengan:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True


def clean_build():
    """Bersihkan folder build sebelumnya"""
    print("\n=== Membersihkan build sebelumnya ===")

    for folder in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(folder):
            print(f"Menghapus {folder}...")
            shutil.rmtree(folder)

    print("[OK] Folder build dibersihkan")


def build_exe():
    """Jalankan PyInstaller untuk build EXE"""
    print("\n=== Memulai build EXE ===")

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        SPEC_FILE
    ]

    print(f"Menjalankan: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=APP_DIR)

    if result.returncode == 0:
        print("\n[SUCCESS] Build EXE berhasil!")
        return True
    else:
        print("\n[ERROR] Build EXE gagal!")
        return False


def copy_additional_files():
    """Salin file tambahan ke folder dist"""
    print("\n=== Menyalin file tambahan ===")

    output_dir = os.path.join(DIST_DIR, 'PPK_Document_Factory')

    if not os.path.exists(output_dir):
        print(f"[ERROR] Folder output tidak ditemukan: {output_dir}")
        return False

    # Buat folder data jika diperlukan (untuk database)
    data_dir = os.path.join(output_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Buat folder output
    output_docs_dir = os.path.join(output_dir, 'output')
    os.makedirs(output_docs_dir, exist_ok=True)

    # Buat folder assets
    assets_dir = os.path.join(output_dir, 'assets')
    signatures_dir = os.path.join(assets_dir, 'signatures')
    os.makedirs(signatures_dir, exist_ok=True)

    print("[OK] Folder tambahan dibuat")
    return True


def create_readme():
    """Buat README untuk distribusi"""
    print("\n=== Membuat README ===")

    output_dir = os.path.join(DIST_DIR, 'PPK_Document_Factory')
    readme_path = os.path.join(output_dir, 'BACA_INI.txt')

    content = """PPK DOCUMENT FACTORY v4.0 - Workflow Edition
===============================================
Workflow-based Pencairan Dana Management System

FITUR UTAMA:
- Workflow pencairan dana berbasis mekanisme (UP, TUP, LS)
- 5 fase per transaksi dengan checklist dokumen
- Tracking saldo UP (maks Rp 50 juta)
- Countdown otomatis untuk TUP (30 hari)
- Kalkulasi tambah/kurang bayar otomatis
- Generate dokumen dari template

CARA PENGGUNAAN:
1. Double-click file PPK_Document_Factory.exe
2. Aplikasi akan terbuka dengan dashboard pencairan dana
3. Pilih mekanisme (UP/TUP/LS) untuk membuat transaksi baru
4. Ikuti 5 fase workflow hingga selesai

STRUKTUR FOLDER:
- data/          : Database aplikasi (otomatis dibuat)
- output/        : Hasil generate dokumen
- templates/     : Template Word dan Excel
  - word/        : Template dokumen Word (.docx)
  - excel/       : Template dokumen Excel (.xlsx)
- assets/        : Aset aplikasi
  - signatures/  : Tanda tangan digital

CATATAN PENTING:
- Pastikan folder templates berisi template dokumen
- Jangan hapus file database di folder data
- Dokumen yang dihasilkan ada di folder output
- Setiap pembayaran memiliki kuitansi uang muka dan rampung

TROUBLESHOOTING:
- Jika aplikasi tidak berjalan, pastikan antivirus tidak memblokir
- Jika error, jalankan dari Command Prompt untuk melihat pesan error
- Untuk UI lama, jalankan: PPK_Document_Factory.exe --legacy

(c) 2024-2026 - PPK Document Factory
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] README dibuat: {readme_path}")
    return True


def main():
    """Main function"""
    print("=" * 60)
    print("PPK DOCUMENT FACTORY v4.0 - BUILD EXE (Workflow Edition)")
    print("=" * 60)

    # Check dependencies
    print("\n=== Memeriksa dependensi ===")
    if not check_pyinstaller():
        return 1

    if not check_dependencies():
        return 1

    # Clean previous build
    clean_build()

    # Build EXE
    if not build_exe():
        return 1

    # Copy additional files
    copy_additional_files()

    # Create README
    create_readme()

    # Final message
    print("\n" + "=" * 60)
    print("BUILD SELESAI!")
    print("=" * 60)
    print(f"\nFile executable ada di:")
    print(f"  {os.path.join(DIST_DIR, 'PPK_Document_Factory')}")
    print("\nUntuk distribusi, zip seluruh folder PPK_Document_Factory")

    return 0


if __name__ == "__main__":
    sys.exit(main())
