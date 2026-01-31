"""Test script to verify get_satker_aktif() method works correctly."""
from app.models.pencairan_models import PencairanManager

# Create manager instance
db = PencairanManager()

# Test get_satker_aktif() method
satker_data = db.get_satker_aktif()

print("=" * 70)
print("TEST: get_satker_aktif() Method")
print("=" * 70)
print()

if satker_data:
    print("✓ Method successfully returns satker data")
    print()
    print("Data Satker Aktif:")
    print("-" * 70)
    for key, value in satker_data.items():
        print(f"  {key:25s} : {value}")
    print()
    print("=" * 70)
    print("✓ TEST PASSED - get_satker_aktif() is working correctly!")
    print("=" * 70)
else:
    print("✗ TEST FAILED - Method returned empty data")
    exit(1)
