"""
build_decision_icons.py - decision icon GFX_decision_mltd_cult_hood (drawn for the "Found a Cult" decision; since round 17 the "Call for People" decision).

Started from the "front" variant (r14/icon_front/build.py): a front-facing pointed cowl for the
drowned faith of M'lyeh, the face opening pure shadow, symmetrical, lit from the upper left like
OWB's / vanilla's painted decision icons, over a soft black halo. Changes from "front":

  1. the lit upper-left side of the cowl and shoulders is lifted ~10-15 luma (grey lift, so chroma
     is untouched); the face opening stays black;
  2. chroma is scaled by SAT about each pixel's own luma - a hue-preserving desaturation;
  3. the outline is side-dependent: a dark teal, thinner, on the edges facing the light, and
     near-black only on the edges turned away from it (lower right, the hem);
  4. the eyes are painted at 1x: 2 px each in EYE_RGB, under the brow's rim highlight;
  5. the violet clasp is gone; a small dim trident / coral sigil (after the "emblem" variant) is
     stitched on the left breast at x <= 16, clear of the target flag's frame at icon x 17;
  6. the lower robe's evenly spaced streaks are replaced by two broad folds per side, one long,
     one short.

Drawn procedurally (numpy + Pillow, no external images) at SS x supersampling, downsampled with
LANCZOS in premultiplied alpha to 33x32; the eyes and the sigil are then painted pixel-exact at 1x.

Sigil: "barb" (bounding box 7x7 at icon x 9-15, y 21-27). Three separated tines need five columns
on their own, so outward-flaring tips cost one column each side; the body is 5x6. The 5x5 "fan"
(splayed tines) reads as an arrow's fletching or the rune Algiz, "fork5" has no flare, and "barb5"
is squat enough to drift back towards a psi - see `python build.py --sigils` -> sigils.png.

Edge luma is measured on the outermost ring of pixels with alpha >= 128, split by whether the
figure's outward normal faces the light: the definition under which FRONT's outline reads
near-black on both sides (lit 19, shadow 3).

DDS: Pillow's writer, no pixel_format. Every functional header field equals vanilla
decision_infiltrate_state.dds (A8R8G8B8, pitch 132, no mips, caps 0x1000); only dwReserved1 differs,
where vanilla carries NVIDIA Texture Tools' writer tag "NVTT" + version and Pillow writes zeros.

Outputs:
  mod_folder/gfx/interface/decisions/mltd_cult_hood.dds  33x32 RGBA, uncompressed, no mips (Pillow's writer)
  event_images/decision_icons/:
  mltd_cult_hood.png  the same pixels
  preview.png         ours beside FRONT, EMBLEM, decision_ffi_mask and decision_infiltrate_state
                      at 8x and 1x on rgb(40,34,28), plus targeted-decision-row mocks with a flag
  closeup_16x.png     ours alone at 16x (inspection only)
  sigils.png          (only with --sigils) the candidate sigil designs side by side

Run:  python build_decision_icons.py [--sigils]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DDS_OUT = os.path.join(HERE, "mod_folder", "gfx", "interface", "decisions", "mltd_cult_hood.dds")
PREVIEW_DIR = os.path.join(HERE, "event_images", "decision_icons")
R14 = os.path.dirname(HERE)
OWB = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196"
HOI4 = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
VANILLA_REF = os.path.join(HOI4, r"gfx\interface\decisions\decision_infiltrate_state.dds")

W, H = 33, 32   # decision_enc_propaganda.dds / decision_infiltrate_state.dds
SS = 16         # supersampling factor
CX = W / 2.0    # 16.5: the axis of symmetry runs through pixel column 16
SEED = 1983     # deterministic noise
LUMA = np.array([0.299, 0.587, 0.114])

# ------------------------------------------------------------------ geometry
# All lengths are in final (1x) pixels.
# Outer silhouette: half-width against y. Pointed cowl, the hood's head
# bulging over a slight waist at the jaw, rounded shoulders, robe.
OUTER = [(0.9, 0.0), (2.4, 1.1), (4.3, 2.9), (6.5, 5.0), (9.0, 7.0),
         (11.5, 8.3), (13.5, 8.6), (15.6, 8.2), (17.2, 8.5), (18.8, 10.1),
         (20.3, 11.9), (21.8, 13.0), (23.8, 13.7), (26.5, 14.0), (30.5, 14.2)]
HEM_Y, HEM_CURVE = 29.6, 1.3        # hem y = HEM_Y - HEM_CURVE * (dx / 14.2)^2

# Face opening (pure shadow): pointed top, widest a little above the middle,
# rounded bottom where the chin would be.
FACE_TOP, FACE_BOT, FACE_HW = 4.9, 18.4, 4.75
FACE_K = 0.80                       # widest where t = 0.5 ** (1 / FACE_K)
FACE_P_TOP, FACE_P_BOT = 1.0, 0.45  # shape exponent: 1 = pointed, 0.5 = round

# Eyes, painted at 1x after the downsample: 2 px each, one pixel row, under the brow
EYE_ROW = 10
EYE_PX = (((14, EYE_ROW), 1.00), ((15, EYE_ROW), 0.92),    # (pixel, strength): outer end
          ((18, EYE_ROW), 1.00), ((17, EYE_ROW), 0.92))    # a touch brighter than inner
EYE_RGB = np.array([60.0, 140, 120])
EYE_GLOW = 0.13                     # EYE_RGB blended into void pixels touching an eye

# Robe front parting: the two front edges meet at the throat and part down the axis
PART_Y = 19.9
# Folds: two broad folds per side, mirrored about the axis: (dx0, y0) -> (dx1, y1), half-width.
# One long (from the shoulder's slope to the hem), one short (hanging below the chest).
FOLDS = [((8.3, 20.4), (10.4, 29.5), 1.00),
         ((3.7, 25.6), (4.6, 29.6), 0.85)]
FOLD_H = 1.0

LIGHT = np.array([-0.55, -0.70, 0.62])   # towards the light: upper left, front

# shade -> colour: violet-black shadows, deep ocean teal mids, pale teal lights
RAMP = [
    (0.00, (5, 5, 12)),
    (0.16, (22, 14, 42)),
    (0.34, (18, 40, 58)),
    (0.52, (18, 68, 80)),
    (0.72, (38, 110, 118)),
    (0.90, (84, 158, 156)),
    (1.00, (124, 192, 182)),
]
VIOLET_LO, VIOLET_HI = np.array([38.0, 22, 64]), np.array([104.0, 84, 150])
SHADOW_VIOLET = np.array([36.0, 26, 70])  # cast into the side turned from the light
LINING = np.array([40.0, 18, 62])        # hood lining just inside the opening
VOID = np.array([2.0, 2, 6])             # the face

# Grade: grey luma lift on the cloth (lit side / everywhere), then a hue-preserving chroma scale
LIFT_LIT, LIFT_BASE = 15.0, 8.0
LIT_LO, LIT_HI = 0.30, 0.80              # diffuse range over which LIFT_LIT fades in
SAT = 0.78

# Outline: near-black on the side turned from the light, a dark teal on the lit side
OUTLINE_DARK = np.array([7.0, 6, 13])
OUTLINE_LIT = np.array([8.0, 15, 18])    # luma ~13; mixed with the halo it lands ~25-30 at 1x
OUTLINE_W_DARK = (0.45, 1.05)            # smoothstep over interior distance D: outline -> cloth
OUTLINE_W_LIT = (0.45, 1.05)

# drop shadow (pure black, like the references' halo)
SHADOW_SIGMA, SHADOW_DX, SHADOW_DY, SHADOW_OPACITY = 1.15, 0.55, 0.8, 0.95

# ------------------------------------------------------------------ sigil
# A three-pronged coral / trident stitched on the left breast, after the "emblem" variant's sigil
# (a teal thread mark on a dark violet ground), shrunk to pixel scale and redrawn so that it reads
# as tines on a shaft rather than a psi: a flat crossbar with square corners, the side tines'
# tips flaring outward (dim pixels one column out), and a shaft longer than the head.
# Grid: '3' bright thread, '2' mid, '1' dim, '.' none. Top-left pixel at (SIGIL_X0, SIGIL_Y0).
SIGILS = {
    "barb": ["3..3..3",      # 7x7: tines on a flat crossbar, side tips kinked outward (full bright, so
                             # both barbs clear the shoulder highlight above them)
             ".3.3.3.",
             ".3.3.3.",
             ".33333.",       # full-bright to the right end, so the bar is symmetric
             "...3...",
             "...3...",       # a 3 px shaft (tines 3 : bar 1 : shaft 3): a trident's
             "...2..."],      # proportions, not psi's 3 : 1 : 2
    "barb5": ["2..3..2",     # 7x5: the same with one-pixel tines
              ".3.3.3.",
              ".33332.",
              "...3...",
              "...2..."],
    "fork5": ["3.3.3",       # 5x5: parallel tines, flat crossbar, square corners
              "3.3.3",
              "33332",
              "..3..",
              "..2.."],
    "fan": ["3.3.3",         # 5x5: side tines splayed outward from the shaft
            ".333.",
            "..3..",
            "..3..",
            "..2.."],
    "fan6": ["3.3.3",        # 5x6: splayed tines on a longer shaft
             ".333.",
             "..3..",
             "..3..",
             "..3..",
             "..2.."],
}
SIGIL = os.environ.get("MLTD_SIGIL", "barb")
SIGIL_POS = {"barb": (9, 21), "barb5": (9, 21)}   # 7-wide designs: tips spill a column each way
SIGIL_X0, SIGIL_Y0 = 10, 21         # 5-wide designs: columns 10-14, rows 21-26
SIG_RGB = np.array([86.0, 134, 120])   # pale sea-green thread, luma ~117 at level 3
SIG_LEVEL = {"3": 1.0, "2": 0.80, "1": 0.55}
SIG_LUMA_MAX = 120.0
GROUND = np.array([20.0, 14, 34])      # dark violet ground the thread is stitched on
GROUND_GAP = 0.60                      # darkening of a gap with thread on both sides (between tines)
GROUND_4, GROUND_8 = 0.45, 0.30   # deeper ring: clears the fold and shoulder highlights beside the shaft and tips        # ... of other 4- / diagonal-only neighbours of thread


# ------------------------------------------------------------------ helpers
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def pchip(xk, yk, x):
    """Monotone cubic Hermite interpolation (Fritsch-Carlson)."""
    xk, yk = np.asarray(xk, float), np.asarray(yk, float)
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.empty_like(yk)
    m[0], m[-1] = d[0], d[-1]
    for k in range(1, len(xk) - 1):
        if d[k - 1] * d[k] <= 0:
            m[k] = 0.0
        else:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    x = np.asarray(x, float)
    i = np.clip(np.searchsorted(xk, x) - 1, 0, len(xk) - 2)
    t = (x - xk[i]) / h[i]
    t2, t3 = t * t, t * t * t
    return ((2 * t3 - 3 * t2 + 1) * yk[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
            + (-2 * t3 + 3 * t2) * yk[i + 1] + (t3 - t2) * h[i] * m[i + 1])


def gblur(a, sx, sy=None):
    """Gaussian blur (sigma in array pixels), zero padding, via FFT."""
    sy = sx if sy is None else sy
    pad = int(np.ceil(4 * max(sx, sy))) + 2
    p = np.pad(a, pad, mode="constant")
    fy = np.fft.fftfreq(p.shape[0])[:, None]
    fx = np.fft.rfftfreq(p.shape[1])[None, :]
    g = np.exp(-2 * np.pi ** 2 * ((fx * sx) ** 2 + (fy * sy) ** 2))
    out = np.fft.irfft2(np.fft.rfft2(p) * g, s=p.shape)
    return out[pad:-pad, pad:-pad]


def shift(a, dx, dy):
    """Shift by whole array pixels, zero fill."""
    out = np.zeros_like(a)
    h, w = a.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]
    return out


def seg_dist(px, py, a, b):
    """Distance from points to segment a-b, and the clamped parameter along it."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    t = np.clip(((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy), 0.0, 1.0)
    return np.hypot(px - (ax + t * vx), py - (ay + t * vy)), t


def ramp(s):
    k = [r[0] for r in RAMP]
    return np.stack([np.interp(s, k, [r[1][c] for r in RAMP]) for c in range(3)], -1)


def lerp(a, b, t):
    return a + (b - a) * t[..., None]


def luma(c):
    return c @ LUMA


def downsample(a):
    """SS-resolution float array -> 1x with LANCZOS."""
    im = Image.fromarray(a.astype(np.float32))
    return np.asarray(im.resize((W, H), Image.LANCZOS), dtype=np.float64)


# ------------------------------------------------------------------ drawing
def draw():
    """Return (rgba uint8 HxWx4, figure coverage at 1x, outward-facing-the-light at 1x)."""
    rng = np.random.default_rng(SEED)
    ys = (np.arange(H * SS) + 0.5) / SS
    xs = (np.arange(W * SS) + 0.5) / SS
    X, Y = np.meshgrid(xs, ys)
    DX = X - CX
    ADX = np.abs(DX)

    # --- outer silhouette: approximate interior distance D (px, >0 inside)
    oy = [p[0] for p in OUTER]
    hw = pchip(oy, [p[1] for p in OUTER], np.clip(ys, oy[0], oy[-1]))
    hw = np.where(ys < oy[0], -1.0, hw)
    dhw = np.gradient(np.maximum(hw, 0.0), ys)
    d_side = (hw[:, None] - ADX) / np.sqrt(1.0 + dhw[:, None] ** 2)
    y_hem = HEM_Y - HEM_CURVE * (DX / 14.2) ** 2
    D = np.minimum(d_side, y_hem - Y)
    alpha = (D > 0).astype(np.float64)

    # --- face opening: signed distance dface (>0 inside the opening)
    t = (ys - FACE_TOP) / (FACE_BOT - FACE_TOP)
    tc = np.clip(t, 0.0, 1.0)
    p_exp = FACE_P_TOP + (FACE_P_BOT - FACE_P_TOP) * tc
    fhw = FACE_HW * np.sin(np.pi * tc ** FACE_K) ** p_exp
    fhw = np.where((t > 0) & (t < 1), fhw, 0.0)
    dfhw = np.clip(np.gradient(fhw, ys), -12, 12)
    dface = (fhw[:, None] - ADX) / np.sqrt(1.0 + dfhw[:, None] ** 2)
    yc = np.clip(Y, FACE_TOP, FACE_BOT)
    tip = -np.sqrt(DX ** 2 + (Y - yc) ** 2)
    dface = np.where((Y <= FACE_TOP) | (Y >= FACE_BOT), tip, dface)
    face_in = smoothstep(-0.12, 0.18, dface)

    # --- height field -> lighting
    hgt = np.zeros_like(X)
    hgt += 1.0 * (1.0 - np.exp(-np.maximum(D, 0.0) / 1.4))          # edge bevel
    u = np.clip(DX / np.maximum(hw, 0.05)[:, None], -1.0, 1.0)
    hgt += 1.0 * np.sqrt(np.maximum(0.0, 1.0 - u ** 2))              # roundness
    rim = np.exp(-((dface + 0.95) / 0.75) ** 2)                      # rolled hood edge
    hgt += 0.60 * rim
    cowl_fold = (np.exp(-((dface + 3.0) / 0.55) ** 2)
                 * smoothstep(5.5, 7.5, Y) * (1.0 - smoothstep(14.5, 17.0, Y)))
    hgt += 0.35 * cowl_fold
    seam = (np.exp(-(DX / 0.45) ** 2) * smoothstep(1.2, 2.2, Y)
            * (1.0 - smoothstep(FACE_TOP - 1.0, FACE_TOP, Y)))
    hgt += 0.30 * seam                                               # crown seam
    folds = np.zeros_like(X)
    for a, b, fw in FOLDS:
        dist, tt = seg_dist(ADX, Y, a, b)
        # a broad rounded ridge that swells in from its top end
        folds += np.exp(-(dist / fw) ** 2) * smoothstep(0.0, 0.35, tt)
    hgt += FOLD_H * folds
    front = np.exp(-(DX / 0.42) ** 2) * smoothstep(PART_Y + 0.8, PART_Y + 2.2, Y)
    hgt -= 0.55 * front                                              # robe's front edges
    face_wall = smoothstep(-0.05, 0.9, dface)
    hgt -= 2.4 * face_wall                                           # the cavity

    gy, gx = np.gradient(hgt, 1.0 / SS)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    lv = LIGHT / np.linalg.norm(LIGHT)
    diff = np.clip(n @ lv, 0.0, 1.0)
    half = lv + np.array([0.0, 0.0, 1.0])
    half /= np.linalg.norm(half)
    spec = np.clip(n @ half, 0.0, 1.0) ** 30

    # ambient occlusion: the front parting, the throat under the face, the hem
    ao = 1.0 - 0.35 * front
    ao *= 1.0 - 0.25 * np.exp(-((Y - (FACE_BOT + 0.9)) / 1.0) ** 2) * np.exp(-(DX / 3.0) ** 2)
    ao *= 1.0 - 0.18 * smoothstep(23.0, 30.0, Y)

    # painted texture: soft blotches only (the old fine vertical streaks combed the robe)
    blot = gblur(rng.random(X.shape) - 0.5, 1.4 * SS)
    blot /= np.abs(blot).max() + 1e-9

    s = (0.24 + 0.74 * diff) * ao + 0.14 * spec + 0.08 * blot
    col = ramp(np.clip(s, 0.0, 1.0))

    # violet in the cool shadows, on the side turned away from the light
    cast = 0.45 * smoothstep(0.55, 0.20, diff) * (1.0 - face_in)
    col = lerp(col, SHADOW_VIOLET * (0.7 + 0.6 * np.clip(s, 0, 1))[..., None], cast)

    # violet on the rolled edge of the hood
    vio = lerp(VIOLET_LO, VIOLET_HI, np.clip(s, 0, 1))
    col = lerp(col, vio, 0.30 * rim * (1.0 - face_in))

    # (1) lift the cloth: a grey offset, strongest where it faces the light
    lift = LIFT_BASE + LIFT_LIT * smoothstep(LIT_LO, LIT_HI, diff)
    col = col + lift[..., None]

    # the face: lining just inside the edge, then pure shadow (never lifted)
    inner = lerp(LINING, VOID, smoothstep(0.0, 1.2, dface))
    col = lerp(col, inner, face_in)

    # (3) outline: its colour and width follow which way the edge faces
    gyD, gxD = np.gradient(D, 1.0 / SS)
    gn = np.hypot(gxD, gyD) + 1e-9
    l2 = LIGHT[:2] / np.linalg.norm(LIGHT[:2])
    facing = (-gxD * l2[0] - gyD * l2[1]) / gn          # outward normal . light, -1..1
    lit_e = smoothstep(-0.15, 0.60, facing)
    ocol = lerp(OUTLINE_DARK, OUTLINE_LIT, lit_e)
    e0 = OUTLINE_W_DARK[0] + (OUTLINE_W_LIT[0] - OUTLINE_W_DARK[0]) * lit_e
    e1 = OUTLINE_W_DARK[1] + (OUTLINE_W_LIT[1] - OUTLINE_W_DARK[1]) * lit_e
    col = lerp(ocol, col, smoothstep(e0, e1, D))

    # (2) hue-preserving desaturation: scale chroma about each pixel's luma
    L = luma(col)[..., None]
    col = L + SAT * (col - L)

    # composite over a black drop shadow, premultiplied
    sh = shift(alpha, int(round(SHADOW_DX * SS)), int(round(SHADOW_DY * SS)))
    sh = np.clip(gblur(sh, SHADOW_SIGMA * SS), 0.0, 1.0) * SHADOW_OPACITY
    out_a = alpha + sh * (1.0 - alpha)
    prem = col * alpha[..., None]

    a1 = np.clip(downsample(out_a), 0.0, 1.0)
    rgb1 = np.stack([downsample(prem[..., c]) for c in range(3)], -1)
    rgb1 = np.where(a1[..., None] > 1e-4, rgb1 / np.maximum(a1, 1e-4)[..., None], 0.0)
    fig1 = np.clip(downsample(alpha), 0.0, 1.0)
    face1 = np.clip(downsample(face_in * alpha), 0.0, 1.0)
    return rgb1, a1, fig1, face1


def paint_eyes(rgb, face1):
    """(4) Two 2-px eyes in EYE_RGB on the void, with a faint glow on void neighbours."""
    eye = {p: s for p, s in EYE_PX}
    glow = np.zeros((H, W))
    for (x, y), s in EYE_PX:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx or dy:
                    glow[y + dy, x + dx] += EYE_GLOW * s * (1.0 if dx == 0 or dy == 0 else 0.5)
    void = (face1 > 0.9) & (luma(rgb) < 30)
    glow = np.clip(glow, 0, 0.3) * void
    rgb = lerp(rgb, np.broadcast_to(EYE_RGB, rgb.shape), glow)
    for (x, y), s in eye.items():
        rgb[y, x] = EYE_RGB * s
    return rgb


def sigil_pixels(name):
    grid = SIGILS[name]
    x0, y0 = SIGIL_POS.get(name, (SIGIL_X0, SIGIL_Y0))
    px = {}
    for j, row in enumerate(grid):
        for i, ch in enumerate(row):
            if ch in SIG_LEVEL:
                px[(x0 + i, y0 + j)] = SIG_LEVEL[ch]
    return px, (x0, y0, x0 + len(grid[0]) - 1, y0 + len(grid) - 1)


def paint_sigil(rgb, name):
    """(5) The trident on a dark violet ground, lit from the upper left, luma <= SIG_LUMA_MAX."""
    px, (x0, y0, x1, y1) = sigil_pixels(name)
    assert x1 <= 16, f"sigil reaches x={x1}; the flag frame starts at icon x 17"
    dark = np.zeros((H, W))
    for (x, y), lv in px.items():
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (x + dx, y + dy)
                if (dx or dy) and q not in px:
                    if (q[0] - 1, q[1]) in px and (q[0] + 1, q[1]) in px:
                        k = GROUND_GAP                     # enclosed between two tines
                    else:
                        k = GROUND_4 if dx == 0 or dy == 0 else GROUND_8
                    dark[q[1], q[0]] = max(dark[q[1], q[0]], k * min(1.0, lv + 0.2))
    rgb = lerp(rgb, np.broadcast_to(GROUND, rgb.shape), dark)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    for (x, y), lv in px.items():
        f = 1.0 - 0.012 * (x - cx) - 0.035 * (y - cy)      # brighter towards the top; nearly flat across, so both tines match
        c = SIG_RGB * lv * f
        c *= min(1.0, SIG_LUMA_MAX / max(luma(c), 1e-6))
        rgb[y, x] = c
    return rgb


def render(sigil=SIGIL):
    rgb, a1, fig1, face1 = draw()
    rgb = paint_eyes(rgb, face1)
    rgb = paint_sigil(rgb, sigil)
    a8 = np.round(a1 * 255).astype(np.uint8)
    rgb8 = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    rgb8[a8 == 0] = 0
    return Image.fromarray(np.dstack([rgb8, a8])), fig1


# ------------------------------------------------------------------ preview
BROWN = (40, 34, 28)
REFS = [
    ("FRONT (r14/icon_front)", os.path.join(R14, "icon_front", "mltd_cult_hood.dds")),
    ("EMBLEM (r14/icon_emblem)", os.path.join(R14, "icon_emblem", "mltd_cult_hood.dds")),
    ("decision_ffi_mask (OWB, replaced)", os.path.join(OWB, r"gfx\interface\decisions\decision_ffi_mask.dds")),
    ("decision_infiltrate_state (vanilla)", VANILLA_REF),
]
# The FRONT / EMBLEM design variants lived in a scratch folder during development; compare against them
# only if they are still around.
REFS = [(n, p) for n, p in REFS if os.path.exists(p)]
ROW_BG = os.path.join(OWB, r"gfx\interface\decisionview\decision_item_bg.dds")   # 3 frames
FLAG = os.path.join(OWB, r"gfx\flags\medium\NCR.tga")                            # 41x26
FLAG_MASK = os.path.join(HOI4, r"gfx\interface\flag_small_mask.tga")             # GFX_flag_small
FLAG_OVERLAY = os.path.join(HOI4, r"gfx\interface\flag_small_overlay.dds")


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def nearest(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def small_flag():
    """Approximation of maskedShieldType GFX_flag_small (general_stuff.gfx:253-258): the flag at
    the mask's size (20x17), centred in the 26x21 overlay, the overlay on top. The overlay's solid
    frame starts at its column 2 / row 2, i.e. icon x 17 / y 14 in a targeted row. A mock."""
    mask = Image.open(FLAG_MASK)
    over = Image.open(FLAG_OVERLAY).convert("RGBA")
    flag = Image.open(FLAG).convert("RGBA").resize(mask.size, Image.LANCZOS)
    out = Image.new("RGBA", over.size, (0, 0, 0, 0))
    out.alpha_composite(flag, ((over.width - flag.width) // 2, (over.height - flag.height) // 2))
    out.alpha_composite(over)
    return out


def targeted_row(frame, icon, flag, label):
    """Mock of countrydecisionview.gui 'targeted_decision_item' (:481-528):
    background at (-1,-1), icon top-left at (15,0), GFX_flag_small at (30,12)."""
    row = Image.new("RGBA", frame.size, BROWN + (255,))
    row.alpha_composite(frame, (0, 0), (1, 1))
    row.alpha_composite(icon, (15, 0))
    if flag is not None:
        row.alpha_composite(flag, (30, 12))
    ImageDraw.Draw(row).text((62, 12), label, fill=(226, 214, 190, 255), font=font(12))
    return row


def build_preview(icon):
    items = [("GFX_decision_mltd_cult_hood (this build)", icon)] + [(n, Image.open(p).convert("RGBA")) for n, p in REFS]
    strip = Image.open(ROW_BG).convert("RGBA")
    frame0 = strip.crop((0, 0, strip.width // 3, strip.height))
    flag = small_flag()

    M, G, Z = 16, 24, 8
    f12, f15 = font(12), font(15)
    fg, fg2 = (228, 218, 198, 255), (196, 186, 166, 255)
    Wp = M * 2 + sum(im.width * Z for _, im in items) + G * (len(items) - 1)
    Wp = max(Wp, 1500)
    cv = Image.new("RGBA", (Wp, 1700), BROWN + (255,))
    d = ImageDraw.Draw(cv)

    y = M
    d.text((M, y), "GFX_decision_mltd_cult_hood - final - 8x (nearest) and 1x, on rgb(40,34,28)",
           fill=fg, font=f15)
    y += 28
    cell_h = max(im.height for _, im in items) * Z
    x = M
    for name, im in items:
        big = nearest(im, Z)
        cv.alpha_composite(big, (x, y))
        d.text((x, y + cell_h + 6), f"{name}  {im.width}x{im.height}", fill=fg2, font=f12)
        cv.alpha_composite(im, (x + (big.width - im.width) // 2, y + cell_h + 26))   # 1x
        x += big.width + G
    # guide on the final's 8x tile: where the target flag's frame starts (x 17, y 14)
    gx0, gy0 = M + 17 * Z, y + 14 * Z
    for yy in range(gy0, y + cell_h, 6):
        d.line([(gx0, yy), (gx0, yy + 2)], fill=(210, 80, 60, 255))
    for xx in range(gx0, M + 33 * Z, 6):
        d.line([(xx, gy0), (xx + 2, gy0)], fill=(210, 80, 60, 255))
    y += cell_h + 26 + 40

    # 1x strip, then magnified 3x
    d.text((M, y), "1x (true size), same order  |  the same strip magnified 3x (nearest)", fill=fg, font=f15)
    y += 26
    sw = sum(im.width + 12 for _, im in items) + 12
    s1 = Image.new("RGBA", (sw, 44), BROWN + (255,))
    xx = 12
    for _, im in items:
        s1.alpha_composite(im, (xx, (44 - im.height) // 2))
        xx += im.width + 12
    cv.alpha_composite(s1, (M, y + 44))
    cv.alpha_composite(nearest(s1, 3), (M + sw + 40, y))
    y += 44 * 3 + 20

    # targeted-row mocks
    d.text((M, y), "targeted_decision_item mock (OWB decision_item_bg frame 0; icon at 15,0; "
                   "GFX_flag_small at 30,12 - its frame covers the icon from x 17, y 14): 1x, then 3x, "
                   "then the final's row at 8x", fill=fg, font=f15)
    y += 26
    # mock rows by name, not index: the FRONT / EMBLEM development variants are optional (see REFS)
    byname = {n.split(" ")[0]: im for n, im in items}
    rows = [targeted_row(frame0, icon, flag, "Found a Cult in New California Republic")]
    for key, label in (("FRONT", "FRONT"), ("EMBLEM", "EMBLEM"),
                       ("decision_ffi_mask", "OWB original: decision_ffi_mask")):
        if key in byname:
            rows.append(targeted_row(frame0, byname[key], flag, label))
    y_rows = y
    for r in rows:
        cv.alpha_composite(r.crop((0, 0, 300, r.height)), (M, y))
        y += r.height + 6
    y2 = y_rows
    xx = M + 320
    for i, r in enumerate(rows):
        c = nearest(r.crop((0, 0, 150, r.height)), 3)
        cv.alpha_composite(c, (xx + (i % 2) * (450 + 16), y2 + (i // 2) * (r.height * 3 + 8)))
    y = max(y, y2 + 2 * (40 * 3 + 8)) + 16
    big_row = nearest(rows[0].crop((10, 0, 60, 40)), 8)
    cv.alpha_composite(big_row, (M, y))
    y += big_row.height + M
    return cv.crop((0, 0, Wp, y)).convert("RGB")


def build_sigil_sheet():
    names = list(SIGILS)
    strip = Image.open(ROW_BG).convert("RGBA")
    frame0 = strip.crop((0, 0, strip.width // 3, strip.height))
    flag = small_flag()
    M, Z = 16, 12
    cw = 14 * Z
    ch = 11 * Z
    cv = Image.new("RGBA", (M + len(names) * (cw + 24), M + ch + 30 + 100 + 50), BROWN + (255,))
    d = ImageDraw.Draw(cv)
    for i, nm in enumerate(names):
        icon, _ = render(nm)
        x = M + i * (cw + 24)
        crop = icon.crop((5, 18, 19, 29))                # the left breast, 14x11
        cv.alpha_composite(nearest(crop, Z), (x, M))
        d.text((x, M + ch + 6), nm, fill=(228, 218, 198, 255), font=font(14))
        cv.alpha_composite(icon, (x, M + ch + 30))
        cv.alpha_composite(nearest(icon, 3), (x + 44, M + ch + 30))
        r = targeted_row(frame0, icon, flag, "")
        cv.alpha_composite(r.crop((0, 0, 70, 40)), (x, M + ch + 30 + 100))
    return cv.convert("RGB")


# ------------------------------------------------------------------ measurement
def stats(im, name, fig1=None):
    a = np.asarray(im.convert("RGBA")).astype(float)
    al = a[..., 3]
    op = al > 200
    lum = luma(a[..., :3])
    chroma = a[..., :3].max(-1) - a[..., :3].min(-1)
    border = np.concatenate([al[0], al[-1], al[1:-1, 0], al[1:-1, -1]])
    line = (f"{name:36s} median opaque luma {np.median(lum[op]):5.1f}  mean chroma {chroma[op].mean():5.1f}  "
            f"border alpha max {border.max():3.0f}  coverage(a>=128) {(al >= 128).mean():.3f}")
    if fig1 is not None:
        # Edge ring = the outermost pixels of the shape as drawn (alpha >= 128, 4-touching a pixel
        # below it) - the definition under which FRONT's outline reads near-black on both sides.
        # Side = the figure's outward normal against the light (> +0.35 lit, < -0.35 shadow).
        gy, gx = np.gradient(fig1)
        gn = np.hypot(gx, gy) + 1e-9
        l2 = LIGHT[:2] / np.linalg.norm(LIGHT[:2])
        facing = (-gx * l2[0] - gy * l2[1]) / gn
        for label, inside in (("alpha>=128 ring", al >= 128), ("figure>=0.5 ring", fig1 >= 0.5)):
            pad = np.pad(inside, 1)
            ring = inside & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
            lit, dark = ring & (facing > 0.35), ring & (facing < -0.35)
            line += (f"\n{'':36s} edge luma, {label}: lit side median {np.median(lum[lit]):.0f} "
                     f"mean {lum[lit].mean():.0f} n={lit.sum()};  shadow side median "
                     f"{np.median(lum[dark]):.0f} mean {lum[dark].mean():.0f} n={dark.sum()}")
    print(line)


def dds_header_compare(path, ref=VANILLA_REF):
    """Compare the 128-byte DDS headers. dwReserved1 (bytes 32-75) carries no format data; vanilla's
    holds the writer tag of NVIDIA Texture Tools ("NVTT" + version) at 68-75, Pillow leaves it zero."""
    a, b = open(path, "rb").read(128), open(ref, "rb").read(128)
    diff = [i for i in range(128) if a[i] != b[i]]
    functional = [i for i in diff if not 32 <= i < 76]
    return functional, [i for i in diff if 32 <= i < 76]


def main():
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    if "--sigils" in sys.argv:
        build_sigil_sheet().save(os.path.join(PREVIEW_DIR, "sigils.png"))
    icon, fig1 = render()
    dds = DDS_OUT
    icon.convert("RGBA").save(dds)
    icon.save(os.path.join(PREVIEW_DIR, "mltd_cult_hood.png"))
    build_preview(icon).save(os.path.join(PREVIEW_DIR, "preview.png"))
    big = Image.new("RGBA", (W * 16, H * 16), BROWN + (255,))
    big.alpha_composite(nearest(icon, 16))
    big.convert("RGB").save(os.path.join(PREVIEW_DIR, "closeup_16x.png"))

    back = Image.open(dds)
    raw = open(dds, "rb").read(128)
    functional, reserved = dds_header_compare(dds)
    print(f"DDS: {back.size} {back.mode}, {os.path.getsize(dds)} bytes, fourcc {raw[84:88]!r}, "
          f"bitcount {int.from_bytes(raw[88:92], 'little')}, mips {int.from_bytes(raw[28:32], 'little')}, "
          f"round-trip identical: {np.array_equal(np.asarray(back.convert('RGBA')), np.asarray(icon))}\n"
          f"     header vs vanilla decision_infiltrate_state.dds: functional bytes differing {functional}; "
          f"dwReserved1 bytes differing {reserved} (vanilla {open(VANILLA_REF, 'rb').read(128)[68:76]!r})")
    stats(icon, f"FINAL (sigil '{SIGIL}')", fig1)
    for n, p in REFS:
        # FRONT shares this silhouette exactly, so its edge ring is measured with our coverage
        stats(Image.open(p), n, fig1 if n.startswith("FRONT") else None)


if __name__ == "__main__":
    main()
