"""Build the intelligence agency logo of The Esoteric Order of M'lyeh.

Input:  event_images/agency/agency_src.jpg - a black-on-white stencil of Marvel's HYDRA insignia (the "Hail M'lyeh"
        joke), 750x737: a square image squashed ~1.7 % vertically. Third-party art - see event_images/SOURCES.md.
Output: mod_folder/gfx/interface/operatives/agencies/mltd_agency_logo_esoteric_order.dds - a 234x119 strip of two
        117x119 frames, uncompressed A8R8G8B8 like every vanilla and OWB agency logo (sprite noOfFrames = 2, declared
        in interface/mltd.gfx), plus previews in event_images/agency/.

Design - a seal, because plain black vanishes on the agency header's near-black disc: a dark abyssal-teal disc, the
skull, the tentacles and both rings in OWB's house gold, a 1 px dark rim. The skull and tentacles are resampled from
the source; both rings are redrawn as true circles (the source clips its outer ring), with the gap between them widened
so it survives the downscale. Frame 2 is frame 1 with OWB's hover glow under it: a warm grey halo, solid to ~3 px and
gone by ~13 px, measured from OWB's own logos (generic_21, generic_1, NCR, BOS, Withered Dogs).

The game draws frame 1 at 0.9x (agency header), 0.7x (insignia picker), 1x (operative events) and 0.3x (operative
badge); --preview renders all four on the game's own backgrounds when vanilla and OWB are installed.

usage: python build_agency_logo.py [--preview]
"""
import glob, math, os, re, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'event_images', 'agency', 'agency_src.jpg')
DDS_OUT = os.path.join(HERE, 'mod_folder', 'gfx', 'interface', 'operatives', 'agencies',
                       'mltd_agency_logo_esoteric_order.dds')
PREVIEW_DIR = os.path.join(HERE, 'event_images', 'agency')
VANILLA = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
OWB = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196'

FW, FH = 117, 119                 # one frame; the strip is 2 x 117 = 234 wide
SS = 8                            # supersampling factor
D = 88                            # outer ring diameter, final px (OWB's round emblems span 88-99 px; 13-15 px is left for the glow)
CXF, CYF = FW / 2, FH / 2         # emblem centre in the frame
RIM = 1.0                         # dark rim outside the outer ring, final px
# Ring radii as fractions of the outer ring's outer radius. Source: thick ring 318.5-353.8, thin ring 363.5-374.8
# (of 374.8). The thick ring's outer edge comes in to 346 and the thin ring's inner edge out to 362.5, so the gap
# between them is ~2 final px instead of ~1.
R_THICK_IN, R_THICK_OUT, R_THIN_IN = 318.5 / 374.75, 346.0 / 374.75, 362.5 / 374.75
INK_LO, INK_HI = 60, 200          # source luma: <= LO is full ink, >= HI none (soft, anti-aliased edge)
DISC_IN, DISC_OUT = (22, 60, 62), (12, 38, 40)          # abyssal teal, centre -> edge
GOLD_TOP, GOLD_BOTTOM = (238, 198, 98), (202, 150, 58)  # OWB's house gold, lit from above
RIM_RGB = (8, 14, 16)
GLOW_RGB = (153, 145, 132)
GLOW_D = [0, 1, 3, 5, 7, 9, 11, 13]                      # distance from the emblem edge, px
GLOW_A = [254, 254, 248, 204, 106, 32, 4, 0]             # glow alpha at that distance


# ------------------------------------------------------------------------------------------------ source geometry
def load_source():
    """The source stretched back to a square, its L array and the fitted circle (cx, cy, thick-ring inner radius,
    thin-ring outer radius) in that square's pixels."""
    src = Image.open(SRC).convert('L')
    w, _ = src.size
    sq = src.resize((w, w), Image.LANCZOS)
    lum = np.asarray(sq).astype(np.float64)
    dark = lum < 128
    n = w

    def runs(cx, cy, ang):
        dx, dy = math.cos(ang), math.sin(ang)
        out, prev = [], None
        for q in range(200 * 4, 420 * 4):
            r = q / 4
            xi, yi = int(round(cx + dx * r)), int(round(cy + dy * r))
            if not (0 <= xi < n and 0 <= yi < n):
                out.append((r, 'edge'))
                break
            d = bool(dark[yi, xi])
            if prev is not None and d != prev:
                out.append((r, 'dark' if d else 'light'))
            prev = d
        return out

    def edges(cx, cy):
        rows = []
        for k in range(360):
            t = runs(cx, cy, math.radians(k))
            darks = [(r, t[i + 1][0] if i + 1 < len(t) else None) for i, (r, kind) in enumerate(t) if kind == 'dark']
            thick = [(a, b) for a, b in darks if b is not None and b - a >= 25 and a > 280]
            if not thick:
                continue
            ti, to = thick[-1]
            thin = [(a, b) for a, b in darks if a > to]
            rows.append((k, ti, thin[0][1] if thin else None))
        return rows

    cx = cy = n / 2
    for _ in range(4):                                   # least-squares circle through the thick ring's inner edge
        rows = edges(cx, cy)
        pts = np.array([[cx + math.cos(math.radians(k)) * ti, cy + math.sin(math.radians(k)) * ti] for k, ti, _ in rows])
        A = np.c_[2 * pts[:, 0], 2 * pts[:, 1], np.ones(len(pts))]
        sol = np.linalg.lstsq(A, (pts ** 2).sum(1), rcond=None)[0]
        cx, cy = sol[0], sol[1]
        r_ti = math.sqrt(sol[2] + cx * cx + cy * cy)
    resid = float(np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r_ti).max())
    r_ho = float(np.median([ho for *_, ho in edges(cx, cy) if ho is not None]))
    assert resid < 3, 'source is not round after the vertical stretch (residual %.1f px)' % resid
    return sq, (cx, cy, r_ti, r_ho), resid


# ------------------------------------------------------------------------------------------------ drawing
def band(rr, r_in, r_out):
    return np.clip(np.minimum(rr - r_in, r_out - rr) + 0.5, 0, 1)


def lerp(a, b, t):
    return np.asarray(a, float) + (np.asarray(b, float) - np.asarray(a, float)) * t[..., None]


def frame1(sq, fit):
    cx, cy, r_ti, r_ho = fit
    W, H = FW * SS, FH * SS
    R = D / 2 * SS                                       # outer radius, supersampled px
    a = r_ho / R                                         # source px per supersampled px
    art = sq.transform((W, H), Image.AFFINE, (a, 0, cx - CXF * SS * a, 0, a, cy - CYF * SS * a),
                       resample=Image.BICUBIC, fillcolor=255)
    ink = np.clip((INK_HI - np.asarray(art).astype(np.float64)) / (INK_HI - INK_LO), 0, 1)
    yy, xx = np.mgrid[0:H, 0:W]
    rr = np.hypot(xx + 0.5 - CXF * SS, yy + 0.5 - CYF * SS)
    keep = np.clip((r_ti - 3) / a - rr + 0.5, 0, 1)      # only the skull and tentacles, well inside the thick ring
    gold = np.maximum(ink * keep, np.maximum(band(rr, R_THICK_IN * R, R_THICK_OUT * R), band(rr, R_THIN_IN * R, R)))
    disc = np.clip(R - rr + 0.5, 0, 1)
    cover = np.clip(R + RIM * SS - rr + 0.5, 0, 1)
    rgb = lerp(RIM_RGB, lerp(DISC_IN, DISC_OUT, np.clip(rr / R, 0, 1)), disc)
    rgb = rgb + (lerp(GOLD_TOP, GOLD_BOTTOM, np.clip((yy - (CYF * SS - R)) / (2 * R), 0, 1)) - rgb) * gold[..., None]
    # premultiplied box downsample
    pm = (rgb * cover[..., None]).reshape(FH, SS, FW, SS, 3).mean((1, 3))
    af = cover.reshape(FH, SS, FW, SS).mean((1, 3))
    out = np.where(af[..., None] > 1e-6, pm / np.maximum(af[..., None], 1e-6), 0)
    return np.dstack([out, af * 255]).clip(0, 255).round().astype(np.uint8)


def frame2(f1):
    """OWB's hover highlight: the same emblem over a warm grey glow that fades with distance from its edge."""
    a1 = f1[..., 3].astype(float)
    solid = a1 >= 128
    edge = solid & ~(np.roll(solid, 1, 0) & np.roll(solid, -1, 0) & np.roll(solid, 1, 1) & np.roll(solid, -1, 1))
    ey, ex = np.nonzero(edge)
    yy, xx = np.mgrid[0:FH, 0:FW]
    d = np.full((FH, FW), 99.0)
    for i in range(0, len(ey), 256):                     # exact distance to the nearest edge pixel
        dd = np.hypot(yy[..., None] - ey[i:i + 256], xx[..., None] - ex[i:i + 256]).min(-1)
        d = np.minimum(d, dd)
    d[solid] = 0
    ga = np.interp(d, GLOW_D, GLOW_A) / 255.0
    fa = a1 / 255.0
    oa = fa + ga * (1 - fa)
    rgb = (f1[..., :3] * fa[..., None] + np.array(GLOW_RGB, float) * (ga * (1 - fa))[..., None]) \
        / np.maximum(oa[..., None], 1e-6)
    return np.dstack([rgb, oa * 255]).clip(0, 255).round().astype(np.uint8)


def build():
    sq, fit, resid = load_source()
    f1 = frame1(sq, fit)
    f2 = frame2(f1)
    strip = np.concatenate([f1, f2], 1)
    assert strip.shape == (FH, 2 * FW, 4)
    for f, name in ((f1, 'frame 1'), (f2, 'frame 2')):   # nothing may touch the frame border
        border = np.r_[f[0, :, 3], f[-1, :, 3], f[:, 0, 3], f[:, -1, 3]]
        assert border.max() < 8, '%s reaches the frame edge (alpha %d)' % (name, border.max())
    os.makedirs(os.path.dirname(DDS_OUT), exist_ok=True)
    Image.fromarray(strip, 'RGBA').convert('RGBA').save(DDS_OUT)
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    Image.fromarray(strip, 'RGBA').save(os.path.join(PREVIEW_DIR, 'mltd_agency_logo_strip.png'))
    ys, xs = np.nonzero(f1[..., 3] >= 128)
    print('fit: centre (%.1f, %.1f), thick ring from r %.1f, outer r %.1f, residual %.2f px' % (fit + (resid,)))
    print('wrote %s (234x119, 2 frames); emblem bbox x %d-%d y %d-%d' % (DDS_OUT, xs.min(), xs.max(), ys.min(), ys.max()))
    return strip


# ------------------------------------------------------------------------------------------------ preview
def find_texture(sprite):
    for root in (OWB, VANILLA):
        for f in sorted(glob.glob(os.path.join(root, 'interface', '*.gfx'))):
            t = open(f, encoding='utf-8', errors='ignore').read()
            m = re.search(r'name\s*=\s*"%s"' % re.escape(sprite), t)
            if m:
                tm = re.search(r'texture[Ff]ile\s*=\s*"([^"]+)"', t[m.end():m.end() + 600])
                if tm:
                    rel = re.sub(r'/+', '/', tm.group(1).replace('\\', '/'))
                    for r2 in (OWB, VANILLA):
                        p = os.path.join(r2, rel)
                        if os.path.exists(p):
                            return np.array(Image.open(p).convert('RGBA'))
    return None


def over(canvas, img, x, y):
    h, w = img.shape[:2]
    H, W = canvas.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    sub = img[y0 - y:y1 - y, x0 - x:x1 - x].astype(float)
    al = sub[..., 3:4] / 255
    c = canvas[y0:y1, x0:x1].astype(float)
    c[..., :3] = sub[..., :3] * al + c[..., :3] * (1 - al)
    canvas[y0:y1, x0:x1] = c.astype(np.uint8)


def scaled(f, sc):
    im = Image.fromarray(f).convert('RGBa')
    im = im.resize((max(1, round(f.shape[1] * sc)), max(1, round(f.shape[0] * sc))), Image.BILINEAR)
    return np.array(im.convert('RGBA'))


def blank(w, h, v):
    c = np.zeros((h, w, 4), np.uint8)
    c[..., :3] = v
    c[..., 3] = 255
    return c


def preview(strip):
    """Row per logo (ours, OWB generic_21 for scale): header x0.9 on the backdrop disc | picker x0.7 on paper |
    operative badge x0.3 | operative event x1 | the strip on a checker, all at 2x (nearest)."""
    bgs = {k: find_texture(k) for k in ('GFX_intelligence_agency_logo_bg', 'GFX_intelligence_agency_header',
                                        'GFX_tiled_paper_w_frame_bg', 'GFX_operative_leader_badge',
                                        'GFX_event_operative_background')}
    rows = [('this build', strip)]
    ref = os.path.join(OWB, 'gfx', 'interface', 'operatives', 'agencies', 'agency_logo_generic_21.dds')
    if os.path.exists(ref):
        rows.append(('OWB generic_21', np.array(Image.open(ref).convert('RGBA'))))
    C = 140
    sheet = blank(4 * (C + 4) + 2 * FW + 12, len(rows) * (C + 4), 20)
    for i, (_, s) in enumerate(rows):
        f1 = s[:, :s.shape[1] // 2]
        cells = []
        c = blank(C, C, 50)
        if bgs['GFX_intelligence_agency_header'] is not None:
            over(c, bgs['GFX_intelligence_agency_header'][:C, :C], 0, 0)
        if bgs['GFX_intelligence_agency_logo_bg'] is not None:
            over(c, bgs['GFX_intelligence_agency_logo_bg'], 19, 13)
        over(c, scaled(f1, 0.9), 11, 6)
        cells.append(c)
        c = blank(C, C, 50)
        if bgs['GFX_tiled_paper_w_frame_bg'] is not None:
            over(c, bgs['GFX_tiled_paper_w_frame_bg'][64:64 + 83, 64:64 + 81], 0, 0)
        over(c, scaled(f1, 0.7), 1, 1)
        cells.append(c)
        c = blank(C, C, 50)
        if bgs['GFX_operative_leader_badge'] is not None:
            over(c, bgs['GFX_operative_leader_badge'][:109, :C], 0, 0)
        over(c, scaled(f1, 0.3), 8, 0)
        cells.append(c)
        c = blank(C, C, 50)
        if bgs['GFX_event_operative_background'] is not None:
            over(c, bgs['GFX_event_operative_background'][25:25 + C, 341:341 + C], 0, 0)
        over(c, f1, 20, 10)
        cells.append(c)
        for j, cell in enumerate(cells):
            over(sheet, cell, j * (C + 4), i * (C + 4))
        yy, xx = np.mgrid[0:FH, 0:2 * FW]
        v = ((yy // 8 + xx // 8) % 2) * 60 + 150
        chk = np.dstack([v, v, v, np.full_like(v, 255)]).astype(np.uint8)
        over(chk, s[:, :2 * FW] if s.shape[1] >= 2 * FW else s, 0, 0)
        over(sheet, chk, 4 * (C + 4) + 8, i * (C + 4) + 10)
    out = os.path.join(PREVIEW_DIR, 'preview.png')
    Image.fromarray(sheet).resize((sheet.shape[1] * 2, sheet.shape[0] * 2), Image.NEAREST).save(out)
    print('preview: %s (rows: %s; columns: header x0.9 | picker x0.7 | badge x0.3 | event x1 | strip)'
          % (out, ', '.join(r[0] for r in rows)))


if __name__ == '__main__':
    s = build()
    if '--preview' in sys.argv:
        preview(s)
