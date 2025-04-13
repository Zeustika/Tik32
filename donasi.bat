@echo off
cls
color 0A
echo ================================================================
echo          TikTok Live Gift Tracking System
echo ================================================================
echo [INFO] IP: 192.168.0.116
echo ================================================================
echo.

:: Input username TikTok
set /p username=  Masukkan Username TikTok Anda : 
if "%username%"=="" (
    echo [ERROR] Username TikTok wajib diisi!
    pause
    exit /b
)

:: Konfirmasi username
echo ================================================================
echo [INFO] Username TikTok: %username%
echo ================================================================
echo.

:: Menjalankan skrip Python
echo [INFO] Menyiapkan koneksi ke TikTok Live...
python donasi.py %username%

if %ERRORLEVEL% NEQ 0 (
    echo ================================================================
    echo [ERROR] Terjadi kesalahan saat menjalankan skrip Python!
    echo [INFO] Pastikan Python terinstal dan semua dependensi sudah terpasang.
    echo ================================================================
) else (
    echo ================================================================
    echo [INFO] Skrip selesai dijalankan.
    echo ================================================================
)

pause
