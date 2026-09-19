# Act VI - "All Waters Are One": integrator notes

Focus file: `mod_folder/common/national_focus/mltd_act6_focus.txt` (LF, no BOM, tabs; braces balance).
Staging: `events.txt` (mltd.60, .61, .62), `loc.yml`, `ideas.txt` (`mltd_the_drowned_south`), `triggers.txt`
(`mltd_texas_beaten`). No `effects.txt`: every effect called already exists (`mltd_intel_foothold`, OWB `add_caps`).

## Layout (absolute cells, given Act V's close at (15,34))

| Focus | Relative | Absolute | Prerequisite |
| --- | --- | --- | --- |
| `mltd_the_southern_deep` (new, chapter) | `mltd_when_the_legion_breaks` (0,1) | (15,35) | `mltd_when_the_legion_breaks` |
| `mltd_tex_all_waters_are_one` (kept) | chapter (-2,1) | (13,36) | chapter |
| `mltd_tex_black_water_rising` (kept, war) | chapter (-2,2) | (13,37) | all waters |
| `mltd_ate_the_feathered_tide` (new) | chapter (0,1) | (15,36) | chapter |
| `mltd_ate_the_serpent_drowns` (new, war) | chapter (0,2) | (15,37) | feathered tide |
| `mltd_tla_the_iron_god_dreams` (kept) | chapter (2,1) | (17,36) | chapter |
| `mltd_tla_the_drowned_god_sleeps` (kept, war) | chapter (2,2) | (17,37) | iron god |
| `mltd_the_last_king_kneels` (new, close) | chapter (0,3) | (15,38) | OR(black water, serpent drowns, drowned god) |

Nothing in this act is listed in the override; it is pulled in through `mltd_when_the_legion_breaks`.

## Merge decisions (numbers)

- **Intel duplicates.** SPEC rule 10 drops "a second intel grant to the same tag", while the Act VI table carries the
  merged focuses' "civ 15". Both are honoured by ONE `add_intel` per tag at civilian 15 / army 10 (the head's army 10,
  the merged focus's civilian 15) plus the merged focus's `token_army`. Branch totals are a little below the old
  sub-trees' (Texas per tag: civilian 35 / army 30 instead of 45 / 30; Tlaloc's voice tags: civilian 15 instead of 25).
- **Tlaloc's voices.** The Iron God now also carries The Three Voices' target order: Tlaloc while he lives, else each
  of MAX / MOC / ZAP, else ARM. A voice tag gets civilian 15 / army 10 + `token_army`; every other living tag keeps The
  Iron God's 10 / 10 (ARM army 10 only). With La Resistance and no tag alive, or without the DLC: electronics 50 %
  (The Iron God's) **and** +50 political power (The Three Voices').
- **No-DLC fallback of All Waters** is +50 political power: the head's +25 plus The Silent Partner's +25.
- **Target gone.** All Waters pays +50 political power when neither TBH nor LNS exists (`mltd_tex_texas_gone_tt`);
  the +80 caps are paid either way, as The Silent Partner paid them. The Feathered Tide pays +25 and The Serpent
  Drowns +50 when ATE is gone **or is our subject** (`mltd_ate_gone_tt`, `mltd_ate_serpent_gone_tt`); the 40 army
  experience is paid either way. Black Water and The Drowned God were already takeable with their targets gone.
- **Gates dropped** (never strand, no intel gates): The Iron God's `mltd_tla_chiconet_alive_tt` existence gate and
  `has_completed_focus = mlt_kingdom_of_mlyeh`; All Waters' `country_exists` gate. The round-23 `is_ai` modifiers on
  All Waters and The Iron God (`NOT mltd_ai_ncr_beaten`) are gone (rule 7). The war capstones keep theirs: Black Water
  and The Drowned God still read `mltd_ai_legion_beaten` + `mltd_ai_army_ready` (as today); The Serpent Drowns reads
  `mltd_ai_stage_ate` + `mltd_ai_army_ready` (SPEC), **plus** (review fix) a second `is_ai` modifier: factor 0 while ATE
  exists, is not our subject and not at war with us, and either ATE fails `mltd_ai_safe_target` or MLT is at war with a
  Texan tag (TBH / LNS) that has not capitulated. Why: `mltd_ai_stage_ate` opens with the Texas and Tlaloc stages and
  `mltd_ai_army_ready` is nearly always true late on, so while the AI waited for Texas to fall (the close needs only
  Texas) The Serpent Drowns was the one Act VI focus left, and its declaration skips the safe-target check that
  `mltd_ai_conquer_ate` makes (Nuevo Aztlan: 686k people, 38 divisions at start). A capitulated Texan tag counts as
  beaten, as in `mltd_texas_beaten`.
- **Order inside the capstones.** Black Water: declarations, then the Trinity theft, 30 army XP, then its old
  rewards. The Drowned God: declarations, then the Iron Bones theft (its tooltip now only shows while one of the five
  tags exists), 20 army XP and +100 caps, then its old rewards.

## Additions beyond the table (small, flavour from OWB's ATE)

OWB's ATE is **Nuevo Aztlan** (`countries_l_english.yml:75-85`; the SPEC's "Aztec Empire" is its history filename). Hooks
used, in text and two small conditionals:
- The blind Speaker, Yesenia Aztlanl (`ATE_speaker_yesenia_aztlanl`), has dreamed of Tlaloc's death for ten years
  (`ATE_EMPRESS_DESC`, `nf_ate.10`). **The Feathered Tide**: while she still rules (`has_country_leader = { character =
  ATE_speaker_yesenia_aztlanl ruling_only = yes }`), ATE also loses 2 % war support (`mltd_ate_speaker_dreams_tt`).
- OWB's Aztlan navy, "the Frogs" (`nf_ate.9`), Kinkaid's `ate_serpent_rises` ("The Serpent Rises", whose icon The
  Serpent Drowns takes). **The Serpent Drowns**: if ATE has completed `ate_serpent_rises`, MLT gains 20 navy experience
  (`mltd_ate_frogs_tt`).
- The Feathered Serpent banner (`feathered_serpent` idea, `nf_ate.2`), the Eagle Knights and Jaguars, and ATE's
  "Brutish Operatives" (`ate_brutish_ops`) appear in the two descriptions only.
- `mltd_texas_beaten` also counts a Texan tag that is **MLT's subject** as beaten (SPEC rule 5's "or is MLT's
  subject"), so a human who puppets Texas is not stranded before the close.

## New content

- Idea `mltd_the_drowned_south` (permanent, from the close): +10 % factory output, +5 % stability; picture
  `generic_gulf_treaty` (OWB `GFX_idea_generic_gulf_treaty`, unused elsewhere in our mod).
- The close also gives `add_research_slot = 1`.
- Events: `mltd.60` (MLT, chapter, one option, `GFX_event_mecha_aztec_calendar`), `mltd.61` (MLT, close, one option,
  `GFX_event_texas_capitol`), `mltd.62` (world news, `GFX_event_fall_alamo`). Options carry no effects; the focuses pay.
- Icons (all OWB, each with `_shine` in `z_fallout_national_focuses_shine.gfx`): chapter
  `GFX_goal_ITZ_navigate_the_gulf`, Feathered Tide `GFX_goal_ATE_empress`, Serpent Drowns
  `GFX_goal_ATE_focus_the_serpent_rises`, close `GFX_goal_MIN_fallen_kingdom`. None is used by another act.

## Loc

- New keys and the four replacement descriptions are in `loc.yml` (replacements at the end, under their own header):
  `mltd_tex_all_waters_are_one_desc`, `mltd_tex_black_water_rising_desc`, `mltd_tla_the_iron_god_dreams_desc`,
  `mltd_tla_the_drowned_god_sleeps_desc`. Replace the old lines in place rather than appending duplicates.
- Nested keys are one level deep and plain: `$mltd_the_southern_deep$`, `$mltd_the_last_king_kneels$`,
  `$mltd_deep_ones$` (ours), OWB's `$ate_serpent_rises$` (`english/ATE/focus_ATE_l_english.yml`) and
  `$texan_economic_union$` (`english/faction_tracking/faction_names_l_english.yml`, already nested by our old
  Silent Partner text). No `replace/` key.
- Characters by token: `[TLA_tlaloc.GetName]`, `[ATE_speaker_yesenia_aztlanl.GetName]`, `[ATE_gail_kinkaid.GetName]`,
  `[MLT_MLULU.GetName]`.

## Now unused (only `mltd_conflicts_focus.txt`, to be deleted, and their own loc lines reference them)

Loc keys: `mltd_tex_the_silent_partner`, `mltd_tex_the_silent_partner_desc`, `mltd_tex_wreckers_on_the_trinity`,
`mltd_tex_wreckers_on_the_trinity_desc`, `mltd_tex_civilian_network_tt`, `mltd_tex_army_network_tt`,
`mltd_tla_the_three_voices`, `mltd_tla_the_three_voices_desc`, `mltd_tla_picking_the_iron_bones`,
`mltd_tla_picking_the_iron_bones_desc`, `mltd_tla_three_voices_network_tt`, `mltd_tla_iron_bones_network_tt`,
`mltd_tla_chiconet_alive_tt`. (Grep over `mod_folder` finds no `$...$` nesting of any of them.)

## AI, plan and telemetry (outside my files - the integrator's job)

- `common/ai_strategy_plans/mltd_MLT.txt`: the late plan's list (lines ~333-341) names the four deleted ids; replace
  with `mltd_the_southern_deep`, `mltd_tex_all_waters_are_one`, `mltd_ate_the_feathered_tide`,
  `mltd_tla_the_iron_god_dreams`, `mltd_tex_black_water_rising`, `mltd_ate_the_serpent_drowns`,
  `mltd_tla_the_drowned_god_sleeps`, `mltd_the_last_king_kneels`. The second plan's `focus_factors` (lines ~231-232)
  zero Black Water and The Drowned God; add `mltd_ate_the_serpent_drowns = 0` there too (it declares war).
- `mltd_ai_conquer_ate` already exists (`common/ai_strategy/mltd_MLT.txt` ~1816) and `mltd_ai_stage_ate` in
  `mltd_ai_triggers.txt`, so the new war has an AI counterpart; `CONQUEST_PLAN.txt` needs an operation line for
  `mltd_ate_the_feathered_tide` / `mltd_ate_the_serpent_drowns` and the close (research slot, idea), or
  `check_plan_sync.py` will flag the new focuses and the ATE war.
- The close waits on Texas whichever capstone is taken first; an AI that takes The Drowned God first reaches Texas
  through its conquest stages (`mltd_ai_stage_tbh` / `_lns`), which open at the same time. The Serpent Drowns now
  waits, for an AI, until no uncapitulated Texan tag is at war with MLT and ATE is a safe target, so an AI fights
  Aztlan after Texas, as `CONQUEST_PLAN.txt`'s 2286+ block already orders it (Texas and Tlaloc sub-trees, then
  `declare war on ATE`). The plan's ATE line can stay after the Texas and Tlaloc lines; if it is rewritten as the focus,
  put `focus mltd_ate_the_feathered_tide` / the Serpent's war after `mltd_tex_black_water_rising`. No deviation line is
  needed for the order; if the plan ever puts ATE before Texas, add `# AI deviation: focus mltd_ate_the_serpent_drowns -
  an AI waits for the Texan war and a safe target`.
- `common/scripted_effects/mltd_telemetry_effects.txt` lists the deleted focus ids, but **a plain rebuild fails**:
  `build_telemetry.py` must be changed first (shared by every act). It asserts no shared focus id is defined twice
  (`:121`) - the kept Act VI ids (`mltd_tex_all_waters_are_one`, `mltd_tex_black_water_rising`,
  `mltd_tla_the_iron_god_dreams`, `mltd_tla_the_drowned_god_sleeps`) are defined in both `mltd_act6_focus.txt` and
  `mltd_conflicts_focus.txt` until the latter is deleted - and it asserts the pulled shared-focus groups are exactly
  `{'Shared Oregon Coastals Focus.txt', 'mltd_conflicts_focus.txt'}` (`:140`), reading the conflict ids from that one
  file (`:142`, and the section title at `:333`). Order: delete `mltd_conflicts_focus.txt`; in `build_telemetry.py`
  replace the two-file assertion and `conflicts = groups['mltd_conflicts_focus.txt']` with the union, in file order, of
  the groups from `mltd_act2_focus.txt` .. `mltd_act6_focus.txt` and `mltd_finale_focus.txt` (assert every pulled group
  is Oregon or one of those), and retitle the `:333` section; then `python build_telemetry.py` and
  `python check_plan_sync.py`.
- CLAUDE.md: the Conflict sub-trees table rows for Texas and Tlaloc, a new Nueva Aztlan row, the event list
  (`mltd.60-62`), the ideas list (`mltd_the_drowned_south`) and the Naming table's taken event ids.

## Unverified

- `has_country_leader = { character = ... ruling_only = yes }` in an effect's `limit`, in another country's scope
  (vanilla documents it; OWB uses it in triggers and achievements).
- `navy_experience` on a tribe with next to no navy (it is only a pool; OWB focuses pay it freely).
- That the Nueva Aztlan cult shelter behaves like the others (it only sets `mltd_cult_sheltered`, which
  `mltd_cult_refresh` reads by flag, not by tag).
