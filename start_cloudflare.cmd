@echo off
title BloxyMe - Cloudflare Tunnel
cd /d "%~dp0"

echo [1/4] Lade cloudflared herunter...
if not exist cloudflared.exe (
    curl.exe -sL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -o cloudflared.exe
    if errorlevel 1 (
        echo Fehler beim Download. Manuell:
        echo https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
        pause & exit /b 1
    )
)
echo OK

echo [2/4] Installiere Abhaengigkeiten...
pip install -r requirements.txt >nul 2>&1
echo OK

echo [3/4] Starte lokalen Server...
start /B python server.py
timeout /t 3 /nobreak >nul
echo OK

echo [4/4] Starte Cloudflare Tunnel (Quick Tunnel)...
echo.
echo =====================================================
echo  Oeffentliche URL wird generiert...
echo  Teilen die URL mit anderen - die sehen dann deine
echo  Website live! Kein Server noetig.
echo =====================================================
echo.
echo  ^| Werbung ausblenden mit: cloudflared tunnel login
echo  ^| (Oder einfach so nutzen, ist gratis)
echo.
cloudflared tunnel --url http://localhost:5000
pause