#!/usr/bin/env python3
"""Render the committed still frames of the field from the same engine as assets/field.js.

Outputs (in assets/): social.png, footer-strip.png, footer-strip-dark.png.
(The favicon is the logo monogram, assets/favicon.svg, not a field frame.)
Same rule, rain, density, 40 warm-up generations and mulberry32 PRNG as field.js, so a seed
gives the same grid in the browser and here (`--check SEED` prints the grid hash to compare).

Deps: Python 3.9+, Pillow (pip install pillow, in a venv). Colors and the field tokens are read from
assets/tokens.css, the tagline from the home hero in index.qmd,
fonts (TTF, Fira Mono Medium) from tools/plots/fonts/ (copied there by tools/sync-ds.sh) or --fonts.
Usage: python tools/still_frames.py [--fonts DIR] [--check SEED]
"""
import argparse, hashlib, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
GENERATIONS = 40   # warm-up generations of a still frame; FIELD.generations in assets/field.js
M32 = 0xFFFFFFFF


def field_tokens():
    """The `field` tokens, read from assets/tokens.css (generated from tokens.json), so the frames
    follow a design-system change after tools/sync-ds.sh without edits here."""
    css = (ASSETS / "tokens.css").read_text()
    f = dict(re.findall(r"--field-([a-z-]+):\s*([^;]+);", css))
    m = re.fullmatch(r"B(\d+)/S(\d+)", f["rule"].strip())
    num = lambda k: float(re.match(r"[\d.]+", f[k].strip()).group(0))
    return ({int(c) for c in m.group(1)}, {int(c) for c in m.group(2)},
            int(num("rain-every")), int(num("rain-size")), num("density"), int(num("cell")))


B, S, RAIN_EVERY, RAIN_SIZE, DENSITY, CELL = field_tokens()


def tagline():
    """The home hero's tagline (index.qmd), so the social card and the hero read the same."""
    m = re.search(r'class="ng-field__tag">([^<]+)<', (ROOT / "index.qmd").read_text(encoding="utf-8"))
    if not m:
        sys.exit("no ng-field__tag in index.qmd")
    return m.group(1).strip().upper()   # .ng-field__tag is label style, set in uppercase


def imul(a, b):
    return (a * b) & M32


def rng(seed):
    """mulberry32, bit-for-bit the JS version (all values kept as unsigned 32-bit)."""
    s = seed & M32

    def nxt():
        nonlocal s
        s = (s + 0x6D2B79F5) & M32
        t = imul(s ^ (s >> 15), 1 | s)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return nxt


class Engine:
    def __init__(self, W, H, seed):
        self.W, self.H, self.rng, self.gen = W, H, rng(seed), 0
        self.cells = [1 if self.rng() < DENSITY else 0 for _ in range(W * H)]

    def counts(self):
        W, H, c = self.W, self.H, self.cells
        out = [0] * (W * H)
        for y in range(H):
            rows = [((y + d) % H) * W for d in (-1, 0, 1)]
            for x in range(W):
                xs = ((x - 1) % W, x, (x + 1) % W)
                out[y * W + x] = sum(c[r + xx] for r in rows for xx in xs) - c[y * W + x]
        return out

    def step(self):
        k, c = self.counts(), self.cells
        self.cells = [(1 if k[i] in S else 0) if c[i] else (1 if k[i] in B else 0) for i in range(len(c))]
        self.gen += 1
        if RAIN_EVERY and self.gen % RAIN_EVERY == 0:
            W, H, half = self.W, self.H, RAIN_SIZE // 2
            rx, ry = int(self.rng() * W), int(self.rng() * H)
            for py in range(-half, half):
                for px in range(-half, half):
                    self.cells[((ry + py) % H) * W + (rx + px) % W] = 1 if self.rng() < 0.5 else 0


def frame(W, H, seed):
    """Neighbour counts (0..8) of a frozen frame: the Field with live=false."""
    e = Engine(W, H, seed)
    for _ in range(GENERATIONS):
        e.step()
    return e, e.counts()


def steps():
    css = (ASSETS / "tokens.css").read_text()
    out = {}
    for theme, sel in (("light", r":root\s*\{"), ("dark", r'\[data-theme="dark"\]\s*\{')):
        block = re.search(sel + r"(.*?)\}", css, re.S).group(1)
        out[theme] = [re.search(r"--step-%d:\s*(#[0-9a-fA-F]{6})" % i, block).group(1).lower() for i in range(9)]
        out[theme + "-muted"] = re.search(r"--ink-muted:\s*(#[0-9a-fA-F]{6})", block).group(1)
    return out


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def paint(counts, W, H, cell, pal, size, x0=0, y0=0):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", size, hexrgb(pal[0]))
    d = ImageDraw.Draw(img)
    for y in range(size[1] // cell + 1):
        for x in range(size[0] // cell + 1):
            k = counts[((y + y0) % H) * W + (x + x0) % W]
            if k:
                d.rectangle([x * cell, y * cell, x * cell + cell - 1, y * cell + cell - 1], fill=hexrgb(pal[k]))
    return img


def spaced(d, xy, text, font, tracking, fill):
    """Draw text with CSS-style letter-spacing (Pillow has none); returns the advance width."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x - xy[0] - tracking


def social(pal, muted_hex, fonts):
    from PIL import ImageDraw, ImageFont
    # 1200x630, light, field-cell at 2x (16px), seed 7 (the home hero's seed). Panel per .ng-field__panel at 2x.
    cell = 2 * CELL
    W, H = -(-1200 // cell), -(-630 // cell)
    _, k = frame(W, H, 7)
    img = paint(k, W, H, cell, pal, (1200, 630))
    d = ImageDraw.Draw(img)
    mono = str(Path(fonts) / "FiraMono-Medium.ttf")
    name_f, tag_f = ImageFont.truetype(mono, 88), ImageFont.truetype(mono, 24)   # display 44/48, label 12/16, at 2x
    name, tag = "Natalie Gill", tagline()
    nw = sum(name_f.getlength(c) for c in name) - 0.88 * (len(name) - 1)
    tw = sum(tag_f.getlength(c) for c in tag) + 1.44 * (len(tag) - 1)
    px, py = 32, 24                                   # space-4 / space-3 at 2x
    pw, ph = int(max(nw, tw)) + 2 * px, 2 * py + 96 + 8 + 32
    left, bottom = 32, 630 - 32                       # space-4 from the corner, at 2x
    top = bottom - ph
    d.rectangle([left, top, left + pw - 1, bottom - 1], fill=hexrgb(pal[0]), outline=hexrgb(pal[2]), width=2)  # line, 1px at 2x
    ink, muted = hexrgb(pal[8]), hexrgb(muted_hex)
    asc = lambda f, lh: (lh - (f.getmetrics()[0] + f.getmetrics()[1])) / 2
    spaced(d, (left + px, top + py + asc(name_f, 96)), name, name_f, -0.88, ink)
    spaced(d, (left + px, top + py + 96 + 8 + asc(tag_f, 32)), tag, tag_f, 1.44, muted)
    img.save(ASSETS / "social.png", optimize=True)


def footer(pals):
    # 960x24 at field-cell (8px): rows 6-8 (a lighter band) of a 960x480 frame (120x60 cells), seed 7.
    # The strip is the full width of the torus, so site.css repeats it horizontally without a seam.
    W, H, row = 960 // CELL, 480 // CELL, 6
    _, k = frame(W, H, 7)
    for theme, name in (("light", "footer-strip.png"), ("dark", "footer-strip-dark.png")):
        paint(k, W, H, CELL, pals[theme], (960, 3 * CELL), 0, row).save(ASSETS / name, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fonts", default=str(ROOT / "tools/plots/fonts"), help="folder with FiraMono-Medium.ttf")
    ap.add_argument("--check", type=int, metavar="SEED", help="print sha256 of a 120x60 grid after 40 generations and exit")
    a = ap.parse_args()
    if a.check is not None:
        e, _ = frame(120, 60, a.check)
        print(hashlib.sha256(bytes(e.cells)).hexdigest(), sum(e.cells) / len(e.cells))
        return
    if not (Path(a.fonts) / "FiraMono-Medium.ttf").exists():
        sys.exit("FiraMono-Medium.ttf not found in %s (run tools/sync-ds.sh or pass --fonts)" % a.fonts)
    pal = steps()
    social(pal["light"], pal["light-muted"], a.fonts)
    footer(pal)
    print("wrote social.png, footer-strip.png, footer-strip-dark.png to", ASSETS)


if __name__ == "__main__":
    main()
