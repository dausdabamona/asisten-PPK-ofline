@echo off
echo ============================================================
echo PPK DOCUMENT FACTORY v3.0 - DEBUG MODE
echo ============================================================
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.
echo Checking Python...
python --version
echo.
echo Checking installed packages...
python -m pip list | findstr -i "pyside6 docx openpyxl"
echo.
echo ============================================================
echo Running application...
echo ============================================================
echo.

python main.py

echo.
echo ============================================================
echo Exit code: %ERRORLEVEL%
echo ============================================================
echo.
echo Jika ada error, copy pesan di atas.
echo.
pause
