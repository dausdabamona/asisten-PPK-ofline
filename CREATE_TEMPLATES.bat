@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0 - CREATE SAMPLE TEMPLATES
echo ============================================================
echo.

cd /d "%~dp0"

python create_templates.py
if errorlevel 1 (
    py create_templates.py
)

echo.
pause
