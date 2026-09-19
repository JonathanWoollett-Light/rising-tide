# Act IV - "The Drowned Republic": notes for the integrator

## What is in this act

`mod_folder/common/national_focus/mltd_act4_focus.txt` holds six shared focuses. It carries over the old NCR sub-tree's five
focuses, keeping their ids, costs, icons and every number, and adds one new close.

| Id | Cell (abs) | Placed as | Prerequisite | Status |
| --- | --- | --- | --- | --- |
| `mltd_ncr_a_mole_in_shady_sands` | (15,27) | (0,1) of `mltd_the_tide_turns_south` | `mltd_the_tide_turns_south` | kept, now the chapter |
| `mltd_ncr_drowned_delegates` | (13,28) | (-2,1) of the chapter | chapter | kept |
| `mltd_ncr_sleepers_on_the_long_15` | (15,28) | (0,1) of the chapter | chapter | kept |
| `mltd_ncr_salt_on_the_caravan_roads` | (17,28) | (2,1) of the chapter | chapter | kept |
| `mltd_ncr_the_turbines_sing` | (15,29) | (0,2) of the chapter | OR (delegates, sleepers, caravan) | kept, the war |
| `mltd_when_shady_sands_falls` | (15,30) | (0,3) of the chapter | `mltd_ncr_the_turbines_sing` | NEW, the close |

Nothing is merged into this act, and no focus id is deleted by it. Nothing here is listed in the override. The chapter
reaches the listed Act III roots through `mltd_the_tide_turns_south` (Act III's file), and the rest of the act reaches the chapter.

## Changes to the kept focuses (all per the spec's rules)

- **Chapter** (`mltd_ncr_a_mole_in_shady_sands`). The `available` block is gone: the Kingdom and `country_exists = NCR`
  were its only tests, and the prerequisite now does that job. `ai_will_do` is 10. The round-23 `is_ai` modifier is
  dropped. The shelter flags are now set only on a tag that exists; the tooltip shows while either NCR or MOT exists. The
  rewards are unchanged: foothold, shelter, and LaR civ 10 / army 5, or +25 PP.
- **The three beads.** Their intelligence `available` blocks are removed; the intel rewards stay inside
  `has_dlc = "La Resistance"`, and the round-23 `is_ai` modifiers are dropped. Fallbacks when the NCR is gone:
  - Delegates keeps its +40 PP and gets the infantry tech bonus through its existing `else`.
  - Sleepers keeps its 30 XP and gets +25 PP through its existing `else`.
  - Caravan gains a new `else = { add_political_power = 25 }` when the NCR does not exist. Its +100 caps still pays either way.
- **The war** (`mltd_ncr_the_turbines_sing`) keeps its Hoover gate, declaration, rewards and `will_lead_to_war_with`. Two
  things change:
  - Its prerequisite is now any one bead (one OR block); it used to be the Sleepers alone.
  - Its round-22 AI hold (0 while `mltd_ai_stage_ncr` or `mltd_ai_army_ready` fails) no longer applies once
    `has_war_with = NCR` or `mltd_ai_ncr_beaten`. The focus is now a spine node that the close requires. If the AI's
    conquest block declared first, or the NCR fell some other way, the old hold would hold an AI off the focus until 2284,
    and with it Acts V, VI and the finale. The hold still does its original job: it stops the focus from starting the war early.
  - **This is a deliberate small departure from rule 7 ("KEEP their existing modifiers").** The existing modifiers are
    kept and gain two exemptions. Act V's and Act VI's war capstones have the same hazard, so their integrators may want
    the same exemption (`has_war_with = <target>`, `mltd_ai_legion_beaten`, ...).
- **Descriptions.** None of the kept `_desc` needed rewriting (no merges), and no existing loc key is replaced.

## The close, `mltd_when_shady_sands_falls`

- 30 days, `ai_will_do` 10, icon `GFX_goal_NCR_FO2_Tattered_Flag` (OWB, with `_shine`).
- **Gate.** `available` is `custom_trigger_tooltip = { tooltip = mltd_ncr_beaten_tt OR = { mltd_ai_ncr_beaten = yes
  has_country_flag = mltd_ncr_capitulated NCR = { is_subject_of = ROOT } } }`. The last two branches are additions to the
  spec, both for rule 5 (never strand), because `has_capitulated` clears once a country leaves its last war:
  - **The win is recorded** (review fix). An NCR that survives the peace as an independent rump - a human who takes only
    some states or releases nations, or Covenant allies (BRK, BDT) sharing the peace points - is neither gone nor
    capitulated any more, so `mltd_ai_ncr_beaten` fails for good although MLT won. The window to select the close while it
    still passed is often zero days (the NCR's capitulation starts the peace conference at once when it is the last enemy),
    and an AI already busy on another focus misses it too. So the staged `on_capitulation` (below) sets the country flag
    `mltd_ncr_capitulated` on MLT when the NCR capitulates while at war with MLT, and the close accepts it.
  - **A subject NCR counts.** A human who puppets the NCR at the peace leaves it existing and not capitulated.
  - The tooltip text: "has capitulated to us, is no more, or is our subject".
- **New staging file `on_actions.txt`** (not in the spec's table): an `on_capitulation = { effect = { ... } }` block,
  indented one tab. Put it inside the `on_actions = { }` of `mod_folder/common/on_actions/mltd_on_actions.txt` (after
  `on_war_relation_added`; that file has no `on_capitulation` yet), and add it to CLAUDE.md's `mltd_on_actions.txt` row and
  the close's description. Without it the close still works through the other two branches, but a rump NCR strands the
  spine at row 30. Act V's close (`mltd_legion_beaten_tt`, the Legion) and Act VI's (`mltd_texas_beaten`, TBH and LNS)
  test `has_capitulated` the same way and have the same hazard; the same `on_capitulation` can carry a branch for each
  (e.g. `tag = CES` -> `mltd_ces_capitulated`), if their gates are given the matching flag.
- **Reward.**
  - Previews both of `mltd.40`'s options with native lines. `effect_tooltip` shows effects and does not run them (vanilla
    effects_documentation; OWB uses it in focuses).
  - Fires `mltd.40` (1 day) and delivers news `mltd.41` to every other country (2 days).
  - **Numbers in two places** (review fix): `add_research_slot = 1`, `mltd_the_drowned_rangers` and the 50 army
    experience live in `mltd.40`'s options and in the focus's two `effect_tooltip` previews. Both files carry a "change both
    together" comment; record the pair in CLAUDE.md's *Numbers in several places* notes when the act is documented.
- **`mltd.40`**, picture `GFX_event_shady_sands`, has two options:
  - (a) `add_research_slot = 1`, ai_chance base 3.
  - (b) `add_ideas = mltd_the_drowned_rangers` + `army_experience = 50`, ai_chance base 1.
- **`mltd.41`** is plain world news, picture `GFX_event_NCR_congress` (OWB uses it in its own news events), with one
  option. Its text is written to hold whoever took Shady Sands.
- **Idea `mltd_the_drowned_rangers`** is permanent, picture `generic_ranger_helm` (OWB `GFX_idea_generic_ranger_helm`,
  the red-eyed ranger helmet): +5 % `army_attack_factor`, +5 % `army_defence_factor`, +5 % `army_org_factor`.

## Keys that become unused once `mltd_conflicts_focus.txt` is deleted

- `mltd_ncr_network_15_tt`, `mltd_ncr_network_20_tt`, `mltd_ncr_network_25_tt` (loc). They were the beads' coverage
  gates, and nothing else in `mod_folder/` or the repo's Python references them (grep). CLAUDE.md mentions the
  `mltd_<tag>_network_<pct>_tt` family generically; its "35 coverage checks are wrapped" note will need a new count.

## AI, plan, telemetry and docs (for the integrator; I edited none of them)

- **`common/ai_strategy_plans/mltd_MLT.txt`.**
  - The Kingdom-and-Books plan lists the four non-war NCR focuses (around lines 193-196) before the Final Ritual. They now
    sit behind `mltd_the_tide_turns_south` and cannot be taken in that phase; move them into the late plan after Act III.
  - Add `mltd_when_shady_sands_falls` right after `mltd_ncr_the_turbines_sing` in the late plan.
  - `mltd_ncr_the_turbines_sing = 0` in the second plan's `focus_factors` is now redundant, because the focus is
    unreachable before the Final Ritual. It is harmless.
- **`CONQUEST_PLAN.txt`.**
  - Line ~358 (`focus mltd_ncr_a_mole_in_shady_sands # the NCR sub-tree, 5 focuses (~177 days) ...`) becomes the Act IV
    chapter, and it follows `mltd_the_tide_turns_south`. The fastest path to the declaration is still 30 + 35 + 42 days
    (chapter, one bead, war), and all three beads plus the war total 177 days, as before.
  - Add `focus mltd_when_shady_sands_falls` once the NCR has capitulated, with the pick in `mltd.40`. The AI takes the
    research slot 3 times in 4, so the plan should take it too, or add a `# AI deviation:` line.
  - `check_plan_sync.py` will want the new id in an `ai_national_focuses` list, and the telemetry rebuilt.
- **`build_telemetry.py:140`** asserts that the pulled shared focuses come from exactly {`Shared Oregon Coastals
  Focus.txt`, `mltd_conflicts_focus.txt`}, and `:142` names that file. It has to learn the act files, then be re-run so
  that `mltd_when_shady_sands_falls` gets its FOCUS line.
- **Duplicate ids.** Until `mltd_conflicts_focus.txt` is deleted, the NCR ids are defined twice (there and here). Delete
  it before any launch.
- **Stall risk, by design.** The close has no date fallback. If the NCR is never beaten (it out-fights MLT, or a human
  never takes the war), the spine stops at row 30, and Acts V, VI and the finale stay closed. A war MLT wins no longer
  stalls it, provided the staged `on_capitulation` is merged (see the gate above). `mltd_ai_stage_ncr` opens
  the AI's NCR war by 2284 at the latest, so an AI MLT at least tries.
- **The research slot is a strong trophy** (the spec asked for it). Option (b) is weaker on paper: three +5 % army
  modifiers and 50 XP. That is why the AI weights (a) 3:1.

## Unverified constructs

- `effect_tooltip = { add_ideas = ... army_experience = 50 }` in a focus `completion_reward`. It is vanilla-documented, and
  OWB uses it in focuses (`April Fools Focus (GIM).txt:541`), but it has not been seen in this mod.
- `relative_position_id` to a shared focus defined in another file (`mltd_the_tide_turns_south`, Act III). Ids are
  global, so this should work, but this mod has not done it before.
- `[253.GetName]` in an event option name (`mltd.40.a`). The mole's focus name already uses the same function.
- That `has_war_with = MLT` still holds on the capitulated NCR when `on_capitulation` fires, including when its
  capitulation ends the war. Vanilla tests `has_war_with` against the capitulated country the same way
  (`00_on_actions.txt:937-938`); the `FROM = { tag = MLT }` branch catches MLT's own win if it does not. That
  `has_capitulated` clears at the peace is documented by vanilla's `days_since_capitulated` ("even if it is no longer
  capitulated", `triggers_documentation.md:2505`).
