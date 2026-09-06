"""Build the extra MLT leader portraits from the source paintings in event_images/portrait/.

Subjects (each ships as one 156x210 uncompressed A8R8G8B8 DDS - the same header class as OWB's
gfx/leaders/MLT/mlulu.dds: flags 0x100f, no mipmaps, opaque alpha - and is declared in mod_folder/interface/mltd.gfx):

  anastasia       event_images/portrait/anastasia_src.jpg (879x1376, hooded figure, clasped hands)
                  -> mod_folder/gfx/leaders/MLT/mltd_anastasia.dds        (GFX_Portrait_mltd_anastasia)
  drowned_herald  event_images/portrait/herald_src.jpg    (799x1200, tentacle-masked hooded figure holding a skull)
                  -> mod_folder/gfx/leaders/MLT/mltd_drowned_herald.dds   (GFX_Portrait_mltd_drowned_herald)

What it does: a cover-crop to 156:210 (LANCZOS) framing head and shoulders with the face in the upper third -
each subject's CROP picks the window - and, optionally, a very light OWB-style darkening (GRADE; strength 0 =
the art untouched). Nothing else: no repaint, no background replacement.

Previews (next to the sources): event_images/portrait/<subject>_preview.png - the crop window drawn on the
source, the 156x210 result at 2x, and OWB's own mlulu.dds at 2x for scale.

Run from the repo root:
  python build_leader_portraits.py                        # all subjects
  python build_leader_portraits.py --subject drowned_herald --set face_y_frac=0.33
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from build_portrait import dds_header  # noqa: E402  (same header check the M'lulu build uses)

OWB_MLULU = Path("C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196/gfx/leaders/MLT/mlulu.dds")
PORTRAIT_SIZE = (156, 210)

# ----------------------------------------------------------------------------------------------
# Per-subject crop window (source pixels). The window is `width` wide, width/(156/210) tall, horizontally
# centred on face_x and placed so the face centre sits at face_y_frac of the window height; it is then
# clamped into the image.
# ----------------------------------------------------------------------------------------------
SUBJECTS = {
    "anastasia": dict(
        src="event_images/portrait/anastasia_src.jpg",
        out="mod_folder/gfx/leaders/MLT/mltd_anastasia.dds",
        preview="event_images/portrait/anastasia_preview.png",
        # width=740 keeps the hood peak (~40 px headroom) and the clasped hands (~45 px below them).
        crop=dict(face_x=505.0, face_y=480.0, face_y_frac=0.35, width=740.0),
    ),
    "drowned_herald": dict(
        src="event_images/portrait/herald_src.jpg",
        out="mod_folder/gfx/leaders/MLT/mltd_drowned_herald.dds",
        preview="event_images/portrait/drowned_herald_preview.png",
        # the tentacle mask sits around (400, 380); a 760 px window is nearly the full height, so the hood
        # peak, the skull in the raised hand and the gloved hand at the belt all stay in frame.
        crop=dict(face_x=400.0, face_y=380.0, face_y_frac=0.33, width=760.0),
    ),
}

# ----------------------------------------------------------------------------------------------
# Optional grade. strength 0 leaves the JPEG's colours exactly as they are (only the resample happens).
# Anything else is a light OWB-style darkening: exposure in stops, a touch of desaturation and a soft
# vignette, all scaled by `strength`.
# ----------------------------------------------------------------------------------------------
GRADE = dict(
    strength=0.0,
    exposure=-0.20,
    desaturate=0.12,
    vignette=0.35,
)


def crop_window(size, c):
    W, H = size
    aspect = PORTRAIT_SIZE[0] / PORTRAIT_SIZE[1]
    w = min(float(c["width"]), W)
    h = w / aspect
    if h > H:
        h = float(H)
        w = h * aspect
    x0 = c["face_x"] - w / 2.0
    y0 = c["face_y"] - c["face_y_frac"] * h
    x0 = min(max(x0, 0.0), W - w)
    y0 = min(max(y0, 0.0), H - h)
    return (x0, y0, x0 + w, y0 + h)


def apply_grade(img, g):
    k = float(g["strength"])
    if k <= 0:
        return img
    a = np.asarray(img.convert("RGB"), dtype=np.float64) / 255.0
    a = a * (2.0 ** (g["exposure"] * k))
    lum = a @ np.array([0.2126, 0.7152, 0.0722])
    a = a + (lum[..., None] - a) * (g["desaturate"] * k)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vig = 1.0 - g["vignette"] * k * np.clip((r - 0.55) / 0.9, 0, 1) ** 2
    a = a * vig[..., None]
    return Image.fromarray(np.round(np.clip(a, 0, 1) * 255).astype(np.uint8), "RGB")


def build(src_path, c, g):
    src = Image.open(src_path).convert("RGB")
    box = crop_window(src.size, c)
    # resize(box=...) resamples straight from the source window with LANCZOS (sub-pixel box, no double resample)
    out = src.resize(PORTRAIT_SIZE, Image.LANCZOS, box=box)
    out = apply_grade(out, g)
    return src, box, out


def write_dds(img, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGBA").save(out_path)          # no pixel_format kwarg -> uncompressed A8R8G8B8 like OWB
    h = dds_header(out_path)
    assert (h["w"], h["h"], h["flags"], h["pf_flags"], h["bpp"], h["mips"]) == (156, 210, 0x100f, 0x41, 32, 0), h
    if OWB_MLULU.exists():
        ref = dds_header(OWB_MLULU)
        assert (ref["flags"], ref["pf_flags"], ref["bpp"], ref["mips"], ref["bytes"]) == (h["flags"], h["pf_flags"], h["bpp"], h["mips"], h["bytes"]), (ref, h)
    re = Image.open(out_path)
    re.load()
    print(f"{out_path.relative_to(ROOT)}: {h['w']}x{h['h']} {h['bytes']} bytes flags=0x{h['flags']:x} "
          f"pf_flags=0x{h['pf_flags']:x} bpp={h['bpp']} -> reopened {re.mode} {re.size}")


def write_preview(src, box, out, preview_path):
    scale = 0.5
    s = src.copy()
    d = ImageDraw.Draw(s)
    d.rectangle(box, outline=(255, 60, 60), width=6)
    s = s.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
    tiles = [out.resize((312, 420), Image.NEAREST)]
    if OWB_MLULU.exists():
        m = Image.open(OWB_MLULU).convert("RGB")
        tiles.append(m.resize((312, 420), Image.NEAREST))
    W = s.width + 20 + sum(t.width + 20 for t in tiles)
    H = max(s.height, 440)
    canvas = Image.new("RGB", (W, H), (30, 30, 32))
    canvas.paste(s, (0, 0))
    x = s.width + 20
    for t in tiles:
        canvas.paste(t, (x, 10))
        x += t.width + 20
    canvas.save(preview_path)
    print(f"preview -> {preview_path.relative_to(ROOT)}  (crop box = {tuple(round(v) for v in box)})")


def parse_set(items, tables):
    out = {t: {} for t in tables}
    for item in items or []:
        k, _, val = item.partition("=")
        for name, table in tables.items():
            if k in table:
                out[name][k] = float(val)
                break
        else:
            raise SystemExit(f"unknown parameter {k!r}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject", choices=sorted(SUBJECTS), help="build one subject (default: all)")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE", help="override a CROP or GRADE parameter (applies to the selected subject(s))")
    ap.add_argument("--no-write", action="store_true", help="preview only, do not touch mod_folder")
    args = ap.parse_args()
    for name in ([args.subject] if args.subject else sorted(SUBJECTS)):
        subj = SUBJECTS[name]
        ov = parse_set(args.set, {"crop": subj["crop"], "grade": GRADE})
        c = dict(subj["crop"], **ov["crop"])
        g = dict(GRADE, **ov["grade"])
        src, box, out = build(ROOT / subj["src"], c, g)
        write_preview(src, box, out, ROOT / subj["preview"])
        if not args.no_write:
            write_dds(out, ROOT / subj["out"])


if __name__ == "__main__":
    main()
