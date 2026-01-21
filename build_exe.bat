@echo off
REM PPK DOCUMENT FACTORY v3.0 - Build EXE (Windows)
REM ================================================
REM Script untuk membuat file executable (.exe)
REM
REM Cara penggunaan:
REM   Double-click file ini atau jalankan dari Command Prompt

echo ============================================================
echo PPK DOCUMENT FACTORY - BUILD EXE
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python dari https://python.org
    pause
    exit /b 1
)

echo [OK] Python ditemukan
echo.

REM Install dependencies
echo === Menginstall dependensi ===
pip install -r requirements.txt
pip install pyinstaller

echo.
echo === Memulai build ===
python build_exe.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build gagal!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo BUILD SELESAI!
echo ============================================================
echo.
echo File executable ada di folder: dist\PPK_Document_Factory
echo.
pause
