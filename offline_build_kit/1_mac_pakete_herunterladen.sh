#!/bin/bash
# ============================================================
#  QR-Code-Generator-MK2 Offline-Build-Kit v1.0.0
#  Schritt 1 von 3 - auf dem MAC mit Internetverbindung ausfuehren.
#
#  Laedt alle fuer den Windows-Build benoetigten Python-Pakete
#  (PySide6-Essentials, segno, pyinstaller + Abhaengigkeiten)
#  als fertige .whl-Dateien fuer 64-Bit-Windows / Python 3.11
#  herunter. Auf dem Mac selbst wird nichts installiert.
#
#  Ergebnis liegt im Ordner "offline_pakete" daneben.
#  Danach: diesen ganzen Ordner (+ ggf. die Projekt-.zip)
#  per USB-Stick/AirDrop/Kabel auf den Win10-PC kopieren.
# ============================================================

set -e
cd "$(dirname "$0")"

KIT_VERSION="1.0.0"
# Python-Version des Windows-10-PCs (Major.Minor)
PY_VER="3.11"
PY_TAG="${PY_VER/./}"            # 3.11 -> 311

# Standardwerte (wie im GitHub-Actions-Build / requirements.txt)
DEFAULT_REQS="PySide6-Essentials==6.12.0
segno==1.6.6"
DEFAULT_PYINSTALLER="pyinstaller==6.22.3"

# Kennung, an der die richtige Programmdatei erkannt wird
MARKER="QR-Code-Generator-MK2"

echo
echo "=== QR-Code-Generator-MK2 Offline-Build-Kit v${KIT_VERSION} ==="
echo "=== Schritt 1: Pakete fuer Windows 10 / Python ${PY_VER} herunterladen ==="
echo

# Python3 finden (nur als Download-Werkzeug, Version egal)
PYTHON=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        PYTHON="$cand"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[FEHLER] Es wurde kein Python auf diesem Mac gefunden."
    echo "Bitte einmalig installieren, z. B. mit:  brew install python"
    echo "(oder von https://www.python.org/downloads/macos/)"
    exit 1
fi
echo "Verwende: $($PYTHON --version) ($PYTHON)"

# ------------------------------------------------------------
# Paketliste bestimmen (Reihenfolge):
#  1. Projekt-.zip in diesem Ordner -> requirements.txt neben
#     qr_generator.py aus der .zip
#  2. Kit liegt noch im Repo-Ordner -> ../requirements.txt
#  3. Standardliste
# ------------------------------------------------------------
PROJ_REQS=""
for z in *.zip; do
    [ -f "$z" ] || continue
    APP_IN_ZIP=$(unzip -Z1 "$z" 2>/dev/null | grep -E '(^|/)qr_generator\.py$' | head -n 1 || true)
    [ -n "$APP_IN_ZIP" ] || continue
    REQ_IN_ZIP="$(dirname "$APP_IN_ZIP")/requirements.txt"
    REQ_IN_ZIP="${REQ_IN_ZIP#./}"
    PROJ_REQS=$(unzip -p "$z" "$REQ_IN_ZIP" 2>/dev/null | tr -d '\r' | sed 's/#.*//' | grep -v '^[[:space:]]*$' || true)
    if [ -n "$PROJ_REQS" ]; then
        echo "Projekt-Archiv gefunden: $z  -> nutze dessen requirements.txt"
    fi
    break
done
if [ -z "$PROJ_REQS" ] && [ -f "../qr_generator.py" ] && [ -f "../requirements.txt" ] \
        && grep -q "$MARKER" "../qr_generator.py"; then
    PROJ_REQS=$(tr -d '\r' < ../requirements.txt | sed 's/#.*//' | grep -v '^[[:space:]]*$' || true)
    [ -n "$PROJ_REQS" ] && echo "Kit liegt im Projektordner -> nutze ../requirements.txt"
fi
if [ -z "$PROJ_REQS" ]; then
    PROJ_REQS="$DEFAULT_REQS"
    echo "Keine requirements.txt des Projekts gefunden - nutze Standardliste"
fi

REQ_FILE="paketliste.txt"
{
    echo "$PROJ_REQS"
    echo "$DEFAULT_PYINSTALLER"
} > "$REQ_FILE"
echo "Paketliste ($REQ_FILE):"
sed 's/^/   /' "$REQ_FILE"

rm -rf offline_pakete
mkdir -p offline_pakete
echo "$PY_VER" > offline_pakete/python_version.txt

echo
echo "Aktualisiere pip (falls moeglich)..."
"$PYTHON" -m pip install --upgrade pip --quiet 2>/dev/null \
    || echo "   (pip-Aktualisierung uebersprungen - kein Problem)"

# WICHTIG: "pip download --platform win_amd64" waehlt zwar korrekt
# Windows-Wheels aus, wertet bedingte Abhaengigkeiten (z. B.
# "sys_platform == 'win32'") aber anhand DIESES Macs aus.
#  - PyInstaller braucht unter Windows "pefile" und "pywin32-ctypes"
# Deshalb werden diese hier explizit ergaenzt.
cp "$REQ_FILE" offline_pakete_reqs_wheel.txt
{
    echo "pefile>=2022.5.30"
    echo "pywin32-ctypes>=0.2.0"
} >> offline_pakete_reqs_wheel.txt

echo
echo "Lade fertige Wheels herunter (Ziel: Windows 64-Bit, Python ${PY_VER})..."
"$PYTHON" -m pip download -r offline_pakete_reqs_wheel.txt -d offline_pakete \
    --platform win_amd64 --python-version "$PY_TAG" --implementation cp --abi "cp$PY_TAG" \
    --only-binary=:all:
rm -f offline_pakete_reqs_wheel.txt

# Kontrolle: die wichtigsten Pakete muessen dabei sein
for pkg in pyside6_essentials shiboken6 segno pyinstaller pefile; do
    if ! ls offline_pakete/ | grep -iq "^${pkg}-.*\.whl$"; then
        echo "[FEHLER] Kein Wheel fuer '${pkg}' heruntergeladen."
        exit 1
    fi
done

# Pruefsummen fuer die Kontrolle auf dem Windows-PC
( cd offline_pakete && { shasum -a 256 *.whl > SHA256SUMS.txt 2>/dev/null \
    || sha256sum *.whl > SHA256SUMS.txt; } )

echo
echo "Heruntergeladen:"
ls -1 offline_pakete | sed 's/^/   /'
echo "Gesamtgroesse: $(du -sh offline_pakete | cut -f1)"

echo
echo "============================================================"
echo " FERTIG. Der Ordner 'offline_pakete' enthaelt jetzt alle"
echo " benoetigten .whl-Dateien fuer Windows/Python ${PY_VER}."
echo
echo " Naechster Schritt: kopiere den kompletten Ordner"
echo "   $(pwd)"
echo " (inkl. offline_pakete/, paketliste.txt,"
echo "  2_win10_pakete_installieren.bat, 3_win10_exe_aus_zip_bauen.bat)"
echo " sowie die QR-Code-Generator-MK2-.zip auf den Windows-10-PC,"
echo " z. B. per USB-Stick. Alternativ den ganzen Projektordner"
echo " (mit diesem Kit darin) kopieren - dann ist keine .zip noetig."
echo "============================================================"
echo
