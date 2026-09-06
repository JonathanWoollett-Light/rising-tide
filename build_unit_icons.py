"""Rebuild the Deep Ones / Star Spawn unit icons (three DDS sheets per sub-unit).

Procedurally drawn silhouettes (Pillow ImageDraw at SS-x supersampling, LANCZOS downscale),
shaded to match the vanilla / OWB divisions_large icons, written as uncompressed A8R8G8B8 DDS
(Pillow .save() with NO pixel_format kwarg - the same header class as every reference icon).

Sheet classes (measured from vanilla + OWB):
  divisions_large  152x42 = 2 frames of 76x42  frame 1 green shaded glyph, frame 2 NATO box
  divisions_small   60x12 = 2 frames of 30x12  frame 1 WHITE shaded glyph, frame 2 NATO box
  texticons         60x12 = 2 frames of 30x12  frame 1 green shaded glyph, frame 2 NATO box

Run from anywhere:  python build_unit_icons.py            (writes the six DDS files)
                    python build_unit_icons.py --preview  (also writes event_images/unit_icons/preview_final.png)
                    python build_unit_icons.py --preview --tag v3   (names it preview_v3.png instead)
Deterministic: running twice yields byte-identical DDS output.
"""
import argparse
import hashlib
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
MOD = ROOT / "mod_folder"
PREVIEW_DIR = ROOT / "event_images" / "unit_icons"
OWB = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196")

# --------------------------------------------------------------------------------------
# Shape / style parameters (everything tunable lives here)
# --------------------------------------------------------------------------------------
SS = 8  # supersampling factor for every raster step

# Output sheets: frame size, glyph fit box (px, in the frame), palette, detail level, rim width (px),
# drop shadow (dx px, dy px, blur px, opacity), NATO box class.
# detail: 2 = every cut line (eye, gills, grooves), 1 = major lines, 0 = bare silhouette (12 px sheets)
SHEETS = {
    # large: 1 px clear above the glyph and 5 px below so the drop shadow fades out inside the frame
    "large": dict(frame=(76, 42), glyph_box=(17, 3, 61, 37), palette="green", detail=2, rim=1.6,
                  shadow=(1.0, 1.5, 1.2, 0.70), box="large"),
    # 12 px sheets: rows 1..10 only, so the silhouette never sits flush with the frame edge
    "onmap": dict(frame=(30, 12), glyph_box=(6, 1, 24, 11), palette="white", detail=0, rim=0.8,
                  shadow=(0.5, 1.0, 0.8, 0.70), box="small"),
    "text": dict(frame=(30, 12), glyph_box=(6, 1, 24, 11), palette="green", detail=0, rim=0.8,
                 shadow=(0.5, 1.0, 0.8, 0.70), box="small"),
}
FILES = {  # sub-unit -> sheet class -> path relative to mod_folder
    "mltd_deep_ones": {
        "large": "gfx/interface/counters/divisions_large/unit_mltd_deep_ones_icon.dds",
        "onmap": "gfx/interface/counters/divisions_small/onmap_unit_mltd_deep_ones_icon.dds",
        "text": "gfx/texticons/unit_mltd_deep_ones_icon_small.dds",
    },
    "mltd_star_spawn": {
        "large": "gfx/interface/counters/divisions_large/unit_mltd_star_spawn_icon.dds",
        "onmap": "gfx/interface/counters/divisions_small/onmap_unit_mltd_star_spawn_icon.dds",
        "text": "gfx/texticons/unit_mltd_star_spawn_icon_small.dds",
    },
}

# Glyph palettes. "green" is measured from vanilla unit_infantry_icon.dds frame 1
# (flat fill 73,106,73; top-left rim up to 172,191,172; bottom-right rim ~37,55,37).
PALETTES = {
    "green": dict(base=(73, 106, 73), light=(172, 191, 172), dark=(34, 52, 34), line=(14, 24, 14)),
    "white": dict(base=(192, 192, 192), light=(240, 240, 240), dark=(70, 70, 70), line=(28, 28, 28)),
}
GRADIENT_TOP, GRADIENT_BOTTOM = 1.14, 0.90  # vertical brightness ramp over the glyph's own height
RIM_LIGHT_WEIGHT, RIM_DARK_WEIGHT, CUT_WEIGHT, HL_WEIGHT = 0.9, 0.85, 0.85, 0.8

# NATO counter box (frame 2), measured from vanilla unit_infantry_icon.dds / unit_infantry_icon_small.dds:
# rect = (x0, y0, x1, y1) inclusive of the 1 px black border; top_row = first inner row value;
# grad = remaining inner rows top->bottom; left_add/right_sub = inner edge columns; shadow = right/bottom alphas
# (1, 2, 3 px outside the box); halo = the 1 px top/left alpha. Every halo/shadow row spans x0-1 .. x1+len(shadow)
# and every column y0-1 .. y1+len(shadow), and each line fades at both ends through taper[<base alpha>]
# (vanilla's exact values; the lines agree wherever they cross, e.g. the 93 column meets the 93 row at 62).
NATO_BOX = {
    "large": dict(rect=(14, 10, 60, 34), top_row=238, grad=(216, 150), left_add=20, right_sub=24, shadow=(93, 47, 15), halo=15,
                  taper={93: (10, 31, 62, 83), 47: (5, 15, 31, 42), 15: (2, 5, 10, 14)}),
    "small": dict(rect=(2, 0, 26, 11), top_row=227, grad=(222, 156), left_add=8, right_sub=12, shadow=(), halo=0, taper={}),
}
NATO_LINE = (36, 36, 36)  # symbol ink
NATO_LINE_W = {"large": 0.085, "small": 0.11}  # stroke width as a fraction of the inner box height

# detail-level sets a primitive is drawn at
ALL, HI, FULL, LOW = (0, 1, 2), (1, 2), (2,), (0,)


def _taper(pts, w0, w1):
    """Polyline -> polygon of a tapering stroke (widths in design units)."""
    pts = np.asarray(pts, float)
    n = len(pts)
    left, right = [], []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        d = b - a
        d = d / (np.hypot(*d) + 1e-9)
        nrm = np.array([-d[1], d[0]])
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append(pts[i] + nrm * w / 2)
        right.append(pts[i] - nrm * w / 2)
    return [tuple(p) for p in left + right[::-1]]


def _hand(palm, tips, thumb, web=0.5, palm_r=0.09):
    """Webbed clawed hand: palm disc + claw tips joined by webbing at `web` of each finger's length."""
    P = np.asarray(palm, float)
    tips = [np.asarray(t, float) for t in tips]
    pts = [P + (palm_r, palm_r * 0.9), P + (palm_r * 0.3, palm_r * 1.1), np.asarray(thumb, float)]
    prev = np.asarray(thumb, float)
    for t in tips:
        mid = (prev + t) / 2
        pts.append(P + web * (mid - P))
        pts.append(t)
        prev = t
    pts.append(P + (palm_r * 1.1, -palm_r * 0.2))
    return [tuple(p) for p in pts]


# ---- Deep One: hunched, gilled fish-man in left-facing profile, head tilted up, jaws agape. ----
# Design space x 0..1.25, y 0..1 (y down).  primitive = (op, kind, data, levels)
#   op   : fill | erase (mask)   cut | uncut (dark line layer; uncut erases lines under a later fill)
#          hl | unhl (pale highlight layer, e.g. the ring of an eye)
#   kind : poly | ellipse | line (line = dict(pts=[...], w=width in design units))
DEEP_ONE_DESIGN = (1.25, 1.0)
DEEP_ONE = [
    # torso: hunched back bulging up-right, chest to the left, haunch at the lower right
    ("fill", "poly", [(0.56, 0.50), (0.44, 0.60), (0.38, 0.78), (0.44, 1.0), (1.02, 1.0), (1.14, 0.82),
                      (1.10, 0.56), (0.98, 0.36), (0.86, 0.26)], ALL),
    # serrated fin crest along the crown and spine
    ("fill", "poly", [(0.58, 0.16), (0.68, 0.00), (0.80, 0.14)], ALL),
    ("fill", "poly", [(0.80, 0.16), (0.94, 0.02), (0.98, 0.30)], ALL),
    ("fill", "poly", [(0.98, 0.34), (1.14, 0.22), (1.12, 0.52)], ALL),
    ("fill", "poly", [(1.10, 0.56), (1.25, 0.52), (1.16, 0.74)], ALL),
    ("fill", "poly", [(1.14, 0.78), (1.24, 0.82), (1.08, 0.96)], HI),
    # head: bulbous cranium + broad snout thrust up-left
    ("fill", "ellipse", [(0.40, 0.08), (0.94, 0.54)], ALL),
    ("fill", "poly", [(0.54, 0.12), (0.30, 0.08), (0.12, 0.10), (0.02, 0.20), (0.02, 0.36), (0.14, 0.44),
                      (0.32, 0.50), (0.52, 0.56), (0.74, 0.56)], ALL),
    # gaping lipless mouth: a wedge notch in the silhouette (survives at 12 px like the mirelurk claw gap)
    ("erase", "poly", [(-0.02, 0.23), (0.48, 0.40), (-0.02, 0.35)], ALL),
    # forearm reaching forward + webbed clawed hand raised in front of the chest, claws up
    # (large sheet only: at 12 px the hand collapses into noise, so the small silhouette is head + crest + body)
    ("fill", "poly", [(0.46, 0.64), (0.58, 0.80), (0.28, 0.94), (0.18, 0.76)], HI),
    ("fill", "poly", _hand(palm=(0.18, 0.82), tips=[(0.00, 0.55), (0.11, 0.48), (0.26, 0.50)],
                           thumb=(0.00, 0.90), web=0.58, palm_r=0.10), HI),
    # cut details
    ("hl", "ellipse", [(0.38, 0.13), (0.54, 0.29)], HI),  # big round fish eye, high and forward: pale ring
    ("cut", "ellipse", [(0.415, 0.165), (0.515, 0.265)], HI),  # ...dark pupil
    ("cut", "line", dict(pts=[(0.66, 0.50), (0.66, 0.62)], w=0.022), FULL),  # gill slits
    ("cut", "line", dict(pts=[(0.72, 0.50), (0.73, 0.63)], w=0.022), FULL),
    ("cut", "line", dict(pts=[(0.78, 0.52), (0.80, 0.64)], w=0.022), FULL),
    ("cut", "line", dict(pts=[(0.50, 0.66), (0.46, 0.76)], w=0.022), FULL),  # arm / chest crease
]

# ---- Star Spawn: towering frontal octopoid, fan of tentacles, bat-wing stubs. Design x 0..1.15, y 0..1 ----
_SS_TENTACLES = [  # centre-lines (x, y), base -> tip
    [(0.34, 0.42), (0.26, 0.58), (0.14, 0.72), (0.04, 0.72)],
    [(0.45, 0.44), (0.41, 0.62), (0.34, 0.84), (0.25, 0.90)],
    [(0.575, 0.45), (0.575, 0.66), (0.57, 0.90), (0.50, 0.98)],
    [(0.70, 0.44), (0.74, 0.62), (0.81, 0.84), (0.90, 0.90)],
    [(0.81, 0.42), (0.89, 0.58), (1.01, 0.72), (1.11, 0.72)],
]
STAR_SPAWN_DESIGN = (1.15, 1.0)
STAR_SPAWN = [
    # bat-wing stubs: two spikes with a scalloped membrane, rooted behind each shoulder
    ("fill", "poly", [(0.32, 0.42), (0.20, 0.52), (0.00, 0.10), (0.14, 0.24), (0.13, 0.00), (0.27, 0.30)], ALL),
    ("fill", "poly", [(0.83, 0.42), (0.95, 0.52), (1.15, 0.10), (1.01, 0.24), (1.02, 0.00), (0.88, 0.30)], ALL),
    # broad shoulders / chest (the bust ends at ~0.70 so the tentacle tips hang free below it)
    ("fill", "poly", [(0.06, 0.46), (1.09, 0.46), (1.00, 0.70), (0.15, 0.70)], ALL),
    # arms hanging at the flanks, clawed tips
    ("fill", "poly", [(0.06, 0.50), (0.22, 0.50), (0.20, 0.92), (0.24, 1.0), (0.13, 0.96), (0.06, 1.0), (0.02, 0.90)], ALL),
    ("fill", "poly", [(0.93, 0.50), (1.09, 0.50), (1.13, 0.90), (1.09, 1.0), (1.02, 0.96), (0.91, 1.0), (0.95, 0.92)], ALL),
    # head: high dome + jowls
    ("fill", "ellipse", [(0.28, 0.00), (0.87, 0.44)], ALL),
    ("fill", "poly", [(0.30, 0.26), (0.85, 0.26), (0.84, 0.46), (0.31, 0.46)], ALL),
    # tentacles: dark groove, then fill, then erase the groove under the fill (so they read over the chest)
    # 12 px sheets (detail 0) draw only tentacles 0, 2, 4, thickened to >= 1.5 px so they survive the downscale
    *[("cut", "poly", _taper(t, 0.15, 0.06), HI) for t in _SS_TENTACLES],
    *[("fill", "poly", _taper(t, 0.11, 0.032), ALL if i in (0, 2, 4) else HI) for i, t in enumerate(_SS_TENTACLES)],
    *[("fill", "poly", _taper(t, 0.17, 0.06), LOW) for i, t in enumerate(_SS_TENTACLES) if i in (0, 2, 4)],
    *[("uncut", "poly", _taper(t, 0.11, 0.032), HI) for t in _SS_TENTACLES],
    # eyes: slanted, angry
    ("cut", "poly", [(0.36, 0.20), (0.50, 0.26), (0.50, 0.31), (0.38, 0.27)], HI),
    ("cut", "poly", [(0.79, 0.20), (0.65, 0.26), (0.65, 0.31), (0.77, 0.27)], HI),
    # arm / chest separation
    ("cut", "line", dict(pts=[(0.22, 0.52), (0.21, 0.70)], w=0.02), FULL),
    ("cut", "line", dict(pts=[(0.93, 0.52), (0.94, 0.70)], w=0.02), FULL),
]

# ---- NATO symbols (frame 2) in inner-box normalized coords (x 0..1 across, y 0..1 down) ----
# each: (kind, data, levels); kind: line (polyline) | arc (dict box/start/end deg)
_wave = [(0.12 + i * 0.076, 0.86 + (0.07 if i % 2 else -0.07)) for i in range(11)]
NATO_DEEP_ONES = [  # Dagon's trident over water
    ("line", [(0.50, 0.12), (0.50, 0.70)], HI),  # shaft
    ("line", [(0.30, 0.16), (0.30, 0.36), (0.50, 0.44), (0.70, 0.36), (0.70, 0.16)], HI),  # outer prongs
    ("line", [(0.44, 0.24), (0.50, 0.08), (0.56, 0.24)], HI),  # centre barb
    ("line", _wave, HI),
    # 12 px sheets: axis-aligned so the 1 px strokes stay crisp
    ("line", [(0.50, 0.08), (0.50, 0.62)], LOW),
    ("line", [(0.30, 0.08), (0.30, 0.40), (0.70, 0.40), (0.70, 0.08)], LOW),
    ("line", [(0.16, 0.86), (0.84, 0.86)], LOW),
]
NATO_STAR_SPAWN = [  # octopoid head with hanging tentacles
    ("arc", dict(box=(0.26, 0.10, 0.74, 0.62), start=180, end=360), ALL),  # dome
    ("line", [(0.26, 0.36), (0.26, 0.50), (0.74, 0.50), (0.74, 0.36)], ALL),  # dome base
    ("line", [(0.33, 0.50), (0.29, 0.70), (0.18, 0.88)], ALL),  # outer tentacles
    ("line", [(0.67, 0.50), (0.71, 0.70), (0.82, 0.88)], ALL),
    ("line", [(0.45, 0.50), (0.44, 0.72), (0.38, 0.92)], HI),  # inner pair (large only)
    ("line", [(0.55, 0.50), (0.56, 0.72), (0.62, 0.92)], HI),
    ("line", [(0.50, 0.50), (0.50, 0.90)], LOW),  # single centre tentacle (small)
    ("line", [(0.42, 0.30), (0.46, 0.34)], HI),  # eyes
    ("line", [(0.58, 0.30), (0.54, 0.34)], HI),
]

GLYPHS = {
    "mltd_deep_ones": (DEEP_ONE_DESIGN, DEEP_ONE, NATO_DEEP_ONES),
    "mltd_star_spawn": (STAR_SPAWN_DESIGN, STAR_SPAWN, NATO_STAR_SPAWN),
}

# --------------------------------------------------------------------------------------
# Rasterisation
# --------------------------------------------------------------------------------------


def _fit(design, box):
    """Uniform scale + centring of the design space into a pixel box (x0,y0,x1,y1), at SS resolution."""
    dw, dh = design
    x0, y0, x1, y1 = box
    bw, bh = (x1 - x0) * SS, (y1 - y0) * SS
    s = min(bw / dw, bh / dh)
    ox = x0 * SS + (bw - dw * s) / 2
    oy = y0 * SS + (bh - dh * s) / 2
    return (lambda p: (ox + p[0] * s, oy + p[1] * s)), s


def _stroke(draw, pts, width, fill):
    draw.line(pts, fill=fill, width=max(1, int(round(width))), joint="curve")
    r = width / 2
    for p in pts:  # round caps
        draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def raster_glyph(design, prims, frame, box, detail):
    """Return (mask, cut, hl) float arrays in 0..1 at SS resolution for one frame."""
    W, H = frame[0] * SS, frame[1] * SS
    mask = Image.new("L", (W, H), 0)
    cut = Image.new("L", (W, H), 0)
    hl = Image.new("L", (W, H), 0)
    draws = {"fill": mask, "erase": mask, "cut": cut, "uncut": cut, "hl": hl, "unhl": hl}
    draws = {k: ImageDraw.Draw(v) for k, v in draws.items()}
    tf, s = _fit(design, box)
    for op, kind, data, levels in prims:
        if detail not in levels:
            continue
        target = draws[op]
        value = 0 if op in ("erase", "uncut", "unhl") else 255
        if kind == "poly":
            target.polygon([tf(p) for p in data], fill=value)
        elif kind == "ellipse":
            (ax, ay), (bx, by) = tf(data[0]), tf(data[1])
            target.ellipse([ax, ay, bx, by], fill=value)
        elif kind == "line":
            _stroke(target, [tf(p) for p in data["pts"]], data["w"] * s, value)
    return tuple(np.asarray(im, np.float32) / 255.0 for im in (mask, cut, hl))


def _shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]
    return out


def _blur(a, radius):
    if radius <= 0:
        return a
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0


def shade(mask, cut, hl, palette, rim_px, shadow):
    """Shade an SS-resolution mask like the vanilla icons; returns a premultiplied float RGBA array."""
    pal = PALETTES[palette]
    base, light, dark, line = (np.array(pal[k], np.float32) / 255.0 for k in ("base", "light", "dark", "line"))
    H, W = mask.shape
    k = max(1, int(round(rim_px * SS)))
    rim_light = _blur(np.clip(mask - _shift(mask, k, k), 0, 1), SS * 0.35) * mask
    rim_dark = _blur(np.clip(mask - _shift(mask, -k, -k), 0, 1), SS * 0.35) * mask
    ys = np.where(mask.max(axis=1) > 0.5)[0]
    y0, y1 = (ys.min(), ys.max()) if len(ys) else (0, H - 1)
    ramp = np.ones(H, np.float32)
    ramp[y0:y1 + 1] = np.linspace(GRADIENT_TOP, GRADIENT_BOTTOM, y1 - y0 + 1)
    col = np.clip(base[None, None, :] * ramp[:, None, None], 0, 1)
    col = col + (light - col) * (RIM_LIGHT_WEIGHT * rim_light)[..., None]
    col = col + (dark - col) * (RIM_DARK_WEIGHT * rim_dark)[..., None]
    col = col + (light - col) * (HL_WEIGHT * hl * mask)[..., None]
    col = col + (line - col) * (CUT_WEIGHT * cut * mask)[..., None]
    sx, sy, srad, salpha = shadow  # black drop shadow under the glyph
    sh = _blur(_shift(mask, int(round(sx * SS)), int(round(sy * SS))), srad * SS) * salpha
    out_a = mask + sh * (1 - mask)
    out_rgb = col * mask[..., None]  # premultiplied; the shadow is black so it adds no colour
    return np.dstack([out_rgb, out_a[..., None]])


def downscale(premul, frame):
    """LANCZOS downscale of a premultiplied float RGBA array to the frame size; returns float RGBA 0..255."""
    W, H = frame
    chans = []
    for c in range(4):
        im = Image.fromarray(np.clip(premul[..., c] * 255, 0, 255).astype(np.uint8))
        chans.append(np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255.0)
    a = np.clip(chans[3], 0, 1)
    rgb = np.dstack(chans[:3])
    rgb = np.where(a[..., None] > 1e-4, rgb / np.maximum(a[..., None], 1e-4), 0)
    return np.dstack([np.clip(rgb, 0, 1), a]) * 255


def nato_frame(frame, box_key, symbol, detail):
    """Frame 2: grey NATO counter box with a dark line symbol. Returns float RGBA 0..255."""
    W, H = frame
    p = NATO_BOX[box_key]
    x0, y0, x1, y1 = p["rect"]
    img = np.zeros((H, W, 4), np.float32)
    img[..., :3] = 255
    img[y0:y1 + 1, x0:x1 + 1] = (0, 0, 0, 255)
    g0, g1 = p["grad"]
    inner_rows = y1 - y0 - 1
    for i, y in enumerate(range(y0 + 1, y1)):
        v = p["top_row"] if i == 0 else g0 + (g1 - g0) * (i - 1) / max(1, inner_rows - 2)
        img[y, x0 + 1:x1, :3] = v
    img[y0 + 1:y1, x0 + 1, :3] = np.clip(img[y0 + 1:y1, x0 + 1, :3] + p["left_add"], 0, 255)
    img[y0 + 1:y1, x1 - 1, :3] = np.clip(img[y0 + 1:y1, x1 - 1, :3] - p["right_sub"], 0, 255)
    # halo (1 px top/left) and drop shadow (right/bottom): black lines outside the box, each spanning the
    # full outer extent x0-1 .. x1+len(shadow) / y0-1 .. y1+len(shadow) and fading at both ends (see NATO_BOX)
    ext = len(p["shadow"])
    xs, ys = range(x0 - 1, x1 + ext + 1), range(y0 - 1, y1 + ext + 1)

    def tapered(n, base):
        vals = [base] * n
        for j, v in enumerate(p["taper"].get(base, ())):
            vals[j], vals[n - 1 - j] = v, v
        return vals

    def paint_row(y, base):
        if 0 <= y < H:
            for x, v in zip(xs, tapered(len(xs), base)):
                if 0 <= x < W:
                    img[y, x] = (0, 0, 0, v)

    def paint_col(x, base):
        if 0 <= x < W:
            for y, v in zip(ys, tapered(len(ys), base)):
                if 0 <= y < H:
                    img[y, x] = (0, 0, 0, v)

    if p["halo"]:
        paint_row(y0 - 1, p["halo"])
        paint_col(x0 - 1, p["halo"])
    for i, a in enumerate(p["shadow"]):
        paint_row(y1 + 1 + i, a)
        paint_col(x1 + 1 + i, a)
    # symbol, drawn at SS resolution and downscaled
    iw, ih = (x1 - x0 - 1), (y1 - y0 - 1)
    sym = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(sym)
    lw = NATO_LINE_W[box_key] * ih * SS

    def tf(q):
        return ((x0 + 1 + q[0] * iw) * SS, (y0 + 1 + q[1] * ih) * SS)

    for kind, data, levels in symbol:
        if detail not in levels:
            continue
        if kind == "line":
            _stroke(d, [tf(q) for q in data], lw, 255)
        elif kind == "arc":
            (ax, ay), (bx, by) = tf(data["box"][:2]), tf(data["box"][2:])
            d.arc([ax, ay, bx, by], data["start"], data["end"], fill=255, width=max(1, int(round(lw))))
    s = np.asarray(sym.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    inside = np.zeros((H, W), np.float32)
    inside[y0 + 1:y1, x0 + 1:x1] = 1
    w = (s * inside)[..., None]
    img[..., :3] = img[..., :3] * (1 - w) + np.array(NATO_LINE, np.float32) * w
    return img


def build_sheet(unit, sheet_key):
    design, prims, symbol = GLYPHS[unit]
    cfg = SHEETS[sheet_key]
    frame = cfg["frame"]
    mask, cut, hl = raster_glyph(design, prims, frame, cfg["glyph_box"], cfg["detail"])
    f1 = downscale(shade(mask, cut, hl, cfg["palette"], cfg["rim"], cfg["shadow"]), frame)
    f2 = nato_frame(frame, cfg["box"], symbol, 1 if sheet_key == "large" else 0)
    sheet = np.concatenate([f1, f2], axis=1)
    return Image.fromarray(np.clip(np.round(sheet), 0, 255).astype(np.uint8), "RGBA")


def dds_header(path):
    d = path.read_bytes()[:128]
    h, w = struct.unpack_from("<II", d, 12)
    pfflags, _fourcc, bits, rm, gm, bm, am = struct.unpack_from("<IIIIIII", d, 80)
    return dict(w=w, h=h, pfflags=hex(pfflags), fourcc=d[84:88] if pfflags & 4 else b"-", bits=bits,
                masks=(hex(rm), hex(gm), hex(bm), hex(am)))


# Division-template counters. HOI4 has no key that names a sprite for a template: a template's
# `template_counter = N` resolves in C++ to the sprite names GFX_div_templ_<N>_large / _small, so
# declaring those sprites yourself is how a custom division icon is done (OWB itself adds 65-255 in
# interface/z_fallout_division_template_icons.gfx; vanilla holds 0-43 and the anniversary DLC 44-64,
# so 256 and 257 are the first free indices in an OWB playset). The textures are exactly frame 1 of
# the counter sheets built above - 76x42 large, 30x12 small - so they are sliced out rather than
# redrawn, and the template icon can never drift from the battalion icon.
TEMPLATE_COUNTERS = {
    "mltd_deep_ones": dict(index=256, source="large", onmap="onmap"),
    "mltd_star_spawn": dict(index=257, source="large", onmap="onmap"),
}
TEMPLATE_DIRS = dict(large="gfx/interface/counters/division_templates_large",
                     small="gfx/interface/counters/division_templates_small")


def write_template_counters():
    """Slice frame 1 of each counter sheet into the two division-template textures."""
    out = []
    for unit, cfg in TEMPLATE_COUNTERS.items():
        for kind, sheet_key in (("large", cfg["source"]), ("small", cfg["onmap"])):
            fw, fh = SHEETS[sheet_key]["frame"]
            sheet = Image.open(MOD / FILES[unit][sheet_key]).convert("RGBA")
            frame = sheet.crop((0, 0, fw, fh))          # frame 1: the shaded glyph, no NATO box
            dst = MOD / TEMPLATE_DIRS[kind] / f"custom_template_{cfg['index']:03d}.dds"
            dst.parent.mkdir(parents=True, exist_ok=True)
            frame.save(dst)                              # uncompressed A8R8G8B8, as above
            hdr = dds_header(dst)
            assert (hdr["w"], hdr["h"]) == (fw, fh), (dst, hdr)
            assert hdr["bits"] == 32 and hdr["pfflags"] == "0x41", hdr
            out.append(f"  {dst.relative_to(MOD)}  {fw}x{fh}  GFX_div_templ_{cfg['index']}_{kind}")
    return out


def write_all():
    results = {}
    for unit, paths in FILES.items():
        for sheet_key, rel in paths.items():
            img = build_sheet(unit, sheet_key)
            dst = MOD / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            img.save(dst)  # no pixel_format -> uncompressed A8R8G8B8, same header class as OWB / vanilla
            back = Image.open(dst)
            back.load()
            a = np.asarray(back.convert("RGBA"))
            hdr = dds_header(dst)
            assert back.size == img.size and a.shape[2] == 4, dst
            assert hdr["bits"] == 32 and hdr["pfflags"] == "0x41", hdr
            assert a[0, 0, 3] == 0 and int(a[..., 3].min()) == 0, "expected truly transparent pixels"
            fw = hdr["w"] // 2
            if sheet_key == "large":  # the glyph's drop shadow must fade out before the frame edge
                assert a[-1, :fw, 3].max() < 32 and a[0, :fw, 3].max() < 32, "frame-1 shadow clipped"
            else:  # 12 px sheets: no opaque silhouette pixel on the top or bottom row
                assert (a[0, :30, 3] >= 200).sum() == 0 and (a[11, :30, 3] >= 200).sum() == 0, "small glyph flush with frame edge"
            digest = hashlib.sha256(dst.read_bytes()).hexdigest()
            results[rel] = (digest, hdr)
            print(f"{rel}: {hdr['w']}x{hdr['h']} A8R8G8B8 pfflags={hdr['pfflags']} bytes={dst.stat().st_size} sha256={digest[:16]}")
    return results


# --------------------------------------------------------------------------------------
# Previews
# --------------------------------------------------------------------------------------
REFS = {  # OWB reference sheets for side-by-side comparison
    "large": ["unit_amphibious_beasts_icon.dds", "unit_mirelurk_infantry_icon.dds", "unit_deathclaw_icon.dds", "unit_paladin_icon.dds"],
    "onmap": ["onmap_unit_amphibious_beasts_icon.dds", "onmap_unit_mirelurk_infantry_icon.dds", "onmap_unit_deathclaw_icon.dds", "onmap_unit_paladin_icon.dds"],
    "text": ["unit_amphibious_beasts_icon_small.dds", "unit_mirelurk_infantry_icon_small.dds", "unit_deathclaw_icon_small.dds", "unit_paladin_icon_small.dds"],
}
REF_DIRS = {"large": "gfx/interface/counters/divisions_large", "onmap": "gfx/interface/counters/divisions_small", "text": "gfx/texticons"}
BG_DARK, BG_LIGHT = (52, 58, 52, 255), (150, 150, 150, 255)


def _on_bg(img, bg, scale):
    big = img.resize((img.width * scale, img.height * scale), Image.NEAREST)
    canvas = Image.new("RGBA", big.size, bg)
    canvas.alpha_composite(big)
    return canvas


def _load_ref(sheet_key, name):
    p = OWB / REF_DIRS[sheet_key] / name
    if not p.exists():
        return None
    im = Image.open(p)
    im.load()
    return im.convert("RGBA")


def _column(title, entries, scale, font):
    """One labelled column: each entry = (label, image) drawn on dark + light ground at `scale` and at 1x."""
    cells = []
    for label, im in entries:
        dark, light = _on_bg(im, BG_DARK, scale), _on_bg(im, BG_LIGHT, scale)
        one = _on_bg(im, BG_DARK, 1)
        cell = Image.new("RGBA", (dark.width + light.width + one.width + 16, dark.height + 14), (28, 28, 28, 255))
        ImageDraw.Draw(cell).text((0, 0), label, fill=(230, 230, 230, 255), font=font)
        cell.paste(dark, (0, 14))
        cell.paste(light, (dark.width + 4, 14))
        cell.paste(one, (dark.width + light.width + 12, 14 + (dark.height - one.height) // 2))
        cells.append(cell)
    W = max(c.width for c in cells)
    H = sum(c.height + 4 for c in cells) + 18
    col = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    ImageDraw.Draw(col).text((0, 2), title, fill=(255, 220, 140, 255), font=font)
    y = 18
    for c in cells:
        col.paste(c, (0, y))
        y += c.height + 4
    return col


def preview(tag, sheets):
    """Side-by-side sheet: ours (all three classes) next to OWB references, on dark and light ground, 4x/8x and 1x."""
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    cols = []
    for sheet_key, scale in (("large", 4), ("onmap", 8), ("text", 8)):
        ours = [(f"{u} [{sheet_key}]", sheets[(u, sheet_key)]) for u in FILES]
        refs = [(f"OWB {n}", _load_ref(sheet_key, n)) for n in REFS[sheet_key]]
        refs = [(l, im) for l, im in refs if im is not None]
        cols.append(_column(f"{sheet_key}  (ours, then OWB references)", ours + refs, scale, font))
    W = sum(c.width + 24 for c in cols)
    H = max(c.height for c in cols) + 8
    out = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    x = 8
    for c in cols:
        out.paste(c, (x, 4))
        x += c.width + 24
    dst = PREVIEW_DIR / f"preview_{tag}.png"
    out.save(dst)
    print("preview:", dst)
    compare(tag, sheets)
    return dst


def compare(tag, sheets):
    """True-size strips (1x, 2x, 3x) of our icons between OWB's, as the game would show them on a dark panel."""
    large = [sheets[(u, "large")] for u in FILES] + [_load_ref("large", n) for n in REFS["large"][:3]]
    text = [sheets[(u, "text")] for u in FILES] + [_load_ref("text", n) for n in REFS["text"][:3]]
    onmap = [sheets[(u, "onmap")] for u in FILES] + [_load_ref("onmap", n) for n in REFS["onmap"][:3]]
    strips = []
    for scale in (1, 2, 3):
        pitch = 152 * scale + 12
        W = pitch * len(large) + 8
        H = (42 + 12 + 12) * scale + 24
        strip = Image.new("RGBA", (W, H), BG_DARK)
        for y, ims in ((4, large), (42 * scale + 10, text), (54 * scale + 16, onmap)):
            x = 8
            for im in ims:
                if im is not None:
                    strip.alpha_composite(im.resize((im.width * scale, im.height * scale), Image.NEAREST), (x, y))
                x += pitch
        strips.append(strip)
    W = max(s.width for s in strips)
    H = sum(s.height + 6 for s in strips)
    out = Image.new("RGBA", (W, H), (28, 28, 28, 255))
    y = 0
    for s in strips:
        out.paste(s, (0, y))
        y += s.height + 6
    dst = PREVIEW_DIR / f"compare_{tag}.png"
    out.save(dst)
    print("compare:", dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="also write event_images/unit_icons/preview_<tag>.png")
    ap.add_argument("--tag", default="final")
    args = ap.parse_args()
    write_all()
    for line in write_template_counters():
        print(line)
    if args.preview:
        sheets = {(u, k): build_sheet(u, k) for u in FILES for k in SHEETS}
        preview(args.tag, sheets)


if __name__ == "__main__":
    main()
