@echo off
REM ============================================================
REM  QR-Code-Generator-MK2 Offline-Build-Kit v1.0.0
REM  Schritt 3 von 3 - auf dem Windows-10-PC ausfuehren, NACHDEM
REM  Schritt 2 (Pakete installieren) einmal erfolgreich lief.
REM
REM  Quelle (in dieser Reihenfolge):
REM   1. genau EINE .zip in diesem Ordner -> wird nach "projekt"
REM      entpackt (z. B. "Download ZIP" von GitHub)
REM   2. keine .zip, aber das Kit liegt noch im Projektordner
REM      -> der uebergeordnete Ordner wird direkt verwendet
REM
REM  Baut mit PyInstaller (aus der venv von Schritt 2)
REM     qr_generator.py -> QR-Code-Generator-MK2-v<Version>-windows.exe
REM  genau wie der GitHub-Actions-Workflow. Komplett offline.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"
set "KITDIR=%~dp0"
set "MARKER=QR-Code-Generator-MK2"

echo.
echo === QR-Code-Generator-MK2 Offline-Build-Kit v1.0.0 ===
echo === Schritt 3: exe bauen ===
echo.

if not exist "venv\Scripts\pyinstaller.exe" (
    echo [FEHLER] venv mit PyInstaller wurde nicht gefunden.
    echo Bitte zuerst "2_win10_pakete_installieren.bat" erfolgreich
    echo ausfuehren ^(im selben Ordner wie dieses Skript^).
    pause
    exit /b 1
)

REM --- .zip-Datei in diesem Ordner suchen ---
set "ZIPFILE="
set /a ZIPCOUNT=0
for %%f in ("*.zip") do (
    set "ZIPFILE=%%f"
    set /a ZIPCOUNT+=1
)

if %ZIPCOUNT% GTR 1 (
    echo [FEHLER] Es liegen mehrere .zip-Dateien in diesem Ordner:
    for %%f in ("*.zip") do echo    - %%f
    echo Bitte nur die gewuenschte Projekt-.zip-Datei hier ablegen.
    pause
    exit /b 1
)

set "APPPY="
if %ZIPCOUNT%==1 (
    echo Gefundenes Archiv: !ZIPFILE!
    echo.
    echo [1/3] Entpacke !ZIPFILE! nach "projekt" ...
    if exist "projekt" rmdir /s /q "projekt"
    mkdir "projekt"
    powershell -NoProfile -Command "Expand-Archive -LiteralPath '!ZIPFILE!' -DestinationPath 'projekt' -Force"
    if errorlevel 1 (
        echo [FEHLER] Entpacken fehlgeschlagen.
        pause
        exit /b 1
    )
    REM --- qr_generator.py suchen (egal wie tief im Archiv) ---
    REM     Es zaehlt nur eine Datei, die "QR-Code-Generator-MK2" enthaelt.
    for /f "delims=" %%f in ('dir /s /b "projekt\qr_generator.py" 2^>nul') do (
        findstr /c:"!MARKER!" "%%f" >nul 2>nul && if not defined APPPY set "APPPY=%%f"
    )
    if not defined APPPY (
        echo.
        echo [FEHLER] In der .zip-Datei wurde keine qr_generator.py des
        echo QR-Code-Generator-MK2 gefunden. Gefundener Inhalt:
        dir /b "projekt"
        pause
        exit /b 1
    )
) else (
    REM --- keine .zip: liegt das Kit im Projektordner? ---
    for %%d in ("%~dp0..") do set "PARENTDIR=%%~fd"
    if exist "!PARENTDIR!\qr_generator.py" (
        findstr /c:"!MARKER!" "!PARENTDIR!\qr_generator.py" >nul 2>nul && set "APPPY=!PARENTDIR!\qr_generator.py"
    )
    if not defined APPPY (
        echo [FEHLER] Keine .zip-Datei in diesem Ordner gefunden und das Kit
        echo liegt auch nicht in einem QR-Code-Generator-MK2-Projektordner.
        echo Bitte die QR-Code-Generator-MK2-.zip in diesen Ordner legen
        echo ^(neben dieses Skript^) und erneut ausfuehren.
        pause
        exit /b 1
    )
    echo Keine .zip gefunden - verwende den Projektordner:
    echo    !PARENTDIR!
    echo.
    echo [1/3] Entpacken nicht noetig.
)
for %%d in ("!APPPY!") do set "APPDIR=%%~dpd"
echo Programmdatei: !APPPY!

REM --- Versionsnummer aus APP_VERSION lesen ---
set "APPVER="
for /f "usebackq delims=" %%v in (`venv\Scripts\python.exe -c "import re,sys;m=re.search(r'^APP_VERSION\s*=\s*[\x22\x27]([0-9A-Za-z.\-]+)',open(sys.argv[1],encoding='utf-8').read(),re.M);print(m.group(1) if m else '')" "!APPPY!"`) do set "APPVER=%%v"
if not defined APPVER (
    echo [WARNUNG] Keine APP_VERSION in qr_generator.py gefunden - nutze "0.0.0".
    set "APPVER=0.0.0"
)
set "EXEBASE=QR-Code-Generator-MK2"
set "EXENAME=!EXEBASE!-v!APPVER!-windows"
echo Version: !APPVER!

REM --- Programmsymbol (wird auch zur Laufzeit als Fenster-Icon genutzt) ---
set "ICONOPT="
if exist "!APPDIR!assets\icon.ico" (
    set ICONOPT=--icon "!APPDIR!assets\icon.ico" --add-data "!APPDIR!assets\icon.ico;assets"
    echo Symbol: assets\icon.ico
) else (
    echo [HINWEIS] assets\icon.ico nicht gefunden - exe bekommt das Standardsymbol.
)

echo.
echo [2/3] Pruefe, ob PySide6 und segno in der venv vorhanden sind ...
venv\Scripts\python.exe -c "import PySide6.QtWidgets, segno" >nul 2>nul
if errorlevel 1 (
    echo [FEHLER] PySide6 oder segno fehlt in der venv. Bitte Schritt 2 erneut ausfuehren.
    pause
    exit /b 1
)
echo    PySide6 + segno ok

if not exist "fertige_exe" mkdir "fertige_exe"
if exist "fertige_exe\!EXENAME!.exe" del /q "fertige_exe\!EXENAME!.exe"

echo.
echo [3/3] Baue !EXENAME!.exe aus qr_generator.py ...
echo       ^(dauert ca. 1-3 Minuten^)
REM Gebaut wird im Projektordner (wie im GitHub-Workflow), Ausgabe
REM und Zwischendateien landen im Kit-Ordner.
pushd "!APPDIR!"
"!KITDIR!venv\Scripts\pyinstaller.exe" --noconfirm --clean --onefile --windowed ^
    --name "!EXEBASE!" !ICONOPT! ^
    --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml ^
    --exclude-module tkinter ^
    --distpath "!KITDIR!build_tmp\dist" --workpath "!KITDIR!build_tmp\work" ^
    --specpath "!KITDIR!build_tmp" "!APPPY!"
set "PYIERR=!errorlevel!"
popd
if not "!PYIERR!"=="0" (
    echo [FEHLER] Build von !EXENAME!.exe fehlgeschlagen.
    pause
    exit /b 1
)
if not exist "build_tmp\dist\!EXEBASE!.exe" (
    echo [FEHLER] PyInstaller lief durch, aber die exe fehlt.
    pause
    exit /b 1
)
move /y "build_tmp\dist\!EXEBASE!.exe" "fertige_exe\!EXENAME!.exe" >nul

REM Aufraeumen der PyInstaller-Zwischendateien (build/, .spec)
if exist "build_tmp" rmdir /s /q "build_tmp"

echo.
echo ============================================================
echo  FERTIG!
echo.
echo  Im Ordner
echo    %~dp0fertige_exe
echo  liegt jetzt:
dir /b "fertige_exe"
echo.
echo  Die exe ist eine einzelne Datei ohne Installation - einfach
echo  per Doppelklick starten. Es werden keine Dateien daneben angelegt.
echo ============================================================
echo.
pause
