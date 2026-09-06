"""Rebuild the graded M'lulu portrait textures from event_images/portrait/.

Outputs (both override OWB's textures by path, so no .gfx change is needed):
  mod_folder/gfx/leaders/MLT/mlulu.dds                                156x210, uncompressed A8R8G8B8
  mod_folder/gfx/interface/ideas/character_small_icons/MLT_mlulu.dds  65x67, DXT1 (1-bit alpha)

Sources (repo-relative, never shipped):
  event_images/portrait/mlulu_original.png            OWB gfx/leaders/MLT/mlulu.dds decoded losslessly
  event_images/portrait/MLT_mlulu_small_original.png  OWB .../character_small_icons/MLT_mlulu.dds decoded (DXT1)
  event_images/portrait/icon_photo_mask.png           65x67 mask: 255 where the small icon shows the portrait,
                                                      0 on the shared "photo card + paper note" template and the
                                                      transparent surround. Regenerate with --derive-icon-mask
                                                      (needs the OWB Workshop folder): it is the per-pixel majority
                                                      vote of "differs from MLT_mlulu" over the 225 other OWB icons
                                                      that share the template's exact alpha channel.
Provenance: both originals are Old World Blues' own art for the MLT country leader; this file only
colour-grades them (a programmatic grade, not a repaint).

What the grade does, in order (all parameters are in GRADE below):
  1. background mask   - pale, low-saturation pixels connected to the image border (soft, feathered);
  2. creature grade    - exposure, partial desaturation (saturated bright spots such as the eyes are
                         protected), teal shadow fog + cyan midtone tint, mild S-curve;
  3. background        - replaced by a radial abyssal-teal gradient (faint cold light behind the head,
                         corners near black) keeping the original's brush variation;
  4. vignette          - strong, soft, elliptical;
  5. rim / glow        - faint cyan sheen on the brightest creature highlights;
  6. film grain        - light, deterministic (seeded).
The small icon is rebuilt by warping the graded portrait through the same similarity transform OWB
used to place the portrait in the template (fitted by search, see ICON_FIT), so both textures match.

Run from the repo root:
  python build_portrait.py                 # writes both .dds
  python build_portrait.py --preview 3     # also writes preview_v3.png (2x) and _compare_v3.png
  python build_portrait.py --set desaturate=0.35 --set vignette_strength=0.9 --preview 4
"""
from __future__ import annotations

import argparse
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "event_images" / "portrait"
PORTRAIT_SRC = SRC / "mlulu_original.png"
ICON_SRC = SRC / "MLT_mlulu_small_original.png"
ICON_MASK_SRC = SRC / "icon_photo_mask.png"
PORTRAIT_OUT = ROOT / "mod_folder" / "gfx" / "leaders" / "MLT" / "mlulu.dds"
ICON_OUT = ROOT / "mod_folder" / "gfx" / "interface" / "ideas" / "character_small_icons" / "MLT_mlulu.dds"
OWB_ICON_DIR = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196"
                    "/gfx/interface/ideas/character_small_icons")  # only for --derive-icon-mask

PORTRAIT_SIZE = (156, 210)
ICON_SIZE = (65, 67)

# ----------------------------------------------------------------------------------------------
# Grade parameters. Colours are sRGB 0..1; masks use smoothstep(lo, hi, x) ramps.
# ----------------------------------------------------------------------------------------------
GRADE = dict(
    # 1. background detection (pale AND unsaturated AND connected to the border)
    bg_lum_lo=0.64, bg_lum_hi=0.84,         # luminance ramp: 0 below lo, 1 above hi
    bg_sat_lo=0.12, bg_sat_hi=0.42,         # saturation ramp: 1 below lo, 0 above hi
    bg_core=0.55,                           # soft-mask level treated as "certainly background" for the flood fill
    bg_grow=4,                              # px: how far the soft mask may extend past the flooded core
    bg_feather=1.6,                         # gaussian sigma (px) of the final mask edge
    # 2. creature grade
    exposure=-0.28,                         # stops
    desaturate=0.22,                        # 0 = untouched, 1 = grey (the teal fog/tint desaturate warm pixels further)
    glow_protect=0.75,                      # how much saturated bright spots (eyes) resist desaturation
    shadow_fog=(0.00, 0.075, 0.095),        # teal lift added in the shadows (x (1-L)^2)
    shadow_fog_strength=1.0,
    mid_tint=(-0.040, 0.012, 0.045),        # cyan push in the midtones (x 4L(1-L))
    contrast=0.45,                          # 0 = linear, 1 = full smoothstep S-curve
    # 3. background replacement
    bg_centre=(0.0, -0.42),                 # gradient centre in normalised coords (x right, y down; 0,0 = middle)
    bg_radius=(0.95, 1.15),                 # ellipse radii (normalised half-width / half-height units)
    bg_col_centre=(0.075, 0.215, 0.235),    # faint cold light behind the head
    bg_col_edge=(0.006, 0.022, 0.030),      # abyssal corners
    bg_texture=0.35,                        # how much of the original background's brush variation survives
    # 4. vignette
    vig_centre=(0.0, -0.15),
    vig_inner=0.55, vig_outer=1.35,         # elliptical distance where darkening starts / is full
    vignette_strength=0.85,                 # 1 = corners fully black
    # 5. rim / glow on the brightest creature highlights
    rim_col=(0.45, 0.90, 1.00),
    rim_lo=0.50, rim_hi=0.85,               # highlight ramp on graded luminance
    rim_strength=0.08, glow_strength=0.12, glow_sigma=3.0,
    # 6. grain
    grain_amount=0.018, grain_sigma=0.5, grain_seed=20260906,
)

# The small icon shows the portrait at 37x50 px inside the template; the full-size vignette and
# exposure swallow it at that scale, so it gets the same pipeline with these values swapped in.
ICON_GRADE_OVERRIDES = dict(exposure=-0.12, vignette_strength=0.70, vig_outer=1.45, grain_amount=0.012)

# Icon geometry: icon pixel (x, y) -> portrait pixel (u, v):
#   u = (cos(a) x - sin(a) y) * s + tx ;  v = (sin(a) x + cos(a) y) * s + ty
# Fitted by SSD search of the OWB icon's photo pixels against the OWB portrait (rmse 38/255, mostly
# DXT1 + template edge noise). Coverage of the mask is u in [-2, 156], v in [-6, 208]: the whole
# portrait, scaled by 1/4.2 and tilted 4.6 degrees - not a crop.
ICON_FIT = dict(scale=4.20, angle_deg=4.583, tx=-13.833, ty=-32.833)
ICON_SUPERSAMPLE = 2.0   # pre-shrink the graded portrait to this many px per icon px before the warp


# ----------------------------------------------------------------------------------------------
# small numpy helpers (no scipy dependency)
# ----------------------------------------------------------------------------------------------
def smoothstep(lo, hi, x):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def luminance(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def saturation(rgb):
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    return np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)


def gaussian(a, sigma):
    """Separable gaussian blur of a 2-D float array with reflect padding."""
    if sigma <= 0:
        return a.copy()
    r = max(1, int(math.ceil(sigma * 3)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(a, ((r, r), (r, r)), mode="reflect")
    tmp = np.zeros_like(p)
    for i, w in enumerate(k):
        tmp += w * np.roll(p, i - r, axis=1)
    out = np.zeros_like(p)
    for i, w in enumerate(k):
        out += w * np.roll(tmp, i - r, axis=0)
    return out[r:-r, r:-r]


def dilate(m, n=1):
    m = m.astype(bool)
    for _ in range(n):
        p = np.pad(m, 1)
        m = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
             | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:])
    return m


def erode(m, n=1):
    """Binary erosion; pixels outside the array count as background (so the image border erodes)."""
    m = m.astype(bool)
    for _ in range(n):
        p = np.pad(m, 1, constant_values=False)
        m = (p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
             & p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:])
    return m


def flood_from(seed, allowed):
    """Grow `seed` through `allowed` (4/8-connected) until it stops changing."""
    cur = seed & allowed
    while True:
        nxt = dilate(cur, 1) & allowed
        if (nxt == cur).all():
            return cur
        cur = nxt


def norm_coords(h, w):
    """Normalised coordinate grid: x in [-1, 1] across the width, y in [-1, 1] down the height."""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    return (xs + 0.5) / w * 2.0 - 1.0, (ys + 0.5) / h * 2.0 - 1.0


# ----------------------------------------------------------------------------------------------
# the grade
# ----------------------------------------------------------------------------------------------
def background_mask(rgb, region, p):
    """Soft 0..1 mask of the pale background inside `region` (bool), connected to region's border."""
    L = luminance(rgb)
    S = saturation(rgb)
    soft = smoothstep(p["bg_lum_lo"], p["bg_lum_hi"], L) * (1.0 - smoothstep(p["bg_sat_lo"], p["bg_sat_hi"], S))
    soft = soft * region
    core = soft > p["bg_core"]
    border = region & ~erode(region, 1)
    connected = flood_from(border & core, core)
    reach = dilate(connected, p["bg_grow"]) & region
    m = soft * reach
    m = gaussian(m, p["bg_feather"])
    # never let the feather bleed onto pixels outside the region (icon frame / note)
    return np.clip(m, 0.0, 1.0) * region


def grade(rgb, nx, ny, region, p):
    """rgb float32 HxWx3 in 0..1; nx, ny normalised coords; region bool mask of pixels to grade."""
    rgb = rgb.astype(np.float32)
    H, W = rgb.shape[:2]
    orig_L = luminance(rgb)
    bg = background_mask(rgb, region, p)

    # --- 2. creature grade -----------------------------------------------------------------
    c = rgb * (2.0 ** p["exposure"])
    L = luminance(c)
    S = saturation(c)
    protect = smoothstep(0.45, 0.80, S) * smoothstep(0.35, 0.75, L) * p["glow_protect"]
    k = (p["desaturate"] * (1.0 - protect))[..., None]
    c = c * (1.0 - k) + L[..., None] * k
    ws = ((1.0 - L) ** 2)[..., None]
    wm = (4.0 * L * (1.0 - L))[..., None]
    c = c + ws * np.asarray(p["shadow_fog"], np.float32) * p["shadow_fog_strength"] + wm * np.asarray(p["mid_tint"], np.float32)
    c = np.clip(c, 0.0, 1.0)
    c = c * (1.0 - p["contrast"]) + smoothstep(0.0, 1.0, c) * p["contrast"]

    # --- 3. background gradient ------------------------------------------------------------
    cx, cy = p["bg_centre"]
    rx, ry = p["bg_radius"]
    d = np.sqrt(((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2)
    t = smoothstep(0.0, 1.0, np.clip(d, 0.0, 1.0))[..., None]
    grad = np.asarray(p["bg_col_centre"], np.float32) * (1.0 - t) + np.asarray(p["bg_col_edge"], np.float32) * t
    # keep the brush variation of the original background: darker original strokes stay darker
    tex = 1.0 + p["bg_texture"] * (np.clip(orig_L, 0.0, 1.0) - 0.92) / 0.92 * 4.0
    grad = grad * np.clip(tex, 0.3, 1.3)[..., None]
    out = c * (1.0 - bg[..., None]) + grad * bg[..., None]

    # --- 4. vignette -------------------------------------------------------------------------
    vx, vy = p["vig_centre"]
    dv = np.sqrt((nx - vx) ** 2 + (ny - vy) ** 2)
    v = 1.0 - p["vignette_strength"] * smoothstep(p["vig_inner"], p["vig_outer"], dv)
    out = out * v[..., None]

    # --- 5. rim / glow -----------------------------------------------------------------------
    Lg = luminance(out)
    h = smoothstep(p["rim_lo"], p["rim_hi"], Lg) * (1.0 - bg) * region
    glow = gaussian(h, p["glow_sigma"])
    out = out + (glow * p["glow_strength"] + h * p["rim_strength"])[..., None] * np.asarray(p["rim_col"], np.float32)

    # --- 6. grain ----------------------------------------------------------------------------
    rng = np.random.default_rng(p["grain_seed"])
    n = rng.normal(0.0, 1.0, (H, W)).astype(np.float32)
    n = gaussian(n, p["grain_sigma"])
    n /= max(n.std(), 1e-6)
    Lg = luminance(np.clip(out, 0, 1))
    out = out + (n * p["grain_amount"] * (0.35 + 0.65 * np.sqrt(Lg)))[..., None]

    out = np.clip(out, 0.0, 1.0)
    return np.where(region[..., None], out, rgb), bg


def to_u8(rgb):
    return (np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


# ----------------------------------------------------------------------------------------------
# portrait + icon builders
# ----------------------------------------------------------------------------------------------
def build_portrait(p):
    src = Image.open(PORTRAIT_SRC).convert("RGB")
    assert src.size == PORTRAIT_SIZE, src.size
    rgb = np.asarray(src).astype(np.float32) / 255.0
    nx, ny = norm_coords(*rgb.shape[:2])
    region = np.ones(rgb.shape[:2], bool)
    out, bg = grade(rgb, nx, ny, region, p)
    return Image.fromarray(to_u8(out), "RGB"), bg


def icon_affine():
    """PIL AFFINE data mapping icon (x, y) -> supersampled-portrait (u', v')."""
    f = ICON_FIT
    s = f["scale"]
    a = math.radians(f["angle_deg"])
    ss_w = max(1, round(PORTRAIT_SIZE[0] / s * ICON_SUPERSAMPLE))
    ss_h = max(1, round(PORTRAIT_SIZE[1] / s * ICON_SUPERSAMPLE))
    kx = ss_w / PORTRAIT_SIZE[0]
    ky = ss_h / PORTRAIT_SIZE[1]
    ca, sa = math.cos(a), math.sin(a)
    # u = (ca x - sa y) s + tx ; v = (sa x + ca y) s + ty ; then scale to the supersampled image
    data = (ca * s * kx, -sa * s * kx, f["tx"] * kx,
            sa * s * ky, ca * s * ky, f["ty"] * ky)
    return (ss_w, ss_h), data


def build_icon(p):
    """Grade the portrait with ICON_GRADE_OVERRIDES, warp it into the template's photo area."""
    graded_portrait, _ = build_portrait({**p, **ICON_GRADE_OVERRIDES})
    icon = Image.open(ICON_SRC).convert("RGBA")
    assert icon.size == ICON_SIZE, icon.size
    mask = np.asarray(Image.open(ICON_MASK_SRC).convert("L")) > 127
    assert mask.shape == (ICON_SIZE[1], ICON_SIZE[0]), mask.shape
    (ss_w, ss_h), data = icon_affine()
    pre = graded_portrait.resize((ss_w, ss_h), Image.LANCZOS)
    warped = pre.transform(ICON_SIZE, Image.AFFINE, data=data, resample=Image.BICUBIC)
    out = np.asarray(icon).copy()
    out[..., :3][mask] = np.asarray(warped)[mask]
    return Image.fromarray(out, "RGBA")


def derive_icon_mask():
    """Recompute icon_photo_mask.png from the OWB Workshop folder (see module docstring)."""
    ref = np.asarray(Image.open(OWB_ICON_DIR / "MLT_mlulu.dds").convert("RGBA")).astype(int)
    votes = np.zeros(ref.shape[:2], int)
    n = 0
    for f in sorted(OWB_ICON_DIR.glob("*.dds")):
        if f.name == "MLT_mlulu.dds":
            continue
        try:
            o = np.asarray(Image.open(f).convert("RGBA")).astype(int)
        except Exception:
            continue
        if o.shape != ref.shape or not (o[..., 3] == ref[..., 3]).all():
            continue
        votes += np.abs(o[..., :3] - ref[..., :3]).sum(-1) >= 40
        n += 1
    mask = votes > n / 2
    Image.fromarray(mask.astype(np.uint8) * 255, "L").save(ICON_MASK_SRC)
    print(f"{ICON_MASK_SRC.relative_to(ROOT)}: {mask.sum()} photo px from {n} same-template icons")


# ----------------------------------------------------------------------------------------------
# DDS verification (headers must match the class OWB ships)
# ----------------------------------------------------------------------------------------------
def dds_header(path):
    d = path.read_bytes()
    assert d[:4] == b"DDS ", path
    size, flags, h, w, pitch, depth, mips = struct.unpack("<7I", d[4:32])
    pf_size, pf_flags, fourcc, bpp = struct.unpack("<2I4sI", d[76:92])
    return dict(bytes=len(d), w=w, h=h, flags=flags, pf_flags=pf_flags, fourcc=fourcc, bpp=bpp, mips=mips)


def match_owb_dxt1_header(path):
    """Pillow's DXT1 header differs from OWB's in five bookkeeping fields (flags 0x81007 vs 0xa1007,
    linear size 272 vs the real 2312, depth 0 vs 1, mipmap count 0 vs 1, pixel-format bpp 32 vs 0). The
    block data is identical in layout; rewrite those fields so the 128-byte header is the one OWB ships."""
    d = bytearray(path.read_bytes())
    h, w = struct.unpack("<II", d[12:20])
    linear = ((w + 3) // 4) * ((h + 3) // 4) * 8
    assert len(d) == 128 + linear, (len(d), linear)
    struct.pack_into("<I", d, 8, 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000)  # caps|height|width|pixelformat|mipmapcount|linearsize
    struct.pack_into("<I", d, 20, linear)
    struct.pack_into("<I", d, 24, 1)          # depth (OWB's exporter writes 1)
    struct.pack_into("<I", d, 28, 1)          # mipmap count
    struct.pack_into("<I", d, 88, 0)          # pixel-format RGBBitCount (unused for FOURCC formats)
    path.write_bytes(bytes(d))


def write_outputs(portrait, icon):
    PORTRAIT_OUT.parent.mkdir(parents=True, exist_ok=True)
    ICON_OUT.parent.mkdir(parents=True, exist_ok=True)
    portrait.convert("RGBA").save(PORTRAIT_OUT)          # no pixel_format -> uncompressed A8R8G8B8 like OWB
    icon.convert("RGBA").save(ICON_OUT, pixel_format="DXT1")
    match_owb_dxt1_header(ICON_OUT)
    hp = dds_header(PORTRAIT_OUT)
    hi = dds_header(ICON_OUT)
    assert (hp["w"], hp["h"], hp["flags"], hp["pf_flags"], hp["bpp"]) == (156, 210, 0x100f, 0x41, 32), hp
    assert (hi["w"], hi["h"], hi["flags"], hi["pf_flags"], hi["fourcc"], hi["mips"]) == (65, 67, 0xa1007, 0x4, b"DXT1", 1), hi
    for path, hdr in ((PORTRAIT_OUT, hp), (ICON_OUT, hi)):
        re = Image.open(path)
        re.load()
        print(f"{path.relative_to(ROOT)}: {hdr['w']}x{hdr['h']} {hdr['bytes']} bytes pf_flags=0x{hdr['pf_flags']:x} "
              f"fourcc={hdr['fourcc']!r} bpp={hdr['bpp']} -> reopened {re.mode} {re.size}")


def write_preview(n, portrait, icon, bg):
    """preview_vN.png = graded portrait at 2x; compare_vN.png = original | graded | bg mask + icons."""
    big = portrait.resize((PORTRAIT_SIZE[0] * 2, PORTRAIT_SIZE[1] * 2), Image.LANCZOS)
    big.save(SRC / f"preview_v{n}.png")
    orig = Image.open(PORTRAIT_SRC).convert("RGB").resize(big.size, Image.LANCZOS)
    m = Image.fromarray(to_u8(np.repeat(bg[..., None], 3, -1)), "RGB").resize(big.size, Image.NEAREST)
    icon_orig = Image.open(ICON_SRC).convert("RGBA")
    ic_w = ICON_SIZE[0] * 4
    ic_h = ICON_SIZE[1] * 4
    sheet = Image.new("RGB", (big.width * 3 + 20, big.height + ic_h + 30), (40, 40, 40))
    sheet.paste(orig, (0, 0))
    sheet.paste(big, (big.width + 10, 0))
    sheet.paste(m, (big.width * 2 + 20, 0))
    chk = Image.new("RGB", (ic_w * 2 + 10, ic_h), (110, 110, 110))
    chk.paste(icon_orig.resize((ic_w, ic_h), Image.LANCZOS), (0, 0), icon_orig.resize((ic_w, ic_h), Image.LANCZOS))
    ic = icon.resize((ic_w, ic_h), Image.LANCZOS)
    chk.paste(ic, (ic_w + 10, 0), ic)
    sheet.paste(chk, (big.width + 10, big.height + 20))
    sheet.save(SRC / f"compare_v{n}.png")
    print(f"wrote preview_v{n}.png and compare_v{n}.png")


def parse_set(items):
    p = dict(GRADE)
    for it in items or []:
        key, val = it.split("=", 1)
        if key not in p:
            raise SystemExit(f"unknown parameter {key}")
        cur = p[key]
        if isinstance(cur, tuple):
            p[key] = tuple(float(x) for x in val.split(","))
        elif isinstance(cur, int) and not isinstance(cur, bool):
            p[key] = int(val)
        else:
            p[key] = float(val)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--preview", type=int, metavar="N", help="also write event_images/portrait/preview_vN.png")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE", help="override a GRADE parameter")
    ap.add_argument("--derive-icon-mask", action="store_true", help="rebuild icon_photo_mask.png from OWB")
    ap.add_argument("--no-dds", action="store_true", help="do not write the .dds outputs")
    args = ap.parse_args()
    if args.derive_icon_mask:
        derive_icon_mask()
    p = parse_set(args.set)
    portrait, bg = build_portrait(p)
    icon = build_icon(p)
    if args.preview is not None:
        write_preview(args.preview, portrait, icon, bg)
    if not args.no_dds:
        write_outputs(portrait, icon)


if __name__ == "__main__":
    main()
