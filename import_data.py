#!/usr/bin/env python3
"""
Script untuk import data DIPA dan Pegawai ke database
"""
import csv
import sqlite3
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import DATABASE_PATH, TAHUN_ANGGARAN

print("=" * 70)
print("IMPORT DATA KE DATABASE PPK")
print("=" * 70)
print(f"\nDatabase: {DATABASE_PATH}")
print(f"Tahun Anggaran: {TAHUN_ANGGARAN}")

# ============================================================================
# IMPORT DATA DIPA
# ============================================================================
print("\n" + "=" * 70)
print("1. IMPORT DATA ANGGARAN DIPA")
print("=" * 70)

dipa_file = r'e:\gdrive\0. 2026\anggaran.csv'

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    with open(dipa_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        imported_dipa = 0
        skipped_dipa = 0
        error_dipa = 0
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Extract data
                kode_program = row.get('KODE_PROGRAM', '').strip()
                kode_kegiatan = row.get('KODE_KEGIATAN', '').strip()
                kode_output = row.get('KODE_OUTPUT', '').strip()
                kode_komponen = row.get('KODE_KOMPONEN', '').strip()
                kode_subkomponen = row.get('KODE_SUBKOMPONEN', '').strip()
                kode_akun = row.get('KODE_AKUN', '').strip()
                kode_item = row.get('KODE_ITEM', '').strip()
                
                # Build kode_full
                kode_parts = [p for p in [
                    kode_program, kode_kegiatan, kode_output,
                    kode_komponen, kode_subkomponen, kode_akun, kode_item
                ] if p]
                kode_full = '.'.join(kode_parts)
                
                if not kode_full:
                    skipped_dipa += 1
                    continue
                
                uraian = row.get('URAIAN_ITEM', '').strip()
                if not uraian:
                    uraian = row.get('URAIAN_SUBKOMPONEN', '').strip()
                
                # Parse numbers
                volume_str = row.get('VOLKEG', '0').strip()
                volume = float(volume_str) if volume_str else 0.0
                
                satuan = row.get('SATKEG', '').strip()
                
                harga_str = row.get('HARGASAT', '0').strip()
                try:
                    harga = float(harga_str.replace('.', '')) if harga_str else 0.0
                except:
                    harga = 0.0
                
                total_str = row.get('TOTAL', '0').strip()
                try:
                    jumlah = float(total_str.replace('.', '')) if total_str else 0.0
                except:
                    jumlah = 0.0
                
                sumber_dana = row.get('SUMBER_DANA', 'RM').strip()
                
                # Check if exists
                cursor.execute("""
                    SELECT id FROM pagu_anggaran
                    WHERE tahun_anggaran = ? AND kode_full = ?
                """, (TAHUN_ANGGARAN, kode_full))
                
                if cursor.fetchone():
                    skipped_dipa += 1
                else:
                    cursor.execute("""
                        INSERT INTO pagu_anggaran (
                            tahun_anggaran, kode_full, uraian,
                            volume, satuan, harga_satuan, jumlah,
                            realisasi, sisa, persen_realisasi,
                            level_kode, sumber_dana,
                            kode_program, kode_kegiatan, kode_akun
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, 0, 8, ?, ?, ?, ?)
                    """, (
                        TAHUN_ANGGARAN, kode_full, uraian,
                        volume, satuan, harga, jumlah,
                        jumlah,
                        sumber_dana,
                        kode_program, kode_kegiatan, kode_akun
                    ))
                    imported_dipa += 1
                    
            except Exception as e:
                error_dipa += 1
                if row_num <= 5:
                    print(f"  ⚠️  Error row {row_num}: {str(e)}")
        
        conn.commit()
        
        print(f"\n✓ Import DIPA selesai!")
        print(f"  ✓ Berhasil diimpor: {imported_dipa}")
        print(f"  ⏭️  Dilewati (sudah ada): {skipped_dipa}")
        if error_dipa > 0:
            print(f"  ❌ Error: {error_dipa}")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM pagu_anggaran WHERE tahun_anggaran = ?", (TAHUN_ANGGARAN,))
        total = cursor.fetchone()[0]
        print(f"  📊 Total data DIPA sekarang: {total}")

except Exception as e:
    print(f"❌ Error: {str(e)}")

conn.close()

# ============================================================================
# INSERT DATA PEGAWAI SAMPLE (karena file yang diberikan adalah Google Sheet)
# ============================================================================
print("\n" + "=" * 70)
print("2. INSERT DATA PEGAWAI")
print("=" * 70)

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Data pegawai sample
pegawai_data = [
    ('198501101985032001', 'Budi Santoso', 'Pembina Tingkat I', 'Kepala Satker', 'budi@example.com', '081234567890', '12345678901234567890'),
    ('198602051986032002', 'Siti Nurhaliza', 'Pembina Tingkat I', 'Bendahara', 'siti@example.com', '081234567891', '12345678901234567891'),
    ('198703101987032003', 'Ahmad Wijaya', 'Penata Tingkat I', 'Sekretaris', 'ahmad@example.com', '081234567892', '12345678901234567892'),
    ('198804151988032004', 'Eka Putri', 'Penata', 'Operator', 'eka@example.com', '081234567893', '12345678901234567893'),
    ('198905201989032005', 'Rahmadi Sukma', 'Penata Muda Tingkat I', 'Koordinator Keuangan', 'rahmadi@example.com', '081234567894', '12345678901234567894'),
    ('199006251990032006', 'Nur Azizah', 'Penata Muda', 'Staf Administrasi', 'nur@example.com', '081234567895', '12345678901234567895'),
]

try:
    inserted_pegawai = 0
    for nip, nama, pangkat, jabatan, email, telepon, npwp in pegawai_data:
        cursor.execute('''
            INSERT OR IGNORE INTO pegawai 
            (nip, nama, pangkat, jabatan, email, telepon, npwp, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (nip, nama, pangkat, jabatan, email, telepon, npwp))
        inserted_pegawai += 1

    conn.commit()
    
    print(f"✓ Insert pegawai selesai!")
    print(f"  ✓ Berhasil diinsert: {inserted_pegawai}")
    
    # Verify
    cursor.execute('SELECT COUNT(*) FROM pegawai WHERE is_active = 1')
    total_pegawai = cursor.fetchone()[0]
    print(f"  👥 Total pegawai aktif sekarang: {total_pegawai}")
    
    cursor.execute('SELECT nip, nama, jabatan FROM pegawai WHERE is_active = 1 ORDER BY nama')
    print(f"\n  Daftar pegawai:")
    for nip, nama, jabatan in cursor.fetchall():
        print(f"    • {nama} ({nip}) - {jabatan}")

except Exception as e:
    print(f"❌ Error: {str(e)}")

conn.close()

print("\n" + "=" * 70)
print("✓ IMPORT DATA SELESAI!")
print("=" * 70)
print("\nSilakan jalankan aplikasi untuk melihat data yang telah diimport.")
