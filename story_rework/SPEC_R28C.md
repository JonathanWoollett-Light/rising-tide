# Rising Tide - round 28c: the user's second set of play-test notes

Read `SPEC_R28.md` (round 28), then `SPEC_R28B.md` (round 28b), then this file. **Where this file
differs, it wins.** Round 28b's sections 1 (rewards that scale) and 3 (every effect shows) stand
unchanged. This file replaces its section 2 (spacing) and section 4 (pairs), and restructures the
spoils branches.

## State of the repo when you start

Round 28b was stopped part-way: see `story_rework/runs/r28b_partial_results.json`.

- **Finished** (their edits are on disk, their staging folders are in
  `...\scratchpad\r28b\<area>\`): the builders of `early`, `spoils` and `rest`.
- **Stopped mid-way:** `late`. Its edits may be partly on disk; its staging folder is partial.
- **Nothing was integrated.** Every staging folder still holds its loc, ideas and scripted loc,
  unmerged.
- `r28b\early\backup\` holds pre-28b copies of the override, `mltd_act2_focus.txt` and
  `mltd_act3_focus.txt`.

Keep using the same staging folder for your area (`r28b\<area>\`). Update it in place so that at
the end it matches your files exactly: an integrator merges it once.

## The user's notes

> - The Drowned Covenant focus needs its mutually exclusive counterpart that declares war on the
>   Broken Coast.
> - The Final Ritual requires that focuses are at least 2 spaces above it, but this doesn't apply
>   below: focuses should only be 1 space below it. The same is true for The Last King Kneels.
> - The economic/buff focuses being on the side of the main line feel awkward; they should be
>   integrated into the main line, by having each group be 2 economic focuses (instead of 3), on
>   either side of the next narrative focus - e.g. The Scribes' Vaults on the left of A Mole in
>   Shady Sands and The Drowned Sound on its right. Where 2 is not enough weight, 4 can be used, 2
>   to the left and 2 to the right (4 for the NCR, the first true superpower MLT fights).

## 1. The Broken Coast's war twin

A new Act III focus, `mltd_brk_the_coast_goes_under` ("The Coast Goes Under" - rename it if a
better title fits the mod's voice). It declares war on the Broken Coast, as Drown the Dance does on
the Bone Dancers.

- **Declaration:** `declare_war_on` with `type = annex_everything`, against BRK while it exists and
  is neither at war with MLT nor MLT's subject; `will_lead_to_war_with = BRK`.

- **Payoff:** BRK loses stability and war support, and MLT gains army XP, sized like Drown the
  Dance's. When BRK is gone or MLT's subject the focus pays political power instead, so Act III
  never strands.

- **Cost:** the war focuses' 45-49 days.

- **Exclusion:** `mutually_exclusive` with `mltd_brk_the_drowned_covenant`, **both ways**.

- **Placement:** a **listed root**, since its prerequisite is the national `mltd_the_final_ritual`.
  The integrator adds the override line. Cell in the table below.

- **For an AI:** a hold in `available`, `mltd_ai_may_drown_the_coast`, added to section W of
  `mltd_ai_triggers.txt` through staging. It keeps the focus unavailable to an AI:

  - while MLT courts the Broken Coast (`mltd_ai_courting_brk`). The AI courts BRK on purpose: run
    3's AI declared on it and lost;
  - while the army is not ready;
  - while MLT is losing a war;
  - while BRK is not a safe target.

  Model it on `mltd_ai_may_drown_the_dance`. A refused Covenant already hands MLT an expiring war
  goal on BRK (round 28), so a human who wants that war has two ways to it, and an AI has one once
  the courtship ends.

- **Rules that change:**

  - CLAUDE.md's and the plan's "the Broken Coast is courted and never fought" becomes "courted
    first; fought only by choice".
  - The Tide Turns South's OR gains this focus, so it names all six Act III focuses.
  - The loc gets a name, a description with its war line, and an odds-free text: it is a war, not
    an invitation.

## 2. The final layout

The tall icons (The Final Ritual's 266x253, The Last King Kneels' 164x146) grow **upward**. Each
needs one empty row above it, and the next focus directly below it. The spoils focuses move off the
right-hand column (section 3) onto the spine's rows, beside the chapter that follows their act's
close. Every cell, with the spine at x = 15:

| Row   | x = 11     | x = 13          | x = 15                    | x = 17        | x = 19     |
| ----- | ---------- | --------------- | ------------------------- | ------------- | ---------- |
| 19-21 |            |                 | Call, Grand Ritual, Walk  |               |            |
| 22    |            | Eyes            | Salt (BRK)                | Bone Shore    |            |
| 23    |            | Knights         | Sail North                | Dancers       |            |
| 24    |            |                 | *empty*                   |               |            |
| 25    |            |                 | **The Final Ritual**      |               |            |
| 26    |            |                 |                           |               |            |
| 27    |            |                 | The Tide Turns South      |               |            |
| 28    |            | Scribes' Vaults | **A Mole in Shady Sands** | Drowned Sound |            |
| 29    |            | Delegates       | Sleepers                  | Caravan Roads |            |
| 30    |            |                 | The Turbines Sing         |               |            |
| 31    |            |                 | When Shady Sands Falls    |               |            |
| 32    | California | California      | **Mars in the Water**     | California    | California |

Notes:

- Rows 19-21: unchanged
- Row 22: Act II heads, unchanged
- Row 23: Act II ends, unchanged
- Row 24: the Final Ritual's room above
- Row 25: `y = 4` of the Walk
- Row 26: **Act III, six focuses - see below**
- Row 27: absolute (15,27)
- Row 28: the north's two spoils flank Act IV's chapter
- Row 32: the NCR's four spoils flank Act V's chapter

From row 33 on, no focus sits at x = 11 or x = 19:

| Row | x = 13                | x = 15                   | x = 17                |
| --- | --------------------- | ------------------------ | --------------------- |
| 33  | 12 / 14 (Act V heads) |                          | 16 / 18 (Act V heads) |
| 34  | 12 / 14 (wars)        |                          | 16 / 18 (wars)        |
| 35  |                       | When the Legion Breaks   |                       |
| 36  | interior              | **The Southern Deep**    | interior              |
| 37  | All Waters            | Feathered Tide           | Iron God              |
| 38  | Black Water           | Serpent Drowns           | Drowned God           |
| 39  |                       | *empty*                  |                       |
| 40  |                       | **The Last King Kneels** |                       |
| 41  | south                 | **R'lyeh Rises**         | south                 |
| 42  | Dreamer               | Priestess                | Return                |

Notes:

- Row 33: Act V heads at x 12, 14, 16, 18
- Row 36: the interior's two spoils flank Act VI's chapter
- Row 37: Act VI heads
- Row 38: Act VI wars
- Row 39: The Last King Kneels' room above
- Row 40: `(0,4)` of The Southern Deep
- Row 41: `(0,1)` of The Last King Kneels; the south's two spoils flank it
- Row 42: the endings

**Act III (row 26), six focuses in three pairs**, two columns apart, centred on the spine:

| x   | focus                 | pair |
| --- | --------------------- | ---- |
| 10  | Terms for the Citadel | WBH  |
| 12  | The Tide-Wall         | WBH  |
| 14  | The Drowned Covenant  | BRK  |
| 16  | The Coast Goes Under  | BRK  |
| 18  | Hail the Drowned King | BDT  |
| 20  | Drown the Dance       | BDT  |

- Each pair is `mutually_exclusive` both ways; the cross-nation success-only flags of round 28
  stay.
- All six are listed roots at absolute cells.
- The Tide Turns South's OR names all six.

Positions: the listed roots and The Tide Turns South are absolute; everything else is
`relative_position_id` to a shared focus, as round 27's rule requires. A spoils focus takes its
flanking chapter as its anchor, e.g. The Scribes' Vaults at `(-2,0)` of A Mole in Shady Sands, but
its **prerequisite** is the previous close, so it gates nothing. The rows follow from the anchors:
A Mole in Shady Sands `(0,1)` of The Tide Turns South, and so on, as today.

## 3. The spoils, restructured

Twelve focuses in four vertical chains become **ten**: two for the north, **four for the NCR's
California**, two for the interior, two for the south. None is chained to another. They sit on the
spine's rows (table above):

- **Prerequisite:** the previous act's close - `mltd_the_tide_turns_south`,
  `mltd_when_shady_sands_falls`, `mltd_when_the_legion_breaks` or `mltd_the_last_king_kneels`. They
  draw a line from that close, the same line their flanking chapter draws.
- **Gating:** no spine focus names them in a prerequisite, so they gate nothing.
- **Gates:** land actually held, as today. The California four may split their gates across the
  state's parts.
- **Payoffs:** round 28b's rule. They scale with the economy they land in, or are sized to their
  moment. Merge the best of each old chain of three into its new focuses: the builder in round 28b
  already rescaled them and fixed their tooltips; keep that work.
  - At most one permanent idea per group; California's four may carry two.
  - Drop the payoffs that no longer have a place, and remove their loc and ideas.
  - The Canals Run Salt's name and description are rewritten, as 28b asked; keep the rewrite
    wherever it lands.
- **Ids:** keep the old ids of the focuses you keep, and delete the rest. The plan, the AI and the
  telemetry name them; the later passes fix those.
- **Icons:** the file's header comment is rewritten for the new layout. Check every spoils icon's
  height against its neighbours - no tall icon (over about 130 px) may sit directly below another
  focus in its column.

## Areas and files (parallel agents, as round 28b)

- `early`
  - Owns: the override (Rising Tide lines only, CRLF), `mltd_act2_focus.txt`, `mltd_act3_focus.txt`
  - This round: the Final Ritual's row (`y = 4` of the Walk); Act III's six cells and three two-way
    pairs, the new war twin, The Tide Turns South at (15,27) with its six-way OR; finish 28b's
    tooltip and reward audit of these files
- `late`
  - Owns: `mltd_act4_focus.txt` ... `mltd_finale_focus.txt`
  - This round: The Last King Kneels `(0,4)` of The Southern Deep, R'lyeh Rises `(0,1)` of it;
    finish 28b's reward scaling and tooltip audit (its builder was stopped mid-way - read the files
    as they are)
- `spoils`
  - Owns: `mltd_spoils_focus.txt`
  - This round: section 3
- `rest`
  - Owns: `mltd_events.txt`, `mltd_decisions.txt`, `mltd_operations.txt`,
    `mltd_scripted_effects.txt`, the Wet Market GUI
  - This round: its 28b build is finished; audit it against 28b's rules, and complete anything the
    new focuses need from it (none expected)

## Return

As round 28b's, plus: every cell you set, and every id you deleted.
