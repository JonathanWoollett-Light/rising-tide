# Handoff: round 27, the story-act rework (second pause, 2026-09-19)

Read this first. [HANDOFF.md](HANDOFF.md) covers the first pause: what the rework is, which files it touched, the first
review's 20 findings (F1-F20) and the open design questions.

## Where things stand

The rework is **built and integrated, and is on its second review-and-fix pass. It has not been tested in game and is
not committed** (`master`, on top of `11b78e1`).

The second pass is the workflow `story-acts-finish` (run `wf_9e6e1b83-680`; its script is saved as
[runs/finish_workflow.js](runs/finish_workflow.js)). Every step finished except the last:

| Step | Done | Result |
| --- | --- | --- |
| **Confirm**: one agent per F1-F20 | yes | 18 resolved, 2 partly (F9, F18). Six resolved ones got small side problems from their fixes (F1, F4, F7, F10, F11, F13), mostly a wrong citation or a wording slip |
| **Review**: four fresh lenses (script, progression, docs, story) on the state after the first fixer | yes | 30 new findings |
| **Verify**: two refutation votes per new finding | yes | 26 survive (1 major, 25 minor); 4 refuted |
| **Fix**: one agent applies the 8 open earlier items and the 26 new ones | **stopped partway** | see below |

What the stopped fixer had already changed:
- `mltd_ai_triggers.txt` section W (the `mltd_ai_may_*` holds), through its helper `runs/finish_fixer/edit_triggers.py`.
- Comments in `mltd_act3_focus.txt`, `mltd_act4_focus.txt` and `mltd_act5_focus.txt`.
- `ai_strategy/mltd_MLT.txt`: an AI network in the Bone Dancers for Hail the Drowned King's gates, the old F7 gap.
- A comment in `ai_strategy_plans/mltd_MLT.txt`.
- The OWB `exodus_effects.txt` line citation, in `mltd_scripted_effects.txt` and CLAUDE.md.

It had **not** started the loc, `CONQUEST_PLAN.txt` or CLAUDE.md items (most of the list).

The repo was checked after the stop and is consistent:

| Check | Result |
| --- | --- |
| `check_plan_sync.py` | OK |
| `ai_run_report.py --selftest` | 62 of 62 |
| `build_telemetry.py` | rebuilds |
| Brace balance, every `.txt` under `mod_folder/` | balanced |
| `mltd_l_english.yml` | BOM, LF, valid UTF-8 |
| `tools/grid.py` | 9 listed roots found; exactly the 39 story focuses pulled in; no overlaps |

## What is left: 34 items

Everything is in [runs/finish_fix_input.json](runs/finish_fix_input.json): exactly what the fixer was given, with each
new finding's verifiers' reasons. Where a verifier said the problem is real but the proposed fix is wrong, follow the
verifier's fix. Some items are already done (list above), so check each against the files before changing anything.
All agents' full results are in [runs/finish_results.json](runs/finish_results.json).
[tools/finish_state.py](tools/finish_state.py) rebuilt both from the journal and prints the summary.

**8 earlier items still open:**
- F9 (partly): the plan's operative schedule the fix added is impossible with MLT's slots.
- F18 (partly): payoff events still repeat their focus text.
- Six small side problems from earlier fixes (F1, F4, F7, F10, F11, F13): citations, a doc contradiction, and "his"
  for the Dreamer.

**26 new, by lens:**
- **Script (2):**
  - The Turbines Sing's hold lifts on a bare `has_capitulated`.
  - Section W's "Muttfruit through a `focus_factors` 0" rationale misreads run 8.
- **Progression (4):**
  - Only the Nuevo Aztlán hold keeps the "no war on a stronger country" rule.
  - The same Muttfruit claim, in the plan header.
  - The docs lean on `ai_will_do` deciding among listed focuses.
  - F7 is wider than the handoff said: both invitations' token gates.
- **Docs (13), all CLAUDE.md, mostly one-line corrections:**
  - "Each chapter fires an MLT event" is not true of Act IV's chapter.
  - The Project summary's "no story focus has an intelligence gate".
  - The "each act is a chapter, fan and close" wording.
  - The `ai_will_do` claims.
  - `effect_tooltip` is not actually unverified.
  - The `exodus_effects` citation.
  - Stale override line numbers (`:1161`, and others).
  - The Bone Dancers' courtship condition.
  - "four merged beads" (one is a head).
  - The coverage range 0.1-0.3 (now 0.25 and 0.3).
  - `nf_mlt` deletes 36 lines, not 38, and is not the only override that deletes.
  - The stale checked Workshop `picture=` item.
  - The first handoff's counts.
- **Story (7):**
  - Major: four of the five act payoffs still narrate their own event in the focus description.
  - `mltd.40.d` makes M'lulu the sleeper again.
  - The endings re-stage the finale.
  - The Tlaloc descriptions still treat him as alive.
  - `mltd.52.d` denies a Legion civil-war case OWB can produce.
  - `mltd.31.d` states a conquest the close does not require.
  - The Nuevo Aztlán fallback tooltips also print when ATE is MLT's subject.

## How to restart

1. **Check the state.** Run `python check_plan_sync.py`, `python ai_run_report.py --selftest` and
   `python story_rework/tools/grid.py`. They should read as the table above.
2. **Finish the fix pass.** Give one agent `runs/finish_fix_input.json` and the fixer prompt: the last `agent(...)` call
   in `runs/finish_workflow.js`, which also lists the checks to run afterwards. Tell it that some items are done (see
   *What the stopped fixer had already changed*) and to verify each first. Items that are design decisions stay
   untouched and are listed as "user decision". In the same session, re-running the script with
   `resumeFromRunId: "wf_9e6e1b83-680"` replays every finished agent from cache and runs only the fixer.
3. **Optional:** one more short review of the fixer's own changes, the way this pass reviewed the first fixer's. Two
   rounds have each found a handful of new minor issues, so expect a few more, mostly wording.
4. **Decide the open design questions** in HANDOFF.md. Still open: the idle focus slot during the great wars, the prices
   of merged beads, whether the AI-only holds pass the fair-play rule, the two research slots, the rewritten older
   Testing entries, and save compatibility.
5. **Play-test** per CLAUDE.md > Testing > Round 27, then commit. Switch the telemetry kill switch off before any
   Workshop upload.
