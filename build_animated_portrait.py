"""Build Rising Tide's animated leader portraits as HOI4 frame strips.

Subjects (see SUBJECTS below):
  mlulu           rain     mod_folder/gfx/leaders/MLT/mltd_mlulu_animated.dds
  drowned_herald  glow     mod_folder/gfx/leaders/MLT/mltd_drowned_herald_animated.dds

Each output is a horizontal strip, frames x 156 wide by 210 tall, uncompressed A8R8G8B8, declared in
interface/mltd.gfx as a frameAnimatedSpriteType, e.g.

    frameAnimatedSpriteType = {
        name = "GFX_Portrait_mltd_mlulu_animated"
        texturefile = "gfx/leaders/MLT/mltd_mlulu_animated.dds"
        noOfFrames = 40
        animation_rate_fps = 12
        looping = yes
        play_on_show = yes
    }

`noOfFrames` and the strip width must agree: width = 156 x noOfFrames. Frame strips are the only
mechanism any animated portrait in OWB (63 sprites in interface/z_fallout_leaders_animated.gfx) or
tnkd (interface/tnkd_leaders_animated.gfx) uses; the `animation = {}` overlay block is for focus
shines and the frontend snow, never a portrait.

How each loop closes seamlessly.
  rain  Each layer is drawn once into a periodic canvas at SS x resolution and then translated by a
        fixed (dx, dy) per frame with wraparound. Over the strip a layer travels dx*frames and
        dy*frames pixels, both exact multiples of the canvas width and height, so the frame after the
        last is pixel-identical to the first. The canvas is 4 px wider than the portrait (at SS x) so
        the horizontal period is a round number; the visible window is a crop of it. A layer of speed
        k crosses the portrait k times per loop, so k is the slowest dial there is.
  glow  A cosine of the frame index with period = frames: 0.5 - 0.5*cos(2*pi*f/frames). It is 0 at
        f = 0, peaks at the midpoint and returns to 0, with zero slope at both ends, so the wrap has
        no discontinuity in value or in rate. The mask is a flood fill inward from the frame edge
        through turquoise pixels, blurred, so the backdrop pulses and the character does not.

Deterministic: fixed seed, no wall clock, no network. Re-running reproduces every strip byte for byte.

Usage:
    python build_animated_portrait.py                       # build every subject + preview GIFs
    python build_animated_portrait.py --subject mlulu       # build one
    python build_animated_portrait.py --no-write            # previews only, do not touch mod_folder
    python build_animated_portrait.py --subject mlulu --frames 80   # rain frames: a multiple of 40
    python build_animated_portrait.py --set rain_gain=1.4 --set glow_amp=0.30
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
LEADERS = ROOT / "mod_folder" / "gfx" / "leaders" / "MLT"
PREVIEW_DIR = ROOT / "event_images" / "portrait"

W, H = 156, 210          # one frame, matching every OWB leader portrait
SS = 4                   # supersample factor for the rain canvas
SEED = 20250907

# Rain loop geometry. Per frame a layer of speed k travels (DX*k, DY*k) SS-pixels.
# Seamlessness needs DX*k*frames % CANVAS_W == 0 and DY*k*frames % CANVAS_H == 0.
DX, DY = 0, 21           # straight down. Loop closure fixes the possible leans: over the strip a
                         # layer must travel a whole number of canvas periods, so at 40 frames the
                         # per-frame step can only be 0, 4, 8 ... real px across (16, 32 ... at SS x)
                         # against 5.25 down - 0 deg or 37 deg, nothing between. A gentler lean needs
                         # more frames: 80 allow DX = 8 (~21 deg) at twice the file size.
CANVAS_W = 640           # 4 px wider (at SS x) than W*SS = 624, so 16*40 = 640 closes exactly
CANVAS_H = H * SS        # 840; 21*40 = 840 closes exactly

SUBJECTS = {
    "mlulu": dict(
        src="mlulu.dds",
        out="mltd_mlulu_animated.dds",
        sprite="GFX_Portrait_mltd_mlulu_animated",
        effect="rain",
        frames=40,        # a multiple of 40, so every layer closes
        fps=12,
        params=dict(
            slant=DX / DY,        # streak direction = travel direction
            rain_gain=1.05,       # overall rain brightness
            haze=0.014,           # faint cold wash pulsing once per loop
            cool=0.026,           # constant cold cast, keeps the portrait in the weather
            # per layer: (speed multiple, streak count, length px @SS, width px @SS, brightness)
            layers=((1, 230, 22, 1.3, 0.18),
                    (2, 145, 34, 1.8, 0.26),
                    (3, 80, 48, 2.4, 0.36)),
            rain_rgb=(158, 196, 226),
        ),
    ),
    "drowned_herald": dict(
        src="mltd_drowned_herald.dds",
        out="mltd_drowned_herald_animated.dds",
        sprite="GFX_Portrait_mltd_drowned_herald_animated",
        effect="glow",
        frames=24,
        fps=8,            # 24 frames at 8 fps = a 3 s throb
        params=dict(
            # backdrop test: teal excess min(G,B) - R, then a green floor, both 0..255
            teal_lo=5.0,
            teal_span=10.0,
            green_lo=26.0,
            green_span=34.0,
            connect=0.35,         # score above which a pixel joins the border-connected blob
            blur=3.0,             # mask softening, px
            glow_amp=0.18,        # peak brightening of the backdrop
            glow_tint=(120, 235, 232),   # what the glow adds, before amplitude
            tint_mix=0.45,        # how much of the glow is tint rather than plain lift
        ),
    ),
}


def load(path: Path) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    if img.size != (W, H):
        raise SystemExit(f"{path} is {img.size}, expected {(W, H)}")
    return np.asarray(img, dtype=np.float32) / 255.0


def to_img(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8), "RGB")


# ------------------------------------------------------------------------------------------ rain
def draw_layer(rng, count: int, length: int, width: float, slant: float) -> np.ndarray:
    """One periodic rain layer on the SS x canvas, as a 0..1 intensity map."""
    canvas = np.zeros((CANVAS_H, CANVAS_W), dtype=np.float32)
    ys = rng.integers(0, CANVAS_H, size=count)
    xs = rng.integers(0, CANVAS_W, size=count)
    strength = rng.uniform(0.45, 1.0, size=count).astype(np.float32)
    lengths = (length * rng.uniform(0.6, 1.25, size=count)).astype(np.int32)
    half = max(1, int(round(width)))
    for y0, x0, s, ln in zip(ys, xs, strength, lengths):
        t = np.arange(ln, dtype=np.float32)
        # taper both ends so a streak has a bright body and fades out head and tail
        fade = np.sin(np.pi * (t + 0.5) / ln) ** 0.7
        yy = (y0 + t.astype(np.int32)) % CANVAS_H
        xc = x0 + slant * t
        for off in range(-half, half + 1):
            w = max(0.0, 1.0 - abs(off) / (half + 0.5))   # triangular cross-section
            if w <= 0.0:
                continue
            xx = (np.rint(xc).astype(np.int32) + off) % CANVAS_W
            np.maximum.at(canvas, (yy, xx), fade * s * w)
    return canvas


def downsample(canvas: np.ndarray) -> np.ndarray:
    x0 = (CANVAS_W - W * SS) // 2
    win = canvas[:, x0:x0 + W * SS]
    return win.reshape(H, SS, W, SS).mean(axis=(1, 3))


def frames_rain(base: np.ndarray, frames: int, p: dict) -> list[Image.Image]:
    rng = np.random.default_rng(SEED)
    layers = [(k, bright, draw_layer(rng, n, ln, wd, p["slant"]))
              for (k, n, ln, wd, bright) in p["layers"]]
    rain_rgb = np.array(p["rain_rgb"], dtype=np.float32) / 255.0
    cold = np.array([0.42, 0.58, 0.78], dtype=np.float32)
    ground = base * (1.0 - p["cool"]) + cold * base.mean(axis=2, keepdims=True) * p["cool"]

    out = []
    for f in range(frames):
        acc = np.zeros((H, W), dtype=np.float32)
        for k, bright, canvas in layers:
            rolled = np.roll(canvas, (DY * k * f) % CANVAS_H, axis=0)
            rolled = np.roll(rolled, (DX * k * f) % CANVAS_W, axis=1)
            acc += downsample(rolled) * bright
        acc *= p["rain_gain"]
        haze = p["haze"] * (0.5 - 0.5 * np.cos(2.0 * np.pi * f / frames))
        rgb = ground * (1.0 - haze) + cold * haze + acc[..., None] * rain_rgb
        out.append(to_img(rgb))
    return out


# ------------------------------------------------------------------------------------------ glow
def hsv_parts(rgb: np.ndarray):
    mx, mn = rgb.max(2), rgb.min(2)
    d = np.maximum(mx - mn, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx)
    i = mx == r
    h[i] = ((g - b)[i] / d[i]) % 6
    i = mx == g
    h[i] = ((b - r)[i] / d[i]) + 2
    i = mx == b
    h[i] = ((r - g)[i] / d[i]) + 4
    return (h * 60.0) % 360.0, np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0), mx


def blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Separable Gaussian, edge-clamped."""
    if sigma <= 0:
        return a
    rad = max(1, int(round(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-rad, rad + 1) / sigma) ** 2)
    k /= k.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (rad, rad)
        padded = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i, w in enumerate(k):
            sl = [slice(None), slice(None)]
            sl[axis] = slice(i, i + out.shape[axis])
            acc += w * padded[tuple(sl)]
        out = acc
    return out


def background_mask(base: np.ndarray, p: dict) -> np.ndarray:
    """The turquoise backdrop, not the character.

    Hue alone does not separate them: the Herald's robes sit in the same 150-195 band as the
    backdrop, and a hue+saturation test scores robe pixels 0.6-0.9. What does separate them is
    *teal excess against red*, min(G,B) - R: median 28 on the backdrop against 2 on the figure.
    (Plain G - max(R,B) fails - it catches the yellow-green light spilling off the skull's jaw.)
    The score is then restricted to the blob connected to the frame edge, which drops the few
    hundred stray interior pixels, and blurred for a soft boundary.
    """
    a = base * 255.0
    teal = np.minimum(a[..., 1], a[..., 2]) - a[..., 0]
    score = (np.clip((teal - p["teal_lo"]) / p["teal_span"], 0.0, 1.0)
             * np.clip((a[..., 1] - p["green_lo"]) / p["green_span"], 0.0, 1.0))
    member = score > p["connect"]
    reach = np.zeros_like(member)
    reach[0, :] = member[0, :]
    reach[-1, :] = member[-1, :]
    reach[:, 0] = member[:, 0]
    reach[:, -1] = member[:, -1]
    while True:                                  # 4-connected flood inward
        grown = reach.copy()
        grown[1:, :] |= reach[:-1, :]
        grown[:-1, :] |= reach[1:, :]
        grown[:, 1:] |= reach[:, :-1]
        grown[:, :-1] |= reach[:, 1:]
        grown &= member
        if grown.sum() == reach.sum():
            break
        reach = grown
    return np.clip(blur(score * reach, p["blur"]), 0.0, 1.0)


def frames_glow(base: np.ndarray, frames: int, p: dict) -> list[Image.Image]:
    mask = background_mask(base, p)[..., None]
    tint = np.array(p["glow_tint"], dtype=np.float32) / 255.0
    out = []
    for f in range(frames):
        pulse = 0.5 - 0.5 * np.cos(2.0 * np.pi * f / frames)
        lift = p["glow_amp"] * pulse * mask
        rgb = base * (1.0 + lift * (1.0 - p["tint_mix"])) + tint * lift * p["tint_mix"]
        out.append(to_img(rgb))
    return out


# ---------------------------------------------------------------------------------------- output
def write_strip(frames: list[Image.Image], path: Path) -> None:
    strip = Image.new("RGB", (W * len(frames), H))
    for i, fr in enumerate(frames):
        strip.paste(fr, (i * W, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    # no pixel_format kwarg -> uncompressed A8R8G8B8, the class OWB's leader portraits use
    strip.convert("RGBA").save(path)


def write_previews(name: str, frames: list[Image.Image], fps: int) -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    gif = PREVIEW_DIR / f"mltd_{name}_animated_preview.gif"
    big = [f.resize((W * 2, H * 2), Image.LANCZOS) for f in frames]
    big[0].save(gif, save_all=True, append_images=big[1:], duration=int(1000 / fps), loop=0)
    n = min(8, len(frames))
    step = max(1, len(frames) // n)
    picks = [frames[i * step] for i in range(n)]
    sheet = Image.new("RGB", (W * n, H), (20, 20, 24))
    for i, fr in enumerate(picks):
        sheet.paste(fr, (i * W, 0))
    sheet.save(PREVIEW_DIR / f"mltd_{name}_animated_sheet.png")
    print(f"  preview {gif.name}")


EFFECTS = {"rain": frames_rain, "glow": frames_glow}


def build(name: str, cfg: dict, frames: int, write: bool) -> None:
    p = cfg["params"]
    if cfg["effect"] == "rain":
        for k, *_ in p["layers"]:
            if (DX * k * frames) % CANVAS_W or (DY * k * frames) % CANVAS_H:
                raise SystemExit(f"--frames {frames} does not close the rain loop for layer speed {k}; "
                                 f"use a multiple of 40")
    base = load(LEADERS / cfg["src"])
    imgs = EFFECTS[cfg["effect"]](base, frames, p)
    write_previews(name, imgs, cfg["fps"])
    if not write:
        print(f"  --no-write: {cfg['out']} not written")
        return
    out = LEADERS / cfg["out"]
    write_strip(imgs, out)
    print(f"  wrote {out.name}  {W * len(imgs)}x{H}  {len(imgs)} frames  {out.stat().st_size:,} bytes")
    print(f"        {cfg['sprite']}: noOfFrames = {len(imgs)}, animation_rate_fps = {cfg['fps']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subject", choices=sorted(SUBJECTS), help="build one subject (default: all)")
    ap.add_argument("--frames", type=int, help="override the frame count for the selected subject(s)")
    ap.add_argument("--no-write", action="store_true", help="previews only, do not touch mod_folder")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a scalar parameter (rain_gain, haze, cool, glow_amp, blur, ...)")
    a = ap.parse_args()

    for name in ([a.subject] if a.subject else sorted(SUBJECTS)):
        cfg = {**SUBJECTS[name], "params": dict(SUBJECTS[name]["params"])}
        for item in a.set:
            k, _, val = item.partition("=")
            if k in cfg["params"] and not isinstance(cfg["params"][k], tuple):
                cfg["params"][k] = float(val)
        print(f"{name} ({cfg['effect']}):")
        build(name, cfg, a.frames or cfg["frames"], not a.no_write)


if __name__ == "__main__":
    main()
