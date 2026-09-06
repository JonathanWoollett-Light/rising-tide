# -*- coding: utf-8 -*-
"""
build_recording_gif.py -- turn a screen recording into a looping Workshop GIF.

    python build_recording_gif.py "<video>" --name preview_menu

Finds the shortest clean loop in the recording, crops it square, and encodes it
with the same palette-and-delta scheme as the Workshop thumbnail, under Steam's
1 MiB preview cap.

**The loop is found, not assumed.**  The main menu has no exact period: the two
rain sheets scroll on 3.4 s and 2.3 s cycles and the logo breathes on 2.0 s, so
they only realign after about 78 seconds.  Instead every (start, length) pair is
scored by how different the frame that *would* come next is from the frame the
loop actually cuts back to, over a short window, and the best is taken.  A seam
scoring below the recording's own typical frame-to-frame difference is one the
eye cannot pick out, because it is a smaller jump than the motion already
present between consecutive frames.

Lengths are restricted to multiples of the frame stride so the GIF's delay --
which it can only store in hundredths of a second -- divides the loop evenly.

Nothing here ships; output lands in ``workshop_page/``.
"""

import argparse
import os

import numpy as np
from PIL import Image

import build_workshop_thumbnail as T

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "workshop_page")

# Carousel images are 16:9 like the rest of workshop_page/.  A square version is
# available for the preview-image slot instead, which is the one Steam wants 1:1.
ASPECT = (16, 9)
BUDGET = 950 * 1024              # Steam's cap is 1 MiB
SEARCH_RES = 240                 # loop scoring runs on greyscale this big
SEAM_WINDOW = 3                  # frames compared either side of the seam
MIN_SECONDS, MAX_SECONDS = 1.0, 5.0
# Measured wrap, as a fraction of the loop's own typical frame-to-frame step.
#
# This has to be well BELOW 1.0, and that is not a safety margin -- it is how a
# real loop is told apart from a coincidence.  Scanning this recording, almost
# every length wraps at 1.1-1.25x a normal step: that is the noise floor, the
# rain simply being somewhere else.  A length where the two rain sheets genuinely
# realign scores far lower - 0.65 here - because the wrap is then a SMALLER
# change than the motion already on screen.  There is no continuum between the
# two, so anything near 1.0 is not a loop no matter how close it looks.
SEAM_OK = 0.85
#
# The cheap greyscale search flatters a seam: fine rain detail averages away at
# 240 px, and comparing against ONE frame of motion understates the step when
# playback advances by `stride` frames.  So the search only shortlists, and
# every candidate is then measured on the real output frames.

# Tried in order until one fits BUDGET.  Resolution goes first because a
# carousel image is displayed large and softness is the most obvious flaw;
# palette and tolerance are spent before frames, since dropping frames is what
# makes rain stutter.  Sizes are 16:9 and divisible by 2.
LADDER = [
    dict(width=640, stride=2, colors=160, tolerance=22),
    dict(width=640, stride=2, colors=128, tolerance=24),
    dict(width=640, stride=2, colors=128, tolerance=28),
    dict(width=640, stride=2, colors=96, tolerance=32),
    dict(width=576, stride=2, colors=160, tolerance=22),
    dict(width=512, stride=2, colors=160, tolerance=20),
    dict(width=480, stride=2, colors=192, tolerance=18),
    dict(width=480, stride=2, colors=160, tolerance=22),
    dict(width=426, stride=2, colors=160, tolerance=22),
    dict(width=426, stride=3, colors=160, tolerance=22),
    dict(width=384, stride=3, colors=128, tolerance=26),
]


def read_frames(path):
    import cv2
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        out.append(fr[:, :, ::-1].copy())          # BGR -> RGB
    cap.release()
    if not out:
        raise SystemExit("could not read any frames from " + path)
    return out, fps


def crop_box(w, h, aspect):
    """Centre-crop to `aspect`, or the whole frame when it already matches."""
    want = aspect[0] / aspect[1]
    if abs(w / h - want) < 1e-4:
        return (0, 0, w, h)
    if w / h > want:
        cw = int(round(h * want))
        return ((w - cw) // 2, 0, (w - cw) // 2 + cw, h)
    ch = int(round(w / want))
    return (0, (h - ch) // 2, w, (h - ch) // 2 + ch)


def canvas_for(width, aspect=ASPECT):
    return width, int(round(width * aspect[1] / aspect[0]))


def find_loop(frames, box, fps, stride):
    """Best (start, length) whose length is a multiple of `stride`."""
    small = np.stack([
        np.asarray(Image.fromarray(f).crop(box)
                   .convert("L").resize((SEARCH_RES, SEARCH_RES), Image.LANCZOS),
                   dtype=np.float32)
        for f in frames])
    n = len(small)
    adjacent = float(np.mean([np.abs(small[i + 1] - small[i]).mean()
                              for i in range(n - 1)]))
    lo = max(stride, int(MIN_SECONDS * fps) // stride * stride)
    hi = min(n - SEAM_WINDOW - 1, int(MAX_SECONDS * fps))
    shortlist = []
    for L in range(lo, hi + 1, stride):
        sc, _, s = min((float(np.mean([np.abs(small[s + L + k] - small[s + k]).mean()
                                       for k in range(SEAM_WINDOW)])), L, s)
                       for s in range(0, n - L - SEAM_WINDOW))
        shortlist.append((L, s, sc))
    shortlist.sort(key=lambda t: t[0])            # shortest first
    return shortlist, adjacent


def measure_wrap(frames, box, canvas, L, s, stride):
    """The wrap step and the typical step, on the real output frames.

    Playback runs ... f[s+L-stride] -> f[s] ..., so a perfect loop makes that
    transition indistinguishable from any other `stride`-sized step.  Both are
    measured the same way and compared.
    """
    def px(i):
        return np.asarray(Image.fromarray(frames[i]).crop(box)
                          .resize(canvas, Image.LANCZOS), dtype=np.float32)
    idx = list(range(s, s + L, stride))
    wrap = float(np.abs(px(idx[-1]) - px(idx[0])).mean())
    steps = [float(np.abs(px(idx[i + 1]) - px(idx[i])).mean())
             for i in range(0, len(idx) - 1, max(1, len(idx) // 8))]
    return wrap, float(np.mean(steps))


def build(video, name, aspect=ASPECT, budget=BUDGET):
    frames, fps = read_frames(video)
    h, w = frames[0].shape[:2]
    box = crop_box(w, h, aspect)
    print("%d frames at %.3g fps, %dx%d -> %d:%d crop %s%s" %
          (len(frames), fps, w, h, aspect[0], aspect[1], box,
           "  (already that shape, nothing cropped)"
           if box == (0, 0, w, h) else ""))

    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".gif")

    cache = {}
    for cfg in LADDER:
        stride = cfg["stride"]
        canvas = canvas_for(cfg["width"], aspect)
        if stride not in cache:
            cache[stride] = find_loop(frames, box, fps, stride)
        shortlist, adjacent = cache[stride]
        pick = None
        for L, s, sc in shortlist:
            wrap, step = measure_wrap(frames, box, canvas, L, s, stride)
            if wrap <= step * SEAM_OK:
                pick = (L, s, wrap, step)
                break
        if pick is None:                          # nothing clean; take the best
            L, s, _ = min(shortlist, key=lambda t: t[2])
            wrap, step = measure_wrap(frames, box, canvas, L, s, stride)
            pick = (L, s, wrap, step)
        L, s, wrap, step = pick
        delay = int(round(1000.0 * stride / fps / 10.0)) * 10       # whole cs
        picked = [Image.fromarray(frames[i]).crop(box)
                  .resize(canvas, Image.LANCZOS)
                  for i in range(s, s + L, stride)]
        out, trans, palette, kept = T.encode_gif_frames(
            picked, colors=cfg["colors"], tolerance=cfg["tolerance"])
        out[0].save(path, save_all=True, append_images=out[1:], loop=0,
                    duration=delay, disposal=1, transparency=trans,
                    optimize=False)
        n = os.path.getsize(path)
        print("  %dx%d, stride %d, %3d colours, tolerance %2d -> %2d frames @ "
              "%d ms (%.2fs), wrap %.2f vs %.2f typical, %.0f KB%s"
              % (canvas[0], canvas[1], stride, cfg["colors"], cfg["tolerance"],
                 len(picked), delay, len(picked) * delay / 1000.0, wrap, step,
                 n / 1024.0,
                 "" if n <= budget else "  -- over budget, trying again"))
        if n <= budget:
            if wrap > step * SEAM_OK:
                print("  WARNING: no length in this recording actually loops "
                      "(best wrap %.2fx a normal step, wanted under %.2f). The "
                      "jump will be visible; record for longer." %
                      (wrap / step, SEAM_OK))
            print("wrote %s  %dx%d  %.1f%% of pixels redrawn per frame"
                  % (path, canvas[0], canvas[1],
                     100.0 * kept / max((len(picked) - 1) * canvas[0] * canvas[1], 1)))
            return n
    raise SystemExit("could not fit %s under %d bytes" % (name, budget))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("video")
    ap.add_argument("--name", default="03_main_menu_animated")
    ap.add_argument("--square", action="store_true",
                    help="1:1 for the preview-image slot instead of the carousel")
    args = ap.parse_args()
    build(args.video, args.name,
          aspect=(1, 1) if args.square else ASPECT)


if __name__ == "__main__":
    main()
