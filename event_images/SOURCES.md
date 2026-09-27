# Image sources and licence status

Everything under `event_images/` is a source or preview; the shipped derivatives live under
`mod_folder/gfx/`. **Licence status is unverified for every third-party image below. Resolve
(permission, licence, or replacement) before any Steam Workshop upload.**

Each entry below is one source file, with what it ships as, its origin and its licence status.

- `kingdom_src.webp`
  - Shipped as: `gfx/event_pictures/mltd_event_kingdom.dds`
  - Origin: <https://punishedbacklog.com/wp-content/uploads/2019/09/sc-fp-preview__huge.jpg.webp>
    (game screenshot / preview art hosted by Punished Backlog)
  - Licence status: unverified
- `grand_ritual_src.webp`
  - Shipped as: `gfx/event_pictures/mltd_event_grand_ritual.dds`
  - Origin: "Heeding the Call", Alexander Kozachenko, Arkham Horror (Fantasy Flight / Asmodee) -
    <https://cdn.svc.asmodee.net/production-arkhamhorror/uploads/image-converter/2025/02/SL19_17055_HeedingtheCall_AlexanderKozachenko_web-scaled.webp>
  - Licence status: unverified - commercial card art
- `final_ritual_src.jpg`
  - Shipped as: `gfx/event_pictures/mltd_event_final_ritual.dds`
  - Origin: <https://i.etsystatic.com/8788928/r/il/dd1bac/524512049/il_570xN.524512049_7ybv.jpg>
    (Etsy listing image)
  - Licence status: unverified
- `call_src.jpg`
  - Shipped as: `gfx/event_pictures/mltd_event_call.dds`, `gfx/loadingscreens/mltd_main.dds` (the
    main-menu background)
  - Origin: The Sinking City press image (Frogwares), hosted by CGMagazine -
    <https://www.cgmagonline.com/wp-content/uploads/2016/03/frogwares-unveils-open-world-lovecraftian-game-the-sinking-city-3.jpg>
  - Licence status: unverified - commercial press/key art
- `portrait/anastasia_src.jpg`
  - Shipped as: `gfx/leaders/MLT/mltd_anastasia.dds`
  - Origin: DeviantArt, deviation `d9rfgge` (wixmp CDN link supplied by the mod author) - artist
    not yet recorded
  - Licence status: unverified - record artist + permission
- `portrait/herald_src.jpg`
  - Shipped as: `gfx/leaders/MLT/mltd_drowned_herald.dds`
  - Origin: <https://i.redd.it/293jfcd9b5z61.jpg> (Reddit-hosted; original artist not yet recorded)
  - Licence status: unverified - record artist + permission
- `portrait/mlulu_original.png`, `portrait/MLT_mlulu_small_original.png`
  - Shipped as: `gfx/leaders/MLT/mlulu.dds`,
    `gfx/interface/ideas/character_small_icons/MLT_mlulu.dds` (colour-graded)
  - Origin: Old World Blues assets (`gfx/leaders/MLT/mlulu.dds`,
    `character_small_icons/MLT_mlulu.dds`)
  - Licence status: OWB asset, redistributed only as a derivative inside an OWB-dependent submod
- (generated)
  - Shipped as: `gfx/leaders/MLT/mltd_mlulu_animated.dds`
  - Origin: The already-graded `mod_folder/gfx/leaders/MLT/mlulu.dds` with a procedural rain loop
    composited over it by `build_animated_portrait.py` (rain is original, drawn from a seed)
  - Licence status: OWB asset derivative, as above
- (generated)
  - Shipped as: `gfx/interface/goals/mltd_book.dds`
  - Origin: Old World Blues `gfx/interface/goals/unique/CHO/cho_scriptorium.dds`, recoloured by
    `build_focus_icons.py`
  - Licence status: OWB asset derivative, as above
- (generated)
  - Shipped as: `gfx/interface/counters/**/unit_mltd_*`, `gfx/texticons/unit_mltd_*`
  - Origin: Procedurally drawn by `build_unit_icons.py` (original work; NATO-box geometry measured
    from vanilla)
  - Licence status: original
- `workshop/owb_wordmark.png`
  - Shipped as: `mod_folder/thumbnail.gif`, `event_images/workshop/thumbnail.png` and
    `gfx/interface/logo_game_static.dds` (the "Old World Blues" wordmark on the marquee)
  - Origin: Matted by hand out of `thumbnail.png` of Steam Workshop item **3296248182**, *OWB -
    Fountain of Dreams* (the only submod thumbnail with light lettering on a dark panel, so the
    only one that mattes cleanly). Every OWB submod reuses this wordmark; it originates with Old
    World Blues itself, which in turn styles it after Bethesda/Obsidian's *Fallout: New Vegas* "Old
    World Blues" DLC logo.
  - Licence status: **unverified - two removes from a commercial game logo.** Reused here on the
    same footing as every other OWB submod thumbnail, but nobody in that chain has a licence on
    record
- (generated)
  - Shipped as: `gfx/interface/logo_game_static.dds`
  - Origin: The marquee from `build_workshop_thumbnail.py` re-cropped by `build_main_menu.py`;
    inherits `workshop/owb_wordmark.png`. Overrides OWB's own header logo by path.
  - Licence status: as `owb_wordmark.png`
- (generated)
  - Shipped as: `gfx/interface/mltd_rain_anim{1,2}.dds`, `gfx/interface/mltd_rain_{base,mask}.dds`
  - Origin: All four drawn procedurally by `build_main_menu.py`. The two animation sheets carry the
    streaks; the base and mask are our own 2560x1792 pair rather than OWB's
    `bg_snow_anim_background.dds` / `bg_snow_anim_mask.dds`, which are 2560x1440 and leave an empty
    band below 1080p (see CLAUDE.md > Why the rain textures are taller than the screen). Nothing of
    OWB's is copied.
  - Licence status: original
- (generated)
  - Shipped as: `mod_folder/thumbnail.gif` (**the asset that ships**) and the repo-side still
    `event_images/workshop/thumbnail.png`
  - Origin: Both composed by `build_workshop_thumbnail.py` from `grand_ritual_src.webp`
    (background), `workshop/owb_wordmark.png`, and the three shipped portraits `mlulu.dds` /
    `mltd_drowned_herald.dds` / `mltd_anastasia.dds`. The marquee, the neon, the panel, the road
    plate and all type are original procedural work.
  - Licence status: **inherits the worst status of its inputs - currently `unverified`.** This is
    the mod's most public image: it is the Workshop store art, not an in-game asset. Resolve
    `grand_ritual_src.webp`, `herald_src.jpg` and `owb_wordmark.png` before uploading
- (generated)
  - Shipped as:
    `gfx/interface/decisions/mltd_decision_cat_{spectral_cabal,loid_ekt_storm,wardens_propaganda}.dds`
  - Origin: Old World Blues `gfx/interface/decisions/decision_cat_spectral_cabal.dds`,
    `decision_cat_loid_ekt_storm.dds` and `decision_cat_wardens_propaganda.dds`, content moved down
    2 transparent rows (bottom 2 rows cropped) by `build_category_pictures.py` so they clear the
    category frame line
  - Licence status: OWB asset derivative, as above
- (generated)
  - Shipped as: `gfx/interface/decisions/mltd_cult_hood.dds`
  - Origin: Procedurally drawn by `build_decision_icons.py` (numpy + Pillow, no source image)
  - Licence status: original
- `agency/agency_src.jpg`
  - Shipped as: `gfx/interface/operatives/agencies/mltd_agency_logo_esoteric_order.dds` (redrawn as
    a gold-on-teal seal by `build_agency_logo.py`: skull and tentacles resampled, rings redrawn)
  - Origin:
    <https://i.etsystatic.com/9715836/r/il/6ef88e/1438113134/il_fullxfull.1438113134_qfdl.jpg>
    (Etsy listing image) - a stencil of **Marvel's HYDRA insignia**, chosen by the mod author for
    the *Hail M'lyeh* joke
  - Licence status: **unverified - Marvel (Disney) trademark and copyright.** The emblem is
    recognisably HYDRA's, so a public Workshop item carrying it is a takedown risk; a redraw (a
    mirelurk skull, a different tentacle count) would clear it
- (generated)
  - Shipped as: `gfx/interface/mltd_logo_animated.dds`
  - Origin: The same marquee as `logo_game_static.dds`, rendered by `build_main_menu.py` as a
    16-frame strip with the neon breathing; inherits `workshop/owb_wordmark.png`.
  - Licence status: as `owb_wordmark.png`
- (generated)
  - Shipped as: `gfx/leaders/MLT/mltd_drowned_herald_animated.dds`
  - Origin: The shipped `mltd_drowned_herald.dds` with a procedural backdrop throb composited over
    it by `build_animated_portrait.py` (the throb is original; the mask is measured, not painted).
  - Licence status: inherits `portrait/herald_src.jpg` - unverified
- (generated)
  - Shipped as:
    `gfx/interface/counters/division_templates_{large,small}/custom_template_25{6,7}.dds`
  - Origin: Sliced by `build_unit_icons.py` from frame 1 of the battalion sheets it draws itself.
  - Licence status: original
- (generated)
  - Shipped as:
    `gfx/interface/equipment/cosmetic/melee/mltd_melee_weaponry_tech_icon_1_cultist_knife.dds`,
    `mltd_melee_weaponry_tech_icon_2_conch_knife.dds`
  - Origin: Old World Blues
    `gfx/interface/equipment/cosmetic/melee/melee_weaponry_tech_icon_1_cultist_knife.dds` and
    `melee_weaponry_tech_icon_2_conch_knife.dds`, cut out of their baked-in glow, scaled down,
    moved up inside the same 130x60 frame and given a regenerated copy of that glow by
    `build_tech_icons.py` (read from the OWB folder at build time; colours untouched)
  - Licence status: OWB asset derivative, as above
- `tech_icons/trident_src.webp`
  - Shipped as:
    `gfx/interface/equipment/cosmetic/melee/mltd_melee_weaponry_tech_icon_3_trident.dds` (MLT's
    *Tridents* tech icon: turned, scaled to 130x60, lifted and given OWB's black outer glow by
    `build_tech_icons.py`)
  - Origin: the image of the Reddit post *Could Mohg's trident have been Godwyn's weapon?*
    (<https://preview.redd.it/could-mohgs-trident-have-been-godwyns-weapon-v0-9ansbzg74zec1.png?width=640&crop=smart&auto=webp&s=2e2d59a7acfadc9c8dc712582d52fc0aef3d378a>),
    supplied by the mod author; a transparent cut-out of the in-game render of **Mohgwyn's Sacred
    Spear** from *Elden Ring* (FromSoftware / Bandai Namco), as the game's wikis carry it. The
    Reddit poster is not the author
  - Licence status: **unverified - commercial game asset.** Recognisable to anyone who has played
    *Elden Ring*; at 130x60 in a tech tree it is a low-exposure placement, but a redraw (the
    procedural route of `build_unit_icons.py` / `build_decision_icons.py`) or an OWB-style kitbash
    would clear it
- `cthuluMINI.V1.1.stl` - **not in the repo** (100 MB); `build_unit_model.py --src`, by default
  `~/Downloads/cthuluMINI.V1.1.stl`
  - Shipped as: `gfx/models/mltd/star_spawn/mltd_star_spawn.mesh` and `mltd_star_spawn_{d,n,s}.dds`
    and the `.anim` clips beside them (the 3D unit model of the Star Spawn and the Deep Ones: the
    sculpt leaned 4.2 degrees onto both feet, decimated from 1,998,186 to 6,000 triangles and
    unwrapped, its surface detail baked into the normal map and the occlusion by
    `build_unit_model.py`. The sculpt carries no colour: the diffuse is painted procedurally)
  - Origin: A 3D-print miniature of Cthulhu, supplied by the mod author as a download. 99,909,384
    bytes, sha256 `b51c419a92c2d335c56d4802406cd820505ae804e89d039387e13f4ad45d483f`, binary STL
    whose header reads `MW 1.0 3131281 US`. **Designer, download page and licence not yet
    recorded**
  - Licence status: **unverified - the only source here with no origin at all: record the designer,
    the download page and the licence.** Print-miniature licences are commonly personal-use only
    and often forbid redistribution and derivatives; the shipped mesh and normal map are a
    derivative (the silhouette and the surface detail survive). An in-game asset only - no store
    art uses it

Preview PNGs (`preview_*.png`, `compare_*.png`, `*_preview.png`, `*/preview.png`,
`agency/mltd_agency_logo_strip.png`, `decision_icons/*.png`, `tech_icons/*.png`,
`unit_model/texture_*.png`, `workshop/thumbnail_{128,77}.png`) are build outputs, not sources.

**The Workshop title image is the highest-risk placement in this repo.** Everything else here is an
in-game asset seen only by people who already own the mod; `thumbnail.png` is the store front. It
is currently built from art whose licence is unverified. Two ways out, in order of preference:

1. Commission or find a licensed/permissive background painting and repoint `BG_SRC` in
   `build_workshop_thumbnail.py`; the rest of the image is already original work. The main-menu
   background has the same problem and the same one-line fix (`SRC` in `build_main_menu.py`) - it
   is seen by anyone who launches with the mod enabled, so it ranks just behind the thumbnail.
2. Fall back to the fully procedural composition explored during design (no third-party raster at
   all except the wordmark) - the working script for it is not kept in the repo, but the approach
   is recorded in README > Workshop art.
