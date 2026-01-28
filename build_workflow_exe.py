"""
Build EXE untuk PPK Workflow Pencairan Dana
============================================

Script ini akan membuat file executable (.exe) untuk aplikasi
Workflow Pencairan Dana menggunakan PyInstaller.

Cara penggunaan:
    python build_workflow_exe.py

Output:
    - File .exe akan ada di folder dist/
    - Nama: PPK_Workflow_Pencairan_Dana.exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

print("=" * 70)
print("PPK WORKFLOW PENCAIRAN DANA - BUILD EXECUTABLE")
print("=" * 70)

# Directories
APP_DIR = Path(__file__).parent
DIST_DIR = APP_DIR / 'dist'
BUILD_DIR = APP_DIR / 'build'
SPEC_FILE = APP_DIR / 'ppk_workflow.spec'

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"\n✅ PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("\n❌ PyInstaller not found!")
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller installed successfully")
            return True
        except:
            print("❌ Failed to install PyInstaller")
            print("Please run: pip install pyinstaller")
            return False

def check_dependencies():
    """Check required dependencies"""
    print("\n📦 Checking dependencies...")
    
    dependencies = {
        'PySide6': 'PySide6',
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Please install: pip install " + ' '.join(missing))
        return False
    
    return True

def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build...")
    
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print("   ✅ Removed build/")
    
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("   ✅ Removed dist/")
    
    # Remove .spec file if exists (we'll regenerate)
    if not SPEC_FILE.exists():
        print("   ⚠️  No spec file found, will use default PyInstaller settings")

def build_exe():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    print("   This may take several minutes...\n")
    
    # Build command
    if SPEC_FILE.exists():
        print(f"   Using spec file: {SPEC_FILE.name}")
        cmd = ['pyinstaller', '--clean', '--noconfirm', str(SPEC_FILE)]
    else:
        print("   Using PyInstaller auto-detection")
        cmd = [
            'pyinstaller',
            '--name=PPK_Workflow_Pencairan_Dana',
            '--onefile',
            '--windowed',
            '--clean',
            '--noconfirm',
            # Add hidden imports
            '--hidden-import=PySide6.QtCore',
            '--hidden-import=PySide6.QtGui',
            '--hidden-import=PySide6.QtWidgets',
            '--hidden-import=sqlite3',
            # Add data files
            '--add-data=app/ui/styles/main.qss;app/ui/styles',
            # Main script
            'test_workflow_ui.py'
        ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return False

def verify_exe():
    """Verify the executable was created"""
    exe_path = DIST_DIR / 'PPK_Workflow_Pencairan_Dana.exe'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Executable created successfully!")
        print(f"   Location: {exe_path}")
        print(f"   Size: {size_mb:.2f} MB")
        return True
    else:
        print("\n❌ Executable not found!")
        return False

def main():
    """Main build process"""
    
    # Step 1: Check PyInstaller
    if not check_pyinstaller():
        return 1
    
    # Step 2: Check dependencies
    if not check_dependencies():
        return 1
    
    # Step 3: Clean previous build
    clean_build()
    
    # Step 4: Build executable
    if not build_exe():
        return 1
    
    # Step 5: Verify
    if not verify_exe():
        return 1
    
    # Success!
    print("\n" + "=" * 70)
    print("🎉 BUILD SUCCESSFUL! 🎉")
    print("=" * 70)
    print("\nYour executable is ready:")
    print(f"   📁 {DIST_DIR / 'PPK_Workflow_Pencairan_Dana.exe'}")
    print("\nYou can now:")
    print("   1. Run the .exe file directly")
    print("   2. Copy it to any Windows PC (no Python needed)")
    print("   3. Share it with other users")
    print("\n⚠️  Note: First run may be slower (Windows Defender scan)")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
