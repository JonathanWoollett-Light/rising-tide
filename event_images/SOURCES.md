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
| `workshop/owb_wordmark.png` | `mod_folder/thumbnail.gif`, `event_images/workshop/thumbnail.png` and `gfx/interface/logo_game_static.dds` (the "Old World Blues" wordmark on the marquee) | Matted by hand out of `thumbnail.png` of Steam Workshop item **3296248182**, *OWB - Fountain of Dreams* (the only submod thumbnail with light lettering on a dark panel, so the only one that mattes cleanly). Every OWB submod reuses this wordmark; it originates with Old World Blues itself, which in turn styles it after Bethesda/Obsidian's *Fallout: New Vegas* "Old World Blues" DLC logo. | **unverified - two removes from a commercial game logo.** Reused here on the same footing as every other OWB submod thumbnail, but nobody in that chain has a licence on record |
| (generated) | `gfx/interface/logo_game_static.dds` | The marquee from `build_workshop_thumbnail.py` re-cropped by `build_main_menu.py`; inherits `workshop/owb_wordmark.png`. Overrides OWB's own header logo by path. | as `owb_wordmark.png` |
| (generated) | `gfx/interface/mltd_rain_anim{1,2}.dds`, `gfx/interface/mltd_rain_{base,mask}.dds` | All four drawn procedurally by `build_main_menu.py`. The two animation sheets carry the streaks; the base and mask are our own 2560x1792 pair rather than OWB's `bg_snow_anim_background.dds` / `bg_snow_anim_mask.dds`, which are 2560x1440 and leave an empty band below 1080p (see CLAUDE.md > Why the rain textures are taller than the screen). Nothing of OWB's is copied. | original |
| (generated) | `mod_folder/thumbnail.gif` (**the asset that ships**) and the repo-side still `event_images/workshop/thumbnail.png` | Both composed by `build_workshop_thumbnail.py` from `grand_ritual_src.webp` (background), `workshop/owb_wordmark.png`, and the three shipped portraits `mlulu.dds` / `mltd_drowned_herald.dds` / `mltd_anastasia.dds`. The marquee, the neon, the panel, the road plate and all type are original procedural work. | **inherits the worst status of its inputs - currently `unverified`.** This is the mod's most public image: it is the Workshop store art, not an in-game asset. Resolve `grand_ritual_src.webp`, `herald_src.jpg` and `owb_wordmark.png` before uploading |
| (generated) | `gfx/interface/decisions/mltd_decision_cat_{spectral_cabal,loid_ekt_storm,wardens_propaganda}.dds` | Old World Blues `gfx/interface/decisions/decision_cat_spectral_cabal.dds`, `decision_cat_loid_ekt_storm.dds` and `decision_cat_wardens_propaganda.dds`, content moved down 2 transparent rows (bottom 2 rows cropped) by `build_category_pictures.py` so they clear the category frame line | OWB asset derivative, as above |
| (generated) | `gfx/interface/decisions/mltd_cult_hood.dds` | Procedurally drawn by `build_decision_icons.py` (numpy + Pillow, no source image) | original |
| `agency/agency_src.jpg` | `gfx/interface/operatives/agencies/mltd_agency_logo_esoteric_order.dds` (redrawn as a gold-on-teal seal by `build_agency_logo.py`: skull and tentacles resampled, rings redrawn) | https://i.etsystatic.com/9715836/r/il/6ef88e/1438113134/il_fullxfull.1438113134_qfdl.jpg (Etsy listing image) - a stencil of **Marvel's HYDRA insignia**, chosen by the mod author for the *Hail M'lyeh* joke | **unverified - Marvel (Disney) trademark and copyright.** The emblem is recognisably HYDRA's, so a public Workshop item carrying it is a takedown risk; a redraw (a mirelurk skull, a different tentacle count) would clear it |
| (generated) | `gfx/interface/mltd_logo_animated.dds` | The same marquee as `logo_game_static.dds`, rendered by `build_main_menu.py` as a 16-frame strip with the neon breathing; inherits `workshop/owb_wordmark.png`. | as `owb_wordmark.png` |
| (generated) | `gfx/leaders/MLT/mltd_drowned_herald_animated.dds` | The shipped `mltd_drowned_herald.dds` with a procedural backdrop throb composited over it by `build_animated_portrait.py` (the throb is original; the mask is measured, not painted). | inherits `portrait/herald_src.jpg` - unverified |
| (generated) | `gfx/interface/counters/division_templates_{large,small}/custom_template_25{6,7}.dds` | Sliced by `build_unit_icons.py` from frame 1 of the battalion sheets it draws itself. | original |

Preview PNGs (`preview_*.png`, `compare_*.png`, `*_preview.png`, `*/preview.png`, `agency/mltd_agency_logo_strip.png`, `decision_icons/*.png`, `workshop/thumbnail_{128,77}.png`)
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
