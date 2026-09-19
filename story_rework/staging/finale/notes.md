# Finale - "R'lyeh Rises" - integrator notes

## Files
- `mod_folder/common/national_focus/mltd_finale_focus.txt` (new; LF, no BOM, tabs): 4 shared focuses.
- `events.txt` -> append to `mod_folder/events/mltd_events.txt` (mltd.70-74; no namespace line).
- `ideas.txt` -> paste inside `ideas = { country = { ... } }` of `mod_folder/common/ideas/mltd_ideas.txt`
  (indented two tabs, like the existing country ideas).
- `loc.yml` -> append to `mod_folder/localisation/english/MLT/mltd_l_english.yml`. All keys are NEW; no existing key is
  replaced. `mltd.72.a` contains a UTF-8 `ä` ("Iä!", from *The Dunwich Horror*, 1929) - keep the file UTF-8 with BOM.
- No `triggers.txt` / `effects.txt`: the finale calls only existing definitions (`mltd_spawn_leviathan`,
  `mltd_leviathan_can_surface`, loc `mltd_newline_tt`).

## Tree
- Pull-in: nothing to list in the override. `mltd_rlyeh_rises` has `prerequisite = mltd_the_last_king_kneels` (Act VI's
  shared close), so the finale reaches the listed Act III roots through shared prerequisites only. If Act VI renames its
  close, change the prerequisite and the `relative_position_id` here.
- Cells, assuming The Last King Kneels at (15,38): R'lyeh Rises (15,39); The Dreamer Wakes (13,40); The Priestess
  Reigns (15,40); Return to the Sea (17,40). The endings each declare `mutually_exclusive` on both others.
- Every finale focus has `cancel_if_invalid = no` + `continue_if_invalid = yes`; none has an intel gate.

## Numbers (for CLAUDE.md's "numbers in several places")
- The 300-state gate is `num_of_controlled_states > 299` in `mltd_rlyeh_rises` and the literal 300 in
  `mltd_rlyeh_rises_states_tt` - change both together. It matches CONQUEST_PLAN's 2285-12 snapshot (300-400 states).
- The finale's +15 victory points in M'lyeh (province 1983) stack on the Kingdom's +15 (30 in all, plus OWB's base).
- "Two" Leviathans: the two `mltd_spawn_leviathan` calls in `mltd_ending_return_to_the_sea` and the prose of
  `mltd_return_to_the_sea_leviathans_tt`.
- Ending ideas: Dreamer +15 % attack, +10 % defence, +10 % war support, -5 % stability; Priestess +20 % stability,
  +20 % political power, -10 % consumer goods; Return +20 % monthly population (`monthly_population = 0.2`, OWB's
  scale), +10 % recruitable population (`conscription_factor`, as the Gift of the Brood) and two Leviathans at Mireport.
  All shown natively by `add_ideas`; no loc repeats them.

## Plan and AI (not done here - the integrator's job)
- `CONQUEST_PLAN.txt` needs the finale: `mltd_rlyeh_rises` (70 days, 300 controlled states) and one ending. The AI's
  weights favour The Dreamer Wakes (ai_will_do 3 / 2 / 1); if the plan picks another, either add a matching
  `focus_factors` / `ai_national_focuses` entry in the late plan (`common/ai_strategy_plans/mltd_MLT.txt`) or write a
  `# AI deviation: focus <id> - <why>` line.
- The late-game plan's `ai_national_focuses` should list `mltd_rlyeh_rises` and the chosen ending after Act VI's close,
  or `check_plan_sync.py` will flag the plan's finale lines as having no AI counterpart.
- The telemetry needs the new focuses' first-seen FOCUS lines, or `check_plan_sync.py` fails with "telemetry: focus ...
  is not polled". **A plain rerun of `build_telemetry.py` will not work - edit it first.** Line 140 asserts that the
  pulled-in shared focuses come from exactly `{'Shared Oregon Coastals Focus.txt', 'mltd_conflicts_focus.txt'}`, so
  once the act and finale files pull focuses in, the assertion fails and the script aborts without writing anything.
  Change it as follows:
  - Line 140: accept `Shared Oregon Coastals Focus.txt` plus `mltd_act2_focus.txt` ... `mltd_act6_focus.txt` and
    `mltd_finale_focus.txt`, with `mltd_conflicts_focus.txt` gone once it is deleted.
  - Lines 142-143: build `conflicts` (better renamed, e.g. `story`) by joining the per-act groups in act order, finale
    last.
  - `gen_focus`'s group title (line 333), the FOCUS comment in the template (line 578) and the summary print (line 998).
  Then run `python build_telemetry.py` and `python check_plan_sync.py`.
- Nothing is AI-only: all four rewards apply to human and AI alike.

## CLAUDE.md
- Event ids 70-74 are now taken (Naming conventions: "1-27 taken" -> add 70-74 once the acts land).
- Layout table: new file `common/national_focus/mltd_finale_focus.txt`.
- The global flag `mltd_rlyeh_risen` is set (hidden) by R'lyeh Rises and read by nothing yet - a hook for later content
  (flavour events, other countries' reactions, the main-menu or news). Delete it if nothing ever uses it.

## Nothing became unused
- The finale merges and deletes nothing, so no key, effect or trigger is freed.

## Optional, not done (outside the spec)
- Renaming the capital to R'lyeh on completion (`358 = { set_state_name = ... set_province_name = { id = 1983 name = ... } }`,
  as the Kingdom does with `STATE_358_MLT` / `VICTORY_POINTS_1983_MLT`) would need two new loc keys. The loc already
  frames it: "The tribe had called its city M'lyeh ... the name the stones themselves remember: R'lyeh". The country
  itself keeps OWB's cosmetic name, M'lyeh, which `mltd.71.d` reads through `[MLT.GetNameDef]`.
- `mltd.70` does not set `mltd_flavour_cooldown`, so a flavour event (mltd.9-19) can land in the same weeks as the
  finale, as it can for every beat after the Kingdom.

## The population variables overflow by the finale (outside the finale's files - the integrator's call)
- `mltd.73.d` no longer prints `[?ROOT.mltd_national_population|0]`. It now reads "its census-takers have run out of
  numbers for the souls beneath the tide". The reason: `mltd_update_national_population` sums raw `state_population`,
  and script variables wrap negative above 2,147,483.647 (CLAUDE.md > Gotchas). The finale needs 300 controlled states,
  and CONQUEST_PLAN's 2285-12 snapshot puts MLT at 3-4M people there, so the printed figure would most likely have been
  a negative number. The telemetry already says as much (`mltd_telemetry_effects.txt:41-42`, which is why it keeps its
  own `mltd_tm_pop_k`). The finale reads neither variable now.
- The same wrap breaks the late readers of both population variables. Past ~2.1M people each reads negative, so every
  `<` test passes and every `>` test fails:
  - `mltd_decisions.txt:452` (the Leviathan summon's AI guard) and `:584` (the Offering of the Tides' guard) test
    `mltd_national_population < 300000` after The Final Ritual. They switch the AI off for good.
  - `mltd_decisions.txt:426` is the Leviathan summon's `available` gate, `mltd_controlled_population > 47999`. It
    greys the decision out for a **human** as well, and `:438` blocks the AI.
  - The Deep Ones and Star Spawn gates (`:314`, `:371`) are only reachable before the unit becomes trainable, so the
    wrap probably never reaches them.
  - Suggested fix: sum `state_population_k` into `mltd_national_population_k` / `mltd_controlled_population_k` beside
    the raw sums (OWB `exodus_effects.txt:385` idiom), and move the late tests to them (`< 300`, `> 47`). Keep the raw
    variables for the early ritual gates at 100,000 / 200,000, which are far below the ceiling. Printing a finale figure
    would then be `[?ROOT.mltd_national_population_k|0] thousand`.

## Unverified
- Two `load_oob` calls in one effect on the same day (the second `mltd_spawn_leviathan`): each should load its own task
  force at Mireport, both named "Leviathan", as repeated summons already do on different days.
- `add_victory_points` on province 1983 if MLT no longer controls M'lyeh when the focus completes (the Kingdom's use was
  always on MLT's own capital).
- How the AI divides its choice among three mutually exclusive focuses with ai_will_do 3 / 2 / 1 (weighted pick, or
  always the highest).
- The `ä` glyph in the event option font (OWB/vanilla fonts carry Latin-1, so it should render).
