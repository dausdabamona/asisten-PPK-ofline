#!/usr/bin/env python
"""
PPK DOCUMENT FACTORY v4.0 - Setup Pegawai Import
=================================================
Import pegawai from CSV file (pegawai_2026-01-14ok.csv)
"""

import os
import sys
import csv
import sqlite3
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import DATABASE_PATH


def import_pegawai_from_csv(csv_path: str, db_path: str = None):
    """
    Import pegawai data from CSV file
    CSV format: nip;nama;jabatan;golongan;pangkat;rekening;bank;unitKerja
    """
    if db_path is None:
        db_path = DATABASE_PATH
    
    print(f"📁 Importing from: {csv_path}")
    print(f"📊 Database: {db_path}")
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure pegawai table exists with all columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pegawai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nip TEXT UNIQUE,
            nama TEXT NOT NULL,
            gelar_depan TEXT,
            gelar_belakang TEXT,
            pangkat TEXT,
            golongan TEXT,
            jabatan TEXT,
            unit_kerja TEXT,
            email TEXT,
            telepon TEXT,
            npwp TEXT,
            no_rekening TEXT,
            nama_bank TEXT,
            is_ppk INTEGER DEFAULT 0,
            is_ppspm INTEGER DEFAULT 0,
            is_bendahara INTEGER DEFAULT 0,
            is_pemeriksa INTEGER DEFAULT 0,
            is_pejabat_pengadaan INTEGER DEFAULT 0,
            signature_path TEXT,
            foto_path TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Check for missing columns and add them
    cursor.execute("PRAGMA table_info(pegawai)")
    existing_columns = {col[1] for col in cursor.fetchall()}
    
    columns_to_add = [
        ('email', 'TEXT'),
        ('telepon', 'TEXT'),
        ('is_pejabat_pengadaan', 'INTEGER DEFAULT 0'),
        ('foto_path', 'TEXT'),
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE pegawai ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added column: {col_name}")
            except:
                pass
    
    conn.commit()
    
    # Read and import CSV
    imported = 0
    updated = 0
    errors = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # CSV uses semicolon as delimiter
        reader = csv.DictReader(f, delimiter=';')
        
        for row_num, row in enumerate(reader, 2):
            try:
                nip = row.get('nip', '').strip()
                nama = row.get('nama', '').strip()
                jabatan = row.get('jabatan', '').strip()
                golongan = row.get('golongan', '').strip()
                pangkat = row.get('pangkat', '').strip()
                rekening = row.get('rekening', '').strip()
                bank = row.get('bank', '').strip()
                unit_kerja = row.get('unitKerja', '').strip()
                
                if not nama:
                    errors.append(f"Baris {row_num}: Nama kosong")
                    continue
                
                # Check if NIP exists
                if nip:
                    cursor.execute("SELECT id FROM pegawai WHERE nip = ?", (nip,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update
                        cursor.execute("""
                            UPDATE pegawai SET
                                nama = ?,
                                jabatan = ?,
                                golongan = ?,
                                pangkat = ?,
                                no_rekening = ?,
                                nama_bank = ?,
                                unit_kerja = ?,
                                is_active = 1,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE nip = ?
                        """, (nama, jabatan, golongan, pangkat, rekening, bank, unit_kerja, nip))
                        updated += 1
                        continue
                
                # Insert new
                cursor.execute("""
                    INSERT INTO pegawai (nip, nama, jabatan, golongan, pangkat, no_rekening, nama_bank, unit_kerja)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nip or None, nama, jabatan, golongan, pangkat, rekening, bank, unit_kerja))
                imported += 1
                
            except Exception as e:
                errors.append(f"Baris {row_num}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Import selesai!")
    print(f"   📥 Ditambahkan: {imported}")
    print(f"   🔄 Diupdate: {updated}")
    
    if errors:
        print(f"   ⚠️ Error: {len(errors)}")
        for err in errors[:5]:
            print(f"      - {err}")
        if len(errors) > 5:
            print(f"      ... dan {len(errors) - 5} lainnya")
    
    return imported, updated, errors


def create_all_tables(db_path: str = None):
    """Create all required tables for PPK Document Factory v4.0"""
    if db_path is None:
        db_path = DATABASE_PATH
    
    print(f"🗄️ Creating tables in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Paket Pejabat Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paket_pejabat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paket_id INTEGER NOT NULL,
            pegawai_id INTEGER NOT NULL,
            peran TEXT NOT NULL,
            urutan INTEGER DEFAULT 1,
            tanggal_penetapan DATE,
            nomor_sk TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
            FOREIGN KEY (pegawai_id) REFERENCES pegawai(id),
            UNIQUE(paket_id, pegawai_id, peran)
        )
    """)
    print("  ✅ Table: paket_pejabat")
    
    # Survey Harga Detail Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_harga_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paket_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            sumber_ke INTEGER NOT NULL,
            jenis_survey TEXT NOT NULL,
            nama_sumber TEXT,
            alamat TEXT,
            kota TEXT,
            telepon TEXT,
            tanggal_survey DATE,
            surveyor TEXT,
            nip_surveyor TEXT,
            platform TEXT,
            link_produk TEXT,
            tanggal_akses DATE,
            nomor_kontrak TEXT,
            tahun_kontrak INTEGER,
            instansi TEXT,
            harga REAL NOT NULL,
            keterangan TEXT,
            bukti_path TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Table: survey_harga_detail")
    
    # Harga Lifecycle Table (Audit Trail)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS harga_lifecycle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paket_id INTEGER NOT NULL,
            item_id INTEGER,
            tahap TEXT NOT NULL,
            tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            harga_satuan REAL,
            total REAL,
            keterangan TEXT,
            created_by TEXT,
            dokumen_ref TEXT,
            
            FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Table: harga_lifecycle")
    
    # Revisi Harga Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revisi_harga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paket_id INTEGER NOT NULL,
            tanggal_revisi DATE,
            nomor_ba_klarifikasi TEXT,
            total_hps_awal REAL,
            total_kontrak_hasil REAL,
            selisih REAL,
            persentase_selisih REAL,
            status TEXT DEFAULT 'draft',
            catatan TEXT,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
            FOREIGN KEY (approved_by) REFERENCES pegawai(id)
        )
    """)
    print("  ✅ Table: revisi_harga")
    
    # Revisi Harga Detail Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revisi_harga_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            revisi_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            harga_hps REAL,
            harga_kontrak REAL,
            selisih REAL,
            keterangan TEXT,
            
            FOREIGN KEY (revisi_id) REFERENCES revisi_harga(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Table: revisi_harga_detail")
    
    # Audit Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            user_name TEXT,
            action TEXT NOT NULL,
            table_name TEXT,
            record_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            notes TEXT
        )
    """)
    print("  ✅ Table: audit_log")
    
    # Bukti Survey Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bukti_survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paket_id INTEGER NOT NULL,
            item_id INTEGER,
            survey_detail_id INTEGER,
            jenis TEXT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            filesize INTEGER,
            mimetype TEXT,
            keterangan TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uploaded_by TEXT,
            
            FOREIGN KEY (paket_id) REFERENCES paket(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES item_barang(id) ON DELETE CASCADE,
            FOREIGN KEY (survey_detail_id) REFERENCES survey_harga_detail(id) ON DELETE CASCADE
        )
    """)
    print("  ✅ Table: bukti_survey")
    
    # Add columns to paket table if not exist
    cursor.execute("PRAGMA table_info(paket)")
    paket_columns = {col[1] for col in cursor.fetchall()}
    
    paket_new_columns = [
        ('nilai_hps_final', 'REAL'),
        ('nilai_kontrak_final', 'REAL'),
        ('overhead_profit', 'REAL DEFAULT 0.10'),
        ('spesifikasi_locked', 'INTEGER DEFAULT 0'),
        ('survey_locked', 'INTEGER DEFAULT 0'),
        ('hps_locked', 'INTEGER DEFAULT 0'),
        ('kak_locked', 'INTEGER DEFAULT 0'),
        ('kontrak_draft_locked', 'INTEGER DEFAULT 0'),
        ('nota_dinas_locked', 'INTEGER DEFAULT 0'),
        ('revisi_locked', 'INTEGER DEFAULT 0'),
        ('kontrak_final_locked', 'INTEGER DEFAULT 0'),
        ('metode_hps', "TEXT DEFAULT 'RATA'"),
    ]
    
    for col_name, col_type in paket_new_columns:
        if col_name not in paket_columns:
            try:
                cursor.execute(f"ALTER TABLE paket ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added paket.{col_name}")
            except:
                pass
    
    # Add columns to item_barang table if not exist
    cursor.execute("PRAGMA table_info(item_barang)")
    item_columns = {col[1] for col in cursor.fetchall()}
    
    item_new_columns = [
        ('harga_hps_satuan', 'REAL'),
        ('total_hps', 'REAL'),
        ('harga_kontrak_satuan', 'REAL'),
        ('total_kontrak', 'REAL'),
        ('selisih_harga', 'REAL'),
        ('selisih_total', 'REAL'),
        ('overhead_profit', 'REAL'),
    ]
    
    for col_name, col_type in item_new_columns:
        if col_name not in item_columns:
            try:
                cursor.execute(f"ALTER TABLE item_barang ADD COLUMN {col_name} {col_type}")
                print(f"  ✅ Added item_barang.{col_name}")
            except:
                pass
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_paket_pejabat_paket ON paket_pejabat(paket_id)",
        "CREATE INDEX IF NOT EXISTS idx_paket_pejabat_peran ON paket_pejabat(peran)",
        "CREATE INDEX IF NOT EXISTS idx_survey_detail_paket ON survey_harga_detail(paket_id)",
        "CREATE INDEX IF NOT EXISTS idx_survey_detail_item ON survey_harga_detail(item_id)",
        "CREATE INDEX IF NOT EXISTS idx_harga_lifecycle_paket ON harga_lifecycle(paket_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name, record_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_pegawai_nip ON pegawai(nip)",
        "CREATE INDEX IF NOT EXISTS idx_pegawai_nama ON pegawai(nama)",
    ]
    
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
        except:
            pass
    
    print("  ✅ Created indexes")
    
    conn.commit()
    conn.close()
    
    print("\n✅ All tables created successfully!")


def main():
    """Main function"""
    print("=" * 60)
    print("PPK DOCUMENT FACTORY v4.0 - Setup Data")
    print("=" * 60)
    
    # Create all tables
    create_all_tables()
    
    # Check for CSV file
    csv_paths = [
        '/mnt/user-data/uploads/pegawai_2026-01-14ok.csv',
        'data/pegawai.csv',
        'pegawai.csv',
    ]
    
    csv_path = None
    for path in csv_paths:
        if os.path.exists(path):
            csv_path = path
            break
    
    if csv_path:
        print("\n" + "=" * 60)
        import_pegawai_from_csv(csv_path)
    else:
        print("\n⚠️ CSV file tidak ditemukan. Jalankan import manual melalui aplikasi.")
    
    print("\n" + "=" * 60)
    print("Setup selesai! Jalankan aplikasi dengan: python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
