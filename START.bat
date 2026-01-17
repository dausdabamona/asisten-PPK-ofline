@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0
echo Template-Driven Procurement Workflow System
echo ============================================================
echo.
echo Starting application...
echo.

cd /d "%~dp0"

REM Try python first
python main.py
if not errorlevel 1 (
    exit /b 0
)

REM Try py launcher
py main.py
if not errorlevel 1 (
    exit /b 0
)

echo.
echo ============================================================
echo ERROR: Aplikasi gagal dijalankan!
echo ============================================================
echo.
echo Kemungkinan penyebab:
echo   1. Python belum terinstall
echo   2. Dependencies belum diinstall (jalankan INSTALL.bat)
echo.
echo Coba jalankan manual:
echo   python main.py
echo.
pause
