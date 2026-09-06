# OWB - Rising Tide

<iframe src="https://github.com/sponsors/JonathanWoollett-Light/button" title="Sponsor JonathanWoollett-Light" height="32" width="114" style="border: 0; border-radius: 6px;"></iframe>

*A submod for [Old World Blues](https://steamcommunity.com/sharedfiles/filedetails/?id=2265420196), for the Mirelurk Tribe (`MLT`).*

**Status:** first content drop, **play-tested once**. The first run found summoned divisions spawning without equipment; that fix and everything after it is not yet re-tested: visible decision cooldowns, the offering decisions, Feed the Spawning Pools, the Star Spawn rebalance, capital victory points, the two animated portraits, the quadrupled summon costs, doubled gifts and the custom division icons. After each change, read `logs/error.log` and confirm `logs/system.log` lists `Active Mod: OWB - Rising Tide` before trusting anything below.

## Features

Everything unlocks after OWB's final MLT focus, *The Kingdom of M'lyeh*, which now also fires an event for MLT and a world news event.

- **Gifts from the Deep** - a decision category of five 30-day missions (Tide / Shell / Current / Brood / Abyss: +20 % army attack, defence and organisation, +30 % recruitable population, +20 % stability - each Book focus shows the one it unlocks). Each costs political power and manpower and feeds the *Gifts from the Deep* dynamic modifier. One at a time; two after the Grand Ritual; permanent (and the category gone) after the Final Ritual.
- **The Books of M'lyeh** - five focuses fanned under *Gifts from the Deep*; each requires control of a notable state in the region (Arago, The Warren, Paisley Pit, Arroyo, The Maw) and unlocks one gift. Reading 1 / 3 / 5 of them gates *Call of the Deep Ones*, *The Grand Ritual* and *The Deep Ones Walk*.
- **The Deep Ones** - a new special-forces creature unit with its own equipment and a locked, script-only 20-width division template, summoned by a decision that sacrifices 8,000 people drawn from every province of the realm at once, each giving in proportion to its size (the division rises at the capital). After *The Deep Ones Walk* the reward tech is granted, the template unlocks and the unit can be trained like any other (its equipment is already producible from the first summon).
- **The Star Spawn** - the next locked, script-only 20-width division, spawned when the Deep Ones are released and unlocked in turn by the Final Ritual. Each one is a siege engine in its own right: the strongest creature equipment in the game by a wide margin, and a battalion needs only ten of them (a Deep One battalion needs twenty), so a division is eighty monsters rather than three hundred. Summoned divisions arrive fully equipped, and their equipment is producible from the first summon.
- **The Grand Ritual** and **The Final Ritual** - 100-day focuses that require a national population of 100,000 / 200,000. Completing them also makes *Gifts from the Deep* grant +50 (then +100) weekly manpower. For the duration of the focus a national spirit applies heavy debuffs, including 10 % and 20 % off division organisation, and a *daily* population toll across every owned state (0.1 %, then 0.25 % - about 9.5 % / 22 % over the ritual); completion lifts the spirit and fires an MLT event plus a world news event ("The Seas Grow Darker", "The Stars Are Right"). Once started they cannot be cancelled. *Gifts from the Deep* unlocks when *The Kingdom of M'lyeh* completes but is deliberately not drawn as its child; the Books fan out beneath it and the rest run down the centre. *Call of the Deep Ones* and *The Deep Ones Walk* each open a single-option event that delivers their effects.
- **Offerings to the Deep** - two repeatable decisions in the *Children of the Deep* category that trade the tribe's people for what the sea owes it: a thousand of the faithful for a hoard of bottle caps, or fifteen hundred to make fresh water break open under the capital for good.
- **Feed the Spawning Pools** - a continuous focus, alongside Old World Blues' own. While it is running, mirelurk, Deep One and Star Spawn equipment costs 15 % less to build, for 1 political power a day. Old World Blues' two creature discounts are both closed to the Mirelurk Tribe, so this is its only one.
- **A capital worth taking** - forming the kingdom raises M'lyeh from 10 victory points to 25 and its port to 10.
- **Reward Technologies tab** - the Deep Ones and Star Spawn techs sit in the Units row beside Faeries.
- **Unit icons** - original division/counter icons for both units (a fish-man and a Cthulhu bust, with NATO-counter variants), drawn procedurally by `build_unit_icons.py`.
- **Outsider Warfare** - all 16 doctrine techs now also buff amphibious platoons (mirelurks, Deep Ones, Star Spawn).
- **Indoctrinate the Faithful** - an MLT-only intelligence operation (La Resistance DLC) that converts 1,500 people of a country you have a network in into MLT manpower.
- **M'lulu** - OWB's portrait and small icon re-graded darker and colder, and the portrait now **animated**: rain falls across it in a seamless two-second loop (`build_animated_portrait.py` builds the 40-frame strip). As a field marshal she gains the *Animal Friend* and *Invader* traits.
- **Coral Prophet Anastasia** - gains *Animal Friend* and a bespoke portrait.
- **The Drowned Herald** - a new general (a notch below M'lulu) who takes command when the *Kingdom of M'lyeh* event fires. The turquoise mist behind him breathes, in a three-second loop. Both extra portraits are cropped by `build_leader_portraits.py` and animated by `build_animated_portrait.py`.
- **A main menu of its own** - the flooded street from *Call of the Deep Ones* becomes the main-menu background, the Old World Blues header logo becomes the *Rising Tide* marquee, and the rain **falls**: two scrolling sheets at different speeds, over the top.
- **Workshop art** - an animated Steam Workshop preview built to the Old World Blues submod house pattern: rain falling across the marquee (`build_workshop_thumbnail.py`, output `mod_folder/thumbnail.gif`).
- **A kingdom without the hangover** - the Black Hollows Night hatching pays 300 political power instead of forcing war economy, closed economy and the worst conscription law on the tribe, and forming the kingdom no longer inflicts Old World Blues' *Cultural Upheval* spirit.

Design notes, tunables and the reasoning behind every identifier are in `CLAUDE.md`.

## Layout

| Path | Contents |
| --- | --- |
| `mod_folder/` | The mod as HOI4 sees it. **Only this directory ships.** |
| `mod_folder/descriptor.mod` | Mod metadata. No `path=`, no `replace_path`. |
| `mod_folder/thumbnail.gif` | The Steam Workshop preview image, animated. The **only** thumbnail that ships; the still lives repo-side at `event_images/workshop/thumbnail.png`. |
| `mod_folder/gfx/loadingscreens/mltd_main.dds`, `mod_folder/gfx/interface/logo_game_*.dds`, `mod_folder/gfx/interface/mltd_rain_*.dds` | Main-menu background, header logo (static and animated) and the rain. Built by `build_main_menu.py`. |
| `event_images/`, `build_event_pictures.py`, `build_portrait.py`, `build_animated_portrait.py`, `build_unit_icons.py`, `build_focus_icons.py`, `build_leader_portraits.py`, `build_workshop_thumbnail.py`, `build_main_menu.py` | Source images and the scripts that rebuild the event pictures, the graded M'lulu portrait/icon, her animated rain strip, the two unit-icon sets, the purple book focus icon, the Anastasia / Drowned Herald portraits, the Workshop title image and the main menu. `event_images/SOURCES.md` lists origin/licence status - complete it before any Workshop upload. |
| `workshop_page/` | Screenshots for the Steam Workshop item's gallery, built by `build_workshop_page.py`. Repo-only; see `workshop_page/README.md`. |
| repo root | Docs and tooling that must never ship. |

## Install

1. Copy `mod_folder/descriptor.mod` to `C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\rising_tide.mod`.
2. Append one line to that copy: `path="C:/Users/<you>/Documents/rising-tide/mod_folder"` - absolute, **forward slashes**, no trailing slash, pointing at `mod_folder`. It is machine-specific, which is why it is not in the repo. (Already installed on this machine.)
3. In the launcher: **Reload Installed Mods**, then add both this mod and Old World Blues to a playset and enable both.
4. **Load order.** `dependencies={ "Old World Blues" }` in *both* `mod_folder/descriptor.mod` and the installed launcher `.mod` is what makes this mod load **after** OWB, so our files win on any overlap and OWB's 95 `replace_path` entries do not delete ours - see OWB's own guide, `<OWB>/doc/OWB_MODDING_README.txt`: "After adding this your mod will load after OWB and won't be replaced by files we have or our replace_paths". Keep that block in both files. If you also order the playset by hand, put Rising Tide **below** Old World Blues - lower in the list loads later.

## How overriding works

This submod declares **no `replace_path`** and merges additively over OWB: ship a file at the same relative path to replace OWB's whole file, or use a new `mltd_`-prefixed filename to add content. Never add `replace_path` - OWB declares 95.

Seven OWB files are overridden: `events/nf_mlt.txt` (the hatching pays political power instead of changing laws), `common/national_focus/Mirelurk Tribe (MLT) Focus.txt` (to add focuses to the existing tree), `common/continuous_focus/generic.txt` (to add one continuous focus to the only palette), `common/technologies/tech_fallout_land_doctrine.txt` (to buff amphibious units in Outsider Warfare), `common/characters/MLT.txt` (traits, Anastasia's portrait, the Drowned Herald), `history/countries/MLT - Mirelurk Tribe.txt` (one line: recruit the Herald at start) and `common/script_enums.txt` (our equipment ids in the documentation enum). All are byte copies of OWB's files plus insertions - the characters file additionally replaces four of Anastasia's lines and two of M'lulu's. The authoritative override rules, naming conventions and encoding requirements live in `CLAUDE.md`; read it before editing anything under `mod_folder/`.

## Workshop art

`build_workshop_thumbnail.py` renders `event_images/workshop/thumbnail.png` (512x512, ~400 KB; Steam caps the
preview at 1 MB) plus 128 px and 77 px previews under `event_images/workshop/`, which are the sizes
the Workshop grid and list actually show. **Only the GIF ships**; the still is kept repo-side
because it is what the GIF is graded against and the image to hand anyone who wants a static one.

There is deliberately **no `picture=` key** in either `.mod` file, and no `thumbnail.png` at the mod
root. That mirrors *The Fire Rises* (Workshop item 3350890356), the one installed mod with a working
animated Workshop preview, exactly. The first publish here did set `picture="thumbnail.png"` and the
Workshop item took the still image; pointing the key at the `.gif` instead is untried, and no
installed mod does it - all 11 that set `picture=` use a `.png`. If a publish still lands a still
image, set the preview by hand on the Workshop page: that needs no re-upload and definitely accepts
a GIF.

The layout is measured off ten installed OWB submod thumbnails rather than invented. All of them
share one formula: a painted background, a band of character busts across the upper third, and a
**neon marquee** across the lower middle - a chamfered hexagon whose outline is a glowing tube with
white fluorescent-tube gaps in the centre of its top and bottom edges, carrying the shared
"Old World Blues" wordmark with the submod's own name beneath it. East Coast Rebirth and Rustbelt
Rising also hang a weathered road sign below it, which is where our "Welcome to M'lyeh" plate comes
from.

No mod ships that wordmark as a reusable asset, so `event_images/workshop/owb_wordmark.png` was
matted out of *OWB - Fountain of Dreams*' thumbnail - the only one with light lettering on a dark
panel, and so the only one that mattes cleanly (the rust-panel versions do not separate). It arrives
silver with a violet keyline, which is that submod's own treatment; `retint_wordmark()` maps it to
the gold that Old World Blues, East Coast Rebirth, Rustbelt Rising and Over The Horizon all use.
`--silver` keeps the silver, which NCR-vs-Legion also uses.

Tunables live at the top of the script: `SATURATION` (the references sit at mean chroma 0.25-0.47),
`WORDMARK_GOLD`, and the layout block `SX0/SX1/SY0/SY1/CH` (the hexagon), `WM_*` / `SUB_*` (the two
type lines) and `PLATE_*` (the road sign).

### The animated preview

`python build_workshop_thumbnail.py --gif` additionally renders
`mod_folder/thumbnail.gif`: the same image with rain falling and the neon
breathing, 350x350, 32 frames at 40 ms (a 1.28 s loop), ~740 KB. Steam accepts an
animated GIF as a Workshop preview image - *The Fire Rises* (Workshop item
3350890356) is the OWB-adjacent precedent, and it sets the budget: **1 MiB, moving
or not**, which is the only thing deciding the size, frame count and palette.

Three things keep it inside that budget, and all three are load-bearing:

- **Frames are delta-encoded** against what the viewer is still looking at, not
  against the previous frame - comparing per-frame would let a pixel creep away
  one `GIF_TOLERANCE` step at a time and the error would accumulate over the loop.
  About 9 % of each frame is redrawn; the rest is transparent over a non-disposed
  canvas.
- **Dithering is off.** Its noise is random, and random noise is exactly what
  run-length compression cannot pack.
- **The palette is chroma-weighted.** Median cut allocates entries by pixel count,
  and this image is overwhelmingly low-chroma teal, so a plain palette starves the
  gold wordmark, the violet outer tube and M'lulu's green eyes - the three things
  carrying the identity - and they snap to grey-blue. Re-feeding the most saturated
  decile (`CHROMA_WEIGHT`) fixes it.

The rain loop closes because the streaks are drawn into a tile periodic over
`(W/2, W)` and rolled by a whole number of pixels per frame whose total over the
loop is an exact multiple of both periods; `rain_tile()` asserts this. The neon
breath uses `0.5 - 0.5*cos(2*pi*f/frames)`, which is 0 with zero slope at both
ends, so any frame count closes.

The GIF is the only thumbnail in `mod_folder/`, and there is no `picture=` key -
see **Workshop art** above for why, and for the fallback if a publish still lands
a still image. It costs every subscriber ~740 KB of download.

### Page images

The thumbnail is one image; the **Additional Previews** gallery on the item page is another thing
entirely, and lives in `workshop_page/`:

```
python build_workshop_page.py "<screenshot>" --name 02_something
```

1920x1080, scaled preserving aspect and centre-cropped only if the source is not already 16:9 (game
screenshots at 2560x1440 are, so nothing is cropped). **JPEG, not PNG** - Steam caps a Workshop
image at 1 MiB and a 1920x1080 PNG of a scene this grainy is ~2.9 MB, so PNG cannot be used at this
size; quality is searched down from 95 until the file fits 900 KB, at 4:4:4 because these frames are
mostly UI text and thin neon.

**Read `event_images/SOURCES.md` before uploading.** The title image is built on the same
unverified third-party art as the event pictures, and it is the one asset that is public before
anyone installs the mod.

## Main menu

`python build_main_menu.py` replaces the Old World Blues main menu with this mod's:

| Output | What | Size |
| --- | --- | --- |
| `gfx/loadingscreens/mltd_main.dds` | The background - `event_images/call_src.jpg`, the flooded street from *Call of the Deep Ones*, graded colder | 1910x1440, 10.5 MB |
| `gfx/interface/logo_game_static.dds` | The header logo - the *Rising Tide* marquee, transparent | 443x303, 0.5 MB |
| `gfx/interface/mltd_logo_animated.dds` | The same marquee as a 16-frame strip, neon breathing | 7088x303 uncompressed, 8.2 MB |
| `gfx/interface/mltd_rain_anim{1,2}.dds` | Two scrolling rain sheets | 2560x1792 DXT5, 4.4 MB each |
| `gfx/interface/mltd_rain_{base,mask}.dds` | The sprite's rect: transparent base, flat mask | 2560x1792 DXT5, 4.4 MB each |

**1910x1440 and 443x303 are not choices** - they are what OWB's `load_colorado.dds` and
`logo_game_static.dds` are, and tnkd's `tnk_main.dds` matches the first. The frontend scales the
background to *cover*, so on a 16:9 screen only the middle ~1074 rows are ever seen; the painting
is placed exactly there and the bands above and below are mirrored, blurred extension for 4:3.

Three script files do the wiring, and they are deliberately separable:

- `interface/z_fallout_ui.gfx` - **OVERRIDE** of OWB's file, one line changed: `GFX_frontend_bg`
  now points at `mltd_main.dds`. This is what tnkd does. Only OWB and tnkd ship this file, so the
  collision risk is low. (Copy OWB's *current* bytes when re-diffing - tnkd's copy is stale and is
  missing `GFX_generic_text_bg_48_owb`.)
- `interface/mltd.gfx` - **new sprite** `GFX_frontend_bg_mltd_rain`, cloned from OWB's
  `GFX_frontend_bg_snow_anim`.
- `interface/frontendmainview.gui` - **OVERRIDE** of OWB's file, re-enabling the overlay `iconType`
  that OWB ships commented out and pointing it at our rain sprite. **This file is the only reason
  the rain moves, and the only high-collision file here** - OWB, East Coast Rebirth, Enclave Reborn
  Redux, Rustbelt Rising and Monarchs and Margaritas all ship it, and whichever loads last wins the
  whole main menu. Delete our copy and the background and logo still work; only the rain stops.
  (ECR, Rustbelt and Monarchs override it for exactly this purpose, each pointing at their own
  `GFX_frontend_bg_*`, so this is the house idiom and the "one menu wins" outcome is unavoidable.)

The header logo ships twice. The static texture is a **texture-path override** of OWB's
`gfx/interface/logo_game_static.dds`, the way tnkd does it - no `.gfx` change (NCR-vs-Legion,
Enclave Reborn Redux and Fountain of Dreams also ship that path, so last loaded wins). Our
`frontendmainview.gui` then points the logo at `GFX_frontend_game_logo_mltd_animated` instead, a
16-frame strip at 8 fps whose neon swells and settles on a raised cosine - 0 with zero slope at
both ends, so the loop closes. The static file is the fallback if another submod's gui wins.

**The strip is uncompressed, like OWB's own `logo_game_animated.dds`.** DXT5 costs a quarter of the
size but quantises colour per 4x4 block, and a block straddling a bright neon edge and the
transparent black outside it gets endpoints spanning cyan to black: measured error on visible pixels
was mean 6 and peak **164**, which shows as a speckled fringe along every tube. Frames are traded
away instead - the breath is a slow, smooth ramp, so 16 frames step by under 2 luma levels each and
the joins are invisible. `LOGO_FRAMES` and `LOGO_FPS` must match `noOfFrames` and
`animation_rate_fps` in `interface/mltd.gfx`.

**The marquee's glow needs a bigger canvas than the thumbnail gives it.** The sign is laid out to
sit 18 px from the edge of a 512-wide thumbnail it is meant to bleed off, but its outer bloom is a
Gaussian of sigma 32, so on that canvas the bloom is cut flat - which as a logo showed up as a hard
vertical edge where alpha jumped 0 to 224 in a single column. `padded_sign_canvas` re-renders the
same sign on a canvas widened by `LOGO_PAD`, shifting every absolute coordinate the sign builder
reads (`W`, `HEXW`, `SY0/SY1/SYM`, `GC`, `WM_TOP`, `SUB_TOP`); sizes and differences are
translation-invariant and are left alone. The crop then crosses the bloom at `LOGO_EDGE`, low enough
that the step is invisible - the build prints the strongest alpha left on the crop border, which
should read ~0.02 rather than ~0.9.

### How the rain works

`animation = {}` blocks attach **only to `spriteType`** - across vanilla and all 25 installed mods
there are ~56,000 of them and not one sits on a `corneredTileSpriteType`, which is what
`GFX_frontend_bg` is. So the rain cannot be an animation on the background itself; it has to be a
second, fully transparent sprite laid over it, which is precisely how OWB's (disabled) snow works.
Ours reuses OWB's `bg_snow_anim_background.dds` (alpha 0 everywhere, so only the animations draw)
and `bg_snow_anim_mask.dds` (a flat 191, so they draw at 75% over the whole screen) unchanged and
by path, without copying either.

Colour lives in RGB and shape lives in **alpha**, which is how OWB's snow textures are built.
Streaks are stamped with modular indexing so they wrap in both axes - a seam would otherwise sweep
across the screen once per cycle - and tapered along their length so they fade in and out instead
of ending square. Coverage is 2.4% and 4.9% of alpha, against OWB's snow at 1.7% and 3.2%.

### Why the rain textures are taller than the screen

The overlay sprite is drawn **unscaled, at exactly the size of its BASE texture** - the one named by
`texturefile`, *not* the scrolling animation textures, which are sampled inside the rect the base
defines. It is anchored to the top-left of the `frontend_background` container, and that container
is 1920x1440 scaled to **cover**, so on anything wider than 4:3 it overflows vertically and its
top-left sits **above** the top of the screen:

```
scale    = max(W / 1920, H / 1440)
overflow = (1440 * scale - H) / 2      # 180 px at 1080p, 240 px at 1440p
```

A sprite only `H` tall therefore runs out `overflow` px short of the bottom, leaving an empty band.
That is why the base and mask here are **ours and 2560x1792** rather than OWB's
`bg_snow_anim_background.dds` and `bg_snow_anim_mask.dds`, which are 2560x1440 and 240 px short on a
1440p screen - and almost certainly why OWB ships its snow overlay commented out, since it has
exactly the same shortfall.

This was established by experiment, not from documentation: enlarging the animation sheets alone
changed nothing, which is what identified the base texture as the thing that sets the rect.

For 16:9 the requirement is `height >= 7/6 * H` and `width >= W`. At the fixed 2560 width the worst
case is 1440p, needing 1680; 1792 leaves margin for an overflow up to 352 px. **4K (needs 3840x2520)
and 21:9 (needs 3440x2010) still fall short** - raise `RAIN_W` and `RAIN_H` in
`build_main_menu.py` and nothing else; streak counts are per 2560x1440 and rescale with the canvas,
so the rain does not get heavier. The cost is four textures, so 3840x2560 would be ~9.8 MB each
instead of 4.4.

`build_main_menu.py --preview` models this geometry rather than guessing at it: it reads the rect
off the base texture that actually ships, prints the rows and columns covered, and warns if they do
not reach every edge. Pass a different `screen=` to `build_preview()` to check another display.

`animationtexturescale` must stay in step with `RAIN_SCALE` in `build_main_menu.py`, which sizes
the streaks for it: the sprite magnifies by `1 / scale`, so at 0.75 a 60 px streak is 80 px on
screen. **`animationrotation` is the one parameter here that cannot be checked without launching
the game** - whether it rotates the texture along with the scroll direction is unknown, so the
streaks are drawn vertical and kept short, which reads as rain either way. 205 and 212 sit just
inside the range OWB's snow uses (210 and 220), which is known to fall downward.

## Update process

OWB updates silently invalidate every file we override, so re-diff after each one.

1. Get [WinMerge](https://winmerge.org/).
2. Compare every file in the submod against its OWB counterpart and update.
   1. 1st folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196\`
   2. 2nd folder: `C:\Users\jonat\Documents\rising-tide\mod_folder\`
   3. Untick `View > Show Left Unique Items`.
   4. The six overrides (`Mirelurk Tribe (MLT) Focus.txt`, `continuous_focus/generic.txt`, `tech_fallout_land_doctrine.txt`, `common/characters/MLT.txt`, `history/countries/MLT - Mirelurk Tribe.txt`, `common/script_enums.txt`) must end up as OWB's new file **plus only our insertions** (plus Anastasia's replaced lines) - keep each file's original line endings and BOM state.
   5. Delete the `.bak` files afterwards.
3. Play the game to test, then read `...\Hearts of Iron IV\logs\error.log` (and `text.log` for localisation - the `warbike_unlock_tech` collision there is intentional) and confirm `system.log` lists both `Old World Blues` and `OWB - Rising Tide` as active mods.

## Compatibility

- Any submod that ships its own `common/continuous_focus/generic.txt` conflicts: whichever loads later wins the whole palette, so either its continuous focuses or *Feed the Spawning Pools* will be missing.
- The [OWB Official NCR versus Caesar's Legion submod](https://steamcommunity.com/sharedfiles/filedetails/?id=3010015443) ships its own `Mirelurk Tribe (MLT) Focus.txt` **and** its own `tech_fallout_land_doctrine.txt`. Rising Tide overrides both; whichever mod loads later wins each whole file, so run one or the other, not both.
- With *OWB: Ultimate Tech Compatibility Mod* (3462816659), which re-lays the whole Reward Technologies tab, the Deep Ones / Star Spawn techs land on its `robco_unlock_tech` (4,24) and `FNR_bollinger_shipyards_unlock_tech` (4,28) in its "Schematics" row and overlap them. Cosmetic only - both stay grantable. No slot next to Faeries is free under both layouts.
- With *OWB Tech Expansion* (2821243420) loaded after this mod, its `countrytechtreeview.gui` has no `warbike_unlock_tech_tree` gridbox, so neither reward tech renders in the tab (they still work when granted by focus).
- The intelligence operation needs the La Resistance DLC; without it the file loads silently and the operation never appears.

## Plan

### High priority

- [ ] Re-test round 9: M'lulu's portrait rains and her small icon is right; the Deep Ones summon stays visible and greyed with a countdown instead of vanishing; the two Offerings decisions pay caps and capital water; *Feed the Spawning Pools* shows up in the continuous-focus palette and discounts creature equipment while selected; the Kingdom focus adds the victory points; a Star Spawn division still spawns fully equipped now that a battalion needs ten pieces instead of forty.
- [ ] Re-test the startup fixes: `error.log` must no longer list the four `script_enum_equipment_bonus_type` warnings or the two `recruit_character` errors for `events/mltd_events.txt` (the only lines in the last log that were ours), and the Drowned Herald must show up as a general once the *Kingdom of M'lyeh* event fires.
- [ ] Re-test after round 3: a summoned / focus-spawned division arrives **with** its equipment (160 / 80 spare in Logistics, hidden `Spawn of the Deep` tech in the equipment tooltip); the Grand / Final Ritual focus tooltips show the red modifier lines with values; the five focuses render as a column below the tree with no overlaps and no line from the Kingdom to Gifts; then the rest of the chain - Deep Ones tech in the Reward Technologies tab, gifts apply instantly and expire at 30 days, the toll ticks daily, the Deep Ones template is trainable after *The Deep Ones Walk*, the operation appears with an agency.
- [ ] Tune the toll and the population gates (`mltd_ritual_toll_factor`, 100,000 / 200,000 - see CLAUDE.md > The rituals) once you have seen them in play.

### Medium priority

- [ ] Bespoke art: focus icons (currently reused OWB sprites), a decision-category banner, cult-flavoured operation phases, and a properly repainted M'lulu (the shipped one is a colour grade).
- [x] Add the Workshop preview image and the matching `picture=` key in both `descriptor.mod` and the installed launcher `.mod`. Published as Workshop item [3798403425](https://steamcommunity.com/sharedfiles/filedetails/?id=3798403425); the launcher wrote `remote_file_id` into both files on upload. Image licences in `event_images/SOURCES.md` are **still unresolved**.
