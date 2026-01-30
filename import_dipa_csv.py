"""
Script untuk import data DIPA dari file CSV
Gunakan file: e:\gdrive\0. 2026\anggaran.csv
"""

import sqlite3
import csv
import os
from app.core.config import DATABASE_PATH, TAHUN_ANGGARAN

def import_dipa_csv(csv_path, tahun_anggaran=TAHUN_ANGGARAN):
    """Import DIPA data dari CSV ke database."""
    
    if not os.path.exists(csv_path):
        print(f"Error: File tidak ditemukan: {csv_path}")
        return False
    
    print("=" * 70)
    print("IMPORT DATA DIPA")
    print("=" * 70)
    print(f"File: {csv_path}")
    print(f"Tahun: {tahun_anggaran}")
    print(f"Database: {DATABASE_PATH}")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        imported = 0
        updated = 0
        skipped = 0
        errors = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames:
                print("Error: CSV file kosong")
                return False
            
            print(f"\nKolom CSV: {', '.join(reader.fieldnames)}")
            print("\n" + "-" * 70)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Parse fields
                    kode_program = row.get('KODE_PROGRAM', '').strip() or '0'
                    kode_kegiatan = row.get('KODE_KEGIATAN', '').strip() or '0'
                    kode_output = row.get('KODE_OUTPUT', '').strip() or row.get('KODE_KRO', '').strip() or '0'
                    kode_komponen = row.get('KODE_KOMPONEN', '').strip() or '0'
                    kode_subkomponen = row.get('KODE_SUBKOMPONEN', '').strip() or '0'
                    kode_akun = row.get('KODE_AKUN', '').strip() or '0'
                    kode_detail = row.get('KODE_DETAIL', '').strip() or '0'
                    
                    # Build kode_full
                    kode_full = f"{kode_program}.{kode_kegiatan}.{kode_output}.{kode_komponen}.{kode_subkomponen}.{kode_akun}.{kode_detail}"
                    
                    uraian = row.get('URAIAN_ITEM', row.get('URAIAN', '')).strip() or 'N/A'
                    
                    # Parse numbers
                    def parse_number(val):
                        if not val or val.strip() == '':
                            return 0.0
                        try:
                            cleaned = ''.join(c for c in str(val) if c.isdigit() or c == '.')
                            return float(cleaned) if cleaned else 0.0
                        except:
                            return 0.0
                    
                    volume = parse_number(row.get('VOLKEG', '0'))
                    satuan = row.get('SATKEG', 'Jenis').strip()
                    harga_satuan = parse_number(row.get('HARGASAT', '0'))
                    jumlah = parse_number(row.get('TOTAL', '0'))
                    
                    # Check if exists
                    cursor.execute("""
                        SELECT id FROM pagu_anggaran
                        WHERE tahun_anggaran = ? AND kode_full = ?
                    """, (tahun_anggaran, kode_full))
                    
                    if cursor.fetchone():
                        # Update
                        cursor.execute("""
                            UPDATE pagu_anggaran
                            SET uraian = ?, volume = ?, satuan = ?,
                                harga_satuan = ?, jumlah = ?, sisa = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE tahun_anggaran = ? AND kode_full = ?
                        """, (
                            uraian, volume, satuan,
                            harga_satuan, jumlah, jumlah,
                            tahun_anggaran, kode_full
                        ))
                        updated += 1
                    else:
                        # Insert
                        cursor.execute("""
                            INSERT INTO pagu_anggaran (
                                tahun_anggaran, kode_full, kode_program, kode_kegiatan,
                                kode_akun, uraian, volume, satuan,
                                harga_satuan, jumlah, realisasi, sisa, persen_realisasi,
                                level_kode, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 0, 8, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            tahun_anggaran, kode_full, kode_program, kode_kegiatan,
                            kode_akun, uraian, volume, satuan,
                            harga_satuan, jumlah, jumlah
                        ))
                        imported += 1
                    
                    if row_num % 100 == 0:
                        print(f"Processing row {row_num}...")
                
                except Exception as e:
                    print(f"  ❌ Row {row_num} Error: {str(e)}")
                    errors += 1
                    continue
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 70)
        print("HASIL IMPORT")
        print("=" * 70)
        print(f"✅ Berhasil diimpor:     {imported}")
        print(f"🔄 Berhasil diupdate:    {updated}")
        print(f"⏭️  Dilewati (duplikat):  {skipped}")
        print(f"❌ Error:                {errors}")
        print(f"📊 Total diproses:       {imported + updated + skipped}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Try common file locations
    possible_files = [
        r'e:\gdrive\0. 2026\anggaran.csv',
        r'e:\gdrive\0. 2026\DIPA.csv',
        r'e:\gdrive\0. 2026\pagu_anggaran.csv',
    ]
    
    csv_file = None
    for f in possible_files:
        if os.path.exists(f):
            csv_file = f
            break
    
    if not csv_file:
        print("File anggaran.csv tidak ditemukan!")
        print(f"Periksa lokasi file di folder: e:\\gdrive\\0. 2026\\")
        exit(1)
    
    success = import_dipa_csv(csv_file)
    exit(0 if success else 1)
