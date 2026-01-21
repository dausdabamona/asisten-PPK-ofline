"""
Import Pegawai dari CSV
=======================
Script untuk import data pegawai dari file CSV
"""

import os
import sys
import csv

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db_manager

def import_pegawai_csv(csv_path: str):
    """Import pegawai from CSV file"""
    
    if not os.path.exists(csv_path):
        print(f"❌ File tidak ditemukan: {csv_path}")
        return
    
    db = get_db_manager()
    
    # Read CSV with semicolon delimiter
    pegawai_list = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # Detect delimiter
        first_line = f.readline()
        f.seek(0)
        
        delimiter = ';' if ';' in first_line else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        
        for row in reader:
            # Map columns
            data = {
                'nip': (row.get('nip') or row.get('NIP') or '').strip(),
                'nama': (row.get('nama') or row.get('NAMA') or '').strip(),
                'jabatan': (row.get('jabatan') or row.get('JABATAN') or '').strip(),
                'pangkat': (row.get('pangkat') or row.get('PANGKAT') or '').strip(),
                'golongan': (row.get('golongan') or row.get('GOLONGAN') or row.get('gol') or '').strip(),
                'unit_kerja': (row.get('unitKerja') or row.get('unit_kerja') or row.get('UNIT_KERJA') or '').strip(),
                'no_rekening': (row.get('rekening') or row.get('no_rekening') or '').strip(),
                'nama_bank': (row.get('bank') or row.get('nama_bank') or '').strip(),
            }
            
            if data['nama']:
                pegawai_list.append(data)
    
    print(f"📋 Ditemukan {len(pegawai_list)} pegawai dalam file")
    
    # Import to database
    imported = 0
    updated = 0
    errors = []
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        for data in pegawai_list:
            try:
                nip = data.get('nip')
                
                if nip:
                    # Check existing
                    cursor.execute("SELECT id FROM pegawai WHERE nip = ?", (nip,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update
                        cursor.execute("""
                            UPDATE pegawai SET
                                nama = ?, jabatan = ?, pangkat = ?, golongan = ?,
                                unit_kerja = ?, no_rekening = ?, nama_bank = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE nip = ?
                        """, (
                            data['nama'], data['jabatan'], data['pangkat'], data['golongan'],
                            data['unit_kerja'], data['no_rekening'], data['nama_bank'],
                            nip
                        ))
                        updated += 1
                        continue
                
                # Insert new
                cursor.execute("""
                    INSERT INTO pegawai (nip, nama, jabatan, pangkat, golongan, unit_kerja, no_rekening, nama_bank)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    nip or None, data['nama'], data['jabatan'], data['pangkat'],
                    data['golongan'], data['unit_kerja'], data['no_rekening'], data['nama_bank']
                ))
                imported += 1
                
            except Exception as e:
                errors.append(f"{data.get('nama', 'Unknown')}: {str(e)}")
        
        conn.commit()
    
    print(f"\n✅ Import selesai!")
    print(f"   Ditambahkan: {imported}")
    print(f"   Diupdate: {updated}")
    
    if errors:
        print(f"\n⚠️ {len(errors)} error:")
        for err in errors[:5]:
            print(f"   - {err}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # Default path
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'pegawai.csv')
        
        # Check uploads folder
        uploads_csv = '/mnt/user-data/uploads/pegawai_2026-01-14ok.csv'
        if os.path.exists(uploads_csv):
            csv_path = uploads_csv
    
    print(f"📁 Importing from: {csv_path}")
    import_pegawai_csv(csv_path)
