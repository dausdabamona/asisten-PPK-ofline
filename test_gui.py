#!/usr/bin/env python3
"""
Test script untuk cek apakah PySide6 bisa jalan
"""

print("=" * 60)
print("PPK DOCUMENT FACTORY - GUI TEST")
print("=" * 60)

# Test 1: Import modules
print("\n[1] Testing imports...")

try:
    import sys
    print(f"    Python: {sys.version}")
except Exception as e:
    print(f"    ERROR sys: {e}")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
    from PySide6.QtCore import Qt
    print("    PySide6: OK")
except Exception as e:
    print(f"    ERROR PySide6: {e}")
    print("\n    Coba install ulang: python -m pip install PySide6")
    input("\nTekan Enter...")
    exit(1)

try:
    import docx
    print("    python-docx: OK")
except Exception as e:
    print(f"    ERROR python-docx: {e}")

try:
    import openpyxl
    print("    openpyxl: OK")
except Exception as e:
    print(f"    ERROR openpyxl: {e}")

# Test 2: Simple GUI
print("\n[2] Testing GUI window...")
print("    Jika window muncul, klik tombol 'Tutup' atau X")

try:
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("PPK DocFactory - Test Window")
    window.setMinimumSize(400, 200)
    
    central = QWidget()
    layout = QVBoxLayout(central)
    
    label = QLabel("✅ PySide6 GUI berfungsi dengan baik!")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
    layout.addWidget(label)
    
    label2 = QLabel("Klik tombol di bawah untuk menutup dan melanjutkan.")
    label2.setAlignment(Qt.AlignCenter)
    layout.addWidget(label2)
    
    btn = QPushButton("Tutup & Lanjutkan ke Aplikasi Utama")
    btn.setStyleSheet("padding: 10px; font-size: 14px;")
    btn.clicked.connect(window.close)
    layout.addWidget(btn)
    
    window.setCentralWidget(central)
    window.show()
    
    app.exec()
    
    print("    GUI test: PASSED")
    
except Exception as e:
    print(f"    ERROR GUI: {e}")
    import traceback
    traceback.print_exc()
    input("\nTekan Enter...")
    exit(1)

# Test 3: Launch main app
print("\n[3] Launching main application...")
print("=" * 60)

try:
    from app.ui.dashboard import main
    main()
except Exception as e:
    print(f"\nERROR launching app: {e}")
    import traceback
    traceback.print_exc()
    input("\nTekan Enter...")
