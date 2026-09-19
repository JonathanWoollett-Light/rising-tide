# Act II - "The Northern Waters": notes for the integrator

## Files

- `mod_folder/common/national_focus/mltd_act2_focus.txt` (new; LF, no BOM, tabs; 6 shared focuses, braces balanced).
- `act2/loc.yml`: one NEW key (`mltd_brk_volunteer_size_6_tt`) and four REPLACEMENT descs
  (`mltd_wbh_the_drowned_knights_desc`, `mltd_brk_salt_on_the_broken_coast_desc`,
  `mltd_brk_the_deep_ones_sail_north_desc`, `mltd_bdt_the_dancers_hear_the_tide_desc`) - replace the existing lines
  in `mltd_l_english.yml` (lines 234, 577, 579, 615 today), do not append duplicates.
- No events, ideas, triggers or effects: Act II has no event of its own (spec).

## What the override needs

1. List the three heads in `Mirelurk Tribe (MLT) Focus.txt`:
   `shared_focus = mltd_wbh_eyes_in_the_sound`, `shared_focus = mltd_brk_salt_on_the_broken_coast`,
   `shared_focus = mltd_bdt_the_bone_shore`. The beads come in through their shared prerequisites. (Done in the
   working copy.)
2. Give `mltd_the_final_ritual` the OR block
   `prerequisite = { focus = mltd_wbh_the_drowned_knights focus = mltd_brk_the_deep_ones_sail_north focus = mltd_bdt_the_dancers_hear_the_tide }`
   (done in the working copy) **and remove its `prerequisite = { focus = mltd_the_deep_ones_walk }` block** (still there,
   override ~line 1691). Keep `relative_position_id = mltd_the_deep_ones_walk` and `y = 3`: positions draw no line.
   - Why: the Walk (15,21), Salt (15,22), Sail North (15,23) and the Ritual (15,24) share column 15, so the Walk -> Ritual
     AND line runs solid straight down through Salt and Sail North and, on its last segment, lies on top of Sail North's
     dashed OR line. The Broken Coast then reads as a mandatory solid chain while Washington and the Bone Dancers look
     optional.
   - The block adds no constraint: every bead needs its head and every head needs the Walk, so the ordering holds without
     it. With it gone the Ritual shows three dashed lines, from (13,23), (15,23) and (17,23).
   - SPEC.md's row-24 line ("prereq Walk AND (OR the 3 ends)") becomes "prereq OR the 3 ends". CLAUDE.md's table row 5
     and anything else describing the Ritual's prerequisites should match.
   - Moving the Broken Coast branch off x = 15 instead would break spec rule 3 and leave the spine empty on rows 22-23.
3. Precedent for a listed shared focus whose prerequisite is a national focus: vanilla `belgium.txt:20` lists
   `CONGO_congo_investments`, whose only prerequisite is `BEL_monetary_reconstruction` (CLAUDE.md > Gotchas).

## Cells (absolute)

| Focus | Cell | Prerequisite | Cost |
| --- | --- | --- | --- |
| `mltd_wbh_eyes_in_the_sound` | (13,22) abs | `mltd_the_deep_ones_walk` | 35 |
| `mltd_wbh_the_drowned_knights` | (13,23) = Eyes (0,1) | Eyes | 56 |
| `mltd_brk_salt_on_the_broken_coast` | (15,22) abs | `mltd_the_deep_ones_walk` | 49 |
| `mltd_brk_the_deep_ones_sail_north` | (15,23) = Salt (0,1) | Salt | 63 |
| `mltd_bdt_the_bone_shore` | (17,22) abs | `mltd_the_deep_ones_walk` | 35 |
| `mltd_bdt_the_dancers_hear_the_tide` | (17,23) = Bone Shore (0,1) | Bone Shore | 56 |

Nothing else in the override occupies x 11-19 at rows 22-23 (computed from the override's positions).

## Merges (the four deleted ids)

- `mltd_wbh_salt_in_the_citadel` -> `mltd_wbh_the_drowned_knights`: each Brotherhood -40 PP, -6 % stability; with La
  Resistance and a living Brotherhood, civilian intel 15 + `token_army` on it; else +25 PP. The Knights' own theft
  (600 infantry equipment over 1,200; 60 power armour over 120) and 30 army XP are unchanged.
- `mltd_brk_the_drowned_raiders` -> `mltd_brk_salt_on_the_broken_coast`: +10 to BRK's cult (tooltip
  `mltd_brk_raiders_cult_tt`, reused), and its intel folded into the root's single grant - civilian 10 + 15 = **25**,
  army 10, plus `token_army`. Without La Resistance, or with BRK gone, the two +25 PP become one **+50 PP**. The shelter
  flag is now set before the cult is founded, so the new cult starts with the halved decay. (Spec rule 10 would drop a
  second intel grant to the same tag as a pure duplicate; it is summed here instead and priced into Salt's 49 days. Cut
  it back to civilian 10 and +25 PP if you want the letter of the rule.)
- `mltd_brk_star_spawn_over_the_strait` -> `mltd_brk_the_deep_ones_sail_north`: `mltd_brk_add_volunteer_size` called
  twice inside `hidden_effect`, behind the new one-line tooltip `mltd_brk_volunteer_size_6_tt` (the effect's own
  `mltd_brk_volunteer_size_tt` would otherwise print "+3" twice). **The 6 is a literal in that key; the 3 stays in the
  effect.** The summon-flag gates (`mltd_deep_ones_summon_unlocked`, `mltd_star_spawn_summon_unlocked`) are gone: the
  Walk sets both.
- `mltd_bdt_salt_on_the_bone_road` -> `mltd_bdt_the_dancers_hear_the_tide`: steals 600 infantry equipment from BDT
  when it holds more than 1,200, else +25 PP; 30 army XP.

## Costs (changed after review)

A focus's price is its length (OWB `FOCUS_POINT_DAYS = 1`). Keeping the kept focuses' own lengths would have paid each
old sub-tree's whole payoff in roughly half its days (Washington 112 -> 77, the Broken Coast 161 -> 77, the Bone Dancers
112 -> 70), on top of the intel gates being gone. So each merged bead now keeps its own length **plus about 40-50 % of the
focus it absorbed, in whole weeks**:

| Bead | Was | Absorbed | Now |
| --- | --- | --- | --- |
| `mltd_wbh_the_drowned_knights` | 42 | Heresy in the Citadel, 35 | 56 |
| `mltd_brk_salt_on_the_broken_coast` | 35 | The Drowned Raiders, 35 | 49 |
| `mltd_brk_the_deep_ones_sail_north` | 42 | Star Spawn over the Strait, 49 | 63 |
| `mltd_bdt_the_dancers_hear_the_tide` | 35 | Salt on the Bone Road, 42 | 56 |

Branches: Washington 91 days (old 112), the Broken Coast 112 (old 161), the Bone Dancers 91 (old 112) - about 70-80 % of
the old days for the same payoff. All six take 294 days, against 385 for the ten old focuses they replace.

**Cross-act consistency:** Acts V and VI kept their kept focuses' own costs through larger merges (e.g. Act V's
`mltd_bos_the_drowned_paladin` stays 35 while absorbing 35 + 40 days of focuses). Pick one rule for all acts - this
one, or "the kept focus's own cost" - before the plan is re-cut; if the latter, restore 42 / 35 / 42 / 35 here.

## Behaviour changes worth knowing

- **No intel gates** on any of the six. The old Citadel / Knights / Raiders / Dancers / Bone Road gates (token or
  coverage) are gone; the tokens they handed out now only open OWB's own operations (steal tech, steal supplies).
- **Fallbacks when the target is gone:** Eyes and Knights pay +25 PP each (no Brotherhood holds Washington); Salt +50 PP;
  Sail North **+50 PP instead of the volunteers** (the old focuses gave the volunteers even with BRK dead - the modifier
  also raises the limit towards any other country at war; drop the `if`/`else` in Sail North if you would rather keep
  that); Bone Shore +25 PP; Dancers +25 PP (intel) + 25 PP (theft).
- Eyes' cult shelter, Salt's and Bone Shore's are wrapped in an existence test, so no flag lands on a dead tag.
- A Brotherhood or BDT that is already MLT's subject is still hit (PP, stability, theft), exactly as before - the rule
  only asks that the focus stay takeable, which it does.
- The Haida watch in `on_daily_MLT` (`mltd_on_actions.txt:46`) keys on `mltd_brk_salt_on_the_broken_coast`, which now
  comes after The Deep Ones Walk rather than after the Kingdom: the watch starts later in the game.
- The Final Ritual now waits on one Act II branch: at least 91 days after the Walk (Washington or the Bone Dancers),
  112 through the Broken Coast. In `CONQUEST_PLAN.txt` the Walk ends ~2277-12 and the Ritual starts ~2278-07, so the
  plan's timeline absorbs it.

## AI and plan (must change in the same round)

- **Focus AI:** all six `ai_will_do = { factor = 3 }`. The round-23 `is_ai` modifiers on Eyes and the old Knights
  (`NOT = { mltd_ai_stage_wbh = yes }`) are dropped (spec rule 7): an AI may now spy on Washington straight after the
  Walk, before it holds 30 states. Neither focus declares anything; The Tide-Wall (Act III) keeps its stage gate.
- `common/ai_strategy_plans/mltd_MLT.txt` names the deleted ids at lines 174, 179, 181, 185 (kingdom_and_books) and
  290, 292, 296, 344 (late game) - remove them, or `check_plan_sync.py` fails.
- **Order before the ritual.** The kingdom_and_books plan lists all six Act II focuses before `mltd_the_final_ritual`,
  so an AI that reaches 200,000 people would still spend 294 days on Act II first. Suggest one branch, then the ritual,
  then the rest - e.g. `mltd_brk_salt_on_the_broken_coast`, `mltd_brk_the_deep_ones_sail_north` (112 days; the
  volunteers feed `mltd_ai_brk_helped` before the NCR), `mltd_the_final_ritual`, then the WBH and BDT beads (still
  takeable after the ritual; nothing in Act II is exclusive). If the ritual should come sooner, Washington or the Bone
  Dancers first is 91 days. The late plan's entries for the kept ids remain valid fallbacks.
- `CONQUEST_PLAN.txt:324-336` (the 2278-03 block): the Raiders, Star Spawn over the Strait and Bone Road lines go; Salt
  becomes 49 days (with the +10 cult, army token and civilian intel 25), Sail North "+6 volunteer divisions" at 63 days,
  the Dancers 56 days with the theft and 30 XP; the WBH comment ("4 focuses, ~155 days") becomes Eyes + Knights
  (91 days) with The Tide-Wall in Act III; the plan must take one Act II branch before `mltd_the_final_ritual`, and no
  longer needs the operations the old intel gates asked for.
- Telemetry: `build_telemetry.py:140` asserts the shared-focus files are exactly `{'Shared Oregon Coastals Focus.txt',
  'mltd_conflicts_focus.txt'}` and line 142 reads `groups['mltd_conflicts_focus.txt']` - both need the per-act files.
  Then rebuild: the four deleted ids' FOCUS lines (`mltd_telemetry_effects.txt:703-705, 843-850, 868-870`) go.

## Stale comments naming deleted focuses or the deleted file

- `common/scripted_effects/mltd_scripted_effects.txt:716-718`, above `mltd_brk_add_volunteer_size`: the section header
  (716) names `common/national_focus/mltd_conflicts_focus.txt` - now `mltd_act2_focus.txt`; 717-718 say "from The Deep
  Ones Sail North and Star Spawn over the Strait" - now "from The Deep Ones Sail North, which calls it twice".
- `common/dynamic_modifiers/mltd_dynamic_modifiers.txt:19`: "Added by mltd_brk_add_volunteer_size (The Deep Ones Sail
  North, Star Spawn over the Strait): +3 volunteer divisions each" - reword to "Added by mltd_brk_add_volunteer_size,
  called twice by The Deep Ones Sail North (+3 each)".
- Not Act II's alone, but the same deletion: `mltd_scripted_effects.txt:382` (the header of `mltd_intel_foothold`,
  "Every conflict sub-tree (common/national_focus/mltd_conflicts_focus.txt) opens with this").
- CLAUDE.md: the WBH, Broken Coast and Bone Dancers rows of the conflict-sub-tree table, the slot table, and
  *The Broken Coast's volunteers* ("The +3 is a literal in `mltd_brk_add_volunteer_size` and
  `mltd_brk_volunteer_size_tt`" - add `mltd_brk_volunteer_size_6_tt`, the 6).

## Loc keys that become unused (delete only once `mltd_conflicts_focus.txt` is gone, and after grepping the other acts)

- Deleted focuses: `mltd_wbh_salt_in_the_citadel`, `mltd_wbh_salt_in_the_citadel_desc`, `mltd_brk_the_drowned_raiders`,
  `mltd_brk_the_drowned_raiders_desc`, `mltd_brk_star_spawn_over_the_strait`, `mltd_brk_star_spawn_over_the_strait_desc`,
  `mltd_bdt_salt_on_the_bone_road`, `mltd_bdt_salt_on_the_bone_road_desc`.
- Dropped intel gates: `mltd_wbh_network_20_tt`, `mltd_wbh_network_25_tt`, `mltd_tca_network_20_tt`,
  `mltd_tca_network_25_tt`, `mltd_brk_network_20_tt`, `mltd_bdt_network_20_tt`.
- Dropped gates: `mltd_brk_deep_ones_answer_tt`, `mltd_brk_star_spawn_answer_tt`, `mltd_wbh_brotherhood_exists_tt`.
- Still used, keep: `mltd_bdt_network_tt` (Hail the Drowned King), `mltd_brk_network_tt` (the Covenant),
  `mltd_brk_volunteer_size_tt` (inside `mltd_brk_add_volunteer_size`), `mltd_brk_raiders_cult_tt` (now Salt's).

## Unverified

- `mltd_brk_add_volunteer_size` twice in one effect: expected +6 on `mltd_brk_volunteer_size_var` (two
  `add_to_variable`s; the second call finds the modifier present and only re-runs `force_update_dynamic_modifier`).
- Not a risk, for the record: a national focus with one OR prerequisite over three shared focuses is vanilla's own
  shape (`belgium.txt:7907`, `CONGO_congo_free_state` / `_overseas_department_of_belgium` / `_dominion_of_congo`), so
  the Final Ritual's reconvergence has a precedent in both directions.
