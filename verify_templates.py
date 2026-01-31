#!/usr/bin/env python3
"""
Verifikasi template yang terdaftar vs yang ada di folder
"""

import os
from pathlib import Path
from app.core.config import DOCUMENT_TEMPLATES, WORD_TEMPLATES_DIR, EXCEL_TEMPLATES_DIR

# Get actual files
word_files = set(f.name for f in Path(WORD_TEMPLATES_DIR).glob('*.docx'))
excel_files = set(f.name for f in Path(EXCEL_TEMPLATES_DIR).glob('*.xlsx'))

# Get registered templates
registered = set(DOCUMENT_TEMPLATES.keys())
registered_word = {t['template'] for t in DOCUMENT_TEMPLATES.values() if t['type'] == 'word'}
registered_excel = {t['template'] for t in DOCUMENT_TEMPLATES.values() if t['type'] == 'excel'}

print("=" * 80)
print("TEMPLATE VERIFICATION REPORT")
print("=" * 80)
print()

# Summary
print(f"📊 SUMMARY:")
print(f"  • Total registered templates: {len(registered)}")
print(f"  • Registered Word templates: {len(registered_word)}")
print(f"  • Registered Excel templates: {len(registered_excel)}")
print()
print(f"  • Actual Word files: {len(word_files)}")
print(f"  • Actual Excel files: {len(excel_files)}")
print()

# Check missing files
print(f"❌ REGISTERED BUT MISSING FILE:")
missing_word = registered_word - word_files
missing_excel = registered_excel - excel_files
if missing_word or missing_excel:
    for f in sorted(missing_word):
        print(f"  • {f} (Word)")
    for f in sorted(missing_excel):
        print(f"  • {f} (Excel)")
else:
    print("  ✅ All registered templates have files!")
print()

# Check extra files not registered
print(f"⚠️  FILES NOT REGISTERED:")
extra_word = word_files - registered_word
extra_excel = excel_files - registered_excel
if extra_word or extra_excel:
    for f in sorted(extra_word):
        print(f"  • {f} (Word)")
    for f in sorted(extra_excel):
        print(f"  • {f} (Excel)")
else:
    print("  ✅ All files are registered!")
print()

# List all registered templates
print("📋 ALL REGISTERED TEMPLATES:")
print("-" * 80)
for code, config in sorted(DOCUMENT_TEMPLATES.items()):
    icon = '📄' if config['type'] == 'word' else '📊'
    print(f"{icon} {code:30} | {config['name']:45} | {config['template']}")

print()
print("=" * 80)
