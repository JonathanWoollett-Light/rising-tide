# CLAUDE.md

## Reference material

This is a submod of **Old World Blues** (OWB), installed at:

`C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196`

Use it as the reference for all script syntax, and as the source for any file this submod overrides. Vanilla HOI4 is at `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV`.

Read `<OWB>/doc/OWB_MODDING_README.txt` first - OWB's official submodders guide: the `dependencies` requirement, the six nation categories, advisor/chief/theorist suppression flags, decimation on state transfer, the AI war-creation system, reserved country-leader ID ranges. Same folder: `border_wars.txt`, `project_exodus.txt`, `read_me_adding_a_new_country.txt`, `mojave_territories_systems.txt`.

MLT specifics from OWB's `history/countries/MLT - Mirelurk Tribe.txt`: it is flagged `is_tribal_nation` and `is_oregon_nation`, and already sets `no_generic_chief`, `no_generic_high_command` and `dont_give_tribal_generic_{chiefs,high_command,theorists}` - generic advisors are suppressed, so any new advisor must be added explicitly. Its capital is state `358` (Crowlands, 2,558 pop at start); it also owns `451` (8,451). MLT + the four nations `mlt_kingdom_of_mlyeh` requires it to absorb (TRL, RBT, CCW, DIS) total ~75,000 population at game start. Its only creature sub-unit is `amphibious_beast_creature` on `amphibious_beast_equipment` (variants `_1`, `_2`, `_armor`, `_king`).

## Project

**OWB - Rising Tide** - a Hearts of Iron IV submod of *Old World Blues* focused on the Mirelurk Tribe, country tag `MLT`. OWB is declared as a dependency in `mod_folder/descriptor.mod`. Everything the game sees lives under `mod_folder/`; the repo root holds docs, tooling and source art that must not ship.

Current state: **first content drop, play-tested once** - the first run found summoned divisions spawning without equipment (fixed in round 3 by the hidden equipment techs); everything since round 3 is not yet re-tested. That now includes visible decision cooldowns, the two offering decisions, Feed the Spawning Pools as a continuous focus, the Star Spawn rebalance, capital victory points, both animated portraits, the quadrupled summon costs, doubled gifts, custom division-template counters, and the two OWB rewards that were taken away (the forced laws and Cultural Upheval). Everything hangs off OWB's final MLT focus `mlt_kingdom_of_mlyeh`. `mltd_gifts_from_the_deep` (15,15) sits directly below the tree's tail with **no prerequisite line** to the Kingdom - it gates on `has_completed_focus = mlt_kingdom_of_mlyeh` inside `available`. The five **Books of M'lyeh** (`mltd_first_book` .. `mltd_fifth_book`) fan out under Gifts at relative (-2,1) (-1,2) (0,1) (1,2) (2,1); Call of the Deep Ones (0,3), the Grand Ritual, the Deep Ones Walk and the Final Ritual continue straight down the centre column, chained by `prerequisite`. Progress through the column is gated by how many Books have been read (`mltd_books_read`: 1 / 3 / 5). Round 13 (the conflict sub-trees, the flavour events, the Book expeditions and the removal of the doctrine override) is not play-tested either.

| Beat | Focus (cost = days) | What it does |
| --- | --- | --- |
| 0 | `mlt_kingdom_of_mlyeh` (OWB, edited) | no longer applies OWB's `itz_civilizing` ("Cultural Upheval", -10 % PP / -20 % stability for 365 days); now also adds **victory points** to the new capital (province 1983 M'lyeh +15, province 7064 Mireport +5) and fires `mltd.1` (MLT) and `mltd.2` (world news, delivered to every other country); either option of `mltd.1` gives the (pre-recruited, role-less) character **The Drowned Herald** (`MLT_DROWNED_HERALD`) his general role via `add_corps_commander_role` (4 / 4-2-2-1, strong + enduring + swamp fox + animal friend - a notch below M'lulu) |
| 1 | `mltd_gifts_from_the_deep` (30) | adds dynamic modifier `mltd_gifts_from_the_deep`; opens the **Gifts from the Deep** decision category; `mltd_gifts_max = 1` |
| 1b | `mltd_first_book` .. `mltd_fifth_book` (30 each) | each requires **control** of a notable regional state - Arago (150, DIS capital), The Warren (235, TRL capital), Paisley Pit (231, MDT), Arroyo (337, ARR), The Maw (274, PMR) - and **starts an expedition**: a three-event chain (`mltd.101-103` Tide ... `mltd.501-503` Abyss) with choices (war support against stability, or which of two named advisors dies), whose last event reads the Book - it sets `mltd_<n>_book_found`, which is what unlocks that gift's decision (Tide / Shell / Current / Brood / Abyss, in that order), and adds 1 to `mltd_books_read`. The focus itself only previews that reward under *When the book is found:*. Icon `GFX_goal_mltd_book` (OWB's `cho_scriptorium.dds` recoloured dark violet by `build_focus_icons.py`, with its own `_shine`). |
| 2 | `mltd_call_of_the_deep_ones` (30) | needs >= 1 Book; its only effect is `country_event = mltd.7`, whose single option spawns the first locked 20-width **Deep Ones** division at the capital, gives 25 army XP and sets flag `mltd_deep_ones_summon_unlocked` (opens **Children of the Deep** and its summon decision) |
| 3 | `mltd_the_grand_ritual` (100) | needs >= 3 Books and national population >= 100,000 (AI also waits until it can spare the summons); **while selected** holds idea `mltd_the_grand_ritual` (-10 % stability / political power / division organisation, -5 % factory output, daily toll 0.1 %/state); on completion removes it, sets `mltd_gifts_max = 2`, fires `mltd.3` + news `mltd.4` |
| 4 | `mltd_the_deep_ones_walk` (30) | needs all 5 Books; its only effect is `country_event = mltd.8`, whose single option grants tech `warbike_unlock_tech` (= The Deep Ones, see Naming: the unit becomes designer-available), adds permanent idea `mltd_children_of_the_deep` (`special_forces_min = 80`), unlocks the Deep Ones template, spawns the first locked **Star Spawn** division and sets flag `mltd_star_spawn_summon_unlocked` (opens its summon decision) |
| 5 | `mltd_the_final_ritual` (100) | needs national population >= 200,000; while selected holds idea `mltd_the_final_ritual` (-20 % stability and division organisation, -15 % political power, -10 % factory output and war support, toll 0.25 %); on completion removes it, grants `mltd_star_spawn_tech`, unlocks the Star Spawn template, makes all five gifts permanent and hides both categories, fires `mltd.5` + news `mltd.6` |

Plus, independent of the tree: the **continuous focus** `mltd_continuous_spawning_pools` (*Feed the Spawning Pools*, -15 % creature equipment build cost while selected), two **offering** decisions that trade population for caps and for capital water (in the Children of the Deep category, open from the Kingdom onward), an MLT-only intelligence operation `mltd_op_indoctrinate_the_faithful` (La Resistance only), a colour-graded (darker, colder) M'lulu portrait + small icon overriding OWB's textures by path, and (via the `common/characters/MLT.txt` override) M'lulu's field-marshal traits gain `animal_friend_trait` + `naval_invader` while Coral Prophet Anastasia gains `animal_friend_trait` and a bespoke portrait (`GFX_Portrait_mltd_anastasia`). MLT also gains a spymaster advisor, *Old Castro* (`MLT_OLD_CASTRO`), whose trait gives +2 operative slots (La Resistance only).

**Round 13** (not yet play-tested) adds three more systems. **Eight conflict sub-trees** (36 focuses, `common/national_focus/mltd_conflicts_focus.txt`) sit on both sides of the trunk as detached shared-focus branches. In each one the tribe's intelligence agency, *The Esoteric Order of M'lyeh*, spies on, robs and destabilises one of OWB's big wars: the NCR and the Hoover Dam (`NCR`, `MOT`), Texas (`TBH`, `LNS`), the Washington Brotherhood (`WBH`), Caesar's Legion (`CES`), the Lost Hills Brotherhood (`BOS`), Tlaloc and his heirs (`TLA`, `MAX`, `MOC`, `ZAP`, `ARM`), Heaven's Guard's holy wars in Idaho (`HEA`), and the Utah road war between the White Legs and the Eighties (`WHT`, `EHT`). Every sub-tree has the same shape:
- a root that founds or upgrades the agency (`mltd_intel_foothold`);
- two or three middle focuses, gated on La Resistance infiltration tokens or network coverage, that pay intel, tokens, stolen equipment and political-power or stability hits on the target;
- a capstone keyed to the target's own OWB storyline: the Hoover outcome flags, `texas_formed`, WBH's mutant purge, Caesar's illness, Lost Hills-NCR tension, Tlaloc's draining databanks, Heaven's Guard's crusades, or the Eighties-White Legs war. Seven of the eight capstones can give a 180-day timed idea.

Without La Resistance every intel gate is empty and every intel reward becomes political power or a tech bonus, so each sub-tree can still be finished. Next to them, **ten Lovecraftian flavour events** (`mltd.9-18`) are drawn from a monthly pool once the Kingdom stands. Each fires at most once, never within 120 days of another, with effects no bigger than OWB's own `flavour.2`.

The five **Book focuses are now expeditions**: each only previews its Book and starts a three-event chain (`mltd.101-103` ... `mltd.501-503`) in which the player chooses war support against stability, or which of two named advisors dies, and whose last event actually reads the Book - see Book expeditions.

## Layout

| Path | Contents |
| --- | --- |
| `mod_folder/` | The mod as HOI4 sees it. **Only this directory ships**; everything else in the repo is docs, tooling and source art. |
| `mod_folder/descriptor.mod` | Mod metadata. **No `picture=` key** - deliberate, see the gotcha below. `remote_file_id="3798403425"` was written by the launcher on the first publish. No `path=`, no `replace_path`. |
| `mod_folder/interface/z_fallout_ui.gfx` | **OVERRIDE** of OWB's file: one line, `GFX_frontend_bg`'s `texturefile` repointed to `gfx/loadingscreens/mltd_main.dds`. tnkd does the same - but copy **OWB's current bytes**, not tnkd's, which are stale and lack `GFX_generic_text_bg_48_owb`. |
| `mod_folder/interface/frontendmainview.gui` | **OVERRIDE** of OWB's file: the overlay `iconType` OWB ships commented out, re-enabled and pointed at `GFX_frontend_bg_mltd_rain`. The only reason the menu rain moves, and the only file here other submods contest (ECR, Enclave Reborn Redux, Rustbelt, Monarchs all ship it). Deleting it costs the rain and nothing else. |
| `mod_folder/gfx/loadingscreens/mltd_main.dds`, `mod_folder/gfx/interface/logo_game_static.dds`, `mod_folder/gfx/interface/mltd_logo_animated.dds`, `mod_folder/gfx/interface/mltd_rain_{base,mask,anim1,anim2}.dds` | Main-menu background (1910x1440), header logo (443x303 static as a texture-path override of OWB's, plus the 16-frame 7088x303 uncompressed strip the frontend actually uses) and the rain (four 2560x1792 DXT5 textures). Built by `build_main_menu.py`; see Main menu below. ~32 MB, most of the mod's size. |
| `mod_folder/thumbnail.gif` | Animated Workshop preview - rain plus a neon breath, 350x350, 32 frames @ 40 ms, ~740 KB. Built by `build_workshop_thumbnail.py`. The **only** thumbnail that ships; the 512x512 still is built repo-side to `event_images/workshop/thumbnail.png`. |
| `<HOI4>/mod/rising_tide.mod` (not in this repo) | Launcher pointer: `descriptor.mod` plus one `path=` line. Machine-specific, so unversioned; regenerate it after any descriptor change. |
| `mod_folder/common/national_focus/Mirelurk Tribe (MLT) Focus.txt` | **OVERRIDE** of OWB's file: +9 lines straight after OWB's two `shared_focus = lurk_*` lines (`:20` a comment, `:21-28` one `shared_focus = mltd_<root>` per conflict sub-tree); +5 lines in `mlt_kingdom_of_mlyeh` (two victory-point grants, a spacer, the event and the news delivery); -1 OWB line (`itz_civilizing`); +10 focuses appended (Gifts, five Books, Call, Grand Ritual, Walk, Final Ritual - see Project). The Books' rewards only preview their Book and fire the expedition's first event. |
| `mod_folder/common/national_focus/mltd_conflicts_focus.txt` | **New file, not an override** (OWB ships nothing by this name, so OWB updates never touch it; it still needs load-after-OWB, because OWB `replace_path`s the folder). The eight conflict sub-trees as 36 top-level `shared_focus` blocks: NCR 5 (`mltd_ncr_*`), Texas 4 (`mltd_tex_*`), WBH 4, CES 5, BOS 5, Tlaloc 4 (`mltd_tla_*`), Heaven's Guard 4 (`mltd_hea_*`), the Utah road war 5 (`mltd_wht_*`). The override lists the roots; everything else comes in through prerequisites. LF, no BOM. See Conflict sub-trees. |
| `mod_folder/common/continuous_focus/generic.txt` | **OVERRIDE** of OWB's continuous-focus palette (the only palette; `generic_focus`, `default = yes`): one inserted focus, `mltd_continuous_spawning_pools`. |
| `mod_folder/common/characters/MLT.txt` | **OVERRIDE** of OWB's MLT characters: +2 traits on `MLT_MLULU`, +1 trait, two replaced portrait lines and attack/planning skill 1 -> 2 on `MLT_CORAL_PROPHET_ANASTASIA`, + role-less character `MLT_DROWNED_HERALD` (name + portraits only; `mltd.1` adds the general role). All 14 tokens OWB's history recruits must stay defined. Also `MLT_OLD_CASTRO`, the Esoteric Order's spymaster: a `cultural_advisor` with `mltd_keeper_of_the_order` (+2 operative slots), `visible` only with La Resistance and `available` once MLT has an agency, cost 150. |
| `mod_folder/common/country_leader/mltd_traits.txt` | `mltd_keeper_of_the_order` (`operative_slot = 2`), Old Castro's advisor trait. New file; OWB does not `replace_path` `common/country_leader`. |
| `mod_folder/events/nf_mlt.txt` | **OVERRIDE** of OWB's MLT event file: `nf_mlt.7` (the Black Hollows Night hatching) pays 300 political power instead of forcing `war_economy`, `children_and_mothers` and `closed_economy`. The only override that deletes OWB content (-38 lines / +6). |
| `mod_folder/history/countries/MLT - Mirelurk Tribe.txt` | **OVERRIDE** of OWB's MLT history: two inserted lines, `recruit_character = MLT_DROWNED_HERALD` and `recruit_character = MLT_OLD_CASTRO` (`recruit_character` is history-only - anywhere else the game logs an error at load). |
| `mod_folder/common/script_enums.txt` | **OVERRIDE** of OWB's script enums: our four equipment ids appended to `script_enum_equipment_bonus_type` (otherwise the game logs one "not in script enum" warning per id at load). |
| `mod_folder/common/technologies/mltd_technologies.txt` | Reward-tab techs `warbike_unlock_tech` (Deep Ones) -> `mltd_star_spawn_tech` (`enable_subunits` + `enable_equipments`), plus two hidden folder-less techs `mltd_deep_ones_equipment_tech` / `mltd_star_spawn_equipment_tech` that only `enable_equipments`, granted by script the first time a division is raised. |
| `mod_folder/common/units/mltd_units.txt` | Sub-units `mltd_deep_ones` (manpower 30, training 200, `need` 20) and `mltd_star_spawn` (manpower 50, training 300, `need` **10** - fewer, bigger monsters): both width 2.5, suppression 5, special forces, `active = no`, flat sub-unit stats only - combat stats come from their equipment. |
| `mod_folder/common/units/equipment/mltd_equipment.txt` | Archetypes `mltd_deep_ones_equipment` / `mltd_star_spawn_equipment` and variants `_1` (x1.3 / **x2.2** of `amphibious_beast_equipment_king`), modelled on `cre_amphibious_eq.txt`. |
| `mod_folder/common/decisions/mltd_decisions.txt` | 5 gift decisions + 5 gift missions in `mltd_gifts_from_the_deep_cat`, each `visible` once its Book's expedition has set `mltd_<n>_book_found`; 2 summon decisions + 2 offering decisions in `mltd_children_of_the_deep_cat`. |
| `mod_folder/common/decisions/categories/mltd_decision_categories.txt` | `mltd_gifts_from_the_deep_cat`, `mltd_children_of_the_deep_cat` (holds the summons *and* the offerings, so it opens at the Kingdom and never closes - each decision hides itself). |
| `mod_folder/common/dynamic_modifiers/mltd_dynamic_modifiers.txt` | `mltd_gifts_from_the_deep` (five variable-backed modifiers). |
| `mod_folder/common/scripted_effects/mltd_scripted_effects.txt` | `mltd_gift_<key>_on/_off`, `mltd_all_gifts_permanent`, `mltd_ensure_*_template`, `mltd_raise_*_here` (state scope), `mltd_spawn_*_division`, `mltd_update_national_population`, `mltd_take_population_everywhere`, `mltd_ritual_daily_toll`, and `mltd_intel_foothold` (the first effect of every conflict root: with La Resistance it founds the agency, or refunds OWB's 15-cap charge and then adds one upgrade; without the DLC it pays +50 PP). |
| `mod_folder/common/scripted_triggers/mltd_scripted_triggers.txt` | `mltd_flavour_can_fire` (`original_tag = MLT`, Kingdom complete, `has_capitulated = no`, no `mltd_flavour_cooldown`): the shared gate every flavour event's `trigger` calls. |
| `mod_folder/common/ideas/mltd_ideas.txt` | `continuous_mltd_spawning_pools` (in a `hidden_ideas` block, added and removed by the continuous focus), `mltd_the_grand_ritual`, `mltd_the_final_ritual` (temporary; debuffs + toll tooltip), `mltd_children_of_the_deep` (permanent; `special_forces_min = 80`). Plus nine timed ideas, all `original_tag = MLT`, `removal_cost = -1`, with reused OWB pictures. Seven are 180-day conflict capstone ideas: `mltd_tex_black_water`, `mltd_wbh_tide_wall`, `mltd_ces_the_drowned_bull`, `mltd_bos_red_tide`, `mltd_tla_dreams_of_wire`, `mltd_hea_pilgrims_of_the_steam` (+5 % political power, +3 % stability), `mltd_wht_rites_on_the_jetty` (+5 % morale, +3 % recruitable population). Two come from flavour events: `mltd_flavour_strange_harvest` (90 days) and `mltd_flavour_unnamed_colour` (120 days). |
| `mod_folder/common/on_actions/mltd_on_actions.txt` | `on_daily_MLT`: recompute `mltd_national_population`, then run `mltd_ritual_daily_toll` while a ritual idea is held. `on_monthly_MLT`: the flavour pool, `random_events = { 50 = 0  10 = mltd.9 ... 10 = mltd.18 }`. |
| `mod_folder/common/operations/mltd_operations.txt` | The intelligence operation (reuses OWB phases; no new phases/tokens). |
| `mod_folder/events/mltd_events.txt` | `add_namespace = mltd`. `mltd.1-8`: 1/3/5 are MLT country events and 2/4/6 world news events delivered via `every_other_country`, one option each; 7/8 are single-option events that carry the Call / Walk effects. `mltd.1`'s `immediate` also sets `mltd_flavour_cooldown` for 90 days. `mltd.9-18` are the Lovecraftian flavour events drawn by `on_monthly_MLT` (see Flavour events). `mltd.101-103`, `201-203`, `301-303`, `401-403` and `501-503` are the five Book expeditions (see Book expeditions). |
| `mod_folder/interface/mltd.gfx` | 3 event pictures, 2 tech icons, 2 equipment icons (`GFX_<equipment_id>_medium`), 2 unit-icon triplets, the book focus icon `GFX_goal_mltd_book` + `_shine`, the portraits `GFX_Portrait_mltd_anastasia` / `GFX_Portrait_mltd_drowned_herald`, and the `frameAnimatedSpriteType` `GFX_Portrait_mltd_mlulu_animated`. |
| `mod_folder/gfx/leaders/MLT/mltd_mlulu_animated.dds`, `mltd_drowned_herald_animated.dds` | The two animated portraits: M'lulu's rain (40 frames @ 12 fps, 6240x210, 5.2 MB) and the Herald's backdrop throb (24 frames @ 8 fps, 3744x210, 3.1 MB), both uncompressed A8R8G8B8 at 156 px per frame. Rebuilt by `build_animated_portrait.py` (`--subject` builds one). |
| `mod_folder/gfx/interface/counters/division_templates_{large,small}/custom_template_25{6,7}.dds` | Division-template counters for the Deep Ones (256) and Star Spawn (257) templates: 76x42 and 30x12, sliced from frame 1 of the battalion sheets by `build_unit_icons.py`. |
| `mod_folder/gfx/interface/goals/mltd_book.dds` | Book focus icon (92x90, uncompressed): OWB's `cho_scriptorium.dds` recoloured to a dark violet tome by `build_focus_icons.py` (needs OWB installed to rebuild). |
| `mod_folder/gfx/leaders/MLT/mltd_anastasia.dds`, `mltd_drowned_herald.dds` | Coral Prophet Anastasia's and the Drowned Herald's portraits (156x210 uncompressed, same header class as OWB's leader portraits), cropped from `event_images/portrait/{anastasia,herald}_src.jpg` by `build_leader_portraits.py` (per-subject `CROP` table; `--subject` builds one). |
| `mod_folder/gfx/event_pictures/mltd_event_*.dds` | 500x200 uncompressed A8R8G8B8. Rebuilt by `build_event_pictures.py` from `event_images/`. |
| `mod_folder/gfx/leaders/MLT/mlulu.dds`, `mod_folder/gfx/interface/ideas/character_small_icons/MLT_mlulu.dds` | Graded portrait (156x210 uncompressed) and small icon (65x67 DXT1) overriding OWB's textures by path - no `.gfx` change. Rebuilt by `build_portrait.py`. Since round 9 the portrait is no longer drawn in game (our characters override points M'lulu at the animated sprite, and nothing else in OWB references `GFX_Portrait_MLT_mlulu`): it is now the **build input** `build_animated_portrait.py` reads, so it must not be deleted. The small icon, by contrast, only started rendering in round 9, through the `small =` keys added to M'lulu. |
| `mod_folder/gfx/interface/counters/divisions_large/unit_mltd_*_icon.dds`, `.../divisions_small/onmap_unit_mltd_*_icon.dds`, `mod_folder/gfx/texticons/unit_mltd_*_icon_small.dds` | Original unit/division icons for `mltd_deep_ones` (fish-man) and `mltd_star_spawn` (Cthulhu bust): 152x42 / 60x12 / 60x12, two frames each (frame 1 shaded glyph - green, or white for the on-map sheet; frame 2 NATO counter box with a line symbol), uncompressed A8R8G8B8 like OWB's. Drawn procedurally by `build_unit_icons.py` (all shape parameters at its top); referenced by the `GFX_unit_mltd_*_icon_*` triplets in `mltd.gfx`. |
| `mod_folder/localisation/english/MLT/mltd_l_english.yml` | All English strings (single file; UTF-8 BOM, LF, 2-space indent). |
| `mod_folder/localisation/replace/mltd_replace_l_english.yml` | Key-for-key overrides of OWB strings - currently only `warbike_unlock_tech(_desc)`. The collision `text.log` reports is intentional. |
| `workshop_page/`, `build_workshop_page.py` | Screenshots for the Steam Workshop item's **Additional Previews** gallery - a different thing from `mod_folder/thumbnail.gif`, which is the single preview image. 1920x1080 JPEG under 900 KB (Steam caps an image at 1 MiB; a 1920x1080 PNG of these scenes is ~2.9 MB, so PNG is not usable at that size). Repo-only. |
| `event_images/workshop/` | `owb_wordmark.png` (the shared OWB marquee wordmark, matted out of *OWB - Fountain of Dreams*' thumbnail - the only submod thumbnail with light lettering on a dark panel, so the only one that mattes cleanly) and the 128/77 px thumbnail previews. |
| `event_images/`, `build_event_pictures.py`, `build_portrait.py`, `build_animated_portrait.py`, `build_unit_icons.py`, `build_focus_icons.py`, `build_leader_portraits.py`, `build_workshop_thumbnail.py` | Source rasters (event pictures; `portrait/` holds the decoded OWB originals, the icon photo mask, the Anastasia and Herald sources and previews; `unit_icons/` and `focus_icons/` hold previews/compare sheets) and the rebuild scripts. Repo root, never shipped. `event_images/SOURCES.md` records the origin/licence status of every image - it must be complete before any Workshop upload. |

Directories are created on demand - git does not track empty ones, so the scaffold lives in this table, not on disk.

## Overriding OWB

No `replace_path` is declared, so this submod merges additively.

- **Override** an OWB file by shipping the *same relative path and filename*. That replaces OWB's whole file (for textures: just the image, the `.gfx` sprite keeps pointing at the path).
- **Add** content with a new `mltd_`-prefixed filename in the same directory.
- The submod must load **after** Old World Blues. `dependencies={ "Old World Blues" }` in both `.mod` files is the supported mechanism (OWB's own `doc/OWB_MODDING_README.txt`: "After adding this your mod will load after OWB and won't be replaced by files we have or our replace_paths"); never remove it. In a hand-ordered playset, place this submod **below** Old World Blues - lower loads later. This is not cosmetic: OWB `replace_path`s `common/ideas`, `common/national_focus`, `common/characters`, `common/decisions`, `events` and `history/countries`, so anything we ship there is deleted outright if we load first.
- Never add `replace_path` - OWB declares 95 of them and ours would delete OWB's matching folder outright.

**Files we override, and the rule for editing them:** copy OWB's bytes (keep whatever BOM / line-ending state OWB's copy has - all six are CRLF; `history/countries/MLT - Mirelurk Tribe.txt` and `events/nf_mlt.txt` carry a BOM, the rest do not), make the edit, then diff. Three are insertion-only (the continuous-focus palette, the MLT history file and the script enums); the characters file also has Anastasia's four replaced lines and M'lulu's two, the focus file **deletes one** OWB line (`add_timed_idea = { idea = itz_civilizing days = 365 }`), and `events/nf_mlt.txt` **deletes 38** (the law block). Re-diff all six after **every** OWB update (Update process below).

- `common/national_focus/Mirelurk Tribe (MLT) Focus.txt` - the only way to add focuses to an existing tree (`mlt_nf`). Our changes: two `add_victory_points` lines, a spacer tooltip and the `country_event`/`news_event` lines at the end of `mlt_kingdom_of_mlyeh`'s `completion_reward`, and ten focus blocks (`mltd_gifts_from_the_deep`, the five Books, `mltd_call_of_the_deep_ones` ... `mltd_the_final_ritual`) before the final brace.
- `common/characters/MLT.txt` - our changes: `MLT_MLULU` `field_marshal` traits += `animal_friend_trait`, `naval_invader` (both `type = corps_commander` traits; OWB's own M'lulu already carries `swamp_fox` there and OWB's `RCK_roach_king` field marshal carries `animal_friend_trait`); `MLT_CORAL_PROPHET_ANASTASIA` `corps_commander` traits += `animal_friend_trait`, her `army.large` / `civilian.large` portraits `GFX_Portrait_Tribal_Generic_3` -> `GFX_Portrait_mltd_anastasia`, and her `attack_skill` / `planning_skill` raised 1 -> 2 (four replaced lines in total); M'lulu's two `large = GFX_Portrait_MLT_mlulu` lines swapped for the animated sprite with `small = GFX_idea_MLT_mlulu` added under each (six lines where there were four); plus a new **role-less** character block `MLT_DROWNED_HERALD` (name + portraits only) appended at the end, and after it `MLT_OLD_CASTRO`, a `cultural_advisor` (OWB has no `political_advisor` slot: its civilian advisors use `cultural_advisor` / `economic_advisor`, and 10 of its 18 operative-slot advisors are cultural). OWB's pattern for late-appearing generals: define the character without a role, recruit him in history (invisible until he has a role), then `add_corps_commander_role = { character = ... traits = {...} skill = ... }` at runtime - 29 OWB event files do exactly this. `recruit_character` outside a history file logs `effectimplementation.cpp: recruit_character should only happen in game/history files` at load. OWB `replace_path`s `common/characters`, so load-after-OWB is mandatory for this file to exist at all.
- `history/countries/MLT - Mirelurk Tribe.txt` - two inserted lines after OWB's last `recruit_character`: `recruit_character = MLT_DROWNED_HERALD` and `recruit_character = MLT_OLD_CASTRO`. (OWB `replace_path`s `history/countries`, so this override only exists when loaded after OWB.)
- `common/continuous_focus/generic.txt` - OWB's only continuous-focus palette, and there is no way to add to a palette from a separate file: a second palette would have to out-score OWB's for MLT and would then *replace* it, costing MLT all 20 of OWB's continuous focuses. So we override the file and insert one focus after `OWB_continuous_mutant`. Same risk profile as the doctrine override - any other submod that ships this file wins or loses it whole.
- `events/nf_mlt.txt` - the laws MLT used to be forced into are not in the Kingdom focus and not in our `mltd.1`: they are in OWB's `nf_mlt.7`, the Black Hollows Night hatching, fired two focus steps upstream by `ritual_of_black_hollows_night`. Its option added `war_economy`, `children_and_mothers` and `closed_economy` at -5 % stability each (or +15 % stability if all three were already held). Our copy keeps the egg payload and pays `add_political_power = 300` instead; no stability is applied either way. Nothing in OWB tests for those three ideas outside that option, and nothing tests `has_idea = itz_civilizing` at all.
- `common/script_enums.txt` - OWB's copy plus our four equipment ids inside `script_enum_equipment_bonus_type`. The enum is documentation-only, but every unlisted equipment id logs an `equipment_database.cpp` warning at load. tnkd ships a stale copy of this file - if both submods are loaded, whichever loads later wins and the other's ids warn again.
- `gfx/leaders/MLT/mlulu.dds`, `gfx/interface/ideas/character_small_icons/MLT_mlulu.dds` - texture-only overrides; header class must match OWB's (uncompressed 32-bit / DXT1 with OWB's alpha). If OWB changes the portrait or the icon template, re-run `build_portrait.py --derive-icon-mask` and re-fit `ICON_FIT`.

OWB's other MLT **script and localisation** files (exact override targets; reproduce spaces, parentheses and the ` - ` separator byte-for-byte):

- `common/countries/MLT - Mirelurk Tribe.txt`
- `common/characters/MLT.txt` (**already overridden** - see above)
- `common/decisions/_mlt_decisions.txt`, `common/decisions/categories/_MLT_categories.txt`
- `common/units/names/00_MLT_names.txt`, `common/units/names_ships/MLT_ship_names.txt`
- `events/nf_mlt.txt` (declares `add_namespace = nf_mlt`; ids 1-7 are taken - we use our own `mltd` namespace instead)
- `history/countries/MLT - Mirelurk Tribe.txt`, `history/units/MLT_2275.txt`, `history/units/MLT_2275_naval.txt`
- `localisation/english/MLT/{characters,events,focus,traits}_MLT_l_english.yml`
- Art: `gfx/leaders/MLT/{mlulu,tinyshell}.dds`, `gfx/interface/ideas/character_small_icons/MLT_{mlulu,tinyshell}.dds`, `gfx/interface/goals/mlt_*.dds` (5), `gfx/interface/ideologies/unique/MLT/MLT_elites.dds`, `gfx/interface/focusview/filter/mlt_eggs.dds`. Their sprites are declared in *shared* OWB `interface/*.gfx` files - declare new sprites in `interface/mltd.gfx`, never by overriding those.

Things OWB already provides that this submod must NOT recreate: the `MLT` tag (`common/country_tags/00_countries.txt`), its flags (`gfx/flags/{,medium/,small/}{MLT,MLT_TRL,MLT_cosmetic_tag}.tga` - 9 files; all three sizes must be replaced together), and its map colour (`common/countries/colors.txt`, which overrides the colour in the country file).

Files to leave alone even though they contain MLT content, because they are shared with other countries:

- `common/national_focus/Shared Oregon Coastals Focus.txt` (also used by DIS)
- `common/ideas/generic_oregon_coastal_ideas.txt.txt` (note the real doubled extension; holds DIS `lake_*` and shared `lurk_*` ideas)
- `common/country_leader/00_traits.txt`, `common/countries/colors.txt`, `common/countries/cosmetic.txt`, `common/bookmarks/old_world_blues.txt`
- `common/units/unit_modifiers/unit_modifiers.txt`, `common/synchronized_dynamic_tokens/tokens.txt`, `interface/countrytechtreeview.gui` - whole-file lists that other submods also override.

## How the mechanics are wired

**Gifts from the Deep** (tnkd's dynamic-modifier-backed-variable pattern). One dynamic modifier reads five gift variables (`mltd_gift_{tide,shell,current,brood,abyss}_var`; +20 % army attack / defence / organisation, +30 % recruitable population, +20 % stability) plus `weekly_manpower = mltd_gift_manpower_var`, which is not a gift: focus 1 initialises it to 0, the Grand Ritual sets it to 50, the Final Ritual doubles it (`multiply_variable`), each followed by `force_update_dynamic_modifier`; `mltd_all_gifts_permanent` never touches it. The 50 / x2 are repeated as literals in `mltd_gift_manpower_grand_tt`, `mltd_gift_manpower_final_tt` and `mltd_gifts_from_the_deep_desc` - change all four together. Each gift is a *decision* (25 PP + 500 manpower) that calls `mltd_gift_<key>_on` (sets the var, `mltd_gifts_active += 1`, `force_update_dynamic_modifier`) and activates a 30-day *mission* whose `timeout_effect` calls `mltd_gift_<key>_off`. The slot gate is `mltd_gifts_active < mltd_gifts_max` (1 after focus 1, 2 after the Grand Ritual), and each gift decision is hidden until its Book is read (`has_country_flag = mltd_<n>_book_found`, set by the last event of that Book's expedition), so the category opens empty after focus 1. `mltd_all_gifts_permanent` (Final Ritual) uses `remove_mission` (which does **not** fire `timeout_effect`), pins every var, zeroes the counter and sets flag `mltd_gifts_permanent`, which hides the category and every gift decision.
*The numbers live in three script places and two loc places:* the `set_temp_variable` preview and the `set_variable` in each `mltd_gift_<key>_on`, the pins in `mltd_all_gifts_permanent`, the `set_temp_variable ... tooltip =` line on each Book focus, and the literal list in `mltd_all_gifts_permanent_tt`. The ten `_on_tt` / `_off_tt` keys read the variables and need no edit.
*Adding a gift touches seven places:* the dynamic-modifier line, the decision + mission pair, the `_on`/`_off` effects, the `if has_active_mission -> remove_mission` line and the `set_variable` in `mltd_all_gifts_permanent`, six loc keys (`<id>`, `<id>_desc`, `<id>_mission`, `<id>_mission_desc`, `mltd_gift_<key>_on_tt`, `_off_tt`), and the value list in `mltd_all_gifts_permanent_tt`.

**Deep Ones / Star Spawn** (OWB's Paladin pattern, with their own equipment). Sub-units are `active = no` and carry only flat sub-unit stats (org, HP, morale, terrain); soft/hard attack, defence, breakthrough, armour, hardness and speed are the **equipment's** flat numbers, exactly like `amphibious_beast_creature`, so the units can be compared stat-for-stat with OWB's mirelurk variants. Templates are 20 width: `"Deep Ones"` = 8 x `mltd_deep_ones` (`need` 20, 26 IC a piece), `"Star Spawn"` = 8 x `mltd_star_spawn` (`need` **10**, 150 IC a piece - deliberately few and huge; a battalion's combat stats come from the equipment and are independent of `need`, which only scales production cost, attrition piece loss and reinforcement volume) (2.5 each, grid rows 0-2 only - OWB's designer is 5 x 3). Each template carries `template_counter` (256 Deep Ones, 257 Star Spawn), which the engine resolves to the sprites `GFX_div_templ_<N>_large` / `_small` declared in `interface/mltd.gfx` - there is no division-template key that names a sprite, so declaring those names *is* the mechanism. Vanilla owns 0-43, the anniversary DLC 44-64 and OWB 65-255, so 256/257 are the first free indices; before this they were both `0`, which drew vanilla's dagger glyph. `mltd_ensure_*_template` first grants the hidden equipment tech (`set_technology = { popup = no ... }` guarded by `NOT has_tech`) - **`create_unit` only equips a division with equipment the country has unlocked**, which is why the first play-test spawned empty divisions - then creates the locked template once (`NOT has_template_containing_unit`, `is_locked = yes`, no `force_allow_recruiting`); `mltd_raise_*_here` (state scope) stockpiles 160 / 80 of the equipment variant (= battalions x `need`, a reinforcement pool) and `create_unit`s the division in that state with `owner = ROOT`; `mltd_spawn_*_division` = ensure + raise at the capital (used by events `mltd.7` / `mltd.8`; the Call and Walk focuses themselves only fire those events, so their effects land when the single option is clicked - the AI clicks immediately). The summon decisions and the Children category are gated on the flags `mltd_deep_ones_summon_unlocked` / `mltd_star_spawn_summon_unlocked` set by those options, not on focus completion. The summon decisions gate on `mltd_controlled_population` (> 15,999 / 31,999, twice what each takes) - a second daily variable summed with the toll's own `is_controlled_by = ROOT` and `> 500` filter, so the gate measures exactly the pool the charge will spend from - and the toll falls on **every** owned+controlled state over 500 people at once, in proportion to what each holds: `mltd_take_population_everywhere` sums the pool into `mltd_toll_pool_k` with `state_population_k`, then charges each state `population / pool_k * mltd_toll_target_k` - dividing first and working in thousands, because the naive order overflows the variable ceiling on every state (see Gotchas). A state with a tenth of the nation pays a tenth, so the big states carry most of it and none is emptied. The division then rises at the **capital** (`mltd_spawn_*_division`), not in a paying state. They hide once the unit becomes trainable. Gating on the plain owned total would let an occupied MLT clear the gate and then spread the whole toll across the handful of states it still holds, or - controlling nothing - pay nothing and get the division free. Because the gate is only refreshed daily, the effect also floors every charge at whatever leaves the state 500 people, so no summoning can empty one. Focus 4/5 grant the reward tech (`enable_subunits`, so the unit appears in the designer; its `enable_equipments` is redundant with the hidden tech) and `set_division_template_lock = { ... is_locked = no }`, guarded by `has_template_containing_unit`. Consequence: the equipment is producible from the first summon (reinforcements for the summoned divisions); the *unit* only from *The Deep Ones Walk* / *The Final Ritual*. Template names are **string-matched** in the ensure effects, the raise effects *and* the unlock lines - change them together.
Both units are `special_forces = yes`. OWB's cap floor is 20 battalions, which the spawned divisions consume; the permanent idea `mltd_children_of_the_deep` (added at focus 4) sets `special_forces_min = 80` so the unlocked templates can actually be trained. Script-spawned units bypass the cap.

**The offerings** (in `mltd_children_of_the_deep_cat` alongside the two summons; the category opens once `mlt_kingdom_of_mlyeh` completes and never closes, because each of its four decisions hides itself). Two decisions trade population for something the tribe cannot otherwise get. `mltd_offering_of_the_drowned` (25 PP, 60-day cooldown) takes 1,000 people from a random owned+controlled state over 3,000 and pays 100 **bottle caps** through OWB's `add_caps` (`caps_scripted_effects.txt:33`): set `caps_to_add` as a temp variable immediately before it, never touch `caps_number_display` directly - `add_caps` writes its own tooltip, plays the sound, runs the bankruptcy check, clamps to [-1000, 25000], refreshes the top bar through `caps_topbar_update_var`, and pays 1.25x political power instead when the caps game rule is off. `mltd_offering_of_the_tides` (35 PP, 180-day cooldown) takes 1,500 and adds a permanent +4 `water` to `capital_scope` (OWB's own MLT tree does the same at `Mirelurk Tribe (MLT) Focus.txt:184`; state 358 starts at 32). Both draw population exactly like the summons.

**Decision cooldowns.** Nothing in this mod uses `days_re_enable` any more: a decision on that cooldown gives the player no countdown and (on the evidence available) may vanish from the category outright, which is why the Deep Ones summon looked like it "only shows sometimes". Instead each repeatable decision sets a timed country flag in a `hidden_effect` (`set_country_flag = { flag = X value = 1 days = N }`) and gates on it in `available` through a `custom_trigger_tooltip` whose loc prints the remaining days with the vanilla formatter `[?<flag>:days_left|0]` (vanilla `nsb_decisions_l_english.yml:197`, `SEA_decisions_l_english.yml:452`). The decision therefore always stays listed, greyed, with a reason. Cooldowns: Deep Ones summon 90, Star Spawn summon 120, Drowned Hoard 60, Drown the Fields 180 - each literal appears in the flag, in the `_cooldown_after_tt` and in the `_cooldown_tt`; change them together. The Deep Ones summon is still hidden for good once `mltd_star_spawn_summon_unlocked` is set (event `mltd.8`), which is deliberate - the unit is trainable by then - and `mltd.8` now says so.

**Feed the Spawning Pools** is a **continuous focus**, the same shape as OWB's equipment-production one: a `focus` block in the palette with `available`, `idea =`, `daily_cost = 1`, `supports_ai_strategy` and `available_if_capitulated = yes`. The engine adds the named idea while the focus is selected and removes it when the player switches, so no script touches it and there is no counter, no ladder and nothing to reset. The discount lives in the idea's `equipment_bonus`, keyed by **archetype** so it reaches every variant - a dynamic modifier cannot carry `build_cost_ic` (OWB tried: `kha_dynamic_modifier.txt:10` is commented out), and the equipment *category* `infantry` is unusable because every creature archetype is `type = infantry` and it would discount rifles too. -15 % matches what a tribal MLT can already get on rifles from `OWB_continuous_Raider_production`; change it in `mltd_ideas.txt` alone. Like every OWB continuous-focus idea it lives in a `hidden_ideas` block; OWB gives those ideas no localisation of their own (the focus's name is what shows), but ours has some in case it ever renders.

**The animated portraits.** Both are `frameAnimatedSpriteType` frame strips, the only mechanism any animated portrait in OWB (63 sprites) or tnkd uses - the `animation = {}` overlay block is for focus shines and the frontend snow, and no portrait anywhere uses it. `build_animated_portrait.py` holds a `SUBJECTS` table (the `build_leader_portraits.py` house pattern) and an `EFFECTS` dispatch. *M'lulu* gets three parallax rain layers over the graded `mlulu.dds`: the loop closes because each layer is drawn once into a periodic canvas and then translated by a fixed per-frame offset whose total over the strip is an exact multiple of the canvas in both axes, so the rain frame count must be a multiple of 40 (the canvas is 4 px wider than the portrait at 4x supersampling, which makes the horizontal period a round number). A layer of speed `k` crosses the portrait `k` times per loop, so `k` and `animation_rate_fps` are the only real speed dials. *The Drowned Herald* gets a throb on his turquoise backdrop: amplitude `0.5 - 0.5*cos(2*pi*f/frames)`, which is 0 at both ends with zero slope, so any frame count closes. Its mask is the crux - hue does **not** separate backdrop from figure (the robes sit in the same 150-195 band and score 0.6-0.9 on a hue+saturation test), but *teal excess against red*, `min(G,B) - R`, does: 28 on the backdrop against 2 on the figure. The score is restricted to the blob connected to the frame edge and blurred; measured leak onto the figure is 0.027 against 0.92 coverage of the backdrop. `noOfFrames` in `mltd.gfx` and the strip width must agree - 156 x frames. M'lulu also gains `small = GFX_idea_MLT_mlulu` under both portrait keys, which stops the engine deriving a small portrait from a 6240-px-wide strip (`character_manager.cpp:319` complains about exactly that for OWB's RCK generics) and finally puts the graded small icon this mod already ships to use.

**The rituals** are 100-day focuses whose idea exists only while the focus is in progress: `select_effect = { hidden_effect = { set_variable ...  add_ideas ... } }` (0.001 / 0.0025) and `completion_reward` starts with `hidden_effect = { remove_ideas = ... }`. The visible tooltip is `custom_effect_tooltip = mltd_ritual_duration_tt` ("For the duration of the ritual:") followed by one `set_temp_variable = { mltd_tt = <value> tooltip = mltd_<modifier>_tt }` line per idea modifier (loc `$MODIFIER_X$: $RIGHT|+=%1$` - tnkd's in-game-tested idiom, `Think Tank (TNK) Focus.txt:1958`), the toll literal, then a blank line (`custom_effect_tooltip = mltd_newline_tt`, whose value is `" \n"` - OWB's `spacer_tt` idiom) before the rest of the rewards. Those values duplicate `mltd_ideas.txt` - change both. Both are `cancelable = no` and `available_if_capitulated = yes` (the idea has `removal_cost = -1`; a cancelled or paused ritual would leave the toll running) and `cancel_if_invalid = no` + `continue_if_invalid = yes` (the toll can push the population back under the gate mid-ritual). Gates: `available = { custom_trigger_tooltip = { check_variable = { mltd_national_population > 99999 / 199999 } } }` (i.e. at least 100,000 / 200,000; the five-tag kingdom is ~75k at start, so both gates require real expansion); `mltd_national_population` is recomputed every day by `mltd_update_national_population` (`every_owned_state = { add_to_variable = { PREV.mltd_national_population = state_population } }`, OWB `exodus_effects.txt:385` precedent) and reads 0 until the first daily tick.
**The toll.** `on_daily_MLT` calls `mltd_ritual_daily_toll` while either ritual idea is held: for every owned state with > 500 population it removes `state_population * mltd_ritual_toll_factor` (at least 1). Over a 100-day ritual that compounds to ~9.5 % (Grand) / ~22 % (Final) of every state. Tunables: the two factors in the `select_effect`s; the > 500 skip and the `max = -1` floor in the effect; the same numbers are repeated **as literals** in `mltd_grand_ritual_toll_modifier_tt` and `mltd_final_ritual_toll_modifier_tt` (literals, because a focus preview renders before `set_variable` runs). Change all of them together.

**Events.** `mltd.1/3/5/7/8` are `country_event`s for MLT (`fire_only_once`, log line kept). `mltd.2/4/6` are plain `news_event`s (`is_triggered_only` only - no `major`, no `fire_only_once`) that the focus delivers with `hidden_effect = { every_other_country = { news_event = { id = X days = 2 } } }`, so MLT itself never receives them; each has one untriggered option `.a` written from the outside world's perspective. Options carry no effects - the focus already applied them. **Event text colours:** OWB's event paper is pale and its event fonts render `§Y`/`§H` as yellow and `§G` as light green (unreadable there); OWB defines no dark purple, so event `.t`/`.d` strings use only `§o` (Zaffre dark blue, 20 20 180) for names and `§c` (wine, 158 56 82) for emphasis, and option strings carry no codes at all (they render white on a dark-brown button). Focus/decision/idea tooltips sit on dark backgrounds and keep `§Y`/`§G`/`§R`. `mltd.9-18` (flavour) and `mltd.101-503` (Book expeditions) follow the same colour rules.

**Operation.** `common/operations/mltd_operations.txt`: `allowed`/`visible` on `original_tag = MLT`, no `operation_target` (any country MLT has a network in - an operation can never target yourself), 60 days, moves 1,500 manpower FROM -> ROOT. The whole agency system needs the La Resistance DLC; the file loads silently without it. Any *script* that references the agency must be wrapped in `has_dlc = "La Resistance"` (OWB `cartel_on_actions.txt:4-7`).

**Reward-tab techs.** A tree root in `fallout_focus_tree_folder` only renders if `interface/countrytechtreeview.gui` has a gridbox named `<root_id>_tree`; OWB ships an orphaned `warbike_unlock_tech_tree` (gui ~line 3893) and nothing else usable. So the Deep Ones tech id **is `warbike_unlock_tech`** (its "Warbikes" strings are overridden in `localisation/replace/`), and `mltd_star_spawn_tech` chains from it via `path` to share the gridbox. Never add a second reward-tab root; overriding the 9,300-line gui would clash with OWB Tech Expansion / UTCM, which both ship it. Positions are `x = 4, y = 24` (Deep Ones) and `x = 4, y = 28` (Star Spawn) - OWB `tech_hidden.txt`'s `@Row_unit3` / `@Col_11` and `@Col_13`, i.e. the "Units" band row holding `sentinel_unit_tech` (4,4), `mininuke_unlock_tech` (4,8), `artillery_ammo_unlock_tech` (4,12), `gehenna_molech_tech` (4,16) and `faerie_unlock_tech` (4,20), continuing its 4-column (280 px) step because `enable_equipments` techs render in the 183 px `techtree_fallout_focus_tree_folder_item` window. In this gui `x` is the vertical row (150 + 70·x px) and `y` the horizontal column. Equipment icons follow OWB's `GFX_<equipment_id>_medium` + `alwaystransparent = yes` convention (OWB declares none for its own creature equipment - those inherit the unlocking tech's icon).

**Portrait.** `build_portrait.py` is a deterministic Pillow/numpy colour grade of OWB's painting (soft background mask -> abyssal teal gradient, cold split-toning, S-curve, vignette, rim, grain); the small icon is the graded portrait warped back into OWB's shared photo-card template (`ICON_FIT`, `icon_photo_mask.png`). It is **not** repainted art - a human or an inpainting tool would still need to paint real water/abyss texture and rim light and clean the silhouette halo.

**Conflict sub-trees** (OWB's Oregon-Coastal pattern: detached `shared_focus` branches pulled into `mlt_nf`). `common/national_focus/mltd_conflicts_focus.txt` holds 36 top-level `shared_focus = { }` blocks in eight sub-trees. The override lists only the roots, as eight `shared_focus = <root>` lines at `Mirelurk Tribe (MLT) Focus.txt:21-28` (a comment at `:20`, straight after OWB's own `lurk_` pair at `:18-19`). This is how OWB itself adds the Oregon Coastal branches to MLT and DIS, and it keeps the per-update re-diff at nine lines instead of ~900 appended ones. A listed root pulls in every shared focus that reaches it through prerequisites **on other shared focuses**, and nothing else; all 431 of OWB's shared focuses that have a prerequisite are reached that way. Four rules keep it working:
- Roots take **absolute** `x`/`y` in `mlt_nf`'s grid, as 30 of OWB's 32 listed roots do (`lurk_aquatic_construction`'s (5,3) is (5,3) in both MLT's and DIS's trees). No root has a `relative_position_id` into `mlt_nf`: none of OWB's 464 or vanilla's 335 shared focuses does that, so it is untested.
- Roots have **no prerequisite**. They open through `available = { has_completed_focus = mlt_kingdom_of_mlyeh country_exists = <target> }`, like OWB's own detached roots (`TEU Joint Focus.txt:5-29`, `TTM Join Focus.txt:3-34`). That draws no line from the Kingdom across the tree, and the roots show greyed until it completes.
- Every other focus has a `prerequisite` on a focus **of its own sub-tree** and is positioned relative to its own root. A focus whose only prerequisite is a national focus is never pulled in (Gotchas).
- Two separate `prerequisite` blocks mean AND; one block listing two focuses is OR, as in the Kingdom. Most capstones use AND; the Utah road war's uses one OR block, and Heaven's Guard's hangs off its Schism alone.

The listing file sorts before the defining one, just as OWB's "Mirelurk..." sorts before "Shared Oregon...", and that is fine.

*Slots* (5x3 boxes; a box is 165 px against a 96 px column, so siblings sit 2 columns apart, OWB's usual spacing):

| Slot | Sub-tree | Root | Box (x, y) | Shape, relative to the root |
| --- | --- | --- | --- | --- |
| a | NCR | (2,13) | 0-4, 13-15 | children (-2,1) (0,1) (2,1); capstone (0,2) under the centre child only |
| b | Texas | (8,13) | 7-9, 13-15 | children (-1,1) (1,1); capstone (0,2) under both |
| c | WBH | (22,13) | 21-23, 13-15 | as Texas |
| d | CES | (28,13) | 26-30, 13-15 | children (-2,1) (2,1); (-2,2) under the left child; capstone (0,2) under both |
| e | BOS | (2,17) | 1-3, 17-19 | children (-1,1) (1,1); (-1,2) under the left child; capstone (1,2) under both |
| f | Heaven's Guard | (8,17) | 7-9, 17-19 | children (-1,1) (1,1); capstone (0,2) under the left child only |
| g | Tlaloc | (22,17) | 21-23, 17-19 | as Texas |
| h | Utah road war | (28,17) | 26-30, 17-19 | children (-2,1) (0,1) (2,1); capstone (0,2) under the left or right child (one OR block) |

The trunk (Kingdom, its three children, Gifts, the Books and the ritual column) stays inside x 13-17. The sub-trees keep at least two empty columns from it and leave row 16 clear on both sides. The tree grows from x 0-28 to 0-30 (31 x 23 cells, ~3,100 x 3,040 px); the focus view scrolls and sizes itself to the tree, so no gui change is needed. Every focus is at x >= 0 (negative x is untested) and below row 12, clear of the default continuous-focus palette at (50, 1000) px, roughly columns 0-8, rows 7-10 (calculated, not seen in game). A grid resolve of the whole tree gave 0 overlapping cells.

*Shared keys.* Costs are 30-45 days (OWB sets `FOCUS_POINT_DAYS = 1`, `common/defines/01_defines.lua:468`). All 36 focuses have `cancel_if_invalid = no` + `continue_if_invalid = yes`, because network coverage decays, operations use up tokens and targets die while a focus runs. All have `ai_will_do = { factor = 3 }` and reuse OWB focus icons (each has its `_shine`). Seven of the eight capstones grant a 180-day timed idea: NCR's grants none, WBH's only while WBH exists, BOS's only on its war branch.

*The agency.* MLT starts with no intelligence agency (OWB's history creates none), so every root calls `mltd_intel_foothold` first (`mltd_scripted_effects.txt:359`).
- With La Resistance and no agency yet: `create_intelligence_agency = { name = mltd_agency_name icon = "GFX_intelligence_agency_logo_generic_21" }`, the same call as Black Canyon's (`Black Canyon (BLC) Focus.txt:391-394`).
- With La Resistance and an agency: one upgrade through OWB's `add_random_agency_upgrade` (`00_scripted_effects.txt:520`, fed `random_agency_upgrade_amount = 1`), with `caps_to_add = 15` + `add_caps` paid *first* to refund the upgrade's 15-cap price, so the balance never dips below zero mid-effect (Gotchas). Both are skipped at `agency_upgrade_number > 29`, OWB's own ceiling (`:540`). Both branches run in `hidden_effect` behind `mltd_intel_foothold_create_tt` / `_upgrade_tt`.
- Without the DLC: +50 PP.

Eight roots therefore give one agency and up to seven upgrades. The helper adds no operative; only `mltd_ces_the_drowned_frumentarius` does (`create_operative_leader`, same shape as `Caesars Legion (CES) Focus.txt:8101-8116`).

*The DLC idiom* (OWB Lost Hills, `Lost Hills (BOS) Focus.txt:9641-9651`).
- In `available`, every intel test sits in `if = { limit = { has_dlc = "La Resistance" [country_exists = <target>] } ... }` with **no `else`**. Without the DLC, or once the target is gone, the gate is empty and the focus can be taken freely.
- The test is always an OR of an infiltration token and a coverage threshold: `has_operation_token = { tag = X token = token_civilian }` (or `token_army`), or `network_national_coverage = { target = X value > 0.1 ... 0.3 }` on the 0-1 scale.
- Tokens come from OWB's own `operation_infiltrate_civilian` / `operation_infiltrate_armed_forces_army` (awarded at `00_operations.txt:162` / `:600`), or from an earlier focus through `add_operation_token` (Lost Hills precedent `:1830-1845`). Each sub-tree's civilian-gated middle focus hands out the `token_army` its army-gated sibling accepts. The Utah road war's two middle focuses target different tags (WHT, EHT), so its WHT `token_army` only opens OWB's own operations.
- In `completion_reward`, `add_intel`, `add_operation_token`, `steal_random_tech_bonus` and `create_operative_leader` sit in `if = { limit = { has_dlc = "La Resistance" country_exists = X } ... } else = { <PP or add_tech_bonus> }`. Equipment theft, PP / stability / war-support hits on the target, caps, population and ideas need no agency and sit outside that `if`.

*Theft without producer.* Every theft is a pair of `add_equipment_to_stockpile` calls:
- The victim's scope gets a negative amount with **no `producer`**, which removes that equipment from every maker in its stockpile (`effects_documentation.md:1262-1263`).
- ROOT then gains the same amount with `producer = <victim>` - OWB's `operation_steal_enemy_supplies` idiom (`operations_fallout.txt:45-63`).

A `producer = <victim>` on the removal would take nothing from stock someone else built. Each pair is guarded by `<victim> = { has_equipment = { X > N } }` (which counts every maker, matching the removal) at or above the amount taken, and most fall back to caps or PP when nothing qualifies.

*Numbers in two places.* Where OWB's tooltip for an effect would read a variable the focus preview cannot see, or would print every theft twice, the effect is hidden and a literal tooltip stands in:
- Lost Hills tension +10: `mltd_bos_tension_rises_tt` (OWB's own `bos_change_tension` tooltip reads `BOS.BOS_tension_to_add`).
- The Legion's population 1,000 / 500 / 500: `mltd_ces_chained_faithful_tt`, `_pens_full_tt`, `_nipton_tt`.
- Tlaloc's 64 databanks: `mltd_tla_drain_databanks_tt`.
- The Iron Bones thefts 400 / 150 / 100: `mltd_tla_iron_bones_theft_tt`.

Change the script and the loc together. The tooltips' coverage percentages (15 / 20 / 25 / 30 %) likewise repeat the `value >` thresholds.

*Per sub-tree.* In the table, "LaR" marks a condition or reward that applies only with La Resistance (without the DLC the gate is free), "else" is the no-DLC substitute, "civ/army N" is `add_intel`, "cov" is `network_national_coverage`, and "foothold" is `mltd_intel_foothold`.

| Focus (cost) | Gate, besides prerequisites | Payoff |
| --- | --- | --- |
| **NCR** - `NCR` (+ `MOT`); root (2,13) | | |
| `mltd_ncr_a_mole_in_shady_sands` (30) | Kingdom; NCR exists | foothold; LaR civ 10 / army 5, else +25 PP |
| `mltd_ncr_drowned_delegates` (35) | LaR: `token_civilian` or cov > 0.2 | +40 PP; NCR -35 PP, -3 % stability (-2 % more under `ncr_crisis` or global `ncr_emergency`); LaR `token_army` + civ 10, else infantry-weapons tech bonus 50 % |
| `mltd_ncr_sleepers_on_the_long_15` (35) | LaR: `token_army` or cov > 0.15 | 15 army XP; MOT (else NCR) -3 % war support; LaR army 10 on NCR and MOT, else +25 PP |
| `mltd_ncr_salt_on_the_caravan_roads` (35) | LaR: `token_army` or cov > 0.25 | steals 400 (or 200) infantry equipment and 100 support; +50 caps |
| `mltd_ncr_the_turbines_sing` (42), after Sleepers | Hoover contested: any first-battle outcome flag, CES has `ces_hoover_dam_battle` / `ces_attack_ncr`, NCR at war with CES, CES gone, or after 2279.06.01 | LaR steals an industry tech bonus from NCR (`fallout_industry_folder`), else industry tech bonus 50 %; Legion victory: 300 NCR infantry equipment (else 15 XP); Wall held: 15 XP; NCR at war with CES: NCR -3 % war support |
| **Texas** - `TBH`, `LNS`; root (8,13) | | |
| `mltd_tex_all_waters_are_one` (30) | Kingdom; TBH or LNS exists | foothold; LaR civ/army 10 on each, else +25 PP |
| `mltd_tex_the_silent_partner` (35) | LaR: `token_civilian` on either, or cov > 0.2 on either | LaR `token_army` + civ 15 on each, else +25 PP; +40 caps; each -2 % stability, -25 PP |
| `mltd_tex_wreckers_on_the_trinity` (35) | LaR: `token_army` on either, or cov > 0.25 on either | steals 400 infantry equipment from TBH, else LNS (victim -2 % war support), else +30 PP; 15 army XP |
| `mltd_tex_black_water_rising` (45), after both | `texas_formed`, TBH or LNS gone, or after 2280.1.1 | +3 permanent `energy` in the capital; `mltd_tex_black_water`; each -3 % stability and war support; LaR civ/army 20 on each, else +25 PP |
| **Washington Brotherhood** - `WBH`; root (22,13) | | |
| `mltd_wbh_eyes_in_the_sound` (35) | Kingdom; WBH exists | foothold; LaR civ 10 / army 15, else +25 PP |
| `mltd_wbh_salt_in_the_citadel` "Heresy in the Citadel" (35) | LaR: `token_civilian`, cov > 0.2, or WBH gone | WBH -40 PP, -3 % stability; LaR civ 15 + `token_army`, else +25 PP |
| `mltd_wbh_the_drowned_knights` (42) | LaR: `token_army`, cov > 0.25, or WBH gone | steals 300 infantry equipment (WBH > 600) and 30 power armour (> 60); 15 army XP |
| `mltd_wbh_the_tide_wall` "The Tide-Wall of the Warren" (45), after both | WBH has `WBH_eradicate_the_mutants`, is at war with MLT or gone, or after 2280.1.1; **and** MLT owns and controls The Warren (235) | instant bunkers in 235 (level 2 in province 2158, level 1 in 2159-2161); WBH alive: its claim on 235 removed, WBH -3 % war support, `mltd_wbh_tide_wall`; WBH gone: 15 XP |
| **Caesar's Legion** - `CES`; root (28,13) | | |
| `mltd_ces_what_the_river_carries` (35) | Kingdom; CES exists | foothold; LaR civ/army 10, else +25 PP |
| `mltd_ces_the_drowned_frumentarius` (42) | LaR: `token_civilian` or cov > 0.1 | LaR operative *Silanus the Drowned* (`operative_frumentarius`, skill 2, nationalities MLT and CES) + `token_army` + civ 15, else +50 PP; CES -3 % stability |
| `mltd_ces_the_chained_are_given_to_the_tide` (35) | none | +1,000 capital population, +3 % stability; +500 if CES has `ces_slaves` or `ces_reservation_slaves`; +500 under global `nipton_massacred_flag` |
| `mltd_ces_salt_in_the_armouries` "A Crate for Every Cross" (35), after the Frumentarius | LaR: `token_army` or cov > 0.15 | steals 400 infantry equipment (CES > 799, else +50 caps) and 100 support (> 199) |
| `mltd_ces_the_sea_against_mars` (45), after Frumentarius + Chained | none | `mltd_ces_the_drowned_bull`; then one of: CES gone +50 PP / Caesar no longer leader or `CES_civil_war`: 20 army XP, CES -3 % stability / `CES_stress` (sick): +75 caps, CES -3 % war support / hale: +50 PP; any `cultofmars*` idea: CES -2 % war support more |
| **Lost Hills Brotherhood** - `BOS` (+ `NCR`); root (2,17) | | |
| `mltd_bos_the_drowned_paladin` (35) | Kingdom; BOS exists | foothold; LaR civ/army 10, else +25 PP; 10 army XP |
| `mltd_bos_the_paladin_returns` (35) | LaR: `token_civilian` or cov > 0.15 | LaR `token_army` + civ 15, else +35 PP; BOS -35 PP |
| `mltd_bos_the_tide_takes_the_armoury` (35) | LaR: `token_army` or cov > 0.2 | steals 300 of the best of `energy_equipment_2` / `_1` / infantry that BOS holds > 400 of (else +50 caps), and 40 power armour (> 150); tiers as OWB `operations_bos.txt:307-404` |
| `mltd_bos_the_codex_unsealed` (40), after Paladin Returns | LaR: `token_civilian` or cov > 0.25 | LaR steals an engineering/industry tech bonus from BOS, else electronics 75 %; BOS -2 % stability |
| `mltd_bos_blood_in_the_water` (45), after Paladin Returns + Armoury | none | BOS at war with NCR: both -3 % war support, `mltd_bos_red_tide`; else if BOS has `bos_tension_dynamic_modifier`: +10 tension in BOS and NCR through OWB's `bos_change_tension` (`BOS_scripted_effects.txt:296`), BOS -3 % stability more under `bos_ncr_accepted_deal_for_maxson`, +25 PP; else +50 PP, BOS -3 % stability |
| **Tlaloc and his successors** - `TLA`; heirs `MAX` `MOC` `ZAP`; `ARM`; root (22,17) | | |
| `mltd_tla_the_iron_god_dreams` (30) | Kingdom; any of the five exists, `tlaloc_died`, or MLT controls 769 (Tlaloc's Lair) | foothold; tooltip prints `TLA.current_databanks`; LaR civ/army 10 on each living tag (army only on ARM), or electronics 50 % if none lives; else electronics 50 % |
| `mltd_tla_the_three_voices` (35) | LaR: `token_civilian` or cov > 0.2 on any living tag; waived once none lives | -3 % stability and -25 PP on TLA, else on each heir, else on ARM; LaR civ 15 + `token_army` on the same tags, else +50 PP |
| `mltd_tla_picking_the_iron_bones` (35) | LaR: `token_army` or cov > 0.3 on any living tag; waived once none lives | steals 400 infantry from TLA (> 399), or once he is gone 150 from each heir (> 149), plus 100 support from ARM (> 99), all behind one tooltip; 10 army XP; +50 caps |
| `mltd_tla_the_drowned_god_sleeps` (45), after both | none | TLA alive and still draining above 100: -64 `current_databanks` (Gotchas), else TLA -3 % stability; TLA gone: each heir and ARM -2 % stability; LaR steals an engineering/industry tech bonus from the first living of TLA / MAX / MOC / ZAP / ARM (electronics 75 % if none lives), else electronics 75 %; `mltd_tla_dreams_of_wire` |
| **Heaven's Guard** - `HEA`; root (8,17) | | |
| `mltd_hea_whispers_in_the_steam` (30) | Kingdom; HEA exists | foothold; LaR civ 10 / army 5, else +25 PP |
| `mltd_hea_a_second_schism` (35) | LaR: `token_civilian` or cov > 0.2 | +40 PP; HEA -35 PP, -3 % stability (-2 % war support more once HEA has `hea_war_in_heaven`); LaR `token_army` + civ 10, else electronics tech bonus 50 % |
| `mltd_hea_steam_for_the_deep` (35) | LaR: `token_army` or cov > 0.25 | steals 300 infantry equipment (HEA > 299, else +25 PP); LaR steals an industry tech bonus from HEA (`fallout_industry_folder`), else industry 50 % |
| `mltd_hea_the_crusade_turns_south` (42), after the Schism | HEA has `hea_war_in_heaven` or `hea_attack_utah`, is at war with WHT / EHT / NCN, is gone, or after 2280.1.1 | HEA at war in Utah: 20 army XP + 60 caps, else +50 PP; `mltd_hea_pilgrims_of_the_steam` |
| **The Utah road war** - `WHT`, `EHT`; root (28,17) | | |
| `mltd_wht_the_lake_god_answers` (30) | Kingdom; WHT or EHT exists | foothold; LaR civ 10 on WHT and army 10 on EHT, else +25 PP |
| `mltd_wht_the_drowned_shamans` (35) | LaR: `token_civilian` or cov > 0.2 on WHT | +40 PP; WHT -3 % stability; WHT has `wht_god_lake` or `wht_god_old`: +2 % stability and war support; LaR `token_army` + civ 10 on WHT, else infantry-weapons tech bonus 50 % |
| `mltd_wht_guns_for_both_sides` (30) | WHT and EHT both exist | sells 200 of MLT's infantry equipment, 100 to each side, for 100 caps (40 caps without the guns); WHT at war with EHT: 15 army XP |
| `mltd_wht_sand_in_the_engines` (35) | LaR: `token_civilian` or cov > 0.15 on EHT | EHT -3 % war support; steals 300 infantry equipment (EHT > 299, else +25 PP); LaR army 10 on EHT, else +20 PP |
| `mltd_wht_rites_on_the_spiral_jetty` (42), after the Shamans or the Engines | WHT at war with EHT or has `wht_betray_eighties`, EHT has `EHT_steal_WHT_legs`, either gone, or after 2280.1.1 | `mltd_wht_rites_on_the_jetty`; WHT has `wht_god_lake` / `wht_god_old`: +50 PP and WHT -2 % stability, else +30 PP |

**Flavour events** (`mltd.9-18`; a monthly pool, not MTTH).

*The pool.* `on_monthly_MLT` (`mltd_on_actions.txt:24-38`) rolls `random_events = { 50 = 0  10 = mltd.9 ... 10 = mltd.18 }` once a month. The `0` entry is the no-event sink (vanilla `00_on_actions.txt:374`, `17000 = 0`), so each roll has a 50-in-150 chance of nothing and 10-in-150 for each event. Like `on_daily_MLT`, it rolls only while the tag is literally `MLT`.

*The gate.* Each event is `is_triggered_only` + `fire_only_once` and has `trigger = { mltd_flavour_can_fire = yes ... }` (`mltd_scripted_triggers.txt:7-12`: `original_tag = MLT`, Kingdom complete, `has_capitulated = no`, no `mltd_flavour_cooldown`). Its `immediate` sets `mltd_flavour_cooldown` for 120 days inside `hidden_effect`. `mltd.1` sets the same flag for 90 days (`mltd_events.txt:8`), so no flavour event lands on top of the Kingdom beats. Four events add a gate of their own: `mltd.11` and `mltd.16` need `mltd_deep_ones_summon_unlocked` (set by `mltd.7`, the Call); `mltd.14` needs `mltd_books_read > 0`; `mltd.18` needs `capital_scope = { is_fully_controlled_by = ROOT }`.

*Pacing.* From a 20,000-run simulation, medians counted from when the 90-day guard lapses, assuming a roll that picks an already-fired or blocked event fires nothing (unverified): first event after ~1 month, fifth ~25 months, tenth ~77 months, and never two closer than ~5 months (the cooldown plus the wait for the next roll). A sink of 200 pushes the tenth to ~117 months. The tunables are the sink, the ten weights and the cooldown. The cooldown is a literal in ten `immediate` blocks, plus `mltd.1`'s 90, and is repeated in the trigger-file and on_actions comments.

*Size.* Effects stay at or below OWB's own `flavour.2` (`events/flavour_events.txt:39`): political power 10-40, stability and war support 0.01-0.03, caps 10-20 through `add_caps`, country manpower +20 / -50, +500 capital population (`add_state_population`, OWB `00_scripted_effects.txt:509`), and two timed ideas (`mltd_flavour_strange_harvest` 90 days, `mltd_flavour_unnamed_colour` 120 days). The one caps cost (`mltd.9` option c, -10) is gated by `trigger = { set_temp_variable = { caps_diff = -10 } caps_cost_trigger = yes }` (OWB `nf_bis.txt:721-723`). The safer option carries `ai_chance` base 2, the rest base 1.

*Presentation.* Pictures are reused OWB `GFX_event_*` sprites, so nothing new goes into `event_images/SOURCES.md`; `mltd.8`'s `GFX_event_mirelurk_red_death_shipwrecker` is deliberately not reused. `.d` text uses only `§o` / `§c` and option text no colour codes, as for `mltd.1-8`. Lovecraft is named only from stories published before 1930; later stories (Innsmouth, The Whisperer in Darkness) and modern games (The Sinking City, Dredge, Bloodborne) are only alluded to, under original names.

*Why not MTTH* (OWB's house idiom): non-triggered events are checked for every country every 20 days (`EVENT_PROCESS_OFFSET`, vanilla `00_defines.lua:301`) across ~424 OWB tags, and their timing cannot be paced. OWB's own `flavour.2` (Pacific trade, MTTH 24 months) can probably already fire for MLT and counts against the same budget.

**Book expeditions** (round 13). A Book focus no longer reads its Book. Its `completion_reward` only previews the reward - `mltd_<n>_book_expedition_tt`, then *When the book is found:* (`mltd_when_book_found_tt`), the gift unlock, the modifier preview and `mltd_book_found_read_tt` - and fires the expedition's first event two days later. Each expedition is three `country_event`s (`is_triggered_only` + `fire_only_once`), chained by `hidden_effect = { country_event = { id = ... days = 7 random_days = 7 } }` in every option behind `mltd_expedition_continues_tt`, so a Book arrives 2-4 weeks after its focus: Tide `mltd.101-103` (Arago), Shell `201-203` (The Warren), Current `301-303` (Paisley Pit), Brood `401-403` (Arroyo), Abyss `501-503` (The Maw).
- *Choices.* War support against stability (101, 501); army XP against stability (102, 201); political power against stability (301); force against 50 caps (401, the caps option gated by `caps_cost_trigger`); +500 capital population against stability (402). In three chains **one of two named advisors dies**: Asenath or Obed (`MLT_TERROR` / `MLT_TIDE_HUNTER`, 202), She Who Knows of Ways or M'lulu's Knowledge (`MLT_KNOWS` / `MLT_MUTANTS`, 302), the Aspect of the Killclaw or of the King (`MLT_KILLCLAW` / `MLT_KING`, 502). Those options run `retire_character` (vanilla `effects_documentation.md:6436`), each gated by `has_character`, and a third option appears only when neither advisor is left, so the event always has a valid option. Sizes follow the flavour events: 0.02-0.03 stability or war support, 10-30 PP or army XP, 250-500 manpower.
- *The Book.* The third event of each chain sets `mltd_<n>_book_found` and adds 1 to `mltd_books_read` inside a `hidden_effect`, then repeats the unlock and preview lines the focus showed. The five gift decisions are `visible` on that flag (they used to test `has_completed_focus`), and the centre column's 1 / 3 / 5 gates count the variable, so both open when an expedition ends rather than when its focus completes.
- *Text.* The same event rules as `mltd.1-8`: `.d` text uses only `§o` / `§c`, options no codes. Advisor names in option text are OWB's own display names (`characters_MLT_l_english.yml`); OWB already named three of them after *The Shadow over Innsmouth* (Asenath, Obed, Robert Olmstead). Pictures are reused OWB sprites plus `GFX_mltd_event_final_ritual` for the Abyss.

## Encoding

These rules are measured from the files on disk, not assumed.

| File type | BOM | Line endings | Indent |
| --- | --- | --- | --- |
| `descriptor.mod`, `*.mod` | **No** (0 of the 55 descriptor + launcher `.mod` files belonging to the 27 installed mods) | LF (same 55) | Tab |
| `localisation/**/*.yml` | **Yes, required** (`EF BB BF`) | LF or CRLF | 2 spaces |
| `*.txt` script - new files | No (house style; 1,749 of OWB's 6,721 `.txt` do carry one and load fine) | LF | Tab |
| `*.txt` script - the six OWB overrides | No, except `history/countries/MLT - Mirelurk Tribe.txt` and `events/nf_mlt.txt`, which keep OWB's BOM (matches OWB either way) | **CRLF** (matches OWB; `.gitattributes` `* -text` keeps it) | Tab |
| `*.gfx` | No (0 of 163 OWB `interface/*.gfx`, 0 of 145 vanilla; still 0 scanned recursively) | Either | Tab |

A localisation `.yml` without the BOM is **silently ignored** - no error, the raw key strings just show in-game. First line must be exactly `l_english:` with no leading whitespace; entries are `  key:0 "Value"`.

Tooling traps, both verified in this environment:

- The editor/Write tool emits UTF-8 **without** a BOM. After writing any `.yml`, prepend one:
  `python -c "p=r'<file>'; d=open(p,'rb').read(); open(p,'wb').write(d if d[:3]==b'\xef\xbb\xbf' else b'\xef\xbb\xbf'+d)"`
- PowerShell 5.1 bare `Set-Content` writes **Windows-1252**, turning `§` into a single invalid byte `A7`. That is HOI4's colour-code prefix. Use `Set-Content -Encoding utf8`, `Out-File`, or the Write tool - never bare `Set-Content`. Conversely `>` and `Out-File` **add** a BOM, so never generate `.mod` files with them.
- Pillow (12.x) writes an OWB-identical uncompressed DDS with `img.convert("RGBA").save("x.dds")` - **no** `pixel_format` kwarg (`'RGBA'`/`'A8R8G8B8'` raise and truncate the file to 0 bytes). `DXT1/3/5` strings also work; `build_portrait.py` patches the DXT1 header dwords to OWB's values.

## Naming conventions

Use the submod prefix `mltd_` / `MLTD_` for anything new, and keep `mlt_` / `MLT_` for anything that must interoperate with OWB's existing MLT content (the `mlt_nf` tree id, `MLT_*` character tokens, the `nf_mlt` event namespace, the `mlt_eggs` variable).

| Thing | Pattern | Example |
| --- | --- | --- |
| New file | `mltd_<kind>.txt` | `common/ideas/mltd_ideas.txt` |
| Loc | one file, `localisation/english/MLT/mltd_l_english.yml`; OWB-key overrides in `localisation/replace/mltd_replace_l_english.yml` | - |
| Focus id | `mltd_<name>` | `mltd_the_grand_ritual` |
| Event | `mltd.<n>` (`add_namespace = mltd`; 1-18 taken, plus 101-103 ... 501-503 for the Book expeditions: `<book number>01-03`) | `mltd.19` |
| Conflict sub-tree focus | `mltd_<target tag, lower case>_<name>` (`mltd_wht_*` covers both Utah tags) | `mltd_hea_a_second_schism` |
| Decision / mission | `mltd_<name>` / `mltd_<name>_mission` | `mltd_gift_of_the_tide_mission` |
| Decision category | `mltd_<name>_cat` | `mltd_children_of_the_deep_cat` |
| Scripted effect | `mltd_<verb_phrase>`; state-scope effects end in `_here` | `mltd_raise_deep_ones_here` |
| Variable / flag | `mltd_<name>_var` (modifier inputs), `mltd_<name>` (counters, flags) | `mltd_gift_tide_var`, `mltd_gifts_permanent` |
| Idea / dynamic modifier | `mltd_<name>` | `mltd_gifts_from_the_deep` |
| Sub-unit | `mltd_<name>` | `mltd_deep_ones` |
| Equipment | `mltd_<name>_equipment` (archetype), `mltd_<name>_equipment_<n>` (variant) | `mltd_star_spawn_equipment_1` |
| Tech | `mltd_<name>_tech` - **exception:** the Deep Ones tech is `warbike_unlock_tech` (see above) | `mltd_star_spawn_tech` |
| Tech / equipment icon sprite | `GFX_<tech_or_equipment_id>_medium` + `alwaystransparent = yes` | `GFX_mltd_deep_ones_equipment_1_medium` |
| Unit icon sprites | `GFX_unit_<subunit>_icon_medium` / `_medium_white` / `_small` | `GFX_unit_mltd_deep_ones_icon_small` |
| Event picture sprite | `GFX_mltd_event_<name>` -> `gfx/event_pictures/mltd_event_<name>.dds` | `GFX_mltd_event_kingdom` |
| Operation | `mltd_op_<name>` | `mltd_op_indoctrinate_the_faithful` |
| Character | `MLT_<NAME>` | `MLT_TIDEWARDEN` |
| Advisor token | `MLT_<name>_<slot>` | `MLT_tidewarden_high_command` |
| Focus icon sprite (new art) | `GFX_goal_mltd_<name>` (+ `_shine`) | `GFX_goal_mltd_deep_currents` |
| Idea sprite (new art) | `GFX_idea_mltd_<name>` | `GFX_idea_mltd_spawning_grounds` |
| Portrait sprite | `GFX_Portrait_MLT_<name>` | `GFX_Portrait_MLT_tidewarden` |
| Loc key | `<id>` and `<id>_desc` (equipment variants also `_short`); tooltips `<thing>_tt` | `mltd_deep_currents_desc` |

OWB's own casing is inconsistent and must be matched exactly when extending it: portraits and character small icons use uppercase `MLT_`, focus goal icons use lowercase `mlt_`. Focus, idea, tech and equipment icons are reused OWB sprites; the new art is the three event pictures, the graded portrait and the two procedurally drawn unit-icon sets.

## Gotchas

- Every `GFX_goal_*` sprite used as a focus `icon` should have a matching `GFX_goal_*_shine`: OWB does this for every one of its focus icons, as does vanilla. Purely decorative `GFX_goal_*` sprites ship with no shine. Without it the focus just renders unhighlighted - no error appears in `error.log`.
- A new focus tree in a *new* file must out-score OWB's, which is `factor = 0` with `modifier = { add = 10 tag = MLT }`. We override the existing filename instead, which avoids the problem entirely.
- `ritual_of_black_hollows_night` has **no** `mlt_` prefix; `mlt_kingdom_of_mlyeh`'s prerequisite block lists two focuses in one block (OR).
- Overriding `common/characters/MLT.txt` requires copying the whole file: `history/countries/MLT - Mirelurk Tribe.txt` recruits 14 characters by exact token, and any missing one is a hard error at game start.
- `add_dynamic_modifier` **stacks**; guard with `NOT = { has_dynamic_modifier = { ... } }` (done in focus 1 and in `mltd_all_gifts_permanent`).
- `activate_mission` cannot re-activate an active mission and `remove_mission` skips `timeout_effect` - the gift decisions gate on `NOT has_active_mission` for exactly this reason.
- `select_effect` runs every time a focus is (re)selected and is **not** shown in the focus tooltip; keep its contents idempotent (`set_variable`, `add_ideas`) and describe them in `completion_reward` with `custom_effect_tooltip` + `set_temp_variable ... tooltip =` modifier lines.
- A focus gated only by `available = { has_completed_focus = X }` (no `prerequisite`) draws no connecting line and shows greyed until X completes - that is how `mltd_gifts_from_the_deep` hangs below `mlt_kingdom_of_mlyeh` without a line.
- Books 1-2 require *direct control* of Arago / The Warren. OWB's Kingdom gate accepts cores held by MLT's sphere (puppets, allies, faction members), so a player who puppeted DIS or TRL must still take those states - by design. Books 3-5 sit in MDT / ARR / PMR land that no OWB `ai_strategy` pushes MLT toward, so **AI MLT usually stops at the Grand Ritual** (3 Books) unless it conquers on its own.
- The Book focuses no longer touch `mltd_books_read`: the last event of each expedition adds the Book (`mltd.103/203/303/403/503`), 2-4 weeks after the focus. The centre column's 1 / 3 / 5 gates (`check_variable = { mltd_books_read > 0 / 2 / 4 }`) and the gift decisions (`has_country_flag = mltd_<n>_book_found`) therefore open when an expedition ends, not when its focus completes. `mltd_book_read_tt` is gone.
- `create_unit ... start_equipment_factor = 1.0` gives a division only equipment the country has **unlocked** (a tech with `enable_equipments`); stockpiled-but-locked equipment is not used. Unlock first (hidden tech), then spawn.
- Decision previews render *before* the effect runs: tooltips that show a number use `set_temp_variable = { mltd_gift_value_temp = X }` immediately before `custom_effect_tooltip`, never a non-temp variable set later in the same block.
- State-scope `add_manpower` (and OWB's `add_state_population`) changes **population**; country-scope `add_manpower` changes the recruitable pool. `weekly_manpower` is a weekly pool change, `monthly_population` a growth %; neither kills people daily - hence the `on_daily_MLT` hook.
- Summon gates are national, at twice the cost (16,000 and 32,000 against 8,000 and 16,000 taken). They used to be single-state thresholds, which the ritual tolls made unreachable: The Grand Ritual is a hard prerequisite of the Walk, so its 100-day toll (~9.5 % of every state) always runs before the Star Spawn summon exists, and the Final Ritual can take ~22 % more: The Warren (235) goes 28,000 -> 25,333 -> 19,724 and Arroyo (337) 25,337 -> 22,927 -> 17,850 without a single summon. spreading the toll removes that failure mode entirely, because no single state has to be large enough. The kingdom is 75,232 people across 12 states, so an 8,000 summon costs every state about 10.6 % of its people. Change the cost, the gate and the ai guard together.
- `on_daily_<TAG>` fires only while the tag is literally `MLT`; the toll, the population variable and the gifts pause if MLT changes tag (cosmetic tags are fine).
- `is_buildable = no` on an equipment **archetype** does not stop its variants being produced once a tech `enable_equipments` them (vanilla `infantry_equipment` works the same way) - so Deep Ones / Star Spawn equipment is producible from the first summon.
- OWB's per-unit mirelurk spirits (`modifier_army_sub_unit_amphibious_beast_creature_*`) do not reach `mltd_deep_ones` / `mltd_star_spawn`; adding them would need the whole-file `unit_modifiers.txt`. Category-keyed buffs do reach them - they are in `category_creatures`, `category_mutant_creatures` and `category_standard_creatures` - which is why we no longer override the doctrine file (next gotcha).
- **Never key doctrine or perk buffs to our sub-units by name.** The units already collect OWB's buffs through their categories: every Outsider Warfare tech buffs `category_mutant_creatures`, which all three amphibious units are in, so a block keyed by the sub-unit's name stacks on top of the same stat. Until 2026-09 this mod overrode `tech_fallout_land_doctrine.txt` with 16 such insertions. They doubled 8 stats across 7 techs (Outsider Warfare org +6 where OWB gives +3), changed OWB's own mirelurk for every nation, and put `max_strength = 5` into Adapted Armour (`we_are_enduring_doctrine`), which in OWB carries no health at all. Vanilla `stats_l_english.yml:218-221` gives `max_strength` no `STAT_*_MOD_VALUE` format key, so the tooltip renders any value as a percentage and `5` shows as "+500%" behind OWB's heart icon, although Paradox's own tooltips for the same script read it as flat HP (`infantry.txt:2828` -> `aat_ideas_l_english.yml:73`, "HP: +5"). The perk trees have the same trap. `creature_perk_tech_*` (`category_standard_creatures`) and `special_forces_perk_tech_*` (`category_special_forces`) in `fallout_perks_doctrine.txt` grant identical buffs with no XOR, so a unit in both categories collects every perk twice. Our units therefore follow the mirelurk and sit in `category_standard_creatures` only, not `category_special_forces` (they keep `special_forces = yes`, which only drives the special-forces cap). No OWB doctrine needs a new category for them: Asymmetric Warfare's Wasteland Knowledge branch reaches them through `category_creatures` and Outsider-Inspired Warfare through `category_mutant_creatures`. Adding a `category_standard_creatures` block to Outsider Warfare would re-create the stack for them and for every nation's mirelurks, deathclaws and ghouls, all of which are also in `category_mutant_creatures`. Known parity gaps, deliberately left alone, which are gaps rather than stacks: OWB's name-keyed mirelurk buffs (`mixed_army_doctrine` armour 0.15, `tech_creatures.txt` `amphibious_beast_upgrade_tech_*`, the `terrain_*_tech_6` morale lines, `lurk_sharpened_conch_knives` / `lurk_hardened_shell_shields`) never reach our units.
- `descriptor.mod` and the launcher `.mod` must be kept in sync by hand; the launcher rewrites its own copy from `descriptor.mod` on rescan, so edits made only there are lost. That includes `picture=`.
- There is **no `picture=` key** in either `.mod` file and **no `thumbnail.png` at the mod root**, on purpose: that is exactly how *The Fire Rises* (3350890356) is shaped, and it is the only installed mod with a working animated Workshop preview. The first publish used `picture="thumbnail.png"` and the item took the still. Pointing the key at a `.gif` is untried and no installed mod does it (all 11 that set `picture=` use a `.png`), so do not reintroduce the key on a hunch. If a publish still lands a still image, set the preview by hand on the Workshop page - no re-upload needed, and GIFs are definitely accepted there.
- The Workshop title image is the one asset that is public *before* anyone installs the mod, and it is currently built on the same unverified third-party art as the event pictures. `event_images/SOURCES.md` records the chain and the two ways out. Nothing else in the repo has that exposure.
- The marquee's neon bloom is a Gaussian of sigma `scf(32)` while the sign sits only 18 px from the edge of the 512-wide thumbnail canvas, so on that canvas the bloom is **clipped flat**. That is deliberate bleed for the thumbnail but a hard edge for the logo (alpha jumped 0 -> 224 in one column). `padded_sign_canvas` in `build_main_menu.py` re-renders the same sign on a wider canvas by shifting every absolute coordinate `build_sign` reads - `W`, `HEXW`, `SY0`/`SY1`/`SYM`, `GC`, `WM_TOP`, `SUB_TOP`. Sizes and differences (`CH`, `GAP_HALF`, `WM_W`, `SUB_W`, `SYM - SY0`) are translation-invariant; `SX0`/`SX1` are read only at import to build `HEXW`. The build prints the strongest alpha left on the crop border - ~0.02 is right, ~0.9 means it is clipping again.
- Ship the animated logo strip **uncompressed**, as OWB does its own. DXT5 quantises colour per 4x4 block; a block straddling a neon tube and the transparent black outside it gets endpoints spanning cyan to black, measured at mean 6 / peak 164 error on visible pixels, which reads as a speckled fringe along the tubes. Trade frames for size instead - the breath is a slow ramp and 16 frames step by under 2 luma levels each. `LOGO_FRAMES`/`LOGO_FPS` must match `noOfFrames`/`animation_rate_fps` in `mltd.gfx`.
- `animation = {}` blocks attach **only to `spriteType`** - ~56,000 across vanilla and all 25 installed mods, and not one on a `corneredTileSpriteType`. `GFX_frontend_bg` is a `corneredTileSpriteType`, so the menu rain cannot be an animation on the background: it must be a second, fully transparent sprite laid over it by the gui, which is exactly how OWB's `GFX_frontend_bg_snow_anim` (disabled in `frontendmainview.gui`) is built.
- In an animation texture, **colour lives in RGB and shape lives in alpha** - OWB's `bg_snow_anim1.dds` is near-white RGB everywhere with alpha 0 except on the flakes. `bg_snow_anim_background.dds` is alpha 0 throughout (so only the animations draw) and `bg_snow_anim_mask.dds` is a flat alpha 191 (a global 75% strength). We reference both by path and copy neither.
- A frontend overlay `iconType` is drawn **unscaled at the size of its BASE texture** (`texturefile`) - *not* of its `animationtexturefile`s, which are sampled inside that rect. Enlarging the animation textures alone does nothing; this was found by trying it. The sprite is anchored to its container's top-left, and `frontend_background` is 1920x1440 scaled to *cover*, so it overflows vertically and its top-left is `(1440*max(W/1920,H/1440) - H)/2` px **above** the screen (180 at 1080p, 240 at 1440p). A base only `H` tall leaves an empty band along the bottom. Hence `mltd_rain_base.dds` and `mltd_rain_mask.dds` at 2560x1792 instead of OWB's 2560x1440 pair, which covers 16:9 up to 1440p; 4K and 21:9 need more - raise `RAIN_W`/`RAIN_H`, nothing else. This is almost certainly why OWB's own snow overlay is commented out.
- `build_main_menu.py --preview` models the frontend geometry (cover-scale, overflow, unscaled sprite rect, magnified scrolling texture, the 191 mask) and prints the rows/columns actually covered. It caught the band above; use it before believing any change to the rain.
- `animationtexturescale` magnifies by `1 / scale`, so OWB's snow at 0.3 is blown up 3.3x. Our rain uses 0.75 and `RAIN_SCALE` in `build_main_menu.py` must be changed with it, or the streaks stop matching their on-screen size. `animationrotation`'s convention (whether it rotates the texture with the scroll) is **unverified** - hence vertical, short streaks, and values inside OWB's known-good 210/220 range.
- `effectFile = "....lua"` resolves to a `.shader` of the same name in `gfx/FX/`; no `.lua` exists. Do not "fix" it.
- Steam caps a Workshop preview image at **1 MiB whether it moves or not**, and that single number decides the GIF's size, frame count and palette. Three things keep it under: frames are delta-encoded against *what is still displayed* rather than against the previous frame (per-frame comparison lets a pixel creep away one `GIF_TOLERANCE` step at a time and accumulates over the loop); dithering is off, because its noise is exactly what run-length compression cannot pack; and the palette is chroma-weighted, because median cut allocates by pixel count and this image is overwhelmingly low-chroma teal - left alone it starves the gold wordmark, the violet tube and the green eyes and snaps all three to grey-blue.
- The rain loop closes because the tile is periodic over `(W/2, W)` and is rolled a whole number of pixels per frame whose total over the loop is an exact multiple of both periods - the same trick as `build_animated_portrait.py`. `rain_tile()` asserts it; changing `GIF_FRAMES` to a number that does not divide the periods will trip it rather than silently seam.
- The OWB marquee wordmark is not shipped as a reusable asset by any mod - every submod re-creates or re-mattes it. Ours comes from *Fountain of Dreams* and arrives silver with a violet keyline; `retint_wordmark()` maps it to the house gold (hue 40-53 deg, which OWB, ECR, Rustbelt Rising and Over The Horizon all use). Silver is legal - NCR-vs-Legion uses it - and `--silver` keeps it.
- A continuous-focus palette cannot be extended from a separate file, and a country gets exactly one palette (chosen by the `country` weight block, `default = yes` as fallback) - see Overriding OWB.
- Script variables are **32-bit fixed point with 3 decimals**, so they overflow above **2,147,483.647** and wrap negative (OWB writes the number at `TON_farming_scripted_effects.txt:11` and detects the wrap at `coring_button_scripted_triggers.txt:141`; vanilla marks `manpower` and friends "DEPRECATED, MAY OVERFLOW" and ships `_k` variants such as `state_population_k` "to avoid variable overflows"). Population arithmetic overflows easily: one state's population times a four-figure target is already hundreds of times over. **Divide before you multiply**, and keep divisors in thousands - `mltd_take_population_everywhere` does both, which caps its intermediate at 1,000 instead of 448,000,000.
- `check_variable`'s equality shorthand is `{ var = X value = N compare = equals }` or `{ X = N }`; **`==` is not valid** and appears nowhere in vanilla or OWB (`triggers_documentation.md:2110-2133`). `>` and `<` shorthand are fine.
- `add_victory_points` renders no trailing spacer in a tooltip (OWB comments on this at `Baggers (BAG) Focus.txt:1337`), so follow a run of them with `custom_effect_tooltip = mltd_newline_tt`.
- `add_caps` is OWB's, not vanilla's: it reads the temp variable `caps_to_add` set immediately before the call, and the displayed balance carries a "k" suffix, so `caps_to_add = 100` reads as "100k Bottle Caps".
- A `frameAnimatedSpriteType` strip must be exactly `frame_width x noOfFrames` wide; if the whole strip appears in the portrait slot, the two disagree.
- Startup `error.log` triage: lines about `artful_positioning_doctrine` / `tactics_doctrine_tech` / `tactics_spec_ops_cap_tech` XOR paths, `occupationlawdatabase`, `provincegraphics ... too far away from center` and `remotefile.cpp ... Failed allocate data buffer` are OWB/vanilla noise, not ours. Ours would mention `mltd`, `MLT_DROWNED_HERALD`, `warbike_unlock_tech` or a file under our paths.

- **Shared focuses come in only through shared prerequisites.** `shared_focus = <id>` in `mlt_nf` pulls in that focus and every shared focus linked to it by prerequisites on other *shared* focuses, and nothing else. A shared focus whose only prerequisite is a national focus is never pulled in: vanilla has to list `CONGO_congo_investments` (sole prerequisite `BEL_monetary_reconstruction`, `congo_shared.txt:951`) explicitly at `belgium.txt:20`. So a conflict focus must never hang off `mlt_kingdom_of_mlyeh` or any other national focus; gate on it in `available` instead. A new sub-tree also needs its root listed in the override. Never point a shared focus's `relative_position_id` at a national focus either: none of OWB's 464 or vanilla's 335 shared focuses does, so it is untested.
- **`network_national_coverage` is a 0-1 fraction** (`triggers_documentation.md:6503-6516`, example `value > 0.5`; vanilla `00_defines.lua:3637` and `:3644`, "[0, 1]"), while `network_strength` is 0-100. OWB's one non-zero coverage test, `Lost Hills (BOS) Focus.txt:9646-9649` (`value > 30`), uses the wrong scale and can never pass - do not copy it. Ours use 0.1-0.3.
- **Agency upgrades from script probably cost caps.** Every OWB upgrade requires 15 caps and pays -15 through `add_caps` in its `complete_effect` (`intelligence_agency_upgrades.txt:16-22`, `:29-34`). OWB's Unbound refunds its own scripted upgrades for that reason (`Unbound (UNB) Focus.txt:370-375`, "needed to counteract caps takeaway from spy upgrades"). `mltd_intel_foothold` refunds 15 per upgrade and skips both upgrade and refund at `agency_upgrade_number > 29`, OWB's ceiling (`00_scripted_effects.txt:540`), where the refund would be free caps. This is untested: if a root leaves the caps balance 15 higher, script upgrades are not charged and the refund must go. Also, `add_caps` runs `check_bankrupt` against the balance *before* its own change (`caps_scripted_effects.txt:48-55`; the condition is balance < 0 and caps net < 0, `:126-127`). That is why the refund is paid *before* the upgrade: paid after it, the refund's own `add_caps` would see the dip whenever the tribe holds under 15 caps with negative caps income, and would start OWB's bankruptcy chain (`bankrupt_events.1`, `:166`) even though the balance ends where it started.
- **The Tlaloc capstone brings his death forward.** `mltd_tla_the_drowned_god_sleeps` subtracts 64 from `TLA.current_databanks`, about 57 days of OWB's base drain (1.12/day, `history/countries/TLA - Tlaloc.txt:157`). So `nf_tlaloc.100` - the release of MAX, MOC and ZAP, `tlaloc_died`, the succession wars and `kill_tlaloc`'s nuke - arrives ~8 weeks sooner. It copies `on_daily_TLA`'s four guards (`tlaloc_on_actions.txt:276-281`), so it never drains a frozen or RRG-bound Tlaloc. It also runs only above 100, so it never zeroes the variable itself: OWB's own daily clamp (`:285-289`) and its `current_databanks = 0` check (`:318-327`) still fire the event.
- **Absorbing TRL is what turns WBH on The Warren.** `WBH_attack_the_warren` becomes available once `TRL = { exists = no }` (`Shared Brotherhood Focus.txt:2113`). With TRL gone, `grant_wargoals_on_core_states_of_prev` falls through to its no-country branch: claims on TRL's cores, 235 included, plus a `demand_stolen_territory` decision (`wargoal_effects.txt:69-83`). WBH's start-of-game truce with MLT (`nf_washington.14`) applies only when TRL is human (`events/nf_washington.txt:478`), so an MLT player never gets it. The Tide-Wall's `remove_claim_by = WBH` on 235 undoes that claim.
- **Operation tokens are shared with OWB's operations.** A `token_army` handed out by a focus also opens OWB's `operation_steal_tech_army` (`00_operations.txt:2443`) and `operation_steal_enemy_supplies` (`operations_fallout.txt:36-38`) against that target. `operation_steal_tech_army` and `operation_steal_tech_civilian` use up their token (`00_operations.txt:2467`, `:1903`). Running one before taking the sibling focus spends the token, and the sibling then waits on its coverage threshold instead.
- **Most capstones need both parents** (two `prerequisite` blocks = AND; Heaven's Guard's needs only its Schism, the Utah road war's takes either middle focus through one OR block), so a capstone strands if a parent can become impossible to take. Every middle focus's intel gate therefore lapses when its target dies: tests sit inside `if = { limit = { country_exists = X } }` or carry a `NOT = { country_exists = X }` branch, and every reward has a fallback.
- **Hoover Dam flags.** The Boulder City outcome is `fbhd_boulder_city_miracle_flag` - with `_flag`, unlike its effect `fbhd_boulder_city_miracle`; OWB's own commented-out test at `Lost Hills (BOS) Focus.txt:2599` has the wrong name. The three outcome flags are set at `hoover_dam_scripted_effects.txt:207/255/264`. No flag records the second battle: test `NCR = { has_war_with = CES }` or `CES = { has_completed_focus = ces_attack_ncr }`. That focus is unavailable before 2279.06.01 (`Caesars Legion (CES) Focus.txt:8586`), which is why The Turbines Sing falls back to that date.
- **There is no `TEX` tag.** `TEX` is a tag alias for TBH or LNS while one of them wears a `TEX_*` / `TAA_Texas_*` cosmetic (`common/country_tag_aliases/tag_aliases.txt:93-106`). Script against `TBH` and `LNS` directly, and test unification with `has_global_flag = texas_formed` (`texan_economic_union_scripted_effects.txt:657`).
- **The flavour guard has a one-day gap.** `mltd_flavour_can_fire` opens as soon as the Kingdom completes, but the 90-day `mltd_flavour_cooldown` is set by `mltd.1`'s `immediate` (`mltd_events.txt:8`), and the Kingdom fires `mltd.1` with `days = 1` (override `:1161`). A monthly roll inside that day can still land a flavour event before `mltd.1`. Setting the flag in the Kingdom's `completion_reward` would close the gap, at the cost of one more override line.
- `retire_character` removes an advisor for good; the Book expeditions use it for their deaths. Gate every such option with `has_character = <token>` and give the event an option that appears only when none of them is left, so the event always has a valid option.
- **Operative slots.** An agency starts with 1 (`00_static_modifiers.txt`, `created_intelligence_agency`) and upgrades add at most +1: vanilla `MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES = 1`, which OWB leaves alone (it only lowers `AGENCY_UPGRADE_PER_OPERATIVE_SLOT` to 4, `resistance_defines.lua:51`). So an unbuffed MLT tops out at 2 after its 4th upgrade, one short of the 3 that OWB's steal-tech operations need. Training Centers' `new_operative_slot_bonus` is "Operative recruitment choices", not slots. Old Castro's `mltd_keeper_of_the_order` brings MLT to 4.

## Testing

After every change, launch the game and read `C:\Users\jonat\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` (truncated each launch). Localisation key collisions go to `text.log` - the `warbike_unlock_tech` / `_desc` collision there is the intentional `replace/` override. `system.log` lists `Active Mod:` lines, which is how you confirm the submod loaded at all.

To reach the content: play MLT, complete `mlt_kingdom_of_mlyeh` (requires owning all cores of TRL, RBT, CCW, DIS; `mltd.1`/`mltd.2` fire 1-2 days later), then Gifts, the five Books (each needs control of its state, and is read only when its three-event expedition ends, 2-4 weeks after the focus), then the centre column (Call needs 1 Book, the Grand Ritual 3, the Walk 5; Call and the Walk each open a one-option event that applies their effects). Round 9 items to confirm first: **M'lulu's portrait rains** in the politics view and the general list (and her small icon is the graded card, not a slice of the strip); the Kingdom focus tooltip lists the two victory-point gains and the map shows M'lyeh at 25 VP; **Summon the Deep Ones stays listed and greyed with a day count** after a summon instead of disappearing, and reappears on day 90; the two Offerings decisions pay caps (top bar updates immediately) and permanent water in the capital; *Feed the Spawning Pools* appears in the continuous-focus palette for MLT (and only MLT), costs 1 political power a day and shows -15 % on all three creature archetypes while selected, and the discount disappears when a different continuous focus is chosen; a Star Spawn division still spawns fully equipped from a 80-piece stockpile. Then: the startup `error.log` no longer has the four `script_enum_equipment_bonus_type` warnings for `mltd_*_equipment*` or the two `recruit_character should only happen in game/history files` lines for `events/mltd_events.txt` (the last play-test's only lines that were ours); the Drowned Herald is absent from the general list at start and appears there, 4 / 4-2-2-1 with his portrait, right after `mltd.1`; the Deep Ones tech shows in the **Reward Technologies** tab; gifts apply the moment the decision is taken and expire after 30 days; a summoned division spawns **with its equipment** (the hidden `Spawn of the Deep` tech appears in the equipment's tooltip; 160 / 80 spare in Logistics) in the state that paid for it; the ritual focus tooltip shows the red modifier lines with values; the ritual idea appears when the focus is *selected* and disappears on completion, and the toll ticks daily in between; the Deep Ones template becomes trainable after focus 4 and its equipment producible; the operation appears once an agency exists (La Resistance) and MLT has a network in a neighbour with > 1,500 manpower.

Round 13 items to confirm (the conflict sub-trees, the flavour events and the Book expeditions; none play-tested yet):
- **Startup logs.** `error.log` has nothing naming `mltd_conflicts_focus.txt`, `mltd_scripted_triggers.txt`, an `mltd_ncr_` / `_tex_` / `_wbh_` / `_ces_` / `_bos_` / `_tla_` / `_hea_` / `_wht_` id, `mltd_intel_foothold` or `mltd_flavour_can_fire`, and `text.log` reports no missing key for them.
- **Layout.** MLT's tree shows the eight sub-trees in their slots: NCR and Texas left of the Kingdom and WBH and CES right of it on rows 13-15; BOS and Heaven's Guard left and Tlaloc and the Utah road war right on rows 17-19. They are greyed until the Kingdom, with **no line** from it, and do not overlap the trunk or the continuous-focus palette. DIS's tree, which shares the `lurk_` roots, shows none of them.
- **Roots.** After the Kingdom each root opens only while its target exists (Tlaloc's also after his death).
- **The agency.** With La Resistance, the first root founds *The Esoteric Order of M'lyeh* and each later root adds exactly one upgrade, leaving the caps balance where it started. A balance 15 higher means script upgrades are not charged and the refund must go; 15 lower means the refund failed.
- **Intel gates.** A middle focus stays greyed, with its token/coverage tooltip, until the token or the coverage arrives. A 0.2 threshold is actually reachable, which confirms the 0-1 scale. A focus-granted `token_army` opens both the sibling focus and OWB's steal operations against that target.
- **Theft.** Each theft lowers the victim's stockpile by exactly the amount taken and shows in MLT's Logistics under the victim's name.
- **Capstone gates** follow the world: a Hoover outcome flag or 1 June 2279; `texas_formed` or 2280; WBH's purge, war with MLT or 2280, **and** The Warren held; Heaven's Guard's holy wars or 2280; the Utah road war or 2280.
- **Tlaloc.** The Drowned God Sleeps cuts `TLA.current_databanks` by 64 (its tooltip prints live numbers), never below 36, and OWB's own death event still fires on schedule.
- **The Warren** gets its four bunkers and loses WBH's claim.
- **No DLC.** With La Resistance disabled in the launcher, every sub-tree can be taken end to end and pays PP and tech bonuses instead.
- **Flavour events.** No flavour event arrives within 90 days of `mltd.1`. After that they come every few months, never two within 120 days, each at most once. `mltd.11` / `mltd.16` appear only after the Call, `mltd.14` only after the first Book, `mltd.18` only with the capital controlled. `event mltd.9` ... `event mltd.18` in the console previews each: `.d` text readable on the pale paper, option text plain, and `mltd.9` option c greyed below 10 caps.
- **Book expeditions.** Completing a Book focus fires its chain two days later; every option shows *The expedition presses on.* and the next event arrives one to two weeks later. The gift decision and `mltd_books_read` change only at the third event. In 202 / 302 / 502 the chosen advisor leaves the advisor list for good, their option is gone from later events, and with both gone only the third option shows. 401's buy option is greyed below 50 caps; 402's first option adds 500 people to the capital.
- **Old Castro.** He appears among the cultural advisors only with La Resistance, greyed until MLT has an agency. Hiring him raises the agency screen's operative slots by 2 (to 3, or 4 after four upgrades), and OWB's steal-tech operations become runnable.

## Install

1. Copy `mod_folder/descriptor.mod` to `C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\rising_tide.mod`.
2. Append one line to that copy: `path="C:/Users/<you>/Documents/rising-tide/mod_folder"` - absolute, **forward slashes**, no trailing slash, pointing at `mod_folder`. It is machine-specific, which is why it is not in the repo. (Already installed on this machine.)
3. In the launcher: **Reload Installed Mods**, then add both this mod and Old World Blues to a playset and enable both.
4. **Load order.** `dependencies={ "Old World Blues" }` in *both* `mod_folder/descriptor.mod` and the installed launcher `.mod` is what makes this mod load **after** OWB, so our files win on any overlap and OWB's 95 `replace_path` entries do not delete ours - see OWB's own guide, `<OWB>/doc/OWB_MODDING_README.txt`: "After adding this your mod will load after OWB and won't be replaced by files we have or our replace_paths". Keep that block in both files. If you also order the playset by hand, put Rising Tide **below** Old World Blues - lower in the list loads later.

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
   4. The six overrides (`Mirelurk Tribe (MLT) Focus.txt`, `continuous_focus/generic.txt`, `common/characters/MLT.txt`, `history/countries/MLT - Mirelurk Tribe.txt`, `common/script_enums.txt`, `events/nf_mlt.txt`) must end up as OWB's new file **plus only our insertions** (plus Anastasia's replaced lines) - keep each file's original line endings and BOM state.
   5. Delete the `.bak` files afterwards.
3. Play the game to test, then read `...\Hearts of Iron IV\logs\error.log` (and `text.log` for localisation - the `warbike_unlock_tech` collision there is intentional) and confirm `system.log` lists both `Old World Blues` and `OWB - Rising Tide` as active mods.

## Compatibility

- Any submod that ships its own `common/continuous_focus/generic.txt` conflicts: whichever loads later wins the whole palette, so either its continuous focuses or *Feed the Spawning Pools* will be missing.
- The [OWB Official NCR versus Caesar's Legion submod](https://steamcommunity.com/sharedfiles/filedetails/?id=3010015443) ships its own `Mirelurk Tribe (MLT) Focus.txt`, which Rising Tide overrides too; whichever mod loads later wins the whole file, so run one or the other, not both. (It also ships `tech_fallout_land_doctrine.txt`, which Rising Tide no longer touches.)
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
