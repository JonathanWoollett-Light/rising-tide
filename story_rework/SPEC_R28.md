# Rising Tide - round 28: the invitations' odds, the Washington alliance, and the spoils branches

Repo `C:\Users\jonat\Documents\rising-tide`; mod under `mod_folder/`. OWB
`C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196`; vanilla
`C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV` (its `documentation/*.md` lists
every effect, trigger and modifier). Read CLAUDE.md first - *The story acts*, *Events*,
*Localisation: functions, not names*, *MLT's AI*, *Gotchas* - and follow its conventions exactly.
Round 27's structure stands; this round adds to it.

## What the user asked for

1. The Broken Coast's Covenant: a **historical** AI always accepts; an **unhistorical** AI accepts
   half the time.
2. A new focus that offers an **alliance to the Brotherhood in Washington**. If it succeeds it
   rules out allying the Broken Coast. The Washington Brotherhood (`WBH`) never accepts on
   historical and accepts half the time on unhistorical; the Northwestern Brotherhood (`TCA`, the
   user's "Northeastern") never accepts on historical and accepts a tenth of the time on
   unhistorical.
3. Every focus whose payoff depends on an AI's answer says in its description how likely that
   answer is.
4. A refused offer leaves MLT worse off than simply fighting: the offer costs more days than the
   war focus, pays no war bonus, and on refusal leaves only a **war goal that expires**.
5. **Optional** economy / buff / tech focuses that do not gate the spine and that pay off conquered
   land.

## 1. The three invitations' odds (`mod_folder/events/mltd_events.txt`)

The answer is an `ai_chance` on the invited country's event options. Use OWB's idiom
(`events/nevada_pact_events.txt:15-22`): a `modifier` with `is_historical_focus_on = yes` inside
`ai_chance`. Weights are relative, so set the refusal's weight rather than piling factors on the
acceptance.

- `mltd.21` the Drowned Covenant
  - Who answers: BRK
  - Historical: always accepts
  - Unhistorical: 50 %
  - How: accept `base = 50`; refuse `base = 50` with
    `modifier = { is_historical_focus_on = yes factor = 0 }`
- `mltd.24` Hail the Drowned King
  - Who answers: BDT
  - Historical: always accepts
  - Unhistorical: always accepts
  - How: unchanged (accept 100 / refuse 0); it is the Odious King's own crowning that gates it
- `mltd.32` Terms for the Citadel (NEW)
  - Who answers: the Brotherhood in Washington
  - Historical: never accepts
  - Unhistorical: WBH 50 %, TCA 10 %
  - How: accept `base = 0`,
    `modifier = { NOT = { is_historical_focus_on = yes } tag = WBH add = 50 }`,
    `modifier = { NOT = { is_historical_focus_on = yes } tag = TCA add = 10 }`; refuse `base = 50`,
    `modifier = { NOT = { is_historical_focus_on = yes } tag = TCA add = 40 }` (so 10 against 90)

A human on the other side always chooses freely; `ai_chance` only weights an AI's pick.

## 2. Terms for the Citadel - the Washington alliance

A third invitation, in Act III beside the Tide-Wall. The Brotherhood is the one power in the north
that would sooner die than kneel to a mirelurk queen, so the offer is a long shot the player may
still want to take.

- Id: `mltd_wbh_terms_for_the_citadel`
- File: `mod_folder/common/national_focus/mltd_act3_focus.txt`
- Cell: **(10,25) absolute**, two columns left of The Tide-Wall (12,25); the cell is free
- Listed root: **yes** - its prerequisite is the national `mltd_the_final_ritual`, so the override
  must list it (see *Pull-in* in CLAUDE.md). The integrator adds the line
- Cost: **63** - longer than The Tide-Wall's 45, deliberately (ask 4)
- Prerequisite: `mltd_the_final_ritual`
- `available`: a Brotherhood holds Washington (`any_country = { mltd_wbh_brotherhood = yes ... }`),
  at peace with MLT, not MLT's subject, in no faction; MLT in no faction or leading one;
  `has_completed_focus = mltd_wbh_eyes_in_the_sound` (as the other two invitations name their Act
  II head, which draws no line); `NOT = { has_country_flag = mltd_brk_covenant_joined }` (ask 2 -
  see below); and, for an AI, the hold `mltd_ai_may_offer_the_citadel`
- `completion_reward`: fires `mltd.32` to the Brotherhood (`mltd_wbh_brotherhood`), as the Covenant
  fires `mltd.21` to BRK; the odds line and the refusal warning are `custom_effect_tooltip`s
- `ai_will_do`: `factor = 1` (an AI's real path is the hold below)

Exclusivity (ask 2) is by **flag, not `mutually_exclusive`**, because the ask is "if successful": a
refused offer must leave the other door open.

- `mltd_wbh_join_the_covenant` (a new scripted effect, modelled on `mltd_brk_join_the_covenant`)
  sets `mltd_wbh_alliance` on MLT when the Brotherhood accepts.
- `mltd_brk_join_the_covenant` sets `mltd_brk_covenant_joined` on MLT when BRK accepts.
- The Covenant's `available` gains `NOT = { has_country_flag = mltd_wbh_alliance }`, with a
  `custom_trigger_tooltip` saying the raiders will not sit at the Brotherhood's table.
- Terms' `available` gains the mirror, `NOT = { has_country_flag = mltd_brk_covenant_joined }`.
- The Tide-Wall's `available` gains `NOT = { has_country_flag = mltd_wbh_alliance }` too: its war
  would break the alliance the moment it was made. Act III's close still has three other paths, so
  nothing strands.

The acceptance effect, `mltd_wbh_join_the_covenant`, mirrors the Broken Coast's:

- MLT founds the Drowned Covenant if it leads no faction (`create_faction_from_template` with
  `mltd_drowned_covenant_template`, else `create_faction`, exactly as `mltd_brk_join_the_covenant`
  does);
- the answering Brotherhood joins it, `add_to_faction`;
- `mltd_drowned_covenant` +75 opinion both ways;
- `set_country_flag = mltd_wbh_alliance` on MLT.

Events (Act III owns `mltd.30-39`):

- `mltd.32`, to the Brotherhood: the offer, two options (accept / refuse) with the `ai_chance` of
  the list above. Accept runs `mltd_wbh_join_the_covenant` in MLT's scope and sends `mltd.33` to
  MLT; refuse sets `mltd_wbh_refused_terms` on MLT, gives MLT the expiring war goal (section 4) and
  sends `mltd.34`.
- `mltd.33` to MLT: the Citadel opens its gates.
- `mltd.34` to MLT: the refusal, and the year MLT has to act on it.

## 3. How likely is the answer (ask 3)

Every focus whose payoff is an AI's answer says so in its own description, and the line reads the
game rule, so it is true in the game being played. Add three `defined_text` functions to
`mod_folder/common/scripted_localisation/mltd_scripted_localisation.txt`:

- `GetMltdBrkOdds`
  - Historical: "The raiders will take the offer."
  - Unhistorical: "The raiders are as likely to take the offer as to spit on it."
- `GetMltdBdtOdds`
  - Historical: "The dancers will take the offer." (same both ways)
  - Unhistorical: same
- `GetMltdWbhOdds`
  - Historical: "The Brotherhood will refuse. Its Codex has no line for kneeling to a drowned
    queen."
  - Unhistorical: WBH: "The Brotherhood is as likely to refuse as to listen." / TCA: "The
    Northwestern Brotherhood will almost certainly refuse; perhaps one chapter in ten would
    listen."

Write them in the style of OWB's own `defined_text` blocks (`GetMltdWmMarketOpen` in the same file
is our precedent), `trigger = { is_historical_focus_on = yes }` and so on, and end each `_desc`
with the function on its own line. The wording is yours; keep it in the mod's voice, and do not
give a bare percentage.

Also add, to each invitation's `completion_reward`, a `custom_effect_tooltip` naming the gamble:
what a yes brings, what a no leaves (the expiring war goal, and no timed idea).

## 4. What a refusal costs (ask 4)

The offer is the slow road, and a refusal leaves only a hunting licence:

- **Cost.** Terms for the Citadel 63 days against The Tide-Wall's 45; the Covenant stays at 49
  against Drown the Dance's 49 (the Broken Coast's refusal already costs an opinion penalty). No
  invitation grants a timed idea; the war focuses keep theirs.
- **The war goal.** On a refusal the refusing country's scope gives MLT
  `create_wargoal = { type = annex_everything target = <refuser> expire = 365 }` - vanilla's
  `expire` is in days (`common/national_focus/germany.txt` uses `expire = 0` for "never"). It goes
  with the existing penalties (`mltd_drowned_covenant_refused` and the global refusal flag for BRK;
  `mltd_bdt_refused_covenant` for BDT). Add it in all three refusal paths: `mltd.21` option b
  (BRK), `mltd.26` (BDT's refusal), `mltd.32` option b (WBH/TCA).
- **The text** says the year is short, and the loc key holds the 365 as a literal beside the effect
  (CLAUDE.md > *Numbers in two places*).

## 5. The spoils branches (ask 5)

Optional focuses that pay off conquered land and gate nothing. They also answer CLAUDE.md > Plan >
Medium priority: the focus slot idles for months while each act's close waits on its war.

**New file** `mod_folder/common/national_focus/mltd_spoils_focus.txt`, nine shared focuses in three
branches of three. Each branch hangs off an act's close (a shared focus), so it is pulled in with
it and needs no new listed root. They sit to the right of the spine, clear of every fan (the spine
is x = 15, the widest fans reach x = 18):

- *The Drowned Harvest* (California)
  - Root cell: (20,28)
  - Chain: (20,29), (20,30)
  - Opens after: `mltd_when_shady_sands_falls` - so it runs while Act V's war is fought
- *The Iron Tithe* (the interior)
  - Root cell: (20,32)
  - Chain: (20,33), (20,34)
  - Opens after: `mltd_when_the_legion_breaks`
- *The Salt Road* (the south)
  - Root cell: (20,36)
  - Chain: (20,37), (20,38)
  - Opens after: `mltd_the_last_king_kneels`

Rules for all nine:

- `prerequisite` on the branch's own previous focus (the root's is its act's close);
  `relative_position_id` to that focus; `cancel_if_invalid = no`, `continue_if_invalid = yes`; an
  OWB icon that has its `_shine`; `ai_will_do` `factor = 2` (below the spine's chapters and closes,
  so an AI takes the spine first and these while it waits).
- Each `available` asks for land the player has actually taken - `num_of_controlled_states`,
  `owns_state`, or a state of that act's theatre (California 253 / 163, the Colorado 520, Texas 892
  / 921) - never for a war's outcome, so they can be taken during the next act's war.
- **Payoffs** are the kind a conqueror gets from land, and each one is modest and permanent rather
  than a spike: building slots or infrastructure in owned states, resource extraction, compliance
  or resistance help, coring cost, construction speed, a research bonus or a small permanent idea.
  Follow OWB's own idioms for these (its focus files are full of `add_building_construction`,
  `add_resource`, `add_compliance`, `add_tech_bonus`, `production_speed_buildings_factor`,
  `local_resources_factor`, `resistance_damage_to_garrison`, `compliance_growth`); check every
  modifier in vanilla's `documentation/modifiers_documentation.md`.
- **Size**: one permanent idea per branch at most, each 2-4 modifiers inside +-5-10 % (the round-27
  balance rule), plus small one-off gifts (a few hundred equipment, 25-100 political power, a tech
  bonus of 50-75 %). No research slots: Acts IV and VI already give the only two.
- New ideas go in `mod_folder/common/ideas/mltd_ideas.txt` in the round-27 shape, with reused OWB
  pictures.
- No new events are needed; if a branch wants one, take `mltd.35-39` (Act III's decade is the only
  one with room) and say so in the return.

## Where the work goes

Because several agents work at once, **write only your own files** and put anything belonging to a
shared file into your staging folder, as round 27 did. Staging root:
`C:\Users\jonat\AppData\Local\Temp\claude\c--Users-jonat-Documents-rising-tide\71877056-fecf-418a-a4f4-50b7c28bba62\scratchpad\r28\<area>\`

- Staging file `events.txt`
  - Contents: whole `country_event` blocks, no `add_namespace`
  - Integrator puts it in: `mod_folder/events/mltd_events.txt`
- Staging file `loc.yml`
  - Contents: `key:0 "Value"` lines, indented 2 spaces - new keys, and replacements for existing
    ones (list which in your return)
  - Integrator puts it in: `mod_folder/localisation/english/MLT/mltd_l_english.yml`
- Staging file `ideas.txt`
  - Contents: idea blocks
  - Integrator puts it in: `mod_folder/common/ideas/mltd_ideas.txt`
- Staging file `effects.txt` / `triggers.txt`
  - Contents: scripted effects / triggers
  - Integrator puts it in: `mltd_scripted_effects.txt` / `mltd_scripted_triggers.txt` (AI holds go
    to `mltd_ai_triggers.txt`, section W)
- Staging file `scripted_loc.txt`
  - Contents: `defined_text` blocks
  - Integrator puts it in: `mod_folder/common/scripted_localisation/mltd_scripted_localisation.txt`
- Staging file `notes.md`
  - Contents: what the integrator, the AI/plan pass and the docs pass must know

## House rules that apply (CLAUDE.md)

- Loc: countries, states and characters through functions (`[WBH.GetNameDef]`, `[235.GetName]`);
  our own things as `$key$`, one level deep, to plain-text keys; event `.d` text only `§o` and
  `§c`, option text no colour codes; focus and idea tooltips may use `§Y` / `§G` / `§R`. UTF-8, and
  the integrator keeps the BOM.
- Events: `is_triggered_only`, `fire_only_once` where it fits, the `immediate = { log = ... }`
  line.
- Fair play: an AI gets nothing a human would not. An AI-only *hold* in `available` follows section
  W's idiom (`hidden_trigger` + `if = { limit = { is_ai = yes ... } }`).
- Every gate that matters shows a `custom_trigger_tooltip`; every literal that appears in both
  script and loc is listed in your return so the docs pass can record it.

## Return (every build agent)

JSON: the files you wrote; every focus with id, cell, cost, prerequisites and gates; events, ideas,
effects, triggers and scripted-loc functions defined; new and replaced loc keys; literals repeated
in two places; anything the AI plans, `CONQUEST_PLAN.txt` or CLAUDE.md must say; and every
construct you could not verify against OWB or vanilla.
