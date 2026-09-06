# Steam Workshop page images

The screenshots uploaded to the Workshop item's **Additional Previews** gallery. Repo-only —
nothing here is inside `mod_folder/` and nothing ships to subscribers.

Not to be confused with:

| | What | Where |
| --- | --- | --- |
| **Preview image** | The single thumbnail Steam shows in grids and lists | `mod_folder/thumbnail.png` (and `thumbnail.gif`), built by `build_workshop_thumbnail.py` |
| **Page images** | The gallery on the item page | here, built by `build_workshop_page.py` |
| Build inputs | The wordmark source and render previews | `event_images/workshop/` |

## Contents

| File | Source | Notes |
| --- | --- | --- |
| `01_main_menu.jpg` | In-game screenshot, 2560x1440, taken 2026-09-09 | The mod's main menu: `mltd_main.dds` background, the *Rising Tide* header logo with its glow intact, and the animated rain reaching every edge. Replaces an earlier shot taken before those two fixes. Carries a "69 FPS" overlay in the top-left corner. |
| `02_focus_tree.jpg` | In-game screenshot, 2560x1440, taken 2026-09-09 | The Mirelurk Tribe focus tree scrolled to the Rising Tide branch: *Gifts from the Deep*, the five Books, and the centre column down to *The Final Ritual*. The tree is a narrow column, so most of the frame is empty black - zoom in with the focus-view controls before re-taking if you want it to fill. Carries a "70 FPS" overlay in the top-left corner. |
| `03_main_menu_animated.gif` | Screen recording, 2560x1440 @ 30 fps, 2026-09-09 | The main menu moving: rain falling, the marquee breathing. 640x360, 35 frames at 70 ms (2.45 s), 882 KB. Built by `build_recording_gif.py`, which finds the loop rather than assuming one. |

## Page text

`description.txt` is the item description in Steam's BBCode. Paste it straight into the Workshop
description field; Steam does not read it from the mod, so it has to be pasted by hand after any
edit. Tags used: `[h1]`-`[h3]`, `[b]`, `[i]`, `[list]`/`[*]`, `[hr][/hr]`.

## Format

`python build_workshop_page.py "<screenshot>" --name 02_something`  -- stills
`python build_recording_gif.py "<recording>" --name 03_something`  -- moving

- **1920x1080.** Scaled preserving aspect, centre-cropped first only if the source is not 16:9.
  Game screenshots at 2560x1440 already are, so nothing is cropped from them.
- **JPEG, quality searched down from 95 until the file is under 900 KB.** Steam caps a Workshop
  image at 1 MiB and a 1920x1080 PNG of a scene this grainy is about 2.9 MB, so PNG is not usable
  at this size at all. 4:4:4 (`subsampling=0`) — these frames are mostly UI text and thin neon,
  which 4:2:0 smears.
- Numbered prefixes set the gallery order.
- **Animated entries are GIF, 640x360, under 950 KB.** Steam caps a Workshop image at 1 MiB whichever
  it is, and 35 frames of falling rain is expensive, so a carousel GIF has to be a quarter of the
  stills' resolution. `build_recording_gif.py` walks a ladder of resolution, palette and tolerance
  until one fits and reports what it settled on.
- The loop is **searched for, not assumed**: the menu's rain sheets and logo only realign after about
  78 seconds, so the script scores every start/length pair and takes the shortest whose wrap is
  measurably smaller than the motion already on screen. Most lengths score ~1.1-1.25x a normal step -
  that is the noise floor, not a loop. A real one comes in near 0.7.

Screenshots taken by the mod author are the author's own; anything else needs a row in
`../event_images/SOURCES.md` before upload.
