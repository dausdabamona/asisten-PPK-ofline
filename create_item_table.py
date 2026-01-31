"""Script untuk membuat tabel transaksi_item."""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'data', 'ppk_factory.db')
print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create transaksi_item table
schema = """
CREATE TABLE IF NOT EXISTS transaksi_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_id INTEGER NOT NULL,
    nomor_urut INTEGER NOT NULL,
    nama_barang TEXT NOT NULL,
    spesifikasi TEXT,
    volume REAL DEFAULT 0,
    satuan TEXT,
    harga_satuan REAL DEFAULT 0,
    total_item REAL DEFAULT 0,
    status TEXT DEFAULT 'diminta',
    volume_disetujui REAL DEFAULT 0,
    volume_dipesan REAL DEFAULT 0,
    volume_diterima REAL DEFAULT 0,
    volume_diserahkan REAL DEFAULT 0,
    harga_survey_1 REAL,
    harga_survey_2 REAL,
    harga_survey_3 REAL,
    harga_rata REAL,
    harga_hps REAL,
    harga_negosiasi REAL,
    harga_realisasi REAL DEFAULT 0,
    total_realisasi REAL DEFAULT 0,
    lembar_permintaan_id INTEGER,
    paket_id INTEGER,
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transaksi_item_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaksi_item_id INTEGER NOT NULL,
    aksi TEXT NOT NULL,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT,
    fase INTEGER,
    dokumen_ref TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT
);

CREATE INDEX IF NOT EXISTS idx_transaksi_item_transaksi ON transaksi_item(transaksi_id);
CREATE INDEX IF NOT EXISTS idx_transaksi_item_status ON transaksi_item(status);
"""

cur.executescript(schema)
conn.commit()
print("Tables created successfully!")

# Check tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("All tables:", [r[0] for r in cur.fetchall()])

# Check transaksi_item columns
cur.execute("PRAGMA table_info(transaksi_item)")
cols = cur.fetchall()
print(f"\ntransaksi_item columns ({len(cols)}):")
for col in cols:
    print(f"  {col[1]} ({col[2]})")

conn.close()
print("\nDone!")
