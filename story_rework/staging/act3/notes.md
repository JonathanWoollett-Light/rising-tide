# Act III - "The Stars Are Right" - integrator notes

Focus file: `mod_folder/common/national_focus/mltd_act3_focus.txt` (LF, no BOM, tabs; 5 shared focuses).
Staging: `events.txt` (mltd.30, mltd.31), `loc.yml` (13 new keys, no replacements), `ideas.txt` (`mltd_the_northern_waters`).
No scripted triggers or effects were needed, so there is no `triggers.txt` / `effects.txt`.

## Tree

| Id | Cell | Prerequisite | Status |
| --- | --- | --- | --- |
| `mltd_wbh_the_tide_wall` | (12,25) abs | `mltd_the_final_ritual` | kept |
| `mltd_brk_the_drowned_covenant` | (14,25) abs | `mltd_the_final_ritual` | kept |
| `mltd_bdt_hail_the_drowned_king` | (16,25) abs | `mltd_the_final_ritual` | kept |
| `mltd_bdt_drown_the_dance` | (18,25) abs | `mltd_the_final_ritual` | kept |
| `mltd_the_tide_turns_south` | (15,26) abs | OR(the four above) | new (close) |

The override already lists the four fan focuses (checked: `Mirelurk Tribe (MLT) Focus.txt:26-29`). The close needs no listing;
it comes in through its prerequisites on them. Act IV's chapter (`mltd_act4_focus.txt`) already points at
`mltd_the_tide_turns_south` for its prerequisite and relative position.

## What changed in the kept focuses

- **All four**: old prerequisites dropped; `prerequisite = { focus = mltd_the_final_ritual }`; absolute cells; everything else
  as in `mltd_conflicts_focus.txt`.
- **The Tide-Wall**: gates unchanged (the Brotherhood's purge / war with MLT / none left / 2280, and The Warren owned and
  controlled). Its AI modifier (`mltd_ai_stage_wbh`, `mltd_ai_army_ready`) now applies only while a Brotherhood the focus
  would declare on exists (`mltd_wbh_brotherhood`, not at war with MLT, not its subject), so an AI is not held off the
  30-army-XP fallback by the readiness line. Reward (review fix): the claim removal on The Warren still runs while any
  Brotherhood lives, but the -3 % war support and the `mltd_wbh_tide_wall` idea now need a Brotherhood that is **not MLT's
  subject** (both the `if` limit and the `every_country` limit); with only a subject one, or none, the `else` pays the
  30 army XP. Before, a puppeted Brotherhood took the war-support hit and MLT got an idea aimed at its own subject.
- **The Drowned Covenant**: `available` now opens with `has_completed_focus = mltd_brk_salt_on_the_broken_coast` (the old
  sub-tree root, an Act II head - no line). Every courtship gate (war, subject, faction, the pirate coast, and with La
  Resistance the 50 % cult, `token_civilian`, 30 % coverage and 50 % civilian intel) sits inside
  `if = { limit = { country_exists = BRK  BRK = { NOT = { is_subject_of = ROOT } } } }`, and the reward's `if` has the same
  limit, so once the Broken Coast is gone **or is MLT's subject** (review fix: before, a subject BRK failed
  `is_subject = no` and left the focus untakeable) the focus is takeable and pays +50 political power (`else`) instead of
  sending `mltd.21`. A BRK that is some other country's subject still fails `is_subject = no`, as before.
- **Hail the Drowned King**: `available` now opens with `has_completed_focus = mltd_bdt_the_bone_shore`; courtship gates and
  `country_exists = BDT` kept (no fallback: it is an invitation, and Drown the Dance is always the other path);
  `mutually_exclusive = { focus = mltd_bdt_drown_the_dance }` kept one-sided; `ai_will_do` kept at **4** (above the war's 3,
  deliberately, so the AI takes the invitation when it can - an exception to the spec's "heads/beads 3").
- **Drown the Dance**: `available` is now
  `if = { limit = { country_exists = BDT  BDT = { NOT = { is_subject_of = ROOT } } } NOT = { is_in_faction_with = BDT } }`, so it
  is free once the Bone Dancers are gone or are MLT's subject (review fix: a subject BDT sits in MLT's faction whenever MLT
  leads one, which used to make the focus untakeable). Reward: the declaration (already skipped for a subject) and BDT's
  -6 % stability / -3 % war support as before, and the **40 army XP only while BDT exists and is not MLT's subject**; with BDT
  gone or a subject, +50 political power instead (today's version paid the 40 XP either way, and until the review fix hit a
  subject BDT with the penalties; the fallback is +50 PP per the spec, not both). Its AI modifier (`mltd_ai_courting_bdt`,
  `mltd_ai_army_ready`) now applies only while BDT exists and is not MLT's subject (`mltd_ai_courting_bdt` itself does not
  test subjects, so a subject BDT could otherwise hold the AI off the free fallback).

Never strand: the close needs any one of the four. Drown the Dance is takeable unless an independent BDT is in MLT's
faction, which only Hail the Drowned King (via `mltd.24`) puts it in - and then Hail already satisfies the OR. With spec
rule 5's "or is MLT's subject" case, the Covenant and Drown the Dance pay +50 PP and the Tide-Wall 30 army XP.

## The close

`mltd_the_tide_turns_south`, 30 days, `ai_will_do` 10. `available`: `num_of_controlled_states > 49` behind
`mltd_tide_turns_south_states_tt` ("Controls at least 50 states" - **the 49/50 is a literal in both places; change them
together**). Reward: `add_ideas = mltd_the_northern_waters`, `country_event = { id = mltd.30 days = 1 }`, and news `mltd.31` to
every other country (days = 2). Both events have no option effects (the focus applied the idea); `mltd.30` has two flavour
options, like `mltd.5`.

Idea `mltd_the_northern_waters` (permanent, `original_tag = MLT`, `removal_cost = -1`, picture OWB's `generic_coast_guard`,
a sailor's cap - `GFX_idea_generic_coast_guard`, `z_fallout_ideas.gfx:3637`, texture `gfx/interface/ideas/generic/coast_guard.dds`;
used in OWB only by puppet, minor-nation (TVR, SHO) and settler ideas, and nowhere in `mod_folder` or the other acts' staging).
Review fix: the first draft used `brk_master_of_sea`, but MLT already shows that anchor as the icon of the dynamic modifier
`mltd_brk_volunteers` (`mltd_dynamic_modifiers.txt:23`, added by Act II's The Deep Ones Sail North and never removed), so the
two would have sat side by side. Stability +5 %, war support +5 %,
justify war goal time -25 %. The -25 % is the act table's own figure and is outside rule 11's +-5-10 % band on purpose
(vanilla uses -0.25 on nine ideas; -10 % justification time would be invisible). Change it here if the band must hold.

Pictures: `mltd.30` `GFX_event_sub_generic_wasteland_river` (a river running across the wastes - the tide turning south),
`mltd.31` `GFX_event_NCR_night` (NCR troopers at a sandbagged post). Neither is used by any other mltd event yet.
Icon: `GFX_goal_BRK_drums_of_war` (has `_shine`; "the drums turn toward California").

## Nothing deleted, nothing made unused

Act III merges nothing. Every tooltip key the four kept focuses use is unchanged and still referenced
(`mltd_wbh_crusade_turns_tt`, `mltd_brk_pirate_coast_tt`, `mltd_brk_strong_cult_tt`, `mltd_brk_network_tt`, `mltd_brk_intel_tt`,
`mltd_brk_covenant_offer_tt`, `mltd_brk_covenant_if_accepted_tt`, `mltd_bdt_strong_cult_tt`, `mltd_bdt_network_tt`,
`mltd_bdt_covenant_offer_tt`, `mltd_newline_tt`), as are `mltd_wbh_tide_wall` (idea) and `mltd.21` / `mltd.24`.
No kept `_desc` needed rewriting: none of the four's text depends on its old position.

## AI and plan implications (for the integrator)

1. **Plan phases.** In `common/ai_strategy_plans/mltd_MLT.txt` the second plan (Kingdom and Books, aborted by
   `mltd_the_final_ritual`) lists `mltd_bdt_hail_the_drowned_king` and `mltd_bdt_drown_the_dance` before the Final Ritual and
   `mltd_wbh_the_tide_wall` / `mltd_brk_the_drowned_covenant` after it (lines ~186-190). All four now need the Final Ritual,
   so they belong only in the late plan. Suggested late-plan order before Act IV: `mltd_brk_the_drowned_covenant`,
   `mltd_bdt_hail_the_drowned_king`, `mltd_bdt_drown_the_dance`, `mltd_wbh_the_tide_wall`, `mltd_the_tide_turns_south`, then
   `mltd_ncr_a_mole_in_shady_sands` (the late plan already has the Covenant / Hail / Drown ahead of the NCR at ~293-298, and
   the Tide-Wall at the end at ~346 - move it up and add the close).
2. **The WBH war no longer comes from the Tide-Wall before the Final Ritual.** Round 22's design had the Tide-Wall declare the
   Washington war in the Kingdom-and-Books phase (the one capstone `focus_factors` did not zero). Now, before the ritual,
   that war can only come from `mltd_ai_conquer_wbh`'s own justification, or waits for the Tide-Wall after the ritual
   (`mltd_ai_stage_wbh` is false while `mltd_the_final_ritual` is held, true again after it). `CONQUEST_PLAN.txt` must
   re-cut the Cascadia war accordingly (its Tide-Wall line moves after the Final Ritual, or the plan justifies on WBH).
   Also re-check any `focus_factors` entry for these four ids in the plans.
3. **The NCR now waits on 50 controlled states** (the close gates Act IV's chapter). `mltd_ai_stage_ncr` already needs the
   north consolidated (> 70 of the north's 79 states), so this should never be the binding gate for the AI; check it
   against the plan's snapshots at the Final Ritual.
4. **Possible AI wait, not a strand**: if the Covenant's and Hail's courtship gates fail, BDT is still courted
   (`mltd_ai_courting_bdt` holds Drown the Dance at 0 while BDT can still crown the Odious King) and the Tide-Wall's crusade
   gate or readiness line fails, an AI takes nothing in Act III until one of them changes. The Tide-Wall's 2280 date fallback
   and the readiness line (which the army's growth meets) end the wait; a human always has Drown the Dance.
5. `check_plan_sync.py` / `build_telemetry.py`: the new focus `mltd_the_tide_turns_south` needs a plan line, an AI plan entry
   and a telemetry FOCUS line (`python build_telemetry.py`), and `CONQUEST_PLAN.txt:370-374` (Hail, Covenant) must move to
   after the Final Ritual. The new idea has no AI hook.
6. CLAUDE.md: the Conflict sub-trees section (slots table, "Round 17" capstone text, Broken Coast / Bone Dancers rows) describes
   the old positions and prerequisites of these four; the event table needs `mltd.30` / `mltd.31`; the ideas row needs
   `mltd_the_northern_waters`.

## Unverified

- A listed shared focus whose only prerequisite is a national focus (`mltd_the_final_ritual`): vanilla's precedent is
  `CONGO_congo_investments` (listed at `belgium.txt:20`), none in OWB; the spec relies on it for Acts II-III.
- A trigger `if` nested inside another trigger `if` in `available` (the Covenant: `country_exists = BRK`, then
  `has_dlc = "La Resistance"`), and how its tooltip renders: the house idiom uses a single level.
- `will_lead_to_war_with = BDT` / `WBH` / `TCA` on a focus whose target no longer exists (unchanged from before; no error seen).
  The same warning also shows when the target is MLT's subject and the focus will not declare (the declaration was
  already skipped for subjects; the review fix only changed the fallback).
- That a subject of MLT counts as `is_in_faction_with` MLT whenever MLT leads a faction (the reason Drown the Dance's
  `available` skips that test for a subject BDT). Harmless either way: the test is skipped for a subject.
- How `justify_war_goal_time = -0.25` reads in the idea tooltip (documented as "1 decimal place").
- Two focuses on the same row two columns apart (14 and 16, 16 and 18) with the mutual-exclusion marker between Hail and Drown:
  the marker is drawn between adjacent focuses, as the old slot j did at (-1,2)/(1,2).
