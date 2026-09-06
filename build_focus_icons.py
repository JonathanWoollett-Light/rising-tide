"""Rebuild Rising Tide's focus icons. Currently one: the dark-purple tome used by the five book focuses.

Output (shipped):
  mod_folder/gfx/interface/goals/mltd_book.dds     92x90, uncompressed A8R8G8B8 (32-bit, straight alpha), 128-byte
                                                   header byte-identical to the source's (flags 0x2100f, 1 mip)
Source (read from the OWB Workshop folder at build time, never copied into the repo):
  <OWB>/gfx/interface/goals/unique/CHO/cho_scriptorium.dds   OWB's "Scriptorium" focus icon: a closed dark-olive
                                                             tome with a grey-blue page block, on a near-black disc
                                                             inside a rose-pink lattice frame with teal medallions
                                                             and orange tassels.
Previews (repo-relative, never shipped, event_images/focus_icons/):
  mltd_book_preview.png   source | result at 4x, and again at 1x, on the focus tree's dark ground (PREVIEW_BG)
  mltd_book_out.png       the result at 1x, lossless (what the .dds holds)
  preview_vN.png          the iteration history (written with --preview preview_vN.png; kept for reference)

Provenance: the texture is Old World Blues' own focus art recoloured programmatically (a deterministic per-pixel
HSV remap plus a tone curve, not a repaint) so it reads as the same object in a darker, colder, purple palette:
  - warm dark leather (cover, disc, shadows)   -> deep violet (hue ~276), saturation floored so it is not just black
  - rose-pink lattice highlights                -> dim purple (hue ~285, darker)
  - teal / green medallions                     -> cold blue-violet
  - grey page block, stone frame, rim highlights -> dim lilac (a tint, not a hue remap)
  - bright orange tassels (the "metal")         -> stay gold, but cooler and slightly desaturated (the only warm accent)
  - everything                                  -> mild S-curve + gamma darkening (~-30 % mean brightness), violet
                                                   lift in the deepest shadows so the blacks are purple-black
Blends between those cases are smoothstep ramps on hue / saturation / value and the candidates are mixed in RGB
(never by averaging hue angles), so neighbouring painted pixels never flip between mappings.
The alpha channel is copied from the source untouched. Fully transparent pixels get RGB = 0 (no hidden hue under
alpha 0); partial-alpha edge pixels are recoloured like the rest.

Run from the repo root:
  python build_focus_icons.py                                   # writes the .dds and the previews
  python build_focus_icons.py --no-write --preview preview_v9.png --set brightness=0.8   # try a tweak
Determinism: pure numpy float64 arithmetic, no randomness; two runs give byte-identical .dds files.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
OWB = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196")
BOOK_SRC = OWB / "gfx/interface/goals/unique/CHO/cho_scriptorium.dds"
BOOK_OUT = ROOT / "mod_folder/gfx/interface/goals/mltd_book.dds"
PREVIEW_DIR = ROOT / "event_images/focus_icons"
BOOK_SIZE = (92, 90)
# The focus tree draws OWB's black scanline tile (alpha ~48/255) over the darkened map; vanilla's
# tiled_focus_bg.dds averages RGB (32,32,31). This is the ground the previews are composited on.
PREVIEW_BG = (24, 26, 30, 255)

# ----------------------------------------------------------------------------------------------
# Recolour parameters. Hues in degrees (0 red, 60 yellow, 120 green, 180 cyan, 240 blue, 300 magenta);
# gains multiply the source channel; ramps are smoothstep(lo, hi, x).
# ----------------------------------------------------------------------------------------------
BOOK = dict(
    # Hue remap as control points  source_hue -> (target_hue, sat_gain, val_gain); linearly interpolated
    # around the circle. Targets all sit in 248..290 so the interpolation never crosses green.
    hue_table=[
        # src   dst    s_gain v_gain
        (335.0, 288.0, 1.00, 0.76),   # rose-pink lattice -> dim purple
        (15.0, 285.0, 1.00, 0.76),
        (28.0, 276.0, 1.35, 1.08),    # warm olive / brown leather, disc, shadows -> deep violet
        (65.0, 276.0, 1.35, 1.08),
        (95.0, 258.0, 1.00, 0.86),    # green medallions -> blue-violet
        (185.0, 250.0, 0.95, 0.86),   # teal medallions -> cold blue-violet
        (225.0, 256.0, 1.00, 0.92),   # steel-blue page highlight stays cold
        (275.0, 272.0, 1.00, 0.92),
        (310.0, 284.0, 1.00, 0.82),
    ],
    violet_sat_min=0.38,          # saturation floor for the dark warm leather so the cover reads violet, not black
    leather_hue_lo=18.0, leather_hue_hi=80.0,   # hue window (deg) in which the floor and the gold test apply
    # bright + saturated warm pixels in the bottom rows are the tassels (the "metal"): keep them gold, just
    # cooler and dimmer. They are red-orange (hue 8-30), i.e. they share a hue band with the rose lattice, so the
    # test also needs the saturation ramp (lattice S~0.32 vs tassel S~0.6) and the row gate (lattice is everywhere,
    # tassels only below row 64 of 90).
    gold_hue=44.0,
    gold_sat_gain=0.82,
    gold_val_gain=1.00,
    gold_hue_lo=4.0, gold_hue_hi=80.0,
    gold_v_lo=0.17, gold_v_hi=0.32,    # tassels sit at V~0.25-0.75; cover/disc are below 0.18
    gold_s_lo=0.34, gold_s_hi=0.52,
    gold_row_lo=58.0, gold_row_hi=64.0,
    # near-greys (page block, stone frame, rim highlights): a lilac tint instead of a hue remap
    neutral_s_lo=0.06, neutral_s_hi=0.20,
    neutral_hue=270.0,
    neutral_tint_sat=0.16,
    neutral_val_gain=0.90,
    # tone: mild S-curve (0 = none, 1 = full smoothstep) then gamma (>1 darkens midtones) then a flat gain.
    # Together they take the mean brightness (HSV value over opaque pixels) down ~30 % against the source.
    s_curve=0.28,
    gamma=1.08,
    brightness=0.78,
    shadow_violet=(0.022, 0.0, 0.050),   # additive lift x (1-L)^2 so the blackest leather has a violet cast
)


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
def smoothstep(lo, hi, x):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def rgb_to_hsv(rgb):
    """rgb float (...,3) in 0..1 -> h in degrees 0..360, s, v."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    v = rgb.max(-1)
    c = v - rgb.min(-1)
    s = np.where(v > 0, c / np.maximum(v, 1e-12), 0.0)
    safe_c = np.where(c > 0, c, 1.0)
    h = np.where(c <= 0, 0.0,
        np.where(v == r, ((g - b) / safe_c) % 6.0,
        np.where(v == g, (b - r) / safe_c + 2.0, (r - g) / safe_c + 4.0)))
    return (h * 60.0) % 360.0, s, v


def hsv_to_rgb(h, s, v):
    h = (h % 360.0) / 60.0
    i = np.floor(h)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    i = i.astype(int) % 6
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def circular_table(table, h):
    """Interpolate (dst, s_gain, v_gain) around the hue circle from sorted control points."""
    src = np.array([row[0] for row in table])
    order = np.argsort(src)
    src = src[order]
    cols = np.array([row[1:] for row in table])[order]
    xs = np.concatenate([src - 360.0, src, src + 360.0])
    out = []
    for k in range(cols.shape[1]):
        ys = np.concatenate([cols[:, k]] * 3)
        out.append(np.interp(h, xs, ys))
    return out


def in_hue_window(h, lo, hi, feather=6.0):
    return smoothstep(lo - feather, lo + feather, h) * (1.0 - smoothstep(hi - feather, hi + feather, h))


def tone_curve(x, s_curve, gamma, brightness):
    """Mild S-curve (blend towards smoothstep(0,1,x)), then gamma, then a flat gain. Applied per RGB channel."""
    x = np.clip(x, 0.0, 1.0)
    s = x * x * (3.0 - 2.0 * x)
    x = x * (1.0 - s_curve) + s * s_curve
    return np.clip(x ** gamma * brightness, 0.0, 1.0)


# ----------------------------------------------------------------------------------------------
# recolour
# ----------------------------------------------------------------------------------------------
def recolour_book(rgba_u8, p):
    a = rgba_u8[..., 3].astype(np.float64) / 255.0
    rgb = rgba_u8[..., :3].astype(np.float64) / 255.0
    h, s, v = rgb_to_hsv(rgb)

    # 1. chroma candidate: hue remapped through the table, gains applied, violet floor on dark warm leather
    h_map, s_gain, v_gain = circular_table(p["hue_table"], h)
    w_warm = in_hue_window(h, p["leather_hue_lo"], p["leather_hue_hi"])
    rows = np.arange(h.shape[0], dtype=np.float64)[:, None] * np.ones_like(h)
    w_gold = (in_hue_window(h, p["gold_hue_lo"], p["gold_hue_hi"])
              * smoothstep(p["gold_v_lo"], p["gold_v_hi"], v)
              * smoothstep(p["gold_s_lo"], p["gold_s_hi"], s)
              * smoothstep(p["gold_row_lo"], p["gold_row_hi"], rows))
    w_leather = w_warm * (1.0 - smoothstep(p["gold_v_lo"], p["gold_v_hi"], v))
    s_chroma = np.maximum(s * s_gain, p["violet_sat_min"] * w_leather)
    chroma = hsv_to_rgb(h_map, np.clip(s_chroma, 0, 1), np.clip(v * v_gain, 0, 1))

    # 2. gold candidate for the fittings / tassels
    gold = hsv_to_rgb(np.full_like(h, p["gold_hue"]), np.clip(s * p["gold_sat_gain"], 0, 1),
                      np.clip(v * p["gold_val_gain"], 0, 1))

    # 3. neutral candidate for greys
    w_neu = 1.0 - smoothstep(p["neutral_s_lo"], p["neutral_s_hi"], s)
    neutral = hsv_to_rgb(np.full_like(h, p["neutral_hue"]), np.clip(s + p["neutral_tint_sat"], 0, 1),
                         np.clip(v * p["neutral_val_gain"], 0, 1))

    out = chroma * (1 - w_gold[..., None]) + gold * w_gold[..., None]
    out = out * (1 - w_neu[..., None]) + neutral * w_neu[..., None]

    # 4. tone curve + violet shadow lift
    out = tone_curve(out, p["s_curve"], p["gamma"], p["brightness"])
    lum = out @ np.array([0.2126, 0.7152, 0.0722])
    out = out + np.array(p["shadow_violet"]) * ((1.0 - lum) ** 2)[..., None]
    out = np.clip(out, 0, 1)

    # 5. no hue under fully transparent pixels; alpha copied verbatim
    out[a <= 0.0] = 0.0
    res = np.empty_like(rgba_u8)
    res[..., :3] = np.round(out * 255.0).astype(np.uint8)
    res[..., 3] = rgba_u8[..., 3]
    return res


def report(src_u8, out_u8, p):
    """Numbers to steer the parameters by: brightness change and where the main colour groups landed."""
    s = src_u8.astype(np.float64) / 255.0
    o = out_u8.astype(np.float64) / 255.0
    op = s[..., 3] > 0.5
    hs, ss, vs = rgb_to_hsv(s[..., :3])
    ho, so, vo = rgb_to_hsv(o[..., :3])
    print(f"  mean V (opaque)   source {vs[op].mean():.3f} -> result {vo[op].mean():.3f} "
          f"({(vo[op].mean() / vs[op].mean() - 1) * 100:+.0f} %)")
    groups = {
        "leather/disc": op & (hs > p["leather_hue_lo"]) & (hs < p["leather_hue_hi"]) & (vs < 0.18) & (ss > 0.15),
        "rose lattice": op & ((hs > 330) | (hs < 20)) & (ss > 0.2) & (ss < 0.45) & (vs > 0.3),
        "teal medallion": op & (hs > 120) & (hs < 200) & (ss > 0.2),
        "greys": op & (ss < 0.08) & (vs > 0.2),
        "tassels (gold)": op & (hs > 4) & (hs < 60) & (ss > 0.5) & (vs > 0.35)
                          & (np.arange(hs.shape[0])[:, None] > 60),
    }
    for name, m in groups.items():
        if m.sum():
            print(f"  {name:15s} {m.sum():5d} px  hue {ho[m].mean():5.1f}  sat {so[m].mean():.2f}  "
                  f"val {vs[m].mean():.2f} -> {vo[m].mean():.2f}")
    assert np.array_equal(src_u8[..., 3], out_u8[..., 3]), "alpha changed"
    assert not out_u8[src_u8[..., 3] == 0][..., :3].any(), "colour under alpha 0"


# ----------------------------------------------------------------------------------------------
# DDS output: Pillow writes uncompressed A8R8G8B8 with flags 0x100f / depth 0 / mipmapcount 0; OWB's goal
# icons (4,207 of 7,334) carry flags 0x2100f / depth 1 / mipmapcount 1 with the same single mip level. Patch
# those three dwords so the header class matches the source byte-for-byte; the pixel block is identical.
# ----------------------------------------------------------------------------------------------
def dds_header(path):
    d = path.read_bytes()
    assert d[:4] == b"DDS ", path
    size, flags, h, w, pitch, depth, mips = struct.unpack("<7I", d[4:32])
    pf_size, pf_flags, fourcc, bpp = struct.unpack("<2I4sI", d[76:92])
    return dict(bytes=len(d), w=w, h=h, flags=flags, pitch=pitch, depth=depth, mips=mips,
                pf_flags=pf_flags, fourcc=fourcc, bpp=bpp)


def write_dds_like_source(img, out_path, src_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGBA").save(out_path)          # no pixel_format kwarg -> uncompressed A8R8G8B8
    d = bytearray(out_path.read_bytes())
    src = src_path.read_bytes()
    for off in (8, 24, 28):                      # flags, depth, mipmapcount
        d[off:off + 4] = src[off:off + 4]
    out_path.write_bytes(bytes(d))
    hs, ho = dds_header(src_path), dds_header(out_path)
    assert src[:128] == bytes(d[:128]), "header differs from the source's"
    assert len(d) == len(src), (len(d), len(src))
    assert (ho["w"], ho["h"], ho["pf_flags"], ho["bpp"], ho["fourcc"]) == (BOOK_SIZE[0], BOOK_SIZE[1], 0x41, 32, b"\0\0\0\0"), ho
    re = Image.open(out_path)
    re.load()
    assert np.array_equal(np.array(re.convert("RGBA")), np.array(img.convert("RGBA"))), "round trip differs"
    print(f"{out_path.relative_to(ROOT)}: {ho['w']}x{ho['h']} {ho['bytes']} bytes flags=0x{ho['flags']:x} "
          f"mips={ho['mips']} pf_flags=0x{ho['pf_flags']:x} bpp={ho['bpp']} (source: {hs['bytes']} bytes, "
          f"flags=0x{hs['flags']:x}) -> reopened {re.mode} {re.size}; sha256 "
          f"{hashlib.sha256(bytes(d)).hexdigest()[:16]}...")


def write_previews(src_img, out_img, name, scale=4):
    """source | result at `scale`x, and the same pair at 1x underneath, on the focus tree's dark ground."""
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out_img.save(PREVIEW_DIR / "mltd_book_out.png")
    w, h = src_img.size
    canvas = Image.new("RGBA", ((w * 2 + 3) * scale, (h + 2) * scale + h + 2), PREVIEW_BG)
    for i, im in enumerate((src_img, out_img)):
        x = (1 + i * (w + 1)) * scale
        canvas.alpha_composite(im.resize((w * scale, h * scale), Image.NEAREST), (x, scale))
        canvas.alpha_composite(im, (x, (h + 2) * scale + 1))
    canvas.convert("RGB").save(PREVIEW_DIR / name)
    print(f"previews -> {PREVIEW_DIR.relative_to(ROOT)}/{name}, mltd_book_out.png")


def parse_set(items):
    out = {}
    for item in items or []:
        k, _, val = item.partition("=")
        if k not in BOOK or k == "hue_table":
            raise SystemExit(f"unknown parameter {k!r}")
        out[k] = type(BOOK[k])(eval(val)) if not isinstance(BOOK[k], tuple) else tuple(eval(val))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", action="append", metavar="KEY=VALUE", help="override a BOOK parameter")
    ap.add_argument("--preview", default="mltd_book_preview.png", metavar="NAME",
                    help="preview file name inside event_images/focus_icons/ (default mltd_book_preview.png)")
    ap.add_argument("--no-write", action="store_true", help="previews only, do not touch mod_folder")
    args = ap.parse_args()
    p = dict(BOOK, **parse_set(args.set))

    src = Image.open(BOOK_SRC)
    src.load()
    assert src.size == BOOK_SIZE, src.size
    src = src.convert("RGBA")
    src_u8 = np.array(src)
    out_u8 = recolour_book(src_u8, p)
    report(src_u8, out_u8, p)
    out = Image.fromarray(out_u8, "RGBA")
    write_previews(src, out, args.preview)
    if not args.no_write:
        write_dds_like_source(out, BOOK_OUT, BOOK_SRC)


if __name__ == "__main__":
    main()
