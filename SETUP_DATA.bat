@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0 - SETUP SAMPLE DATA
echo ============================================================
echo.

cd /d "%~dp0"

python setup_data.py
if errorlevel 1 (
    py setup_data.py
)

pause
