# QR-Code-Generator-MK2 — Windows-exe offline bauen: Mac lädt, Win10 baut

**Offline-Build-Kit v1.0.0** (für QR-Code-Generator-MK2 ab v2.0.0)

Drei Skripte, drei Schritte. Python 3.11 (64-Bit) ist auf dem
Windows-10-PC bereits installiert — dieses Kit kümmert sich nur noch um
die Pakete und den eigentlichen exe-Build. Das Ergebnis ist dieselbe
Datei, die sonst GitHub Actions baut:
`QR-Code-Generator-MK2-v<Version>-windows.exe`.

```
offline_build_kit/
├── 1_mac_pakete_herunterladen.sh      <- läuft auf dem Mac (mit Internet)
├── 2_win10_pakete_installieren.bat    <- läuft auf dem Win10-PC
├── 3_win10_exe_aus_zip_bauen.bat      <- läuft auf dem Win10-PC
└── ANLEITUNG.md                       <- diese Datei
```

Das Kit liegt im Repo im Ordner `offline_build_kit/`. Es gibt zwei Wege:

- **Weg A – Kit im Projektordner lassen (einfachster Weg):** Den ganzen
  Projektordner (entpackte Repo-ZIP) kopieren. Schritt 3 erkennt, dass
  das Kit im Projektordner liegt, und baut direkt daraus — keine
  zusätzliche `.zip` nötig.
- **Weg B – Kit separat:** Nur den Ordner `offline_build_kit` kopieren
  und die Projekt-`.zip` (z. B. „Download ZIP" von GitHub) daneben legen.

---

## Schritt 1 — auf dem Mac

1. Den Projektordner (Weg A) oder den Kit-Ordner samt Projekt-`.zip`
   (Weg B) z. B. auf den Schreibtisch legen.
2. Terminal öffnen, in den Kit-Ordner wechseln und das Skript starten:
   ```bash
   cd ~/Desktop/QR-Code-Generator-MK2/offline_build_kit
   chmod +x 1_mac_pakete_herunterladen.sh
   ./1_mac_pakete_herunterladen.sh
   ```
3. Es entstehen
   - der Ordner **`offline_pakete`** mit den `.whl`-Dateien für
     `PySide6-Essentials`, `shiboken6`, `segno`, `pyinstaller` und deren
     Abhängigkeiten — passend für **Windows 64-Bit / Python 3.11**,
     egal welches Python auf dem Mac läuft (auf dem Mac wird nichts
     installiert). Größe ca. 90–100 MB, vor allem durch PySide6,
   - eine Prüfsummen-Datei `offline_pakete/SHA256SUMS.txt`,
   - die Datei **`paketliste.txt`**.

   > Die Paketversionen kommen aus der `requirements.txt` des Projekts
   > (aus der `.zip` bzw. aus `../requirements.txt`, wenn das Kit im
   > Projektordner liegt). PyInstaller ist fest auf `6.22.3` gesetzt —
   > genau wie im GitHub-Actions-Workflow.

**Danach auf den Windows-10-PC kopieren** (USB-Stick, Kabel — egal wie):
- Weg A: den kompletten Projektordner
- Weg B: den kompletten Kit-Ordner (inkl. `offline_pakete` und
  `paketliste.txt`) und **daneben** die Projekt-`.zip`

---

## Schritt 2 — auf dem Windows-10-PC: Pakete installieren

1. Doppelklick auf **`2_win10_pakete_installieren.bat`**.
2. Das Skript
   - sucht ein passendes Python 3.11 (64-Bit): erst `python`, sonst
     den Python-Launcher `py -3.11`,
   - prüft per SHA256, dass beim Kopieren keine Paketdatei beschädigt
     wurde,
   - legt die virtuelle Umgebung `venv` an und installiert alle Pakete
     **ausschließlich** aus `offline_pakete` (`--no-index`, kein
     Internet).
3. Am Ende erscheint `FERTIG.`.

---

## Schritt 3 — auf dem Windows-10-PC: exe bauen

1. Doppelklick auf **`3_win10_exe_aus_zip_bauen.bat`**.
2. Das Skript
   - nimmt **eine** `.zip` im Kit-Ordner (entpackt nach `projekt`) —
     oder, wenn keine `.zip` da ist, direkt den übergeordneten
     Projektordner,
   - sucht darin die `qr_generator.py` des QR-Code-Generator-MK2
     (egal in welchem Unterordner),
   - liest die Versionsnummer aus `APP_VERSION`,
   - baut mit PyInstaller genau wie der GitHub-Workflow
     (`--onefile --windowed`, Symbol aus `assets/icon.ico`) die exe.
3. Ergebnis liegt in **`fertige_exe`**:
   ```
   fertige_exe/
   └── QR-Code-Generator-MK2-v2.0.1-windows.exe
   ```

**Neue Projektversion später bauen:** neue `.zip` gegen die alte
austauschen (bzw. den Projektordner aktualisieren) und
`3_win10_exe_aus_zip_bauen.bat` erneut starten. Schritt 1/2 müssen nicht
wiederholt werden, solange sich die `requirements.txt` nicht ändert.

---

## exe benutzen

Die exe ist **eine einzige Datei** ohne Installation und ohne
nebenliegende Dateien — sie kann allein an jeden beliebigen Ort kopiert
werden. Per Doppelklick starten — es öffnet sich direkt das
Programmfenster (kein Konsolenfenster, kein Browser, kein Netzwerk-Port).
Das Programm legt keine Konfigurations- oder Hilfsdateien an.

---

## Was dieses Kit nicht baut

- **macOS-App:** Eine Mac-App lässt sich nur auf einem Mac bauen,
  nicht unter Windows.

---

## Fehlerbehebung

- **„Kein passendes Python 3.11 (64-Bit) gefunden"** (Schritt 2) →
  `python --version` bzw. `py --list` prüfen. Die Pakete aus Schritt 1
  passen nur zu 3.11 / 64-Bit. Ein anderes Python? Dann im Mac-Skript
  oben `PY_VER="3.11"` anpassen und Schritt 1 wiederholen.
- **„DEFEKT"/„FEHLT" bei der Paketprüfung** → Kopiervorgang
  unvollständig; `offline_pakete` erneut auf den PC kopieren.
- **„venv mit PyInstaller wurde nicht gefunden"** (Schritt 3) → erst
  Schritt 2 erfolgreich durchlaufen lassen, im selben Ordner.
- **„mehrere .zip-Dateien"** → höchstens eine `.zip` neben die Skripte
  legen. Das Kit selbst nicht als `.zip` daneben liegen lassen.
- **„keine qr_generator.py des QR-Code-Generator-MK2 gefunden"** →
  falsches Archiv; das Skript zeigt den gefundenen Inhalt an.
- **Windows Defender meldet die neue exe** → normal bei frisch
  gebauten, unsignierten PyInstaller-exe-Dateien: „Trotzdem ausführen"
  bzw. Ausnahme eintragen.
- **Schritt 2 meldet `pefile` oder `pywin32-ctypes` fehlt** → ist im
  Mac-Skript bereits berücksichtigt (beide werden explizit mitgeladen).
  Bei erneutem Auftreten Schritt 1 mit diesem Skript wiederholen.
