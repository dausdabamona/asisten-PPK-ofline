import sqlite3

conn = sqlite3.connect('e:/gdrive/aplikasi/data/ppk_workflow.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(pegawai)')
print('Kolom tabel pegawai:')
for row in cursor.fetchall():
    print(f"  {row[1]} ({row[2]})")

conn.close()
