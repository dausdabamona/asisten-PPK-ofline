# -*- mode: python ; coding: utf-8 -*-
"""
PPK DOCUMENT FACTORY v4.0 - PyInstaller Spec File (Workflow Edition)
=====================================================================
Build executable dengan: pyinstaller ppk_factory.spec

Versi ini menggunakan UI workflow-based untuk pencairan dana (UP/TUP/LS)
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Path aplikasi
block_cipher = None
ROOT_DIR = os.path.dirname(os.path.abspath(SPEC))

# Collect PySide6 data files
pyside6_datas = collect_data_files('PySide6', include_py_files=False)

# Collect submodules - termasuk modul baru untuk workflow
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
    # Core modules
    'app.core',
    'app.core.config',
    'app.core.database',
    'app.core.database_v4',
    # Model modules
    'app.models',
    'app.models.pencairan_models',
    # Config modules
    'app.config',
    'app.config.workflow_config',
    # Service modules
    'app.services',
    'app.services.dokumen_generator',
    # UI Components
    'app.ui.components',
    'app.ui.components.sidebar',
    'app.ui.components.dashboard_cards',
    'app.ui.components.fase_stepper',
    'app.ui.components.dokumen_checklist',
    'app.ui.components.kalkulasi_widget',
    'app.ui.components.countdown_widget',
    'app.ui.components.rincian_kalkulasi_widget',
    # UI Dialogs
    'app.ui.dialogs',
    'app.ui.dialogs.dokumen_dialog',
    # UI Pages
    'app.ui.pages',
    'app.ui.pages.pencairan',
    'app.ui.pages.pencairan.base_list_page',
    'app.ui.pages.pencairan.base_detail_page',
    'app.ui.pages.pencairan.transaksi_form',
    'app.ui.pages.pencairan.up_list',
    'app.ui.pages.pencairan.up_detail',
    'app.ui.pages.pencairan.tup_list',
    'app.ui.pages.pencairan.tup_detail',
    'app.ui.pages.pencairan.ls_list',
    'app.ui.pages.pencairan.ls_detail',
    'app.ui.pages.pencairan.dashboard_pencairan',
    # Main window
    'app.ui.main_window_v2',
]

# Data files to bundle
datas = [
    # Word templates
    (os.path.join(ROOT_DIR, 'templates', 'word'), os.path.join('templates', 'word')),
    # Excel templates
    (os.path.join(ROOT_DIR, 'templates', 'excel'), os.path.join('templates', 'excel')),
    # QSS Stylesheet
    (os.path.join(ROOT_DIR, 'app', 'ui', 'styles'), os.path.join('app', 'ui', 'styles')),
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
