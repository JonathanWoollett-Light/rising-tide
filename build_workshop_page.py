# -*- coding: utf-8 -*-
"""
build_workshop_page.py -- prepare a screenshot for the Steam Workshop page.

    python build_workshop_page.py "<screenshot>" --name 01_main_menu

Scales to 1920x1080 preserving aspect, centre-cropping first if the source is
not already 16:9, and writes a JPEG into ``workshop_page/``.

**Why JPEG.**  Steam caps a Workshop image at 1 MiB.  A 1920x1080 PNG of a
painted, grainy scene is about 2.9 MB, so PNG cannot be used at this size at
all; JPEG at quality 95 with no chroma subsampling is ~840 KB and visually
indistinguishable on a screenshot.  The quality is searched downward until the
file fits ``BUDGET`` with margin rather than being fixed, so an unusually busy
frame degrades gracefully instead of silently blowing the limit.

Chroma subsampling is off (``subsampling=0``).  These frames are mostly UI text
and thin neon, both of which 4:2:0 smears badly.

Nothing here ships: ``workshop_page/`` is repo-only, like ``event_images/``.
"""

import argparse
import os

import numpy as np
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "workshop_page")

TARGET = (1920, 1080)
BUDGET = 900 * 1024          # Steam's cap is 1 MiB; leave headroom
QUALITY = (95, 93, 91, 88, 85, 82)


def ui_window_box(im):
    """Bounding box of a HOI4 interface window, or None.

    The game's panels are warm brown and the world behind them is blue-grey, so
    `R - B` separates the two cleanly where luminance and saturation do not.
    Rows and columns only count when a quarter of them are warm, which ignores
    stray UI bits floating over the map.
    """
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    warm = (a[..., 0] - a[..., 2]) > 12
    ry = np.nonzero(warm.sum(1) > w * 0.25)[0]
    rx = np.nonzero(warm.sum(0) > h * 0.25)[0]
    if not len(ry) or not len(rx):
        return None
    return int(rx.min()), int(ry.min()), int(rx.max()) + 1, int(ry.max()) + 1


def fit_16_9(im, target=TARGET, keep_ui=False):
    """Scale to `target`, cropping only as much as the aspect demands.

    Centred by default.  With `keep_ui`, the crop is instead slid to contain the
    interface window whole -- a windowed HOI4 capture is a few px taller than
    16:9 and the panel sits slightly off centre, so a centre crop shaves the
    frame off one edge for no reason.
    """
    want = target[0] / target[1]
    have = im.width / im.height
    if abs(have - want) > 1e-4:
        box = ui_window_box(im) if keep_ui else None
        if have > want:                       # too wide: trim the sides
            cw = int(round(im.height * want))
            x = (im.width - cw) // 2
            if box:
                x = min(box[0], max(box[2] - cw, x))
                x = max(0, min(x, im.width - cw))
            im = im.crop((x, 0, x + cw, im.height))
        else:                                 # too tall: trim top and bottom
            ch = int(round(im.width / want))
            y = (im.height - ch) // 2
            if box:
                y = min(box[1], max(box[3] - ch, y))
                y = max(0, min(y, im.height - ch))
            im = im.crop((0, y, im.width, y + ch))
    return im.resize(target, Image.LANCZOS)


def save_under_budget(out, path, budget=BUDGET):
    for q in QUALITY:
        out.save(path, quality=q, subsampling=0, optimize=True, progressive=True)
        if os.path.getsize(path) <= budget:
            return q
    raise SystemExit("cannot fit %s under %d bytes even at quality %d"
                     % (path, budget, QUALITY[-1]))


def crop_16_9(im, keep_ui=False):
    """Trim to 16:9 at the source's own resolution, resampling nothing.

    Upscaling a windowed capture to 1920x1080 only softens the interface text
    it is being taken for, so a screenshot that is already close to 16:9 is
    better off simply trimmed.
    """
    target = (im.width, int(round(im.width * 9 / 16)))
    if target[1] > im.height:
        target = (int(round(im.height * 16 / 9)), im.height)
    return fit_16_9(im, target, keep_ui=keep_ui)


def build(src, name, target=TARGET, budget=BUDGET, keep_ui=False,
          native=False):
    im = Image.open(src).convert("RGB")
    before = im.size
    out = crop_16_9(im, keep_ui=keep_ui) if native \
        else fit_16_9(im, target, keep_ui=keep_ui)
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".jpg")

    q = save_under_budget(out, path, budget)

    n = os.path.getsize(path)
    how = "" if abs(before[0] / before[1] - 16 / 9) < 1e-4 else (
        ", trimmed around the interface window" if keep_ui else ", centre-trimmed")
    print("wrote %s\n  %dx%d -> %dx%d%s, quality %d, %.0f KB of a %.0f KB budget"
          % (path, before[0], before[1], out.size[0], out.size[1], how, q,
             n / 1024.0, budget / 1024.0))
    return n


def collage(sources, name, target=TARGET, budget=BUDGET, keep_ui=False):
    """Four 16:9 images as quarters of one 16:9 image.

    A 2x2 grid of 16:9 tiles is itself exactly 16:9, so the tiles need no
    letterboxing and nothing is distorted.  A one-pixel rule is drawn along the
    seams only because adjacent screenshots of the same dark UI otherwise run
    into each other.
    """
    if len(sources) != 4:
        raise SystemExit("a quartered collage needs exactly 4 images, got %d"
                         % len(sources))
    tw, th = target[0] // 2, target[1] // 2
    sheet = Image.new("RGB", target)
    for i, src in enumerate(sources):
        tile = fit_16_9(Image.open(src).convert("RGB"), (tw, th), keep_ui=keep_ui)
        sheet.paste(tile, ((i % 2) * tw, (i // 2) * th))
    d = ImageDraw.Draw(sheet)
    d.line([(tw, 0), (tw, target[1])], fill=(28, 26, 22))
    d.line([(0, th), (target[0], th)], fill=(28, 26, 22))

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".jpg")
    q = save_under_budget(sheet, path, budget)
    n = os.path.getsize(path)
    print("wrote %s\n  4 tiles of %dx%d -> %dx%d, quality %d, %.0f KB of a "
          "%.0f KB budget"
          % (path, tw, th, target[0], target[1], q, n / 1024.0, budget / 1024.0))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("source", nargs="+", help="path(s) to the screenshot(s)")
    ap.add_argument("--name", required=True,
                    help="output basename, e.g. 01_main_menu")
    ap.add_argument("--collage", action="store_true",
                    help="tile exactly 4 sources into one 16:9 image")
    ap.add_argument("--keep-ui", action="store_true",
                    help="slide the crop to keep a HOI4 interface window whole")
    ap.add_argument("--native", action="store_true",
                    help="trim to 16:9 without resampling (single source only)")
    ap.add_argument("--width", type=int, default=TARGET[0])
    ap.add_argument("--height", type=int, default=TARGET[1])
    args = ap.parse_args()
    target = (args.width, args.height)
    if args.collage:
        collage(args.source, args.name, target, keep_ui=args.keep_ui)
    else:
        if len(args.source) != 1:
            raise SystemExit("one source unless --collage")
        build(args.source[0], args.name, target, keep_ui=args.keep_ui,
              native=args.native)


if __name__ == "__main__":
    main()
