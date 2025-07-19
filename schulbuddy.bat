@echo off
title SchulBuddy Docker Manager

:menu
cls
echo.
echo ===============================================
echo        🎓 SchulBuddy Docker Manager
echo ===============================================
echo.
echo [1] Setup - Umgebung konfigurieren
echo [2] Build - Docker Images bauen
echo [3] Start - Services starten
echo [4] Stop  - Services stoppen
echo [5] Logs  - Logs anzeigen
echo [6] Status - Service-Status
echo [7] Clean - Aufräumen
echo [8] Install - Komplette Installation
echo [9] Update - Auf neueste Version aktualisieren
echo [0] Exit
echo.
set /p choice="Wähle eine Option (0-9): "

if "%choice%"=="1" goto setup
if "%choice%"=="2" goto build
if "%choice%"=="3" goto start
if "%choice%"=="4" goto stop
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto status
if "%choice%"=="7" goto clean
if "%choice%"=="8" goto install
if "%choice%"=="9" goto update
if "%choice%"=="0" goto exit
goto menu

:setup
echo.
echo 🔧 Starte Setup...
powershell -ExecutionPolicy Bypass -File "scripts\setup-env.ps1"
pause
goto menu

:build
echo.
echo 🔨 Baue Docker Images...
docker-compose build --no-cache
pause
goto menu

:start
echo.
echo 🚀 Starte SchulBuddy...
docker-compose up -d
pause
goto menu

:stop
echo.
echo 🛑 Stoppe SchulBuddy...
docker-compose down
pause
goto menu

:logs
echo.
echo 📋 Zeige Logs... (Strg+C zum Beenden)
docker-compose logs -f schulbuddy
pause
goto menu

:status
echo.
echo 📊 Service-Status:
docker-compose ps
pause
goto menu

:clean
echo.
echo 🧹 Räume auf...
docker-compose down -v --rmi all
pause
goto menu

:install
echo.
echo 🚀 Starte komplette Installation...
call :setup
call :build
call :start
echo.
echo ✅ Installation abgeschlossen!
echo 🌐 Öffne http://localhost:5000 in deinem Browser
pause
goto menu

:update
echo.
echo 🔄 Update wird durchgeführt...
git pull
call :build
call :start
pause
goto menu

:exit
echo.
echo 👋 Auf Wiedersehen!
exit /b 0
