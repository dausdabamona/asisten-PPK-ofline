#!/usr/bin/env python3
"""
Simple build runner untuk menghindari KeyboardInterrupt
"""
import subprocess
import sys
import os

os.chdir('e:\\gdrive\\aplikasi')

# Run PyInstaller directly
cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--clean', '--noconfirm', 
    'ppk_factory.spec'
]

print("=" * 60)
print("Building EXE...")
print("=" * 60)

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Print output real-time
for line in proc.stdout:
    print(line, end='')

proc.wait()

if proc.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ BUILD SUCCESSFUL!")
    print("=" * 60)
else:
    print(f"\n❌ BUILD FAILED with code {proc.returncode}")
    sys.exit(1)
