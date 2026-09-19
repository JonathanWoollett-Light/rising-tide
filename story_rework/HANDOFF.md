# Handoff: round 27, the story-act rework (paused 2026-09-19)

> **Superseded for current status by [HANDOFF_2.md](HANDOFF_2.md)** (the second pause). This file still holds the
> rework's description, its file list, the first review's findings F1-F20 and the open design questions.

## Where things stand

The focus-tree rework is **built, integrated and mostly reviewed, but not tested in game and not committed**. It turns
the ten side-by-side conflict sub-trees into one central story line in the style of the Mojave Chapter's tree.

The last step, the fixer that applies the review findings, was stopped partway through, on purpose, to pause the run.
By then it had applied almost every finding (see *Review findings*). The repo was checked after the stop:

| Check | Result |
| --- | --- |
| `python check_plan_sync.py` | OK |
| `python ai_run_report.py --selftest` | 62 of 62 pass |
| Brace balance, every `.txt` under `mod_folder/` | balanced |
| `mltd_l_english.yml` | UTF-8 with BOM, LF, decodes cleanly |
| Grid (integrator's resolver) | 116 focuses, 116 distinct cells, no overlaps |
| Pull-in | exactly the 39 story focuses, nothing else |

`git status`: 20 modified files (1,716 lines added, 4,318 removed), `mltd_conflicts_focus.txt` deleted, and six new focus
files. Everything is on `master` and uncommitted, on top of `11b78e1 WIP: Big update 4`.

## What the rework is

- **The spine** runs down the centre column, x = 15. Act I (Kingdom -> Books -> Call -> Grand Ritual) is unchanged.
- **Acts II and III** are fans that reconverge on the rituals.
- **Acts IV, V and VI** each run chapter -> fan -> war -> close.
- **The finale** is *R'lyeh Rises*, then three mutually exclusive endings.

There are 39 story focuses: 28 existing ids kept, 18 merged away into kept focuses, and 11 new.

| Rows | Act | Focuses |
| --- | --- | --- |
| 22-23 | II *The Northern Waters* | Washington / Broken Coast / Bone Dancers, two each; the Final Ritual needs any one branch end |
| 24 | Final Ritual (national) | moved down a row |
| 25-26 | III *The Stars Are Right* | Tide-Wall, Covenant, Hail the Drowned King, Drown the Dance -> **The Tide Turns South** (NEW) |
| 27-30 | IV *The Drowned Republic* | A Mole in Shady Sands -> three beads -> The Turbines Sing (war) -> **When Shady Sands Falls** (NEW; +1 research slot or the Drowned Rangers) |
| 31-34 | V *The Sea Against Mars* | **Mars in the Water** (NEW) -> Legion / Lost Hills / Utah / Heaven's Guard, head + war each -> **When the Legion Breaks** (NEW) |
| 35-38 | VI *All Waters Are One* | **The Southern Deep** (NEW) -> Texas / **Nuevo Aztlan** (NEW branch: two focuses, war on ATE) / Tlaloc -> **The Last King Kneels** (NEW; +1 research slot) |
| 39-40 | Finale | **R'lyeh Rises** (NEW) -> *The Dreamer Wakes* / *The Priestess Reigns* / *Return to the Sea* (NEW) |

Full design: [SPEC.md](SPEC.md). Where the code differs from the spec, **the code wins**:
- The Final Ritual has no Walk prerequisite, only the OR over the three Act II ends.
- The Tide Turns South also opens from 2281.
- `mltd_texas_beaten`, `mltd_ai_ncr_beaten` and `mltd_ai_legion_beaten` also accept a recorded capitulation flag and
  MLT's subject.

## Files

**Mod** (every file except the new focus files already existed and was edited):
- `mod_folder/common/national_focus/mltd_act2_focus.txt` ... `mltd_act6_focus.txt`, `mltd_finale_focus.txt` - the story
  (shared focuses), new.
- `mod_folder/common/national_focus/Mirelurk Tribe (MLT) Focus.txt` - 7 listed roots replace the 10 old ones; the Final
  Ritual is at (0,3) from the Walk and reconverges Act II.
- `mod_folder/events/mltd_events.txt` - new events `mltd.30-31`, `40-41`, `50-52`, `60-62`, `70-74`.
- `mod_folder/common/ideas/mltd_ideas.txt` - `mltd_the_northern_waters`, `mltd_the_drowned_rangers`,
  `mltd_mars_beneath_the_waves`, `mltd_the_drowned_south` and the three ending ideas.
- `mod_folder/localisation/english/MLT/mltd_l_english.yml` - the round-27 section; about 80 dead keys removed.
- `mltd_scripted_triggers.txt` (`mltd_texas_beaten`), `mltd_scripted_effects.txt` (population in thousands),
  `mltd_on_actions.txt` (merged `on_capitulation` flags).
- AI: `ai_strategy_plans/mltd_MLT.txt` (the acts' order), `mltd_ai_triggers.txt` (section W: the `mltd_ai_may_*` hold on
  each story war focus), `ai_strategy/mltd_MLT.txt`, `scorers/country/mltd_ai_cult_target_scorer.txt`.
- Tools and docs: `build_telemetry.py`, `ai_run_report.py`, `mltd_telemetry_effects.txt` (rebuilt), `CONQUEST_PLAN.txt`
  (re-cut from the Walk to the end), `CLAUDE.md` (round 27 throughout), `README.md`.

**This folder** (repo-only, never ships):
- `SPEC.md` - the build spec every agent worked from.
- `staging/act2..finale/` - each act builder's `notes.md` and the raw parts that were merged into the shared files. The
  notes hold the per-act design reasoning and unverified points.
- `runs/build_results.json` - the builders' and reviewers' reports: each focus, each deleted id and where its effects
  went, loc keys, events.
- `runs/integrate_results.json` - the integrator's, the AI/plan agent's and the docs agent's reports, plus the 20
  review findings.
- `runs/review_findings.json` - the 20 findings on their own.
- `runs/fix_loc.py`, `fix_plan.py`, `fix_claude.py` - the fixer's edit scripts, all three already run.
- `runs/build_workflow.js`, `runs/integrate_workflow.js` - the two workflow scripts.
- `tools/grid.py` - the grid and pull-in resolver; `tools/check.py`, `tools/refcheck.py` - loc and reference checks.

## Review findings (20: 1 blocker, 6 major, 13 minor)

The fixer numbered them F1-F20 in the order script, progression, story. **Applied** (confirmed in the files):
- **F4, blocker:** the AI could take a story war focus early. Fixed by `mltd_ai_may_*` holds in each war focus's
  `available`, AI-only.
- **F5, major:** Act III's close could strand. Fixed with a 2281 fallback.
- **F1/F6, major:** population overflow. `mltd_national_population` / `mltd_controlled_population` are now summed from
  `state_population_k` and capped just under the variable ceiling.
- **F2/F19, minor:** the NCR-beaten tooltip.
- **F10-F18, F20:** every narrative and loc finding. The Final Ritual no longer promises the city rising; Act VI's
  opening fits Tlaloc's death; the Last King's order of kings; *Ph'nglui* in the finale; the Bone Dancers' "awake king";
  the Tide Turns South texts; the doubled "turns south"; payoff events that repeated their focus text; the order of
  Act V's river texts.
- **F8, F9 and part of F7:** plan text (the research-slot header, the Covenant and Hail setup).

**Not confirmed or still open:**
- **F7 (AI side):** no AI strategy builds a network in the Bone Dancers or points the cult operations at them, so an AI
  rarely meets *Hail the Drowned King*'s La Resistance gates. The plan now tells a human to do it. The AI needs a
  `mltd_ai_network_bdt`-style block, or a deviation line.
- **F3 (minor):** two act headers (`mltd_act3_focus.txt:13`, `mltd_act5_focus.txt:6`) still mention "the old conflict
  sub-trees". This is history in a comment; harmless.
- The fixer never returned its applied/rejected list, so apart from the spot checks above nothing is confirmed
  finding by finding.

## Open design questions (the user's call)

1. **The focus slot idles during the big wars.** Each act's close waits on its war: about 630 days in the NCR war, 320
   in the Legion's and 340 in Texas's, with only OWB's `lurk_` fillers to take. Options: side beads that open mid-war
   (occupation, integration of conquered land), or accept it.
2. **Inconsistent prices for merged beads.** Act II's four merged beads were lengthened; Acts V and VI kept their old
   lengths.
3. **AI-only holds in `available`.** The `mltd_ai_may_*` triggers restrict the AI rather than favour it, and follow the
   precedent of `mltd_ai_may_press_claims`. Confirm this passes the fair-play rule.
4. **Two research slots** (at When Shady Sands Falls and The Last King Kneels). They are big; the plan's tech has a
   deviation line rather than an AI `research_tech` for the fifth slot.
5. **CLAUDE.md's older Testing entries (rounds 13-25)** were edited by the docs agent so they no longer point at the
   removed sub-trees. Review the diff if you would rather keep them as history.
6. **Saves.** A game in progress inside a removed focus loses it; the rework is not save-compatible mid-sub-tree.

## Unverified until the game is run

These are collected in CLAUDE.md > Testing > Round 27:
- Listed shared roots whose prerequisite is a national focus (vanilla precedent: `belgium.txt:20`).
- `relative_position_id` across files.
- The national Final Ritual's OR prerequisite over shared focuses.
- `effect_tooltip` previews of event options in the Act IV and V closes (Act V's population preview may print +0).
- Two `mltd_brk_add_volunteer_size` calls making +6.
- Two `load_oob` calls in one effect (*Return to the Sea*).
- Whether `has_war_with = MLT` still holds on a capitulated country for the merged `on_capitulation` flags.
- Whether an AI still skips a planned focus whose `ai_will_do` reads 0.
- The a-umlaut in `mltd.72.a`.
- `[?ROOT.mltd_national_population|0]` in `mltd.73.d`.

## How to restart

**In a new Claude Code session** (a stopped workflow cannot be resumed across sessions):

1. Read this file, then [SPEC.md](SPEC.md) and CLAUDE.md > *The story acts*.
2. Re-run the checks: `python check_plan_sync.py`, `python ai_run_report.py --selftest`,
   `python story_rework/tools/grid.py` (it may need its paths adjusted), and a brace-balance pass over `mod_folder/`.
3. Optionally finish the fix pass. Give an agent `runs/review_findings.json` and the fix-stage prompt in
   `runs/integrate_workflow.js` (the last `agent(...)` call). Tell it most findings are already applied and it should
   verify each against the files before changing anything; the open ones are F7 (AI side) and F3.
4. Decide the open design questions above.
5. Launch the game and work through CLAUDE.md > Testing > Round 27. Read `error.log` for anything naming `mltd_act`,
   `mltd_finale`, `mltd.3x`-`mltd.7x`, `mltd_ai_may_` or the new ideas. Open MLT's focus tree and check that the spine
   renders top to bottom with the lines as in the table above.
6. When it holds, commit. The telemetry kill switch is still on; switch it off before any Workshop upload.

**If this same session is still open**, the stopped run can be resumed. Every stage but the fixer replays from cache,
and the fixer re-runs live against the already-fixed files:
`Workflow({scriptPath: "<runs/integrate_workflow.js, or its original path under ~/.claude/projects/...>", resumeFromRunId: "wf_1a0b70fa-71a"})`.
