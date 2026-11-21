# -*- coding: utf-8 -*-
"""
QR-Code-Generator-MK2
Desktop-Programm (PySide6) zum Erzeugen moeglichst grober QR-Codes.
"Grob" heisst: kleinstmoegliche QR-Version (= wenigste Module), damit jedes
Modul bei gleicher Ausgabegroesse so gross wie moeglich wird.

Export: SVG (Vektor) und Bitmap (BMP / PNG).
"""

import os
import sys

import segno
from PySide6.QtCore import Qt, QTimer, QRectF, QMimeData
from PySide6.QtGui import (
    QColor, QPainter, QImage, QIcon, QPixmap, QFont, QAction, QKeySequence,
    QDragEnterEvent, QDropEvent,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPlainTextEdit, QPushButton,
    QComboBox, QSpinBox, QCheckBox, QHBoxLayout, QVBoxLayout, QGridLayout,
    QFrame, QFileDialog, QColorDialog, QMessageBox, QSizePolicy,
)

APP_NAME = "QR-Code-Generator-MK2"
APP_VERSION = "2.0.0"

# --------------------------------------------------------------------------
# Farben im Stil der Dashboards (dunkel, Lattice-artig, Amber/Teal-Akzente)
# --------------------------------------------------------------------------
C_BG = "#0b0f14"
C_PANEL = "#111821"
C_PANEL2 = "#16202b"
C_BORDER = "#223041"
C_TEXT = "#d5dde6"
C_MUTED = "#7b8a9a"
C_AMBER = "#ffb000"
C_TEAL = "#19c3b4"
C_RED = "#ff5c5c"

STYLESHEET = f"""
* {{
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
    color: {C_TEXT};
}}
QMainWindow, QWidget#root {{ background: {C_BG}; }}
QFrame#panel {{
    background: {C_PANEL};
    border: 1px solid {C_BORDER};
    border-radius: 6px;
}}
QFrame#header {{
    background: {C_PANEL};
    border: none;
    border-bottom: 1px solid {C_BORDER};
}}
QLabel#title {{
    font-family: "Consolas", "Cascadia Mono", monospace;
    font-size: 13pt; font-weight: 700; letter-spacing: 2px; color: {C_TEXT};
}}
QLabel#titleAccent {{
    font-family: "Consolas", "Cascadia Mono", monospace;
    font-size: 13pt; font-weight: 700; letter-spacing: 2px; color: {C_AMBER};
}}
QLabel#version {{
    font-family: "Consolas", monospace; color: {C_MUTED}; font-size: 9pt;
}}
QLabel#section {{
    font-family: "Consolas", "Cascadia Mono", monospace;
    font-size: 8.5pt; font-weight: 700; letter-spacing: 2px; color: {C_AMBER};
    padding-bottom: 2px;
}}
QLabel#muted {{ color: {C_MUTED}; font-size: 9pt; }}
QLabel#statKey {{
    font-family: "Consolas", monospace; color: {C_MUTED}; font-size: 9pt;
}}
QLabel#statVal {{
    font-family: "Consolas", monospace; color: {C_TEAL}; font-size: 10pt;
    font-weight: 700;
}}
QLabel#pill {{
    font-family: "Consolas", monospace; font-size: 8.5pt; font-weight: 700;
    letter-spacing: 1px; border-radius: 9px; padding: 2px 10px;
}}
QPlainTextEdit {{
    background: {C_BG};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 6px;
    font-family: "Consolas", "Cascadia Mono", monospace;
    font-size: 10.5pt;
    selection-background-color: {C_TEAL};
    selection-color: {C_BG};
}}
QPlainTextEdit:focus {{ border: 1px solid {C_TEAL}; }}
QComboBox, QSpinBox {{
    background: {C_BG};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 20px;
}}
QSpinBox {{ padding: 4px 4px; }}
QSpinBox::up-button, QSpinBox::down-button {{
    subcontrol-origin: border; width: 18px; background: {C_PANEL2};
    border-left: 1px solid {C_BORDER};
}}
QSpinBox::up-button {{ subcontrol-position: top right; border-top-right-radius: 4px; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; border-bottom-right-radius: 4px; }}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{ background: {C_BORDER}; }}
QSpinBox::up-arrow {{ image: url(ARROW_UP); width: 8px; height: 8px; }}
QSpinBox::down-arrow {{ image: url(ARROW_DOWN); width: 8px; height: 8px; }}
QComboBox::down-arrow {{ image: url(ARROW_DOWN); width: 9px; height: 9px; }}
QComboBox:hover, QSpinBox:hover {{ border: 1px solid {C_TEAL}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {C_PANEL2};
    border: 1px solid {C_BORDER};
    selection-background-color: {C_TEAL};
    selection-color: {C_BG};
    outline: 0;
}}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {C_BORDER}; border-radius: 3px; background: {C_BG};
}}
QCheckBox::indicator:checked {{ background: {C_TEAL}; border: 1px solid {C_TEAL}; }}
QPushButton {{
    background: {C_PANEL2};
    border: 1px solid {C_BORDER};
    border-radius: 4px;
    padding: 7px 14px;
    font-family: "Consolas", monospace;
    font-weight: 700;
    letter-spacing: 1px;
}}
QPushButton:hover {{ border: 1px solid {C_TEAL}; color: {C_TEAL}; }}
QPushButton:pressed {{ background: {C_BG}; }}
QPushButton:disabled {{ color: {C_MUTED}; border: 1px solid {C_BORDER}; }}
QPushButton#primary {{
    background: {C_AMBER}; color: {C_BG}; border: 1px solid {C_AMBER};
}}
QPushButton#primary:hover {{ background: #ffc640; color: {C_BG}; }}
QPushButton#primary:disabled {{
    background: {C_PANEL2}; color: {C_MUTED}; border: 1px solid {C_BORDER};
}}
QPushButton#swatch {{ padding: 4px; min-width: 60px; }}
QToolTip {{
    background: {C_PANEL2}; color: {C_TEXT}; border: 1px solid {C_TEAL};
    padding: 4px;
}}
QMessageBox {{ background: {C_PANEL}; }}
"""

# Zeichen, die im QR-Alphanumerik-Modus erlaubt sind
ALNUM_CHARS = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")


def _arrow_files():
    """Erzeugt kleine Pfeil-PNGs (Teal) im Temp-Ordner fuer das Stylesheet."""
    import tempfile
    from PySide6.QtGui import QPolygonF
    from PySide6.QtCore import QPointF
    d = os.path.join(tempfile.gettempdir(), "qr_generator_mk2")
    os.makedirs(d, exist_ok=True)
    paths = {}
    for name, pts in (("up", [(1, 11), (8, 4), (15, 11)]),
                      ("down", [(1, 5), (8, 12), (15, 5)])):
        img = QImage(16, 16, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(C_TEAL))
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))
        p.end()
        fp = os.path.join(d, f"arrow_{name}.png")
        img.save(fp, "PNG")
        paths[name] = fp.replace("\\", "/")
    return paths


def build_stylesheet():
    a = _arrow_files()
    return STYLESHEET.replace("ARROW_UP", a["up"]).replace("ARROW_DOWN", a["down"])


def resource_path(rel):
    """Pfad zu gebuendelten Dateien (PyInstaller --onefile oder Quellcode)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def build_qr(text, error, allow_micro, boost):
    """Erzeugt den kleinstmoeglichen (= grobsten) QR-Code fuer den Text."""
    return segno.make(
        text,
        error=error,
        micro=allow_micro,      # False -> nur normale QR-Codes
        boost_error=boost,      # False -> ECC nicht automatisch anheben
    )


def mode_label(qr):
    m = (qr.mode or "").lower()
    return {
        "numeric": "Numerisch",
        "alphanumeric": "Alphanumerisch",
        "byte": "Byte",
        "kanji": "Kanji",
        "hanzi": "Hanzi",
    }.get(m, qr.mode or "-")


# --------------------------------------------------------------------------
# Vorschau-Widget
# --------------------------------------------------------------------------
class QRPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.matrix = None
        self.border = 4
        self.dark = QColor("#000000")
        self.light = QColor("#ffffff")
        self.message = "Text eingeben …"
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_qr(self, matrix, border, dark, light):
        self.matrix = matrix
        self.border = border
        self.dark = QColor(dark)
        self.light = QColor(light)
        self.update()

    def clear(self, message):
        self.matrix = None
        self.message = message
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.fillRect(self.rect(), QColor(C_BG))

        # Raster im Hintergrund (Dashboard-Look)
        p.setPen(QColor("#121a23"))
        step = 24
        for x in range(0, self.width(), step):
            p.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            p.drawLine(0, y, self.width(), y)

        if not self.matrix:
            p.setPen(QColor(C_MUTED))
            f = QFont("Consolas", 11)
            p.setFont(f)
            p.drawText(self.rect(), Qt.AlignCenter, self.message)
            return

        n = len(self.matrix)
        total = n + 2 * self.border
        avail = min(self.width(), self.height()) - 40
        mod = max(1, avail // total)           # ganzzahlige Modulgroesse -> scharf
        size = mod * total
        ox = (self.width() - size) // 2
        oy = (self.height() - size) // 2

        p.fillRect(ox, oy, size, size, self.light)
        p.setPen(Qt.NoPen)
        p.setBrush(self.dark)
        for r, row in enumerate(self.matrix):
            y = oy + (r + self.border) * mod
            c = 0
            while c < n:
                if row[c]:
                    start = c
                    while c < n and row[c]:
                        c += 1
                    p.drawRect(ox + (start + self.border) * mod, y,
                               (c - start) * mod, mod)
                else:
                    c += 1

        # Eckmarkierungen in Teal
        p.setBrush(Qt.NoBrush)
        pen = p.pen()
        p.setPen(QColor(C_TEAL))
        L = 14
        x0, y0, x1, y1 = ox - 6, oy - 6, ox + size + 5, oy + size + 5
        for (ax, ay, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1),
                                 (x0, y1, 1, -1), (x1, y1, -1, -1)):
            p.drawLine(ax, ay, ax + dx * L, ay)
            p.drawLine(ax, ay, ax, ay + dy * L)
        p.setPen(pen)

        # Modulgroesse unten rechts
        p.setPen(QColor(C_MUTED))
        p.setFont(QFont("Consolas", 8))
        p.drawText(self.rect().adjusted(0, 0, -8, -4),
                   Qt.AlignRight | Qt.AlignBottom,
                   f"{n}×{n} Module · Vorschau {mod}px/Modul")


# --------------------------------------------------------------------------
# Kleine Helfer
# --------------------------------------------------------------------------
def section(text):
    lbl = QLabel(text.upper())
    lbl.setObjectName("section")
    return lbl


def panel():
    f = QFrame()
    f.setObjectName("panel")
    return f


def make_app_icon():
    """Icon zur Laufzeit (falls keine .ico gebuendelt ist)."""
    ico = resource_path(os.path.join("assets", "icon.ico"))
    if os.path.exists(ico):
        return QIcon(ico)
    pm = QPixmap(64, 64)
    pm.fill(QColor(C_BG))
    p = QPainter(pm)
    qr = segno.make("MK2", error="L", micro=False)
    m = [list(r) for r in qr.matrix]
    s = 64 / len(m)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(C_AMBER))
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                p.drawRect(QRectF(c * s, r * s, s, s))
    p.end()
    return QIcon(pm)


# --------------------------------------------------------------------------
# Hauptfenster
# --------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}")
        self.setWindowIcon(make_app_icon())
        self.resize(1080, 700)
        self.setAcceptDrops(True)

        self.qr = None
        self.used_text = ""
        self.dark_color = "#000000"
        self.light_color = "#ffffff"

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(14, 14, 14, 14)
        body.setSpacing(14)
        outer.addLayout(body, 1)

        body.addWidget(self._build_left(), 0)
        body.addWidget(self._build_right(), 1)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(150)
        self.timer.timeout.connect(self.regenerate)

        # Shortcuts
        act_svg = QAction(self, shortcut=QKeySequence("Ctrl+S"))
        act_svg.triggered.connect(self.save_svg)
        self.addAction(act_svg)
        act_bmp = QAction(self, shortcut=QKeySequence("Ctrl+B"))
        act_bmp.triggered.connect(self.save_bitmap)
        self.addAction(act_bmp)

        self.regenerate()

    # ---------------- Header ----------------
    def _build_header(self):
        h = QFrame()
        h.setObjectName("header")
        h.setFixedHeight(54)
        lay = QHBoxLayout(h)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(6)

        mark = QLabel("▮")
        mark.setStyleSheet(f"color:{C_AMBER}; font-size:16pt;")
        lay.addWidget(mark)
        t1 = QLabel("QR-CODE")
        t1.setObjectName("titleAccent")
        t2 = QLabel("GENERATOR")
        t2.setObjectName("title")
        t3 = QLabel("MK2")
        t3.setObjectName("titleAccent")
        for w in (t1, t2, t3):
            lay.addWidget(w)
        v = QLabel(f"  v{APP_VERSION}")
        v.setObjectName("version")
        lay.addWidget(v)
        lay.addStretch(1)

        self.pill = QLabel("BEREIT")
        self.pill.setObjectName("pill")
        self.pill.setFixedHeight(22)
        lay.addWidget(self.pill, 0, Qt.AlignVCenter)
        self._set_pill("BEREIT", C_TEAL)
        return h

    def _set_pill(self, text, color):
        self.pill.setText(text)
        self.pill.setStyleSheet(
            f"color:{color}; border:1px solid {color}; background:{C_BG};")

    # ---------------- Linke Spalte ----------------
    def _build_left(self):
        col = QWidget()
        col.setFixedWidth(380)
        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(14)

        # --- Eingabe
        p1 = panel()
        l1 = QVBoxLayout(p1)
        l1.setContentsMargins(14, 12, 14, 14)
        l1.addWidget(section("Eingabe"))
        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText("Text, URL, WLAN-Daten … (auch .txt per Drag & Drop)")
        self.edit.setPlainText("https://example.com")
        self.edit.textChanged.connect(lambda: self.timer.start())
        self.edit.setMinimumHeight(110)
        l1.addWidget(self.edit)
        self.lbl_chars = QLabel("")
        self.lbl_chars.setObjectName("muted")
        l1.addWidget(self.lbl_chars)
        v.addWidget(p1, 1)

        # --- Optionen
        p2 = panel()
        g = QGridLayout(p2)
        g.setContentsMargins(14, 12, 14, 14)
        g.setHorizontalSpacing(10)
        g.setVerticalSpacing(8)
        g.addWidget(section("Optionen"), 0, 0, 1, 2)

        g.addWidget(QLabel("Fehlerkorrektur"), 1, 0)
        self.cb_err = QComboBox()
        self.cb_err.addItem("L – 7 %  (grobster Code)", "L")
        self.cb_err.addItem("M – 15 %", "M")
        self.cb_err.addItem("Q – 25 %", "Q")
        self.cb_err.addItem("H – 30 %", "H")
        self.cb_err.setToolTip("Je niedriger die Fehlerkorrektur, desto weniger Module –\n"
                               "L ergibt den grobsten QR-Code.")
        self.cb_err.currentIndexChanged.connect(self.regenerate)
        g.addWidget(self.cb_err, 1, 1)

        self.chk_boost = QCheckBox("Freie Kapazität für Fehlerkorrektur nutzen")
        self.chk_boost.setToolTip("Hebt die Fehlerkorrektur an, wenn das ohne\n"
                                  "größere Version möglich ist (Code bleibt gleich grob).")
        self.chk_boost.setChecked(True)
        self.chk_boost.toggled.connect(self.regenerate)
        g.addWidget(self.chk_boost, 2, 0, 1, 2)

        self.chk_micro = QCheckBox("Micro-QR erlauben (noch gröber)")
        self.chk_micro.setToolTip("Micro-QR-Codes haben nur einen Suchmarker und\n"
                                  "11–17 Module, werden aber von vielen Handy-Apps\n"
                                  "NICHT gelesen.")
        self.chk_micro.toggled.connect(self.regenerate)
        g.addWidget(self.chk_micro, 3, 0, 1, 2)

        self.chk_upper = QCheckBox("In Großbuchstaben umwandeln (Alphanumerik)")
        self.chk_upper.setToolTip(
            "Großbuchstaben, Ziffern und  $%*+-./: werden im kompakteren\n"
            "Alphanumerik-Modus kodiert – oft eine Version kleiner.\n"
            "ACHTUNG: verändert den Inhalt! Bei URLs nur sinnvoll, wenn\n"
            "der Pfad nicht groß-/kleinschreibungsabhängig ist.")
        self.chk_upper.toggled.connect(self.regenerate)
        g.addWidget(self.chk_upper, 4, 0, 1, 2)

        g.addWidget(QLabel("Ruhezone (Module)"), 5, 0)
        self.sp_border = QSpinBox()
        self.sp_border.setRange(0, 20)
        self.sp_border.setValue(4)
        self.sp_border.setToolTip("Weißer Rand um den Code. Norm: 4 (Micro-QR: 2).")
        self.sp_border.valueChanged.connect(self.regenerate)
        g.addWidget(self.sp_border, 5, 1)

        g.addWidget(QLabel("Pixel pro Modul"), 6, 0)
        self.sp_scale = QSpinBox()
        self.sp_scale.setRange(1, 200)
        self.sp_scale.setValue(20)
        self.sp_scale.setToolTip("Gilt für Bitmap-Export und als Größe im SVG.")
        self.sp_scale.valueChanged.connect(self._update_stats)
        g.addWidget(self.sp_scale, 6, 1)

        g.addWidget(QLabel("Farben"), 7, 0)
        crow = QHBoxLayout()
        self.btn_dark = QPushButton()
        self.btn_dark.setObjectName("swatch")
        self.btn_dark.clicked.connect(lambda: self._pick_color("dark"))
        self.btn_light = QPushButton()
        self.btn_light.setObjectName("swatch")
        self.btn_light.clicked.connect(lambda: self._pick_color("light"))
        crow.addWidget(self.btn_dark)
        crow.addWidget(self.btn_light)
        g.addLayout(crow, 7, 1)
        self._update_swatches()
        v.addWidget(p2, 0)

        # --- Export
        p3 = panel()
        l3 = QVBoxLayout(p3)
        l3.setContentsMargins(14, 12, 14, 14)
        l3.setSpacing(8)
        l3.addWidget(section("Export"))
        self.btn_svg = QPushButton("SVG SPEICHERN   (Strg+S)")
        self.btn_svg.setObjectName("primary")
        self.btn_svg.clicked.connect(self.save_svg)
        self.btn_bmp = QPushButton("BITMAP SPEICHERN   (Strg+B)")
        self.btn_bmp.setObjectName("primary")
        self.btn_bmp.clicked.connect(self.save_bitmap)
        self.btn_clip = QPushButton("BILD IN ZWISCHENABLAGE")
        self.btn_clip.clicked.connect(self.copy_clipboard)
        l3.addWidget(self.btn_svg)
        l3.addWidget(self.btn_bmp)
        l3.addWidget(self.btn_clip)
        v.addWidget(p3, 0)
        return col

    # ---------------- Rechte Spalte ----------------
    def _build_right(self):
        col = QWidget()
        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(14)

        pv = panel()
        lv = QVBoxLayout(pv)
        lv.setContentsMargins(14, 12, 14, 14)
        lv.addWidget(section("Vorschau"))
        self.preview = QRPreview()
        lv.addWidget(self.preview, 1)
        v.addWidget(pv, 1)

        ps = panel()
        gs = QGridLayout(ps)
        gs.setContentsMargins(14, 12, 14, 14)
        gs.setHorizontalSpacing(18)
        gs.setVerticalSpacing(4)
        gs.addWidget(section("Status"), 0, 0, 1, 6)
        self.stats = {}
        keys = [("version", "VERSION"), ("modules", "MODULE"),
                ("ecc", "FEHLERKORR."), ("mode", "MODUS"),
                ("size", "BITMAP"), ("fill", "RUHEZONE")]
        for i, (k, label) in enumerate(keys):
            r, c = divmod(i, 3)
            kl = QLabel(label)
            kl.setObjectName("statKey")
            vl = QLabel("-")
            vl.setObjectName("statVal")
            gs.addWidget(kl, 1 + r * 2, c * 2)
            gs.addWidget(vl, 2 + r * 2, c * 2)
            self.stats[k] = vl
        self.lbl_hint = QLabel("")
        self.lbl_hint.setObjectName("muted")
        self.lbl_hint.setWordWrap(True)
        gs.addWidget(self.lbl_hint, 5, 0, 1, 6)
        v.addWidget(ps, 0)
        return col

    # ---------------- Logik ----------------
    def _effective_text(self):
        t = self.edit.toPlainText()
        if self.chk_upper.isChecked():
            t = t.upper()
        return t

    def regenerate(self):
        text = self._effective_text()
        raw = self.edit.toPlainText()
        self.lbl_chars.setText(f"{len(raw)} Zeichen · {len(raw.encode('utf-8'))} Bytes (UTF-8)")

        if not text:
            self.qr = None
            self.preview.clear("Text eingeben …")
            self._set_pill("LEER", C_MUTED)
            self._set_export_enabled(False)
            self._update_stats()
            return
        try:
            self.qr = build_qr(text, self.cb_err.currentData(),
                               self.chk_micro.isChecked(),
                               self.chk_boost.isChecked())
            self.used_text = text
        except Exception as exc:  # zu lang o. ae.
            self.qr = None
            self.preview.clear("Text zu lang für einen QR-Code")
            self._set_pill("FEHLER", C_RED)
            self._set_export_enabled(False)
            self._update_stats()
            self.lbl_hint.setText(str(exc))
            return

        matrix = [list(r) for r in self.qr.matrix]
        self.preview.set_qr(matrix, self.sp_border.value(),
                            self.dark_color, self.light_color)
        self._set_pill("MICRO-QR" if self.qr.is_micro else "QR OK", C_TEAL
                       if not self.qr.is_micro else C_AMBER)
        self._set_export_enabled(True)
        self._update_stats()

    def _set_export_enabled(self, on):
        for b in (self.btn_svg, self.btn_bmp, self.btn_clip):
            b.setEnabled(on)

    def _update_stats(self):
        s = self.stats
        if not self.qr:
            for k in s:
                s[k].setText("-")
            if self.edit.toPlainText() == "":
                self.lbl_hint.setText("")
            return
        qr = self.qr
        n = qr.symbol_size(border=0)[0]
        b = self.sp_border.value()
        px = (n + 2 * b) * self.sp_scale.value()
        s["version"].setText(str(qr.designator.split("-")[0]))
        s["modules"].setText(f"{n} × {n}")
        s["ecc"].setText(qr.error or "–")
        s["mode"].setText(mode_label(qr))
        s["size"].setText(f"{px} × {px} px")
        s["fill"].setText(f"{b} Module")

        hint = []
        if not qr.is_micro and not self.chk_upper.isChecked():
            up = self.edit.toPlainText().upper()
            if up and all(ch in ALNUM_CHARS for ch in up):
                try:
                    q2 = build_qr(up, self.cb_err.currentData(),
                                  self.chk_micro.isChecked(),
                                  self.chk_boost.isChecked())
                    n2 = q2.symbol_size(border=0)[0]
                    if n2 < n:
                        hint.append(f"Tipp: In Großbuchstaben wäre der Code nur "
                                    f"{n2}×{n2} statt {n}×{n} Module groß.")
                except Exception:
                    pass
        if qr.is_micro:
            hint.append("Hinweis: Micro-QR wird von vielen Handy-Kameras nicht erkannt.")
        if b < (2 if qr.is_micro else 4):
            hint.append("Hinweis: Ruhezone kleiner als Norm – Lesbarkeit kann leiden.")
        self.lbl_hint.setText("  ".join(hint))

    def _pick_color(self, which):
        cur = QColor(self.dark_color if which == "dark" else self.light_color)
        col = QColorDialog.getColor(cur, self, "Farbe wählen")
        if not col.isValid():
            return
        if which == "dark":
            self.dark_color = col.name()
        else:
            self.light_color = col.name()
        self._update_swatches()
        self.regenerate()

    def _update_swatches(self):
        for btn, col, name in ((self.btn_dark, self.dark_color, "Modul"),
                               (self.btn_light, self.light_color, "Grund")):
            fg = "#000000" if QColor(col).lightness() > 128 else "#ffffff"
            btn.setText(name)
            btn.setStyleSheet(f"background:{col}; color:{fg};")

    # ---------------- Export ----------------
    def _default_name(self, ext):
        base = "".join(ch if ch.isalnum() else "_" for ch in self.used_text[:30]).strip("_")
        return f"QR_{base or 'Code'}.{ext}"

    def render_image(self):
        matrix = [list(r) for r in self.qr.matrix]
        n = len(matrix)
        b = self.sp_border.value()
        sc = self.sp_scale.value()
        size = (n + 2 * b) * sc
        img = QImage(size, size, QImage.Format_RGB32)
        img.fill(QColor(self.light_color))
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing, False)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self.dark_color))
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                if val:
                    p.drawRect((c + b) * sc, (r + b) * sc, sc, sc)
        p.end()
        return img

    def save_svg(self):
        if not self.qr:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "SVG speichern", self._default_name("svg"), "SVG-Datei (*.svg)")
        if not path:
            return
        if not path.lower().endswith(".svg"):
            path += ".svg"
        try:
            self.qr.save(path, kind="svg", scale=self.sp_scale.value(),
                         border=self.sp_border.value(),
                         dark=self.dark_color, light=self.light_color,
                         xmldecl=True, svgns=True, nl=True,
                         title=None)
            self._flash("SVG GESPEICHERT")
        except Exception as exc:
            QMessageBox.critical(self, "Fehler", f"SVG konnte nicht gespeichert werden:\n{exc}")

    def save_bitmap(self):
        if not self.qr:
            return
        path, flt = QFileDialog.getSaveFileName(
            self, "Bitmap speichern", self._default_name("bmp"),
            "Bitmap (*.bmp);;PNG-Bild (*.png)")
        if not path:
            return
        low = path.lower()
        if not (low.endswith(".bmp") or low.endswith(".png")):
            path += ".png" if "png" in flt.lower() else ".bmp"
        fmt = "PNG" if path.lower().endswith(".png") else "BMP"
        img = self.render_image()
        if img.save(path, fmt):
            self._flash(f"{fmt} GESPEICHERT")
        else:
            QMessageBox.critical(self, "Fehler", "Bitmap konnte nicht gespeichert werden.")

    def copy_clipboard(self):
        if not self.qr:
            return
        QApplication.clipboard().setImage(self.render_image())
        self._flash("KOPIERT")

    def _flash(self, text):
        self._set_pill(text, C_AMBER)
        QTimer.singleShot(1800, self.regenerate)

    # ---------------- Drag & Drop ----------------
    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls() or e.mimeData().hasText():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent):
        md: QMimeData = e.mimeData()
        if md.hasUrls():
            for url in md.urls():
                fp = url.toLocalFile()
                if fp and os.path.isfile(fp):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                            self.edit.setPlainText(fh.read().rstrip("\r\n"))
                    except Exception as exc:
                        QMessageBox.warning(self, "Fehler", str(exc))
                    return
        if md.hasText():
            self.edit.setPlainText(md.text())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setStyleSheet(build_stylesheet())
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
