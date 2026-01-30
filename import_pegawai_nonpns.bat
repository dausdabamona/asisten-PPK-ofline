@echo off
REM Script untuk import data pegawai Non-PNS
REM =============================================

echo.
echo ============================================================
echo IMPORT DATA PEGAWAI NON-PNS
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu
    pause
    exit /b 1
)

echo [INFO] Menjalankan import pegawai Non-PNS...
echo.

REM Run the import script
python import_pegawai_nonpns.py

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Import selesai!
    echo ============================================================
    echo.
) else (
    echo.
    echo ============================================================
    echo [ERROR] Import gagal!
    echo ============================================================
    echo.
)

pause
