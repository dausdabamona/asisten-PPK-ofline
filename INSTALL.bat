@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0 - INSTALL DEPENDENCIES
echo ============================================================
echo.

REM Check Python
echo Mencari Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python 3.8+ dari https://www.python.org/
    echo.
    echo PENTING: Centang "Add Python to PATH" saat install!
    pause
    exit /b 1
)

echo Python ditemukan.
echo.
echo Installing dependencies...
echo.

REM Try Method 1: python -m pip (most reliable)
echo Metode 1: python -m pip...
python -m pip install PySide6 python-docx openpyxl
if not errorlevel 1 (
    goto SUCCESS
)

REM Try Method 2: pip directly
echo.
echo Metode 2: pip langsung...
pip install PySide6 python-docx openpyxl
if not errorlevel 1 (
    goto SUCCESS
)

REM Try Method 3: pip3
echo.
echo Metode 3: pip3...
pip3 install PySide6 python-docx openpyxl
if not errorlevel 1 (
    goto SUCCESS
)

REM Try Method 4: py -m pip
echo.
echo Metode 4: py -m pip...
py -m pip install PySide6 python-docx openpyxl
if not errorlevel 1 (
    goto SUCCESS
)

REM All methods failed
echo.
echo ============================================================
echo ERROR: Tidak dapat menginstall dependencies!
echo ============================================================
echo.
echo Coba jalankan manual di Command Prompt:
echo   python -m pip install PySide6 python-docx openpyxl
echo.
echo Atau install pip dulu:
echo   python -m ensurepip --upgrade
echo.
pause
exit /b 1

:SUCCESS
echo.
echo ============================================================
echo INSTALASI BERHASIL!
echo ============================================================
echo.
echo Langkah selanjutnya:
echo   1. Jalankan SETUP_DATA.bat (opsional, untuk data contoh)
echo   2. Jalankan START.bat untuk membuka aplikasi
echo.
pause
