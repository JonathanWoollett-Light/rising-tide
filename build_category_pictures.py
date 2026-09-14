"""Derive Rising Tide copies of three OWB decision-category pictures, shifted down so
they stop painting over the orange frame line of the category description box.

The collision (OWB 5.1.11a, all measured - the script re-measures it every run):

  OWB interface/countrydecisionview.gui:133-152  decision_category_desc
      background  position { x=0 y=-1 }  quadTextureSprite GFX_tiled_decisions_bg_small
      "picture"   position { x=5 y=3 }
  vanilla interface/countrytechtreeview.gfx:244-251  GFX_tiled_decisions_bg_small
      corneredTileSpriteType, texture gfx/interface/tiles/tiled_decisions_bg_small.dds,
      borderSize 16x16 (OWB replaces that texture by path)
  OWB tiled_decisions_bg_small.dds, 48x48: row 4 orange (174,98,34), row 5 dark red
      (108,0,0) along the top edge; column 3 orange on the left, 43 red + 44 orange on
      the right.

  So the orange line is drawn at desc y = -1 + 4 = 3 and the red line at y = 4, and the
  picture's row 0 is drawn at y = 3: an opaque picture covers both. N is the number of
  rows the content must move down to start just below the last frame line:

      N = (bg_y + last_line_row + 1) - picture_y = (-1 + 5 + 1) - 3 = 2

  which puts the first content row at desc y = 5, directly under the red line - the way
  a 500-wide picture's right edge (x = 5 + 499 = 504) already sits directly left of the
  red frame column (x = 505).

The fix keeps each texture's size: N transparent rows on top, the same N rows cropped
off the bottom. A picture that already starts with t transparent rows moves by N - t.

Output: <out>/gfx/interface/decisions/mltd_decision_cat_<key>.dds, uncompressed
A8R8G8B8 like OWB's own (Pillow writes the pixel data byte-for-byte; the header is then
copied from OWB's source file, because Pillow leaves DDSD_MIPMAPCOUNT, dwDepth and
dwMipMapCount at 0 where OWB's category pictures carry 0x20000 / 1 / 1).

    python build_category_pictures.py                 # build into ./out
    python build_category_pictures.py --out <dir>     # e.g. <repo>/mod_folder
    python build_category_pictures.py --n 1           # override the measured N
    python build_category_pictures.py --check         # measure and report only
"""
import argparse
import os
import re
import struct
import sys

import numpy as np
from PIL import Image

OWB = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196"
VAN = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
HERE = os.path.dirname(os.path.abspath(__file__))

GUI = r"interface\countrydecisionview.gui"
DESC_BG_TEX = r"gfx\interface\tiles\tiled_decisions_bg_small.dds"
DESC_BG_BORDER = (16, 16)  # vanilla interface/countrytechtreeview.gfx:248

# key -> (OWB sprite, OWB texture, the Rising Tide category that uses it)
PICTURES = {
    "spectral_cabal": ("GFX_decision_cat_spectral_cabal",
                       r"gfx\interface\decisions\decision_cat_spectral_cabal.dds",
                       "mltd_gifts_from_the_deep_cat"),
    "loid_ekt_storm": ("GFX_decision_cat_picture_loid_ekt_storm",
                       r"gfx\interface\decisions\decision_cat_loid_ekt_storm.dds",
                       "mltd_children_of_the_deep_cat"),
    "wardens_propaganda": ("GFX_decision_cat_wardens_propaganda",
                           r"gfx\interface\decisions\decision_cat_wardens_propaganda.dds",
                           "mltd_cult_infiltration_cat"),
}


def out_rel(key):
    return os.path.join("gfx", "interface", "decisions", f"mltd_decision_cat_{key}.dds")


def sprite_name(key):
    return f"GFX_mltd_decision_cat_{key}"


# ---------------------------------------------------------------- measuring

def read_text(path):
    data = open(path, "rb").read()
    if data[:3] == b"\xef\xbb\xbf":
        data = data[3:]
    text = data.decode("utf-8", "replace").replace("\r\n", "\n")
    return "\n".join(re.sub(r"#.*", "", line) for line in text.split("\n"))


def _block_from(text, open_brace):
    depth = 0
    for j in range(open_brace, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace:j + 1]
    raise ValueError("unbalanced braces")


def _enclosing_block(text, idx):
    depth = 0
    i = idx
    while i >= 0:
        if text[i] == "}":
            depth += 1
        elif text[i] == "{":
            if depth == 0:
                return _block_from(text, i)
            depth -= 1
        i -= 1
    raise ValueError("no enclosing block")


POS = re.compile(r"position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s*y\s*=\s*(-?\d+)\s*\}")


def gui_geometry(owb=OWB):
    """Background and picture positions inside decision_category_desc."""
    text = read_text(os.path.join(owb, GUI))
    i = text.index('name = "decision_category_desc"')
    desc = _enclosing_block(text, i)
    bg = _block_from(desc, desc.index("{", desc.index("background")))
    pic = _enclosing_block(desc, desc.index('name = "picture"'))
    bx, by = map(int, POS.search(bg).groups())
    px, py = map(int, POS.search(pic).groups())
    sprite = re.search(r'quadTextureSprite\s*=\s*"([^"]+)"', bg).group(1)
    return dict(bg_x=bx, bg_y=by, pic_x=px, pic_y=py, bg_sprite=sprite)


def load_rgba(path):
    return np.array(Image.open(path).convert("RGBA"))


def desc_bg_path(owb=OWB):
    p = os.path.join(owb, DESC_BG_TEX)
    return p if os.path.exists(p) else os.path.join(VAN, DESC_BG_TEX)


def frame_line_rows(tex, border=DESC_BG_BORDER):
    """Rows of the top border that carry an opaque line different from the fill,
    across the whole tiled top-edge section (so they are drawn along the full edge)."""
    bx, by = border
    h, w = tex.shape[:2]
    fill = tex[h // 2, w // 2, :3]
    rows = []
    for y in range(by):
        seg = tex[y, bx:w - bx]
        if (seg[:, 3] == 255).all() and (np.abs(seg[:, :3].astype(int) - fill).sum(axis=1) > 30).all():
            rows.append((y, tuple(int(v) for v in seg[len(seg) // 2, :3])))
    return rows


def measure(owb=OWB):
    g = gui_geometry(owb)
    tex = load_rgba(desc_bg_path(owb))
    lines = frame_line_rows(tex)
    if not lines:
        raise SystemExit("no frame line found in the desc background - re-measure by hand")
    last = lines[-1][0]
    first_free = g["bg_y"] + last + 1          # first desc row below every frame line
    n = max(0, first_free - g["pic_y"])
    return dict(g, lines=lines, first_free=first_free, n=n,
                line_desc_rows=[(g["bg_y"] + r, c) for r, c in lines])


# ---------------------------------------------------------------- fixing

def top_transparent_rows(rgba):
    a = rgba[..., 3]
    for y in range(a.shape[0]):
        if a[y].max() > 0:
            return y
    return a.shape[0]


def shift_down(rgba, n):
    """N transparent rows on top, the bottom N rows cropped: same size."""
    if n <= 0:
        return rgba.copy()
    out = np.zeros_like(rgba)
    out[n:] = rgba[:rgba.shape[0] - n]
    return out


DDS_HEADER_FREE = {8, 24, 28}  # dwFlags, dwDepth, dwMipMapCount


def copy_header(out_path, src_path):
    """Give Pillow's output the source file's exact 128-byte header. Refuses unless
    the two differ only in dwFlags / dwDepth / dwMipMapCount and the sizes agree."""
    src = open(src_path, "rb").read()
    out = open(out_path, "rb").read()
    if len(src) != len(out):
        raise SystemExit(f"{out_path}: size {len(out)} != source {len(src)}")
    a = struct.unpack("<32I", src[:128])
    b = struct.unpack("<32I", out[:128])
    bad = [i * 4 for i in range(32) if a[i] != b[i] and i * 4 not in DDS_HEADER_FREE]
    if bad:
        raise SystemExit(f"{out_path}: header differs from source at offsets {bad}")
    with open(out_path, "wb") as f:
        f.write(src[:128] + out[128:])


def is_uncompressed_argb(path):
    h = open(path, "rb").read(128)
    pf_flags, fourcc, bits, rm, gm, bm, am = struct.unpack_from("<I4s5I", h, 80)
    return (pf_flags & 0x41) == 0x41 and not (pf_flags & 0x4) and bits == 32 and \
        (rm, gm, bm, am) == (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)


def build(out_dir, n=None, owb=OWB, keep_pillow_header=False, check=False, log=print):
    m = measure(owb)
    n_line = m["n"] if n is None else n
    log(f"gui   {GUI}: background y={m['bg_y']} ({m['bg_sprite']}), picture x={m['pic_x']} y={m['pic_y']}")
    log(f"frame {DESC_BG_TEX}: line rows " +
        ", ".join(f"{r} {c} -> desc y {r + m['bg_y']}" for r, c in m["lines"]))
    log(f"N = ({m['bg_y']} + {m['lines'][-1][0]} + 1) - {m['pic_y']} = {m['n']}" +
        ("" if n is None else f"  (overridden: {n})"))
    results = {}
    for key, (sprite, rel, cat) in PICTURES.items():
        src = os.path.join(owb, rel)
        if not is_uncompressed_argb(src):
            raise SystemExit(f"{src}: not uncompressed A8R8G8B8 - Pillow would not reproduce it")
        rgba = load_rgba(src)
        t = top_transparent_rows(rgba)
        shift = max(0, n_line - t)
        fixed = shift_down(rgba, shift)
        h, w = rgba.shape[:2]
        line_px = [int((rgba[r, :, 3] > 0).sum()) for r in range(max(0, n_line))]
        dst = os.path.join(out_dir, out_rel(key))
        log(f"{key:20} {w}x{h}  top transparent rows {t}  opaque on frame rows "
            f"{line_px}  shift {shift}  -> {'(check only)' if check else dst}")
        results[key] = dict(src=src, dst=dst, shift=shift, fixed=fixed, orig=rgba)
        if check or shift == 0:
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        Image.fromarray(fixed, "RGBA").save(dst)          # no pixel_format kwarg
        if not keep_pillow_header:
            copy_header(dst, src)
        back = load_rgba(dst)
        assert back.shape == rgba.shape
        assert (back[:shift, :, 3] == 0).all()
        assert np.array_equal(back[shift:], rgba[:h - shift])
        if not keep_pillow_header:
            assert open(dst, "rb").read(128) == open(src, "rb").read(128)
    return m, results


def gfx_snippet():
    lines = ["\t# Decision-category pictures: OWB's, moved down 2 rows (build_category_pictures.py)"]
    for key in PICTURES:
        lines += ["\tspriteType = {",
                  f'\t\tname = "{sprite_name(key)}"',
                  f'\t\ttexturefile = "{out_rel(key).replace(os.sep, "/")}"',
                  "\t}"]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--n", type=int, default=None, help="override the measured N")
    ap.add_argument("--owb", default=OWB)
    ap.add_argument("--pillow-header", action="store_true",
                    help="keep Pillow's header instead of copying OWB's")
    ap.add_argument("--check", action="store_true", help="measure only, write nothing")
    args = ap.parse_args(argv)
    build(args.out, args.n, args.owb, args.pillow_header, args.check)
    if not args.check:
        print("\nmltd.gfx:\n" + gfx_snippet())
        print("\ncategories:")
        for key, (sprite, rel, cat) in PICTURES.items():
            print(f"\t{cat}: picture = {sprite} -> {sprite_name(key)}")


if __name__ == "__main__":
    sys.exit(main())
