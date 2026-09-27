# Rising Tide - round 28b: fixes from the user's play-test of round 28

Read `story_rework/SPEC_R28.md` (round 28's spec) and CLAUDE.md first. Round 28 is built and
integrated: Terms for the Citadel, the invitations' odds and refusal war goals, and the spoils
branches (`mltd_spoils_focus.txt`, **twelve** focuses in four branches - the builder added the
north's). The user then played it and asked for four changes. They apply to the whole mod, not just
the examples.

## 1. Rewards must scale to when they are taken

> "The Legion's Armouries ... doesn't scale sensibly into late game: by the point MLT can take this
> focus they will have thousands of support and infantry equipment ... they will also probably be
> transitioning away from an infantry equipment heavy army and towards amphibious creatures ... The
> Gulf Yards is also useless because it gives a flat amount ... focuses like these should have
> amounts sensible for when they might be taken or should give a modifier which naturally scales."

The rule, for **every** reward in the mod (focus, decision, event option), weighted towards the
late acts:

- **Prefer a modifier that scales** with the economy it lands in: a permanent or timed idea, or a
  dynamic modifier, carrying production efficiency (`production_factory_efficiency_gain_factor`,
  `production_factory_max_efficiency_factor`), output (`industrial_capacity_factory`,
  `industrial_capacity_dockyard`), construction speed (`production_speed_buildings_factor`, or a
  building-specific `production_speed_<building>_factor`), research speed, local resources, or an
  `equipment_bonus` on the archetypes MLT actually builds late (`amphibious_beast_equipment`,
  `mltd_deep_ones_equipment`, `mltd_star_spawn_equipment` - see `continuous_mltd_spawning_pools` in
  `mltd_ideas.txt`). Check every modifier in vanilla `documentation/modifiers_documentation.md`.
- **Or size a one-off to its moment**, using `CONQUEST_PLAN.txt`'s snapshots for when a player
  takes the focus (about 60 military factories at the NCR's fall, ~110 by 2285): a gift that
  matters is a real fraction of a year's output, not a few hundred rifles. Pay equipment in what
  MLT fields at that point. From Act IV on that is creature equipment; an **archetype**
  (`amphibious_beast_equipment`) gives MLT its best unlocked variant, as the Call for Equipment
  decision does.
- **Thefts** (the story acts' war focuses) follow the same rule: a flat 600-800 rifles in 2286 is
  noise. Scale them to the moment, or turn them into something that scales; keep the
  `has_equipment` guards and the no-`producer` removal (CLAUDE.md > *Theft without producer*).
- Early rewards (Acts I-II, before ~2278) are already sized for their time; leave them unless a
  reward is plainly out of scale.
- Every number that moves and also appears in loc changes in both places (CLAUDE.md > *Numbers in
  two places*), and every reward `CONQUEST_PLAN.txt` quotes is updated by the AI/plan pass.

## 2. Tall icons need room

> "The Final Ritual and The Last King Kneels focus icons are 2y tall so their focuses need
> additional spacing, more so than typical focuses."

Measured icon textures (a normal focus icon is about 92x90; a row is about 130 px): The Final
Ritual's `GFX_goal_CHC_cultists` is **266x253** (nearly three rows and three columns); The Last
King Kneels' `GFX_goal_MIN_fallen_kingdom` is **164x146**. Both get an empty row above and below,
and nothing on the rows next to them within a column of the spine. The new rows (the spine stays x
= 15):

- Rows 19-23: Call, the Grand Ritual, the Walk, Act II heads (13/15/17), Act II ends (13/15/17) -
  unchanged
- Row 24: **empty**
- Row 25: `mltd_the_final_ritual` - was 24: `y = 3` -> `y = 4` of the Walk (override, CRLF)
- Row 26: **empty**
- Row 27: Act III: Terms (10), The Tide-Wall (12), the Covenant (14), Hail (16), Drown the Dance
  (18) - was 25: absolute `y = 25` -> `27`
- Row 28: `mltd_the_tide_turns_south` - was 26: absolute `y = 26` -> `28`; everything that chains
  from it moves with it
- Rows 29-36: Act IV (29-32) and Act V (33-36) - +2, automatically (relative to The Tide Turns
  South)
- Rows 37-39: Act VI's chapter, heads and wars - +2, automatically
- Row 40: **empty**
- Row 41: `mltd_the_last_king_kneels` - was 38: `(0,3)` -> `(0,4)` of The Southern Deep
- Row 42: **empty**
- Row 43: `mltd_rlyeh_rises` - was 39: `(0,1)` -> `(0,2)` of The Last King Kneels
- Row 44: the endings (13/15/17) - follow R'lyeh Rises

The spoils branches are relative to their closes, so they move with them; check that none of their
cells lands on the empty rows next to the two tall icons within x 13-17 (they sit at x = 20, so
they should not). The Grand Ritual (152x139) and Salt on the Caravan Roads (149x154) are tall too,
but the user did not ask for them and their neighbouring cells within reach are empty or were
accepted; leave them, and say so in the return.

## 3. Every effect shows

> "The Canals Run Salt focus shows no effect. If the effect requires some conditions to be
> calculated that will only be present later it should use a custom tooltip, else it should show
> the effect (this rule should be applied generally across everything in the mod). The focus text
> also appears to be grammatically wrong and reads poorly and should be changed."

The rule, for **every** `completion_reward`, decision `complete_effect` / `remove_effect` / mission
`timeout_effect`, and event option in the mod:

- A player must see what they will get **before** they take it.
- An effect whose tooltip the engine draws correctly now (a plain `add_ideas`,
  `add_political_power`, an `if` whose limit already holds) stays as it is.
- An effect the preview cannot show gets a `custom_effect_tooltip` that says what it will do, and
  the effect itself goes in `hidden_effect`. That covers:
  - `every_*_state` / `every_*_country` with a `limit` no state or country passes yet (which
    previews as nothing);
  - an `if` whose limit reads a condition that will only hold later;
  - a random pick;
  - a value computed at run time.
- The tooltip must be true in every branch: where an `if` picks between outcomes, say what each
  gives.
- `The Canals Run Salt` is the reported case; find every other one.

Also rewrite The Canals Run Salt's name and description so they read well (the user found the text
ungrammatical), keeping the mod's voice and the house loc rules.

## 4. War and alliance pairs sit side by side and exclude each other

> "The focus pairs which either declare war on or try to ally nations (e.g. Hail the Drowned King
> and Drown the Dance) should be adjacent to each other and should be mutually exclusive."

In Act III (row 27 after section 2):

- **Terms for the Citadel (10) and The Tide-Wall (12)**, both aimed at the Brotherhood in
  Washington, and **Hail the Drowned King (16) and Drown the Dance (18)**, both aimed at the Bone
  Dancers. Each pair is already two columns apart, the house spacing. The Covenant (14) has no war
  twin, since the Broken Coast is courted and never fought.
- Make each pair **`mutually_exclusive` both ways**. Until now Hail -> Drown was one-sided (round
  24): a refused invitation used to strand the war branch. Round 28 gives every refused invitation
  an expiring war goal, so the refusal no longer strands anything, and the pair can exclude both
  ways as the user asks.
- The Tide-Wall's round-28 flag gate (`NOT = { has_country_flag = mltd_wbh_alliance }`) becomes
  redundant: drop it, or keep it only if it still guards something the exclusion does not.
- The **cross-nation** exclusion stays flag-based, because the user asked for it only on success:
  an accepted Terms closes the Covenant, and an accepted Covenant closes Terms. Do not turn it into
  `mutually_exclusive`.
- Act III's close stays reachable: its OR names all five Act III focuses, and every pair's refusal
  path still completes a focus.
- Check the AI side. Section W's holds, and the plans' order, must still let an AI through Act III
  with the new exclusions: an AI that takes an invitation now forfeits its war twin, and the other
  way round.

## Files and ownership (parallel agents)

Write only your own files; put shared-file content in your staging folder
`C:\Users\jonat\AppData\Local\Temp\claude\c--Users-jonat-Documents-rising-tide\71877056-fecf-418a-a4f4-50b7c28bba62\scratchpad\r28b\<area>\`,
with the same file names as round 28 (`loc.yml`, `ideas.txt`, `effects.txt`, `triggers.txt`,
`events.txt`, `scripted_loc.txt`, `notes.md`).

- `early`: the override `Mirelurk Tribe (MLT) Focus.txt` (the Final Ritual's `y`; the tooltip audit
  of every Rising Tide focus in it, the Kingdom included - never OWB's own focuses),
  `mltd_act2_focus.txt`, `mltd_act3_focus.txt`
- `late`: `mltd_act4_focus.txt`, `mltd_act5_focus.txt`, `mltd_act6_focus.txt`,
  `mltd_finale_focus.txt`
- `spoils`: `mltd_spoils_focus.txt`
- `rest`: `mltd_events.txt`, `mltd_decisions.txt`, `mltd_operations.txt`,
  `mltd_scripted_effects.txt` (effects whose tooltips the focuses call),
  `common/scripted_guis/mltd_wet_market_gui.txt`

Loc and ideas always go through staging. Say in your return which existing keys you replace.

## Return

JSON: the files you changed; every reward you rescaled (focus or event, what it gave, what it gives
now, why that size); every tooltip you added (where, what it says); position changes; loc keys new
or replaced; literals now in two places; what the AI/plan and docs passes must update; unverified
constructs.
