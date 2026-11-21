# QR-Code-Generator-MK1

**Version 1.0.0**

Eigenständiges Windows-Programm (keine Web-App) zum Erzeugen **möglichst grober QR-Codes** –
also mit so wenigen Modulen wie möglich, damit jedes einzelne Modul bei gleicher Druck-/Bildgröße
maximal groß wird. Export als **SVG** (Vektor) und als **Bitmap** (BMP oder PNG).

![Screenshot](docs/screenshot.png)

## Funktionen

- Text eingeben → QR-Code wird live erzeugt (auch `.txt`-Datei per Drag & Drop)
- Automatisch **kleinstmögliche QR-Version** und optimaler Kodierungsmodus (Numerisch / Alphanumerisch / Byte)
- Fehlerkorrektur wählbar – Standard **L (7 %)** ergibt den grobsten Code
- Option „Freie Kapazität für Fehlerkorrektur nutzen“: hebt die Fehlerkorrektur an, **ohne** den Code größer zu machen
- Option **Micro-QR** (11–17 Module, noch gröber – aber von vielen Handy-Apps nicht lesbar)
- Option **Großbuchstaben**: nutzt den kompakteren Alphanumerik-Modus (verändert den Inhalt!) –
  das Programm zeigt einen Tipp an, wenn das eine kleinere Version ergeben würde
- Ruhezone (Rand) und Pixel pro Modul einstellbar, Farben wählbar
- Export: **SVG** (`Strg+S`), **BMP/PNG** (`Strg+B`), Bild in die Zwischenablage
- Statusanzeige: Version, Modulanzahl, Fehlerkorrektur, Modus, Bitmap-Größe

## Download / Build

Der Build läuft automatisch über **GitHub Actions** (`.github/workflows/build-exe.yml`):

- Bei jedem Push auf `main`/`master` → ZIP als Artefakt unter *Actions*
- Bei einem Tag `v*` (z. B. `v1.0.0`) → zusätzlich GitHub-Release mit der ZIP

Die ZIP enthält `QR-Code-Generator-MK1.exe` (einzelne Datei, keine Installation nötig) und diese README.

## Lokal starten (Entwicklung)

```bash
pip install -r requirements.txt
python qr_generator.py
```

## Projektstruktur

```
QR-Code-Generator-MK1/
├─ .github/workflows/build-exe.yml   GitHub-Actions-Build (Windows-EXE + ZIP)
├─ assets/icon.ico                   Programm-Icon
├─ assets/icon.png
├─ docs/screenshot.png               Bild für die README
├─ qr_generator.py                   Programm (PySide6 + segno)
├─ requirements.txt
└─ README.md
```
