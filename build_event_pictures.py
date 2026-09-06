"""Rebuild mod_folder/gfx/event_pictures/*.dds from event_images/.

OWB event pictures are 500x200 (news) / 500x194 (country), uncompressed A8R8G8B8 DDS.
Pillow writes exactly that header when .save() is called with NO pixel_format kwarg.
Run from the repo root:  python build_event_pictures.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "event_images"
OUT = ROOT / "mod_folder" / "gfx" / "event_pictures"
W, H = 500, 200

# name -> (source file, vertical crop anchor: 0 = top, 0.5 = centre, 1 = bottom)
PICTURES = {
    "mltd_event_kingdom": ("kingdom_src.webp", 0.5),
    "mltd_event_grand_ritual": ("grand_ritual_src.webp", 0.4),
    "mltd_event_final_ritual": ("final_ritual_src.jpg", 0.5),
    "mltd_event_call": ("call_src.jpg", 0.75),
}


def cover_crop(img, anchor_y):
    """Crop to W:H aspect, keeping full width when possible, anchored vertically."""
    sw, sh = img.size
    target = W / H
    if sw / sh > target:  # too wide: crop sides (centred)
        cw = round(sh * target)
        left = (sw - cw) // 2
        return img.crop((left, 0, left + cw, sh))
    ch = round(sw / target)  # too tall: crop top/bottom at the anchor
    top = round((sh - ch) * anchor_y)
    return img.crop((0, top, sw, top + ch))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (src, anchor) in PICTURES.items():
        img = Image.open(SRC / src).convert("RGBA")
        img = cover_crop(img, anchor).resize((W, H), Image.LANCZOS)
        dst = OUT / f"{name}.dds"
        img.save(dst)  # no pixel_format -> uncompressed A8R8G8B8, same header as OWB
        print(f"{dst.name}: {W}x{H} {dst.stat().st_size} bytes")


if __name__ == "__main__":
    main()
