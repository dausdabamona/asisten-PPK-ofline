#!/usr/bin/env python3
"""
Simple build script untuk PPK Factory
Membuat executable dengan PyInstaller - versi simple
"""

import os
import sys
import subprocess

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SPEC_FILE = os.path.join(APP_DIR, 'ppk_factory.spec')

print("=" * 60)
print("PPK FACTORY - Build EXE (Simple Mode)")
print("=" * 60)

# Clean build folders
print("\n[1/3] Cleaning build directories...")
import shutil
import time
for folder in ['build', '__pycache__']:
    folder_path = os.path.join(APP_DIR, folder)
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"  ✓ Deleted {folder}")
        except PermissionError:
            print(f"  ⚠ Skipped {folder} (in use, will be cleaned during build)")

# Run PyInstaller
print("\n[2/3] Running PyInstaller...")
print("-" * 60)

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--clean',
    '--noconfirm',
    '--onefile',  # Single executable
    '--windowed',  # No console window
    '--name=PPK_Factory',
    '--icon=assets/icons/app.ico' if os.path.exists(os.path.join(APP_DIR, 'assets/icons/app.ico')) else None,
    'main.py'
]

# Filter None values
cmd = [c for c in cmd if c is not None]

try:
    result = subprocess.run(cmd, cwd=APP_DIR)
    if result.returncode != 0:
        print(f"\n❌ Build failed with exit code {result.returncode}")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)

print("\n[3/3] Checking output...")
print("-" * 60)

dist_dir = os.path.join(APP_DIR, 'dist')
if os.path.exists(dist_dir):
    exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
    if exe_files:
        exe_file = os.path.join(dist_dir, exe_files[0])
        size_mb = os.path.getsize(exe_file) / (1024 * 1024)
        print(f"✓ Build successful!")
        print(f"  File: {exe_file}")
        print(f"  Size: {size_mb:.2f} MB")
        print("\n✓ Executable siap untuk testing!")
    else:
        print("❌ No .exe files found in dist folder")
        sys.exit(1)
else:
    print("❌ dist folder not found")
    sys.exit(1)
