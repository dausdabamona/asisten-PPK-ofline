import csv

csv_path = r'e:\gdrive\0. 2026\suplier\pegawai_nonpns.csv'
rows = list(csv.DictReader(open(csv_path)))

print("=" * 60)
print("DATA BARIS 11 (yang error):")
print("=" * 60)
print(rows[10])  # index 10 = baris 11

print("\n" + "=" * 60)
print("SEMUA BARIS:")
print("=" * 60)
for i, row in enumerate(rows, 1):
    print(f"Baris {i}: {row.get('NMPPPNPN', 'N/A')} | NIP: {row.get('NIKPPNPN', 'N/A')}")
