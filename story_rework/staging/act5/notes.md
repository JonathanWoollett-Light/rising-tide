# Act V - "The Sea Against Mars" - notes for the integrator

## Files
- `mod_folder/common/national_focus/mltd_act5_focus.txt` - 10 shared focuses, LF, no BOM, tabs; braces balanced (347/347
  after the review fixes).
- `act5/events.txt` - `mltd.50` (MLT, chapter), `mltd.51` (MLT, close, two options), `mltd.52` (world news). No namespace line.
- `act5/ideas.txt` - `mltd_mars_beneath_the_waves` (permanent; +5 % army attack, +5 % war support, +5 % recruitable
  population via `conscription_factor`; picture `generic_legion`, OWB's torn Legion flag).
- `act5/loc.yml` - 20 NEW keys and 8 REPLACEMENT `_desc` values (marked by a comment; replace the existing values of
  the same keys, do not add them twice).
- No `triggers.txt` / `effects.txt`: nothing new was needed. The close uses `mltd_ai_legion_beaten`
  (`common/scripted_triggers/mltd_ai_triggers.txt`), which the spec names.
- `act5/on_actions.txt` (review fix; not in the spec's table, the same kind of file Act IV stages): an `on_capitulation`
  branch that sets the country flag `mltd_ces_capitulated` on MLT when the Legion capitulates while at war with MLT.
  Merge its `if` into Act IV's `on_capitulation` effect in `mod_folder/common/on_actions/mltd_on_actions.txt`, beside the
  NCR branch. It can also stay a block of its own, because on_actions merge across blocks (OWB's 00_, ARR_ and
  BAG_on_actions.txt each carry one). Add it to CLAUDE.md's `mltd_on_actions.txt` row.

## Layout (absolute cells, derived from the relative positions)
Chapter `mltd_mars_in_the_water` (15,31) = (0,1) of `mltd_when_shady_sands_falls` (defined in `mltd_act4_focus.txt`,
checked). Heads (12,32) CES, (14,32) BOS, (16,32) Utah, (18,32) HEA; capstones (12..18,33) under their own heads; close
`mltd_when_the_legion_breaks` (15,34), one OR block over the four capstones. Act VI's chapter hangs off
`mltd_when_the_legion_breaks` (the id the spec gives).

## Decisions worth a look
- **The close counts a recorded win and a subject Legion as beaten**: `OR = { mltd_ai_legion_beaten = yes
  has_country_flag = mltd_ces_capitulated CES = { is_subject_of = ROOT } }`, under `mltd_legion_beaten_tt` ("has
  capitulated, is no more, or is our subject"). Both branches serve rule 5 (never strand), as in Act IV's close for the NCR:
  - `has_capitulated` clears once the Legion leaves its last war. A Legion that survives the peace as a rump (a human who
    takes only some states, Covenant allies sharing the points, an ally who puppets it) would otherwise never count as
    beaten, and the window to select the close while the Legion is still capitulated is often zero days. The flag, set by
    the staged `on_capitulation` above, keeps the win. The flag branch is a review fix; the reviewer did not raise it, but
    it is the same hazard as review finding 2 and the one Act IV's notes flagged for Act V.
  - A human who puppets the Legion has the subject branch.
- **The idea is granted by the focus, not the event** ("plus permanent idea" in the spec), so both options get it. The
  focus previews both event options with native lines (`effect_tooltip`), in Act IV's pattern: `mltd_legion_breaks_choice_tt`
  header, `mltd_legion_breaks_freed_tt` + the option-a effects, `mltd_legion_breaks_pens_tt` + the option-b effects. The
  5,000 / +5 % / 5,000 live in two places, the event's options and the focus's `effect_tooltip` - change both (list the
  pair in CLAUDE.md's *Numbers in several places*).
- **The two options are the same 5,000 people** (review fix; the spec gave +20,000 manpower for option b).
  - Why: 20,000 sat in OWB's top ~0.6 % of `add_manpower` grants (982 positive grants in OWB's focuses and events: median
    500, 90th percentile 2,000, 99th 15,000), and was 2-20 times an AI MLT's whole pool in every saved run (`mp_k` 1-10 in
    SNAP). Option a's 5,000 people give only a few hundred recruitable manpower, so it was dominated by about two orders
    of magnitude.
  - Now, freed: 5,000 people in the capital (they grow, and count toward the summons' and offerings' pools) and +5 %
    stability. Fed to the pools: 5,000 manpower at once.
  - The texts that promised "tens of thousands" of the chained now say "thousands" (`mltd_when_the_legion_breaks_desc`,
    `mltd.51.d`), and `mltd.51.d` no longer promises a host "greater than the Legion's ever was".
- **The Chained Are Given to the Tide** is folded into `mltd.51` option a with the spec's numbers (+5,000 capital
  population through OWB's `add_state_population`, +5 % stability) instead of its old 1,000 (+500 with full pens, +500
  after Nipton). Its conditional extras were dropped: the spec defines the option.
- **Intelligence duplicates** (rule 10): where a merged focus granted intel to the same country again, the two grants are
  one `add_intel` at the larger values - CES civ 15 / army 10 (was 10/10 + 15), BOS civ 15 / army 10 (was 10/10 + 15),
  HEA civ 10 / army 5 (was 10/5 + 10), WHT civ 10 (was 10 + 10), EHT army 10 (was 10 + 10; Sand in the Engines' copy and
  its +20 no-DLC fallback dropped). Tokens were never duplicates and all stay.
- **No-DLC fallbacks are summed where both halves survive**: River +75 PP (25 + 50), Paladin +60 PP (25 + 35) plus the
  Codex's electronics 75 % bonus, Whispers +25 PP plus the Schism's electronics 50 % bonus, Lake God +25 PP plus the
  Shamans' infantry-weapons 50 % bonus. With La Resistance but the target gone, the same fallbacks pay (River: +25, and
  +50 if there is no agency).
- **Tech bonus names**: the four bonuses that were named after a deleted focus now carry the focus that grants them -
  `mltd_bos_the_drowned_paladin` (was `mltd_bos_the_codex_unsealed`), `mltd_wht_the_lake_god_answers` (was
  `mltd_wht_the_drowned_shamans`), `mltd_hea_whispers_in_the_steam` (was `mltd_hea_a_second_schism`),
  `mltd_hea_the_crusade_turns_south` (was `mltd_hea_steam_for_the_deep`). A save holding an unused bonus under an old name
  would show the raw key once those loc keys are deleted (cosmetic).
- **Costs unchanged** on the kept focuses (River 35, Sea 45, Paladin 35, Blood 45, Lake God 30, Rites 42, Whispers 30,
  Crusade 42); new: chapter 35, close 30. Each branch is now 2 focuses (CES 80 days, was 192 over 5; BOS 80, was 190;
  Utah 72, was 172; HEA 72, was 142), and only one branch is needed to reach the close (35 + 35..45 + 42..45 + 30).
  If the merged heads feel too rich for their length, raise their `cost` - the payoff was kept, not the time.
- **Shelter flags and tooltips** are now inside `if = { limit = { country_exists = X } }` (they used to be set on the tag
  unconditionally), so a dead target gets no flag and the tooltip does not show.
- **Order in the capstones**: the declaration first, then the merged theft (the old Salt/Armoury/Sand/Steam rewards), then
  the capstone's own rewards. A capstone taken while already at war with the target still steals.
- **Guns for Both Sides never arms an enemy** (review fix). The sale now lives in The Lake God Answers, an ungated head
  that opens once the NCR is beaten, which is exactly when the AI's WHT and EHT conquest stages open. It used to test
  only that the buyer existed, so an MLT already at war with the White Legs or the Eighties handed that enemy 200 of its
  rifles. Each sale now also needs `NOT = { has_war_with = <buyer> }`; if neither buyer qualifies, the 80-caps fallback
  pays. In CLAUDE.md's Guns for Both Sides row, "to each side that is still alive" should become "to each side that is
  still alive and not at war with us".
- **The capstones' AI hold is readiness only** (review fix). This departs from the list in rule 7, under that rule's own
  second sentence (drop modifiers that only wait on an earlier act).
  - Before, each of the four read `OR = { NOT = { mltd_ai_ncr_beaten = yes } NOT = { mltd_ai_army_ready = yes } }`.
  - The chapter already needs Act IV's close, so the NCR term no longer orders anything. It could only hold the AI back
    once a beaten NCR outlived the peace, which Act IV's close now allows through its flag `mltd_ncr_capitulated`. All
    four capstones would then read 0 for an AI, and with them Act V's close, Act VI and the finale.
  - Now: `modifier = { factor = 0 is_ai = yes NOT = { mltd_ai_army_ready = yes } }`.
- **Act VI has the same hazard one act later** (for the integrator, or Act VI's fixer). `mltd_act6_focus.txt` (lines ~167
  and ~625) holds two capstones on `NOT = { mltd_ai_legion_beaten = yes }` for an AI. Act V's close can now complete on
  the recorded win while a rump Legion lives on, and then those two capstones would read 0 for an AI for good. The same
  fix applies there: drop the Legion term and keep readiness.

## Now unused (only the deleted `mltd_conflicts_focus.txt` and the loc file reference them; grep-checked)
Focus name/desc loc of the 11 deleted focuses: `mltd_ces_the_drowned_frumentarius(_desc)`,
`mltd_ces_the_chained_are_given_to_the_tide(_desc)`, `mltd_ces_salt_in_the_armouries(_desc)`,
`mltd_bos_the_paladin_returns(_desc)`, `mltd_bos_the_tide_takes_the_armoury(_desc)`, `mltd_bos_the_codex_unsealed(_desc)`,
`mltd_wht_the_drowned_shamans(_desc)`, `mltd_wht_guns_for_both_sides(_desc)`, `mltd_wht_sand_in_the_engines(_desc)`,
`mltd_hea_a_second_schism(_desc)`, `mltd_hea_steam_for_the_deep(_desc)`.
Tooltips: `mltd_ces_chained_faithful_tt`, `mltd_ces_chained_pens_full_tt`, `mltd_ces_chained_nipton_tt`,
`mltd_ces_network_10_tt`, `mltd_ces_network_15_tt`, `mltd_bos_paladin_gate_tt`, `mltd_bos_codex_gate_tt`,
`mltd_bos_armoury_gate_tt`, `mltd_hea_network_20_tt`, `mltd_hea_network_25_tt`, `mltd_wht_network_20_tt`,
`mltd_eht_network_15_tt`.
Still used (keep): `mltd_ces_drowned_frumentarius_operative`, `mltd_ces_mars_*_tt`, `mltd_ces_cult_sheltered_tt`,
`mltd_bos_armoury_bare_tt`, `mltd_bos_war_feeds_tt`, `mltd_bos_tension_rises_tt`, `mltd_bos_accords_betrayed_tt`,
`mltd_bos_no_quarrel_tt`, `mltd_bos_cult_sheltered_tt`, `mltd_wht_shamans_converts_tt`, `mltd_wht_guns_war_tt`,
`mltd_wht_road_war_tt`, `mltd_wht_jetty_old_ones_tt`, `mltd_wht_cult_sheltered_tt`, `mltd_hea_schism_war_tt`,
`mltd_hea_crusade_tt`, `mltd_hea_crusade_loot_tt`, `mltd_hea_cult_sheltered_tt`, the temp variable `mltd_wht_sold`, and
the four timed ideas (`mltd_ces_the_drowned_bull`, `mltd_bos_red_tide`, `mltd_wht_rites_on_the_jetty`,
`mltd_hea_pilgrims_of_the_steam`).

## AI, plan, telemetry (for the integrator)
- `common/ai_strategy_plans/mltd_MLT.txt`, `mltd_MLT_late_game`: replace the Legion / Lost Hills / Utah / Heaven's Guard
  lists with `mltd_mars_in_the_water`, `mltd_ces_what_the_river_carries`, `mltd_ces_the_sea_against_mars`,
  `mltd_bos_the_drowned_paladin`, `mltd_bos_blood_in_the_water`, `mltd_wht_the_lake_god_answers`,
  `mltd_wht_rites_on_the_spiral_jetty`, `mltd_hea_whispers_in_the_steam`, `mltd_hea_the_crusade_turns_south`,
  `mltd_when_the_legion_breaks`. The Kingdom-and-Books plan's `focus_factors` zeroes on the four capstones are harmless
  but moot now (the tree cannot reach them before the NCR falls).
- **Act V now needs the NCR beaten** (through Act IV's close). The AI stages for CES/BOS/WHT/EHT/HEA
  (`mltd_ai_stage_*`: Final Ritual AND (NCR beaten OR 2283)) keep a 2283 fallback the tree no longer has: a stalled NCR
  war holds every Act V capstone, while the conquest blocks may still justify on those targets by hand after 2283. The
  plan should say so (a `# AI deviation:` line if the AI keeps the date).
- The close waits on the Legion, and only The Sea Against Mars declares on it; an AI that takes Blood in the Water, the
  Rites or the Crusade first keeps working the fan (heads are factor 3, ungated) until its army is ready for the CES war.
- Without the NCR term an AI takes the capstones on readiness alone, while `mltd_ai_stage_ces/bos/wht/eht/hea` still
  read `mltd_ai_ncr_beaten OR 2283`. If a beaten NCR outlives the peace, a capstone can start a war whose conquest stage
  is still closed. The conquest block then follows, because it is on for any target MLT is already at war with. To keep
  the stages in step, the integrator can read the stages' `mltd_ai_ncr_beaten` as "Act IV's close done".
- `mltd.51`: AI picks option a two times in three (spec's base 2 / 1). `CONQUEST_PLAN.txt` should pick one for the human
  line (suggest a: the population feeds the Leviathan summons and the offerings; option b is now 5,000 manpower, not
  20,000).
- Rerun `python build_telemetry.py` (11 focus ids gone, 2 new) and make `check_plan_sync.py` pass: the plan must name
  `mltd_mars_in_the_water` and `mltd_when_the_legion_breaks` (or carry deviation lines).
- CLAUDE.md to update:
  - Conflict sub-trees: the CES/BOS/HEA/Utah rows, including the Guns for Both Sides row (above), and *Numbers in two
    places* - the Legion's 1,000 / 500 / 500 tooltips are gone.
  - The Events list (`mltd.50-52`) and the Naming table's taken event ids.
  - The `mltd_on_actions.txt` row: `on_capitulation`, flag `mltd_ces_capitulated`.
  - The close's 5,000 / +5 % / 5,000 under *Numbers in several places*.

## Loc values changed by the review fixes (no keys added or removed)
- `mltd_mars_in_the_water_desc`, `mltd.50.d`: the Legion's scouts water pack-brahmin, not horses. The wasteland has no
  horses (OWB's own `ces_the_frontier_desc`: "And find out what horses were!"), so the scouts also "went", not "rode",
  down to the river.
- `mltd_mars_in_the_water_desc`: "For a generation", not "For a century", because the Legion dates from 2247 (OWB
  `nf_legion.3.d`).
- `mltd_mars_beneath_the_waves_desc`: "the host of §Y[MLT.GetNameDef]§!", naming the nation through its function. It
  reads "M'lyeh" after the Kingdom (OWB's `MLT_cosmetic_tag_*`). "The faithful of M'lyeh" elsewhere means the faith and
  stays.
- `mltd_when_the_legion_breaks_desc`, `mltd.51.d`: "thousands" of the chained, not "tens of thousands" (see the 5,000
  above).

## Unverified
- That `effect_tooltip = { capital_scope = { set_temp_variable = { pop_add = 5000 } add_state_population = yes } }`
  prints `+5,000` in the focus tooltip (OWB's `add_state_population_tt` reads `[?pop_add|0+=]`; temp variables are set
  while tooltips are built, which is how OWB's `add_caps` previews work, but not seen inside `effect_tooltip`). If it
  reads `+0`, replace that preview with a literal custom tooltip.
- Whether the two 5,000s (people freed into the capital, or manpower at once) feel like a real choice in play. If the
  trophy feels small, raise both together.
- The staged `on_capitulation` branch, as for Act IV's: that `has_war_with = MLT` still holds for the capitulated
  country inside the on_action. Vanilla tests it there (`00_on_actions.txt:937-938`), and `FROM = { tag = MLT }` covers
  MLT's own win if it does not.
- Picture choices are OWB sprites checked to exist: `GFX_event_CES_camp_2` (a legionary above a river), `GFX_event_legion_slaves`,
  `GFX_event_CES_burning`; focus icons `GFX_goal_CES_The_Rubicon` and `GFX_goal_CES_Free_Slaves`, both with `_shine`.
