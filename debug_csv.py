import csv

CSV_PATH = "e:/gdrive/0. 2026/suplier/pegawai_2026-01-14ok.csv"

print("Test parsing CSV:")
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    print(f"\nHeader: {reader.fieldnames}\n")
    
    for idx, row in enumerate(reader, 1):
        print(f"Baris {idx}:")
        print(f"  Keys available: {list(row.keys())}")
        
        for key, value in row.items():
            if value:
                print(f"  {key}: {value[:50] if len(value) > 50 else value}")
        
        if idx >= 3:
            break
