# Rising Tide - balance review after rounds 28b and 28c

2026-09-22. This review rests on:

- 145 verdicts from six lenses: the country's power curve, the focuses, the ideas, the units, the
  systems, and MLT's AI;
- a skeptic's check of each of the 29 medium- or high-severity "too strong" and "too weak"
  verdicts. 17 were upheld, often with corrections; 12 were refuted;
- OWB's measured norms (focus rewards, spirits, rivals, units);
- the seven archived AI spectator runs.

Two caveats before reading on:

- **Nothing here is play-tested.** The last human play-test was before round 3.
- **Every AI run ran on round 19-24 code.** No run has seen the story acts, the invitations, the
  spoils or round 28b's rescaled rewards.

So every figure after 2279 comes from `CONQUEST_PLAN.txt`'s model [M] or from the code. No game
file was changed.

Tags used below:

- **[upheld]**: a skeptic checked the verdict and it stood, sometimes with corrections, which are
  included.
- **[refuted]**: a skeptic showed the verdict wrong. The item then sits under *About right*, with
  the reason.
- **[unchecked]**: the verdict was rated risky or low severity, so it was not sent to a skeptic.

______________________________________________________________________

## 0. What the user decided, 2026-09-22

The review's proposals went to the user the day it was written. What was applied, and what was not:

- 2, the research slot
  - Decision: **Applied.** `add_research_slot` moved from The Last King Kneels to The Tide Turns
    South, so the NCR war is fought on four slots and MLT still ends on five (`mltd.40` a is now
    the fifth).
  - Where it landed: `mltd_act3_focus.txt`, `mltd_act6_focus.txt`; the plan's research ladder and
    its slot-4 line
- 6, the Drowned Rangers
  - Decision: **Applied.** Attack and defence 0.05 -> 0.10 (organisation stays 0.05), army
    experience 50 -> 100, in the idea, the event option and its preview.
  - Where it landed: `mltd_ideas.txt`, `mltd_events.txt`, `mltd_act4_focus.txt`
- A3, Old Castro
  - Decision: **Applied.** `ai_will_do` 100 -> 10003, OWB's idiom for an advisor the AI must hire.
  - Where it landed: `common/characters/MLT.txt`
- 1, the Drowned Hoard's cooldown
  - Decision: Declined.
- 3, the Wet Market's tech gates
  - Decision: Declined.
- 4, the Star Spawn summon cap
  - Decision: Declined.
- 5, the Leviathan fleet cap
  - Decision: Declined.
- 7, the gift rentals
  - Decision: Open: the user asked for a fuller description before deciding.
- A1, A2, the other AI items
  - Decision: Declined for now; the next spectator run comes first.

Three changes were made in the same pass that the review did not propose. They are the user's own:

- **The three invitations now ask the same set** - the invitee's cult at 40 %, its civilian
  infiltration token and 25 % network coverage - plus a rival gate. The Drowned Covenant lost
  `brk_nf_pirate_coast`'s VIC/DRE coast and its civilian intel over 50 %; Hail the Drowned King
  lost the Odious King and gained the pilgrims' rule; Terms for the Citadel, which had no intel
  gate, gained the three. This answers the risk listed in section 5 about the Covenant's VIC/DRE
  gate.
- **The Last King Kneels** wears OWB's Texan icon and Act VI closed up a row.
- **Long focus effects** are grouped into blocks with `mltd_newline_tt` spacers.

______________________________________________________________________

## 1. Verdict

Played by a human on the plan, MLT is **strong from the Kingdom to the Final Ritual (2276-79)**.
There it turns people into equipment faster than any factory could. From 2279 it is **roughly
level** with its rivals, and its one real economic weakness is **research**.

Industry is not a weakness at all. The plan's premise that conquest halves every state's industry
is wrong for OWB's default rules (section 4), so the plan understates MLT by roughly half from 2279
on.

Played by the AI, MLT is **too slow at every gate**. It wins every war it starts in the north, but
it:

- never opens on CCW;
- reaches the Kingdom 95-543 days late;
- waits years on the five Books, a consolidated north and a cult that never grows;
- has war-focus holds that could send it into a war it cannot win.

Stage by stage:

- 2275-76, Oregon
  - Human on the plan: Every war is a formality. Mirelurk armour 15 faces Oregon piercing of 1-2,
    the one exception being TRL's single behemoth division.
  - AI (runs 1-8): Wins every war it starts: TRL in 14-28 days, MDT in 77-161. But it never
    justifies on CCW, in all 7 runs.
  - Verdict: Human: about right (this is OWB's armour balance). AI: too slow.
- 2276-79, the build-up
  - Human on the plan: Summons, the Drowned Hoard feeding the Wet Market, gift rentals and ungated
    king-form lots: ~70-100k IC of monsters and market mirelurks in two years, against ~18-25k IC a
    year of MLT's own arms output.
  - AI (runs 1-8): Enters it 95-543 days late and leaves it 1.8-2.5 years late, with 5 states
    against 12-15 at the Kingdom's date.
  - Verdict: **Too strong for a human** in the population-to-equipment loop.
- 2278-79, the Final Ritual
  - Human on the plan: The 36.3 % toll is refilled by conquest, because OWB's default rule keeps
    conquered people. The permanent gifts follow.
  - AI (runs 1-8): Loses 40-42 % of its people and never recovers: 137-140k for two years in run 8.
  - Verdict: Price about right. The gifts are the largest block in the mod, but they hold up
    (section 3).
- 2279-82, the NCR
  - Human on the plan: The one real contest: the NCR's side has 86 states, 1.23M people and 100 civ
    / 54 mil at start, and fights the Legion too.
  - AI (runs 1-8): No run opened the NCR stage. In run 8 the Legion annexed the NCR in 2281-02.
  - Verdict: About right. Research on 3 slots is the weak lever.
- 2282-85, the Legion, the interior and Texas
  - Human on the plan: Unknown. The rivals grow by then: the Legion eats Vegas and New Mexico, TBH
    eats LNS, MOC takes Tlaloc.
  - AI (runs 1-8): Unreached.
  - Verdict: The "victory laps" verdict was **refuted**; keep the plan's 18 / 15 months.
- 2286, the finale
  - Human on the plan: 300 controlled states is about a quarter of the map. The endings are a real
    choice, the Priestess the weakest.
  - AI (runs 1-8): Out of reach: the best run owned 51 states.
  - Verdict: About right. The Priestess is disputed (section 5).

______________________________________________________________________

## 2. Too strong and too weak

The numbers below are the lenses' proposals as corrected by the skeptics. None is applied: each one
changes the human game too, so it is the designer's call.

### 2a. Content (human and AI alike), most important first

- **1. The Drowned Hoard feeding the Wet Market**
  - Verdict: Too strong, high [upheld]
  - Evidence: 25 PP and 1,000 people give 100 caps every 60 days. That is 600 caps (~15,000 IC of
    mirelurks at 25 IC a cap) a year: ~80 % of MLT's 2277 arms output, 12x its native caps income,
    and 4-6x OWB's best repeatable caps decision (Eagle Rock's casino, ~150 a year). With the caps
    rule off, `add_caps` pays 1.25x in political power, a PP printer.
  - Proposed: Cooldown 60 -> **90 days**. It still yields ~400 caps (~10,000 IC) a year.
  - Where: `mltd_decisions.txt:541` (the flag's `days`) and
    `mltd_offering_drowned_cooldown_after_tt`. `_cooldown_tt` prints the countdown and needs no
    edit. Plan `:42-43`, `:264`, `:271`, `:839`, `:862-863`.
- **2. Research: 3 slots through the NCR war**
  - Verdict: Too weak, medium [upheld by 2 of 3; the third says wait for a play-test]
  - Evidence: The 4th slot comes only with `mltd.40` a (~2282-05) and the 5th with The Last King
    Kneels (~2285-12), so the whole NCR war is fought on 3. Rivals start on 4-5: NCR 4 (+2 from its
    tree), CES 4 (+1), WBH 5, TLA 5. Almost every tribal peer gains slots from OWB content (HEA +2,
    EHT +2, WHT, BDT, TRL +1); MLT gains none.
  - Proposed: Move `add_research_slot = 1` from The Last King Kneels to The Tide Turns South
    (~2279-07). MLT still ends on 5. The other variant, turning The Northern Waters' stability into
    +5 % research, was **refuted**: speed on 3 slots is worth ~0.15 of a slot.
  - Where: `mltd_act6_focus.txt:1080` -> `mltd_act3_focus.txt:713-714`, with a preview line.
    CLAUDE.md's "Acts IV and VI give the only two", the story-acts rows and Testing. Plan `:47`,
    `:561`, `:659-661`, `:847-853`, `:918-920`.
- **3. The Wet Market's `_2`, armour and king rows have no tech gate**
  - Verdict: Too strong, medium [upheld]
  - Evidence: Every row tests only `mltd_wet_market_can_buy`: open, caps, stock, cooldown. So from
    2277 a human buys 250 king mirelurks for 200 caps, a form OWB dates to 2282. Against the `_1`
    MLT builds then, the king has soft attack 22 vs 13, breakthrough 16 vs 9 and armour 20 vs 15.
    The armour form (armour 25, piercing 15) is a bigger jump still. MLT's AI buyer is tech-gated.
    OWB's own sellers keep better tiers behind influence.
  - Proposed: Gate buy rows 2-4 on `has_tech` for `amphibious_beast_intermediate_form` /
    `_armor_form` / `_king_form`, each in a `custom_trigger_tooltip`. Leave selling ungated. The
    shared requirement line (`GetMltdWmRequirement`) needs a key or function per row.
  - Where: `mltd_wet_market_gui.txt:61-72`. Plan: one line saying the better lots open with their
    techs.
- **4. Summon the Star Spawn: its window, and the dodge through the ritual**
  - Verdict: Too strong, medium [upheld]
  - Evidence: 75 PP and 16,000 people buy a trained, elite 12,000 IC division plus 2,400 IC of
    spare, every 120 days. The only gate is 32,000 controlled people. The 200k gate binds only at
    the ritual's start, and the 0.25 %-a-day toll would take a third of those people anyway, so a
    first-day summon really costs ~10k. The decision hides only when the Final Ritual completes, so
    delaying the ritual keeps it open.
  - Proposed: Cap it at **3 summons** (a counter, a `custom_trigger_tooltip` and a line in
    `mltd_summon_the_star_spawn_desc`). With the Walk's free division that is at most 4, the plan's
    "3-4". Keep the price and cooldown.
  - Where: `mltd_decisions.txt:368-377` (available), `:392-404` (effect). Plan `:361-363`,
    `:404-405`.
- **5. Summon the Leviathan: a flat price that never retires**
  - Verdict: Too strong late, medium [unchecked; three lenses agree]
  - Evidence: 100 PP and 24,000 people every 180 days, forever. That is ~5 % of the nation in 2280
    and under 1 % by 2285, so ~20 ships by 2291 [M] plus Return to the Sea's two. Each has 400 HP,
    240 heavy attack, armour 20 and visibility 8, against 2-4 `heavy_1` hulls in each Pacific navy.
    The land summons retire in 2277 and 2279.
  - Proposed: Cap the fleet: `has_navy_size = { size < 6 unit = mltd_leviathan }` in `available`
    (vanilla `triggers_documentation.md:4444-4457`), with a tooltip. Return to the Sea may still
    exceed it. The alternative is a toll of max(24k, 2 % of the controlled population).
  - Where: `mltd_decisions.txt:419-431`; `mltd_summon_the_leviathan_desc`. Plan `:416`, `:899-904`.
- **6. The Drowned Rangers (`mltd.40` b) against a fourth research slot (a)**
  - Verdict: Too weak, medium [upheld]
  - Evidence: +5 % attack, defence and organisation and 50 army XP is OWB's median spirit. Against
    it stands +33 % research throughput for a 3-slot country. The AI takes the slot 3 times in 4,
    and the plan's own note calls b a trap.
  - Proposed: Attack and defence **0.05 -> 0.10**; organisation stays 0.05 (the gifts already give
    +20 %). Army XP **50 -> 100**. Still inside the act band and at OWB's 75th-90th percentile.
  - Where: `mltd_ideas.txt:346-347`; `mltd_events.txt:1559` and its preview at
    `mltd_act4_focus.txt:554`. Plan `:561`, `:891-894`, `:921-923`.
- **7. The gift rentals before 2279**
  - Verdict: Too strong, medium [upheld; two lenses called it about right]
  - Evidence: 25 PP and 500 manpower give 30 days of +20 % attack, defence, organisation or
    stability, renewable at once, with no drawback. OWB's rentable attack buffs top out at +15 %
    and all carry a cooldown or malus (PLS Prayer to Jupiter, Utah's Tar ritual). Against it:
    political power is the real limit (run 8 sat at 7-30 PP at war).
  - Proposed: **90-day** missions at **100 PP**: ~1.1 PP a day against 0.83, and two thirds fewer
    clicks. Leave the +20 alone.
  - Where: `mltd_decisions.txt:22`, `:59` and the same pair in each gift;
    `mltd_gift_lasts_30_days_tt`. CLAUDE.md Testing ("expire after 30 days").
- **8. Star Spawn speed 10**
  - Verdict: Risky, low [unchecked]
  - Evidence: Double the king mirelurk's 5.5, and faster than every OWB tank (6-9) and every
    creature (at most 6). With armour 44 and breakthrough 280 a division, it is the best
    exploitation division on the map. It is the one Star Spawn stat with no OWB precedent.
  - Proposed: **10 -> 7** (tank speed, still the fastest creature), or 8 if the stride is part of
    the fantasy.
  - Where: `mltd_equipment.txt:95`, and its header comment at `:11`.
- **9. Blood in the Water's Red Tide is unreachable**
  - Verdict: Too weak, low [unchecked; two lenses]
  - Evidence: The idea (+5 % attack, +10 % army XP gain) needs Lost Hills at war with the NCR, but
    Act V opens only once the NCR is beaten.
  - Proposed: Grant `mltd_bos_red_tide` whenever the focus declares on a living Lost Hills that is
    not MLT's subject. Keep the war-support hits as the extra, and update `mltd_bos_war_feeds_tt`
    and its siblings.
  - Where: `mltd_act5_focus.txt:694-707` (the effect); preview at `:642-656`.
- **10. The pacing chapters**
  - Verdict: Too weak, low [unchecked]
  - Evidence: Mars in the Water: 35 days for 30 army XP. The Southern Deep: 35 days for 50 PP.
    R'lyeh Rises: 70 days for +15 victory points and a flag nothing reads. A Mole in Shady Sands
    pays more in 30.
  - Proposed: Mars in the Water and The Southern Deep **35 -> 21 days**, or a 180-day +5 % attack
    against the act's target (the Tide-Wall's `targeted_modifier`). R'lyeh Rises **70 -> 35**, or a
    payoff on `mltd_rlyeh_risen`.
  - Where: `mltd_act5_focus.txt:83`; `mltd_act6_focus.txt:76`; `mltd_finale_focus.txt:22`. Plan
    timeline.
- **11. Long Act II/III focuses with thin payoffs**
  - Verdict: Too weak, low [unchecked]
  - Evidence: Terms for the Citadel is 63 days for a certain refusal on historical rules. The Deep
    Ones Sail North is 63 days for +6 volunteers. The Dancers Hear the Tide is 56 days, and gates
    nothing in Act III.
  - Proposed: Terms **63 -> 49** (level with the other invitations). Sail North **63 -> 49**, or
    +25 army XP; keep the +6, which the AI's NCR stage leans on. Dancers **56 -> 42**.
  - Where: `mltd_act3_focus.txt:96`; `mltd_act2_focus.txt:385`, `:472`. Plan timeline.
- **12. Fallbacks when a story target is gone**
  - Verdict: Too weak, low [unchecked]
  - Evidence: +25 or +50 PP for 35-63-day focuses is 0.5-1.4 PP a focus day; OWB pays ~3.3. Targets
    are often gone early: TCA or PMR ate the Brotherhood in Washington by 2279 in two runs.
  - Proposed: Scale to ~1.5 PP a day: 35 days -> 50, 49 -> 75, 56-63 -> 100. The Drowned Knights'
    +25 -> 75 first.
  - Where: e.g. `mltd_act2_focus.txt:192`. Every head, bead and invitation `else`, and the matching
    `effect_tooltip` previews.
- **13. Dead manpower modifiers**
  - Verdict: Too weak, low [unchecked]
  - Evidence: Manpower never binds after mid-2276: run 8 ended with 34k idle.
  - Proposed: Mars Beneath the Waves: `conscription_factor 0.05` ->
    `experience_gain_army_factor 0.10`. The Rites: `recruitable_population_factor 0.03` (a
    state-category modifier in vanilla's docs) -> `conscription_factor 0.03`, or
    `experience_gain_army_factor 0.05`. Optional: the Drowned Harvest's `monthly_population 0.1` ->
    `resistance_decay 0.10`.
  - Where: `mltd_ideas.txt:369`, `:281`, `:503`.
- **14. Call for People, Indoctrinate the Faithful**
  - Verdict: Too weak, low [unchecked]
  - Evidence: Both pay manpower that binds nothing. Run 8 never used Call for People.
  - Proposed: Call for People: **+20 population a point** in the capital (OWB's
    `add_state_population`), the mod's real currency. Indoctrinate: the target **loses double**
    what MLT gains, a pre-war weapon.
  - Where: `mltd_decisions.txt:663`, `mltd_cult_call_people_tt`; `mltd_scripted_effects.txt:645`
    (`mltd_indoctrinate_transfer`), `mltd_op_indoctrinate_the_faithful_tt`.
- **15. The Wet Market idea**
  - Verdict: Too weak, low [unchecked; three lenses]
  - Evidence: +20 % `caps_income_modifier` multiplies only the M'lyeh node's 3.4-17 caps a quarter,
    i.e. +1-3. The +4 % consumer goods is permanent and grows with every factory. Net, a small
    loss.
  - Proposed: `consumer_goods_factor` **0.04 -> 0.02**, or drop it. Optionally,
    `caps_income_modifier` -> `caps_flat_income_modifier = 5` here and in The Salt Road.
  - Where: `mltd_ideas.txt:298-299`, `:549`.
- **16. Theft shares have no ceiling**
  - Verdict: Risky, low [unchecked]
  - Evidence: A quarter of the victim's store, /5 as mirelurks, uncapped. A 20,000-rifle depot (run
    8's own AI held 17,000) gives 1,000 mirelurks (~18,000 IC, ~30 % of the plan's 2282 arms
    output) on day one.
  - Proposed: `clamp_temp_variable = { var = mltd_theft_brood max = 750 }` after each `/5`, and say
    so in each theft tooltip.
  - Where: `mltd_act4_focus.txt:263`, `:422`; `mltd_act5_focus.txt:250`, `:561`, `:1068`, `:1313`;
    `mltd_act6_focus.txt:268`, `:839`.

### 2b. MLT's AI only (fair play: preferences and the human's own actions only)

- **A1. The great-war holds have no strength test**
  - Verdict: Risky, high [unchecked; two lenses and the runs]
  - Evidence: The Turbines Sing, The Sea Against Mars and Black Water Rising hold an AI only on
    readiness and not losing. Readiness is capped at 20 divisions. A focus's declaration skips
    `mltd_ai_safe_by_strength`. In run 8's world (the Legion holding the NCR, Lost Hills and
    northern Mexico by 2282), a 63-division, 39-state MLT would declare. Run 3 lost to a 47-state
    Broken Coast.
  - Proposed: Add `NOT = { <target> = { strength_ratio = { tag = ROOT ratio > 1.5 } } }`, waived
    while the target fights a third major (the strike-at-war idiom). Add no date escape: a stalled
    close can recover, a capitulated MLT cannot.
  - Where: `mltd_ai_triggers.txt:1364`, `:1384`, `:1464`; readiness clamp at
    `mltd_ai_survey_effects.txt:74`.
- **A2. The Walk's five-Book gate**
  - Verdict: Too weak, high [upheld, with corrections]
  - Evidence: In all three full runs the last Book held the Walk. It came 767-1,054 days late
    against the plan's 1081. Book 4 (Arroyo) came through a network in runs 2 and 8. One operative
    can never reach 100 against counter-intelligence of 0.5 or more. A four-Book Walk would have
    moved the Final Ritual ~160 / ~270 / ~25 days.
  - Proposed: Preferred: lower the Books' network gate **99.9 -> 74.9**. It fixes the step that
    bound runs 2 and 8, and a spying human gains too. Pair it with running
    `mltd_ai_book_network_arr` / `_pmr` from the Kingdom on. The alternative is a 4-Book Walk,
    which leaves the fifth Book a skippable gift. Both touch the human game.
  - Where: `Mirelurk Tribe (MLT) Focus.txt:1428`, `:1468`, `:1506`, `:1544`, `:1582` (or `:1715`);
    `mltd_MLT.txt:361`, `:378`.
- **A3. Old Castro is never hired**
  - Verdict: Too weak, medium [upheld]
  - Evidence: No run logged his hire; operative slots never exceeded 2. Run 212246 banked 802-853
    PP with an agency and still did not hire him. His factor-100 weight stays under vanilla's
    `CRITICAL_IDEA_PRIORITY = 400`. Round 25's `pp_spend` id `cultural_advisor` is probably inert:
    the engine's AI code names six vanilla slots, and this is not one (a skeptic's reading of
    `hoi4.exe`, unverified).
  - Proposed: `ai_will_do` **100 -> 10003** (OWB's idiom for a guaranteed advisor). He still costs
    the human's 150 PP.
  - Where: `common/characters/MLT.txt:442`.
- **A4. No opening on CCW**
  - Verdict: Too weak, high [upheld; the proposed diagnosis refuted]
  - Evidence: Check (a) failed in all 7 runs. TRL took CCW on days 168-245. MLT's first war came on
    day 630, from Expanding M'lulu's Domain. War support and political power do not explain it: no
    justification ever started, whatever their level. The `-150` hypothesis is contradicted: the AI
    justified on MDT at a lower net value.
  - Proposed: No content number fixes it. List `mlt_expanding_mlulus_domain` above
    `mlt_protect_the_southern_crossing` (~28 days sooner). Accept the gap. Any A/B test should vary
    Black Hollows Night's manpower or OWB's `WARGOAL_GENERATION_STRENGTH_FACTOR`, not the `-150`.
  - Where: `ai_strategy_plans/mltd_MLT.txt:65-66`. Plan `:907`: "242-543" -> **"95-543"**.
- **A5. The NCR stage**
  - Verdict: Too weak as framed; the proposal **refuted**
  - Evidence: Relaxing the cult gate (40 -> 20 or 25 %) and moving the stage's fallback to 2282
    would have changed nothing in either cited run. In run 8 the NCR was gone before the Final
    Ritual ended. The binding gate is `mltd_ai_north_done`, which no run ever set (north = 39 of
    79). A 2282 fallback skips the north, New Reno and the Broken Coast gates, with no strength
    test on the NCR: run 2's endless war again.
  - Proposed: Leave `2284.1.1`. The cult threshold is cosmetic (AI cults never grow); tie its date
    to 2281 if anything. Find out why `mltd_ai_north_done` never sets: a safe target keeps holding
    northern land and is never conquered.
  - Where: `mltd_ai_triggers.txt:250-260`, `:661-673`; `mltd_ai_survey_effects.txt:84-102`.
- **A6. The Broken Coast courtship has no end date**
  - Verdict: Too weak, low-medium [upheld; proposal moved]
  - Evidence: The Covenant's gates (cult 50 %, token, coverage 0.3, civilian intel, the VIC/DRE
    coast) were never in an AI's reach. While courted, BRK fails `mltd_ai_safe_target` and The
    Coast Goes Under waits. Round 28c's review already ends the courtship on
    `mltd_brk_covenant_lapsed` / `_joined`.
  - Proposed: Do not date the courtship itself: that opens BRK fronts mid-NCR-war and re-closes the
    NCR stage. In `mltd_ai_may_drown_the_coast`, add: the courtship is over, **or** date > 2282.1.1
    with the Covenant untaken and out of reach. Test `mltd_ai_safe_by_strength`, as Drown the Dance
    does. Drop the Bone Dancers half. Update the plan's deviation line.
  - Where: `mltd_ai_triggers.txt:1263-1297`.
- **A7. Act III's list order**
  - Verdict: Risky, medium [unchecked]
  - Evidence: The late plan lists Drown the Dance before The Tide-Wall. In the AI's usual world the
    Brotherhood in Washington is gone by 2279, so The Tide-Wall is a free payout that opens the
    close. Round 28c's `mltd_ai_act3_path_taken` already ends the 2281 escapes once any Act III
    focus is done.
  - Proposed: List **The Tide-Wall first**.
  - Where: `ai_strategy_plans/mltd_MLT.txt:322-323`.
- **A8. Act V/VI side wars during the great war**
  - Verdict: Risky, medium [unchecked]
  - Evidence: Blood in the Water, the Rites, the Crusade and The Drowned God Sleeps hold only on
    readiness and a safe target. Nothing holds them while the Legion's or Texas's war runs. Run 8's
    army never met even its peace target.
  - Proposed: Hold the three Act V side wars while `has_war_with = CES` and CES has not
    capitulated, and The Drowned God Sleeps during an uncapitulated Texan war (The Serpent Drowns'
    idiom). Add a `# AI deviation: war BOS WHT EHT HEA ...` line.
  - Where: `mltd_ai_triggers.txt:1399`, `:1415`, `:1446`, `:1484`.
- **A9. The army sits under its target**
  - Verdict: Too weak, medium [the power lens's version refuted; the AI lens's upheld]
  - Evidence: Run 8 held 63 of 88 divisions (0.70) while factories doubled. The idle 17k infantry
    weapons suit no late template, and `mltd_ai_army_short` was already on the whole time. So a
    further `ai_wanted_divisions_factor` push is refuted. The suspect: every line template's
    anti-tank company is `essential`, so a division short only of it sits under OWB's 0.95
    peacetime deploy threshold. Unverified.
  - Proposed: First log `anti_tank_equipment` and the deployment queue in SNAP
    (`build_telemetry.py`). Then add `equipment_variant_production_factor id = anti_tank_equipment`
    only while the stock is below ~1,000: it costs water the mirelurks need.
  - Where: `mltd_MLT.txt` section A (beside `:53`); the telemetry template.
- **A10. The AI's cult operations never run**
  - Verdict: The support-equipment diagnosis **refuted**
  - Evidence: Run 3 held support for years and still nurtured nothing. In run 8, support stayed
    plentiful for ~1,100 days with no operation. What binds is operatives and the strength-20
    network: the Book networks (900) and OWB's rescue (1000) outrank the cult blocks (850).
  - Proposed: Make sure an operative builds a strength-20 network in `mltd_ai_cult_target` once the
    Books are read. Log that network's strength in SNAP. A3 (Old Castro) comes first.
  - Where: `mltd_MLT.txt` section D.
- **A11. The AI's slow research**
  - Verdict: The "too few slots for the AI" verdict **refuted**
  - Evidence: `anti_tank_tech_1` was forced from 2276 yet finished 960 days after its start year,
    while unforced techs filled the slots. That is weighting, not slots.
  - Proposed: An AI-only research weight on the anti-tank and industry categories, or a stronger
    push on `anti_tank_tech_1`. No slot change for the AI's sake.
  - Where: `mltd_MLT.txt:134-140`.
- **A12. The AI's post-ritual 300k guards**
  - Verdict: Disputed, low
  - Evidence: No AI run exceeded 253k after the ritual, so the Leviathan and Tides guards are dead
    for the AI. The AI lens calls that harmless, because it sat on idle mirelurks and manpower.
  - Proposed: Optional: 300,000 -> 150,000.
  - Where: `mltd_decisions.txt:452`, `:589`.

______________________________________________________________________

## 3. About right - leave alone

**The big blocks.** The skeptics defended these against the lenses.

- **The permanent gifts** (`mltd_scripted_effects.txt:130-134`: +20 % attack, defence, organisation
  and stability, +30 % recruitable population). **Refuted twice** as too strong.
  - OWB's own creature capstone, `RCK_roach_king_6`, is the same +20/+20/+20 plus more.
  - Stability binds at war: run 2, the only post-ritual war, sat at 70-83.
  - The Final Ritual that buys the gifts is Act II's close, and CLAUDE.md leaves Acts I-II's
    rewards as sized for their time.
  - Pinning them below the rented 20 would make the ritual a nerf.
  - One rule stands: **no later content adds a permanent army attack, defence or organisation
    modifier.** On the plan's path the stack reaches +40 % attack and +30 % defence at the ending.
    Between 2279 and 2284 MLT sits at the Roach King's capstone level; only the ending takes it
    past OWB's maximum.
  - If a human play-test sees the NCR fall clearly before 2282-04, pin the permanent Tide and Shell
    at 0.15 and keep the rentals at 0.20.
- **The Deep Ones Walk's free Star Spawn division** (14,400 IC). **Refuted** as too strong.
  - OWB's single-focus grants reach 11,000-19,500 IC (Eagle Rock's `eag_tanks`, the NCR's
    `ncr_butter`).
  - The division's piercing of 18 does not dominate the power armour it meets next.
  - A half-equipped division would stay half-strength for ~800 days.
  - Optional trim: drop only the 16 spare.
- **The Final Ritual's price** (toll `0.0025` at `Mirelurk Tribe (MLT) Focus.txt:1761`; penalties
  at `mltd_ideas.txt:72-76`).
  - The proposal to bar gifts during the rituals was **refuted**. Renting organisation back is
    worthless at peace, and the rents already eat most of the ritual's political-power margin.
  - Keep `0.0025` and the 200,000 gate. Only if the next AI run again sits flat at ~140k, consider
    the plan's gentler `0.0014`.
- **The Legion, interior and Texas wars.** The "victory laps" verdict was **refuted**: it compared
  2282 MLT with 2275 rivals, and every run shows the rivals growing. No reward inflates these wars.
  Keep the plan's 18 / 15 months [M].
- **The NCR war for a human.** 29 months [M] is plausible. Add no army bonus before 2282.

**Focuses:** The Call of the Deep Ones, the Grand Ritual, the Kingdom's edits, Feed the Spawning
Pools, The Spreading Cult, The Wet Market focus and seller prices (25 IC a cap, OWB's rate), Gifts
from the Deep, the Books, Eyes in the Sound, Salt on the Broken Coast, The Bone Shore, the Hail /
Drown the Dance pair, The Tide Turns South, Act IV's chapter, beads and war, the Act V and VI heads
and wars, The Last King Kneels, the endings (the Priestess aside, section 5), the ten spoils, and
R'lyeh Rises' 300-state gate.

**Ideas:**

- The Grand Ritual's idea; Children of the Deep's `special_forces_min = 80` (`mltd_ideas.txt:96`).
  Do not raise it, but it is not the only brake on the monsters: OWB's tactics perks (+70, ~200
  army XP) and `mixed_army_doctrine` (+40) take the cap to 170-210 for any country, so IC is their
  real limit (corrected after review).
- The act ideas, the 180-day war ideas, The Drowned South, The Dreamer Wakes, Return to the Sea,
  the `mltd.51` choice, and the spoils' permanent and timed ideas (The Legion's Steel, Black Water
  Visions).
- The creature build-cost stack: -15 % on the plan's path, -25 % peak, -40 % only in a 9-day edge
  case. It stays under the Roach King's -30 % plus OWB's continuous -10 %. Add no fourth cut.

**Units and systems:**

- The Star Spawn's six combat stats (1.2-1.6x OWB's best per width, paid for at 1.3-2.1x the IC),
  the Deep Ones battalion, and the Leviathan as a ship.
- The Deep Ones summon, Call for Equipment, the Offering of the Tides, the ritual gates, the
  flavour events, the Book expeditions, and Cult Infiltration's war penalties (self-limiting
  through war decay).

______________________________________________________________________

## 4. Corrections the plan still owes

These are model errors, not balance changes. Earlier passes brought the plan up to rounds 28b and
28c; these remain.

- **Decimation.** OWB's default Exodus rule is `FACTORY_DECIMATION_ONLY` (OWB
  `00_game_rules.txt:4066-4071`). It keeps conquered people and removes factories only by
  `round(level x 2 x share - 2.5)` for arms (`- 3.5` for civilian) (`exodus_effects.txt:112-122`).
  At MLT's stability that means a factory is lost only at ~6-13 levels, and no state on the map
  starts above 9 civ or 7 mil. The halving call is commented out (`00_on_actions.txt:474-479`).
  - Replace the halving lines at plan `:100`, `:141`, `:166`, `:289`, `:309`, `:563`, `:661`,
    `:879`, and CLAUDE.md's spoils note.
  - Re-derive the snapshots as ranges: ~70-80 civ / 65-75 mil at 2279-11, ~175 / ~125 at 2282-05,
    280+ / 230+ at 2285-12. Land taken from raiders arrives pre-stripped.
  - Consequence: industry is not MLT's handicap; research is. Add no factory-output rewards.
    Optionally re-key The Drowned South's `industrial_capacity_factory 0.10` (`mltd_ideas.txt:388`)
    to `research_speed_factor 0.10`.
- **Water.** Conquered states bring their water: ~67 by the Kingdom, ~118 by 2278, 154 across the
  north without BRK, plus NCR 92 and MOT 132. Mirelurks are not special forces (OWB
  `creatures.txt:163`), so their lines are limited by IC. The monsters are limited by IC too: the
  100-battalion special-forces cap rises to 170-210 with OWB's spec-ops perks and
  `mixed_army_doctrine` (corrected after review). Fix plan `:33`, `:186`, `:344`, `:844-846`,
  `:884`.
- **2279-01 Deep Ones count** (`:405`): ~4, not 5-6, unless more lines move to Deep Ones (the water
  is there).
- **Templates** (`:345`, `:571-572`): the plan's Tide Wall and late levies drop the anti-tank
  company its own `:190-191` prescribes and the AI's templates carry. Piercing goes 8 -> ~21, and
  damage against power armour 50 % -> 65-80 %.
  - `check_plan_sync.py` compares only the AI templates' `regiments`, so writing the company into
    the template line fails the check. Either teach it to read `support`, or keep the company in
    the `#` comment.
  - Researching `anti_tank_equipment_tech_2` needs an AI `research_tech` entry or a deviation line.
- **Armour notes** (`:38-40`, `:143`). TCA's and WBH's opening power-armour divisions already
  pierce ~20 in 2275, enough for mirelurk `_1` and `_2`. The Legion's Prime Legionaries pierce
  ~6-7.
- **`:661`.** `specialized_industry_tech_7` needs `tools_tech_level_scientific`, which MLT cannot
  reach. Pick another tech, and update the deviation line at `:834`.
- **`:264`.** "Then only with caps under 50" is the AI's guard. A human keeps offering after the
  ritual, which raises the plan's late caps and Wet Market figures.
- **Research levers the plan gives up.** Born Warriors' +15 % research is dropped on day 81
  (`:86-87`) for manpower that stops binding in mid-2276. `OWB_continuous_research` (+10 %) is the
  alternative to Feed the Spawning Pools. The research note should name both.
- **The NCR peace.** The Legion shares the peace in OWB's Hoover war, so MLT may annex well under
  the NCR side's 86 states. Add a branch note for a Legion that eats the NCR first (run 8): take
  When Shady Sands Falls at once, fill the special-forces cap, and lead the Legion war with Star
  Spawn.
- **The Priestess note** (`:927-929`) leaves out the -10 % stability of `able_bodied_tribesmen` and
  the war penalty.

______________________________________________________________________

## 5. Risks the numbers cannot settle without a play-test

- **Stability after 2279.** The skeptics disagree, and it decides four rewards: the Abyss gift's
  +20 %, The Northern Waters' +5 %, The Unchained's +5 % and The Priestess Reigns' +20 %.
  - Run 2, the only late war, sat at 70-83 with harsher conscription laws.
  - On the plan's lighter `able_bodied_tribesmen`, that reads as roughly 85-98 in the NCR war and
    near the cap by 2285-86 (this review's estimate [M], not a measurement).
  - If it pins at 100, The Priestess Reigns' +20 % and The Unchained's +5 % go to waste. The
    Priestess fix is then to **add** a coring lever beside the stability, not to replace it:
    `maxium_core_cost_increase = -50` (OWB's key and spelling, `00_traits.txt:822`), or
    `core_creation_cost_factor` -0.10 to -0.15. A -0.25 cost factor saves nothing on the states
    that cost over 400 raw, which are exactly the Texan and Mexican ones: OWB multiplies before its
    300 cap (`coring_button_scripted_triggers.txt:189-218`).
  - If it sits below 90 at war, all four are live and stay as they are.
- **Whether the NCR war is a contest.** It is the test of the permanent gifts (section 3).
- **Whether a division draws a variant its country has not researched.** Vanilla fields captured
  equipment, so probably yes, which is why row 3 of section 2a matters.
- **A Legion that eats the NCR** (run 8). OWB's variance, not a number; watch A1.
- **The rivals' 2280s stockpiles.** OWB history gives the NCR, the Legion, Texas and Tlaloc none,
  so every theft size and the Canals' ~500 hatch is modelled.
- **The idle focus slot:** ~530 days in the NCR's war, ~150 in the Legion's, ~245 in Texas's. The
  lurk\_ fillers pay 2275 rewards and run dry around Texas's war.
  - Design option: open each act's chapter and spying heads on the previous act's war focus. For
    example, Mars in the Water would need The Turbines Sing, with the wars and closes kept behind
    the close through `available`.
  - That fills ~165 and ~130 days and shelters the next targets' cults before their wars.
- **The Covenant's VIC/DRE gate** (`mltd_act3_focus.txt:375-383`) rests on the Broken Coast's own
  conquests: the runs saw it take DRE, never VIC. Leading a faction may also pull MLT into the
  raiders' wars. Consider "BRK controls at least 12 states" instead.
- **Monster piercing from Act V.** Star Spawn pierce 18 and Deep Ones 10, against 40-75 late armour
  (MXC, Lost Hills, the Enclave, Tlaloc's robots). Do not raise the stat: it would dominate
  2278-82. Put an anti-tank company into the monster templates from Act V instead.
- **AI constructs never seen in a run:**
  - the `hidden_trigger` holds in shared focuses' `available`;
  - `has_wargoal_against` in an `ai_strategy` `enable`;
  - `cultural_advisor` as a `pp_spend` id;
  - `research_tech` against the AI's own weights;
  - the invitations' odds and refusal war goals;
  - every story act.

The next spectator run on current code should come before any of the AI tuning above except A3.
