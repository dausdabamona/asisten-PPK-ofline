"""
Script untuk import data pegawai dari CSV ke database
"""
import sqlite3
import csv
from pathlib import Path

# Path database
DB_PATH = Path("e:/gdrive/aplikasi/data/ppk_workflow.db")
CSV_PATH = Path("e:/gdrive/0. 2026/suplier/pegawai_2026-01-14ok.csv")

def import_pegawai():
    """Import data pegawai dari CSV"""
    
    if not CSV_PATH.exists():
        print(f"❌ File CSV tidak ditemukan: {CSV_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Bersihkan data pegawai yang lama
    print("🗑️  Menghapus data pegawai lama...")
    cursor.execute("DELETE FROM pegawai")
    conn.commit()
    
    # Baca dan import data dari CSV
    imported = 0
    errors = 0
    
    print(f"📂 Membaca file: {CSV_PATH}")
    
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:  # utf-8-sig removes BOM
        reader = csv.DictReader(f, delimiter=';')
        
        for idx, row in enumerate(reader, 1):
            try:
                nama = row['nama'].strip()
                nip = row['nip'].strip()
                jabatan = row['jabatan'].strip()
                golongan = row.get('golongan', '').strip()
                pangkat = row.get('pangkat', '').strip()
                rekening = row.get('rekening', '').strip()
                bank = row.get('bank', '').strip()
                unit_kerja = row.get('unitKerja', '').strip()
                
                # Skip jika nama kosong
                if not nama:
                    continue
                
                # Insert ke database dengan kolom yang sesuai
                cursor.execute("""
                    INSERT INTO pegawai (
                        nip, nama, jabatan, golongan, pangkat, 
                        no_rekening, nama_bank, unit_kerja, is_active
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (nip, nama, jabatan, golongan, pangkat, rekening, bank, unit_kerja))
                
                imported += 1
                
                if imported % 20 == 0:
                    print(f"  ⏳ Progress: {imported} pegawai...")
                    
            except Exception as e:
                errors += 1
                print(f"  ⚠️  Baris {idx} error: {e}")
                continue
    
    conn.commit()
    
    # Verifikasi hasil
    cursor.execute("SELECT COUNT(*) FROM pegawai WHERE is_active=1")
    total = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"✅ IMPORT SELESAI")
    print(f"{'='*60}")
    print(f"✓ Berhasil diimpor: {imported} pegawai")
    print(f"✗ Gagal: {errors}")
    print(f"📊 Total pegawai aktif di database: {total}")
    print(f"{'='*60}\n")
    
    # Tampilkan 10 pegawai pertama
    print("📋 Sample data (10 pegawai pertama):")
    cursor.execute("""
        SELECT nama, nip, jabatan 
        FROM pegawai 
        WHERE is_active=1 
        ORDER BY nama 
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        jabatan_str = row[2] if row[2] else ''
        print(f"  • {row[0]} - {row[1]} ({jabatan_str[:50]})")
    
    conn.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("IMPORT DATA PEGAWAI DARI CSV")
    print("="*60 + "\n")
    
    import_pegawai()
