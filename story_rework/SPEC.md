# Rising Tide - the story acts (round 27) - build spec

Repo: `C:\Users\jonat\Documents\rising-tide` (mod files under `mod_folder/`). OWB: `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196`.
Scratch staging root: `C:\Users\jonat\AppData\Local\Temp\claude\c--Users-jonat-Documents-rising-tide\71877056-fecf-418a-a4f4-50b7c28bba62\scratchpad\story\`

## Why

The ten conflict sub-trees (`mod_folder/common/national_focus/mltd_conflicts_focus.txt`, 46 shared focuses) sit left and
right of MLT's trunk with no line to anything, 31 columns wide. The user wants a tree that reads as a story, like OWB's
Mojave Chapter (`common/national_focus/Mojave Chapter (MOJ) Focus.txt`): ONE central spine of chapter focuses, each
followed by a short fan of 1-2-deep beads that RECONVERGE (OR prerequisites) into the next spine node, with an event at
every story beat and mutually exclusive endings at the bottom.

## The shape (every coordinate is the absolute grid cell; the spine is x = 15)

```
row 20  [Grand Ritual]                                  national (override) - unchanged
row 21  [The Deep Ones Walk]                            national (override) - unchanged
row 22  [WBH Eyes]      [BRK Salt]      [BDT Bone Shore]      ACT II fan heads (listed roots)
row 23  [WBH Knights]   [BRK Sail N.]   [BDT Dancers]         ACT II fan ends
row 24  [The Final Ritual]                              national - moved from row 23; prereq Walk AND (OR the 3 ends)
row 25  [Tide-Wall] [Covenant] [Hail King] [Drown Dance]      ACT III fan (listed roots, prereq Final Ritual)
row 26  [The Tide Turns South]                          ACT III close (NEW)
row 27  [A Mole in Shady Sands]                         ACT IV chapter
row 28  [Delegates] [Sleepers] [Caravan Roads]          ACT IV fan
row 29  [The Turbines Sing]                             ACT IV war
row 30  [When Shady Sands Falls]                        ACT IV close (NEW)
row 31  [Mars in the Water]                             ACT V chapter (NEW)
row 32  [CES River] [BOS Paladin] [WHT Lake God] [HEA Whispers]    ACT V fan heads
row 33  [CES Mars]  [BOS Blood]   [WHT Rites]    [HEA Crusade]     ACT V fan capstones (wars)
row 34  [When the Legion Breaks]                        ACT V close (NEW)
row 35  [The Southern Deep]                             ACT VI chapter (NEW)
row 36  [TEX All Waters] [ATE Feathered Tide] [TLA Iron God]       ACT VI fan heads (ATE NEW)
row 37  [TEX Black Water] [ATE Serpent Drowns] [TLA Drowned God]   ACT VI fan capstones (ATE NEW)
row 38  [The Last King Kneels]                          ACT VI close (NEW)
row 39  [R'lyeh Rises]                                  FINALE (NEW)
row 40  [The Dreamer Wakes] [The Priestess Reigns] [Return to the Sea]   ENDINGS (NEW, mutually exclusive)
```

Act I (Kingdom -> The Spreading Cult / The Wet Market -> Gifts -> the five Books -> Call of the Deep Ones -> Grand
Ritual) is unchanged and lives in the override `Mirelurk Tribe (MLT) Focus.txt`; do not touch it.

## Architecture rules (all acts)

1. **Every story focus of Acts II-VI and the finale is a `shared_focus`** in a per-act file:
   `mod_folder/common/national_focus/mltd_act2_focus.txt` ... `mltd_act6_focus.txt`, and `mltd_finale_focus.txt`.
   Header comment, then top-level `shared_focus = { ... }` blocks, LF, no BOM, tabs (copy the style of
   `mltd_conflicts_focus.txt`). `mltd_conflicts_focus.txt` is READ-ONLY for you: copy kept focus blocks out of it; the
   integrator deletes it afterwards.
2. **Pull-in.** A shared focus enters MLT's tree only if it is listed in the override (`shared_focus = <id>`) or reaches
   a listed one through `prerequisite`s on other SHARED focuses. The integrator lists exactly these roots in the
   override: the three Act II heads and the four Act III fan focuses. Everything else must chain to one of them through
   shared prerequisites. National focuses may be named in a shared focus's `prerequisite` (Act II heads -> Walk, Act III
   fan -> Final Ritual); that is why those seven are listed.
3. **Positions.** Listed roots (Act II heads, Act III fan) and `mltd_the_tide_turns_south` use ABSOLUTE `x`/`y` and no
   `relative_position_id`. Every other focus uses `relative_position_id` to a SHARED focus, exactly as given in the
   per-act tables (never to a national focus). Do not move anything off the table's cell.
4. **Prerequisites.** Separate `prerequisite = { }` blocks are AND; one block listing several `focus =` is OR.
   Fans reconverge with ONE OR block over the fan's last beads.
5. **Never strand.** The OR reconvergence must always have a takeable path, for a human and for the AI:
   - Every fan bead (head or end) must be takeable when its target country no longer exists (or is MLT's subject):
     drop `country_exists` from `available`, and give the reward an `if = { limit = { country_exists = X } ... }
     else = { <fallback, usually +25-50 political power> }`.
   - **No intelligence gates on any story focus**: remove every `has_operation_token` / `network_national_coverage` /
     `intel_level_over` test from `available` (keep the intel REWARDS, still inside `has_dlc = "La Resistance"` ifs).
     Exceptions: `mltd_brk_the_drowned_covenant` and `mltd_bdt_hail_the_drowned_king` keep their courtship conditions
     (cult, token, coverage, intel) because they are invitations, and their act always has another path.
   - Story-world gates on war capstones stay (Hoover flags or 1 June 2279; `texas_formed` or 2280; WBH's purge or
     2280 + The Warren; Heaven's Guard's holy wars or 2280; the Utah road war or 2280) - they already carry a
     "target gone" branch; keep it.
6. **Every story shared focus** has `cancel_if_invalid = no` and `continue_if_invalid = yes`.
7. **Focus AI.** Heads/beads `ai_will_do = { factor = 3 }`; chapters, closes, finale `factor = 10`. War capstones KEEP
   their existing stage/readiness modifiers (`mltd_ai_stage_*`, `mltd_ai_army_ready`, `mltd_ai_ncr_beaten`,
   `mltd_ai_legion_beaten`, the Bone Dancers' courtship). DROP the round-23 `is_ai` modifiers that only waited on an
   earlier act (e.g. `NOT = { has_completed_focus = mltd_the_deep_ones_walk }`): the tree now enforces the order.
8. **Icons.** Reuse OWB/our focus icons; each must have a `_shine` sprite (check OWB `interface/*.gfx`). Kept focuses
   keep their icons. New focuses pick fitting existing icons (no new art).
9. **Kept ids stay ids.** Keep the id of every kept focus; the AI, plan and events name them. New ids are exactly the
   ones in this spec.
10. **Merges.** A deleted focus's distinctive effects move into the kept bead named in the merge map; drop pure
    duplicates (a second foothold, a second intel grant to the same tag) and keep each branch's total payoff about equal
    to or a little below what the old sub-tree paid. Reuse existing tooltip keys where the effect is unchanged.
11. **Balance guide for NEW rewards.** Chapter focus: an event plus a small reward (25-50 political power or 20-30 army
    experience). Close: an event with the trophy plus a world news event. Permanent act ideas: 2-4 modifiers, each within
    +-5 % .. +-10 % (timed ideas 180 days as before). Endings are the one place for large bonuses (up to +-20 %).
    Everything a focus gives applies to human and AI alike (fair play); nothing AI-only.

## Where each kind of output goes

Write the focus file into `mod_folder/` directly. Put everything that belongs in a SHARED file into your staging folder
`<staging root>\act<N>\` (N = 2, 3, 4, 5, 6 or `finale`) - the integrator merges these, so parallel acts never edit the
same file:

| Staging file | Contents | Integrator puts it in |
| --- | --- | --- |
| `events.txt` | complete `country_event` / `news_event` blocks, NO `add_namespace` line | `mod_folder/events/mltd_events.txt` |
| `loc.yml` | loc lines only, `  key:0 "Value"` (2-space indent, no `l_english:` header). NEW keys, and REPLACEMENT values for existing keys (list those in your return) | `mod_folder/localisation/english/MLT/mltd_l_english.yml` |
| `ideas.txt` | complete idea blocks (the text that goes inside `ideas = { country = { ... } }`) | `mod_folder/common/ideas/mltd_ideas.txt` |
| `triggers.txt` | complete scripted-trigger definitions | `mod_folder/common/scripted_triggers/mltd_scripted_triggers.txt` |
| `effects.txt` | complete scripted-effect definitions | `mod_folder/common/scripted_effects/mltd_scripted_effects.txt` |
| `notes.md` | anything the integrator must know: keys/effects that became unused, AI/plan implications, unverified constructs | - |

Do NOT edit any existing file in `mod_folder/` (override, loc, events, ideas, AI, plan, triggers, effects). Only create
your own focus file and your staging files.

Existing definitions you may call (read them first): `mltd_intel_foothold`, `mltd_brk_add_volunteer_size` (+3 each
call), `mltd_brk_join_the_covenant`, `mltd_bdt_join_the_covenant`, `mltd_cult_add_strength`, `mltd_wbh_brotherhood`
(trigger), `mltd_ai_ncr_beaten`, `mltd_ai_legion_beaten`, `mltd_ai_stage_*`, `mltd_ai_army_ready`, OWB's `add_caps`
(temp `caps_to_add`), `add_state_population` (temp `pop_add`), `caps_cost_trigger`.

## Event ids and names reserved per act

| Act | Event ids | Notes |
| --- | --- | --- |
| III | `mltd.30` (MLT, The Tide Turns South), `mltd.31` (world news) | |
| IV | `mltd.40` (MLT, When Shady Sands Falls, two options), `mltd.41` (world news) | |
| V | `mltd.50` (MLT, Mars in the Water), `mltd.51` (MLT, When the Legion Breaks, two options), `mltd.52` (world news) | |
| VI | `mltd.60` (MLT, The Southern Deep), `mltd.61` (MLT, The Last King Kneels), `mltd.62` (world news) | |
| Finale | `mltd.70` (MLT, R'lyeh Rises), `mltd.71` (world news), `mltd.72` / `.73` / `.74` (MLT, one per ending) | |

Event rules (CLAUDE.md > Events): `country_event`s are `is_triggered_only = yes` + `fire_only_once = yes` with the
`immediate = { log = "[GetDateText]: [Root.GetName]: event mltd.N" }` line; news events are plain `news_event`s
(`is_triggered_only` only) delivered by the focus through `hidden_effect = { every_other_country = { news_event = { id =
X days = 2 } } }`. `.d` text uses only `§o` (names) and `§c` (emphasis); option text has no colour codes. Pictures:
reused OWB `GFX_event_*` sprites or our `GFX_mltd_event_*` (verify the sprite name exists). Loc refers to countries,
states, characters and our own things through functions/keys (CLAUDE.md > Localisation: functions, not names); `$key$`
nesting one level deep, to plain-text keys only, never to a `localisation/replace/` key inside a sentence. Lovecraft
named only from stories published before 1930.

---

## ACT II - "The Northern Waters" (file `mltd_act2_focus.txt`, staging `act2`)

Between The Deep Ones Walk and The Final Ritual. Three branches of two beads. Heads are listed roots: prerequisite
`mltd_the_deep_ones_walk` (national), absolute positions. Ends: prerequisite their head, `relative_position_id` = their
head, (0,1). No new events. No close focus: the Final Ritual (national) is the reconvergence - the integrator adds
`prerequisite = { focus = mltd_wbh_the_drowned_knights focus = mltd_brk_the_deep_ones_sail_north focus =
mltd_bdt_the_dancers_hear_the_tide }` to it.

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_wbh_eyes_in_the_sound` (kept) | (13,22) abs | Walk | as today (foothold, shelters cults, intel), available no longer needs a Brotherhood (fallback PP when none holds Washington) |
| `mltd_wbh_the_drowned_knights` (kept) | head (0,1) | Eyes | today's theft + 30 XP, PLUS merged `mltd_wbh_salt_in_the_citadel` (each Brotherhood -40 PP, -6 % stability; LaR civ 15 + `token_army`). No intel gate. |
| `mltd_brk_salt_on_the_broken_coast` (kept) | (15,22) abs | Walk | as today, PLUS merged `mltd_brk_the_drowned_raiders` (+10 to BRK's cult; LaR `token_army` + civ 15). Fallback if BRK is gone. |
| `mltd_brk_the_deep_ones_sail_north` (kept) | head (0,1) | Salt | +6 volunteer divisions: call `mltd_brk_add_volunteer_size` twice (it merges `mltd_brk_the_star_spawn_over_the_strait`); keep "no war with BRK while it exists"; `mltd_deep_ones_summon_unlocked` gate can go (the Walk set it). Fallback if BRK is gone. |
| `mltd_bdt_the_bone_shore` (kept) | (17,22) abs | Walk | as today; fallback if BDT gone. |
| `mltd_bdt_the_dancers_hear_the_tide` (kept) | head (0,1) | Bone Shore | as today (cult +10, intel/token) PLUS merged `mltd_bdt_salt_on_the_bone_road` (steal 600 infantry equipment from BDT when it holds > 1,200, else +25 PP; 30 army XP). No intel gate. |

Deleted here: `mltd_wbh_salt_in_the_citadel`, `mltd_brk_the_drowned_raiders`, `mltd_brk_star_spawn_over_the_strait`,
`mltd_bdt_salt_on_the_bone_road`.

## ACT III - "The Stars Are Right" (file `mltd_act3_focus.txt`, staging `act3`)

After The Final Ritual: the north is decided. Four listed roots, prerequisite `mltd_the_final_ritual` (national),
absolute cells; then the close.

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_wbh_the_tide_wall` (kept) | (12,25) abs | Final Ritual | as today (declares war on the living Brotherhood(s), bunkers, claims, idea); drop its old prerequisites; keep its gates. |
| `mltd_brk_the_drowned_covenant` (kept) | (14,25) abs | Final Ritual | as today (event `mltd.21`), its courtship gates kept; add `has_completed_focus = mltd_brk_salt_on_the_broken_coast` to `available` (the old prerequisite, now drawn as no line); if BRK no longer exists the focus is takeable and pays +50 PP instead. |
| `mltd_bdt_hail_the_drowned_king` (kept) | (16,25) abs | Final Ritual | as today (event `mltd.24`), courtship gates kept, `mutually_exclusive` with Drown the Dance (one-sided, as today); add `has_completed_focus = mltd_bdt_the_bone_shore` to `available`. |
| `mltd_bdt_drown_the_dance` (kept) | (18,25) abs | Final Ritual | as today (declares war on BDT); takeable (fallback +50 PP) if BDT is gone. |
| `mltd_the_tide_turns_south` (NEW) | (15,26) abs | OR(the four above) | 30 days. available: `num_of_controlled_states > 49` (custom_trigger_tooltip `mltd_tide_turns_south_states_tt`). Reward: event `mltd.30`, news `mltd.31`, permanent idea `mltd_the_northern_waters` (e.g. +5 % stability, +5 % war support, -25 % justify war goal time). Its text: the north is the tribe's, and the drums turn toward California. |

## ACT IV - "The Drowned Republic" (file `mltd_act4_focus.txt`, staging `act4`)

All relative to the chapter `mltd_ncr_a_mole_in_shady_sands`, which is relative to `mltd_the_tide_turns_south` (0,1).

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_ncr_a_mole_in_shady_sands` (kept, now the CHAPTER) | tide_turns_south (0,1) | `mltd_the_tide_turns_south` | as today (foothold, shelters NCR and MOT cults, intel), available: nothing but the prerequisite (fallback if NCR gone); `ai_will_do` factor 10 |
| `mltd_ncr_drowned_delegates` (kept) | mole (-2,1) | mole | as today, no intel gate, fallback if NCR gone |
| `mltd_ncr_sleepers_on_the_long_15` (kept) | mole (0,1) | mole | as today, no intel gate, fallback |
| `mltd_ncr_salt_on_the_caravan_roads` (kept) | mole (2,1) | mole | as today, no intel gate, fallback |
| `mltd_ncr_the_turbines_sing` (kept, the WAR) | mole (0,2) | OR(delegates, sleepers, caravan) | as today (Hoover gate, declaration, stage gating in ai_will_do) |
| `mltd_when_shady_sands_falls` (NEW, CLOSE) | mole (0,3) | Turbines | 30 days; available `mltd_ai_ncr_beaten = yes` (custom_trigger_tooltip `mltd_ncr_beaten_tt`: "[NCR.GetNameDefCap] has capitulated or is no more"). Reward: event `mltd.40` with two options - (a) `add_research_slot = 1` ("the scholars of Shady Sands serve the tide"; ai_chance base 3), (b) permanent idea `mltd_the_drowned_rangers` (+5 % army attack, +5 % army defence, +5 % division recon or org) and 50 army experience (ai_chance base 1) - and news `mltd.41`. |

## ACT V - "The Sea Against Mars" (file `mltd_act5_focus.txt`, staging `act5`)

Chapter `mltd_mars_in_the_water` relative to `mltd_when_shady_sands_falls` (0,1); all else relative to the chapter.

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_mars_in_the_water` (NEW, CHAPTER) | shady_sands_falls (0,1) | `mltd_when_shady_sands_falls` | 35 days; event `mltd.50` (the Legion's scouts find the river running salt); +30 army experience |
| `mltd_ces_what_the_river_carries` (kept) | chapter (-3,1) | chapter | as today, PLUS merged `mltd_ces_the_drowned_frumentarius` (the operative *Silanus the Drowned* when an agency exists, LaR token_army + civ 15, CES -6 % stability). Fallback if CES gone. |
| `mltd_ces_the_sea_against_mars` (kept, WAR) | chapter (-3,2) | river | as today, PLUS merged `mltd_ces_salt_in_the_armouries` (steal 800 infantry equipment when CES > 1,599 and 200 support when > 399; else +100 caps) |
| `mltd_bos_the_drowned_paladin` (kept) | chapter (-1,1) | chapter | as today, PLUS merged `mltd_bos_the_paladin_returns` (BOS -35 PP; LaR token_army + civ 15) and `mltd_bos_the_codex_unsealed` (LaR steal an engineering/industry tech bonus from BOS, else electronics tech bonus 75 %; BOS -4 % stability). Fallback if BOS gone. |
| `mltd_bos_blood_in_the_water` (kept, capstone) | chapter (-1,2) | paladin | as today, PLUS merged `mltd_bos_the_tide_takes_the_armoury` (the energy-weapon/power-armour theft with its tiers) |
| `mltd_wht_the_lake_god_answers` (kept) | chapter (1,1) | chapter | as today, PLUS merged `mltd_wht_the_drowned_shamans` (+40 PP; WHT -6 % stability; the `wht_god_lake`/`wht_god_old` bonus) and `mltd_wht_guns_for_both_sides` (the per-buyer sale, with round 24's fix). Fallback if both gone. |
| `mltd_wht_rites_on_the_spiral_jetty` (kept, capstone) | chapter (1,2) | lake god | as today, PLUS merged `mltd_wht_sand_in_the_engines` (EHT -3 % war support; steal 600 infantry equipment when EHT > 599) |
| `mltd_hea_whispers_in_the_steam` (kept) | chapter (3,1) | chapter | as today, PLUS merged `mltd_hea_a_second_schism` (+40 PP; HEA -35 PP, -6 % stability, -2 % war support more under `hea_war_in_heaven`; LaR token_army + civ 10, else electronics 50 %). Fallback if HEA gone. |
| `mltd_hea_the_crusade_turns_south` (kept, capstone) | chapter (3,2) | whispers | as today, PLUS merged `mltd_hea_steam_for_the_deep` (steal 600 infantry equipment when HEA > 599; LaR steal an industry tech bonus, else industry 50 %) |
| `mltd_when_the_legion_breaks` (NEW, CLOSE) | chapter (0,3) | OR(the four capstones) | 30 days; available `mltd_ai_legion_beaten = yes` (tooltip `mltd_legion_beaten_tt`). Event `mltd.51` with two options - (a) free the Legion's slaves into the tide: +5,000 population in the capital (OWB `add_state_population`, `pop_add`), +5 % stability (merges `mltd_ces_the_chained_are_given_to_the_tide`; ai_chance base 2); (b) the pens feed the spawning pools: +20,000 manpower (country `add_manpower`) (ai_chance base 1) - plus permanent idea `mltd_mars_beneath_the_waves` (e.g. +5 % army attack, +5 % war support, +5 % recruitable population) and news `mltd.52`. |

Deleted here: `mltd_ces_the_drowned_frumentarius`, `mltd_ces_the_chained_are_given_to_the_tide`,
`mltd_ces_salt_in_the_armouries`, `mltd_bos_the_paladin_returns`, `mltd_bos_the_tide_takes_the_armoury`,
`mltd_bos_the_codex_unsealed`, `mltd_wht_the_drowned_shamans`, `mltd_wht_guns_for_both_sides`,
`mltd_wht_sand_in_the_engines`, `mltd_hea_a_second_schism`, `mltd_hea_steam_for_the_deep`.

## ACT VI - "All Waters Are One" (file `mltd_act6_focus.txt`, staging `act6`)

Chapter `mltd_the_southern_deep` relative to `mltd_when_the_legion_breaks` (0,1); all else relative to the chapter.

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_the_southern_deep` (NEW, CHAPTER) | legion_breaks (0,1) | `mltd_when_the_legion_breaks` | 35 days; event `mltd.60`; +50 political power |
| `mltd_tex_all_waters_are_one` (kept) | chapter (-2,1) | chapter | as today, PLUS merged `mltd_tex_the_silent_partner` (LaR token_army + civ 15 on each; +80 caps; each -4 % stability, -25 PP). Fallback if both gone. |
| `mltd_tex_black_water_rising` (kept, WAR) | chapter (-2,2) | all waters | as today (declares war on TBH and LNS), PLUS merged `mltd_tex_wreckers_on_the_trinity` (steal 800 infantry equipment from TBH, else LNS; 30 army XP) |
| `mltd_ate_the_feathered_tide` (NEW) | chapter (0,1) | chapter | 35 days. The Aztec Empire (`ATE`, OWB): foothold-style spying - `mltd_intel_foothold`, shelter ATE's cult (`set_country_flag = mltd_cult_sheltered` in ATE's scope, tooltip `mltd_ate_cult_sheltered_tt`), LaR civ/army 10 on ATE else +25 PP; ATE -4 % stability. Fallback if ATE gone. Research OWB's ATE (history, focus tree, ideas) for flavour hooks. |
| `mltd_ate_the_serpent_drowns` (NEW, WAR) | chapter (0,2) | feathered tide | 42 days. Declares war on ATE (`declare_war_on`, `type = annex_everything`) if it exists and is neither at war with MLT nor its subject; `will_lead_to_war_with = ATE`; ATE -6 % stability, -3 % war support; 40 army XP; fallback +50 PP if ATE gone. `ai_will_do` modifiers like the other war capstones: 0 for an AI until `mltd_ai_stage_ate` and while `mltd_ai_army_ready` is false. |
| `mltd_tla_the_iron_god_dreams` (kept) | chapter (2,1) | chapter | as today, PLUS merged `mltd_tla_the_three_voices` (-6 % stability and -25 PP on TLA, else each heir, else ARM; LaR civ 15 + token_army, else +50 PP). |
| `mltd_tla_the_drowned_god_sleeps` (kept, WAR) | chapter (2,2) | iron god | as today, PLUS merged `mltd_tla_picking_the_iron_bones` (the theft behind `mltd_tla_iron_bones_theft_tt`, 20 XP, +100 caps) |
| `mltd_the_last_king_kneels` (NEW, CLOSE) | chapter (0,3) | OR(the three capstones) | 30 days; available: Texas beaten - a NEW scripted trigger `mltd_texas_beaten` (TBH and LNS each either do not exist or have capitulated), tooltip `mltd_texas_beaten_tt`. Event `mltd.61`, news `mltd.62`; reward `add_research_slot = 1` and permanent idea `mltd_the_drowned_south` (e.g. +10 % factory output, +5 % stability). |

Deleted here: `mltd_tex_the_silent_partner`, `mltd_tex_wreckers_on_the_trinity`, `mltd_tla_the_three_voices`,
`mltd_tla_picking_the_iron_bones`.

## FINALE - "R'lyeh Rises" (file `mltd_finale_focus.txt`, staging `finale`)

`mltd_rlyeh_rises` relative to `mltd_the_last_king_kneels` (0,1); endings relative to `mltd_rlyeh_rises`.

| Id | Cell | Prereq | Content |
| --- | --- | --- | --- |
| `mltd_rlyeh_rises` (NEW) | last_king (0,1) | `mltd_the_last_king_kneels` | 70 days; available `num_of_controlled_states > 299` (tooltip `mltd_rlyeh_rises_states_tt`). Event `mltd.70`, news `mltd.71`; +15 victory points in M'lyeh (province 1983, `add_victory_points`, followed by `custom_effect_tooltip = mltd_newline_tt`); global flag `mltd_rlyeh_risen`. |
| `mltd_ending_the_dreamer_wakes` (NEW) | rlyeh (-2,1) | R'lyeh | 35 days; mutually exclusive with the other two endings (declare on all three, both ways); event `mltd.72`; permanent idea `mltd_the_dreamer_wakes` (war: e.g. +15 % army attack, +10 % army defence, +10 % war support, -5 % stability). ai_will_do base 3. |
| `mltd_ending_the_priestess_reigns` (NEW) | rlyeh (0,1) | R'lyeh | as above; event `mltd.73`; idea `mltd_the_priestess_reigns` (rule: e.g. +20 % stability, +20 % political power, -10 % consumer goods). ai_will_do base 2. |
| `mltd_ending_return_to_the_sea` (NEW) | rlyeh (2,1) | R'lyeh | as above; event `mltd.74`; idea `mltd_the_return_to_the_sea` (the deep: e.g. +0.2 monthly population growth (`monthly_population`), +10 % recruitable population, and two Leviathans raised at once through `mltd_spawn_leviathan` twice, if Mireport is held). ai_will_do base 1. |

The ending events close the campaign's story: M'lulu's fate, the Great Old One, what the world is now. They may read
live numbers through `[?ROOT.mltd_books_read|0]`, `[?ROOT.mltd_national_population|0]` etc. only if the variable exists.

## Return (every build agent)

Return JSON (the schema enforces it): the files you wrote; every focus with id, cell, prerequisites and status
(kept/new); every id you deleted (merged away) and where its effects went; every NEW loc key and every EXISTING loc key
you replaced; events, ideas, scripted triggers and effects defined; loc/tooltip keys and scripted effects/triggers that
your changes made UNUSED (candidates for the integrator to delete - only if nothing else in `mod_folder/` references
them; check with grep); and a list of unverified constructs.
