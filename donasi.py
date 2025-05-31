@echo off
cls
color 0A
echo ================================================================
echo TikTok Live Gift Tracking System - WiFi Scanner
echo ================================================================
echo.

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python tidak terinstal atau tidak ada di PATH!
    echo [INFO] Silakan install Python terlebih dahulu.
    pause
    exit /b
)

echo [INFO] Mencari perangkat ESP32 di jaringan WiFi...
echo ================================================================
python wifi_scanner.py

if %ERRORLEVEL% NEQ 0 (
    echo ================================================================
    echo [ERROR] Gagal menjalankan WiFi scanner!
    echo [INFO] Melanjutkan dengan input manual...
    echo ================================================================
    goto MANUAL_INPUT
)

if exist "selected_esp32.tmp" (
    set /p ESP32_IP=<selected_esp32.tmp
    del selected_esp32.tmp
    echo [INFO] ESP32 terpilih: %ESP32_IP%
) else (
    echo [INFO] Tidak ada ESP32 yang dipilih, menggunakan input manual...
    goto MANUAL_INPUT
)

goto USERNAME_INPUT

:MANUAL_INPUT
set /p ESP32_IP= Masukkan Alamat IP ESP32 Anda : 
if "%ESP32_IP%"=="" (
    echo [ERROR] Alamat IP ESP32 wajib diisi!
    pause
    exit /b
)

:USERNAME_INPUT
echo ================================================================
echo [INFO] IP ESP32: %ESP32_IP%
echo ================================================================
echo.

set /p username= Masukkan Username TikTok Anda : 
if "%username%"=="" (
    echo [ERROR] Username TikTok wajib diisi!
    pause
    exit /b
)

echo ================================================================
echo [INFO] Username TikTok: %username%
echo ================================================================
echo.

echo [INFO] Testing koneksi ke ESP32...
python -c "import requests; response = requests.get('http://%ESP32_IP%', timeout=5); print('[INFO] ESP32 dapat diakses!') if response.status_code == 200 else print('[WARNING] ESP32 mungkin tidak merespon dengan baik')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Tidak dapat menguji koneksi ke ESP32, melanjutkan...
)

echo ================================================================
echo [INFO] Starting TikTok Live Gift Tracking...
echo ================================================================
python donasi.py %username% %ESP32_IP%

if %ERRORLEVEL% NEQ 0 (
    echo ================================================================
    echo [ERROR] Terjadi kesalahan saat menjalankan skrip Python!
    echo [INFO] Pastikan Python terinstal dan semua dependensi sudah terpasang.
    echo [INFO] Install dependensi dengan: pip install requests rich TikTokLive
    echo ================================================================
) else (
    echo ================================================================
    echo [INFO] Skrip selesai dijalankan.
    echo ================================================================
)

pause
