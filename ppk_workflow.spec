# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller Spec File untuk PPK Workflow Pencairan Dana
"""

import os
import sys
from pathlib import Path

# Get app directory (use SPECPATH which is always the spec file location)
app_dir = Path(SPECPATH)

block_cipher = None

a = Analysis(
    ['test_workflow_ui.py'],
    pathex=[str(app_dir)],
    binaries=[],
    datas=[
        # Include QSS stylesheet
        ('app/ui/styles/main.qss', 'app/ui/styles'),
        # Include config files
        ('app/config/*.py', 'app/config'),
        # Include models
        ('app/models/*.py', 'app/models'),
        # Include templates
        ('app/templates/*.py', 'app/templates'),
        # Include UI components
        ('app/ui/components/*.py', 'app/ui/components'),
        # Include UI pages
        ('app/ui/pages/pencairan/*.py', 'app/ui/pages/pencairan'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlite3',
        'app.models.pencairan_models',
        'app.config.workflow_config',
        'app.ui.components',
        'app.ui.pages.pencairan',
        'app.ui.sidebar',
        'app.ui.workflow_main_window',
        'app.templates.engine',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PPK_Workflow_Pencairan_Dana',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if available
    version_file=None,
)
