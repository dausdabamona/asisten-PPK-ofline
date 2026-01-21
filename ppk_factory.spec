# -*- mode: python ; coding: utf-8 -*-
"""
PPK DOCUMENT FACTORY v3.0 - PyInstaller Spec File
==================================================
Build executable dengan: pyinstaller ppk_factory.spec
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Path aplikasi
block_cipher = None
ROOT_DIR = os.path.dirname(os.path.abspath(SPEC))

# Collect PySide6 data files
pyside6_datas = collect_data_files('PySide6', include_py_files=False)

# Collect submodules
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'docx',
    'docx.oxml',
    'docx.oxml.ns',
    'docx.oxml.text.paragraph',
    'docx.oxml.text.run',
    'docx.shared',
    'docx.enum.text',
    'docx.enum.table',
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.utils',
    'PIL',
    'PIL.Image',
    'PIL.ExifTags',
    'PIL.TiffImagePlugin',
    'PIL.JpegImagePlugin',
    'PIL.PngImagePlugin',
]

# Data files to bundle
datas = [
    # Word templates
    (os.path.join(ROOT_DIR, 'templates', 'word'), os.path.join('templates', 'word')),
    # Excel templates
    (os.path.join(ROOT_DIR, 'templates', 'excel'), os.path.join('templates', 'excel')),
]

# Add PySide6 data
datas.extend(pyside6_datas)

a = Analysis(
    [os.path.join(ROOT_DIR, 'main.py')],
    pathex=[ROOT_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'cv2',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PPK_Document_Factory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available: icon='assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PPK_Document_Factory',
)
