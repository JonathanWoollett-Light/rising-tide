# -*- coding: utf-8 -*-
"""
build_main_menu.py -- the mod's main-menu background, header logo and rain.

Writes three things:

  mod_folder/gfx/loadingscreens/mltd_main.dds     1910x1440, uncompressed
  mod_folder/gfx/interface/logo_game_static.dds    443x303, uncompressed
  mod_folder/gfx/interface/mltd_rain_anim{1,2}.dds 2560x1440, DXT5

and nothing else -- the wiring is three script files, described in
README > Main menu.

**Dimensions are not free choices.**  1910x1440 is what Old World Blues'
`load_colorado.dds` and tnkd's `tnk_main.dds` both are, and 443x303 is
OWB's `logo_game_static.dds`; the frontend scales the background to cover,
so on a 16:9 screen only the middle ~1074 rows are ever visible and the
source is placed there deliberately.  The rain textures copy the geometry of
OWB's `bg_snow_anim1.dds` exactly (2560x1440, colour in RGB, shape in ALPHA)
because the sprite that drives them is a clone of OWB's snow sprite, and
matching a known-good configuration is the only way to be confident about
`animationtexturescale` without launching the game.

The header logo reuses the marquee from ``build_workshop_thumbnail`` rather
than redrawing it, so the Workshop thumbnail and the main menu cannot drift
apart.  Run that script first if the wordmark source has changed.

Deterministic: one seed, no wall-clock, no network.
"""

import argparse
import math
import os

import cv2
import numpy as np
from PIL import Image

import build_workshop_thumbnail as T

BASE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(BASE, "mod_folder")
PREVIEW = os.path.join(BASE, "event_images", "workshop")

SRC = os.path.join(BASE, "event_images", "call_src.jpg")
BG_OUT = os.path.join(MOD, "gfx", "loadingscreens", "mltd_main.dds")
LOGO_OUT = os.path.join(MOD, "gfx", "interface", "logo_game_static.dds")
RAIN_OUT = os.path.join(MOD, "gfx", "interface", "mltd_rain_anim%d.dds")
RAIN_BASE_OUT = os.path.join(MOD, "gfx", "interface", "mltd_rain_base.dds")
RAIN_MASK_OUT = os.path.join(MOD, "gfx", "interface", "mltd_rain_mask.dds")

# --- background ------------------------------------------------------------
BG_W, BG_H = 1910, 1440          # OWB's own frontend background dimensions
# The frontend container is 1920x1440 with preserve_aspect_ratio and a 100%
# minimum on both axes, so a 16:9 screen shows only the middle 1074 rows.
# The painting goes exactly there; the bands above and below are extension.
SAFE_H = 1074

# --- header logo -----------------------------------------------------------
LOGO_W, LOGO_H = 443, 303
LOGO_OUT_ANIM = os.path.join(MOD, "gfx", "interface", "mltd_logo_animated.dds")
# The strip is UNCOMPRESSED, like OWB's own logo_game_animated.dds.  DXT5 costs
# a quarter of the size but quantises colour per 4x4 block, and a block that
# straddles a bright neon edge and the transparent black outside it gets
# endpoints spanning cyan to black: measured error on visible pixels was mean 6
# and peak 164, which reads as a speckled fringe all along the tubes.  Frames
# are traded away instead -- the breath is a slow, smooth ramp, so 16 of them at
# 8 fps steps by about one luma level per frame and no one can see the joins.
LOGO_FRAMES = 16                 # must match noOfFrames in interface/mltd.gfx
LOGO_FPS = 8                     # must match animation_rate_fps there
LOGO_PULSE = 0.42                # peak of the neon breath
# The thumbnail's sign sits 18 px from the edge of a 512-wide canvas while its
# outer neon bloom is a Gaussian of sigma 32, so on that canvas the bloom is cut
# flat -- deliberate full bleed for the thumbnail, but as a logo it shows as a
# hard vertical edge (alpha jumped 0 -> 224 in one column).  Rendering the sign
# on a canvas padded by this much, in 512-space, lets the bloom finish.
LOGO_PAD = 96.0
# Where to trim the finished bloom.  Cutting at literally zero would make the
# hexagon small inside the logo, since a Gaussian tail runs on for 3 sigma; this
# is low enough that the step at the edge is invisible.
LOGO_EDGE = 4.0 / 255.0

# --- rain ------------------------------------------------------------------
# The overlay sprite is drawn UNSCALED, at exactly the size of its BASE texture
# -- the one named by `texturefile`, not the scrolling animation textures --
# anchored to the top-left of the `frontend_background` container.  That
# container is 1920x1440 scaled to *cover*, so on any screen wider than 4:3 it
# overflows vertically and its top-left sits ABOVE the top of the screen:
#
#     scale    = max(W / 1920, H / 1440)
#     overflow = (1440 * scale - H) / 2      ... 240 px on 2560x1440
#
# so a sprite only H tall runs out `overflow` px short of the bottom.  This was
# measured the hard way: enlarging the animation textures alone changed nothing,
# because they are sampled *within* the rect the base texture defines.  Hence
# our own base and mask below rather than OWB's, which are 2560x1440 -- and
# almost certainly why OWB ships its snow overlay commented out, since it has
# exactly this shortfall on any 16:9 screen.
#
# For 16:9 the requirement is  height >= 7/6 * H  and  width >= W; at the fixed
# 2560 width the worst case is H = 1440, needing 1680.  1792 leaves margin for
# an overflow up to 352 px.  Ultrawide and 4K need more on both axes: raise
# these two numbers and nothing else.
RAIN_W, RAIN_H = 2560, 1792
# The sprite magnifies by 1 / RAIN_SCALE, so a streak drawn N px long here is
# N / RAIN_SCALE px long on screen.  Keep the two in step when tuning.
RAIN_SCALE = 0.75
# counts are per 2560x1440 and scaled to the real canvas below, so changing
# RAIN_H does not change how heavily it rains
RAIN_LAYERS = (
    # count  length     width  alpha        seed   -- far layer first
    (1100,  (26, 64),   1.3,   (0.22, 0.47), 7701),
    (650,   (50, 120),  2.0,   (0.36, 0.75), 7702),
)
RAIN_RGB = (206, 226, 240)       # OWB's snow sits at (213, 227, 240)
RAIN_MASK_ALPHA = 191            # OWB's mask strength, i.e. 75%

rng = np.random.default_rng(20260911)


def save_dds(img, path, pixel_format=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if pixel_format:
        img.save(path, pixel_format=pixel_format)
    else:
        img.save(path)
    return os.path.getsize(path)


# ===========================================================================
# 1.  MAIN MENU BACKGROUND
# ===========================================================================
def build_background():
    src = Image.open(SRC).convert("RGB")
    art = src.resize((BG_W, int(round(BG_W * src.height / src.width))),
                     Image.LANCZOS)
    top = (BG_H - SAFE_H) // 2
    if art.height != SAFE_H:                       # source is not exactly 16:9
        art = art.resize((BG_W, SAFE_H), Image.LANCZOS)

    a = np.asarray(art).astype(np.float32) / 255.0

    # --- extend into the bands the 4:3 canvas needs and 16:9 never shows.
    #     Mirrored, blurred and pushed down, so if anyone does see them on a
    #     4:3 screen they read as more sky and more water, not as a repeat.
    def band(rows, flip_from_top):
        strip = a[:rows] if flip_from_top else a[-rows:]
        strip = strip[::-1].copy()
        strip = cv2.GaussianBlur(strip, (0, 0), 26)
        fade = np.linspace(0.0, 1.0, rows, dtype=np.float32)
        if flip_from_top:
            fade = fade                             # darkest at the frame edge
        else:
            fade = fade[::-1]
        return strip * (0.34 + 0.66 * fade)[:, None, None]

    canvas = np.zeros((BG_H, BG_W, 3), np.float32)
    canvas[top:top + SAFE_H] = a
    canvas[:top] = band(top, True)
    canvas[top + SAFE_H:] = band(BG_H - top - SAFE_H, False)

    yy, xx = np.mgrid[0:BG_H, 0:BG_W].astype(np.float32)
    ny, nx = yy / BG_H, xx / BG_W

    # the painting is already a cold teal-green; nudge it the last of the way
    # to the mod's abyssal palette and put some violet in the upper corners
    L = canvas @ np.array([0.30, 0.59, 0.11], np.float32)
    canvas = np.clip(canvas * 0.86 + np.dstack([L * 0.10, L * 0.155, L * 0.175]),
                     0, 1)
    corner = (np.clip(np.abs(nx - 0.5) * 2.1 - 0.34, 0, 1) ** 1.5) * \
        (1 - T.smoothstep(ny, 0.05, 0.55))
    canvas = np.clip(canvas + np.array([0.085, 0.020, 0.150], np.float32) *
                     corner[..., None], 0, 1)

    # The logo sits top-centre and the menu buttons run down the left, so
    # darken both -- otherwise the wordmark competes with the lit doorway.
    logo_zone = np.exp(-(((nx - 0.5) / 0.34) ** 2 + ((ny - 0.16) / 0.20) ** 2))
    left_zone = np.clip(1 - nx / 0.40, 0, 1) ** 1.6 * T.smoothstep(ny, 0.12, 0.42)
    canvas *= (1 - 0.42 * logo_zone - 0.22 * left_zone)[..., None].clip(0.30, 1)

    d = np.sqrt(((nx - 0.5) / 0.78) ** 2 + ((ny - 0.5) / 0.78) ** 2)
    canvas *= np.clip(1 - 0.34 * T.smoothstep(d, 0.72, 1.42), 0, 1)[..., None]
    canvas = np.clip((canvas - 0.5) * 1.05 + 0.5, 0, 1)

    img = Image.fromarray(np.clip(canvas * 255, 0, 255).astype(np.uint8)) \
        .convert("RGBA")
    n = save_dds(img, BG_OUT)
    os.makedirs(PREVIEW, exist_ok=True)
    img.convert("RGB").resize((640, 483), Image.LANCZOS) \
        .save(os.path.join(PREVIEW, "main_menu_preview.png"))
    print("wrote %s  %dx%d  %.1f MB" % (BG_OUT, BG_W, BG_H, n / 1048576.0))
    return n


# ===========================================================================
# 2.  HEADER LOGO
# ===========================================================================
class padded_sign_canvas:
    """Render the marquee on a canvas wide enough for its own glow.

    ``build_workshop_thumbnail`` lays the sign out for a 512-wide thumbnail it
    is meant to bleed off, so its outer bloom is clipped by the canvas.  Widen
    the canvas and shift every absolute coordinate the sign builder reads, and
    the same code produces a complete, unclipped sign.  Sizes and differences
    (CH, GAP_HALF, WM_W, SUB_W, `SYM - SY0`) are translation-invariant and are
    left alone; SX0/SX1 are only read at import to build HEXW, so patching
    HEXW covers them.
    """

    KEYS = ("W", "HEXW", "SY0", "SY1", "SYM", "GC", "WM_TOP", "SUB_TOP")

    def __init__(self, pad512=LOGO_PAD):
        self.pad512 = pad512

    def __enter__(self):
        self.saved = {k: getattr(T, k) for k in self.KEYS}
        p = T.scf(self.pad512)
        T.W = int(self.saved["W"] + 2 * p)
        T.HEXW = [(x + p, y + p) for x, y in self.saved["HEXW"]]
        for k in ("SY0", "SY1", "SYM", "GC", "WM_TOP", "SUB_TOP"):
            setattr(T, k, self.saved[k] + self.pad512)
        return self

    def __exit__(self, *exc):
        for k, v in self.saved.items():
            setattr(T, k, v)
        return False


def _sign_rgba():
    """The marquee, cropped to its own glow, as float RGB + alpha."""
    with padded_sign_canvas():
        srgb, sa = T.build_sign(T.build_wordmark(), T.build_subtitle())
    ys, xs = np.nonzero(sa > LOGO_EDGE)
    x0, x1 = xs.min(), xs.max() + 1
    y0, y1 = ys.min(), ys.max() + 1
    rgb = np.clip(srgb[y0:y1, x0:x1], 0, 1)
    a = np.clip(sa[y0:y1, x0:x1], 0, 1)
    edge = max(a[0].max(), a[-1].max(), a[:, 0].max(), a[:, -1].max())
    print("  sign cropped to %dx%d; strongest alpha on the crop border %.3f "
          "(a hard edge would be ~0.9)" % (a.shape[1], a.shape[0], edge))
    return rgb, a


def _fit_logo(rgb, a):
    """Scale to the logo box and sit it low, the way OWB's and tnkd's do."""
    img = Image.fromarray(
        (np.dstack([rgb, a]) * 255).astype(np.uint8), "RGBA")
    k = min(LOGO_W / img.width, LOGO_H / img.height)
    img = img.resize((max(1, int(round(img.width * k))),
                      max(1, int(round(img.height * k)))), Image.LANCZOS)
    out = Image.new("RGBA", (LOGO_W, LOGO_H), (0, 0, 0, 0))
    out.paste(img, ((LOGO_W - img.width) // 2, LOGO_H - img.height - 4), img)
    return out


def build_logo():
    """The marquee on its own, transparent, at OWB's logo dimensions.

    Two files: the static texture, which overrides OWB's by path the way tnkd
    does, and a frame strip whose neon breathes.  The frontend uses the strip;
    the static one is the fallback if another submod's copy of
    frontendmainview.gui wins the load order.
    """
    rgb, a = _sign_rgba()
    out = _fit_logo(rgb, a)
    n = save_dds(out, LOGO_OUT)
    out.save(os.path.join(PREVIEW, "logo_game_static_preview.png"))
    print("wrote %s  %dx%d  %d KB" % (LOGO_OUT, LOGO_W, LOGO_H, n / 1024))

    # --- the breath.  Same construction as the thumbnail GIF's: seed a bloom
    #     from the sign's own bright, chromatic pixels so the violet tube
    #     breathes violet and the teal tube teal, then swell it on a raised
    #     cosine, which is 0 with zero slope at both ends so the loop closes.
    bloom = T.bloom_layer(rgb)
    frames = []
    for f in range(LOGO_FRAMES):
        amt = LOGO_PULSE * (0.5 - 0.5 * math.cos(2 * math.pi * f / LOGO_FRAMES))
        fr = np.clip(rgb + bloom * amt, 0, 1)
        # the glow has to carry alpha too, or it brightens nothing outside the
        # sign and the halo never actually grows
        fa = np.clip(a + T.lum_of(bloom) * amt * 1.35, 0, 1)
        frames.append(_fit_logo(fr, fa))

    strip = Image.new("RGBA", (LOGO_W * LOGO_FRAMES, LOGO_H), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        strip.paste(fr, (i * LOGO_W, 0))
    n += save_dds(strip, LOGO_OUT_ANIM)
    frames[0].save(os.path.join(PREVIEW, "logo_animated_preview.gif"),
                   save_all=True, append_images=frames[1:], loop=0,
                   duration=int(round(1000.0 / LOGO_FPS)), disposal=2,
                   optimize=True)
    print("wrote %s  %dx%d  %d frames @ %d fps  uncompressed  %.1f MB"
          % (LOGO_OUT_ANIM, LOGO_W * LOGO_FRAMES, LOGO_H, LOGO_FRAMES,
             LOGO_FPS, os.path.getsize(LOGO_OUT_ANIM) / 1048576.0))
    return n


# ===========================================================================
# 3.  ANIMATED RAIN
# ===========================================================================
def build_rain_rect():
    """The sprite's own base and mask, at the size the rect has to be.

    The base is transparent everywhere, so only the animations draw; the mask
    is flat, so they draw at even strength across the whole rect.  Both are
    constant images and exist purely to set and fill the rect -- OWB's
    equivalents are identical in content and only 2560x1440, which is what left
    the band along the bottom.
    """
    base = np.zeros((RAIN_H, RAIN_W, 4), np.uint8)
    base[..., :3] = np.array((197, 205, 219), np.uint8)   # OWB's, alpha 0 over it
    n = save_dds(Image.fromarray(base, "RGBA"), RAIN_BASE_OUT, pixel_format="DXT5")

    mask = np.zeros((RAIN_H, RAIN_W, 4), np.uint8)
    mask[..., :3] = 255
    mask[..., 3] = RAIN_MASK_ALPHA
    n += save_dds(Image.fromarray(mask, "RGBA"), RAIN_MASK_OUT, pixel_format="DXT5")
    print("wrote the rain base and mask       %dx%d  DXT5  %.1f MB total"
          % (RAIN_W, RAIN_H, n / 1048576.0))
    return n


def build_rain():
    """Two scrolling rain sheets, drawn to wrap in both axes.

    Colour lives in RGB and shape lives in ALPHA, which is how OWB's snow
    textures are built and what the sprite's "add" blend expects: a flat pale
    RGB with an alpha mask cut out of it.  Streaks are stamped on a 3x3
    lattice so one crossing an edge reappears opposite, because the sprite
    scrolls the texture continuously and any seam would sweep across the
    screen once per cycle.

    Streaks are drawn vertical and kept short.  The scroll direction is set by
    ``animationrotation`` in the sprite, and whether that rotates the texture
    with it is the one thing here that cannot be checked without launching the
    game -- short streaks stay readable as rain either way, long ones would
    not.
    """
    total = 0
    for i, (count, ln, wide, alpha, seed) in enumerate(RAIN_LAYERS, start=1):
        r = np.random.default_rng(seed)
        a = np.zeros((RAIN_H, RAIN_W), np.float32)
        count = int(round(count * (RAIN_W * RAIN_H) / (2560.0 * 1440.0)))
        for _ in range(count):
            h = int(r.uniform(*ln))
            w = max(2, int(round(wide * r.uniform(0.75, 1.3))) + 2)
            v = r.uniform(*alpha)
            # taper along the streak so it fades in and out instead of ending
            # square, and across it so the edges are not aliased
            t = np.linspace(0.0, 1.0, h, dtype=np.float32)
            # clip before the fractional power: sin(pi) lands a hair below zero
            # in float32, and a negative base to a fractional power is NaN --
            # which np.maximum then propagates into the sheet
            along = np.clip(np.sin(np.pi * t), 0.0, None) ** 0.65
            across = np.clip(1.0 - np.linspace(-1.0, 1.0, w,
                                               dtype=np.float32) ** 2, 0, 1) ** 0.6
            patch = v * along[:, None] * across[None, :]
            # modular indexing wraps the streak round the edges for free, which
            # is what keeps the scroll seamless -- a seam would sweep across the
            # screen once per cycle
            ys = (np.arange(h) + int(r.random() * RAIN_H)) % RAIN_H
            xs = (np.arange(w) + int(r.random() * RAIN_W)) % RAIN_W
            sl = np.ix_(ys, xs)
            a[sl] = np.maximum(a[sl], patch)
        a = cv2.GaussianBlur(a, (0, 0), 0.8)
        a = np.clip(a * 255.0, 0, 255)

        rgb = np.zeros((RAIN_H, RAIN_W, 3), np.uint8)
        rgb[...] = np.array(RAIN_RGB, np.uint8)
        img = Image.fromarray(np.dstack([rgb, a.astype(np.uint8)]), "RGBA")
        n = save_dds(img, RAIN_OUT % i, pixel_format="DXT5")
        total += n
        print("wrote %s  %dx%d  DXT5  %.1f MB  (alpha covers %.2f%%)"
              % (RAIN_OUT % i, RAIN_W, RAIN_H, n / 1048576.0,
                 100.0 * (a > 16).mean()))
    return total


# ===========================================================================
# 4.  PREVIEW  (not shipped)
# ===========================================================================
PREVIEW_TIMES = (3.4, 2.3)       # keep in step with animationtime in mltd.gfx
PREVIEW_SCREEN = (2560, 1440)    # the screen the preview models


def frontend_geometry(screen):
    """Where the engine puts the background container and the rain sprite.

    `frontend_background` is 1920x1440 with preserve_aspect_ratio and a 100%
    minimum on both axes, i.e. scaled to *cover* and centred, so on anything
    wider than 4:3 it overflows vertically and its top-left is above the screen.
    The overlay iconType is anchored to that top-left and drawn unscaled, which
    is the whole reason the rain sheets have to be taller than the screen.
    """
    W, H = screen
    scale = max(W / 1920.0, H / 1440.0)
    cw, ch = 1920.0 * scale, 1440.0 * scale
    return scale, (W - cw) / 2.0, (H - ch) / 2.0


def build_preview(screen=PREVIEW_SCREEN, size=(480, 270), frames=24, ms=60):
    """A simulation of the finished menu, for looking at without launching.

    It reproduces the engine's geometry -- cover-scale the background, anchor
    the unscaled rain sprite to the container's overflowing top-left, magnify
    the animation texture by 1 / RAIN_SCALE, scroll it, and add it through
    OWB's flat 191 mask -- so the coverage it reports is meaningful.  It is a
    model, not a capture: the one thing it cannot predict is whether
    `animationrotation` turns the texture along with the scroll direction.
    """
    W, H = screen
    scale, ox, oy = frontend_geometry(screen)

    bg = Image.open(BG_OUT).convert("RGB")
    big = bg.resize((int(round(1920 * scale)), int(round(1440 * scale))),
                    Image.LANCZOS)
    view = Image.new("RGBA", (W, H))
    view.paste(big, (int(round(ox)), int(round(oy))))
    logo = Image.open(LOGO_OUT).convert("RGBA")
    view.alpha_composite(logo, ((W - LOGO_W) // 2, 24))
    base = np.asarray(view.convert("RGB")).astype(np.float32)

    # The rect is the size of the sprite's BASE texture, unscaled, at the
    # container's top-left.  Read it off the file rather than assuming, so the
    # model cannot drift away from what actually ships.
    bw, bh = Image.open(RAIN_BASE_OUT).size
    rx, ry = int(round(ox)), int(round(oy))
    covered = (max(0, ry), min(H, ry + bh), max(0, rx), min(W, rx + bw))
    print("  sprite rect %dx%d (from %s) at (%d,%d); covers rows %d-%d and "
          "cols %d-%d of %dx%d"
          % (bw, bh, os.path.basename(RAIN_BASE_OUT), rx, ry, covered[0],
             covered[1], covered[2], covered[3], W, H))
    if covered[1] < H or covered[3] < W or covered[0] > 0 or covered[2] > 0:
        print("  WARNING: the rain does not reach every edge on this screen -- "
              "raise RAIN_W / RAIN_H")

    sheets = []
    for i in (1, 2):
        t = np.asarray(Image.open(RAIN_OUT % i).convert("RGBA")).astype(np.uint8)
        m = 1.0 / RAIN_SCALE
        sheets.append(np.asarray(Image.fromarray(t, "RGBA").resize(
            (int(RAIN_W * m), int(RAIN_H * m)), Image.LANCZOS)).astype(np.float32))

    out = []
    for f in range(frames):
        frame = base.copy()
        rect = np.zeros((bh, bw, 3), np.float32)
        for sh, t in zip(sheets, PREVIEW_TIMES):
            h, w = sh.shape[:2]
            dy = int((f / frames) * (frames * ms / 1000.0) / t * h) % h
            dx = int(dy * 0.18) % w
            roll = np.roll(np.roll(sh, dy, axis=0), dx, axis=1)[:bh, :bw]
            al = (roll[..., 3:4] / 255.0) * (191.0 / 255.0)
            rect = rect + roll[..., :3] * al
        y0, y1 = max(0, ry), min(H, ry + bh)
        x0, x1 = max(0, rx), min(W, rx + bw)
        frame[y0:y1, x0:x1] = np.clip(
            frame[y0:y1, x0:x1] + rect[y0 - ry:y1 - ry, x0 - rx:x1 - rx], 0, 255)
        out.append(Image.fromarray(frame.astype(np.uint8)).resize(size, Image.LANCZOS))

    path = os.path.join(PREVIEW, "main_menu_preview.gif")
    os.makedirs(PREVIEW, exist_ok=True)
    pal = out[0].quantize(colors=200, method=Image.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in out]
    q[0].save(path, save_all=True, append_images=q[1:], loop=0, duration=ms,
              disposal=1, optimize=True)
    print("wrote %s  %dx%d  %d frames  %.0f KB  (model of %dx%d, not a capture)"
          % (path, size[0], size[1], frames, os.path.getsize(path) / 1024.0,
             W, H))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--only", choices=("background", "logo", "rain"),
                    help="build just one of the three")
    ap.add_argument("--preview", action="store_true",
                    help="also write event_images/workshop/main_menu_preview.gif")
    args = ap.parse_args()
    jobs = {"background": build_background, "logo": build_logo,
            "rain": lambda: build_rain_rect() + build_rain()}
    total = 0
    for name, fn in jobs.items():
        if args.only in (None, name):
            total += fn()
    print("total %.1f MB added to the mod" % (total / 1048576.0))
    if args.preview:
        build_preview()


if __name__ == "__main__":
    main()
