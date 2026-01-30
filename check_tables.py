import sqlite3
from app.core.config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=" * 60)
print("TABLES IN DATABASE")
print("=" * 60)
for t in tables:
    print(f"  - {t[0]}")

# Check if pagu_anggaran exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagu_anggaran'")
result = cursor.fetchone()

print("\n" + "=" * 60)
if not result:
    print("ERROR: pagu_anggaran table NOT FOUND!")
    print("\nNeed to create table pagu_anggaran")
else:
    print("OK: pagu_anggaran table EXISTS")
    # Get schema
    cursor.execute('PRAGMA table_info(pagu_anggaran)')
    cols = cursor.fetchall()
    print("\nColumns:")
    for col in cols:
        print(f"  {col[1]:30} {col[2]}")
    
    # Count records
    cursor.execute('SELECT COUNT(*) FROM pagu_anggaran')
    count = cursor.fetchone()[0]
    print(f"\nRecords: {count}")

print("=" * 60)
conn.close()
