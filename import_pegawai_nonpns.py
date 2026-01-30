"""
Script untuk import data pegawai Non-PNS/Kontrak dari CSV ke database
"""
import sqlite3
import csv
from pathlib import Path
from datetime import datetime

# Path database
DB_PATH = Path("e:/gdrive/aplikasi/data/ppk_workflow.db")
CSV_PATH = Path("e:/gdrive/0. 2026/suplier/pegawai_nonpns.csv")

def import_pegawai_nonpns():
    """Import data pegawai Non-PNS dari CSV"""
    
    if not CSV_PATH.exists():
        print(f"❌ File CSV tidak ditemukan: {CSV_PATH}")
        print(f"   Harapkan file di: {CSV_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Baca dan import data dari CSV
    imported = 0
    errors = 0
    duplicates = 0
    
    print(f"📂 Membaca file: {CSV_PATH}")
    print(f"{'='*70}")
    
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            try:
                # Extract data dari CSV dengan fallback untuk field kosong
                nama = (row.get('NMPPPNPN') or '').strip()
                nik_ppnpn = (row.get('NIKPPNPN') or '').strip()
                npwp = (row.get('NPWP') or '').strip()
                status = (row.get('STATUS') or '').strip()
                no_rekening = (row.get('NOREK') or '').strip()
                
                # Fields opsional dengan default value
                jabatan = (row.get('JABATAN') or 'Non-PNS').strip() or 'Non-PNS'
                unit_kerja = (row.get('UNIT_KERJA') or 'Umum').strip() or 'Umum'
                nama_bank = (row.get('BANK') or 'BRI').strip() or 'BRI'
                email = (row.get('EMAIL') or '').strip()
                telepon = (row.get('TELEPON') or '').strip()
                
                # Skip jika nama kosong
                if not nama or not nik_ppnpn:
                    print(f"  ⚠️  Baris {idx}: Nama atau ID kosong, skip")
                    continue
                
                # Check apakah sudah ada
                cursor.execute(
                    "SELECT id FROM pegawai WHERE nama = ? AND is_active = 1",
                    (nama,)
                )
                
                if cursor.fetchone():
                    duplicates += 1
                    print(f"  ⚠️  Baris {idx}: {nama} sudah ada, skip")
                    continue
                
                # Insert ke database
                cursor.execute("""
                    INSERT INTO pegawai (
                        nip, nama, jabatan, golongan, pangkat,
                        unit_kerja, email, telepon, npwp,
                        no_rekening, nama_bank, is_ppk, is_ppspm,
                        is_bendahara, is_pemeriksa, is_pejabat_pengadaan,
                        is_active, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nik_ppnpn,           # nip (menggunakan NIKPPNPN sebagai ID)
                    nama,                # nama
                    jabatan,             # jabatan
                    'Non-PNS',           # golongan
                    'Non-PNS',           # pangkat
                    unit_kerja,          # unit_kerja
                    email,               # email
                    telepon,             # telepon
                    npwp,                # npwp
                    no_rekening,         # no_rekening
                    nama_bank,           # nama_bank
                    0,                   # is_ppk (default: tidak)
                    0,                   # is_ppspm (default: tidak)
                    0,                   # is_bendahara (default: tidak)
                    0,                   # is_pemeriksa (default: tidak)
                    0,                   # is_pejabat_pengadaan (default: tidak)
                    1,                   # is_active
                    datetime.now().isoformat()  # created_at
                ))
                
                imported += 1
                
                if imported % 10 == 0:
                    print(f"  ⏳ Progress: {imported} pegawai non-PNS...", end='\r')
                
            except KeyError as e:
                errors += 1
                print(f"\n  ❌ Baris {idx}: Kolom tidak ditemukan - {e}")
                continue
            except Exception as e:
                errors += 1
                print(f"\n  ❌ Baris {idx}: Error - {str(e)[:60]}")
                continue
    
    conn.commit()
    
    # Verifikasi hasil
    cursor.execute("""
        SELECT COUNT(*) FROM pegawai
        WHERE is_active=1 AND golongan='Non-PNS'
    """)
    total_nonpns = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pegawai WHERE is_active=1")
    total_all = cursor.fetchone()[0]
    
    print(f"\n{'='*70}")
    print(f"✅ IMPORT SELESAI")
    print(f"{'='*70}")
    print(f"✓ Berhasil diimpor: {imported} pegawai Non-PNS")
    print(f"⚠️  Duplikat (skip): {duplicates}")
    print(f"❌ Gagal: {errors}")
    print(f"{'='*70}")
    print(f"📊 Statistik Database:")
    print(f"   • Total Pegawai Non-PNS: {total_nonpns}")
    print(f"   • Total Pegawai (semua): {total_all}")
    print(f"{'='*70}\n")
    
    # Tampilkan data yang baru diimpor
    if imported > 0:
        print(f"📋 Data Non-PNS terbaru (sample):")
        cursor.execute("""
            SELECT nama, nip, jabatan, unit_kerja, npwp
            FROM pegawai
            WHERE is_active=1 AND golongan='Non-PNS'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            jabatan_str = row[2] if row[2] else 'Non-PNS'
            unit_str = row[3] if row[3] else 'Umum'
            npwp_str = row[4] if row[4] else '-'
            print(f"  • {row[0]}")
            print(f"    └─ ID: {row[1]} | Jabatan: {jabatan_str} | Unit: {unit_str}")
    
    conn.close()
    
    return imported > 0


if __name__ == "__main__":
    print("\n" + "="*70)
    print("IMPORT DATA PEGAWAI NON-PNS")
    print("="*70 + "\n")
    
    success = import_pegawai_nonpns()
    
    if not success:
        print("⚠️  PERHATIAN:")
        print("   File CSV belum tersedia.")
        print("   Harap siapkan file dengan nama: pegawai_nonpns.csv")
        print("   Lokasi: e:\\gdrive\\0. 2026\\suplier\\")
        print("\n   Format CSV yang dibutuhkan:")
        print("   NMPPPNPN, NIKPPNPN, NPWP, STATUS, NOREK, BANK, JABATAN, UNIT_KERJA")
        print()
