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

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "workshop_page")

TARGET = (1920, 1080)
BUDGET = 900 * 1024          # Steam's cap is 1 MiB; leave headroom
QUALITY = (95, 93, 91, 88, 85, 82)


def fit_16_9(im, target=TARGET):
    """Scale to `target`, centre-cropping only as much as the aspect demands."""
    want = target[0] / target[1]
    have = im.width / im.height
    if abs(have - want) > 1e-4:
        if have > want:                       # too wide: trim the sides
            w = int(round(im.height * want))
            x = (im.width - w) // 2
            im = im.crop((x, 0, x + w, im.height))
        else:                                 # too tall: trim top and bottom
            h = int(round(im.width / want))
            y = (im.height - h) // 2
            im = im.crop((0, y, im.width, y + h))
    return im.resize(target, Image.LANCZOS)


def build(src, name, target=TARGET, budget=BUDGET):
    im = Image.open(src).convert("RGB")
    before = im.size
    out = fit_16_9(im, target)
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".jpg")

    for q in QUALITY:
        out.save(path, quality=q, subsampling=0, optimize=True,
                 progressive=True)
        if os.path.getsize(path) <= budget:
            break
    else:
        raise SystemExit("cannot fit %s under %d bytes even at quality %d"
                         % (name, budget, QUALITY[-1]))

    n = os.path.getsize(path)
    cropped = "" if before[0] / before[1] == target[0] / target[1] else \
        " (centre-cropped to 16:9 first)"
    print("wrote %s\n  %dx%d -> %dx%d%s, quality %d, %.0f KB of a %.0f KB budget"
          % (path, before[0], before[1], target[0], target[1], cropped, q,
             n / 1024.0, budget / 1024.0))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("source", help="path to the screenshot")
    ap.add_argument("--name", required=True,
                    help="output basename, e.g. 01_main_menu")
    ap.add_argument("--width", type=int, default=TARGET[0])
    ap.add_argument("--height", type=int, default=TARGET[1])
    args = ap.parse_args()
    build(args.source, args.name, (args.width, args.height))


if __name__ == "__main__":
    main()
