# Image sources and licence status

Everything under `event_images/` is a source or preview; the shipped derivatives live under `mod_folder/gfx/`.
**Licence status is unverified for every third-party image below. Resolve (permission, licence, or replacement) before any Steam Workshop upload.**

| Source file | Shipped as | Origin | Licence status |
| --- | --- | --- | --- |
| `kingdom_src.webp` | `gfx/event_pictures/mltd_event_kingdom.dds` | https://punishedbacklog.com/wp-content/uploads/2019/09/sc-fp-preview__huge.jpg.webp (game screenshot / preview art hosted by Punished Backlog) | unverified |
| `grand_ritual_src.webp` | `gfx/event_pictures/mltd_event_grand_ritual.dds` | https://cdn.svc.asmodee.net/production-arkhamhorror/uploads/image-converter/2025/02/SL19_17055_HeedingtheCall_AlexanderKozachenko_web-scaled.webp - "Heeding the Call", Alexander Kozachenko, Arkham Horror (Fantasy Flight / Asmodee) | unverified - commercial card art |
| `final_ritual_src.jpg` | `gfx/event_pictures/mltd_event_final_ritual.dds` | https://i.etsystatic.com/8788928/r/il/dd1bac/524512049/il_570xN.524512049_7ybv.jpg (Etsy listing image) | unverified |
| `call_src.jpg` | `gfx/event_pictures/mltd_event_call.dds`, `gfx/loadingscreens/mltd_main.dds` (the main-menu background) | https://www.cgmagonline.com/wp-content/uploads/2016/03/frogwares-unveils-open-world-lovecraftian-game-the-sinking-city-3.jpg - The Sinking City press image (Frogwares), hosted by CGMagazine | unverified - commercial press/key art |
| `portrait/anastasia_src.jpg` | `gfx/leaders/MLT/mltd_anastasia.dds` | DeviantArt, deviation `d9rfgge` (wixmp CDN link supplied by the mod author) - artist not yet recorded | unverified - record artist + permission |
| `portrait/herald_src.jpg` | `gfx/leaders/MLT/mltd_drowned_herald.dds` | https://i.redd.it/293jfcd9b5z61.jpg (Reddit-hosted; original artist not yet recorded) | unverified - record artist + permission |
| `portrait/mlulu_original.png`, `portrait/MLT_mlulu_small_original.png` | `gfx/leaders/MLT/mlulu.dds`, `gfx/interface/ideas/character_small_icons/MLT_mlulu.dds` (colour-graded) | Old World Blues assets (`gfx/leaders/MLT/mlulu.dds`, `character_small_icons/MLT_mlulu.dds`) | OWB asset, redistributed only as a derivative inside an OWB-dependent submod |
| (generated) | `gfx/leaders/MLT/mltd_mlulu_animated.dds` | The already-graded `mod_folder/gfx/leaders/MLT/mlulu.dds` with a procedural rain loop composited over it by `build_animated_portrait.py` (rain is original, drawn from a seed) | OWB asset derivative, as above |
| (generated) | `gfx/interface/goals/mltd_book.dds` | Old World Blues `gfx/interface/goals/unique/CHO/cho_scriptorium.dds`, recoloured by `build_focus_icons.py` | OWB asset derivative, as above |
| (generated) | `gfx/interface/counters/**/unit_mltd_*`, `gfx/texticons/unit_mltd_*` | Procedurally drawn by `build_unit_icons.py` (original work; NATO-box geometry measured from vanilla) | original |
| `workshop/owb_wordmark.png` | `thumbnail.png` (the "Old World Blues" wordmark on the marquee) | Matted by hand out of `thumbnail.png` of Steam Workshop item **3296248182**, *OWB - Fountain of Dreams* (the only submod thumbnail with light lettering on a dark panel, so the only one that mattes cleanly). Every OWB submod reuses this wordmark; it originates with Old World Blues itself, which in turn styles it after Bethesda/Obsidian's *Fallout: New Vegas* "Old World Blues" DLC logo. | **unverified - two removes from a commercial game logo.** Reused here on the same footing as every other OWB submod thumbnail, but nobody in that chain has a licence on record |
| (generated) | `gfx/interface/logo_game_static.dds` | The marquee from `build_workshop_thumbnail.py` re-cropped by `build_main_menu.py`; inherits `workshop/owb_wordmark.png`. Overrides OWB's own header logo by path. | as `owb_wordmark.png` |
| (generated) | `gfx/interface/mltd_rain_anim{1,2}.dds` | Rain sheets drawn procedurally by `build_main_menu.py`. The sprite that scrolls them reuses OWB's `bg_snow_anim_background.dds` and `bg_snow_anim_mask.dds` unchanged, by path, without copying them. | original |
| (generated) | `thumbnail.png` | Composed by `build_workshop_thumbnail.py` from `grand_ritual_src.webp` (background), `workshop/owb_wordmark.png`, and the three shipped portraits `mlulu.dds` / `mltd_drowned_herald.dds` / `mltd_anastasia.dds`. The marquee, the neon, the panel, the road plate and all type are original procedural work. | **inherits the worst status of its inputs - currently `unverified`.** This is the mod's most public image: it is the Workshop store art, not an in-game asset. Resolve `grand_ritual_src.webp`, `herald_src.jpg` and `owb_wordmark.png` before uploading |

Preview PNGs (`preview_*.png`, `compare_*.png`, `*_preview.png`, `workshop/thumbnail_{128,77}.png`)
are build outputs, not sources.

**The Workshop title image is the highest-risk placement in this repo.** Everything else here is an
in-game asset seen only by people who already own the mod; `thumbnail.png` is the store front. It is
currently built from art whose licence is unverified. Two ways out, in order of preference:

1. Commission or find a licensed/permissive background painting and repoint `BG_SRC` in
   `build_workshop_thumbnail.py`; the rest of the image is already original work. The main-menu
   background has the same problem and the same one-line fix (`SRC` in `build_main_menu.py`) -
   it is seen by anyone who launches with the mod enabled, so it ranks just behind the thumbnail.
2. Fall back to the fully procedural composition explored during design (no third-party raster at
   all except the wordmark) - the working script for it is not kept in the repo, but the approach is
   recorded in README > Workshop art.
