import sqlite3

conn = sqlite3.connect('e:/gdrive/aplikasi/data/ppk_workflow.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM pegawai WHERE is_active=1")
total = cursor.fetchone()[0]

print(f"Total pegawai aktif: {total}")

cursor.execute("SELECT nama, nip, jabatan FROM pegawai WHERE is_active=1 LIMIT 5")
print("\n5 pegawai pertama:")
for row in cursor.fetchall():
    print(f"  - {row[0]} ({row[1]})")

conn.close()
