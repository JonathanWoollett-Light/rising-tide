"""Rebuild MLT's three melee technology icons: the Cultist Knife and the Conch Knife (OWB's art, made smaller, lifted
and given a fresh shadow) and the Tridents (ours: MLT's Heavy Melee Weaponry).

How the game uses them: a tech's icon is the sprite GFX_<tech_id>_medium, and the engine first looks for
GFX_<TAG>_<tech_id>_medium - that is how OWB gives MLT (and DIS) the Cultist Knife and the Conch Knife
(interface/z_fallout_technologies_faction.gfx, GFX_MLT_melee_weaponry_tech_1_medium / _2_medium). The equipment a
tech unlocks has no sprite of its own and inherits the tech's. All three sprites are declared in
mod_folder/interface/z_mltd_technologies_faction.gfx: the third is a new name, the first two are OWB's names
re-pointed at our textures, which needs a file that sorts after OWB's (see that file's header). The Tridents' name
comes from the loc keys MLT_melee_equipment_3(_short, _desc) in mltd_l_english.yml, like OWB's MLT_melee_equipment_2.

Output (shipped; mod_folder/gfx/interface/equipment/cosmetic/melee/):
  mltd_melee_weaponry_tech_icon_1_cultist_knife.dds   MLT's Basic Melee Weaponry
  mltd_melee_weaponry_tech_icon_2_conch_knife.dds     MLT's Conch Knife
  mltd_melee_weaponry_tech_icon_3_trident.dds         MLT's Tridents
      each 130x60, uncompressed A8R8G8B8 (32-bit, straight alpha), 128-byte header byte-identical to OWB's
      melee_weaponry_tech_icon_2_conch_knife.dds (flags 0x2100f, depth 1, 1 mip; 31,328 bytes). 130x60 is the size of
      1,220 of OWB's 1,250 equipment icons, and the unit, division-designer and pop-up views draw the sprite from its
      top-left corner, so a wider texture (OWB has a few: its 160x38 anti-tank gun) would overflow there.
Sources:
  event_images/tech_icons/trident_src.webp   640x640 RGBA cut-out of a trident on a transparent ground, lying at
                                             ~44 deg, head to the upper right (origin and licence:
                                             event_images/SOURCES.md)
  <OWB>/gfx/interface/equipment/cosmetic/melee/melee_weaponry_tech_icon_1_cultist_knife.dds, ..._2_conch_knife.dds
                                             read from the OWB Workshop folder at build time, never copied into the
                                             repo. DIS uses the same two textures, which is why we re-point MLT's
                                             sprites instead of overriding the textures by path.
Previews (event_images/tech_icons/, never shipped):
  mlt_melee_preview.png   per tier, OWB's icon and ours at 3x on the tech tree's item background, then the three as a
                          row at 1x on the available and the researched background
  <icon>_out.png          each result at 1x, lossless (what the .dds holds)

The tech box (countrytechtreeview.gui, techtree_fallout_infantry_folder_item: 183x84, vanilla's
technology_*_item_bg.dds) draws the icon centred on (91, 50), so the 60-px texture covers box rows 20-79. Measured off
the background: the name band ends at row 17, the main panel is rows 18-64, a darker strip runs along rows 65-78 and
the frame closes at 79. An object centred in its texture (row 50) therefore sits 9 px below the panel's centre, and
OWB's Conch Knife (47 px tall) reached row 72 with its glow on the frame. CENTRE_Y puts the vertical centre of all
three objects on texture row 24 (box row 44), which keeps the tallest of them, the rescaled Conch Knife (box rows
26-61), inside the panel with its glow ending where the strip begins.

What it does:
  - the two knives (kind "owb"): the object is cut out of OWB's icon, scaled by `scale` about its horizontal centre
    (LANCZOS through a sub-pixel source box, then a light unsharp mask; OWB's colours are not touched) and given
    the same generated glow as the trident, so all three carry one shadow. The cut is by alpha: OWB's icons are an
    opaque object, a 1-2 px anti-aliased edge and a pure-black glow whose alpha next to the object is ~185
    (GLOW_EDGE; the 99th percentile of the colourless pixels is 184 on the Cultist Knife), so the object's own alpha
    is (A - GLOW_EDGE) / (255 - GLOW_EDGE). A first version scaled the whole icon, glow included: the glow came out
    thinner and softer than the trident's (163 / 89 / 42 / 15 at 1-4 px), and the Conch Knife's faint coloured wisps,
    which OWB's icon carries up to 12 px from the shell, were smeared into it. The cut drops those wisps.
  - the trident (kind "cutout"), all measured off OWB's 73 melee icons:
      tilt   flat, head to the right, like MLT's other two. The source's axis is found by PCA on its opaque pixels
             and then trued on the haft alone (shaft_slope), because the head's bulk pulls the PCA axis off it. A
             first version lay at 21.5 deg, as OWB's gut harpoon (21.9) and war glaive (20.3) do: it filled the frame
             corner to corner and its tines, butt and glow were cut by the texture's edge.
      fit    fit_w = 120: the longest the trident can be with nothing cut. It is five times longer than it is wide,
             so the width is what limits it, and the 5 px glow has to fit past either tip: at 120 the strongest
             alpha left on the texture's border is 6, which cannot be seen (118 leaves 0). At 128, edge to edge as
             OWB's swords and machetes are (border alpha 53-250), the glow past both tips was cut square at alpha 166
             and read in game as the ends being cropped. report prints the border's strongest alpha.
      grade  a mild gamma lift and gain, because the source is a dark render (median luminance 50 against OWB's
             solid-pixel median of 70) and a 6x downscale greys it further; then an unsharp mask.
      glow   every OWB icon carries the same pure-black outer glow. Its alpha by distance from the object, averaged
             over the gut harpoon, war glaive and katana, is GLOW (165 / 110 / 70 / 28 / 4 at 1-5 px). Reproduced
             from a distance transform taken at 4x and box-filtered down (GLOW_OFFSET calibrates it against OWB's by
             the same measurement, which `report` prints).
All resampling is done on premultiplied alpha, so no dark or light fringe is pulled in from under alpha 0.

Run from the repo root (needs OWB and vanilla installed):
  python build_tech_icons.py                                  # writes the three .dds and the previews
  python build_tech_icons.py --no-write --set scale=0.9       # try a tweak, previews only
  python build_tech_icons.py --icon trident --set fit_w=128   # the trident edge to edge (its glow is cut)
Determinism: no randomness; two runs give byte-identical .dds files.
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent
OWB = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196")
VANILLA = Path("C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV")
OWB_MELEE = OWB / "gfx/interface/equipment/cosmetic/melee"
OUT_DIR = ROOT / "mod_folder/gfx/interface/equipment/cosmetic/melee"
HEADER_REF = OWB_MELEE / "melee_weaponry_tech_icon_2_conch_knife.dds"
PREVIEW_DIR = ROOT / "event_images/tech_icons"
PREVIEW = "mlt_melee_preview.png"
ICON_SIZE = (130, 60)
SS = 4                                  # supersampling of the glow's distance transform
# The tech box (see the docstring): a 183x84 window, icon centred on (91, 50); rows measured off the background.
ITEM_BGS = [VANILLA / "gfx/interface/techtree/technology_available_item_bg.dds",
            VANILLA / "gfx/interface/techtree/technology_researched_item_bg.dds"]
ITEM_ICON_CENTRE = (91, 50)
ITEM_PANEL_ROWS = (18, 64)
ITEM_STRIP_ROWS = (65, 78)
PREVIEW_BG = (24, 26, 30, 255)
LUMA = np.array([0.2126, 0.7152, 0.0722])

# Black outer glow: alpha (0-255) at 0, 1, 2 ... px from the object, measured off OWB's icons (see the docstring).
# The object's own anti-aliased edge adds to the first ring, so the lookup starts GLOW_OFFSET px out: at 0.4 the
# result measures ~179 / 112 / 67 / 28 / 5 by the same ruler (report), the closest fit to OWB's.
GLOW = [255.0, 165.0, 110.0, 70.0, 28.0, 4.0, 0.0]
GLOW_OFFSET = 0.4
# The alpha of OWB's glow right beside the object; above it a pixel is (partly) object. See the docstring.
GLOW_EDGE = 185.0

# The vertical centre of every object, in texture rows (the texture's own centre is 30). See the docstring.
CENTRE_Y = 24.0

ICONS = {
    "cultist_knife": dict(
        kind="owb", tier=1,
        src="melee_weaponry_tech_icon_1_cultist_knife.dds",
        out="mltd_melee_weaponry_tech_icon_1_cultist_knife.dds",
        scale=0.76,
        gamma=1.0, gain=1.0, saturation=1.0,
        sharpen_radius=0.7, sharpen_amount=0.6,
    ),
    "conch_knife": dict(
        kind="owb", tier=2,
        src="melee_weaponry_tech_icon_2_conch_knife.dds",
        out="mltd_melee_weaponry_tech_icon_2_conch_knife.dds",
        scale=0.76,
        gamma=1.0, gain=1.0, saturation=1.0,
        sharpen_radius=0.7, sharpen_amount=0.6,
    ),
    "trident": dict(
        kind="cutout", tier=3,
        src="event_images/tech_icons/trident_src.webp",
        out="mltd_melee_weaponry_tech_icon_3_trident.dds",
        tilt=0.0,                       # degrees above horizontal; 0 = flat, head to the right
        fit_w=120.0, fit_h=48.0,        # the object's box inside the 130x60 icon; 120 is the longest with nothing cut
        gamma=0.86,                     # < 1 lifts the midtones
        gain=1.12,
        saturation=1.10,
        sharpen_radius=0.7, sharpen_amount=0.9,
    ),
}


def premultiplied(img):
    a = np.asarray(img.convert("RGBA"), dtype=np.float64)
    pm = a.copy()
    pm[..., :3] *= a[..., 3:4] / 255.0
    return a, pm


def object_mask(rgba):
    """The painted object of a finished icon: solid and lit, i.e. not the black glow around it."""
    return (rgba[..., 3] > 200) & (rgba[..., :3] @ LUMA > 12)


def axis_angle(alpha):
    """Angle (degrees, y up) of the principal axis of the opaque pixels."""
    ys, xs = np.where(alpha > 0.5)
    w, v = np.linalg.eigh(np.cov(np.vstack([xs, -ys])))
    ax = v[:, -1]
    return float(np.degrees(np.arctan2(ax[1], ax[0])) % 180.0)


def shaft_slope(pm, lo=0.08, hi=0.55):
    """Residual tilt (degrees, y up) of the haft of an object already laid roughly flat with its head to the right:
    a line through the alpha-weighted centre of each column between `lo` and `hi` of its length, which is haft
    only - clear of the butt cap and of the head."""
    al = pm[..., 3]
    ys, xs = np.where(al > 127.0)
    x0, x1 = xs.min(), xs.max()
    cols = np.arange(int(x0 + lo * (x1 - x0)), int(x0 + hi * (x1 - x0)))
    rows = np.arange(al.shape[0], dtype=np.float64)
    cy = np.array([(al[:, c] * rows).sum() / al[:, c].sum() for c in cols])
    return float(np.degrees(np.arctan(-np.polyfit(cols, cy, 1)[0])))      # image rows run down


def resample(pm, fn):
    """Apply a PIL operation to a premultiplied float RGBA array, channel by channel (mode F keeps the precision)."""
    return np.stack([np.asarray(fn(Image.fromarray(np.ascontiguousarray(pm[..., k], dtype=np.float32), "F")),
                                dtype=np.float64) for k in range(4)], -1)


def clamped(pm):
    pm[..., 3] = np.clip(pm[..., 3], 0.0, 255.0)
    pm[..., :3] = np.clip(pm[..., :3], 0.0, pm[..., 3:4])         # premultiplied: colour never exceeds alpha
    return pm


def fitted(pm, box, canvas, centre):
    """Scale the object's alpha bounding box into `box` (keeping aspect) and put its centre on `centre`; LANCZOS."""
    ys, xs = np.where(pm[..., 3] > 127.0)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    s = min(box[0] / (x1 - x0), box[1] / (y1 - y0))
    # a margin around the crop so LANCZOS sees the anti-aliased edge and the transparent ground beyond it
    m = 8
    crop = np.pad(pm, ((m, m), (m, m), (0, 0)))[y0:y1 + 2 * m, x0:x1 + 2 * m]
    w, h = max(1, round(crop.shape[1] * s)), max(1, round(crop.shape[0] * s))
    small = resample(crop, lambda im: im.resize((w, h), Image.LANCZOS))
    out = np.zeros((canvas[1], canvas[0], 4))
    ox, oy = round(centre[0] - w / 2.0), round(centre[1] - h / 2.0)
    sx0, sy0 = max(0, -ox), max(0, -oy)
    dx0, dy0 = max(0, ox), max(0, oy)
    cw, ch = min(w - sx0, canvas[0] - dx0), min(h - sy0, canvas[1] - dy0)
    out[dy0:dy0 + ch, dx0:dx0 + cw] = small[sy0:sy0 + ch, sx0:sx0 + cw]
    return clamped(out), s


def cut_out(pm):
    """The object of a finished OWB icon without its glow, premultiplied. The glow is pure black, so the icon's
    premultiplied colour already is the object's; only the alpha has to be told apart (GLOW_EDGE)."""
    obj = pm.copy()
    obj[..., 3] = np.clip((pm[..., 3] - GLOW_EDGE) / (255.0 - GLOW_EDGE), 0.0, 1.0) * 255.0
    return clamped(obj)


def rescaled(obj, s, centre_y, ss=1):
    """A cut-out object scaled by `s` about the icon's horizontal centre, with its vertical centre put on
    `centre_y`, rendered at `ss` x. LANCZOS through a sub-pixel source box, so the placement is exact."""
    ys, _ = np.where(obj[..., 3] > 127.0)
    cy = (ys.min() + ys.max() + 1) / 2.0
    m = 40                                                          # transparent ground for the box to reach into
    pad = np.pad(obj, ((m, m), (m, m), (0, 0)))
    W, H = ICON_SIZE
    x0 = W / 2.0 * (1.0 - 1.0 / s) + m
    y0 = cy - centre_y / s + m
    box = (x0, y0, x0 + W / s, y0 + H / s)
    return clamped(resample(pad, lambda im: im.resize((W * ss, H * ss), Image.LANCZOS, box=box)))


def over_glow(obj, alpha_ss):
    """The object over OWB's black glow, generated from its alpha at SS x: the glow adds alpha and no colour."""
    oa = obj[..., 3] / 255.0
    return straight(obj[..., :3], oa + (outer_glow(alpha_ss) / 255.0) * (1.0 - oa))


def grade(pm, p):
    """Gamma, gain, saturation and an unsharp mask on the straight colour; returns premultiplied again."""
    a = pm[..., 3:4] / 255.0
    rgb = np.where(a > 0, pm[..., :3] / np.maximum(a, 1e-9), 0.0) / 255.0
    rgb = np.clip(rgb, 0, 1) ** p["gamma"] * p["gain"]
    lum = rgb @ LUMA
    rgb = np.clip(lum[..., None] + (rgb - lum[..., None]) * p["saturation"], 0, 1)
    # unsharp on premultiplied colour so the transparent ground cannot bleed in; alpha stays as it is
    prem = rgb * a
    blur = np.stack([ndi.gaussian_filter(prem[..., k], p["sharpen_radius"]) for k in range(3)], -1)
    prem = np.clip(prem + (prem - blur) * p["sharpen_amount"], 0.0, a)
    return np.concatenate([prem * 255.0, pm[..., 3:4]], -1)


def outer_glow(alpha_ss):
    """OWB's black glow from the object's alpha at SS x: distance transform, GLOW lookup, box filter down."""
    d = ndi.distance_transform_edt(alpha_ss <= 127.0) / SS + GLOW_OFFSET
    g = np.interp(d, np.arange(len(GLOW), dtype=np.float64), GLOW)
    g[alpha_ss > 127.0] = GLOW[0]
    h, w = g.shape
    return g.reshape(h // SS, SS, w // SS, SS).mean(axis=(1, 3))


def straight(pm_rgb, alpha):
    """Premultiplied colour and a (0-1) alpha -> the RGBA image the .dds holds; no colour under alpha 0."""
    rgb = np.where(alpha[..., None] > 0, pm_rgb / 255.0 / np.maximum(alpha[..., None], 1e-9), 0.0)
    res = np.zeros((ICON_SIZE[1], ICON_SIZE[0], 4), dtype=np.uint8)
    res[..., :3] = np.round(np.clip(rgb, 0, 1) * 255.0)
    res[..., 3] = np.round(np.clip(alpha, 0, 1) * 255.0)
    res[res[..., 3] == 0] = 0
    return Image.fromarray(res, "RGBA")


def build_cutout(p):
    src = Image.open(ROOT / p["src"])
    a, pm = premultiplied(src)

    def turned(deg):                                            # clockwise, so negative for PIL
        return resample(pm, lambda im: im.rotate(-deg, resample=Image.BICUBIC, expand=True))

    flat = axis_angle(a[..., 3] / 255.0)                        # the turn that lays the PCA axis flat
    flat += shaft_slope(turned(flat))                           # ... and then the haft itself
    turn = flat - p["tilt"]
    rot = turned(turn)
    fit, centre = (p["fit_w"], p["fit_h"]), (ICON_SIZE[0] / 2.0, CENTRE_Y)
    obj, scale = fitted(rot, fit, ICON_SIZE, centre)
    obj = grade(obj, p)
    big, _ = fitted(rot, (fit[0] * SS, fit[1] * SS), (ICON_SIZE[0] * SS, ICON_SIZE[1] * SS),
                    (centre[0] * SS, centre[1] * SS))
    out = over_glow(obj, big[..., 3])
    print(f"  source {src.size[0]}x{src.size[1]}, turned {turn:.1f} deg clockwise, scaled x{scale:.4f}")
    return None, out


def build_owb(p):
    src = Image.open(OWB_MELEE / p["src"])
    assert src.size == ICON_SIZE, src.size
    _, pm = premultiplied(src)
    cut = cut_out(pm)
    obj = grade(rescaled(cut, p["scale"], CENTRE_Y), p)
    print(f"  OWB's {p['src']}, cut out and scaled x{p['scale']:.2f}")
    return src.convert("RGBA"), over_glow(obj, rescaled(cut, p["scale"], CENTRE_Y, SS)[..., 3])


def report(out, before=None):
    def extent(img):
        a = np.asarray(img, dtype=np.float64)
        ys, xs = np.where(object_mask(a))
        gy, gx = np.where(a[..., 3] > 8)
        return a, (xs.min(), xs.max(), ys.min(), ys.max()), (gx.min(), gx.max(), gy.min(), gy.max())

    top = ITEM_ICON_CENTRE[1] - ICON_SIZE[1] // 2                 # the box row of texture row 0
    a, o, g = extent(out)
    if before is not None:
        _, bo, bg = extent(before)
        print(f"  OWB's:  object x {bo[0]}-{bo[1]} y {bo[2]}-{bo[3]}; in the tech box rows {bo[2] + top}-{bo[3] + top}, "
              f"glow to row {bg[3] + top}")
    print(f"  ours:   object x {o[0]}-{o[1]} y {o[2]}-{o[3]}; in the tech box rows {o[2] + top}-{o[3] + top}, "
          f"glow to row {g[3] + top}  (panel rows {ITEM_PANEL_ROWS[0]}-{ITEM_PANEL_ROWS[1]}, "
          f"strip {ITEM_STRIP_ROWS[0]}-{ITEM_STRIP_ROWS[1]})")
    al = a[..., 3]
    border = max(al[0].max(), al[-1].max(), al[:, 0].max(), al[:, -1].max())
    solid = object_mask(a)
    d = ndi.distance_transform_edt(~solid)
    ring = [al[(d > k - 0.5) & (d <= k + 0.5)].mean() for k in range(1, 6)]
    print(f"  strongest alpha on the texture's border {border:.0f}  (OWB's flat knives 0, swords 53-81, machete 250); "
          f"mean luminance {(a[..., :3] @ LUMA)[solid].mean():.1f}  (OWB median 70)")
    print("  glow alpha at 1-5 px: " + " / ".join(f"{v:.0f}" for v in ring) + "  (OWB 165 / 110 / 70 / 28 / 4)")


# ----------------------------------------------------------------------------------------------
# DDS output: Pillow writes uncompressed A8R8G8B8 with flags 0x100f / depth 0 / mipmapcount 0; OWB's cosmetic
# melee icons carry flags 0x2100f / depth 1 / mipmapcount 1 with the same single mip level. Patch those three
# dwords so the header matches OWB's Conch Knife byte-for-byte; the pixel block is identical.
# ----------------------------------------------------------------------------------------------
def write_dds_like_owb(img, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGBA").save(out_path)          # no pixel_format kwarg -> uncompressed A8R8G8B8
    d = bytearray(out_path.read_bytes())
    ref = HEADER_REF.read_bytes()
    for off in (8, 24, 28):                      # flags, depth, mipmapcount
        d[off:off + 4] = ref[off:off + 4]
    out_path.write_bytes(bytes(d))
    assert ref[:128] == bytes(d[:128]), "header differs from OWB's Conch Knife"
    assert len(d) == len(ref), (len(d), len(ref))
    h, w = struct.unpack("<2I", d[12:20])
    assert (w, h) == ICON_SIZE, (w, h)
    re = Image.open(out_path)
    re.load()
    assert np.array_equal(np.array(re.convert("RGBA")), np.array(img.convert("RGBA"))), "round trip differs"
    flags, = struct.unpack("<I", d[8:12])
    print(f"  {out_path.relative_to(ROOT)}: {w}x{h} {len(d)} bytes flags=0x{flags:x} -> reopened {re.mode} {re.size}; "
          f"sha256 {hashlib.sha256(bytes(d)).hexdigest()[:16]}...")


def write_preview(built, scale=3):
    """Per tier: OWB's icon | ours at `scale`x on the available item. Below: the three as a row at 1x, OWB's first
    (the tiers it has), then ours on the available and on the researched background."""
    bgs = [Image.open(b).convert("RGBA") for b in ITEM_BGS if b.exists()]
    bw, bh = (bgs[0].size if bgs else (183, 84))
    flat = Image.new("RGBA", (bw, bh), (40, 44, 40, 255))

    def item(icon, bg):
        tile = (bg or flat).copy()
        if icon is not None:
            tile.alpha_composite(icon, (ITEM_ICON_CENTRE[0] - icon.width // 2, ITEM_ICON_CENTRE[1] - icon.height // 2))
        return tile

    names = sorted(built, key=lambda n: ICONS[n]["tier"])
    pad, label = 12, 14
    big_w, big_h = bw * scale, bh * scale
    rows_1x = [("OWB's", [built[n][0] for n in names], bgs[0] if bgs else None),
               ("ours", [built[n][1] for n in names], bgs[0] if bgs else None),
               ("ours, researched", [built[n][1] for n in names], bgs[1] if len(bgs) > 1 else None)]
    W = pad + 2 * (big_w + pad)
    H = pad + len(names) * (label + big_h + pad) + len(rows_1x) * (label + bh + pad)
    canvas = Image.new("RGBA", (W, H), PREVIEW_BG)
    draw = ImageDraw.Draw(canvas)
    y = pad
    for n in names:
        before, after = built[n]
        for c, (icon, text) in enumerate(((before, f"tier {ICONS[n]['tier']}: OWB's"), (after, f"tier {ICONS[n]['tier']}: ours"))):
            x = pad + c * (big_w + pad)
            draw.text((x, y), text if icon is not None else f"tier {ICONS[n]['tier']}: OWB has none for MLT", fill=(200, 200, 200))
            canvas.alpha_composite(item(icon, bgs[0] if bgs else None).resize((big_w, big_h), Image.NEAREST), (x, y + label))
        y += label + big_h + pad
    for text, icons, bg in rows_1x:
        draw.text((pad, y), text, fill=(200, 200, 200))
        for c, icon in enumerate(icons):
            canvas.alpha_composite(item(icon, bg), (pad + c * (bw + 6), y + label))
        y += label + bh + pad
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(PREVIEW_DIR / PREVIEW)
    for n in names:
        built[n][1].save(PREVIEW_DIR / f"{n}_out.png")
    print(f"previews -> {PREVIEW_DIR.relative_to(ROOT)}/{PREVIEW}, " + ", ".join(f"{n}_out.png" for n in names))


def parse_set(items, table):
    out = {}
    for item in items or []:
        k, _, val = item.partition("=")
        if not any(isinstance(p.get(k), float) for p in ICONS.values()):
            raise SystemExit(f"unknown parameter {k!r}")
        if isinstance(table.get(k), float):
            out[k] = float(val)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--icon", choices=sorted(ICONS), help="write one icon's .dds (default: all); the preview shows all")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE",
                    help="override a numeric ICONS parameter, in every icon that has it")
    ap.add_argument("--no-write", action="store_true", help="previews only, do not touch mod_folder")
    args = ap.parse_args()
    built = {}
    for name in sorted(ICONS, key=lambda n: ICONS[n]["tier"]):
        p = dict(ICONS[name], **parse_set(args.set, ICONS[name]))
        print(f"{name}:")
        before, out = (build_owb if p["kind"] == "owb" else build_cutout)(p)
        report(out, before)
        built[name] = (before, out)
        if not args.no_write and args.icon in (None, name):
            write_dds_like_owb(out, OUT_DIR / p["out"])
    write_preview(built)


if __name__ == "__main__":
    main()
