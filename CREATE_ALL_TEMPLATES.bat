@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0 - CREATE ALL TEMPLATES
echo ============================================================
echo.

cd /d "%~dp0"

python create_templates_complete.py
if errorlevel 1 (
    py create_templates_complete.py
)

echo.
echo Template sudah dibuat di folder:
echo   - templates/word/
echo   - templates/excel/
echo.
pause
