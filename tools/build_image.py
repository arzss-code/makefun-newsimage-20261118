#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
makefun-newsimage — infografis berita dunia, 18 November 2026
Digambar 100% deterministik dengan Pillow: tanpa jaringan, tanpa angka acak.
Hasil selalu PNG 1024x1024, di bawah 1 MiB.

Jalankan : python3 tools/build_image.py
Output   : /output/entry.png  (atau path file lain via env MAKEFUN_OUT)
Catatan  : entri yang dinilai adalah main.py, yang hanya menyalin entry.png
           ke $MAKEFUN_OUTPUT_DIR tanpa Pillow. Rebuild byte-identik
           bergantung pada font DejaVu/Liberation dan versi Pillow.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# ------------------------------------------------------------------ palet
BG       = (11, 14, 20)     # latar editorial gelap
PANEL    = (19, 25, 38)     # kartu panel kanan
PANEL_LN = (39, 47, 68)     # garis pemisah / bingkai
SLATE    = (56, 66, 92)     # batang chart yang tidak disorot
INK      = (240, 243, 248)  # teks utama
MUTED    = (150, 160, 178)  # teks sekunder
FAINT    = (96, 106, 126)   # teks tersier
RED      = (231, 76, 80)    # konflik / risiko tinggi
GOLD     = (245, 184, 65)   # diplomasi / waspada
GREEN    = (118, 185, 0)    # Nvidia / tenang
CYAN     = (88, 184, 226)   # teknologi / tekanan
VIOLET   = (158, 122, 236)  # hiburan

# ------------------------------------------------------------------ font
_FONT_DIRS = (
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
)


def _find(names):
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


_SANS = _find(("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"))
_BOLD = _find(("DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "ArialBold.ttf"))
if _SANS is None or _BOLD is None:
    raise SystemExit("error: font TTF tidak ditemukan; pasang DejaVu Sans atau Liberation Sans")

_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_BOLD if bold else _SANS, size)
    return _cache[key]


# --------------------------------------------------- util teks (anti-terpotong)
def wrap(draw, text, fnt, max_w):
    """Pecah teks jadi baris; tiap baris <= max_w piksel (diukur via textlength)."""
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            cand = word if not cur else cur + " " + word
            if draw.textlength(cand, font=fnt) <= max_w:
                cur = cand
                continue
            if cur:
                lines.append(cur)
                cur = ""
            # kata tunggal lebih lebar dari kolom: pecah per karakter
            while len(word) > 1 and draw.textlength(word, font=fnt) > max_w:
                cut = len(word) - 1
                while cut > 1 and draw.textlength(word[:cut], font=fnt) > max_w:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
        if cur:
            lines.append(cur)
    return lines


def limit_lines(draw, lines, n, fnt, max_w):
    """Batasi jumlah baris; baris terakhir diberi elipsis bila terpotong."""
    if len(lines) <= n:
        return lines
    lines = list(lines[:n])
    last = lines[-1]
    while draw.textlength(last + "…", font=fnt) > max_w and len(last) > 1:
        last = last[:-1]
    lines[-1] = last + "…"
    return lines


def fit_size(draw, text, start, max_w, bold=True, floor=20):
    """Kecilkan ukuran font sampai teks muat dalam max_w."""
    size = start
    while size > floor and draw.textlength(text, font=font(size, bold)) > max_w:
        size -= 2
    return size


def tracked(draw, xy, text, fnt, fill, track=2, anchor="lm"):
    """Tulis huruf per huruf dengan letter-spacing."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor=anchor)
        x += draw.textlength(ch, font=fnt) + track
    return x


# ------------------------------------------------------------------ konten
DATE_TXT = "RABU, 18 NOVEMBER 2026"
KICKER = "MAKEFUN NEWS • BRIEFING BERITA DUNIA"
SUBLINES = (
    "Diplomasi Asia, serangan di Laut Hitam, guncangan chip, "
    "dan satu tanggal yang dinanti para gamer."
)

STORIES = (
    {"tag": "01 · DIPLOMASI", "color": GOLD,
     "head": "Trump keliling Asia jelang KTT Xi–Putin",
     "body": "KTT Xi–Putin pekan ini di Beijing; tarif, chip, dan keamanan laut "
             "jadi taruhan utama lengkung diplomasi Asia."},
    {"tag": "02 · KONFLIK", "color": RED,
     "head": "Ukraina serang Jembatan Kerch",
     "body": "Drone laut dan rudal melumpuhkan lalu lintas jembatan; Moskow siap "
             "balasan, premi asuransi Laut Hitam melonjak."},
    {"tag": "03 · TEKNOLOGI", "color": GREEN,
     "head": "Nvidia tolak kembalinya Jensen Huang",
     "body": "Dewan direksi menolak skema kembalinya sang pendiri; gangguan "
             "teknologi global meluas ke bank dan maskapai."},
    {"tag": "04 · HIBURAN", "color": VIOLET,
     "head": "GTA VI akhirnya rilis Kamis ini",
     "body": "Rockstar pastikan 19 November hari-H; pre-order pecahkan rekor, "
             "distributor siagakan server tengah malam."},
)

AGENDA = (
    ("RABU, 18 NOV", "Pembukaan KTT Xi–Putin di Beijing", GOLD),
    ("KAMIS, 19 NOV", "GTA VI tayang perdana global", VIOLET),
    ("JUMAT, 20 NOV", "Sidang dewan direksi Nvidia", GREEN),
)

BARS = (("FY22", 27), ("FY23", 27), ("FY24", 61), ("FY25", 131), ("FY26", 215))

FEAR = 68  # indeks ketakutan global (0-100)

FLASHPOINTS = (
    ("Selat Taiwan", "KRITIS", RED),
    ("Jembatan Kerch", "KRITIS", RED),
    ("Selat Hormuz", "WASPADA", GOLD),
    ("Rantai pasokan chip", "TEKANAN", CYAN),
)


# ------------------------------------------------------------------ blok kiri
def chip(draw, xy, text, color):
    f = font(12, True)
    tw = draw.textlength(text, font=f)
    x, y = xy
    h = 24
    draw.rounded_rectangle([x, y, x + tw + 18, y + h], radius=12, outline=color, width=1)
    draw.text((x + 9, y + h / 2), text, font=f, fill=color, anchor="lm")
    return h + 10


def render_story(draw, y, s, dry=False):
    x, max_w = 48, 500
    yy = y
    if not dry:
        chip(draw, (x, yy), s["tag"], s["color"])
    yy += 34
    f = font(26, True)
    for ln in wrap(draw, s["head"], f, max_w):
        if not dry:
            draw.text((x, yy), ln, font=f, fill=INK)
        yy += 32
    yy += 6
    bf = font(16)
    for ln in limit_lines(draw, wrap(draw, s["body"], bf, max_w), 3, bf, max_w):
        if not dry:
            draw.text((x, yy), ln, font=bf, fill=MUTED)
        yy += 23
    return yy - y


def render_agenda(draw, y, dry=False):
    x, max_w = 48, 500
    yy = y
    if not dry:
        tracked(draw, (x, yy + 9), "AGENDA PEKAN INI", font(13, True), CYAN, 2)
    yy += 30
    for date, text, col in AGENDA:
        tf = font(14)
        lines = wrap(draw, text, tf, max_w - 138)
        row_h = max(30, len(lines) * 20 + 12)
        if not dry:
            cy = yy + row_h / 2
            draw.text((x, cy), date, font=font(14, True), fill=col, anchor="lm")
            for i, ln in enumerate(lines):
                draw.text((x + 138, cy + (i - (len(lines) - 1) / 2) * 20),
                          ln, font=tf, fill=MUTED, anchor="lm")
        yy += row_h
    return yy - y


def draw_left_column(draw):
    top, bottom = 196, 972
    blocks = [
        (lambda y, dr, s=s: render_story(draw, y, s, dr), None) for s in STORIES
    ]
    blocks.append((lambda y, dr: render_agenda(draw, y, dr), None))
    heights = [fn(0, True) for fn, _ in blocks]
    total = sum(heights)
    gap = max(16.0, (bottom - top - total) / (len(blocks) - 1))
    y = float(top)
    for i, (fn, _) in enumerate(blocks):
        fn(int(round(y)), False)
        y += heights[i]
        if i < len(blocks) - 1:
            mid = y + gap / 2
            draw.line((48, mid, 548, mid), fill=PANEL_LN, width=1)
            y += gap


# ------------------------------------------------------------------ panel kanan
def section_title(draw, y, left, right=""):
    draw.text((626, y), left, font=font(13, True), fill=INK, anchor="lm")
    if right:
        draw.text((950, y), right, font=font(11), fill=MUTED, anchor="rm")


def section_sep(draw, y):
    draw.line((626, y, 950, y), fill=PANEL_LN, width=1)


def draw_panel(draw):
    draw.rounded_rectangle([600, 176, 976, 976], radius=18,
                           fill=PANEL, outline=PANEL_LN, width=1)

    # kepala panel
    tracked(draw, (626, 210), "PANEL DATA", font(12, True), CYAN, 2)
    draw.text((950, 210), "18 NOV 2026", font=font(11), fill=FAINT, anchor="rm")
    section_sep(draw, 226)

    # --- A. bar chart pendapatan Nvidia ---
    section_title(draw, 252, "PENDAPATAN NVIDIA", "US$ miliar, tahun fiskal")
    base, max_h = 448, 118
    vmax = max(v for _, v in BARS)
    slot = (950 - 626) / len(BARS)
    for i, (lab, v) in enumerate(BARS):
        last = i == len(BARS) - 1
        bh = max(3.0, max_h * v / vmax)
        cx = 626 + slot * (i + 0.5)
        draw.rectangle([cx - 18, base - bh, cx + 18, base],
                       fill=GREEN if last else SLATE)
        draw.text((cx, base - bh - 8), str(v), font=font(12, True),
                  fill=GREEN if last else MUTED, anchor="ms")
        draw.text((cx, 460), lab, font=font(12, last),
                  fill=GREEN if last else MUTED, anchor="mm")
    draw.line((626, base, 950, base), fill=PANEL_LN, width=2)
    draw.text((626, 482), "*FY26 = proyeksi konsensus",
              font=font(10), fill=FAINT, anchor="lm")
    section_sep(draw, 506)

    # --- B. gauge indeks ketakutan ---
    section_title(draw, 524, "INDEKS KETAKUTAN GLOBAL", "skala 0–100")
    cx, cy, r = 788, 668, 82
    bbox = [cx - r, cy - r, cx + r, cy + r]
    for a0, a1, col in ((180, 252, GREEN), (252, 306, GOLD), (306, 360, RED)):
        draw.arc(bbox, a0, a1, fill=col, width=12)
    for deg in (180, 225, 270, 315, 360):  # tick 0/25/50/75/100
        a = math.radians(deg)
        x0, y0 = cx + 87 * math.cos(a), cy + 87 * math.sin(a)
        x1, y1 = cx + 93 * math.cos(a), cy + 93 * math.sin(a)
        draw.line((x0, y0, x1, y1), fill=FAINT, width=2)
    ang = 180 + 1.8 * FEAR
    nx, ny = cx + 58 * math.cos(math.radians(ang)), cy + 58 * math.sin(math.radians(ang))
    draw.line((cx, cy, nx, ny), fill=INK, width=4)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=INK)
    draw.text((cx, 698), str(FEAR), font=font(36, True), fill=INK, anchor="mm")
    draw.text((cx, 728), "+7 POIN PEKAN INI", font=font(11, True), fill=RED, anchor="mm")
    draw.text((698, 684), "0", font=font(10), fill=FAINT, anchor="mm")
    draw.text((878, 684), "100", font=font(10), fill=FAINT, anchor="mm")
    section_sep(draw, 744)

    # --- C. titik panas 24 jam ---
    section_title(draw, 762, "TITIK PANAS 24 JAM", "peringkat risiko")
    for i, (name, status, col) in enumerate(FLASHPOINTS):
        cyy = 788 + 44 * i + 22
        draw.ellipse([628, cyy - 4, 636, cyy + 4], fill=col)
        draw.text((648, cyy), name, font=font(15), fill=INK, anchor="lm")
        draw.text((950, cyy), status, font=font(11, True), fill=col, anchor="rm")
        if i < len(FLASHPOINTS) - 1:
            draw.line((626, cyy + 22, 950, cyy + 22), fill=PANEL_LN, width=1)


# ------------------------------------------------------------------ kanvas
def draw_header(draw):
    # strip warna atas
    for i, col in enumerate((GOLD, RED, GREEN, VIOLET)):
        draw.rectangle([i * 256, 0, (i + 1) * 256, 6], fill=col)

    draw.rectangle([48, 44, 58, 54], fill=RED)
    tracked(draw, (68, 49), KICKER, font(13, True), MUTED, 2)

    size = fit_size(draw, DATE_TXT, 64, 928)
    draw.text((48, 62), DATE_TXT, font=font(size, True), fill=INK)

    bf = font(17)
    for i, ln in enumerate(wrap(draw, SUBLINES, bf, 928)[:2]):
        draw.text((48, 146 + i * 22), ln, font=bf, fill=MUTED)

    draw.line((48, 176, 976, 176), fill=PANEL_LN, width=2)
    draw.rectangle([48, 174, 168, 178], fill=GOLD)


def draw_footer(draw):
    draw.line((48, 990, 976, 990), fill=PANEL_LN, width=1)
    draw.text((48, 1006), "MAKEFUN NEWS — INFOGRAFIS DETERMINISTIK • PYTHON + PIL • TANPA JARINGAN",
              font=font(11), fill=FAINT, anchor="lm")
    draw.text((976, 1006), "18 NOV 2026 • HAL 01/01", font=font(11, True),
              fill=FAINT, anchor="rm")


def output_path():
    p = os.environ.get("MAKEFUN_OUT") or "/output/entry.png"
    d = os.path.dirname(os.path.abspath(p))
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        d = os.path.join(os.getcwd(), "output")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, os.path.basename(p) or "entry.png")
    return p


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    draw_header(d)
    draw_left_column(d)
    draw_panel(d)
    draw_footer(d)

    path = output_path()
    img.save(path, "PNG", optimize=True)

    size = os.path.getsize(path)
    ok = size <= 1024 * 1024
    print(f"[{'ok' if ok else 'error'}] {path}")
    print(f"     resolusi : {img.size[0]}x{img.size[1]}")
    print(f"     ukuran   : {size:,} bytes ({size / 1024:.0f} KiB) — "
          f"{'DI BAWAH 1 MiB' if ok else 'MELEBIHI 1 MiB!'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
