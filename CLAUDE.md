# CLAUDE.md

## Reference material

This is a submod of **Old World Blues** (OWB), installed at:

`C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196`

Use it as the reference for all script syntax, and as the source for any file this submod
overrides. Vanilla HOI4 is at `C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV`.

Read `<OWB>/doc/OWB_MODDING_README.txt` first - OWB's official submodders guide: the `dependencies`
requirement, the six nation categories, advisor/chief/theorist suppression flags, decimation on
state transfer (its halving is out of date: see The story acts > *The spoils*), the AI war-creation
system, reserved country-leader ID ranges. Same folder: `border_wars.txt`, `project_exodus.txt`,
`read_me_adding_a_new_country.txt`, `mojave_territories_systems.txt`.

MLT specifics from OWB's `history/countries/MLT - Mirelurk Tribe.txt`: it is flagged
`is_tribal_nation` and `is_oregon_nation`, and already sets `no_generic_chief`,
`no_generic_high_command` and `dont_give_tribal_generic_{chiefs,high_command,theorists}` - generic
advisors are suppressed, so any new advisor must be added explicitly. Its capital is state `358`
(Crowlands, 2,558 pop at start); it also owns `451` (8,451). MLT + the four nations
`mlt_kingdom_of_mlyeh` requires it to absorb (TRL, RBT, CCW, DIS) total ~75,000 population at game
start. Its only creature sub-unit is `amphibious_beast_creature` on `amphibious_beast_equipment`
(variants `_1`, `_2`, `_armor`, `_king`).

## Project

**OWB - Rising Tide** - a Hearts of Iron IV submod of *Old World Blues* focused on the Mirelurk
Tribe, country tag `MLT`. OWB is declared as a dependency in `mod_folder/descriptor.mod`.
Everything the game sees lives under `mod_folder/`; the repo root holds docs, tooling and source
art that must not ship.

**Keep [`CONQUEST_PLAN.txt`](CONQUEST_PLAN.txt), the code and MLT's AI in step.** The plan is the
simplified ideal strategy: a human MLT's conquest - every focus, decision, operation, war,
production and research step, one per line, with `# snapshot` lines of expected strength - kept so
that balance and gameplay work has a perspective and nobody re-derives the timeline. MLT's AI (see
*MLT's AI* under How the mechanics are wired) follows it broadly and adapts where a game drifts
away from it. All three must agree after every change, in the same change:

- A change to a number, focus, decision, operation, unit or mechanic the plan uses updates the plan
  \- the affected operations and their `#` comments, the snapshots after them and the notes at the
  end - **and** the AI's matching focus order, conquest stage, guard, weight or template.
- A change to the AI updates the plan wherever the AI follows it. Where the AI deliberately does
  something else, the plan's notes say so in a line
  `# AI deviation: <focus|war|research|operation|template> <ids> - <why>`.
- `python check_plan_sync.py` must pass. It fails when an id the plan or the AI names does not
  exist; when the plan gives a state to a country that does not own it at game start, or writes a
  state under the wrong name; when a focus, war, tech, `mltd_op_` operation or division template
  (battalions and support companies alike) in the plan has no AI counterpart and no deviation line;
  when the AI conquers a country the plan never names; when a deviation line no longer applies; or
  when the telemetry misses a focus, tech or conquest target the plan or the AI uses (rebuild it
  with `python build_telemetry.py`); or when a focus of ours takes any length but 7, 30, 60, 120 or
  180 days (Project > *Focus lengths*, below). It cannot check other numbers - those stay a reading
  job.

**The code is the single source of truth for costs.** This file explains mechanisms and names the
file, effect, variable or loc key that holds a number; it does not restate what anything costs -
focus lengths, political power, manpower, caps, population or equipment prices, operatives,
cooldowns, or the rituals' penalties and tolls. Read those in the script. Where a loc key repeats a
script literal, the two change together (the *Numbers in several places* notes say where).
`CONQUEST_PLAN.txt` is the one document that quotes costs, because it models them.

**Rewards scale to when they are taken** (round 28b; every focus, decision and event option). A
reward must still matter on the day it is taken: a few hundred rifles is noise against the ~200 or
more military factories of `CONQUEST_PLAN.txt`'s 2285 snapshot. So a reward either:

- carries a modifier that grows with the economy it lands in: production efficiency or output,
  construction or research speed, compliance, or an `equipment_bonus` keyed by the archetypes MLT
  builds late (`amphibious_beast_equipment`, `mltd_deep_ones_equipment`,
  `mltd_star_spawn_equipment`, as `continuous_mltd_spawning_pools` is);
- or is a one-off sized to its moment from the plan's snapshots, and paid in what MLT fields then.
  From Act IV on that is mirelurks, through the archetype `amphibious_beast_equipment`, which gives
  MLT its best unlocked variant (as *Call for Equipment* does).

Thefts follow the same rule (The story acts > *Theft without producer*). Rewards taken before ~2278
(Acts I-II) were already sized for their time and stay. An act idea stays inside +-5-10 %; the
endings are the one place for large bonuses. Watch one stack: several rewards pull the same lever,
a build-cost cut on the three creature archetypes, and the engine adds them - Feed the Spawning
Pools, `mltd_the_pens_emptied` (option b of `mltd.51`) and `mltd_the_return_to_the_sea` (an
ending). They peak at -25 % with the first two, or -40 % if Return to the Sea lands in the pens'
last weeks. Check the stack before adding another: round 28c's reviews turned The Legion's Steel
into a defence and armour bonus and dropped the cut first staged for Black Water Rising.

**Every effect shows before it is taken** (round 28b; every `completion_reward`, decision
`complete_effect` / `remove_effect`, mission `timeout_effect` and event option). An effect whose
tooltip the engine draws correctly stays as it is. One it cannot draw runs in `hidden_effect`
behind a `custom_effect_tooltip` that says what it will do, true in every branch:

- A loop (`every_owned_state`, `every_country`) whose `limit` nothing passes yet previews as
  nothing, and an `every_country` names no country. The house writes one block per tag instead (The
  Drowned Knights and The Tide-Wall: WBH, then TCA), or a custom line (the spoils' compliance and
  works).
- An `if` whose limit may only hold later - a victim's stock, a state not yet held, Caesar's health
  \- is shown as `custom_effect_tooltip` ("If ... when the focus completes:") and
  `effect_tooltip = { <the native lines> }`, with the real `if` in `hidden_effect`. While the
  condition can still change, every outcome is shown; one that can no longer change (a completed
  focus, a country gone) shows as it is.
- A random pick (the offerings' state) or an amount computed at run time (a theft's share, a hatch)
  is a custom line that states the rule, printing the numbers through temp variables where the
  preview can read them.
- A focus that fires an event whose option carries the effects previews that option after its
  `country_event`, because the engine's preview names an event only by its title:
  `custom_effect_tooltip = mltd_event_brings_tt` and an `effect_tooltip` of the option (the
  Kingdom, the Call and the Walk; vanilla `australia_taog.txt:1390-1394`, OWB
  `Twin Mothers (TTM) Focus.txt:1830-1838`), or the trophy closes' own headers. Keep each such
  block equal to the option it shows.

**Native lines first, and few of them** (2026-09-24, the user's notes: too many focuses were too
text heavy, the Drowned Covenant first among them). The rule above says what a preview must show;
this one says how little text it may take to show it:

- An effect the engine draws is shown by its own line, in an `effect_tooltip` where it must not run
  yet (the faction founded, the invitee joining, the war goal); a `custom_effect_tooltip` is only
  the header over such lines ("If they accept:", "If they refuse:") or the one line an effect the
  engine cannot draw needs (a theft's share, the bunkers in The Warren).
- A branch whose limit is tested again at completion is written as a plain `if` / `else`: the
  preview draws the branch that holds when it is read, so a fallback shows only when it is the one
  due (a war focus's +50 political power against MLT's subject). From round 28c's review to
  2026-09-23 every such fallback was previewed beside the offer, under a line saying when it is
  paid. The exception is a focus whose `available` asks what its `if` asks: read off a plain `if` /
  `else`, its preview shows the fallback for as long as the focus cannot be taken. The three
  invitations are that case - Terms for the Citadel showed only its +50 from game start, with WBH
  leading OWB's Northern League (Gotchas > *OWB's Brotherhood leads the Northern League*) - so
  since 2026-09-25 each previews through an `if` of its own, which shows the offer unless the focus
  is running and the offer can no longer go (`focus_progress`), beside the real `if` / `else` in
  `hidden_effect`; both read one trigger (The story acts > *The invitations*).
- A side effect that hangs on the target's own storyline and would take a paragraph to preview is
  left out, not previewed: the war focuses lost theirs (Caesar's health, the Hoover outcome, Lost
  Hills' quarrel and the rest), and their targets' stability and war-support losses, which mattered
  little, gave way to a bonus against the target and The First Wave (The story acts > *The wars*).

**A long tooltip reads as blocks** (round 28c's balance review; every `completion_reward`, decision
`complete_effect` and event option that runs past a handful of lines). The effects are grouped -
what M'lyeh gains, what the target loses, the intelligence work, the war, the event that follows -
and the groups are separated by `custom_effect_tooltip = mltd_newline_tt`, the blank line (OWB's
`spacer_tt` idiom, value `" \n"`). A block keeps its neighbours' order from focus to focus, so a
reader finds the war where the last focus put it. Nothing runs differently: the spacer is loc only,
and it is the same key the rituals and the victory points already use.

Every literal such a tooltip repeats is listed under *Numbers in two places* or its system's own
notes.

**Focus lengths** (2026-09-25, the user: completion times were too inconsistent). Every focus of
ours takes 7, 30, 60, 120 or 180 days - the lengths OWB's own MLT focuses keep to (7 and 30) and
the two rituals already had. A focus's weight picks its length: a spying head, a light bead, a
chapter, a close, a war focus, a Book, the Kingdom's three children (The Spreading Cult, The Wet
Market, Gifts from the Deep), a spoils one-off or an ending takes 30; one that carries more - an
Act II bead that absorbed another focus, an invitation, a spoils idea focus, the Call, the Walk,
R'lyeh Rises - 60; the rituals 120 and 180. So an invitation takes twice its war twin's time, and
the offer stays the slow road. The cost in each focus's file is the number; `check_plan_sync.py`
fails on any length outside the five. Until then our focuses ran from 30 to 70 days, most in steps
of a week, and `CONQUEST_PLAN.txt` was re-timed with the change.

Current state: **first content drop, play-tested once** - the first run found summoned divisions
spawning without equipment (fixed in round 3 by the hidden equipment techs); everything since round
3 is not yet re-tested. That now includes visible decision cooldowns, the two offering decisions,
Feed the Spawning Pools as a continuous focus, the Star Spawn rebalance, capital victory points,
both animated portraits, the quadrupled summon costs, doubled gifts, custom division-template
counters, and the two OWB rewards that were taken away (the forced laws and Cultural Upheval).
Everything hangs off OWB's final MLT focus `mlt_kingdom_of_mlyeh`. `mltd_gifts_from_the_deep`
(15,16) sits directly below the tree's tail - a row under the Kingdom's two Rising Tide children,
*The Spreading Cult* (14,15) and *The Wet Market* (16,15) - with **no prerequisite line** to the
Kingdom - it gates on `has_completed_focus = mlt_kingdom_of_mlyeh` inside `available`. The five
**Books of M'lyeh** (`mltd_first_book` .. `mltd_fifth_book`) fan out under Gifts at relative (-2,1)
(-1,2) (0,1) (1,2) (2,1). Call of the Deep Ones (0,3) and the Grand Ritual continue straight down
the centre column, chained by `prerequisite`. Since round 27 the story acts carry on down the same
column (x = 15), to row 42 since 2026-09-24, and since 2026-09-24 The Deep Ones Walk and the Final
Ritual sit among them, below Act III and two rows apart (see The story acts); since round 28c the
optional spoils focuses flank the chapters on the spine's own rows. Progress through the column is
gated by how many Books have been read (`mltd_books_read`: 1 / 3 / 5). Round 13 (the conflict
sub-trees, the flavour events, the Book expeditions and the removal of the doctrine override) is
not play-tested either, and nor is round 14 (The Spreading Cult and The Wet Market, the Cult
Infiltration fixes, the Books' network gate and the category pictures), or round 15 (the cult
decisions' costs and titles, the plain `is_major` gate, the agency logo and *Hail M'lyeh*), round
16 (the list of cults, the defecting general, The Wet Market's seller and the new ritual and market
numbers), round 17 (the cult operations and Calls, the summons' spare equipment, the Kingdom's
trade node and the conflict war goals) round 18 (MLT's AI), round 19 (its telemetry), round 20
(MLT's AI after its second spectator run: the north first, the NCR's side, pockets, the army's
size) round 21 (after the third: an army sized by frontage and armed from OWB's marketplace, no war
on a stronger country, and the Broken Coast sub-tree with its Drowned Covenant) round 22 (after the
fourth: no new war below half the army's target, militia before infantry while the line is short,
the Washington sub-tree following whichever Brotherhood holds Washington, and the Bone Dancers
sub-tree), round 23 (the capstones' `is_ai` gates, `mltd_ai_strike_<tag>_at_war`, the opening's
order and anti-tank) or round 24 (the review fixes: the territory give-away, the 16 bare coverage
tooltips, the Wet Market's caps guard, the Bone Dancers' courtship and dead end, the Washington
existence guards, Guns for Both Sides, the Deep Ones summon's second population gate, the
nurture-cult guard, and the political power an AI now spends on Old Castro - which aimed at the
wrong category, see round 25) or round 25 (the Broken Coast's white peace with the Haida
Confederation the day it is thrown off Haida Gwaii; Old Castro's real spending category,
`cultural_advisor`; and checks (i) and (j) of the run report, which judged the Wet Market buyer
while it had no cause to buy and skipped the between-ritual Deep Ones summons that round 24 had
started guarding) or round 26 (the Leviathan: a summoned capital ship granted by the Grand Ritual,
its summon decision and its tech beside the Broken Coast's Personal Floating Palace) or round 27
(the story acts: the ten conflict sub-trees rebuilt as one spine of five acts and a finale below
the Walk, with the Final Ritual moved into it; new closes, chapters and trophies, Nuevo Aztlán,
R'lyeh Rises and three endings; see Round 27 below) or round 28 (the invitations' odds by the
historical-focus rule, Terms for the Citadel - the Drowned Covenant offered to the Brotherhood in
Washington - the refusals' expiring war goals, and four optional spoils branches; see Round 28
below) or rounds 28b and 28c (the user's two sets of notes on round 28: rewards that scale, every
effect shown, room for the tall icons, each northern nation courted or fought, the Broken Coast's
war twin and the spoils moved onto the spine; see Rounds 28b and 28c below) or round 28c's balance
review (the fourth research slot moved to Act III's close, the Drowned Rangers doubled, Old
Castro's hire weight, one set of gates for all three invitations, and The Last King Kneels' shorter
icon, which closed the spine up a row; see Round 28c's balance review below) or the changes of
2026-09-23 (summons that stay open once their units can be trained and bring their own
special-forces room, a slower cult decay, `bypass` on the story focuses aimed at a nation, and the
monsters' equipment icons; Testing > *2026-09-23*) or the changes of 2026-09-24 (Act II and III
moved above The Deep Ones Walk and The Final Ritual, so that each northern nation is courted or
fought before the Walk and the long ritual; a new cultural advisor, the Tide-Speaker, with -30 %
justification time; war focuses that grant a bonus against their target and The First Wave in place
of their target's stability and war-support losses; and lighter tooltips; see *2026-09-24* below)
or the fix of 2026-09-25 (OWB's Cannibal Territories trade, which bypassed itself once MLT held the
state and so shut the Barrows, is bypassed only when the player chooses to; Overriding OWB, Gotchas
\> *A bypass fires by itself*) and the invitations' previews of the same day, which showed only
their +50 political power while the invitee could not be asked (Project > *Native lines first, and
few of them*), and the league hand-over of the same day: Terms for the Citadel may ask a
Brotherhood that leads its faction - WBH leads OWB's Northern League from 2275 - and a yes brings
that faction's members into the Drowned Covenant (The story acts > *The invitations*), and the
focus lengths of the same day: every focus of ours takes 7, 30, 60, 120 or 180 days (Project >
*Focus lengths*).

The beats, each with its focus and what it does:

- Beat 0, `mlt_kingdom_of_mlyeh` (OWB, edited): no longer applies OWB's `itz_civilizing` ("Cultural
  Upheval", -10 % PP / -20 % stability for 365 days); now also adds **victory points** to the new
  capital (province 1983 M'lyeh +15, province 7064 Mireport +5), makes M'lyeh (358) MLT's main
  **trade node** (OWB's `create_map_node`, linked to Arroyo 337 and West Portland 23; caps rule
  only; round 17), and fires `mltd.1` (MLT) and `mltd.2` (world news, delivered to every other
  country); either option of `mltd.1` gives the (pre-recruited, role-less) character **The Drowned
  Herald** (`MLT_DROWNED_HERALD`) his general role via `add_corps_commander_role` (4 / 4-2-2-1,
  strong + enduring + swamp fox + animal friend - a notch below M'lulu), which the focus previews
  since round 28b (`mltd_event_brings_tt` and an `effect_tooltip` of the option)
- Beat 0a, `mltd_the_spreading_cult`, Kingdom-relative (-1,2): opens **Cult Infiltration** (the
  category, its two Call decisions and the two cult operations gate on it) and founds a cult at 20
  % in every neighbouring major (`mltd_cult_neighbouring_major`); with La Resistance it founds the
  agency *The Esoteric Order of M'lyeh*, under its own seal
  (`GFX_intelligence_agency_logo_mltd_esoteric_order`), if MLT has none (otherwise - no DLC, or an
  agency already founded - +50 PP); no other focus founds it, and the story acts' spying heads only
  upgrade it
- Beat 0b, `mltd_the_wet_market`, Kingdom-relative (1,2): permanent idea `mltd_the_wet_market` (+20
  % `caps_income_modifier` and a `consumer_goods_factor` penalty) and +40 influence with each of
  OWB's five Organization Marketplace sellers when the caps rule is on, and opens a seller of its
  own, **The Wet Market**, selling mirelurk equipment (otherwise +50 PP) - see The Wet Market
- Beat 1, `mltd_gifts_from_the_deep`: adds dynamic modifier `mltd_gifts_from_the_deep`; opens the
  **Gifts from the Deep** decision category; `mltd_gifts_max = 1`
- Beat 1b, `mltd_first_book` .. `mltd_fifth_book`: each requires **control** of a notable regional
  state - or, with La Resistance, a full-strength (100 %) intelligence network in it - Arago (150,
  DIS capital), The Warren (235, TRL capital), Paisley Pit (231, MDT), Arroyo (337, ARR), The Maw
  (274, PMR) - and **starts an expedition**: a three-event chain (`mltd.101-103` Tide ...
  `mltd.501-503` Abyss) with choices (war support against stability, or which of two named advisors
  dies), whose last event reads the Book - it sets `mltd_<n>_book_found`, which is what unlocks
  that gift's decision (Tide / Shell / Current / Brood / Abyss, in that order), and adds 1 to
  `mltd_books_read`. The focus itself only previews that reward under *When the book is found:*.
  Icon `GFX_goal_mltd_book` (OWB's `cho_scriptorium.dds` recoloured dark violet by
  `build_focus_icons.py`, with its own `_shine`).
- Beat 2, `mltd_call_of_the_deep_ones`: needs >= 1 Book; its only effect is
  `country_event = mltd.7` (previewed since round 28b, as the Kingdom's), whose single option
  spawns the first locked 20-width **Deep Ones** division at the capital, gives 25 army XP and sets
  flag `mltd_deep_ones_summon_unlocked` (opens **Children of the Deep** and its summon decision)
- Beat 3, `mltd_the_grand_ritual`: needs >= 3 Books and national population >= 100,000; **while
  selected** holds idea `mltd_the_grand_ritual` (stability, political-power, organisation and
  factory-output penalties, and a daily population toll on every state); on completion removes it,
  sets `mltd_gifts_max = 2`, grants `mltd_leviathan_tech`, raises the first **Leviathan** at
  Mireport if MLT controls it (`mltd_spawn_leviathan`; "Father Dagon", the pride of the fleet),
  sets flag `mltd_leviathan_summon_unlocked` (opens its summon decision; round 26, see The
  Leviathan), fires `mltd.3` + news `mltd.4`
- Beat 3a, Act II, *The Northern Waters* (`mltd_act2_focus.txt`, round 27): three branches of two
  focuses under The Grand Ritual since 2026-09-24 (rows 21-22; under the Walk until then): the
  Brotherhood in Washington, the Broken Coast and the Bone Dancers. They spy, rob and court, and
  each branch leads on to its nation's Act III pair (row 23), an invitation and a war, any one of
  which opens The Deep Ones Walk - see The story acts
- Beat 4, `mltd_the_deep_ones_walk`: since 2026-09-24 below Act III, at (0,5) of The Grand Ritual,
  row 25 (row 24 is left empty for its tall icon - Gotchas); it needs any one of Act III's six
  focuses (one OR prerequisite) and all 5 Books - until then it followed The Grand Ritual directly,
  on row 21. Its only effect is `country_event = mltd.8` (previewed since round 28b), whose single
  option grants tech `warbike_unlock_tech` (= The Deep Ones, see Naming: the unit becomes
  designer-available), adds permanent idea `mltd_children_of_the_deep` (`special_forces_min = 80`),
  unlocks the Deep Ones template, spawns the first locked **Star Spawn** division and sets flag
  `mltd_star_spawn_summon_unlocked` (opens its summon decision)
- Beat 5, `mltd_the_final_ritual`: sits at (0,2) of the Walk, row 27, since 2026-09-24 (row 26 is
  left empty for its tall icon - Gotchas; round 28b put it at (0,4), row 25). Since 2026-09-24 it
  needs The Deep Ones Walk, and national population >= 200,000; from round 27 to 2026-09-23 it
  needed any one of Act II's three branch ends, and Act III came after it (earlier on 2026-09-24,
  any one of Act III's six). While selected it holds idea `mltd_the_final_ritual` (heavier
  penalties, war support included, and a heavier toll). On completion it removes the idea, grants
  `mltd_star_spawn_tech`, unlocks the Star Spawn template, makes all five gifts permanent and hides
  the Gifts from the Deep category (Children of the Deep stays, for the three summons and the
  offerings; since 2026-09-23 the Star Spawn summon stays open beside the trained unit), and fires
  `mltd.5` + news `mltd.6`
- Beat 6, Acts III-VI (`mltd_act3_focus.txt` ... `mltd_act6_focus.txt`, round 27): four acts, rows
  23-40. The north decided (*The Stars Are Right*: since round 28c six focuses in three pairs, each
  northern nation invited or fought - the invitation and its war twin exclude each other - since
  2026-09-24 each pair under its nation's Act II bead and before The Deep Ones Walk and The Final
  Ritual, and closed after the ritual by The Tide Turns South at 50 controlled states or from
  2281); the NCR (*The Drowned Republic*); the Legion and the interior (*The Sea Against Mars*);
  the south (*All Waters Are One*). Acts IV-VI are each a chapter, a fan of branches that spy, rob
  and declare the act's wars, and a close; Act III is a fan, then the Walk and The Final Ritual,
  then a close. Every close fires an event and world news, and Acts IV and V offer their trophy as
  a choice; each close but Act III's waits for its great war to be won - see The story acts
- Beat 6a, the spoils (`mltd_spoils_focus.txt`, round 28; restructured in round 28c): ten optional
  focuses in four groups, one group after each of Acts III-VI's closes: two for the north, four for
  California, two for the interior, two for the south. None is chained; each flanks, on the spine's
  own row, the chapter that follows its close (rows 29, 33, 37 and 41). They gate nothing and pay
  off the land the acts conquer: compliance or resistance in conquered cores, mirelurks hatched per
  held state, a building slot and an instant factory in each held works state, a tech bonus, two
  timed ideas, and one permanent idea per group (two in California) - see The story acts > *The
  spoils*
- Beat 7, `mltd_rlyeh_rises` and the endings (`mltd_finale_focus.txt`, round 27): rows 41-42.
  R'lyeh Rises needs 300 controlled states; it adds victory points in M'lyeh, sets the global flag
  `mltd_rlyeh_risen` and fires `mltd.70` + news `mltd.71`. Then one of three mutually exclusive
  endings follows - *The Dreamer Wakes*, *The Priestess Reigns* or *Return to the Sea* - each a
  permanent idea and a closing event (`mltd.72-74`)

Plus, independent of the tree: the **continuous focus** `mltd_continuous_spawning_pools` (*Feed the
Spawning Pools*, -15 % creature equipment build cost while selected), two **offering** decisions
that trade population for caps and for capital water (in the Children of the Deep category, open
from the Kingdom onward), an MLT-only intelligence operation `mltd_op_indoctrinate_the_faithful_*`
(La Resistance only; manpower taken from the target, scaled by the target's own, and on a critical
success one of the target's generals defects), a colour-graded (darker, colder) M'lulu portrait +
small icon overriding OWB's textures by path, and (via the `common/characters/MLT.txt` override)
M'lulu's field-marshal traits gain `animal_friend_trait` + `naval_invader` while Coral Prophet
Anastasia gains `animal_friend_trait` and a bespoke portrait (`GFX_Portrait_mltd_anastasia`). MLT
also gains a spymaster advisor, *Old Castro* (`MLT_OLD_CASTRO`), whose trait gives +2 operative
slots (La Resistance only). From *The Spreading Cult* on (beat 0a), **Cult Infiltration** grows
cults of M'lyeh abroad - founded and nurtured by La Resistance operations on any country MLT's
network reaches, and drawn on by two untargeted decisions for manpower or equipment: they wither
every week, faster the stronger they are, and at war with MLT they cost their country stability,
war support, organisation and factory output, and raise its air accidents.

**Round 13** (not yet play-tested) added three more systems.

Its **conflict sub-trees** set the tribe's intelligence agency, *The Esoteric Order of M'lyeh*, to
spy on, rob and destabilise one of OWB's big wars each. There were eight at first and ten from
round 22: 46 shared focuses in `mltd_conflicts_focus.txt`, beside the trunk. Their targets:

- the NCR and the Hoover Dam (`NCR`, `MOT`);
- Texas (`TBH`, `LNS`);
- the Washington Brotherhood (`WBH`);
- Caesar's Legion (`CES`);
- the Lost Hills Brotherhood (`BOS`);
- Tlaloc and his heirs (`TLA`, `MAX`, `MOC`, `ZAP`, `ARM`);
- Heaven's Guard's holy wars in Idaho (`HEA`);
- the Utah road war between the White Legs and the Eighties (`WHT`, `EHT`);
- and, courted rather than robbed, the Broken Coast (`BRK`, round 21) and the Bone Dancers (`BDT`,
  round 22).

Each sub-tree was a root that upgraded the agency, then two or three middle focuses gated on La
Resistance tokens or coverage, then a capstone keyed to the target's own OWB storyline. **Round 27
replaced them with the story acts** (below): the same focuses, most under their old ids, rebuilt as
one spine down the centre column, with no intel gates.

Round 13 also added **ten Lovecraftian flavour events** (`mltd.9-18`), drawn from a monthly pool
once the Kingdom stands. Each fires at most once, never within 120 days of another, with effects no
bigger than OWB's own `flavour.2`. Round 15 adds *Hail M'lyeh* (`mltd.19`) to the same pool. It is
the one event that can recur, at most once a year, and it hands MLT a civilian infiltration token
on a random country its network reaches.

The five **Book focuses are now expeditions**: each only previews its Book and starts a three-event
chain (`mltd.101-103` ... `mltd.501-503`) in which the player chooses war support against
stability, or which of two named advisors dies, and whose last event actually reads the Book - see
Book expeditions.

**Round 27** (not yet play-tested) turns the tree's second half into a story. Act I - the national
tree from the Kingdom to The Deep Ones Walk - is unchanged. Five acts and a finale continue down
the centre column:

- *The Northern Waters* (Act II): three branches under the Walk (under The Grand Ritual since
  2026-09-24), any one of which opened the Final Ritual until 2026-09-24;
- *The Stars Are Right* (Act III): the north's answer after the ritual (before the Walk and the
  ritual since 2026-09-24) - the Tide-Wall, the Covenant, or the Bone Dancers' invitation or
  drowning;
- *The Drowned Republic* (Act IV): the NCR;
- *The Sea Against Mars* (Act V): the Legion, Lost Hills, Utah and Heaven's Guard;
- *All Waters Are One* (Act VI): Texas, Nuevo Aztlán and Tlaloc;
- *R'lyeh Rises*: the finale, whose three mutually exclusive endings close the campaign.

Acts IV-VI are each a chapter focus on the spine, a short fan of branches that reconverge through
one OR prerequisite, and a close; Act II is a fan between the Walk and the Final Ritual, and Act
III a fan off the Final Ritual, closed by The Tide Turns South. Every close fires an event and
world news. The 39 story focuses are shared focuses in six files. 27 are the old sub-trees' focuses
under their old ids, 12 are new, and the other 19 were merged into the focus beside them. Only the
invitations still have intelligence gates - the Covenant and Hail the Drowned King then, all three
since round 28c's balance review - and every other story focus is takeable once its target is gone
or is MLT's subject. The three war closes wait for the NCR, the Legion and Texas to be beaten - see
The story acts.

**Round 28** (not yet play-tested) adds to the story acts without touching their spine:

- *The odds.* An AI's answer to each invitation reads the game's historical-focus rule. A
  historical Broken Coast always swears to the Drowned Covenant and an unhistorical one half the
  time; the Bone Dancers always do, as before. Each invitation's description ends with a line, read
  from the same rule, that says how likely the answer is.
- *Terms for the Citadel* (`mltd_wbh_terms_for_the_citadel`), a third invitation in Act III beside
  The Tide-Wall, offers the Drowned Covenant to the Brotherhood in Washington. A historical
  Brotherhood never accepts; an unhistorical Washington Brotherhood accepts half the time and the
  Northwestern one a tenth. An accepted alliance closes the Broken Coast's Covenant, and a Broken
  Coast sworn to the Covenant closes Terms; a refusal closes nothing. (Round 28 also closed The
  Tide-Wall on an accepted alliance; since round 28b Terms and the wall exclude each other
  outright.)
- *What a refusal costs.* The offer is the slow road and grants no war bonus, and every refusal -
  the Broken Coast's, the Bone Dancers' or the Brotherhood's - leaves MLT only an
  `annex_everything` war goal that expires after a year. (Round 28 also left The Tide-Wall open
  after a refused Terms, without its war bonus; since round 28b a refused Terms leaves only the war
  goal.)
- *The spoils branches* (`mltd_spoils_focus.txt`): four optional branches of three economy focuses,
  one off each of Acts III-VI's closes, that pay off conquered land and gate nothing. Round 28c
  rebuilt them as ten unchained focuses beside the chapters.

**Rounds 28b and 28c** (not yet play-tested) answer the user's two sets of play-test notes on round
28:

- *Two house rules*, for the whole mod: rewards scale to when they are taken, and every effect
  shows before it is taken (Project, above). Under the first, the thefts of Acts IV-VI became
  shares of the victim's store, paid in mirelurks; `mltd.51`'s two options became ideas; and Black
  Water Rising lost its flat energy. Under the second, previews were rewritten across the tree and
  its events and decisions, from what the Kingdom's event brings to the late acts' conditions.
- *The pairs.* Each northern nation now has an invitation and a war twin, side by side on Act III's
  row and mutually exclusive both ways: Terms for the Citadel and The Tide-Wall (the Brotherhood in
  Washington), The Drowned Covenant and The Coast Goes Under (the Broken Coast), Hail the Drowned
  King and Drown the Dance (the Bone Dancers). The Coast Goes Under
  (`mltd_brk_the_coast_goes_under`) is round 28c's one new focus: the Broken Coast is courted first
  and fought only by choice. The Tide Turns South's OR names all six.
- *Room for the tall icons.* The Final Ritual's and The Last King Kneels' icons stand far taller
  than a focus and grow upward, so each was given an empty row above it and the next focus directly
  below (Gotchas). The balance review below then gave The Last King Kneels a short icon and took
  its row back.
- *The spoils on the spine.* Round 28's twelve focuses in four side branches became ten, none
  chained, each flanking the chapter that follows its close: two for the north, four for
  California, two for the interior, two for the south.

**Round 28c's balance review** (not yet play-tested; `story_rework/BALANCE_REVIEW.md`, whose
section 0 records which of its proposals the user took). Six changes, three of them the review's:

- *The fourth research slot comes at Act III's close.* `add_research_slot` moved from The Last King
  Kneels to The Tide Turns South, so MLT fights the NCR's war on four slots where it fought it on
  three; `mltd.40` option a is now the fifth, and the total is unchanged. Every rival starts on
  four or five and gains more from its own tree.
- *The Drowned Rangers are worth choosing.* `mltd.40` option b, the trophy that stood against a
  research slot, doubled its army attack and defence (its organisation and the idea's shape are
  unchanged) and doubled its army experience.
- *Old Castro is hired.* His `ai_will_do` is OWB's 10003, the weight it gives an advisor the AI
  must take; a plain 100 never got him hired in a spectator run (MLT's AI > *Cults and the
  market*).
- *One set of gates for the three invitations*, the user's own design: each asks the invitee's cult
  at 40 %, its civilian infiltration token and a quarter of it covered, plus one rival gate. The
  Covenant gave up the tree's two heaviest tests, Hail the Drowned King the Odious King, and Terms
  for the Citadel, which asked for no intelligence at all, gained all three (The story acts > *The
  invitations*).
- *Long tooltips read as blocks*, a house rule of its own (Project, above): a focus's or an
  option's effects are grouped and the groups separated by `mltd_newline_tt`.
- *The Last King Kneels wears a Texan icon*, `GFX_goal_TBH_The_Last_Piece` (100x88, a claw closing
  on the map of Texas) in place of the 164x146 ghoul king that was neither Texan nor short. With no
  tall icon there the empty row between Act VI's wars and its close went, and the spine closed up:
  R'lyeh Rises, the south's spoils and the endings each moved up a row.

Also declined, and so still as they were: the Drowned Hoard's cooldown, the Wet Market's ungated
lots, a cap on the Star Spawn summons and one on the Leviathan fleet (Plan > Medium priority).

See The story acts > *The invitations* and *The spoils*.

**2026-09-24** (not yet play-tested; the user's notes on the mid-game): after the Kingdom the tribe
stood still through the long ritual column while its neighbours grew, the wars that need no
justification sat behind The Final Ritual, and the north is full of small straggler nations - the
Koover Union (BEL) among them - each a slow justification. A second set of notes the same day asked
for The Deep Ones Walk to sit just before the ritual, for war focuses that bring a bonus against
their target and an immediate buff instead of stability and war-support losses of little
consequence, and for less text. Five changes:

- *Acts II and III before the Walk and the ritual.* Act II hangs off The Grand Ritual (rows 21-22),
  and each northern nation is one column of the tree: its Act II head and bead, then its Act III
  pair on row 23, the invitation and the war twin, one column either side of the bead. The Deep
  Ones Walk follows any one of the six (one OR block), on row 25 under an empty row 24; The Final
  Ritual follows the Walk on row 27 under an empty row 26, and The Tide Turns South follows the
  ritual on row 28, with everything below it one row lower than before. The override lists Act II's
  three heads and The Tide Turns South, no longer Act III's six (The story acts > *Pull-in*); an
  AI's middle plan takes Act III before the Walk, and its Washington stages and
  `mltd_ai_terms_pending` read The Grand Ritual (MLT's AI). Earlier the same day the ritual itself
  took the OR over the six, on row 26, with the Walk still under The Grand Ritual.
- *The Tide-Speaker* (`MLT_TIDE_SPEAKER`), a cultural advisor hireable from the Kingdom, whose
  trait `mltd_claims_of_the_tide` cuts justification time by 30 %. MLT has three cultural slots and
  Old Castro was its only civilian advisor, so what she costs is political power - against Castro,
  the summons and the Calls - which makes hiring her a strategic choice rather than a free bonus.
  It stacks with The Northern Waters' -25 % from Act III's close.
- *The wars' rewards.* Every story war focus grants a 180-day idea with +10 % attack and +10 %
  defence against the countries it goes to war with, and the shared 60-day `mltd_the_first_wave`
  (+10 % division recovery rate, +5 % breakthrough), against a target that is not MLT's subject -
  in place of the target's stability and war-support losses (The story acts > *The wars*).
- *Lighter tooltips* (Project > *Native lines first, and few of them*). The invitations read as the
  offer, "If they accept:" and "If they refuse:" over native lines; the war focuses dropped their
  side branches keyed to their targets' own stories, and their thefts are one line each with no
  floor; four heads lost a conditional line.

## Layout

- `mod_folder/`: The mod as HOI4 sees it. **Only this directory ships**; everything else in the
  repo is docs, tooling and source art.
- `mod_folder/descriptor.mod`: Mod metadata. **No `picture=` key** - deliberate, see the gotcha
  below. `remote_file_id="3798403425"` was written by the launcher on the first publish. No
  `path=`, no `replace_path`.
- `mod_folder/interface/z_fallout_ui.gfx`: **OVERRIDE** of OWB's file: one line,
  `GFX_frontend_bg`'s `texturefile` repointed to `gfx/loadingscreens/mltd_main.dds`. tnkd does the
  same - but copy **OWB's current bytes**, not tnkd's, which are stale and lack
  `GFX_generic_text_bg_48_owb`.
- `mod_folder/interface/frontendmainview.gui`: **OVERRIDE** of OWB's file: the overlay `iconType`
  OWB ships commented out, re-enabled and pointed at `GFX_frontend_bg_mltd_rain`. The only reason
  the menu rain moves, and the only file here other submods contest (ECR, Enclave Reborn Redux,
  Rustbelt, Monarchs all ship it). Deleting it costs the rain and nothing else.
- `mod_folder/gfx/loadingscreens/mltd_main.dds`, `mod_folder/gfx/interface/logo_game_static.dds`,
  `mod_folder/gfx/interface/mltd_logo_animated.dds`,
  `mod_folder/gfx/interface/mltd_rain_{base,mask,anim1,anim2}.dds`: Main-menu background
  (1910x1440), header logo (443x303 static as a texture-path override of OWB's, plus the 16-frame
  7088x303 uncompressed strip the frontend actually uses) and the rain (four 2560x1792 DXT5
  textures). Built by `build_main_menu.py`; see Main menu below. ~32 MB, most of the mod's size.
- `mod_folder/thumbnail.gif`: Animated Workshop preview - rain plus a neon breath, 350x350, 32
  frames @ 40 ms, ~740 KB. Built by `build_workshop_thumbnail.py`. The **only** thumbnail that
  ships; the 512x512 still is built repo-side to `event_images/workshop/thumbnail.png`.
- `<HOI4>/mod/rising_tide.mod` (not in this repo): Launcher pointer: `descriptor.mod` plus one
  `path=` line. Machine-specific, so unversioned; regenerate it after any descriptor change.
- `mod_folder/common/national_focus/Mirelurk Tribe (MLT) Focus.txt`: **OVERRIDE** of OWB's file:
  +10 lines straight after OWB's two `shared_focus = lurk_*` lines (`:20-25` a comment, `:26-29`
  the story acts' four listed focuses - Act II's three heads and, since 2026-09-24, The Tide Turns
  South in place of Act III's six - see The story acts; from round 28c to 2026-09-23 nine listed
  lines, `:26-34`, and until round 27 ten `shared_focus = mltd_<root>` lines, one per conflict
  sub-tree); +7 lines in `mlt_kingdom_of_mlyeh` (a spacer between OWB's rewards and ours with its
  comment, two victory-point grants, a second spacer, the event and the news delivery) and, since
  round 17, an 18-line trade-node block before the victory points; since round 28b, after the
  `country_event` of the Kingdom, the Call and the Walk, a preview of the event's option (a
  comment, `custom_effect_tooltip = mltd_event_brings_tt` and an `effect_tooltip` block); -1 OWB
  line (`itz_civilizing`); +12 focuses appended (The Spreading Cult, The Wet Market, Gifts, five
  Books, Call, Grand Ritual, Walk, Final Ritual - see Project); since round 20, four replaced
  lines: the AI gate of the claim focuses (see MLT's AI); since 2026-09-25, three inserted lines
  and a four-line comment in OWB's Cannibal Territories trade
  (`mlt_offer_muttfruit_for_the_cannibal_territories`), so that owning the state lets the player
  bypass it but no longer bypasses it by itself (Overriding OWB). The Books' rewards only preview
  their Book and fire the expedition's first event. Since 2026-09-24 The Deep Ones Walk's
  prerequisite is one OR block over Act III's six focuses (The Grand Ritual until then), with a
  three-line comment above it, and it sits at (0,5) of The Grand Ritual (it was (0,1)), with a
  two-line comment; The Final Ritual's prerequisite is the Walk, with a two-line comment (from
  round 27, one OR block over Act II's three branch ends, and briefly on 2026-09-24 over Act III's
  six), and it sits at (0,2) of the Walk (round 28b: (0,4); round 27: (0,3)), with a four-line
  comment.
- `mod_folder/common/national_focus/mltd_act2_focus.txt` ... `mltd_act6_focus.txt`,
  `mltd_finale_focus.txt`: **New files, not overrides** (round 27). OWB ships nothing by these
  names, so OWB updates never touch them; they still need load-after-OWB, because OWB
  `replace_path`s the folder. Together they hold the story acts as 41 top-level `shared_focus`
  blocks: Act II 6 (the `mltd_wbh_*`, `mltd_brk_*` and `mltd_bdt_*` heads and beads), Act III 7
  (Terms for the Citadel since round 28, The Coast Goes Under since round 28c), Act IV 6
  (`mltd_ncr_*` and its close), Act V 10 (`mltd_ces_*`, `mltd_bos_*`, `mltd_wht_*`, `mltd_hea_*`,
  the chapter and the close), Act VI 8 (`mltd_tex_*`, `mltd_ate_*`, `mltd_tla_*`, the chapter and
  the close), and the finale 4. Each file opens with a header comment on its act: its layout, its
  merges, and what changed. The override lists the four story focuses whose prerequisite is a
  national focus (nine until 2026-09-23); everything else comes in through shared prerequisites.
  LF, no BOM. See The story acts. They replace `mltd_conflicts_focus.txt` (rounds 13-26, the ten
  conflict sub-trees), which round 27 deleted. `build_telemetry.py` names the six files, and since
  round 28 `mltd_spoils_focus.txt`, in `STORY_FILES`.
- `mod_folder/common/national_focus/mltd_spoils_focus.txt`: **New file, not an override** (round
  28; restructured in round 28c): the spoils, ten top-level `shared_focus` blocks (`mltd_spoils_*`)
  in four groups - two each for the north, the interior and the south, four for California. Round
  28 shipped twelve, in four chained branches of three at x = 20. Each names only its act's close
  in its prerequisite, so the engine pulls it in with that close and the override lists none of
  them; each takes the chapter after that close as its `relative_position_id`, on the chapter's own
  row. Nothing names a spoils focus in a prerequisite, so nothing waits on one. Its header comment
  gives each group's close, anchor, cells, icons, gates and payoffs. Needs load-after-OWB, as the
  act files do. LF, no BOM. See The story acts > *The spoils*.
- `mod_folder/common/continuous_focus/generic.txt`: **OVERRIDE** of OWB's continuous-focus palette
  (the only palette; `generic_focus`, `default = yes`): one inserted focus,
  `mltd_continuous_spawning_pools`.
- `mod_folder/common/characters/MLT.txt`: **OVERRIDE** of OWB's MLT characters: +2 traits on
  `MLT_MLULU`, +1 trait, two replaced portrait lines and attack/planning skill 1 -> 2 on
  `MLT_CORAL_PROPHET_ANASTASIA`, + role-less character `MLT_DROWNED_HERALD` (name + portraits only;
  `mltd.1` adds the general role). All 14 tokens OWB's history recruits must stay defined. Also
  `MLT_OLD_CASTRO`, the Esoteric Order's spymaster: a `cultural_advisor` with
  `mltd_keeper_of_the_order` (+2 operative slots), `visible` only with La Resistance and
  `available` once MLT has an agency. And, since 2026-09-24, `MLT_TIDE_SPEAKER`, the Tide-Speaker:
  a `cultural_advisor` with `mltd_claims_of_the_tide` (-30 % justification time), `available` once
  the Kingdom is done.
- `mod_folder/common/country_leader/mltd_traits.txt`: `mltd_keeper_of_the_order`
  (`operative_slot = 2`), Old Castro's advisor trait, and, since 2026-09-24,
  `mltd_claims_of_the_tide` (`justify_war_goal_time = -0.3`), the Tide-Speaker's. New file; OWB
  does not `replace_path` `common/country_leader`.
- `mod_folder/events/nf_mlt.txt`: **OVERRIDE** of OWB's MLT event file: `nf_mlt.7` (the Black
  Hollows Night hatching) pays 300 political power instead of forcing `war_economy`,
  `children_and_mothers` and `closed_economy`. The override that deletes the most OWB content (-36
  lines / +7); the focus override drops one line and replaces four more. Round 18 inserts three
  `ai_chance` lines that steer an AI to the plan's picks in `nf_mlt.1-3`.
- `mod_folder/history/countries/MLT - Mirelurk Tribe.txt`: **OVERRIDE** of OWB's MLT history: four
  inserted lines (plus comments), `recruit_character = MLT_DROWNED_HERALD`,
  `recruit_character = MLT_OLD_CASTRO`, `recruit_character = MLT_TIDE_SPEAKER` (2026-09-24;
  `recruit_character` is history-only - anywhere else the game logs an error at load) and, since
  round 24, `set_variable = { never_return_stolen_territory = 1 }` - see *The territory give-away*
  under How the mechanics are wired.
- `mod_folder/common/script_enums.txt`: **OVERRIDE** of OWB's script enums: our four equipment ids
  appended to `script_enum_equipment_bonus_type` (otherwise the game logs one "not in script enum"
  warning per id at load).
- `mod_folder/common/technologies/tech_naval.txt`: **OVERRIDE** of OWB's naval techs (round 26):
  one inserted `path` block in `brk_palace_ships_tech`, leading to `mltd_leviathan_tech`, so that
  tech renders beside the Personal Floating Palace (see The Leviathan). CRLF, no BOM, as OWB's.
- `mod_folder/history/units/mltd_leviathan_first.txt`, `mltd_leviathan.txt`: The Leviathan's two
  OOBs (round 26): one bare `mltd_leviathan_1` hull at Mireport (7064), the first flagged
  `pride_of_the_fleet`. OWB `replace_path`s `history/units`, so they need load-after-OWB.
- `mod_folder/common/technologies/mltd_technologies.txt`: Since round 26 also
  `mltd_leviathan_tech`, in the naval folder (see The Leviathan). Reward-tab techs
  `warbike_unlock_tech` (Deep Ones) -> `mltd_star_spawn_tech` (`enable_subunits` +
  `enable_equipments`), plus two hidden folder-less techs `mltd_deep_ones_equipment_tech` /
  `mltd_star_spawn_equipment_tech` that only `enable_equipments`, granted by script the first time
  a division is raised.
- `mod_folder/common/units/mltd_units.txt`: Sub-units `mltd_deep_ones` and `mltd_star_spawn` (a
  lower `need` - fewer, bigger monsters): both width 2.5, suppression 5, special forces,
  `active = no`, flat sub-unit stats only - combat stats come from their equipment. Both carry
  `sprite = mltd_star_spawn`, so both are drawn with the mod's own 3D model (The Star Spawn model);
  `build_unit_model.py` checks the two lines (`SUB_UNITS`).
- `mod_folder/common/units/equipment/mltd_equipment.txt`: Archetypes `mltd_deep_ones_equipment` /
  `mltd_star_spawn_equipment` and variants `_1` (x1.3 / **x2.2** of
  `amphibious_beast_equipment_king`), modelled on `cre_amphibious_eq.txt`.
- `mod_folder/common/decisions/mltd_decisions.txt`: 5 gift decisions + 5 gift missions in
  `mltd_gifts_from_the_deep_cat`, each `visible` once its Book's expedition has set
  `mltd_<n>_book_found`; 2 summon decisions + 2 offering decisions in
  `mltd_children_of_the_deep_cat`. Plus 2 untargeted decisions in `mltd_cult_infiltration_cat`,
  *Call for People* and *Call for Equipment* (see Cult Infiltration). Their `ai_will_do` blocks are
  MLT's decision AI (see MLT's AI).
- `mod_folder/common/decisions/categories/mltd_decision_categories.txt`:
  `mltd_gifts_from_the_deep_cat`, `mltd_children_of_the_deep_cat` (holds the summons *and* the
  offerings, so it opens at the Kingdom and never closes - each decision shows once it is
  unlocked). `mltd_cult_infiltration_cat` (opens with *The Spreading Cult*). All three pictures are
  ours: OWB's, moved down 2 rows (`build_category_pictures.py`, see Gotchas).
- `mod_folder/common/dynamic_modifiers/mltd_dynamic_modifiers.txt`: `mltd_gifts_from_the_deep`
  (five variable-backed modifiers). `mltd_cult_infiltration`, which sits on **foreign** countries
  that hold a cult and bites only at war with MLT. `mltd_summoned_host` (2026-09-23):
  `special_forces_min` from `mltd_summoned_sf_var`, 8 for each summoned division (Deep Ones / Star
  Spawn).
- `mod_folder/common/scripted_effects/mltd_scripted_effects.txt`: `mltd_gift_<key>_on/_off`,
  `mltd_all_gifts_permanent`, `mltd_ensure_*_template`, `mltd_raise_*_here` (state scope),
  `mltd_spawn_*_division`, `mltd_add_summoned_room` (each summoned division's own special-forces
  room, 2026-09-23), `mltd_update_national_population`, `mltd_take_population_everywhere`,
  `mltd_ritual_daily_toll`, and `mltd_intel_foothold` (the first effect of the story acts' eleven
  spying heads: with La Resistance and an agency it refunds OWB's caps charge and then adds one
  upgrade; without an agency, without the DLC or at OWB's 30-upgrade ceiling it pays +50 PP - since
  round 14 *The Spreading Cult* founds the agency). The cult effects `mltd_cult_add_strength`,
  `mltd_cult_refresh`, `mltd_cult_weekly` and `mltd_cult_dissolve` run in the target country's
  scope; `mltd_cult_rebuild_list` (MLT scope) rebuilds the category's sorted list of cults,
  `mltd_cult_list`, and sums `mltd_cult_total_strength` for the Call decisions.
  `mltd_indoctrinate_transfer` / `mltd_indoctrinate_defector`: the operation's manpower and its
  critical success. `mltd_wet_market_pay` / `mltd_wet_market_receive` pay for a Wet Market lot and
  pay out for one sold. `mltd_brk_join_the_covenant` (round 21), `mltd_bdt_join_the_covenant`
  (round 22) and `mltd_wbh_join_the_covenant` (round 28) are the invitations' acceptances, each run
  in MLT's scope from the invitee's event, with the invitee as ROOT: MLT founds or leads the
  Drowned Covenant, the invitee joins, +75 opinion both ways. When the Broken Coast or the
  Brotherhood actually joins, its effect also sets the flag that closes the other invitation
  (`mltd_brk_covenant_joined`, `mltd_wbh_alliance`), and the Brotherhood's drops every claim it
  holds on MLT's land and, since 2026-09-25, when the Brotherhood leads a faction, brings each of
  its other members at peace with MLT and its allies along through
  `mltd_wbh_bring_into_the_covenant` (The story acts > *The invitations*). Since round 28b each
  writes the join as a line (`mltd_<tag>_joins_covenant_tt`) under the test the join will pass once
  the faction exists, with `add_to_faction` and the flags in `hidden_effect`: previewed plainly, a
  faction founded in the same effect showed nobody joining it. `mltd_legion_pens_freed` /
  `mltd_legion_pens_fed` (round 28b) are `mltd.51`'s two options, which Act V's close previews by
  calling them in `effect_tooltip`, so their numbers live in one place.
- `mod_folder/common/scripted_triggers/mltd_scripted_triggers.txt`: `mltd_flavour_can_fire`
  (`original_tag = MLT`, Kingdom complete, `has_capitulated = no`, no `mltd_flavour_cooldown`): the
  shared gate every flavour event's `trigger` calls. `mltd_cult_neighbouring_major`: a neighbouring
  major (plain `is_major`), where *The Spreading Cult* plants the first cults.
  `mltd_hail_candidate`: a country where *Hail M'lyeh* can strike (MLT's network there, no civilian
  token yet). `mltd_defector_candidate` and `mltd_defector_story_character`: who may defect on the
  operation's critical success. `mltd_wet_market_can_buy` / `mltd_wet_market_can_sell`: The Wet
  Market's buy and sell conditions. `mltd_wbh_brotherhood` (round 22): the Brotherhood that holds
  Washington - WBH, or TCA once it wears `TCA_northwestern_brotherhood` - which every `mltd_wbh_*`
  focus (Acts II and III) reads. `mltd_wbh_terms_target` (round 28): the one Brotherhood Terms for
  the Citadel asks - WBH unless it is gone or someone's subject, else TCA as the Northwestern
  Brotherhood - at peace with MLT, no one's subject, and in no faction or (since 2026-09-25) its
  faction's leader. `mltd_wbh_terms_can_offer`, `mltd_brk_covenant_can_offer` and
  `mltd_bdt_covenant_can_offer` (2026-09-25): whether each invitation can be sent now, read by its
  focus's hidden reward and by its preview (The story acts > *The invitations*).
  `mltd_texas_beaten` (round 27): the gate of Act VI's close. It passes when TBH and LNS are each
  gone, capitulated, recorded as capitulated to MLT (`mltd_tbh_capitulated` /
  `mltd_lns_capitulated`, set by `on_capitulation`) or MLT's subject.
- `mod_folder/common/scripted_localisation/mltd_scripted_localisation.txt`: `GetMltdCultList` (with
  `GetMltdCultRow1`-`8` and `GetMltdCultMore`): the list of cults abroad in the Cult Infiltration
  category's description (see Cult Infiltration > *The list*); `GetMltdWmRequirement`: the
  requirement line of The Wet Market's rows; `GetMltdWmMarketOpen` / `GetMltdWmAvailability`: its
  tab's tooltip; `GetMltdBrkOdds`, `GetMltdBdtOdds` and `GetMltdWbhOdds` (round 28): the last line
  of each invitation's description, how likely its answer is under the game's historical-focus rule
  (The story acts > *The invitations*); `GetMltdMirelurksName`, `GetMltdKillclawsName`,
  `GetMltdBloodrageName`, `GetMltdMirelurkKingsName`: OWB's mirelurk equipment names, which live in
  OWB's `replace/` folder and so cannot be nested in a sentence; for the same reason, since round
  28b, `GetMltdBunkerName` (OWB's "Outpost", for The Tide-Wall's bunker line) and
  `GetMltdArmsFactoryName` / `GetMltdCivilianFactoryName` (for the spoils' works lines). New file;
  OWB `replace_path`s the folder, so it needs load-after-OWB.
- `mod_folder/common/scripted_guis/mltd_wet_market_gui.txt`,
  `mod_folder/interface/mltd_wet_market.gui`: The Wet Market's seller button and item panel: two
  child scripted GUIs of OWB's Organization Marketplace window `trade_ledger_window` (see The Wet
  Market). New files; no OWB override.
- `mod_folder/common/ideas/mltd_ideas.txt`: `continuous_mltd_spawning_pools` (in a `hidden_ideas`
  block, added and removed by the continuous focus), `mltd_the_grand_ritual`,
  `mltd_the_final_ritual` (temporary; debuffs + toll tooltip), `mltd_children_of_the_deep`
  (permanent; `special_forces_min = 80`). Plus nine timed ideas, all `original_tag = MLT`,
  `removal_cost = -1`, with reused OWB pictures. Seven are 180-day ideas from the story acts' war
  focuses (the old conflict capstones): `mltd_tex_black_water`, `mltd_wbh_tide_wall`,
  `mltd_ces_the_drowned_bull`, `mltd_bos_red_tide`, `mltd_tla_dreams_of_wire`,
  `mltd_hea_pilgrims_of_the_steam` (+5 % political power, +3 % stability),
  `mltd_wht_rites_on_the_jetty` (+5 % morale, +3 % recruitable population). Two come from flavour
  events: `mltd_flavour_strange_harvest` (90 days) and `mltd_flavour_unnamed_colour` (120 days).
  Plus the permanent `mltd_the_wet_market` (+20 % caps income and a consumer-goods penalty), from
  the focus of the same name. Round 27 adds seven permanent ideas, in the same shape and with
  reused OWB pictures. Four are act ideas: `mltd_the_northern_waters` (The Tide Turns South),
  `mltd_the_drowned_rangers` (option b of `mltd.40`), `mltd_mars_beneath_the_waves` (When the
  Legion Breaks) and `mltd_the_drowned_south` (The Last King Kneels). Three come one per ending -
  `mltd_the_dreamer_wakes`, `mltd_the_priestess_reigns` and `mltd_the_return_to_the_sea` - and are
  the tree's one place for large bonuses. Round 28 adds four more permanent ideas, in the same
  shape, one from the idea focus of each spoils group, with 2-3 modifiers each inside +-5-10 %:
  `mltd_the_drowned_sound`, `mltd_the_drowned_harvest`, `mltd_the_iron_tithe` and
  `mltd_the_salt_road`; round 28c adds California's second, `mltd_the_office_of_salt` (research
  speed, maximum factory efficiency). Round 28b adds four more in the same shape. Two are 365-day
  spoils ideas: `mltd_the_legions_steel` (an `equipment_bonus` of defence and armour on the three
  creature archetypes since round 28c) and `mltd_the_black_water_visions` (research speed). Two
  come from `mltd.51`: the permanent `mltd_the_unchained` (stability, compliance growth) and the
  730-day `mltd_the_pens_emptied` (a build-cost cut on the three creature archetypes). Round 28c
  swaps `mltd_the_return_to_the_sea`'s recruitable population for the same kind of cut (the stack:
  Project > *Rewards scale to when they are taken*). 2026-09-24: the seven war ideas carry
  `targeted_modifier` blocks (+10 % attack and defence against each target), the four war focuses
  that had none got one of the same kind - `mltd_brk_the_raiders_hunted`,
  `mltd_bdt_the_dance_drowned`, `mltd_ncr_the_turbines_silenced`, `mltd_ate_the_serpent_hunted` -
  and every war focus grants the 60-day `mltd_the_first_wave` (+10 % division recovery rate, +5 %
  breakthrough) as well (The story acts > *The wars*).
- `mod_folder/common/on_actions/mltd_on_actions.txt`: `on_daily_MLT`: recompute
  `mltd_national_population`, then run `mltd_ritual_daily_toll` while a ritual idea is held, and
  rebuild the list of cults once *The Spreading Cult* is done (`mltd_cult_rebuild_list`); it also
  watches the Broken Coast's landings on Haida Gwaii (round 25; since round 28c not while MLT
  itself fights the Broken Coast - see *The Broken Coast off Haida Gwaii*). `on_monthly_MLT`:
  restocks The Wet Market (+250 while below 2,500) and rolls the flavour pool,
  `random_events = { 50 = 0  10 = mltd.9 ... 10 = mltd.19 }`. `on_weekly_MLT`: every cult abroad
  decays (`mltd_cult_weekly`), then the category's list of cults is rebuilt
  (`mltd_cult_rebuild_list`). `on_war_relation_added`: a war between MLT and a cult's country
  switches its penalties on at once. `on_capitulation` (round 27): when the NCR, CES, TBH or LNS
  capitulates while at war with MLT (or with MLT as `FROM`, the winner), it sets
  `mltd_ncr_capitulated`, `mltd_ces_capitulated`, `mltd_tbh_capitulated` or `mltd_lns_capitulated`
  on MLT. That lets an act's close outlive the peace (see The story acts). Since round 18
  `on_weekly_MLT` also re-scores an AI MLT's cult-operation target and buys it Wet Market lots, and
  since round 20 runs its weekly survey, `mltd_ai_survey` (see MLT's AI).
- `mod_folder/common/operations/mltd_operations.txt`: The intelligence operation, as five variants
  by the target's manpower (reuses OWB phases; no new phases/tokens): the target's manpower for
  support equipment, by band, and a critical success that hands MLT one of the target's generals
  (see Operation). Since round 17 also the cult operations `mltd_op_found_a_cult` and
  `mltd_op_nurture_the_cult` (see Cult Infiltration). The cult operations' `ai_will_do` clears the
  engine's minimum AI score (see MLT's AI).
- `mod_folder/events/mltd_events.txt`: `add_namespace = mltd`. `mltd.1-8`: 1/3/5 are MLT country
  events and 2/4/6 world news events delivered via `every_other_country`, one option each; 7/8 are
  single-option events that carry the Call / Walk effects. `mltd.1`'s `immediate` also sets
  `mltd_flavour_cooldown` for 90 days. `mltd.9-18` are the Lovecraftian flavour events drawn by
  `on_monthly_MLT` (see Flavour events); `mltd.19` is *Hail M'lyeh*, from the same pool (see Hail
  M'lyeh); `mltd.20` names the general who defects on the operation's critical success (see
  Operation). `mltd.21` (to the Broken Coast) offers the Drowned Covenant and `mltd.22` / `mltd.23`
  bring MLT its acceptance or refusal (round 21, see The story acts); `mltd.24-26` do the same for
  the Bone Dancers (round 22). Since round 28 the refusing option of `mltd.21` and `mltd.24` also
  hands MLT a war goal on the refuser that expires, and `mltd.21`'s answer is weighted by the
  historical-focus rule. `mltd.27` (round 25, hidden) makes the Haida Confederation white-peace the
  Broken Coast the day BRK is thrown off Haida Gwaii - see *The Broken Coast off Haida Gwaii*.
  Round 27's story acts add five groups (see The story acts): `mltd.30-31`, Act III's close and its
  news; `mltd.40-41`, Act IV's close (a two-option trophy) and its news; `mltd.50-52`, Act V's
  chapter, its close (a two-option trophy) and its news; `mltd.60-62`, Act VI's chapter, its close
  and its news; and `mltd.70-74`, R'lyeh Rises, its news and one event per ending. Round 28 adds
  `mltd.32-34` in Act III's decade: Terms for the Citadel's offer to the Brotherhood in Washington,
  then its acceptance and its refusal reaching MLT. Since round 28b `mltd.51`'s options call
  `mltd_legion_pens_freed` / `mltd_legion_pens_fed`; since round 28c's review `mltd.24`'s
  acceptance option carries a `trigger`, as `mltd.21`'s and `mltd.32`'s do; and since round 28c
  `mltd.27` makes no peace while the Broken Coast is at war with MLT. `mltd.101-103`, `201-203`,
  `301-303`, `401-403` and `501-503` are the five Book expeditions (see Book expeditions).
- `mod_folder/interface/z_mltd_technologies_faction.gfx`: MLT's three melee technology icons,
  `GFX_MLT_melee_weaponry_tech_{1,2,3}_medium`. The first two are **OWB's sprite names re-pointed**
  at our smaller, lifted, re-shadowed copies of its Cultist Knife and Conch Knife; the third is
  ours, the Tridents. The file's name is load-bearing: a sprite declared twice takes the
  declaration read last, and `interface/*.gfx` are read in filename order, so it must sort after
  OWB's `z_fallout_technologies_faction.gfx` - in `mltd.gfx` the two re-pointed sprites would lose
  (see MLT's melee icons, and Gotchas).
- `mod_folder/interface/mltd.gfx`: 4 event pictures, 2 tech icons, 2 equipment icons
  (`GFX_<equipment_id>_medium`; renders of our own model since 2026-09-23, OWB's mirelurk king and
  bloodrage before), 2 unit-icon triplets, the book focus icon `GFX_goal_mltd_book` + `_shine`, the
  portraits `GFX_Portrait_mltd_anastasia` / `GFX_Portrait_mltd_drowned_herald`, and the
  `frameAnimatedSpriteType` `GFX_Portrait_mltd_mlulu_animated`. Also the three decision-category
  pictures `GFX_mltd_decision_cat_{spectral_cabal,loid_ekt_storm,wardens_propaganda}`, the
  cult-hood icon `GFX_decision_mltd_cult_hood` (*Call for People*) and the agency logo
  `GFX_intelligence_agency_logo_mltd_esoteric_order` (`noOfFrames = 2`).
- `mod_folder/gfx/interface/decisions/mltd_decision_cat_*.dds`, `build_category_pictures.py`: The
  three decision-category pictures: OWB's `decision_cat_spectral_cabal`,
  `decision_cat_loid_ekt_storm` and `decision_cat_wardens_propaganda` with their content moved down
  2 transparent rows (bottom 2 cropped, size kept) so they clear the category frame line, and OWB's
  DDS header copied onto the output. `--check` re-measures the shift from OWB's gui and frame
  texture after an update; `--out mod_folder` rebuilds.
- `mod_folder/gfx/interface/decisions/mltd_cult_hood.dds`, `build_decision_icons.py`: The cult-hood
  decision icon (`GFX_decision_mltd_cult_hood`; drawn for round 14's *Found a Cult*, used since
  round 17 by *Call for People*; it replaced OWB's Mexican wrestler mask `GFX_decision_ffi_mask`):
  a front-facing cult hood with faint teal eyes and a small coral-trident sigil, 33x32 uncompressed
  RGBA with a header matching vanilla `decision_infiltrate_state.dds`. Drawn procedurally,
  supersampled and seeded; previews (the 8x/1x sheet with OWB's and vanilla's icons and a mocked
  targeted-decision row) go to `event_images/decision_icons/`.
- `mod_folder/gfx/interface/operatives/agencies/mltd_agency_logo_esoteric_order.dds`,
  `build_agency_logo.py`: The Esoteric Order of M'lyeh's agency logo
  (`GFX_intelligence_agency_logo_mltd_esoteric_order`): a 234x119 strip of two 117x119 frames,
  uncompressed like OWB's, frame 2 carrying OWB's hover glow. A gold-on-abyssal-teal seal redrawn
  from `event_images/agency/agency_src.jpg`, a stencil of Marvel's HYDRA insignia (the *Hail
  M'lyeh* joke; a licence risk, see `event_images/SOURCES.md`): the skull and tentacles are
  resampled, both rings redrawn as true circles with a wider gap. `--preview` renders it in the
  game's four logo slots into `event_images/agency/`.
- `mod_folder/common/intelligence_agencies/000_mltd_intelligence_agencies.txt`: MLT's
  `intelligence_agency` entry (the seal, `names = { mltd_agency_name }`, `default` and `available`
  on `original_tag = MLT`), so an agency founded from the intelligence screen gets our name and
  logo too and the change-insignia list keeps offering them. New file; OWB `replace_path`s the
  folder, so it needs load-after-OWB. `000_` sorts before OWB's `00_intelligence_agencies.txt`,
  whose generics also match MLT: the tie-break is undocumented, and the first valid entry is the
  likely rule.
- `mod_folder/gfx/leaders/MLT/mltd_mlulu_animated.dds`, `mltd_drowned_herald_animated.dds`: The two
  animated portraits: M'lulu's rain (40 frames @ 12 fps, 6240x210, 5.2 MB) and the Herald's
  backdrop throb (24 frames @ 8 fps, 3744x210, 3.1 MB), both uncompressed A8R8G8B8 at 156 px per
  frame. Rebuilt by `build_animated_portrait.py` (`--subject` builds one).
- `mod_folder/gfx/interface/equipment/mltd/mltd_{deep_ones,star_spawn}_equipment.dds`,
  `build_equipment_icons.py`: The two monsters' equipment icons (2026-09-23;
  `GFX_mltd_{deep_ones,star_spawn}_equipment_1_medium`): renders of the mod's own 3D model,
  textured with its shipped diffuse, normal and specular maps and posed through
  `build_unit_model.py`'s rig, skin and clips - the Star Spawn in the rearing frame of `attack`,
  full height and teal; the Deep Ones mid-stride in `move`, smaller, darker and greener - each
  whole in a 130x60 uncompressed texture whose header is byte-identical to OWB's
  `mirelurk_king_equipment.dds`, with a glow measured off OWB's 27 creature icons. The script reads
  the model's bake cache (run `build_unit_model.py` first if the temp folder was cleaned) and
  refuses one that no longer matches the shipped `.mesh`; `--no-write` builds only the previews
  (`event_images/equipment_icons/`), `--set` tries a pose or grade, `--rerender` forces a render.
  Tunables at its top. Derived from the sculpt, so they share its unrecorded licence
  (`event_images/SOURCES.md`).
- `mod_folder/gfx/interface/counters/division_templates_{large,small}/custom_template_25{6,7}.dds`:
  Division-template counters for the Deep Ones (256) and Star Spawn (257) templates: 76x42 and
  30x12, sliced from frame 1 of the battalion sheets by `build_unit_icons.py`.
- `mod_folder/gfx/interface/goals/mltd_book.dds`: Book focus icon (92x90, uncompressed): OWB's
  `cho_scriptorium.dds` recoloured to a dark violet tome by `build_focus_icons.py` (needs OWB
  installed to rebuild).
- `mod_folder/gfx/interface/equipment/cosmetic/melee/mltd_melee_weaponry_tech_icon_{1_cultist_knife,2_conch_knife,3_trident}.dds`,
  `build_tech_icons.py`: MLT's three melee tech icons (130x60, uncompressed, header byte-identical
  to OWB's Conch Knife icon), all with the object's vertical centre on texture row 24 (`CENTRE_Y`).
  The two knives are OWB's own icons, read from the OWB folder at build time: the object is cut out
  of its baked-in glow by alpha, scaled (`scale`) and lifted. The trident is
  `event_images/tech_icons/trident_src.webp` laid flat with its head to the right (the axis is
  trued on the haft, not only by PCA), scaled to the longest that leaves nothing cut by the
  texture's edge (`fit_w`) and lifted in tone. All three then get the same generated copy of OWB's
  black outer glow, measured off OWB's 73 melee icons. `--no-write` builds only the preview sheet
  (`mlt_melee_preview.png`: OWB's and ours per tier on the tech box's background, then the row of
  three) into `event_images/tech_icons/`. Needs OWB and vanilla installed. See MLT's melee icons.
- `mod_folder/gfx/leaders/MLT/mltd_anastasia.dds`, `mltd_drowned_herald.dds`: Coral Prophet
  Anastasia's and the Drowned Herald's portraits (156x210 uncompressed, same header class as OWB's
  leader portraits), cropped from `event_images/portrait/{anastasia,herald}_src.jpg` by
  `build_leader_portraits.py` (per-subject `CROP` table; `--subject` builds one).
- `mod_folder/gfx/event_pictures/mltd_event_*.dds`: 500x200 uncompressed A8R8G8B8. Rebuilt by
  `build_event_pictures.py` from `event_images/`.
- `mod_folder/gfx/leaders/MLT/mlulu.dds`,
  `mod_folder/gfx/interface/ideas/character_small_icons/MLT_mlulu.dds`: Graded portrait (156x210
  uncompressed) and small icon (65x67 DXT1) overriding OWB's textures by path - no `.gfx` change.
  Rebuilt by `build_portrait.py`. Since round 9 the portrait is no longer drawn in game (our
  characters override points M'lulu at the animated sprite, and nothing else in OWB references
  `GFX_Portrait_MLT_mlulu`): it is now the **build input** `build_animated_portrait.py` reads, so
  it must not be deleted. The small icon, by contrast, only started rendering in round 9, through
  the `small =` keys added to M'lulu.
- `mod_folder/gfx/interface/counters/divisions_large/unit_mltd_*_icon.dds`,
  `.../divisions_small/onmap_unit_mltd_*_icon.dds`,
  `mod_folder/gfx/texticons/unit_mltd_*_icon_small.dds`: Original unit/division icons for
  `mltd_deep_ones` (fish-man) and `mltd_star_spawn` (Cthulhu bust): 152x42 / 60x12 / 60x12, two
  frames each (frame 1 shaded glyph - green, or white for the on-map sheet; frame 2 NATO counter
  box with a line symbol), uncompressed A8R8G8B8 like OWB's. Drawn procedurally by
  `build_unit_icons.py` (all shape parameters at its top); referenced by the
  `GFX_unit_mltd_*_icon_*` triplets in `mltd.gfx`.
- `mod_folder/gfx/models/mltd/star_spawn/`: `mltd_star_spawn.mesh`, `mltd_star_spawn_{d,n,s}.dds`,
  `mltd_star_spawn_{idle,idle2,move,attack,attack2,defend}.anim`, `mltd_star_spawn_mesh.gfx`,
  `mltd_star_spawn_animations.asset`: The Star Spawn's 3D unit model, in the shape of OWB's
  `gfx/models/owbentity/mirelurk/`: a 6,000-triangle mesh with a 32-bone skeleton and a
  four-influence skin; its diffuse (1024), normal and specular (512) textures, DXT5 with full mip
  chains - the header flags and caps of OWB's `mirelurk_d.dds`; six animation clips; the `pdxmesh`
  declaration `mltd_star_spawn_mesh` (shader `PdxMeshAdvanced`, one `animation = { id type }` line
  per clip); and the clips' declarations, which as in vanilla sit **beside the `.anim` files**:
  `file` is relative to the declaring `.asset`'s folder. ~2.7 MB. All of it is **generated** by
  `build_unit_model.py`. See The Star Spawn model.
- `mod_folder/gfx/entities/mltd_entities.asset`: The entity `mltd_star_spawn_entity`, generated
  too: what `sprite = mltd_star_spawn` in `mltd_units.txt` resolves to. Its `scale`, and its states
  \- the script's `STATES` table, OWB's `mirelurk_entity`'s set with an animation each; no `death`.
  New file; OWB `replace_path`s neither `gfx/entities` nor `gfx/models`.
- `build_unit_model.py`, `unit_model_clips/`, `event_images/unit_model/`: The model's build:
  Blender headless (import, decimate, unwrap, Cycles bakes; then an armature from the script's
  `RIG` table and bone-heat skin weights), then numpy and Pillow (the textures, the skinned
  `.mesh`, an `.anim` per clip, the `.gfx` and the two `.asset`s), written to a staging folder and
  copied into `mod_folder` only when every check passes. `unit_model_clips/<animation id>.py` are
  the clips: small modules that pose the rig as a function of time and import nothing but `math`.
  `--clip NAME` measures and draws one clip in seconds; `--preview` renders `preview.png`, a
  contact sheet per clip (`anim_<id>.png`) and, with ffmpeg on the PATH, `animations.mp4`;
  `--check` re-checks the shipped files without Blender. Needs Blender - built and only ever run
  with 5.2.2 LTS - numpy and Pillow. The sculpt it reads is **not in the repo** (100 MB): `--src`,
  by default `~/Downloads/cthuluMINI.V1.1.stl`, whose hash `event_images/SOURCES.md` records.
  Repo-only.
- `mod_folder/common/ai_strategy_plans/mltd_MLT.txt`, `mod_folder/common/ai_strategy/mltd_MLT.txt`,
  `mod_folder/common/ai_strategy/mltd_MLT_frontier.txt`,
  `mod_folder/common/ai_templates/mltd_MLT.txt`: MLT's AI: the three phase plans (focus order,
  research and advisor weights); every `ai_strategy` block (unit mix, research, political power,
  the army's size, every front, Old Castro and, since 2026-09-24, the Tide-Speaker, the Book
  networks, the conquest stages, the war-goal holds - since round 28 those on a refused
  invitation's war goal too - the holds on the NCR's side, DIS, The Warren, the cult operations);
  the frontier (conquests no stage schedules, and military-access requests); and the five division
  roles. New files; OWB `replace_path`s all three folders, so they need load-after-OWB. See MLT's
  AI.
- `mod_folder/common/scorers/country/mltd_ai_cult_target_scorer.txt`,
  `mod_folder/common/peace_conference/ai_peace/mltd_MLT_peace.txt`: The AI's cult-operation target,
  scored weekly from `on_weekly_MLT`, and its peace desires (states, never puppets). New files; OWB
  `replace_path`s both folders.
- `mod_folder/common/scripted_triggers/mltd_ai_triggers.txt`: The conquest stages,
  `mltd_ai_stage_<tag>`: one per country MLT's AI conquers on the plan's schedule, read by its
  conquest block in `common/ai_strategy/mltd_MLT.txt` - edit the stages here. Section H holds the
  tests they share: the north's 79 states (`mltd_ai_north_state`), the NCR's side, a safe target, a
  cut-off enemy, the frontier, the NCR's readiness and the late army. Section W (round-27 review)
  holds `mltd_ai_may_*`, one per story war focus (`mltd_ai_may_drown_the_coast` since round 28c)
  and, since round 28, `mltd_ai_may_offer_the_citadel` for Terms for the Citadel, which declares no
  war but whose refusal hands MLT a war goal: the AI's hold on that focus, called from the focus's
  own `available` (The story acts > *The AI*). Beside it, `mltd_ai_terms_pending` (round 28) marks
  an offer the AI still means to make, which holds its war on WBH (MLT's AI > *The invitations' war
  goals*). Two of its triggers are not AI-only: `mltd_ai_ncr_beaten` and `mltd_ai_legion_beaten`
  are also the gates of Act IV's and Act V's closes, for a human too (round 27, The story acts), so
  edit them with both uses in mind.
- `mod_folder/common/scripted_effects/mltd_ai_survey_effects.txt`: `mltd_ai_survey`: an AI MLT's
  weekly reading of the map (border states, the army's target, the north, pockets) into variables
  and flags its strategy reads. `mltd_ai_buy_line_equipment` (round 21): its purchases of infantry
  weapons from OWB's sellers. Both called from `on_weekly_MLT`.
- `mod_folder/common/scripted_effects/mltd_ai_frontage_effects.txt`, `build_ai_frontage.py`:
  Generated (round 21): `mltd_ai_set_state_edges` writes each state's frontage (`mltd_ai_edge`, the
  divisions that fill its provinces touching another state) and its count of neighbouring states
  (`mltd_ai_nbs`), measured once from OWB's `map/provinces.bmp`, `definition.csv`, state history
  and terrain combat widths by `build_ai_frontage.py` (repo-only; `--dry` prints, rerun after an
  OWB map change).
- `mod_folder/common/opinion_modifiers/mltd_opinion_modifiers.txt`,
  `mod_folder/common/factions/templates/mltd_factions.txt`: Round 21, the Broken Coast: the opinion
  modifiers `mltd_drowned_envoys`, `mltd_drowned_covenant` and `mltd_drowned_covenant_refused`, and
  the faction template `mltd_drowned_covenant_template`. New files; OWB `replace_path`s
  `common/factions/templates` (not `common/opinion_modifiers`), so the template needs
  load-after-OWB.
- `mod_folder/common/scripted_effects/mltd_telemetry_effects.txt`,
  `mod_folder/common/on_actions/mltd_telemetry_on_actions.txt`,
  `mod_folder/common/scripted_triggers/mltd_telemetry_triggers.txt`: The AI telemetry: `MLTD` lines
  in `game.log` while MLT exists (see MLT's AI > *Telemetry*). The effects file is generated by
  `build_telemetry.py` - edit its template, not the output. The kill switch `mltd_telemetry_on` is
  `always = yes`; set it to `always = no` before a Workshop upload. Deleting the three files
  removes the telemetry.
- `build_telemetry.py`, `ai_run_report.py`, `ai_runs/`: The telemetry's generator (`--dry` prints
  its lists) and the run report (`--selftest`, `--list`, `--run N`, `--plan-only`, `--csv FILE`,
  `--out FILE`, `--save`); `ai_runs/` holds saved reports, their raw lines and `runs.csv`.
  Repo-only.
- `mod_folder/localisation/english/MLT/mltd_l_english.yml`: All English strings (single file; UTF-8
  BOM, LF, 2-space indent).
- `mod_folder/localisation/replace/mltd_replace_l_english.yml`: Key-for-key overrides of OWB
  strings - currently only `warbike_unlock_tech(_desc)`. The collision `text.log` reports is
  intentional.
- `workshop_page/`, `build_workshop_page.py`: Screenshots for the Steam Workshop item's
  **Additional Previews** gallery - a different thing from `mod_folder/thumbnail.gif`, which is the
  single preview image. 1920x1080 JPEG under 900 KB (Steam caps an image at 1 MiB; a 1920x1080 PNG
  of these scenes is ~2.9 MB, so PNG is not usable at that size). Repo-only.
- `CONQUEST_PLAN.txt`, `check_plan_sync.py`: The simplified ideal strategy: a paper plan for a
  human MLT's conquest of the map, written as one operation per line with `#` comments. It covers
  every focus, decision, justification, war, production and research step from 2275 to the 2290s,
  with `# snapshot` lines giving the expected strength at each milestone (the cache). Its opening
  is an early rush by manual justification (CCW, then TRL, then RBT, all in 2275, before TRL can
  grow), and it closes with balance notes, a summary of MLT's AI and its `# AI deviation:` lines.
  Modelled figures are marked [M]; rebuild the snapshots after balance changes.
  `check_plan_sync.py` checks the plan against the code and the AI (see Project). Both repo-only.
- `.mdformat.toml`, `.markdownlint-cli2.jsonc`: The configs of mdformat, which formats every `.md`
  in the repo, and of markdownlint-cli2, which lints them - no line over 100 characters, table rows
  included (Markdown). Repo-only.
- `event_images/workshop/`: `owb_wordmark.png` (the shared OWB marquee wordmark, matted out of *OWB
  \- Fountain of Dreams*' thumbnail - the only submod thumbnail with light lettering on a dark
  panel, so the only one that mattes cleanly) and the 128/77 px thumbnail previews.
- `event_images/`, `build_event_pictures.py`, `build_portrait.py`, `build_animated_portrait.py`,
  `build_unit_icons.py`, `build_focus_icons.py`, `build_tech_icons.py`,
  `build_leader_portraits.py`, `build_workshop_thumbnail.py`: Source rasters (event pictures;
  `portrait/` holds the decoded OWB originals, the icon photo mask, the Anastasia and Herald
  sources and previews; `tech_icons/` holds the trident source and its previews; `unit_icons/` and
  `focus_icons/` hold previews/compare sheets) and the rebuild scripts. Repo root, never shipped.
  `event_images/SOURCES.md` records the origin/licence status of every image - it must be complete
  before any Workshop upload.

Directories are created on demand - git does not track empty ones, so the scaffold lives in this
list, not on disk.

## Overriding OWB

No `replace_path` is declared, so this submod merges additively.

- **Override** an OWB file by shipping the *same relative path and filename*. That replaces OWB's
  whole file (for textures: just the image, the `.gfx` sprite keeps pointing at the path).
- **Add** content with a new `mltd_`-prefixed filename in the same directory.
- The submod must load **after** Old World Blues. `dependencies={ "Old World Blues" }` in both
  `.mod` files is the supported mechanism (OWB's own `doc/OWB_MODDING_README.txt`: "After adding
  this your mod will load after OWB and won't be replaced by files we have or our replace_paths");
  never remove it. In a hand-ordered playset, place this submod **below** Old World Blues - lower
  loads later. This is not cosmetic: OWB `replace_path`s `common/ideas`, `common/national_focus`,
  `common/characters`, `common/decisions`, `events` and `history/countries`, so anything we ship
  there is deleted outright if we load first.
- Never add `replace_path` - OWB declares 95 of them and ours would delete OWB's matching folder
  outright.

**Files we override, and the rule for editing them:** copy OWB's bytes (keep whatever BOM /
line-ending state OWB's copy has - all seven are CRLF; `history/countries/MLT - Mirelurk Tribe.txt`
and `events/nf_mlt.txt` carry a BOM, the rest do not), make the edit, then diff. Four are
insertion-only (the continuous-focus palette, the MLT history file, the script enums and
`tech_naval.txt`); the characters file also has Anastasia's four replaced lines and M'lulu's two,
the focus file **deletes one** OWB line (`add_timed_idea = { idea = itz_civilizing days = 365 }`),
and `events/nf_mlt.txt` **deletes 36** (the law block). Re-diff all seven after **every** OWB
update (Update process below).

- `common/national_focus/Mirelurk Tribe (MLT) Focus.txt` - the only way to add focuses to an
  existing tree (`mlt_nf`). Our changes: the trade-node block (round 17, before the victory
  points), a spacer tooltip between OWB's own rewards and ours, two `add_victory_points` lines, a
  second spacer and the `country_event`/`news_event` lines at the end of `mlt_kingdom_of_mlyeh`'s
  `completion_reward`, and twelve focus blocks (`mltd_the_spreading_cult`, `mltd_the_wet_market`,
  `mltd_gifts_from_the_deep`, the five Books, `mltd_call_of_the_deep_ones` ...
  `mltd_the_final_ritual`) before the final brace. Round 20 replaces OWB's
  `ai_has_no_other_wars_or_wargoals = yes` in the `available` of `mlt_expanding_mlulus_domain`,
  `mlt_cascadian_current`, `mlt_sea_of_cortez` and `mlt_tropic_of_cancer` with
  `mltd_ai_may_press_claims = yes` (a trailing `# Rising Tide:` comment on each line). Rounds 27 to
  28c, 2026-09-24 and 2026-09-25 made eight more changes:
  - round 27 replaced the ten `shared_focus = mltd_<root>` lines that listed the conflict
    sub-trees' roots (rounds 13-26) with a three-line comment and seven lines - the story acts'
    listed roots, the focuses whose prerequisite is a national focus;
  - round 27 gave `mltd_the_final_ritual` one OR prerequisite over Act II's three branch ends in
    place of the Walk, with a two-line comment, and moved it from `y = 2` to `y = 3` under the
    Walk;
  - round 28 appended an eighth listed line, `shared_focus = mltd_wbh_terms_for_the_citadel`, and
    grew the comment above the list to five lines;
  - round 28b moved `mltd_the_final_ritual` to `y = 4` of the Walk, with a three-line comment (its
    tall icon: Gotchas);
  - round 28b added, after the `country_event` of the Kingdom, the Call and the Walk, a preview of
    the event's option: a comment, `custom_effect_tooltip = mltd_event_brings_tt` and an
    `effect_tooltip` block;
  - round 28c appended a ninth listed line, `shared_focus = mltd_brk_the_coast_goes_under`, and
    grew the comment to six lines (`:20-25`; the list is `:26-34`);
  - 2026-09-24 replaced Act III's six listed lines with one for The Tide Turns South, so the list
    is `:26-29` under the rewritten six-line comment `:20-25`; gave `mltd_the_deep_ones_walk` one
    OR prerequisite over Act III's six in place of The Grand Ritual, with a three-line comment, and
    moved it to `y = 5` of The Grand Ritual, with a two-line comment; and gave
    `mltd_the_final_ritual` the Walk as its prerequisite in place of Act II's three beads, with a
    two-line comment, and moved it to `y = 2` of the Walk, with a four-line comment;
  - 2026-09-25 inserted three lines and a four-line comment in OWB's
    `mlt_offer_muttfruit_for_the_cannibal_territories`: `NOT = { owns_state = 186 }` in its
    `available`, `enable_automatic_bypass = no`, and
    `NOT = { has_completed_focus = mlt_dig_barrows_for_spawning_pools }` in its `bypass`, each with
    a `# Rising Tide` comment. OWB's `bypass = { owns_state = 186 }` completed the trade by itself
    the day MLT held Cannibal Territories, and the Barrows, whose `available` asks that the trade
    is not done (or its offer refused), shut for good; now holding the state lets the player bypass
    the trade or dig the Barrows, and once the Barrows are dug the trade cannot be bypassed at all
    (Gotchas > *A bypass fires by itself*).
- `common/characters/MLT.txt` - our changes: `MLT_MLULU` `field_marshal` traits +=
  `animal_friend_trait`, `naval_invader` (both `type = corps_commander` traits; OWB's own M'lulu
  already carries `swamp_fox` there and OWB's `RCK_roach_king` field marshal carries
  `animal_friend_trait`); `MLT_CORAL_PROPHET_ANASTASIA` `corps_commander` traits +=
  `animal_friend_trait`, her `army.large` / `civilian.large` portraits
  `GFX_Portrait_Tribal_Generic_3` -> `GFX_Portrait_mltd_anastasia`, and her `attack_skill` /
  `planning_skill` raised 1 -> 2 (four replaced lines in total); M'lulu's two
  `large = GFX_Portrait_MLT_mlulu` lines swapped for the animated sprite with
  `small = GFX_idea_MLT_mlulu` added under each (six lines where there were four); plus a new
  **role-less** character block `MLT_DROWNED_HERALD` (name + portraits only) appended at the end,
  after it `MLT_OLD_CASTRO`, and after him, since 2026-09-24, `MLT_TIDE_SPEAKER`, both
  `cultural_advisor`s (OWB has no `political_advisor` slot: its civilian advisors use
  `cultural_advisor` / `economic_advisor`, and 10 of its 18 operative-slot advisors are cultural).
  OWB's pattern for late-appearing generals: define the character without a role, recruit him in
  history (invisible until he has a role), then
  `add_corps_commander_role = { character = ... traits = {...} skill = ... }` at runtime - 29 OWB
  event files do exactly this. `recruit_character` outside a history file logs
  `effectimplementation.cpp: recruit_character should only happen in game/history files` at load.
  OWB `replace_path`s `common/characters`, so load-after-OWB is mandatory for this file to exist at
  all.
- `history/countries/MLT - Mirelurk Tribe.txt` - three inserted lines after OWB's last
  `recruit_character`: `recruit_character = MLT_DROWNED_HERALD`,
  `recruit_character = MLT_OLD_CASTRO` and, since 2026-09-24,
  `recruit_character = MLT_TIDE_SPEAKER`, and, since round 24,
  `set_variable = { never_return_stolen_territory = 1 }` (The territory give-away). (OWB
  `replace_path`s `history/countries`, so this override only exists when loaded after OWB.)
- `common/continuous_focus/generic.txt` - OWB's only continuous-focus palette, and there is no way
  to add to a palette from a separate file: a second palette would have to out-score OWB's for MLT
  and would then *replace* it, costing MLT all 20 of OWB's continuous focuses. So we override the
  file and insert one focus after `OWB_continuous_mutant`. Same risk profile as the doctrine
  override - any other submod that ships this file wins or loses it whole.
- `events/nf_mlt.txt` - the laws MLT used to be forced into are not in the Kingdom focus and not in
  our `mltd.1`: they are in OWB's `nf_mlt.7`, the Black Hollows Night hatching, fired two focus
  steps upstream by `ritual_of_black_hollows_night`. Its option added `war_economy`,
  `children_and_mothers` and `closed_economy` at -5 % stability each (or +15 % stability if all
  three were already held). Our copy keeps the egg payload and pays `add_political_power = 300`
  instead; no stability is applied either way. Nothing in OWB tests for those three ideas outside
  that option, and nothing tests `has_idea = itz_civilizing` at all. Round 18 adds three
  `ai_chance` lines, one on each option the plan picks in `nf_mlt.1`, `.2` and `.3`, so an AI MLT
  picks them too.
- `common/technologies/tech_naval.txt` (round 26) - OWB's copy plus one
  `path = { leads_to_tech = mltd_leviathan_tech research_cost_coeff = 1 }` block (and a comment) at
  the top of `brk_palace_ships_tech`. A tech renders only in the gridbox of its tree's root,
  `fallout_naval_folder` has three (`nautics_tech_1`, `brk_black_flag_ships_tech`,
  `brk_palace_ships_tech`) and no orphan to borrow, and the gui is off limits, so this is the only
  way to put the Leviathan beside the Palace. *OWB: Ultimate Tech Compatibility Mod* and the
  NCR-vs-Legion submod ship this file too (Compatibility).
- `common/script_enums.txt` - OWB's copy plus our six equipment ids inside
  `script_enum_equipment_bonus_type`. The enum is documentation-only, but every unlisted equipment
  id logs an `equipment_database.cpp` warning at load. tnkd ships a stale copy of this file - if
  both submods are loaded, whichever loads later wins and the other's ids warn again.
- `gfx/leaders/MLT/mlulu.dds`, `gfx/interface/ideas/character_small_icons/MLT_mlulu.dds` -
  texture-only overrides; header class must match OWB's (uncompressed 32-bit / DXT1 with OWB's
  alpha). If OWB changes the portrait or the icon template, re-run
  `build_portrait.py --derive-icon-mask` and re-fit `ICON_FIT`.

OWB's other MLT **script and localisation** files (exact override targets; reproduce spaces,
parentheses and the spaced hyphen, as in `MLT - Mirelurk Tribe.txt`, byte-for-byte):

- `common/countries/MLT - Mirelurk Tribe.txt`
- `common/characters/MLT.txt` (**already overridden** - see above)
- `common/decisions/_mlt_decisions.txt`, `common/decisions/categories/_MLT_categories.txt`
- `common/units/names/00_MLT_names.txt`, `common/units/names_ships/MLT_ship_names.txt`
- `events/nf_mlt.txt` (declares `add_namespace = nf_mlt`; ids 1-7 are taken - we use our own `mltd`
  namespace instead)
- `history/countries/MLT - Mirelurk Tribe.txt`, `history/units/MLT_2275.txt`,
  `history/units/MLT_2275_naval.txt`
- `localisation/english/MLT/{characters,events,focus,traits}_MLT_l_english.yml`
- Art: `gfx/leaders/MLT/{mlulu,tinyshell}.dds`,
  `gfx/interface/ideas/character_small_icons/MLT_{mlulu,tinyshell}.dds`,
  `gfx/interface/goals/mlt_*.dds` (5), `gfx/interface/ideologies/unique/MLT/MLT_elites.dds`,
  `gfx/interface/focusview/filter/mlt_eggs.dds`. Their sprites are declared in *shared* OWB
  `interface/*.gfx` files - declare new sprites in `interface/mltd.gfx`, never by overriding those.

Things OWB already provides that this submod must NOT recreate: the `MLT` tag
(`common/country_tags/00_countries.txt`), its flags
(`gfx/flags/{,medium/,small/}{MLT,MLT_TRL,MLT_cosmetic_tag}.tga` - 9 files; all three sizes must be
replaced together), and its map colour (`common/countries/colors.txt`, which overrides the colour
in the country file).

Files to leave alone even though they contain MLT content, because they are shared with other
countries:

- `common/national_focus/Shared Oregon Coastals Focus.txt` (also used by DIS)
- `common/ideas/generic_oregon_coastal_ideas.txt.txt` (note the real doubled extension; holds DIS
  `lake_*` and shared `lurk_*` ideas)
- `common/country_leader/00_traits.txt`, `common/countries/colors.txt`,
  `common/countries/cosmetic.txt`, `common/bookmarks/old_world_blues.txt`
- `common/units/unit_modifiers/unit_modifiers.txt`,
  `common/synchronized_dynamic_tokens/tokens.txt`, `interface/countrytechtreeview.gui` - whole-file
  lists that other submods also override.

## How the mechanics are wired

**Gifts from the Deep** (tnkd's dynamic-modifier-backed-variable pattern). One dynamic modifier
reads five gift variables (`mltd_gift_{tide,shell,current,brood,abyss}_var`; +20 % army attack /
defence / organisation, +30 % recruitable population, +20 % stability) plus
`weekly_manpower = mltd_gift_manpower_var`, which is not a gift: focus 1 initialises it to 0, the
Grand Ritual sets it to 20, the Final Ritual doubles it to 40 (`multiply_variable`), each followed
by `force_update_dynamic_modifier`; `mltd_all_gifts_permanent` never touches it. The 20 / x2 (+20,
then +40; +50 / +100 until round 16) are repeated as literals in `mltd_gift_manpower_grand_tt`,
`mltd_gift_manpower_final_tt` and `mltd_gifts_from_the_deep_desc` - change all four together. Each
gift is a *decision* that calls `mltd_gift_<key>_on` (sets the var, `mltd_gifts_active += 1`,
`force_update_dynamic_modifier`) and activates a 30-day *mission* whose `timeout_effect` calls
`mltd_gift_<key>_off`. The slot gate is `mltd_gifts_active < mltd_gifts_max` (1 after focus 1, 2
after the Grand Ritual), and each gift decision is hidden until its Book is read
(`has_country_flag = mltd_<n>_book_found`, set by the last event of that Book's expedition), so the
category opens empty after focus 1. `mltd_all_gifts_permanent` (Final Ritual) uses `remove_mission`
(which does **not** fire `timeout_effect`), pins every var, zeroes the counter and sets flag
`mltd_gifts_permanent`, which hides the category and every gift decision. *The numbers live in
three script places and two loc places:* the `set_temp_variable` preview and the `set_variable` in
each `mltd_gift_<key>_on`, the pins in `mltd_all_gifts_permanent`, the
`set_temp_variable ... tooltip =` line on each Book focus, and the literal list in
`mltd_all_gifts_permanent_tt`. The ten `_on_tt` / `_off_tt` keys read the variables and need no
edit. *Adding a gift touches seven places:* the dynamic-modifier line, the decision + mission pair,
the `_on`/`_off` effects, the `if has_active_mission -> remove_mission` line and the `set_variable`
in `mltd_all_gifts_permanent`, six loc keys (`<id>`, `<id>_desc`, `<id>_mission`,
`<id>_mission_desc`, `mltd_gift_<key>_on_tt`, `_off_tt`), and the value list in
`mltd_all_gifts_permanent_tt`.

**Deep Ones / Star Spawn** (OWB's Paladin pattern, with their own equipment). Sub-units are
`active = no` and carry only flat sub-unit stats (org, HP, morale, terrain); soft/hard attack,
defence, breakthrough, armour, hardness and speed are the **equipment's** flat numbers, exactly
like `amphibious_beast_creature`, so the units can be compared stat-for-stat with OWB's mirelurk
variants. Templates are 20 width: `"Deep Ones"` = 8 x `mltd_deep_ones`, `"Star Spawn"` = 8 x
`mltd_star_spawn` (deliberately few and huge - a low `need` and costly pieces; a battalion's combat
stats come from the equipment and are independent of `need`, which only scales production cost,
attrition piece loss and reinforcement volume) (2.5 each, grid rows 0-2 only - OWB's designer is 5
x 3). Each template carries `template_counter` (256 Deep Ones, 257 Star Spawn), which the engine
resolves to the sprites `GFX_div_templ_<N>_large` / `_small` declared in `interface/mltd.gfx` -
there is no division-template key that names a sprite, so declaring those names *is* the mechanism.
Vanilla owns 0-43, the anniversary DLC 44-64 and OWB 65-255, so 256/257 are the first free indices;
before this they were both `0`, which drew vanilla's dagger glyph. `mltd_ensure_*_template` first
grants the hidden equipment tech (`set_technology = { popup = no ... }` guarded by `NOT has_tech`)
\- **`create_unit` only equips a division with equipment the country has unlocked**, which is why
the first play-test spawned empty divisions - then creates the locked template once
(`NOT has_template_containing_unit`, `is_locked = yes`, no `force_allow_recruiting`);
`mltd_raise_*_here` (state scope) stockpiles 32 / 16 of the equipment variant - the +20 % spare,
since `start_equipment_factor = 1.0` fills the division itself (round 17; until then it was a whole
second division's worth, 160 / 80, repeated in `mltd_spawn_*_tt`) - and `create_unit`s the division
in that state with `owner = ROOT`; `mltd_spawn_*_division` = ensure + raise at the capital (used by
events `mltd.7` / `mltd.8`; the Call and Walk focuses themselves only fire those events, so their
effects land when the single option is clicked - the AI clicks immediately). The summon decisions
and the Children category are gated on the flags `mltd_deep_ones_summon_unlocked` /
`mltd_star_spawn_summon_unlocked` set by those options, not on focus completion. The summon
decisions gate on `mltd_controlled_population` (twice what each takes) - a second daily variable
summed with the toll's own `is_controlled_by = ROOT` and `> 500` filter, so the gate measures
exactly the pool the charge will spend from - and the toll falls on **every** owned+controlled
state over 500 people at once, in proportion to what each holds: `mltd_take_population_everywhere`
sums the pool into `mltd_toll_pool_k` with `state_population_k`, then charges each state
`population / pool_k * mltd_toll_target_k` - dividing first and working in thousands, because the
naive order overflows the variable ceiling on every state (see Gotchas). A state with a tenth of
the nation pays a tenth, so the big states carry most of it and none is emptied. The division then
rises at the **capital** (`mltd_spawn_*_division`), not in a paying state. Since 2026-09-23 neither
decision retires: each stays open once its unit can be trained (the Deep Ones summon used to hide
at `mltd.8`, the Star Spawn one at The Final Ritual), and after The Final Ritual their AI draws
only above 300,000 people, as the Leviathan's does. Each toll (`mltd_toll_target_k`) repeats as a
total in `mltd_deep_ones_toll_tt` / `mltd_star_spawn_toll_tt` (worded as a total since round 28c -
"taken from every state" read as a per-state figure) and in words in the decision's `_desc`, and
its gate, twice the toll, in `mltd_summon_state_pop_*_tt`; change them together. Gating on the
plain owned total would let an occupied MLT clear the gate and then spread the whole toll across
the handful of states it still holds, or - controlling nothing - pay nothing and get the division
free. Because the gate is only refreshed daily, the effect also floors every charge at whatever
leaves the state 500 people, so no summoning can empty one. Focus 4/5 grant the reward tech
(`enable_subunits`, so the unit appears in the designer; its `enable_equipments` is redundant with
the hidden tech) and `set_division_template_lock = { ... is_locked = no }`, guarded by
`has_template_containing_unit`. Consequence: the equipment is producible from the first summon
(reinforcements for the summoned divisions); the *unit* only from *The Deep Ones Walk* / *The Final
Ritual*. Template names are **string-matched** in the ensure effects, the raise effects *and* the
unlock lines - change them together. Both units are `special_forces = yes`. OWB's cap floor is 20
battalions; the permanent idea `mltd_children_of_the_deep` (added at focus 4) sets
`special_forces_min = 80` so the unlocked templates can actually be trained. Script-spawned units
bypass the cap, but they count against it. So since 2026-09-23 every summoned division brings its
own room: `mltd_spawn_*_division` (the Call's and the Walk's events and both summon decisions) ends
with `mltd_add_summoned_room`, which adds 8 - the template's 8 battalions - to
`mltd_summoned_sf_var`, read as `special_forces_min` by the dynamic modifier `mltd_summoned_host`,
and shows it as `mltd_summon_sf_room_tt`. The cap is the larger of that floor and OWB's 2 % of the
non-special battalions (`01_defines.lua:126-127`), which would need 5,000 of them to pass 100, so
the floor is what binds and a summon never takes a place a trained division could use. The room
stays if the division is lost. The 8 repeats in the tooltip; both templates are 8 battalions, so
change it with them. It is not a hard ceiling: OWB's tactics perks (`tactics_spec_ops_cap_tech`,
`_2`, `_3`, bought with army experience) and `mixed_army_doctrine`, Outsider Warfare's last step,
raise `special_forces_min` further for any country, so IC is what really limits the monsters.

**The territory give-away** (round 24). OWB's `return_stolen_territory` decision
(`common/decisions/territory_disputes.txt:317`) lets a country that has annexed another's cores
hand them back, and its `ai_will_do` is vetoed only by `dont_return_stolen_territory@FROM` - FROM
being the *demander* - or by the tag-agnostic `never_return_stolen_territory` (`:466-467`). OWB's
MLT history sets only `dont_return_stolen_territory@TRL`, so once TRL is annexed and a survivor
inherits its claims nothing vetoes the decision: an AI MLT gave its whole conquest back **at
peace**, reverting to its pre-war borders (run `20260917-212152`: `owned=15 pop_k=98` on day 1095,
`owned=5 pop_k=31` on day 1126, with no war start or end in between). Population then never reaches
the Grand Ritual's 100,000 gate, so the entire ritual column stalls. Our history override adds
`never_return_stolen_territory` beside OWB's line. This is fair play: it removes an AI-only
disadvantage - a human is simply offered the decision and declines - and the price of refusing, the
demander's claims and a `take_claimed_state` war goal on timeout, falls on both alike.

**The offerings** (in `mltd_children_of_the_deep_cat` alongside the two summons; the category opens
once `mlt_kingdom_of_mlyeh` completes and never closes, because each of its four decisions hides
itself). Two decisions trade population for something the tribe cannot otherwise get.
`mltd_offering_of_the_drowned` takes people from a random owned+controlled state large enough to
spare them and pays 100 **bottle caps** through OWB's `add_caps` (`caps_scripted_effects.txt:33`):
set `caps_to_add` as a temp variable immediately before it, never touch `caps_number_display`
directly - `add_caps` writes its own tooltip, plays the sound, runs the bankruptcy check, clamps to
[-1000, 25000], refreshes the top bar through `caps_topbar_update_var`, and pays 1.25x political
power instead when the caps game rule is off. `mltd_offering_of_the_tides` takes people the same
way and adds a permanent +4 `water` to `capital_scope` (OWB's own MLT tree does the same at
`Mirelurk Tribe (MLT) Focus.txt:184`; state 358 starts at 32). Both draw population exactly like
the summons. Since round 28b the random state is picked in `hidden_effect` behind a line that
states the rule (`mltd_offering_drowned_toll_tt`, `mltd_offering_tides_toll_tt`); the people taken
and the state floor repeat there and, in words, in each decision's `_desc` - change them together.

**Decision cooldowns.** Nothing in this mod uses `days_re_enable` any more: a decision on that
cooldown gives the player no countdown and (on the evidence available) may vanish from the category
outright, which is why the Deep Ones summon looked like it "only shows sometimes". Instead each
repeatable decision sets a timed country flag in a `hidden_effect`
(`set_country_flag = { flag = X value = 1 days = N }`) and gates on it in `available` through a
`custom_trigger_tooltip` whose loc prints the remaining days with the vanilla formatter
`[?<flag>:days_left|0]` (vanilla `nsb_decisions_l_english.yml:197`,
`SEA_decisions_l_english.yml:452`). The decision therefore always stays listed, greyed, with a
reason. Each cooldown's length is a literal in its flag, its `_cooldown_after_tt` and its
`_cooldown_tt`; change them together. Until 2026-09-23 the Deep Ones summon hid for good once
`mltd_star_spawn_summon_unlocked` was set (event `mltd.8`); it now stays, and `mltd.8` says so
(`mltd_deep_ones_summon_remains_tt`, which the Walk previews).

**Feed the Spawning Pools** is a **continuous focus**, the same shape as OWB's equipment-production
one: a `focus` block in the palette with `available`, `idea =`, `daily_cost`,
`supports_ai_strategy` and `available_if_capitulated = yes`. The engine adds the named idea while
the focus is selected and removes it when the player switches, so no script touches it and there is
no counter, no ladder and nothing to reset. The discount lives in the idea's `equipment_bonus`,
keyed by **archetype** so it reaches every variant - a dynamic modifier cannot carry
`build_cost_ic` (OWB tried: `kha_dynamic_modifier.txt:10` is commented out), and the equipment
*category* `infantry` is unusable because every creature archetype is `type = infantry` and it
would discount rifles too. -15 % matches what a tribal MLT can already get on rifles from
`OWB_continuous_Raider_production`; change it in `mltd_ideas.txt` alone. Like every OWB
continuous-focus idea it lives in a `hidden_ideas` block; OWB gives those ideas no localisation of
their own (the focus's name is what shows), but ours has some in case it ever renders.

**The animated portraits.** Both are `frameAnimatedSpriteType` frame strips, the only mechanism any
animated portrait in OWB (63 sprites) or tnkd uses - the `animation = {}` overlay block is for
focus shines and the frontend snow, and no portrait anywhere uses it. `build_animated_portrait.py`
holds a `SUBJECTS` table (the `build_leader_portraits.py` house pattern) and an `EFFECTS` dispatch.
*M'lulu* gets three parallax rain layers over the graded `mlulu.dds`: the loop closes because each
layer is drawn once into a periodic canvas and then translated by a fixed per-frame offset whose
total over the strip is an exact multiple of the canvas in both axes, so the rain frame count must
be a multiple of 40 (the canvas is 4 px wider than the portrait at 4x supersampling, which makes
the horizontal period a round number). A layer of speed `k` crosses the portrait `k` times per
loop, so `k` and `animation_rate_fps` are the only real speed dials. *The Drowned Herald* gets a
throb on his turquoise backdrop: amplitude `0.5 - 0.5*cos(2*pi*f/frames)`, which is 0 at both ends
with zero slope, so any frame count closes. Its mask is the crux - hue does **not** separate
backdrop from figure (the robes sit in the same 150-195 band and score 0.6-0.9 on a hue+saturation
test), but *teal excess against red*, `min(G,B) - R`, does: 28 on the backdrop against 2 on the
figure. The score is restricted to the blob connected to the frame edge and blurred; measured leak
onto the figure is 0.027 against 0.92 coverage of the backdrop. `noOfFrames` in `mltd.gfx` and the
strip width must agree - 156 x frames. M'lulu also gains `small = GFX_idea_MLT_mlulu` under both
portrait keys, which stops the engine deriving a small portrait from a 6240-px-wide strip
(`character_manager.cpp:319` complains about exactly that for OWB's RCK generics) and finally puts
the graded small icon this mod already ships to use.

**The rituals** are long focuses whose idea exists only while the focus is in progress:
`select_effect = { hidden_effect = { set_variable ...  add_ideas ... } }` (the toll factor) and
`completion_reward` starts with `hidden_effect = { remove_ideas = ... }`. The visible tooltip is
`custom_effect_tooltip = mltd_ritual_duration_tt` ("For the duration of the ritual:") followed by
one `set_temp_variable = { mltd_tt = <value> tooltip = mltd_<modifier>_tt }` line per idea modifier
(loc `$MODIFIER_X$: $RIGHT|+=%1$` - tnkd's in-game-tested idiom,
`Think Tank (TNK) Focus.txt:1958`), the toll literal, then a blank line
(`custom_effect_tooltip = mltd_newline_tt`, whose value is `" \n"` - OWB's `spacer_tt` idiom)
before the rest of the rewards. Those values duplicate `mltd_ideas.txt` - change both. Both are
`cancelable = no` and `available_if_capitulated = yes` (the idea has `removal_cost = -1`; a
cancelled or paused ritual would leave the toll running) and `cancel_if_invalid = no` +
`continue_if_invalid = yes` (the toll can push the population back under the gate mid-ritual).
Gates: `check_variable = { mltd_national_population > 99999 / 199999 }` in a
`custom_trigger_tooltip` in `available` (i.e. at least 100,000 / 200,000; the five-tag kingdom is
~75k at start, so both gates require real expansion); `mltd_national_population` is recomputed
every day by `mltd_update_national_population` and reads 0 until the first daily tick. Since the
round-27 review it is summed in thousands
(`add_to_variable = { PREV.mltd_national_population_k = state_population_k }` in
`every_owned_state`, OWB `exodus_effects.txt:392-396` precedent), then copied back into people and
capped at 2,147,000, as is `mltd_controlled_population` (the summons' pool): a raw sum of
`state_population` wrapped negative past ~2.1M people (Gotchas), which the later story acts reach,
and would have failed the Final Ritual's gate - and every act after it - for good. Every gate and
AI guard on the two variables sits below the cap, so the cap changes no test; the ritual tooltips'
*currently* simply stops at 2,147,000. The `_k` variables keep the true figure. **The toll.**
`on_daily_MLT` calls `mltd_ritual_daily_toll` while either ritual idea is held: for every owned
state with > 500 population it removes `state_population * mltd_ritual_toll_factor` (at least 1).
Tunables: the two factors in the `select_effect`s; the > 500 skip and the `max = -1` floor in the
effect; the same numbers are repeated **as literals** in `mltd_grand_ritual_toll_modifier_tt` and
`mltd_final_ritual_toll_modifier_tt` (literals, because a focus preview renders before
`set_variable` runs). Change all of them together.

**Events.** `mltd.1/3/5/7/8` are `country_event`s for MLT (`fire_only_once`, log line kept).
`mltd.2/4/6` are plain `news_event`s (`is_triggered_only` only - no `major`, no `fire_only_once`)
that the focus delivers with
`hidden_effect = { every_other_country = { news_event = { id = X days = 2 } } }`, so MLT itself
never receives them; each has one untriggered option `.a` written from the outside world's
perspective. Options carry no effects - the focus already applied them. **Event text colours:**
OWB's event paper is pale and its event fonts render `§Y`/`§H` as yellow and `§G` as light green
(unreadable there); OWB defines no dark purple, so event `.t`/`.d` strings use only `§o` (Zaffre
dark blue, 20 20 180) for names and `§c` (wine, 158 56 82) for emphasis, and option strings carry
no codes at all (they render white on a dark-brown button). Focus/decision/idea tooltips sit on
dark backgrounds and keep `§Y`/`§G`/`§R`. `mltd.9-18` (flavour) and `mltd.101-503` (Book
expeditions) follow the same colour rules. So do the story acts' events (`mltd.30-74`, round 27),
which also follow the same pattern: MLT country events with the log line, and news events delivered
by the close. Their options carry no effects either, with two exceptions: the trophies `mltd.40`
and `mltd.51`, whose options apply the choice. Each of those two closes previews both options with
`effect_tooltip` - `mltd.51`'s since round 28b by calling the options' own scripted effects,
`mltd_legion_pens_freed` / `mltd_legion_pens_fed`. Three events whose options carry a focus's
effects - `mltd.1` (the Drowned Herald's role, in both options), `mltd.7` and `mltd.8` - are
previewed the same way by the Kingdom, the Call and the Walk (round 28b; Project > *Every effect
shows before it is taken*). The invitations (`mltd.21`, `mltd.24`, round 28's `mltd.32`) are the
other kind: sent to the invitee, their two options are its answer and carry its effects, weighted
for an AI by `ai_chance` (The story acts > *The invitations*).

**Operation.** `common/operations/mltd_operations.txt`: `allowed`/`visible` on
`original_tag = MLT`, no `operation_target` (any country MLT has a network in - an operation can
never target yourself). It is five operations, `mltd_op_indoctrinate_the_faithful_<amount>`, one
per band of the target's manpower, because an operation's `equipment` is a fixed base cost (vanilla
`common/operations/_documentation.md:151-158`): each is `visible` only while the target's manpower
is in its band, so the intelligence screen shows exactly one, and all five share the loc keys
`mltd_op_indoctrinate_the_faithful(_desc)`, the icon and the phases. Each variant holds its band,
the manpower it moves FROM -> ROOT and its support-equipment price (the file's header comment lists
them); the lowest variant also shows, greyed, below its band. At completion
`mltd_indoctrinate_transfer` moves the variant's amount, or less if the target has since fallen
into a lower band, so MLT never gains manpower the target does not lose; since round 28c the
outcome tooltip, `mltd_op_indoctrinate_the_faithful_tt`, says so, and says the defector comes only
if the target has one to spare. The bands and amounts repeat there. `cost_multiplier = 0` turns off
the engine's default +15 % cost per repeat against the same target
(`DEFAULT_OPERATION_COST_MULTIPLIER`, vanilla `00_defines.lua:3733-3737`). Nothing else: no
stability, no war support. Its critical success (`outcome_extra_execute`, which replaces the base
outcome when it fires and so repeats the transfer, as vanilla's do at `00_operations.txt:246-279`)
also runs `mltd_indoctrinate_defector`: `random_army_leader` picks a `mltd_defector_candidate` - an
unassigned one if there is one; never a field marshal, a country leader or anyone with a
country-leader role, an advisor, an exile, or one of OWB's 66 story generals in
`mltd_defector_story_character` - and `set_nationality = ROOT` moves the character with every role,
skill and trait (OWB `exile_on_actions.txt`, vanilla `AAT_Finland.txt:741-754`). If the defector
turns out invisible in MLT (175 of OWB's 768 army-leader roles carry a `visible` trigger, mostly on
the old country's focuses or flags), they are sent back; with no valid general nothing more happens
(the old kin bonus is gone). Event `mltd.20` names the defector and their old country (picture
`GFX_event_sub_generic_war_room`). The whole agency system needs the La Resistance DLC; the file
loads silently without it. Any *script* that references the agency must be wrapped in
`has_dlc = "La Resistance"` (OWB `cartel_on_actions.txt:4-7`).

**The Leviathan** (round 26). A capital ship that is only ever summoned. Its equipment
(`common/units/equipment/mltd_equipment.txt`) is **non-modular** the way vanilla's repair ship is
(`repair_ships.txt`: an archetype with no `module_slots`, a variant with `module_slots = inherit`),
so the designer offers nothing to fit and every stat is the hull's own;
`can_be_produced = { always = no }` keeps it out of every dockyard even though
`mltd_leviathan_tech` enables it. Its numbers are sized against a Heavy Floating Fortress
(`ship_hull_heavy_5`) fitted with late modules - the equipment file's header works the comparison -
and differ where the brief asked: visibility 8 (a third of the Fortress's), fuel 0 (OWB's "energy
cells"), speed 18, range 6,000. Hit profile is visibility x the sub-unit's `hit_profile_mult`, so
the sub-unit `mltd_leviathan` (`common/units/mltd_units.txt`) carries 2.5 to keep it about as
hittable as a Fortress once battle is joined: hard to find, not untouchable. Its own sub-unit also
keeps it out of OWB's per-unit sea-terrain penalties (`common/terrain/00_terrain.txt` names
`heavy_ship_unit` and `super_heavy_ship_unit` in fjords); `category_capital_ship` techs and
doctrines still reach it. The weather resistance is `navy_weather_penalty = -0.5` on
`mltd_leviathan_tech`: it is a country modifier - no ship or sub-unit stat touches weather - so it
covers MLT's whole navy. *Raising it.* A ship cannot be made with `create_unit`, so
`mltd_spawn_leviathan` does what OWB does for the Palace (`_BRK_decisions.txt:44-48`): the tech,
then `load_oob` - `history/units/mltd_leviathan_first.txt` once (flag `mltd_leviathan_raised`;
pride of the fleet), `mltd_leviathan.txt` after that. An OOB names its naval base and loads there
whoever holds it, so the decision and the effect itself test `mltd_leviathan_can_surface` (control
of Mireport, 7064, the capital's naval base). The Grand Ritual raises the first one only if that
holds (otherwise the first summon becomes the pride of the fleet); the tech and the decision come
either way. Mireport is tested when the preview is drawn and again when the 120-day ritual
completes, so since round 28c's review both of its lines say so, as Return to the Sea's do:
`mltd_grand_ritual_leviathan_tt` over a hidden `mltd_spawn_leviathan` while Mireport is held,
`mltd_leviathan_no_mireport_tt` while it is not. *The tech* sits in the naval folder's unique
column at `x = 6, y = 36` (`tech_naval.txt`'s `@Row_3` / `@Col_11`, below the Palace), as a path
child of `brk_palace_ships_tech` through the `tech_naval.txt` override;
`allow_branch = { original_tag = MLT }` hides it from everyone else. It is never researched
(`allow = { always = no }`); `mltd_the_grand_ritual` grants it. *The summon*
(`mltd_summon_the_leviathan`, Children of the Deep, visible from `mltd_leviathan_summon_unlocked`)
never retires, since the ship can never be built: every land pays the toll
(`mltd_toll_target_k = 24`), gated at twice that on `mltd_controlled_population`, on a 180-day
timed-flag cooldown, for 100 political power. The 24 / 48,000 / 180 repeat in
`mltd_leviathan_toll_tt`, `mltd_summon_state_pop_leviathan_tt`, `mltd_summon_the_leviathan_desc`
and `mltd_leviathan_summon_cooldown_after_tt`. Its AI guard keeps the nation over the Final
Ritual's gate and, after it, summons only above 300,000 people. There is no focus of its own (round
26 first shipped one, *The Leviathan Wakes*, and removed it the same round): the Grand Ritual's
completion does it all. *Art.* No new art: the tech takes OWB's `VTS_tales_of_monsters` goal icon,
the equipment the Floating Fortress's hull icon, the event `GFX_event_BRK_shipwreck`, and the
sub-unit the super-heavy hull's model and ship icons (declared under `mltd_leviathan`'s names in
`interface/mltd.gfx`, since the engine looks ship icons up by sub-unit id).

**Reward-tab techs.** A tree root in `fallout_focus_tree_folder` only renders if
`interface/countrytechtreeview.gui` has a gridbox named `<root_id>_tree`; OWB ships an orphaned
`warbike_unlock_tech_tree` (gui ~line 3893) and nothing else usable. So the Deep Ones tech id **is
`warbike_unlock_tech`** (its "Warbikes" strings are overridden in `localisation/replace/`), and
`mltd_star_spawn_tech` chains from it via `path` to share the gridbox. Never add a second
reward-tab root; overriding the 9,300-line gui would clash with OWB Tech Expansion / UTCM, which
both ship it. Positions are `x = 4, y = 24` (Deep Ones) and `x = 4, y = 28` (Star Spawn) - OWB
`tech_hidden.txt`'s `@Row_unit3` / `@Col_11` and `@Col_13`, i.e. the "Units" band row holding
`sentinel_unit_tech` (4,4), `mininuke_unlock_tech` (4,8), `artillery_ammo_unlock_tech` (4,12),
`gehenna_molech_tech` (4,16) and `faerie_unlock_tech` (4,20), continuing its 4-column (280 px) step
because `enable_equipments` techs render in the 183 px `techtree_fallout_focus_tree_folder_item`
window. In this gui `x` is the vertical row (150 + 70·x px) and `y` the horizontal column.
Equipment icons follow OWB's `GFX_<equipment_id>_medium` + `alwaystransparent = yes` convention
(OWB declares none for its own creature equipment - those inherit the unlocking tech's icon).

**MLT's melee icons** (the Tridents, MLT's Heavy Melee Weaponry, and OWB's two knives resized). OWB
already gives MLT its own first two melee tiers, the Cultist Knife (shown under the generic name
*Basic Melee Weaponry*) and the Conch Knife, and the third is ours, done the same way - no script,
no file override:

- *The icon.* For a tech's icon the engine looks for `GFX_<TAG>_<tech_id>_medium` before
  `GFX_<tech_id>_medium`. OWB declares `GFX_MLT_melee_weaponry_tech_1_medium` / `_2_medium` in
  `z_fallout_technologies_faction.gfx`; we declare `GFX_MLT_melee_weaponry_tech_3_medium` in
  `interface/z_mltd_technologies_faction.gfx`. The equipment a tech unlocks has no sprite of its
  own and inherits the tech's, so production and logistics show the trident too.
- *The two knives.* The same file declares OWB's two sprite names again, pointed at our own copies
  of its textures. The last declaration read wins and `.gfx` files are read in filename order
  (Gotchas), hence the `z_mltd_` name. Overriding the two textures by path would be simpler but DIS
  uses them too. unverified in game; if MLT still shows OWB's sizes, the rule is wrong and the path
  override is the fallback.
- *The tech box* (`countrytechtreeview.gui`, `techtree_fallout_infantry_folder_item`: 183x84 over
  vanilla's `technology_*_item_bg.dds`) draws the icon centred on (91, 50), so a 60-px texture
  covers box rows 20-79. Measured off the background: the name band ends at row 17, the main panel
  is rows 18-64, a darker strip runs along rows 65-78 and the frame closes at 79. An object centred
  in its texture therefore sits 9 px below the panel's centre, and OWB's Conch Knife (47 px tall)
  reached row 72 with its glow on the frame. `build_tech_icons.py` scales both knives (`scale`) and
  puts the vertical centre of all three objects on texture row 24 (`CENTRE_Y`), which keeps the
  tallest, the Conch Knife, inside the panel with its glow ending where the strip begins. Every
  other tech's icon still sits at OWB's height.
- *The size.* The textures stay 130x60: 1,220 of OWB's 1,250 equipment icons are, and the unit,
  intel-ledger and pop-up views draw the sprite from its top-left corner, so a wider texture (OWB
  has a few, e.g. its 160x38 anti-tank gun) overflows to the right there. The trident is five times
  longer than it is wide, so lying flat it is limited by the width, and the 5 px glow has to fit
  past both tips: `fit_w` is the longest that leaves nothing on the texture's border. Edge to edge,
  as OWB's swords and machetes are, its glow was cut square and read in game as cropped ends. Since
  the trident cannot grow, the knives shrink (`scale`) until the three look in proportion. A wider
  texture is the only way to a bigger flat trident.
- *One shadow.* Every OWB icon carries the same pure-black outer glow. Scaling a finished icon
  scales that glow with it, so it comes out thinner and softer than its neighbours', and the Conch
  Knife's faint coloured wisps (OWB's icon has them up to 12 px from the shell) smear into it. So
  the knives are cut out first: the glow is pure black, which makes the icon's premultiplied colour
  the object's own, and the object's alpha is whatever lies above the glow's peak beside the object
  (`GLOW_EDGE`). All three objects then get one generated glow (`GLOW`, from a distance transform);
  `report` prints each icon's glow by distance against OWB's.
- *The name.* A tech that enables equipment shows the equipment's name, and the engine looks for
  `<TAG>_<equipment_id>` first: OWB's `MLT_melee_equipment_2`
  (`fallout_equipment_faction_l_english.yml:972-974`), our `MLT_melee_equipment_3`, `_short` and
  `_desc` in `mltd_l_english.yml`. OWB defines no such keys for tier 3, so they are new keys, not
  `replace/` overrides. Ours are plain text (OWB's are one-level aliases of a shared
  `melee_weaponry_tech_icon_*` key, because DIS shares its knives; nothing shares the trident).
- *The tag.* Both lookups use the country tag, never the cosmetic tag - OWB keys none of its
  3-letter-prefixed icons or names to one - so the trident survives the Kingdom's
  `MLT_cosmetic_tag` as the Conch Knife does. It also follows the tag: another country that annexes
  MLT sees Heavy Melee Weaponry.
- *Left generic*, as OWB leaves the Conch Knife: the Organization Marketplace lists the tier under
  its own static name and icon (`melee_runner_equip_3`, `GFX_melee_weaponry_tech_3_medium` in
  `_organization_scripted_localization.txt`), for every country.
- *The textures* are built by `build_tech_icons.py` (Layout): the trident from a third-party
  cut-out whose licence is unverified, the knives from OWB's own icons (`event_images/SOURCES.md`).
  After an OWB update, rerun it - it reads OWB's two knives - and check that OWB has not given MLT
  a tier-3 icon or `MLT_melee_equipment_3` of its own.

**Portrait.** `build_portrait.py` is a deterministic Pillow/numpy colour grade of OWB's painting
(soft background mask -> abyssal teal gradient, cold split-toning, S-curve, vignette, rim, grain);
the small icon is the graded portrait warped back into OWB's shared photo-card template
(`ICON_FIT`, `icon_photo_mask.png`). It is **not** repainted art - a human or an inpainting tool
would still need to paint real water/abyss texture and rim light and clean the silhouette halo.

**The Star Spawn model** (2026-09-21). Star Spawn **and Deep Ones** divisions are drawn with the
mod's own 3D model, a Cthulhu miniature: one entity, one size, both sub-units' `sprite` naming it
(until the rig went in, the Deep Ones wore OWB's mirelurk). Their equipment needs nothing: a land
unit's model comes from its sub-unit's `sprite`, and an equipment's `visual_level = 0` falls back
to that entity, as the Star Spawn's did in game. **Seen in game once, as a static mesh**: it drew,
textured and lit as designed - so a skeleton-less mesh does serve as a unit's main entity in OWB,
and the script's own DXT5 blocks and spliced mip chains load - but at entity scale 1.2 it read as
too large (9.6 units, twice the mirelurks beside it), and with no skeleton it glided like a chess
piece. Since then it is scale 1.0 and has a skeleton, a skin and six animation clips, **none of
which has been seen in game yet**. `build_unit_model.py` makes all of it from a ~2-million-triangle
3D-print sculpt that carries no UVs, no colour and one fixed pose, and everything it relies on was
measured from the game's own files - OWB's where OWB overrides vanilla's:

- *Lookup.* A sub-unit's `sprite = X` resolves to the entity `X_entity`; a `TAG_` or
  graphical-culture prefix overrides it. OWB's `sprite = mirelurk_infantry`
  (`common/units/creatures.txt:162`) -> `mirelurk_infantry_entity`
  (`jango_owb_base_entity.asset:370`), which `DED` (Deadline) overrides with
  `DED_mirelurk_infantry_entity` (`retexture_infantry.asset:12`); vanilla's `sprite = infantry` ->
  `infantry_entity` (`units_infantry.asset:141`). So `sprite = mltd_star_spawn` - on both of our
  sub-units - needs only `mltd_star_spawn_entity`. A `pdxmesh` is declared in a `.gfx`
  (`objectTypes = { pdxmesh = { ... } }`), an entity in an `.asset`; OWB keeps both under
  `gfx/models/owbentity/`, vanilla under `gfx/entities/`, and the engine reads either.

- *The rig.* 32 bones in the script's `RIG` table (the shader holds 50: `float4x4 matBones[50]`,
  OWB's `pdxmesh.shader:234`): a root on the ground, pelvis - spine - chest - neck - head, three
  two-bone beard bundles, three-bone arms and wings, four-bone legs. The sculpt is a posed
  miniature, not a T-pose, so the joints were placed **by measurement**: each part sliced along its
  own axis for its centre line, the bends read off that, every joint then walked to the middle of
  its limb (up the distance-to-surface field, across the bone only) and checked for lying inside
  the body, and left and right segment lengths compared (left over right, from `RIG`: arms 1.05 /
  0.96 / 1.05, wings 1.04 / 0.93 / 1.05; the legs differ more - thigh 1.15, shin 0.82 - because the
  sculpt's rear leg is out in a lunge and the walk across the limb drags a hip or shoulder into the
  torso, where the body is thickest: the right hip was mirrored from the left by hand). The table's
  order is the export order and is **depth-first** - a bone, then its whole subtree - as all 487
  skeletons in vanilla and OWB are; `check()` holds it to that. Every bone exports with an
  **identity rest orientation** - its bind matrix is a translation to its joint, so `tx` (the
  inverse bind, four columns of three) is `I | -joint` and a pose's rotation about the model's axes
  is the bone's local rotation as it stands. The engine does not care how a bone is oriented at
  rest; an animator does. Skin weights are Blender's automatic (bone heat) weights on the low-poly
  (`bl_stage_weights`; it converges on this decimated mesh, which is a closed manifold), cut to the
  four strongest per vertex and renormalised: the vertex shader takes four influences and rebuilds
  the fourth weight as `1 - the other three` (`:241`, `:290`), so weights that do not sum to 1 skew
  every vertex. An unused influence is `-1` / `0`, as in OWB's meshes. With a skin in the mesh the
  engine takes the effect's Skinned variant by itself (the mirelurk names plain `PdxMeshAdvanced`
  too); that variant also defines `ATLAS`, which only offsets the *diffuse* UV by a per-entity
  constant - the mirelurk's situation exactly.

- *The clips* are modules in `unit_model_clips/`, one per animation id: `SECONDS` and
  `clip(u, rig) -> pose` for `u` in 0..1, a pose being
  `{bone: rotation vector in degrees about the model's axes, "bone.t": translation}`. The
  convention (right-hand rule, the figure facing -y with x to its left): **+rx pitches forward** -
  an upright part bows, a forward-pointing part (head, the raised arm, a foot) dips, a hanging limb
  swings *back*; +rz yaws to its left; +ry rolls a part's top to its left. Feet are driven by
  `rig.ik` - analytic two-bone IK that bends the knee about the axis it is already bent about in
  the sculpt and keeps the foot level - so a planted foot stays planted while the body moves. That
  hinge is read off the sculpt's own bend, which on the 99 % straight rear leg is a slim 12
  degrees: moving `shin_r` by 0.05 turns its hinge by up to 26 degrees, so re-look at `move` after
  touching that joint (a truly straight limb is refused outright). Every clip **ends where it
  starts**, and the variants that one state draws between - `idle` / `idle2`, `attack` / `attack2`
  \- also **start in the sculpt's own pose** (`check()` holds them to it), so they chain without a
  step; `move` and `defend` close on their own crouched poses and rely on the states' blend times.
  A clip must be a whole number of frames.

  - `idle`, 4 seconds: the sculpt's pose, breathing: chest, wings a beat behind, the beard
    drifting, the raised claw flexing. In `STATES`: `idle` (chance 4).
  - `idle2`, 5 seconds: a slow look to its right, then head back, wings spread, beard flaring: a
    bellow. In `STATES`: `idle` (chance 1), `training`.
  - `move`, 1.75 seconds: a heavy, crouched walk, two steps a cycle. In `STATES`: `move`; `retreat`
    at `animation_speed = 1.25`.
  - `attack`, 2.25 seconds: rears back with the left claw raised, lunges and rakes it forward and
    down, recovers; the rear foot steps up with the lunge, and the wing tips and the beard trail
    the body by a frame or two. In `STATES`: `attack` (chance 3).
  - `attack2`, 2.5 seconds: twists to load the hanging right hand, swings it across while the wings
    buffet, the head snaps down and the beard flares *forward* (swung back it sinks into the chest
    and vanishes). In `STATES`: `attack` (chance 2), `support_attack`.
  - `defend`, 3 seconds: hunkered low, wings mantled forward like a shield - not far inward, or
    both wing spars pass through the head - arms drawn in, bracing once a loop. In `STATES`:
    `defend`.

  Idles and attacks are `looping = no` variants drawn by `chance`, each attack handing back through
  `next_state = "attack"` - the idiom of OWB's `mirelurk_entity` and of vanilla's
  `infantry_rifle_entity`. There is **no `death` state**: the mirelurk has none either. The
  sculpt's rear leg is 99 % straight, so a walk centred between the sculpt's own foot positions
  locks the knees: `move` centres its stride 0.8 behind the hips, on symmetric tracks, with the
  pelvis 0.2 lower, and its foot paths leave and land at the ground's own speed (a cubic Hermite),
  so nothing snaps. It also gives `rig.ik` a **pole** - the direction the knee should point,
  forward and a little out: the limb is spun about its hip-to-ankle line until it does, the ankle
  staying on target. Without one the knee goes wherever the smallest rotation leaves it, and the
  right leg, folded far from the sculpt's lunge, threw its knee out sideways and above the hip for
  a third of the cycle. `check()` cannot see that, nor a beard inside a chest: closure, the ground
  and edge stretch are all it gates, so **look at the contact sheets** (`--clip`) from more than
  one side after touching a clip.

- *The files.* The skeleton is an object of bones under the shape, after the mesh: `ix`, `pa` (the
  parent's index; none on the root), `tx`; the skin an object under the mesh, after the material:
  `bones = 4`, `ix`, `w`. An `.anim` is `info` (`fps`, `sa` = samples, `j` = bones) holding one
  object per bone - `sa`, a string naming which of `t` / `q` / `s` it animates, and its first `t`,
  `q` (x, y, z, w) and `s` - then `samples`, the animated curves packed frame by frame and, within
  a frame, bone by bone. Both are OWB's mirelurk's layout property for property; OWB's clips are 24
  fps and their last sample repeats the first (61 samples are 60 steps), and so are ours. `q` and
  `-q` are one rotation but the engine interpolates between samples, so each bone's quaternions are
  kept on one side from frame to frame. **`emulate()`** plays a `.mesh` and an `.anim` read back
  from disk as the engine does - `world = parent's world . T(t) R(q)`, a vertex moved by
  `sum of weight . world . tx` - and was proven on OWB's mirelurk with its idle, run and attack
  clips (feet held on the ground in every frame, claws thrust to z = -6 in the attack, the last
  sample the first; an independent emulator written from `io_pdx_mesh`'s importer agrees with it)
  before it was trusted with ours. `check()` holds every shipped clip, read back, to the pose it
  was written from (5e-7 units), and checks that it ends where it starts, never sinks below the
  ground, never stretches an edge more than 3x, and - for `move` - keeps a foot within 0.12 of the
  ground in every frame.

- *Authoring.* `python build_unit_model.py --clip move` samples one clip from the caches, prints
  what makes motion read as natural or broken - whether it closes, the mesh's lowest point, how
  long each foot is planted and how steadily it travels back while it is, how straight each leg
  gets against its full length, the fastest joint in degrees per sample - and draws its contact
  sheet, in about three seconds; nothing is written to `mod_folder`. `--preview` draws every sheet
  and `event_images/unit_model/animations.mp4`.

- *Space.* Y up, **-Z forward**, left-handed: the mirelurk's claws reach z -3.3 against +2.6
  behind, the deathclaw's tail lies at +6.1, vanilla's planes carry their tail fins at +8.5 and
  +9.2. Blender's `(x, y, z)` becomes `(x, z, y)` - a reflection - so V is flipped and the triangle
  winding reversed, exactly as `io_pdx_mesh` does. In OWB's and vanilla's meshes
  `cross(p1 - p0, p2 - p0)` agrees with the vertex normals on ~100 % of triangles; ours on 99.1 % -
  52 slivers, 0.4 % of the area, that decimation folded over a neighbour (rendered from 36
  directions with back-face culling, such slivers open no hole). `check()` also holds the signed
  volume to the mirelurk's sign: an STL's winding is not repaired on import, and an inside-out
  sculpt would flip it.

- *The `.mesh`.* `@@b@`, `pdxasset = { 1 0 }`, then `object` > the shape > `mesh` (`p`, `n`, `ta` -
  tangent plus bitangent sign - `u0`, `tri`) > `aabb`, `material` and `skin`, then the `skeleton`,
  and an empty `locator`: OWB's `mirelurk.mesh` object for object and property for property, with
  vanilla's material set (`shader`, `diff`, `n`, `spec`; the mirelurk's holds only `shader`). The
  format is `io_pdx_mesh`'s `pdx_data.py`, whose writer reproduced the static first version byte
  for byte; the script carries its own ~60-line reader and writer and needs no Blender add-on (the
  add-on predates Blender 5). Nothing strains the engine: vanilla's largest mesh has 38,447
  vertices, OWB's largest unit 33,711.

- *The shader is `PdxMeshAdvanced`*, as OWB's mirelurk (`mirelurk_mesh.gfx`) and every other OWB
  unit `meshsettings` that names a shader - 150 of OWB's 274 blocks; its 50 static buildings,
  cities and map objects use `PdxMeshAdvancedSnow` (the same defines plus `PDX_SNOW`), and whether
  a static *unit* wants that variant is unverified (Testing's snow check). **OWB overrides
  `gfx/FX/pdxmesh.shader` and `gfx/FX/standardfuncsgfx.fxh`, so its copies are the ones that run**
  (its `PdxMeshAdvancedLogo` exists nowhere else); as of this OWB version the normal and specular
  decode is vanilla's, line for line. The line numbers below are OWB's. `PdxMeshAdvanced` defines
  `EMISSIVE`, `PDX_IMPROVED_BLINN_PHONG` and `RIM_LIGHT` (`pdxmesh.shader:764-769`), which sets
  what the textures mean; plain `PdxMeshStandard` (`:725`) defines nothing and reads the same files
  in the legacy RGB layout (Gotchas).

  - **Normal map**: `UnpackRRxGNormal` (`standardfuncsgfx.fxh:311-318`) takes x from **G** and y
    from **-A** and rebuilds z; **B is the emissive mask** (`pdxmesh.shader:472`), so it stays 0 -
    under OWB's shader any blue there tints the model orange at night (`:558-559`; vanilla's lets
    the unlit diffuse through instead). The vertex shader rebuilds the bitangent as
    `cross(normal, tangent) * tangent.w` (`:258`); because the space swap is a reflection that
    bitangent is the mirror of Blender's, which cancels the shader's flip, so **A takes Blender's
    green channel as it is** and G takes its red: A means *up the image* (the OpenGL way), with the
    rows top-down. `check()` proves it on the shipped file: decoded the shader's way through the
    mesh's own tangent frame, the map reproduces an object-space bake through the same rays to 4.0
    degrees (median, DXT5 and the 512 downsample included), against 17.3 with A the other way up
    and 15.0 with no map at all. An independent test that uses no Blender data agrees: over 211
    vanilla `PdxMeshAdvanced` meshes with their own maps the shader's reading wins in 133 of the
    139 decisive cases, and ours lands on the same side. **Do not calibrate against OWB's own
    normal maps**: most of its modder-made ones (72 of 91 decisive) are green-inverted against the
    shader - which also shows how little an inverted green shows on a map unit.
  - **Specular map**: G is the specular level (`g * g * 0.4`, `:522`), B metalness (`:523`), A
    glossiness (`:476`); R is unused. Ours is a constant level, no metal, and a gloss that follows
    the occlusion - wet on open skin, matt in the cuts.
  - OWB's own mirelurk ships a flat normal map (128, 128, 0, 128) and an all-zero specular map: its
    creatures are diffuse-only.

- *Textures.* DXT5 with a full mip chain and OWB's header values (flags `0xa1007`, caps `0x401008`,
  linear size of the top level) - `mirelurk_d.dds` and vanilla's unit textures share those flags
  and caps, and most are DXT5. Pillow writes no mip chain, so each level is compressed alone and
  spliced under one header. Pillow compresses only the colour half of the diffuse's and the
  specular map's blocks: the alpha half of every block is the script's own (Gotchas), and so is the
  normal map's colour half, which fits G alone and keeps B at 0 in every endpoint - so at every mip
  level. A normal that leans past the surface (0.5 % of texels) is mirrored to +z before the mips
  are built, because that is what the shader's `+sqrt` reconstructs. The texels between UV islands
  are filled from their surroundings (a pull-push pyramid), so no mip level bleeds background into
  an island.

- *The look.* The sculpt has no colour, so the diffuse is painted from bakes: three noises and
  Cycles' pointiness pick between the palette's six colours (`DEEP` ... `CREVICE` at the script's
  top), a top light and wet feet are multiplied in, then the baked occlusion. Its brightness is set
  against OWB's `mirelurk_d.dds`, whose model stands beside it in the same army (luma p5 / median /
  p95: the mirelurk 40 / 58 / 110, ours 29 / 65 / 113 - the build measures and prints both). The
  preview sheet is an approximation, not the game: its roughness and specular level are derived
  from the engine's own maths, but Blender's BSDF conserves energy where the engine adds specular
  on top, and its map-size figures are downsampled renders on two terrain-coloured stand-ins.

- *The unwrap.* Smart UV Project shatters a decimated sculpt - 1,252 islands on 6,000 triangles,
  measured - because its angle test sees every bump, and its `island_margin` is added per island
  (15 % of the texture left in use). `bl_unwrap` projects a smoothed stand-in instead (three
  volume-preserving Laplacian passes; same topology, so the UVs are the real mesh's), puts the true
  coordinates back, rescales the islands against their true areas (`average_islands_scale`; without
  it thin parts starve) and repacks with an exact margin: 735 islands, 6,321 vertices, texel
  density within 1.5x across the 5th-95th percentile.

- *Pose and size.* This miniature stood on a scenic base that is not in the STL, so one sole hung 3
  % of its height in the air: `SRC_ROLL_DEG = -4.2` leans the figure onto both (`check()` holds
  both sides to the ground). The origin is the bounding box's centre, which for this
  forward-leaning figure lies under the torso, about 1.3 units ahead of the feet. The mesh is 8
  units tall and the entity's `scale` is 1.0: 8.0 on the map, against an OWB human's 5.9 (7.37 x
  0.8), a mirelurk's 4.8 and a deathclaw's 7.6 (6.3 x 1.2) - the game draws all of them at the same
  ~22 px a unit at the recording's zoom, so the first version's 1.2 stood twice as tall as the
  mirelurks beside it. `ENTITY_SCALE` in the script is the dial - it writes the `.asset`; the 1.0,
  the 8 and the 8.0 are repeated in the script's comments and in Testing's height ratio, so change
  them together. The bake distances (`CAGE_EXTRUSION`, `MAX_RAY_DISTANCE`, `AO_DISTANCE`) and the
  noise scales are absolute, tuned at 8 units.

- *Rebuild.* `python build_unit_model.py` - about a minute from nothing (import 1 s, decimation 20
  s, five OptiX bakes 4 s each, the skin weights 3 s), a few seconds from the caches, built and
  only ever run with **Blender 5.2.2 LTS** (the newest install under
  `C:/Program Files/Blender Foundation/` is used; pin one with `--blender`) plus numpy and Pillow.
  It writes into a staging folder, runs `check()`, and copies into `mod_folder` only if every check
  passes. The bake is cached in the system temp directory, keyed on the sculpt's hash, the
  `BAKE_KEYS` tunables and a hash of the script's baking half, so palette and scale changes take
  seconds and an edit to the unwrap re-bakes; a bake that dies half-way does not look current. The
  skin weights are cached beside it, keyed on the `RIG` tables, the low-poly and the weighing code;
  clips are not cached at all - they are arithmetic. **With the sculpt missing** it paints from the
  cache, and stops if a bake parameter - `SRC_YAW_DEG` and `SRC_ROLL_DEG` included - no longer
  matches it. Given one bake the outputs are byte-identical from run to run. Across re-bakes on the
  same device (OptiX, fixed `SEED`) the mesh and the occlusion bake are bit-identical; the normal
  and emission bakes differ by one float16 step in a few dozen to about 200 of 4.2 M texels, which
  moved a few diffuse blocks in one re-bake of five and nothing in the others. The `.gfx` and the
  `.asset` are generated - edit the templates in the script, not the files. The script writes one
  entity; a second model means extending `ASSET_TEMPLATE`, not a second run. A stale `.anim` that
  `STATES` no longer names is removed from `mod_folder` on publish.

- *The sculpt* (`cthuluMINI.V1.1.stl`) is the one source in this mod whose **designer, download
  page and licence are not recorded at all** - see `event_images/SOURCES.md`. The mesh is a
  derivative of it. The sculpt and the bake cache are the model's only inputs and neither is in the
  repo: keep a copy of the STL somewhere durable **outside** the repo (the repo is public and
  `.gitignore` refuses `*.stl`), and name a durable cache with `--work` if the temp directory is
  cleaned. With both gone the model cannot be re-posed or re-textured.

**The story acts** (round 27; OWB's Mojave Chapter pattern,
`common/national_focus/Mojave Chapter (MOJ) Focus.txt`, built from detached `shared_focus` branches
pulled into `mlt_nf`). From round 13 to round 26 the tree's second half was the *conflict
sub-trees* - ten of them by round 22, 46 shared focuses in `mltd_conflicts_focus.txt` - left and
right of the trunk, with no line to anything. Round 27 deleted that file and rebuilt its focuses as
one story down the centre column, x = 15. Act I - the national tree from the Kingdom to The Deep
Ones Walk - is unchanged. Five acts and a finale follow it, each built from:

- a **chapter** focus on the spine;
- a short **fan** of branches, one or two focuses deep;
- a **close** back on the spine, which the fan reconverges on through one OR prerequisite.

Every close fires an event and world news, most chapters fire one too, and three mutually exclusive
endings sit at the bottom. The 41 story focuses live in six files, `mltd_act2_focus.txt` ...
`mltd_act6_focus.txt` and `mltd_finale_focus.txt` (Layout):

- 27 are the old sub-trees' focuses under their old ids, because the AI, the plan, the telemetry
  and the events name them;
- 14 are new: the chapters and closes, Nuevo Aztlán's two focuses, R'lyeh Rises and the endings,
  since round 28 Terms for the Citadel, and since round 28c the Broken Coast's war twin, The Coast
  Goes Under;
- the other 19 old focuses were merged into a kept focus of their branch (*Merged away* below).

Beside them, a seventh file holds the spoils (round 28; restructured in round 28c): ten optional
focuses that are no part of the story's order, pulled in the same way (*The spoils* below).

- Act II *The Northern Waters*
  - Chapter (spine): none; the heads hang off The Grand Ritual (The Deep Ones Walk until
    2026-09-24)
  - Fan: Washington: `mltd_wbh_eyes_in_the_sound` -> `mltd_wbh_the_drowned_knights`; the Broken
    Coast: `mltd_brk_salt_on_the_broken_coast` -> `mltd_brk_the_deep_ones_sail_north`; the Bone
    Dancers: `mltd_bdt_the_bone_shore` -> `mltd_bdt_the_dancers_hear_the_tide`
  - Close (spine): none since 2026-09-24; each bead leads on to its nation's Act III pair (until
    then the fan reconverged on `mltd_the_final_ritual`)
- Act III *The Stars Are Right*
  - Chapter (spine): none; each pair hangs off its nation's Act II bead (off The Final Ritual until
    2026-09-23)
  - Fan: three pairs, an invitation and a war twin for each northern nation, mutually exclusive
    both ways: the Brotherhood in Washington (`mltd_wbh_terms_for_the_citadel` /
    `mltd_wbh_the_tide_wall`), the Broken Coast (`mltd_brk_the_drowned_covenant` /
    `mltd_brk_the_coast_goes_under`), the Bone Dancers (`mltd_bdt_hail_the_drowned_king` /
    `mltd_bdt_drown_the_dance`). Any one of the six opens `mltd_the_deep_ones_walk` (national), on
    the spine, and the Walk opens `mltd_the_final_ritual`
  - Close (spine): `mltd_the_tide_turns_south`, after The Final Ritual
- Act IV *The Drowned Republic*
  - Chapter (spine): `mltd_ncr_a_mole_in_shady_sands`
  - Fan: `mltd_ncr_drowned_delegates`, `mltd_ncr_sleepers_on_the_long_15`,
    `mltd_ncr_salt_on_the_caravan_roads`, then the war, `mltd_ncr_the_turbines_sing`
  - Close (spine): `mltd_when_shady_sands_falls`
- Act V *The Sea Against Mars*
  - Chapter (spine): `mltd_mars_in_the_water`
  - Fan: four branches, each a head then its war: the Legion (`mltd_ces_what_the_river_carries` ->
    `mltd_ces_the_sea_against_mars`), Lost Hills (`mltd_bos_the_drowned_paladin` ->
    `mltd_bos_blood_in_the_water`), Utah (`mltd_wht_the_lake_god_answers` ->
    `mltd_wht_rites_on_the_spiral_jetty`), Heaven's Guard (`mltd_hea_whispers_in_the_steam` ->
    `mltd_hea_the_crusade_turns_south`)
  - Close (spine): `mltd_when_the_legion_breaks`
- Act VI *All Waters Are One*
  - Chapter (spine): `mltd_the_southern_deep`
  - Fan: three branches, each a head then its war: Texas (`mltd_tex_all_waters_are_one` ->
    `mltd_tex_black_water_rising`), Nuevo Aztlán (`mltd_ate_the_feathered_tide` ->
    `mltd_ate_the_serpent_drowns`), Tlaloc (`mltd_tla_the_iron_god_dreams` ->
    `mltd_tla_the_drowned_god_sleeps`)
  - Close (spine): `mltd_the_last_king_kneels`
- Finale *R'lyeh Rises*
  - Chapter (spine): `mltd_rlyeh_rises`
  - Fan: the endings, mutually exclusive: `mltd_ending_the_dreamer_wakes`,
    `mltd_ending_the_priestess_reigns`, `mltd_ending_return_to_the_sea`
  - Close (spine): none

*Pull-in.* A shared focus enters `mlt_nf` only in two ways (Gotchas): the override lists it
(`shared_focus = <id>`), or it reaches a listed focus through prerequisites on other *shared*
focuses.

- **The listed four.** The override lists them at `Mirelurk Tribe (MLT) Focus.txt:26-29`, after a
  comment at `:20-25` and OWB's two `lurk_` roots. They are exactly the story focuses whose
  prerequisite is a national focus: the three Act II heads (The Grand Ritual since 2026-09-24; The
  Deep Ones Walk before) and The Tide Turns South (The Final Ritual). From round 27 to 2026-09-23
  Act III's focuses were listed in The Tide Turns South's place - nine lines by round 28c - because
  their prerequisite was The Final Ritual; since 2026-09-24 each names its nation's Act II bead and
  comes in with it.
- **The precedent.** Vanilla lists `CONGO_congo_investments` the same way at `belgium.txt:20`; its
  only prerequisite is `BEL_monetary_reconstruction` (`congo_shared.txt:951`). OWB has no such
  case.
- **Everything else** chains back to those four, across files too: Act IV's chapter names Act III's
  close, defined in `mltd_act3_focus.txt`, for both its prerequisite and its position. The spoils
  come in the same way, each through its prerequisite on an act's close.
- **The reverse direction.** The Deep Ones Walk is a national focus with one OR prerequisite over
  Act III's six focuses (since 2026-09-24; from round 27 The Final Ritual took one, over the three
  Act II ends until 2026-09-23 and over Act III's six briefly on 2026-09-24). That is vanilla's
  shape at `belgium.txt:7907`, where three `CONGO_` shared focuses reconverge on a national one.
- **Adding a focus.** A new story focus that names a national focus in its prerequisite must be
  listed too; one that names only shared focuses must not be. A new story file must also go into
  `STORY_FILES` in `build_telemetry.py`, which asserts the set of files it pulls in - as
  `mltd_spoils_focus.txt` did in round 28.

*The rules every story focus follows* (from round 27's build spec):

- **Positions.** The listed four take absolute `x`/`y`. Every other story or spoils focus takes
  `relative_position_id` to a *shared* focus, never to a national one: none of OWB's 464 or
  vanilla's 335 shared focuses does that, so it is untested. Siblings sit two columns apart (a box
  is 165 px against a 96 px column), so no two focuses on a row are one column apart. Since
  2026-09-24 Act II's heads stand four apart, so that each nation's Act III pair fits either side
  of its bead. A spoils focus takes the chapter it flanks as its anchor, on the chapter's own row,
  but names the previous close in its prerequisite (*The spoils*).
- **Tall icons** (round 28c). The Final Ritual's icon grows upward, so it has an empty row above it
  (26 since 2026-09-24, 24 before) and the next focus directly below it; and no icon taller than
  about 130 px sits directly below another focus (Gotchas). Since 2026-09-24 The Deep Ones Walk
  (152x171) has the same room, an empty row 24 above it, now that it sits below Act III; until then
  it stood directly under The Grand Ritual. The Last King Kneels was the other until round 28c's
  balance review gave it a short icon and took its empty row back.
- **Prerequisites.** Separate `prerequisite` blocks are AND; one block listing several focuses is
  OR.
  - Each fan reconverges on its close through **one OR block** over its last focuses, so any one
    branch opens the close. Since 2026-09-24 The Deep Ones Walk's names all six Act III focuses,
    the ritual names the Walk and The Tide Turns South the ritual; until then The Tide Turns
    South's named the six and the ritual's Act II's three beads.
  - From round 27 to 2026-09-24 The Final Ritual had no prerequisite on the Walk: every Act II head
    already needed the Walk, and a Walk -> Ritual line would have run solid down x = 15 through
    Salt on the Broken Coast and The Deep Ones Sail North. Since the Walk moved below Act III the
    ritual names it, over the empty row 26.
  - Each Act III focus names its nation's Act II bead in its prerequisite (since 2026-09-24), which
    also carries the Act II head that the three invitations named in `available`
    (`has_completed_focus`, no line) from round 27 on: the Covenant Salt on the Broken Coast, Hail
    the Drowned King The Bone Shore, and Terms for the Citadel Eyes in the Sound.
- **Exclusions.** Each Act III pair names the other in `mutually_exclusive`, both ways: MLT courts
  a northern nation or fights it, never both. Round 28b made the Brotherhood's pair (Terms, new in
  round 28, and The Tide-Wall) and the Bone Dancers' pair exclude each other both ways, and round
  28c gave the Broken Coast's Covenant its war twin. From round 24 to round 28 Hail the Drowned
  King excluded Drown the Dance on one side only, because a refused invitation then stranded the
  war branch; since round 28 a refusal leaves an expiring war goal instead, and the invitation's
  focus completes and opens The Deep Ones Walk (The Final Ritual earlier on 2026-09-24, the close
  until then) whatever the answer. Across nations the exclusion is a flag that only an accepted
  offer sets (*The invitations*). The endings each name both others.
- **Never strand.** An act's close must always have a takeable path, for a human and for the AI.
  - Every head and bead is takeable once its target is gone or is MLT's subject. `country_exists`
    is out of `available`, and the reward is an
    `if = { limit = { country_exists = X } ... } else = { ... }` whose `else` pays political power
    (or army experience, or a tech bonus).
  - **Bypass** (2026-09-23; the user found Drown the Dance paying +50 PP and declaring nothing, the
    Bone Dancers long gone). The 31 focuses aimed at a nation - every `mltd_<tag>_*` story focus:
    Act II's six, Act III's six, Act IV's five (A Mole in Shady Sands, the chapter, included) and
    the heads and wars of Acts V and VI - carry `bypass`, true once every nation the focus acts on
    is gone: `NOT = { country_exists = X }` per tag (NCR and MOT for the chapter and the Sleepers,
    WHT and EHT, TBH and LNS, TLA, MAX, MOC and ZAP for the war and ARM too for its head), or, for
    the four Washington focuses, `mltd_wbh_no_brotherhood_tt` over
    `NOT = { any_country = { mltd_wbh_brotherhood = yes } }`. A bypassed focus completes with no
    reward and reads as completed, so it still opens its close or chapter, and nothing strands. A
    spying head that is bypassed gives no agency upgrade. A target that is MLT's subject is not
    bypassed: the focus pays its fallback, as before, and so does one whose target dies while it
    runs (unverified: whether the engine bypasses a focus already in progress). The chapters,
    closes, spoils and endings have no nation of their own and no bypass.
  - **No intelligence gates.** Round 27 took every `has_operation_token`,
    `network_national_coverage` and `intel_level_over` test out of every `available`. The intel
    *rewards* stay, inside `has_dlc = "La Resistance"` (*The DLC idiom*).
  - The exceptions are the three invitations, which keep their courtship lines: since round 28c's
    balance review each asks for its invitee's cult at 40 %, that country's `token_civilian` and 25
    % coverage (*The invitations*). Until then the Covenant asked for 50 %, `token_civilian`, 30 %
    coverage and 50 % civilian intel, Hail the Drowned King for what all three now ask, and Terms
    for the Citadel (round 28) for no intelligence at all.
  - Act III cannot strand. Every invitation completes whatever its invitee answers - paying +50 PP
    where the offer could no longer be accepted (Hail the Drowned King since round 28c's review) -
    so taking one always opens The Deep Ones Walk (the close until 2026-09-24). The Coast Goes
    Under and Drown the Dance have no world gate: each is takeable unless its target is an
    independent ally in MLT's faction, which only an accepted invitation (whose focus has then
    completed) or the diplomacy screen can make it. The Tide-Wall keeps its world gate. So the
    Walk, and the ritual after it, always have a path: the Bone Dancers' column has no world gate
    from The Grand Ritual down, and a column whose nation is gone is bypassed.
  - The wars keep their story-world gates, each with a "target gone" branch or a date: The Turbines
    Sing, a Hoover outcome flag or 1 June 2279; Black Water Rising, `texas_formed` or 2280; The
    Tide-Wall, WBH's purge, a war with MLT, no Brotherhood left or 2280, and The Warren held; The
    Crusade Turns South, Heaven's Guard's holy wars or 2280; the Rites, the Utah road war or 2280.
    The Coast Goes Under, Drown the Dance, The Sea Against Mars, Blood in the Water, The Serpent
    Drowns and The Drowned God Sleeps have none.
  - The three war closes have no fallback date: each waits for its great war. *Beaten* means gone,
    capitulated now, capitulated to MLT at any time, or MLT's subject.
  - Why "at any time": `has_capitulated` clears once the country leaves its last war, so a rump
    that outlives the peace would never count again. So `on_capitulation` (`mltd_on_actions.txt`)
    records a capitulation while at war with MLT as a country flag on MLT: `mltd_ncr_capitulated`,
    `mltd_ces_capitulated`, `mltd_tbh_capitulated` or `mltd_lns_capitulated`.
  - The closes' gates are three triggers. The NCR's close reads `mltd_ai_ncr_beaten`
    (`mltd_ncr_beaten_tt`) and the Legion's reads `mltd_ai_legion_beaten`
    (`mltd_legion_beaten_tt`). Both are the AI's own stage tests in `mltd_ai_triggers.txt`,
    extended in round 27 so that the stages open exactly when the next act does. Act VI's close
    reads `mltd_texas_beaten` (`mltd_scripted_triggers.txt`), which needs both Texan tags beaten.
  - If the NCR is never beaten, the spine stops at When Shady Sands Falls (row 31), with only the
    north's spoils beside it. That is by design.
  - Every story focus has `cancel_if_invalid = no` + `continue_if_invalid = yes`, because targets
    die, and coverage and states come and go, while a focus runs.
- **Size gates.** Two focuses count land instead of a war: The Tide Turns South needs 50 controlled
  states (`num_of_controlled_states > 49`) or the year 2281 (round-27 review: run 8's AI held 35-39
  states for two years after its Final Ritual, which would have shut Acts IV-VI for the whole
  game), both repeated in `mltd_tide_turns_south_states_tt`; R'lyeh Rises needs 300 (`> 299`,
  repeated in `mltd_rlyeh_rises_states_tt`) and has no fallback - it is the finale. Change each
  pair together. One idea focus in each spoils group counts land too (*The spoils*).
- **Events.** Every close fires an MLT event and a world news event, which the close delivers
  through `every_other_country`, as the Kingdom does. Of the chapters, Act V's, Act VI's and R'lyeh
  Rises fire an MLT event (`mltd.50`, `mltd.60`, `mltd.70`); Act IV's chapter, A Mole in Shady
  Sands, fires none, and Acts II and III have no chapter. Act II has no event of its own. Act III's
  three invitations each send the invitee an event whose options are its answer (`mltd.21`,
  `mltd.24`, `mltd.32`), and the answer reaches MLT as an event of its own (*The invitations*). Act
  III's wars fire none.
  - Two closes' events carry the act's trophy as a choice. `mltd.40` (When Shady Sands Falls)
    offers a research slot, or `mltd_the_drowned_rangers` and army experience. `mltd.51` (When the
    Legion Breaks, round 28b) frees the chained - the permanent `mltd_the_unchained` - or feeds
    them to the pools - the timed `mltd_the_pens_emptied`, a build-cost cut on the three creature
    archetypes. Until round 28b it paid the capital's population and stability, or manpower.
  - Each close previews both options in its own tooltip with `effect_tooltip`, which shows an
    effect without running it. When Shady Sands Falls repeats `mltd.40`'s effects there, so their
    numbers live in the option and in the preview: change both. When the Legion Breaks calls the
    options' own scripted effects, `mltd_legion_pens_freed` / `mltd_legion_pens_fed`, so
    `mltd.51`'s numbers live only in the two ideas and in the timed idea's days.
- **Ideas.** Every close but the NCR's grants a permanent act idea; the NCR's is option b of
  `mltd.40`. Each ending grants its own idea. The old capstones' 180-day ideas stay with their war
  focuses (Layout, `mltd_ideas.txt`); The Coast Goes Under, sized like Drown the Dance, grants
  none. No invitation grants an idea (round 28: the war focuses keep the bonuses).
- **Focus AI.** `ai_will_do` is 3 for heads, beads and wars (The Coast Goes Under included), 10 for
  chapters, closes and R'lyeh Rises, 4 for Hail the Drowned King (above Drown the Dance's 3), 1 for
  Terms for the Citadel, 3 / 2 / 1 for the three endings, and 2 for every spoils focus. Those
  weights are tie-breaks only: an AI with a plan takes the first *listed* focus that is available,
  so what orders the invitations before the wars, and The Dreamer Wakes before the other endings,
  is the late plan's own order (MLT's AI > Focus order). A weight decides only between focuses no
  plan lists - a subject MLT's, whose plans all abort. *The AI* below covers the war focuses'
  holds.
- **Icons.** Every story focus reuses an OWB focus icon that has its `_shine`, the new focuses
  included. Round 28c gave three a normal-height icon, because a spoils focus now sits directly
  above them: Salt on the Caravan Roads `GFX_goal_MOJ_ncr_trade` (was `GFX_goal_NCR_Caravan`), All
  Waters Are One `GFX_goal_LNS_texan_dollar` (was `GFX_goal_CHC_Texas`) and The Dreamer Wakes
  `GFX_goal_MDT_gorgon_eye` (was `GFX_goal_CHC_madness`); each file's header says so. Round 28c's
  balance review did the same for The Last King Kneels, for the room rather than the neighbour:
  `GFX_goal_TBH_The_Last_Piece` (100x88, a claw closing on the map of Texas) in place of
  `GFX_goal_MIN_fallen_kingdom` (164x146, a ghoul king, and not Texan), which let the spine close
  up a row.

*Positions* (round 28c, `story_rework/SPEC_R28C.md`, with the rows as 2026-09-24 left them;
absolute cells, the spine is x = 15; relative positions in brackets; *(spoils)* marks a spoils
focus):

- Rows 19, 20, x 15: Call of the Deep Ones, The Grand Ritual (national, unchanged)
- Row 21, x 11, 15, 19: Act II heads, listed, under The Grand Ritual: `mltd_wbh_eyes_in_the_sound`,
  `mltd_brk_salt_on_the_broken_coast`, `mltd_bdt_the_bone_shore` (row 22 at x 13, 15, 17, under the
  Walk, until 2026-09-23)
- Row 22, x 11, 15, 19: their beads, (0,1) of each head: `mltd_wbh_the_drowned_knights`,
  `mltd_brk_the_deep_ones_sail_north`, `mltd_bdt_the_dancers_hear_the_tide`
- Row 23, x 10, 12, 14, 16, 18, 20: Act III, three pairs, each at (-1,1) and (1,1) of its nation's
  bead: `mltd_wbh_terms_for_the_citadel` / `mltd_wbh_the_tide_wall`,
  `mltd_brk_the_drowned_covenant` / `mltd_brk_the_coast_goes_under`,
  `mltd_bdt_hail_the_drowned_king` / `mltd_bdt_drown_the_dance` (row 26, listed, until 2026-09-23)
- Row 24 is empty: the room The Deep Ones Walk's tall icon grows into
- Row 25, x 15: `mltd_the_deep_ones_walk` (national; (0,5) of The Grand Ritual since 2026-09-24,
  (0,1) on row 21 before; OR over row 23)
- Row 26 is empty: the room The Final Ritual's tall icon grows into
- Row 27, x 15: `mltd_the_final_ritual` (national; (0,2) of the Walk since 2026-09-24, (0,4) since
  round 28b, (0,3) before)
- Row 28, x 15: `mltd_the_tide_turns_south` (absolute and, since 2026-09-24, listed; after The
  Final Ritual)
- Row 29, x 13, 15, 17: The Scribes' Vaults *(spoils)*, `mltd_ncr_a_mole_in_shady_sands` ((0,1) of
  row 28), The Drowned Sound *(spoils)* - the spoils at (-2,0) and (2,0) of the chapter
- Row 30, x 13, 15, 17: Drowned Delegates, Sleepers on the Long 15, Salt on the Caravan Roads
  ((-2,1) (0,1) (2,1) of the chapter)
- Row 31, x 15: `mltd_ncr_the_turbines_sing` ((0,2); OR over row 30)
- Row 32, x 15: `mltd_when_shady_sands_falls` ((0,3))
- Row 33, x 11, 13, 15, 17, 19: Salt in the Canals *(spoils)*, The Foundries Relit *(spoils)*,
  `mltd_mars_in_the_water` ((0,1) of row 32), The Office of Salt and Industry *(spoils)*, The
  Drowned Harvest *(spoils)* - the spoils at (-4,0) (-2,0) (2,0) (4,0) of the chapter
- Row 34, x 12, 14, 16, 18: What the River Carries, The Drowned Paladin, The Lake God Answers,
  Whispers in the Steam ((-3,1) (-1,1) (1,1) (3,1) of the chapter)
- Row 35, x 12, 14, 16, 18: The Sea Against Mars, Blood in the Water, Rites on the Spiral Jetty,
  The Crusade Turns South (each (x,2), under its own head)
- Row 36, x 15: `mltd_when_the_legion_breaks` ((0,3); OR over row 35)
- Row 37, x 13, 15, 17: The Legion's Armouries *(spoils)*, `mltd_the_southern_deep` ((0,1) of row
  36), The Iron Tithe *(spoils)*
- Row 38, x 13, 15, 17: All Waters Are One, The Feathered Tide, The Iron God Dreams ((-2,1) (0,1)
  (2,1) of the chapter)
- Row 39, x 13, 15, 17: Black Water Rising, The Serpent Drowns, The Drowned God Sleeps (each (x,2),
  under its own head)
- Row 40, x 15: `mltd_the_last_king_kneels` ((0,3) of the chapter; (0,4) from round 28b to round
  28c's balance review, which gave it a short icon and took its empty row back; OR over row 39)
- Row 41, x 13, 15, 17: The Black Water Wells *(spoils)*, `mltd_rlyeh_rises` ((0,1) of row 40;
  round 28b had it at (0,2)), The Salt Road *(spoils)*
- Row 42, x 13, 15, 17: the endings ((-2,1) (0,1) (2,1) of R'lyeh Rises)

The tree is now x 0-28 by rows 0-42, with 128 focuses: the 45 national ones, OWB's and ours, the 32
`lurk_` focuses, the 41 story focuses and the 10 spoils focuses. A grid resolve of it
(`python story_rework/tools/grid.py`, whose table round 28c's integration moved to SPEC_R28C's and
2026-09-24 to the rows above) gives 128 distinct cells, every one of the 51 shared `mltd_` focuses
and the four national cells from the Call to the Final Ritual on its spec cell, and rows 24 and 26
the only empty ones. The focus view scrolls and sizes itself to the tree, so no gui change is
needed.

- Every story and spoils focus is at x >= 10 and row >= 21. That keeps it clear of the default
  continuous-focus palette, which covers roughly columns 0-8, rows 7-10.
- No focus uses negative x or an `offset` block.
- The cells the old sub-trees used (x 0-9 and 21-30, rows 13-23) are empty again.
- Rows from The Tide Turns South down are one lower than round 28c's - its rows 27-41 are today's
  28-42 - since 2026-09-24 put the Walk and the ritual, each under an empty row, below Act III,
  which moved up to row 23. A note tagged with an earlier round gives that round's rows.

*Merged away* (round 27). Each deleted focus's distinctive effects moved into the kept focus of its
branch:

- Act II: `mltd_wbh_salt_in_the_citadel` ("Heresy in the Citadel") into The Drowned Knights
- Act II: `mltd_brk_the_drowned_raiders` into Salt on the Broken Coast
- Act II: `mltd_brk_star_spawn_over_the_strait` into The Deep Ones Sail North (its +3 volunteers)
- Act II: `mltd_bdt_salt_on_the_bone_road` into The Dancers Hear the Tide
- Act V: `mltd_ces_the_drowned_frumentarius` into What the River Carries
- Act V: `mltd_ces_salt_in_the_armouries` ("A Crate for Every Cross") into The Sea Against Mars
- Act V: `mltd_ces_the_chained_are_given_to_the_tide` into option a of `mltd.51`
- Act V: `mltd_bos_the_paladin_returns`, `mltd_bos_the_codex_unsealed` into The Drowned Paladin
- Act V: `mltd_bos_the_tide_takes_the_armoury` into Blood in the Water
- Act V: `mltd_wht_the_drowned_shamans`, `mltd_wht_guns_for_both_sides` into The Lake God Answers
- Act V: `mltd_wht_sand_in_the_engines` into the Rites
- Act V: `mltd_hea_a_second_schism` into Whispers in the Steam
- Act V: `mltd_hea_steam_for_the_deep` into the Crusade
- Act VI: `mltd_tex_the_silent_partner` into All Waters Are One
- Act VI: `mltd_tex_wreckers_on_the_trinity` into Black Water Rising
- Act VI: `mltd_tla_the_three_voices` into The Iron God Dreams
- Act VI: `mltd_tla_picking_the_iron_bones` into The Drowned God Sleeps

How the merges were done:

- **Duplicate intel.** A second intel grant to the same country became one `add_intel` at the
  larger values. Salt on the Broken Coast is the exception: it sums the two grants.
- **Fallbacks.** Where both halves had a no-DLC fallback, the fallbacks are summed.
- **Tech bonuses.** A tech bonus that was named after a deleted focus now carries the name of the
  focus that grants it.
- **Lengths.** Act II's four merged focuses - Salt on the Broken Coast, a head, and three beads -
  grew longer, to pay for what they absorbed. Acts V and VI kept their focuses' old lengths. Since
  2026-09-25 every focus of ours takes 7, 30, 60, 120 or 180 days (Project > *Focus lengths*): the
  four merged focuses and the invitations 60, every other head, bead and war 30.
- **Loc.** The deleted focuses' loc keys went with them, and so did the dropped gates'
  `mltd_<tag>_network_<pct>_tt` tooltips.

*The agency.* MLT starts with no intelligence agency (OWB's history creates none). Eleven story
focuses call `mltd_intel_foothold` first; these are the spying heads:

- Act II: Eyes in the Sound, Salt on the Broken Coast, The Bone Shore;
- Act IV: A Mole in Shady Sands;
- Act V: What the River Carries, The Drowned Paladin, The Lake God Answers, Whispers in the Steam;
- Act VI: All Waters Are One, The Feathered Tide, The Iron God Dreams.

What the helper does:

- Since round 14 the helper no longer founds the agency: *The Spreading Cult* does, with
  `create_intelligence_agency`, whose `name` is the literal "The Esoteric Order of M'lyeh" (see
  Gotchas) and whose `icon` is `GFX_intelligence_agency_logo_mltd_esoteric_order` - the shape of
  Black Canyon's call (`Black Canyon (BLC) Focus.txt:391-394`); until round 15 it borrowed Black
  Canyon's `generic_21` as well. The icon needs only a declared sprite (vanilla passes four
  unregistered ones, e.g. `norway.txt:3372-3375`);
  `common/intelligence_agencies/000_mltd_intelligence_agencies.txt` makes the same name and seal
  MLT's default when the agency is founded from the intelligence screen instead. Because an agency
  can be founded from that screen while the focus runs, *The Spreading Cult*'s founding line names
  both outcomes since round 28c's review (`mltd_spreading_cult_agency_tt`: the agency, or +50 PP if
  one exists by the time the focus completes; the 50 repeats the focus's `else`). With La
  Resistance but no agency yet, the helper pays +50 PP, as it does without the DLC; since round 28c
  that branch previews both outcomes (`mltd_intel_foothold_no_agency_tt`: +50 PP, or the upgrade if
  an agency is founded before the focus completes) over a hidden +50 PP.
- With La Resistance and an agency: one upgrade through OWB's `add_random_agency_upgrade`
  (`00_scripted_effects.txt:520`, fed `random_agency_upgrade_amount = 1`), with `caps_to_add` +
  `add_caps` paid *first* to refund the upgrade's caps price, so the balance never dips below zero
  mid-effect (Gotchas). At `agency_upgrade_number > 29`, OWB's own ceiling (`:540`), both are
  skipped and the helper falls through to its +50 PP `else`. The upgrade runs in `hidden_effect`
  behind `mltd_intel_foothold_upgrade_tt`, which since round 28c also names the ceiling's +50 PP
  (the founding tooltip is now *The Spreading Cult*'s `mltd_spreading_cult_agency_tt`). The +50 and
  the 30 repeat in both tooltips; change them together.
- Without the DLC: +50 PP.

Once an agency exists, the eleven heads therefore give up to eleven upgrades - fewer since
2026-09-23, because a head whose nation is gone is bypassed and gives none. The helper adds no
operative. Only `mltd_ces_what_the_river_carries` adds one, since it absorbed The Drowned
Frumentarius:

- it uses `create_operative_leader`, the same shape as `Caesars Legion (CES) Focus.txt:8101-8116`;
- it does so only with an agency: the call sits in
  `if = { limit = { has_intelligence_agency = yes } }`, and the `else` pays +50 PP. Since round
  28c's review that `else` is `mltd_ces_frumentarius_no_agency_tt` over a hidden +50 PP, which
  names both outcomes (the 50, or the operative offered for recruitment if an agency is founded
  before the focus completes), the shape of the helper's no-agency branch.

*Cult shelters.* Each spying head sets the country flag `mltd_cult_sheltered` on those of its
targets that exist. The flag halves cult decay there (round 17; tooltips
`mltd_<key>_cult_sheltered_tt`). The targets are:

- the Brotherhood that holds Washington;
- BRK; BDT;
- NCR and MOT; CES; BOS; WHT and EHT; HEA;
- TBH and LNS; ATE; TLA, MAX, MOC, ZAP and ARM.

*The wars.* Eleven focuses declare war with `declare_war_on` and `annex_everything` (round 22;
until then each granted a war goal):

- The Tide-Wall: whichever Brotherhood holds Washington; its `will_lead_to_war_with` names both WBH
  and TCA;
- The Coast Goes Under (round 28c): BRK;
- Drown the Dance: BDT;
- The Turbines Sing: NCR;
- The Sea Against Mars: CES;
- Blood in the Water: BOS;
- the Rites: WHT and EHT;
- the Crusade: HEA;
- Black Water Rising: TBH and LNS;
- The Serpent Drowns: ATE;
- The Drowned God Sleeps: TLA, MAX, MOC and ZAP.

Each declares on every living target that is neither at war with MLT nor its subject - Act III's
three, nor in its faction (Drown the Dance since round 28c) - and names its targets in
`will_lead_to_war_with`, which warns the target's AI while the focus runs. The focus's own length
is the run-up. Since 2026-09-24 every one of them, against a target that is not MLT's subject (Act
III's three: nor its ally), whether it declared the war or one already runs, grants:

- a 180-day idea whose `targeted_modifier` blocks give +10 % attack and +10 % defence against each
  of its targets - the seven old capstone ideas (`mltd_wbh_tide_wall`, whose +5 % attack became +10
  %, `mltd_ces_the_drowned_bull`, `mltd_bos_red_tide`, which until then came only on Blood in the
  Water's war branch, `mltd_wht_rites_on_the_jetty`, `mltd_hea_pilgrims_of_the_steam`,
  `mltd_tex_black_water`, `mltd_tla_dreams_of_wire`) beside their own modifiers, and for the other
  four a targeted idea of their own (`mltd_brk_the_raiders_hunted`, `mltd_bdt_the_dance_drowned`,
  `mltd_ncr_the_turbines_silenced`, `mltd_ate_the_serpent_hunted`);
- The First Wave, `mltd_the_first_wave`, 60 days of +10 % division recovery rate and +5 %
  breakthrough - the immediate buff the user asked for, a percentage so that it matters in 2285 as
  in 2278;
- with the target MLT's subject instead, +50 political power (The Tide-Wall: 30 army experience).

They replace the targets' stability and war-support losses, of little consequence, and the flat
payouts beside them (army experience, caps). A targeted modifier works in an idea, not in a dynamic
modifier (vanilla `aat_dynamic_modifiers.txt:751`), hence ideas; several targets are several blocks
(vanilla `ENG_tackle_fascism_idea_1`). The 0.10s are literals in each idea and nowhere else: the
preview draws them. Whether a second war focus inside The First Wave's 60 days restarts its timer
is unverified.

*The AI.* Each war focus is **unavailable** to an AI while its war would come too early. The hold
is a scripted trigger in the focus's own `available`, `mltd_ai_may_*` (`mltd_ai_triggers.txt`,
section W): a `hidden_trigger` whose `if = { limit = { is_ai = yes ... } }` a human always passes -
the idiom of the claim focuses' `mltd_ai_may_press_claims`. Each holds only while the focus would
start a war: with every target gone, already at war with MLT or its subject, the focus is a payout
and nothing waits. Until the round-27 review the holds were `ai_will_do` modifiers reading 0, and
that is not a hold: an AI takes every entry of its plan's `ai_national_focuses` that is available,
whatever its `ai_will_do` reads. Run 8 (`ai_runs/20260918-170847`, round-24 code) completed The
Tide-Wall on day 1715 with Washington's stage closed and The Turbines Sing on day 2513 with the
NCR's never open. Its two Muttfruit FOCUS lines are no evidence either way: both trades were
bypassed - by owning 186, and 493 and 450 - and a bypassed focus reads as completed, so whether a
`focus_factors` zero holds a focus is still untested. Terms for the Citadel (round 28) declares no
war, but it has a hold too, because a refusal hands MLT a war goal that OWB's AI would use at once.

Every hold also waits while MLT is losing a war (surrender progress over 15 %, the line of
`mltd_ai_may_press_claims`), and lifts as soon as it is not, so it strands no act. The optional
wars - those whose act's close also opens through a sibling - wait for a safe target as well
(`mltd_ai_safe_target`, or `mltd_ai_safe_by_strength` for the courted Bone Dancers), as the
conquest blocks for the same targets demand, because a focus's own declaration skips that check.
The Tide-Wall and Drown the Dance are an AI's usual ways through Act III, so their safe-target test
gives way on 1 January 2281, the date The Tide Turns South's own size gate gives way - since round
28c's review only while no Act III focus is done (`mltd_ai_act3_path_taken`), because any one of
the six opens The Deep Ones Walk (the close until 2026-09-24), and after that the escape could only
send an AI to war on a stronger country or, through the refusal holds that reuse these triggers,
release a refused invitation's war goal on one. Terms for the Citadel's hold gives way on the same
terms; The Coast Goes Under keeps its test with no date. The escape matters more since 2026-09-24:
an AI that has taken none of the six has not reached The Deep Ones Walk, and so The Final Ritual,
either. The Turbines Sing, The Sea Against Mars and Black Water Rising, whose closes need their
wars, wait on no safe target.

- The Tide-Wall, through `mltd_ai_may_raise_the_tide_wall`: unavailable to an AI while
  `mltd_ai_stage_wbh` or `mltd_ai_army_ready` fails, MLT is losing, or a Brotherhood it would
  declare on is not a safe target (from 2281 only while no Act III focus is done,
  `mltd_ai_act3_path_taken`) - only while a Brotherhood stands at peace with MLT and is not its
  subject
- Terms for the Citadel (round 28; no war of its own), through `mltd_ai_may_offer_the_citadel`:
  unavailable to an AI while historical focuses are on (the answer would be no);
  `mltd_ai_courting_brk` holds (an acceptance would close the Covenant, which the NCR's stage
  counts on through `mltd_ai_brk_helped`); the Brotherhood to be asked is not WBH itself (the
  Northwestern one accepts a tenth of the time, and since round 28b taking Terms forfeits The
  Tide-Wall whatever the answer); `mltd_ai_stage_wbh` or readiness fails; MLT is losing; or the
  Brotherhood is not a safe target (from 2281 only while no Act III focus is done) - everything The
  Tide-Wall's war would wait for. Only while a Brotherhood can be asked
- Drown the Dance, through `mltd_ai_may_drown_the_dance`: unavailable to an AI while the army is
  not ready or MLT is losing; before 2281, `mltd_ai_courting_bdt` holds; the Bone Dancers fail
  `mltd_ai_safe_by_strength` (from 2281 only while no Act III focus is done); or MLT is at war with
  an NCR that has not capitulated - only while BDT exists, is at peace with MLT and is not its
  subject. Since the round-27 review `mltd_ai_network_bdt` and `mltd_ai_infiltrate_bdt` build the
  Bone Dancers' network and take their civilian token; since round 28c's balance review Hail the
  Drowned King's gates no longer rest on the Bone Dancers' own tree either, so an AI that courts
  them can reach it. From 2281 the war stops waiting for them
- The Coast Goes Under (round 28c), through `mltd_ai_may_drown_the_coast`: unavailable to an AI
  while `mltd_ai_courting_brk` holds (no date: the courtship is on purpose - run 3's AI declared on
  the 47-state Broken Coast and lost); the army is not ready; MLT is losing; BRK fails
  `mltd_ai_safe_target`; or MLT is at war with an NCR that has not capitulated - only while BRK
  exists, is at peace with MLT and is not its subject. No 2281 escape: the Walk has five other
  paths
- The Turbines Sing, through `mltd_ai_may_start_ncr_war`: unavailable to an AI while
  `mltd_ai_stage_ncr` or readiness fails, or MLT is losing - lifted once MLT is at war with the
  NCR, the NCR is gone or MLT's subject, or it has capitulated to MLT (`mltd_ncr_capitulated`),
  because the close needs the focus and an AI must not be held off it after the war. A capitulation
  to anyone else does not lift it
- The Serpent Drowns, through `mltd_ai_may_start_ate_war`: unavailable to an AI while
  `mltd_ai_stage_ate` or readiness fails, or MLT is losing; also while ATE fails
  `mltd_ai_safe_target` (its declaration skips that check), or while an uncapitulated Texan tag is
  at war with MLT
- The Sea Against Mars, Black Water Rising, through `mltd_ai_may_start_<ces|texas>_war`:
  unavailable to an AI while readiness fails, or MLT is losing - nothing else: their closes wait on
  them
- Blood in the Water, the Rites, the Crusade, The Drowned God Sleeps, through
  `mltd_ai_may_start_<bos|utah|hea|tla>_war`: unavailable to an AI while readiness fails, MLT is
  losing, or a target it would declare on is not a safe target

Act V's four wars and Act VI's Black Water and Drowned God dropped their old stage terms
(`mltd_ai_ncr_beaten`, `mltd_ai_legion_beaten`). Those terms only repeated what the chapter already
requires, and once a beaten rump outlived the peace they could only strand an AI. The round-23
`is_ai` modifiers that made a head wait for an earlier stage are gone as well: the tree now
enforces the order.

The plans' order:

- The Kingdom-and-Books plan takes Act II's Broken Coast branch right after The Grand Ritual and
  OWB's claim focuses (after the Walk until 2026-09-24), then Act III - the invitations first, each
  after the Act II branch it hangs off: the Covenant; The Bone Shore, The Dancers Hear the Tide and
  Hail the Drowned King; Eyes in the Sound, The Drowned Knights and Terms for the Citadel; then
  Drown the Dance, The Tide-Wall and The Coast Goes Under. The Deep Ones Walk and The Final Ritual
  are listed between Sail North and the Covenant, so each is taken the day it opens - the Walk once
  one of the six is done, the ritual once the Walk is and its 200,000 people are there (since
  2026-09-24; until then this plan took the Walk after The Grand Ritual, and the ritual after the
  Broken Coast's branch and the other two Act II branches while it waited).
- The late plan lists the acts in order:
  - Act III's close, The Tide Turns South, then Act IV's chapter and one bead (the Sleepers);
  - what the north has left, the invitations first, so that taking one forfeits only its own war
    twin: the Broken Coast's Act II pair and the Covenant; The Bone Shore, The Dancers Hear the
    Tide and Hail the Drowned King; Eyes in the Sound, The Drowned Knights and Terms for the
    Citadel - ahead of The Turbines Sing, because the Covenant is one way to the help the NCR's
    stage waits on;
  - The Turbines Sing, Act IV's other two beads while it is held, then the north's three wars -
    Drown the Dance, The Tide-Wall and, last, The Coast Goes Under (round 28c) - the north's two
    spoils, and Act IV's close;
  - the claim focuses;
  - Act V's chapter and its four branches, head then war, California's four spoils, the close; Act
    VI's chapter, Texas, Tlaloc, then Nuevo Aztlán, the interior's two spoils, the close;
  - R'lyeh Rises and The Dreamer Wakes, with the other two endings as fallbacks, then the south's
    two spoils. Until 2026-09-24 Act II's Washington bead, The Drowned Knights, came last, for the
    long waits while a great war held the next chapter shut; since then Terms for the Citadel needs
    it, so it sits with the north.
- The spoils (round 28; groups since round 28c) are each listed after the *next* act's war focuses
  and before that act's close, one-offs first and the idea focuses last, so an AI works a group
  while the close waits on its war, or while a war focus is held, and never ahead of the war:
  listed before the next chapter, it would put that war off by the group's length. The south's,
  whose act has no successor, comes after the ending.
- Eyes in the Sound moved up into Act III in round 28, because Terms needed it done, and at the
  bottom of the list it would have waited behind every filler; since 2026-09-24 Terms hangs off The
  Drowned Knights, and both plans list Washington's Act II branch just before it.
- In practice an AI takes The Coast Goes Under only as a payout in a war the raiders already fight
  with MLT: a refused Covenant has excluded it, and the AI offers Terms, whose acceptance would end
  the courtship, only once the courtship is over. `CONQUEST_PLAN.txt`, which never takes the twin,
  carries the `# AI deviation:` line.
- No story focus rests on a `focus_factors` zero, whose effect is untested: each chapter waits for
  the previous close, and each war holds itself in `available`.

Settled by run 8: the engine does **not** skip a listed focus whose `ai_will_do` reads 0, which is
why the holds are in `available`.

*Shared keys.*

- **Doubled amounts.** Caps, equipment, stability and army-XP amounts were doubled on 2026-09-14,
  both what MLT gains and what it inflicts, and every theft guard with them, so a guard still
  demands at least what is taken. A guard N where N+1 is a multiple of 50 became 2(N+1)-1 (399 ->
  799); any other guard became 2N (600 -> 1200).
- **Left alone.** Political power, war support, intel, population, tech bonuses, the timed ideas
  and Black Water Rising's +3 energy (gone since round 28b) were not doubled.
- **Rescaled** (round 28b, the house rule *Rewards scale to when they are taken*). The flat thefts
  of Acts IV-VI became shares of the victim's store, paid in mirelurks since round 28c (*Theft
  without producer*); `mltd.51`'s two options became ideas; Black Water Rising lost its flat
  energy, and Return to the Sea's recruitable population became a creature build-cost cut. Act II's
  and III's rewards, sized for their time, stayed.
- **Cost.** A focus's cost is its length in days (OWB sets `FOCUS_POINT_DAYS = 1`,
  `common/defines/01_defines.lua:468`), and since 2026-09-25 every focus of ours takes 7, 30, 60,
  120 or 180 (Project > *Focus lengths*).

*The DLC idiom* (OWB Lost Hills, `Lost Hills (BOS) Focus.txt:9641-9651`).

- **In `available`.** Only the three invitations test intel there (*Never strand*). They do it
  inside `if = { limit = { has_dlc = "La Resistance" } ... }` with **no `else`**, so without the
  DLC their intel lines simply do not apply. Each is the same set of three lines, all of which must
  pass - the invitee's cult, `has_operation_token = { tag = X token = token_civilian }` and
  `network_national_coverage = { target = X value > 0.25 }` on the 0-1 scale. Terms for the Citadel
  writes the set once per tag, WBH then TCA, inside one `custom_trigger_tooltip`
  (`mltd_wbh_terms_faithful_tt`), because which Brotherhood is asked is only settled at completion
  \- the house idiom for that pair, as The Drowned Knights and The Tide-Wall use it. Until round
  28c's balance review the Covenant also tested `intel_level_over` and its own higher cult and
  coverage numbers; until round 27, each middle focus instead tested an OR of one token and one
  coverage threshold.
- **Tokens.** They come from OWB's own `operation_infiltrate_civilian` /
  `operation_infiltrate_armed_forces_army` (awarded at `00_operations.txt:162` / `:600`), or from a
  focus through `add_operation_token` (Lost Hills precedent `:1830-1845`). Many heads and beads
  hand out a `token_army`, which now only opens OWB's own operations (Gotchas). The invitations
  test `token_civilian`, which only OWB's infiltration and *Hail M'lyeh* hand out.
- **In `completion_reward`.** `add_intel`, `add_operation_token`, `steal_random_tech_bonus` and
  `create_operative_leader` sit in
  `if = { limit = { has_dlc = "La Resistance" country_exists = X } ... }` with an
  `else = { <PP or add_tech_bonus> }`. Equipment theft, PP / stability / war-support hits on the
  target, caps, population and ideas need no agency, and sit outside that `if`.

*Theft without producer.* Every theft removes the equipment from the victim with
`add_equipment_to_stockpile` and a negative amount with **no `producer`**, which takes it from
every maker in its stockpile (`effects_documentation.md:1262-1263`); a `producer = <victim>` on the
removal would take nothing from stock someone else built. What MLT gains depends on the act:

- **Act II** (The Drowned Knights, The Dancers Hear the Tide): a flat lot, sized for its time. ROOT
  gains the same amount with `producer = <victim>` - OWB's `operation_steal_enemy_supplies` idiom
  (`operations_fallout.txt:45-63`) - guarded by `<victim> = { has_equipment = { X > N } }` at or
  above the amount taken; that trigger counts every maker, matching the removal. Since round 28b
  each is a custom tooltip over the hidden pair (`mltd_wbh_knights_theft_tt`,
  `mltd_bdt_bone_road_theft_tt`), because a preview taken before the victim's store qualifies would
  show nothing.
- **Acts IV-VI** (round 28b; paid in mirelurks since round 28c): a share of the victim's store - a
  fifth (Salt on the Caravan Roads) or a quarter (every Act V and VI war; The Turbines Sing's rout
  took a tenth until 2026-09-24) - read with `<TAG>.num_equipment@<type>` into a temp variable,
  rounded, and moved with `amount = <variable>`; each store is guarded at 100. The haul is paid as
  one mirelurk - the archetype `amphibious_beast_equipment`, MLT's best unlocked breed - for every
  five pieces taken (and one per suit of power armour in Blood in the Water), about their worth in
  IC; rifles are no use to the creature army the plan fields from Act V on, and any factory makes
  them, while every creature line draws water, and slows when it runs short. The preview prints the
  live share and the mirelurks from the same temp variables; the transfers are hidden.
- **No floors** since 2026-09-24. From round 28c's review a theft's old fallback was paid whenever
  the haul was worth less than it (100 caps under 125 mirelurks, a point of political power or army
  experience for a mirelurk); the war focuses' thefts now sit beside their idea and The First Wave,
  one line each, and pay what they take.

*Numbers in two places.* Some effects are hidden behind a literal tooltip. This happens where OWB's
tooltip for an effect would read a variable the focus preview cannot see, would print every theft
twice, where two calls make one number, or where the effect's limit may not hold yet when the
preview is read (round 28b's rule, Project > *Every effect shows before it is taken*):

- Tlaloc's 64 databanks and the test above 100: `mltd_tla_drain_databanks_tt`.
- The Deep Ones Sail North's +6 volunteer divisions, which are two calls of +3:
  `mltd_brk_volunteer_size_6_tt` (*The Broken Coast's volunteers*).
- The two Leviathans of Return to the Sea: two `mltd_spawn_leviathan` calls, and the prose of
  `mltd_return_to_the_sea_leviathans_tt`.
- Act II's thefts (round 28b): The Drowned Knights' infantry equipment and power armour and their
  guards, `mltd_wbh_knights_theft_tt`; The Dancers Hear the Tide's infantry equipment, guard and
  +25 PP fallback, `mltd_bdt_bone_road_theft_tt`.
- The Tide-Wall's bunker levels and The Warren's four provinces (round 28b):
  `mltd_wbh_tide_wall_bunkers_tt`.
- The late thefts (rounds 28b-28c; one line each, no floor, since 2026-09-24): each share, the one
  mirelurk per five pieces and the guard of 100 - `mltd_ncr_caravan_theft_tt` (a fifth);
  `mltd_ces_crates_theft_tt` (a quarter); `mltd_bos_armoury_theft_tt` (a quarter, and one mirelurk
  a suit); `mltd_wht_sand_theft_tt`, `mltd_hea_steam_theft_tt` and `mltd_tex_wreckers_theft_tt` (a
  quarter of the rifles); `mltd_tla_iron_bones_theft_tt` (The Drowned God Sleeps' quarters).
- Guns for Both Sides' 200 rifles, 100 caps and guard on MLT's own rifles (`> 199`, written "at
  least 200"): `mltd_wht_guns_sale_tt`.
- The +50 political power fallbacks previewed as a condition (round 28c's review): *The Spreading
  Cult*'s, in `mltd_spreading_cult_agency_tt`; What the River Carries', in
  `mltd_ces_frumentarius_no_agency_tt`; The Foundries Relit's, in the `effect_tooltip` under
  `mltd_spoils_foundries_bonus_else_tt`. Each repeats its focus's `else`. (The three invitations'
  fallbacks had their own `_fallback_tt` lines from round 28c's review to 2026-09-23; since then
  the preview draws the native `else` when it is the branch that holds.)
- The three events a focus previews (round 28b): the Drowned Herald's general role, skill and
  traits in both options of `mltd.1` and in the Kingdom's `effect_tooltip`; `mltd.7`'s army
  experience in its option and in the Call's; `mltd.8`'s option and the Walk's (the override).

Change the script and the loc together. Several other literals are repeated in the same way:

- the size gates' 50 and 300 states, and `mltd.40`'s options in When Shady Sands Falls' preview
  (above). `mltd.51`'s numbers are no longer repeated: its close previews the options' scripted
  effects, so they live in `mltd_the_unchained`, `mltd_the_pens_emptied` and the 730 days of
  `mltd_legion_pens_fed`, which "two years" repeats in `mltd_the_pens_emptied_desc` and
  `mltd.51.d`;
- the invitations' thresholds, one set of numbers since round 28c's balance review (40 % and 25 %):
  `mltd_brk_strong_cult_tt` and `mltd_brk_network_tt`, `mltd_bdt_strong_cult_tt` and
  `mltd_bdt_network_tt`, and `mltd_wbh_terms_faithful_tt`, which carries both of Terms' in one
  line. The review deleted `mltd_brk_intel_tt` and `mltd_brk_pirate_coast_tt` with the gates they
  printed;
- the invitations' odds (round 28): the `ai_chance` of `mltd.21`, `mltd.24` and `mltd.32` against
  the lines `GetMltdBrkOdds`, `GetMltdBdtOdds` and `GetMltdWbhOdds` print (`mltd_brk_odds_*`,
  `mltd_bdt_odds`, `mltd_wbh_odds_*`); and the Washington-first rule of `mltd_wbh_terms_target`
  against `GetMltdWbhOdds`'s branches;
- the refusals' year: `expire = 365` in the refusing options of `mltd.21`, `mltd.24` and `mltd.32`
  against `mltd_refusal_wargoal_expires_tt`, and as "a year" in `mltd_invitation_if_refused_tt` and
  `mltd_wbh_terms_if_refused_tt`, as "a year" in `mltd.23.d` and `mltd.26.d`, and as "within the
  year" in `mltd.34.d`;
- the Covenant's +75 lives in `mltd_drowned_covenant` (`mltd_opinion_modifiers.txt`) alone since
  2026-09-24, when the invitations' tooltips stopped quoting it;
- the spoils' 80 / 120 / 180 / 250 controlled states against `mltd_spoils_sound_states_tt`,
  `mltd_spoils_harvest_states_tt`, `mltd_spoils_tithe_states_tt` and
  `mltd_spoils_salt_road_states_tt`; each one-off's figure against its tooltip - the compliance and
  resistance in `mltd_spoils_scribes_compliance_tt`, `mltd_spoils_canals_compliance_tt` and
  `mltd_spoils_armouries_resistance_tt`, the slots and factories in
  `mltd_spoils_cascades_works_tt`, `mltd_spoils_foundries_works_tt` and
  `mltd_spoils_forges_works_tt`, the mirelurks per state and the Gulf ports in
  `mltd_spoils_canals_hatch_tt` and `mltd_spoils_gulf_hatch_tt`; and the state ids each spoils
  focus asks for or acts on against the states its description names (the Office of Salt and
  Industry's The Hub and Sac-City included). The ideas' modifiers and the timed ideas' days are
  drawn by the engine.

*Per act.* Each focus below has its gate, besides its prerequisites, and its payoff. Conventions:

- "LaR" marks a condition or reward that applies only with La Resistance.
- "else" is the no-DLC or target-gone substitute.
- "civ/army N" is `add_intel`, and "cov" is `network_national_coverage`.
- "foothold" is `mltd_intel_foothold`, and "shelters" sets `mltd_cult_sheltered`.
- "alive" means the target exists; when it does not, the focus pays the fallback named. Since
  2026-09-23 a focus whose every target is gone is bypassed (*Never strand* > *Bypass*), so the
  fallback is paid only for a target that is MLT's subject or dies while the focus runs.
- Every war focus's `available` also holds an AI through its `mltd_ai_may_*` trigger (*The AI*,
  above); the list shows only what a human sees.

**Act II - The Northern Waters** (`mltd_act2_focus.txt`), under The Grand Ritual since 2026-09-24
(The Deep Ones Walk before); each bead leads on to its nation's Act III pair

- `mltd_wbh_eyes_in_the_sound`
  - Gate: none (since round 27 it needs no Brotherhood in Washington)
  - Payoff: foothold; shelters the cults of whichever Brotherhood holds Washington
    (`mltd_wbh_brotherhood`); LaR with a Brotherhood: civ 10 / army 15 on it, else +25 PP
- `mltd_wbh_the_drowned_knights`
  - Gate: none
  - Payoff: from Heresy in the Citadel: each Brotherhood -40 PP, -6 % stability; LaR with a
    Brotherhood: civ 15 + `token_army` on it, else +25 PP; steals 600 infantry equipment (> 1,200)
    and 60 power armour (> 120) from whichever holds them; 30 army XP. Since round 28c's review
    none of it touches a Brotherhood in MLT's faction (an accepted Terms for the Citadel) or its
    subject: the +25 PP pays instead, and `mltd_wbh_knights_theft_tt` says so
- `mltd_brk_salt_on_the_broken_coast`
  - Gate: none
  - Payoff: foothold. BRK alive: shelters its cult, then adds +10 to it, founding it if needed
    (from The Drowned Raiders); lifts OWB's `world_view_brk` / `brk_view_world` between MLT and BRK
    and adds `mltd_drowned_envoys` both ways. LaR and BRK: civ 25 / army 10 + `token_army`, else
    +50 PP
- `mltd_brk_the_deep_ones_sail_north`
  - Gate: no war with BRK while it exists
  - Payoff: BRK alive: +6 volunteer divisions (`mltd_brk_add_volunteer_size` twice; the second call
    came from Star Spawn over the Strait), else +50 PP
- `mltd_bdt_the_bone_shore`
  - Gate: none
  - Payoff: foothold; BDT alive: shelters its cult, `mltd_drowned_envoys` both ways; LaR and BDT:
    civ/army 10, else +25 PP
- `mltd_bdt_the_dancers_hear_the_tide`
  - Gate: none
  - Payoff: +10 to BDT's cult, founding it if needed; LaR and BDT: civ 15 + `token_army`, else +25
    PP; from Salt on the Bone Road: steals 600 infantry equipment (BDT > 1,200), else +25 PP; 30
    army XP. Since round 28c's review the intel, token and theft skip Bone Dancers in MLT's faction
    (an accepted Hail the Drowned King) or its subject, and the +25 PPs pay instead

**Act III - The Stars Are Right** (`mltd_act3_focus.txt`), since 2026-09-24 under the Act II beads
and before The Deep Ones Walk and The Final Ritual (after the ritual until then): three pairs, each
**mutually exclusive both ways**, each under its nation's bead

- `mltd_wbh_terms_for_the_citadel` (round 28), x 10; excludes The Tide-Wall
  - Gate: its prerequisite, The Drowned Knights (since 2026-09-24; until then Eyes in the Sound
    done, in `available`). A Brotherhood passes `mltd_wbh_terms_target`
    (`mltd_wbh_terms_brotherhood_tt`: WBH unless it is gone or someone's subject, else TCA as the
    Northwestern Brotherhood; at peace with MLT, no one's subject, and in no faction or leading its
    own - since 2026-09-25; until then in no faction, which WBH never is while the Northern League
    it founds in 2275 stands, Gotchas > *OWB's Brotherhood leads the Northern League*); MLT in no
    faction or leading one; the Broken Coast has not joined the Covenant
    (`mltd_brk_covenant_joined`, `mltd_wbh_terms_no_covenant_tt`), which is this invitation's rival
    gate. LaR, since round 28c's balance review: the common set against whichever Brotherhood would
    be asked - its cult at 40 %, `token_civilian`, cov > 0.25 - written one branch per tag, WBH
    then TCA, behind `mltd_wbh_terms_faithful_tt`; until then Terms asked for no intelligence at
    all
  - Payoff: the offer, then "If it accepts:" over the faction founded and the Brotherhood joining
    (native lines), its claims dropped (`mltd_wbh_terms_claims_tt`) and, while it leads a faction,
    that faction's other members coming too (`mltd_wbh_terms_faction_wbh_tt` / `_tca_tt`, which
    name the faction; since 2026-09-25), and "If it refuses:" over the war goal (since 2026-09-24);
    then event `mltd.32` to that Brotherhood - the reward re-tests the Brotherhood, MLT's faction
    and the Covenant flag first. Accept: `mltd_wbh_join_the_covenant` - MLT founds or leads the
    Drowned Covenant; if the Brotherhood leads a faction, every other member at peace with MLT and
    its allies leaves it and joins the Covenant, with its +75 both ways (since 2026-09-25, *The
    invitations*); the Brotherhood joins and drops every claim it holds on MLT's land,
    `mltd_drowned_covenant` +75 both ways, flag `mltd_wbh_alliance` (which closes the Covenant) -
    and `mltd.33`. Refuse: an `annex_everything` war goal on the Brotherhood that expires after 365
    days, flag `mltd_wbh_refused_terms` (read since round 28b only by MLT's AI), and `mltd.34`.
    Either way The Tide-Wall is closed. A historical AI Brotherhood always refuses; unhistorical,
    WBH accepts half the time and TCA a tenth. With no Brotherhood left to ask, or the Covenant or
    a faction in the way by the time it completes: +50 PP, which since 2026-09-25 the preview shows
    only while the focus runs and the offer can no longer go (from round 28c's review to 2026-09-23
    beside the offer under `mltd_wbh_terms_fallback_tt`, and on 2026-09-24 whenever no Brotherhood
    could be asked, which hid the offer)
- `mltd_wbh_the_tide_wall` "The Tide-Wall of the Warren", x 12; excludes Terms
  - Gate: the Brotherhood has `WBH_eradicate_the_mutants` (OWB's shared Brotherhood tree, which TCA
    also flies), is at war with MLT or none is left, or after 2280.1.1; **and** MLT owns and
    controls The Warren (235). Round 28's gate on `mltd_wbh_alliance` went in round 28b: only Terms
    can set that flag, and Terms now excludes the wall
  - Payoff: declares war on each living Brotherhood that is not MLT's subject or in its faction,
    one block per tag, WBH then TCA (`will_lead_to_war_with` names both); the bunkers in 235 while
    it is still MLT's (level 2 in province 2158, level 1 in 2159-2161;
    `mltd_wbh_tide_wall_bunkers_tt` over the hidden build); while a Brotherhood lives, WBH's and
    TCA's claims on 235 are removed (`mltd_wbh_tide_wall_claims_tt`); against one that is not MLT's
    subject or ally: `mltd_wbh_tide_wall` (core defence, +10 % attack and defence against both
    Brotherhoods) and The First Wave, since 2026-09-24 in place of each Brotherhood's -3 % war
    support; else 30 army XP. Round 28's no-bonus branch after a refused Terms went with the
    exclusion
- `mltd_brk_the_drowned_covenant`, x 14; excludes The Coast Goes Under
  - Gate: its prerequisite, The Deep Ones Sail North (since 2026-09-24; until then Salt on the
    Broken Coast done, in `available`). While BRK lives and is not MLT's subject: at peace with
    MLT, no subject and in no faction; MLT in no faction or leading one; since round 28 no alliance
    with the Brotherhood in Washington (`mltd_wbh_alliance`, `mltd_brk_no_brotherhood_table_tt`),
    this invitation's rival gate. LaR: BRK's cult at 40 %, `token_civilian`, cov > 0.25. Round
    28c's balance review cut the tree's two heaviest gates - `brk_nf_pirate_coast`'s VIC and DRE
    coast, which rests on the raiders' own conquests, and civilian intel over 50 % - and brought
    the cult and coverage down from 50 % and 30 % to the set all three invitations share
  - Payoff: the invitation, then "If they accept:" over the faction founded and BRK joining and "If
    they refuse:" over the war goal, native lines under two headers
    (`mltd_invitation_if_accepted_tt` / `_refused_tt`, since 2026-09-24); then event `mltd.21` to
    BRK - the reward re-tests BRK, MLT's faction and the alliance first, else +50 PP. Accept
    (offered only while BRK can still join): MLT founds the Drowned Covenant if it leads no faction
    (`create_faction_from_template`, `create_faction` without No Compromise, No Surrender), BRK
    joins, `mltd_drowned_covenant` +75 both ways and, since round 28, flag
    `mltd_brk_covenant_joined`, which closes Terms for the Citadel (`mltd_brk_join_the_covenant`;
    the Covenant's tooltip said so until 2026-09-24, Terms' own gate says so still), and `mltd.22`.
    Refuse: MLT -25 of BRK (`mltd_drowned_covenant_refused`, decaying), global flag
    `mltd_brk_refused_covenant`, since round 28 an `annex_everything` war goal on BRK that expires
    after 365 days - since round 28c the tree's one road to war with the raiders once the Covenant
    is taken - and `mltd.23`. A historical AI BRK always accepts; an unhistorical one half the time
    (round 28; until then always). BRK gone or MLT's subject: +50 PP, previewed then and, since
    2026-09-25, while the focus runs and the offer can no longer go (on 2026-09-24 whenever the
    offer could not go, the raiders in a faction or at war included); paying it sets
    `mltd_brk_covenant_lapsed`, which ends the AI's courtship of the raiders (round 28c's review)
- `mltd_brk_the_coast_goes_under` "The Coast Goes Under" (round 28c), x 16; excludes the Covenant
  - Gate: while BRK lives and is not MLT's subject: not in MLT's faction
  - Payoff: BRK alive and not MLT's subject or ally: declares war (`annex_everything`;
    `will_lead_to_war_with = BRK`); `mltd_brk_the_raiders_hunted` (180 days, +10 % attack and
    defence against BRK) and The First Wave (until 2026-09-24: BRK -6 % stability, -3 % war
    support, 40 army XP, and no idea). Else +50 PP. Sized like Drown the Dance, and since
    2026-09-25 half as long as the Covenant (as long as it until then). The Broken Coast is courted
    first and fought only by choice: a human has two roads to that war, this focus or a refused
    Covenant's war goal
- `mltd_bdt_hail_the_drowned_king`, x 18; excludes Drown the Dance
  - Gate: its prerequisite, The Dancers Hear the Tide (since 2026-09-24; until then The Bone Shore
    done, in `available`). BDT exists, is at peace with MLT, is no subject and in no faction; MLT
    in no faction or leading one; the rival gate (round 28c's balance review,
    `mltd_bdt_not_pilgrims_tt`): BDT has not taken `bdt_listen_to_the_pilgrims`, one of the three
    exclusive roads of OWB's Bone Dancers tree, which swears them to Heaven's Guard's seraph lords,
    and MLT is not in a faction with HEA. It replaced round 22's demand that they had already
    crowned OWB's Odious King (`bdt_hail_to_the_king`), which an AI BDT takes only on its own roll.
    LaR: BDT's cult at 40 %, `token_civilian`, cov > 0.25
  - Payoff: the invitation, "If they accept:" and "If they refuse:" over native lines, as the
    Covenant's (since 2026-09-24), then event `mltd.24` to BDT - since round 28c's review the
    reward re-tests BDT and MLT's faction first, else +50 PP: the Broken Coast's invitation again
    (`mltd_bdt_join_the_covenant`, with the same faction and opinion modifiers; it sets no
    exclusivity flag, so the Bone Dancers can sit beside the raiders or the Brotherhood). A refusal
    sets `mltd_bdt_refused_covenant`, since round 28 gives MLT an `annex_everything` war goal on
    BDT that expires after 365 days, and fires `mltd.26`. An AI BDT always accepts, under either
    rule. The +50 PP fallback shows in the preview only while the focus runs and the offer can no
    longer go (since 2026-09-25), and sets `mltd_bdt_covenant_lapsed`, which ends the AI's
    courtship (round 28c's review)
- `mltd_bdt_drown_the_dance`, x 20; excludes Hail
  - Gate: while BDT lives and is not MLT's subject: not in MLT's faction
  - Payoff: BDT alive and not MLT's subject or (since round 28c) ally: declares war
    (`annex_everything`); `mltd_bdt_the_dance_drowned` (180 days, +10 % attack and defence against
    BDT) and The First Wave (until 2026-09-24: BDT -6 % stability, -3 % war support, 40 army XP).
    Else +50 PP. Two-way since round 28b; from round 24 to round 28 Hail named this focus but this
    one did not name Hail (*Exclusions*, above)
- `mltd_the_deep_ones_walk` (national; since 2026-09-24 between the fan and the ritual)
  - Gate: any one of the six (one OR block) and all five Books
  - Payoff: Beat 4 (Project)
- `mltd_the_final_ritual` (national; since 2026-09-24 between the Walk and the close)
  - Gate: The Deep Ones Walk and 200,000 people
  - Payoff: Beat 5 (Project)
- `mltd_the_tide_turns_south` (close)
  - Gate: The Final Ritual (since 2026-09-24; until then any one of the six, one OR block); 50
    controlled states, or from 2281
  - Payoff: a research slot, MLT's fourth (round 28c's balance review moved it here from The Last
    King Kneels, so the NCR's war is fought on four); permanent idea `mltd_the_northern_waters`
    (stability, war support, justification time); event `mltd.30` (two options, no effects), news
    `mltd.31`

**Act IV - The Drowned Republic** (`mltd_act4_focus.txt`): `NCR` (+ `MOT`)

- `mltd_ncr_a_mole_in_shady_sands` (chapter)
  - Gate: none
  - Payoff: foothold; shelters the NCR's and MOT's cults; LaR and NCR: civ 10 / army 5, else +25 PP
- `mltd_ncr_drowned_delegates`
  - Gate: none
  - Payoff: +40 PP. NCR alive: NCR -35 PP, -6 % stability (until 2026-09-24 -4 % more under
    `ncr_crisis` or the global `ncr_emergency`, previewed as a condition). LaR and NCR:
    `token_army` + civ 10, else infantry-weapons tech bonus 50 %
- `mltd_ncr_sleepers_on_the_long_15`
  - Gate: none
  - Payoff: 30 army XP; MOT (else NCR) -3 % war support; LaR and NCR: army 10 on NCR and MOT, else
    +25 PP
- `mltd_ncr_salt_on_the_caravan_roads` (icon `GFX_goal_MOJ_ncr_trade` since round 28c)
  - Gate: none
  - Payoff: NCR alive: a fifth of its infantry and a fifth of its support equipment, each store
    guarded at 100, paid as one mirelurk per five pieces (rounds 28b-28c; it was 800, or 400,
    rifles and 200 support), else +25 PP; +100 caps either way
- `mltd_ncr_the_turbines_sing` (the war), after any one bead
  - Gate: Hoover contested: any first-battle outcome flag, CES has `ces_hoover_dam_battle` /
    `ces_attack_ncr`, NCR at war with CES, CES gone, or after 2279.06.01
  - Payoff: declares war on NCR; against an NCR that is not MLT's subject,
    `mltd_ncr_the_turbines_silenced` (180 days, +10 % attack and defence against it) and The First
    Wave (since 2026-09-24), else +50 PP. LaR: steals an industry tech bonus from NCR
    (`fallout_industry_folder`), else industry tech bonus 50 %. Until 2026-09-24 it also paid by
    the first Battle for Hoover Dam - after a Legion rout a tenth of the NCR's rifles as mirelurks,
    after a held wall 30 army XP, both previewed while the battle was undecided - and cost the NCR
    3 % war support while it fought the Legion
- `mltd_when_shady_sands_falls` (close)
  - Gate: the NCR beaten (`mltd_ncr_beaten_tt`)
  - Payoff: event `mltd.40`, a choice. Option a: a research slot (the AI's pick 3 times in 4).
    Option b: the permanent `mltd_the_drowned_rangers` (army attack, defence and organisation) and
    army experience. News `mltd.41`

**Act V - The Sea Against Mars** (`mltd_act5_focus.txt`): `CES`, `BOS` (+ `NCR`), `WHT` and `EHT`,
`HEA`

- `mltd_mars_in_the_water` (chapter)
  - Gate: none
  - Payoff: 30 army XP; event `mltd.50`
- `mltd_ces_what_the_river_carries`
  - Gate: none
  - Payoff: foothold; shelters CES's cult. LaR: with an agency, the operative *Silanus the Drowned*
    (`operative_frumentarius`, skill 2, nationalities MLT and CES), else +50 PP (previewed with
    both outcomes since round 28c's review, `mltd_ces_frumentarius_no_agency_tt`); and, with CES
    alive, `token_army` + civ 15 / army 10, else +25 PP. No DLC: +75 PP. CES -6 % stability
- `mltd_ces_the_sea_against_mars` (war)
  - Gate: none
  - Payoff: declares war on CES; against a Legion that is not MLT's subject,
    `mltd_ces_the_drowned_bull` (now with +10 % attack and defence against CES) and The First Wave
    (since 2026-09-24), and from A Crate for Every Cross a quarter of the Legion's infantry and
    support equipment (each guarded at 100), paid as one mirelurk per five pieces (it was 800 and
    200); else +50 PP. Until 2026-09-24 the crates had a floor of 100 caps under 125 mirelurks, and
    the focus paid by Caesar's health (dead or at civil war 40 army XP and CES -6 % stability, sick
    +150 caps and CES -3 % war support, hale +50 PP, all three previewed while it could change) and
    cost the Cult of Mars 2 % war support
- `mltd_bos_the_drowned_paladin`
  - Gate: none
  - Payoff: foothold; shelters BOS's cult. LaR and BOS: `token_army` + civ 15 / army 10, and steals
    an engineering/industry tech bonus from BOS; else +60 PP and an electronics tech bonus 75 %. 20
    army XP. BOS -35 PP, -4 % stability
- `mltd_bos_blood_in_the_water` (war)
  - Gate: none
  - Payoff: declares war on BOS; against a Lost Hills that is not MLT's subject,
    `mltd_bos_red_tide` (now with +10 % attack and defence against BOS, and with every war, where
    it came only on the quarrel's war branch) and The First Wave (since 2026-09-24), and from The
    Tide Takes the Armoury a quarter of the best of `energy_equipment_2` / `_1` / infantry that BOS
    holds 100 of, and a quarter of its power armour (guard 100), paid as one mirelurk per five
    weapons and one per suit (it was 600 and 80; the tiers are as OWB's
    `operations_bos.txt:307-404`); else +50 PP. Until 2026-09-24 the armoury had a floor of 100
    caps under 125 mirelurks, and the focus paid by Lost Hills' quarrel with the NCR (the war's -3
    % war support on both, the tension through OWB's `bos_change_tension`, the Maxson accords' -6 %
    stability), each previewed as a condition
- `mltd_wht_the_lake_god_answers`
  - Gate: none
  - Payoff: foothold; shelters WHT's and EHT's cults. From The Drowned Shamans: +40 PP; WHT -6 %
    stability (until 2026-09-24 also +4 % stability and +2 % war support if WHT had `wht_god_lake`
    or `wht_god_old`). LaR: `token_army` + civ 10 on WHT if alive (else an infantry-weapons tech
    bonus 50 %), and army 10 on EHT if alive. No DLC: +25 PP and infantry-weapons 50 %. From Guns
    for Both Sides: sells 200 of MLT's infantry equipment to each of WHT and EHT that is alive and
    not at war with MLT, for 100 caps from each, one line (`mltd_wht_guns_sale_tt`; until
    2026-09-24 also 80 caps if it could arm neither, and 30 army XP while WHT and EHT were at war)
- `mltd_wht_rites_on_the_spiral_jetty` (war)
  - Gate: WHT at war with EHT or has `wht_betray_eighties`, EHT has `EHT_steal_WHT_legs`, either
    gone, or after 2280.1.1
  - Payoff: declares war on WHT and EHT; against either that is not MLT's subject,
    `mltd_wht_rites_on_the_jetty` (now with +10 % attack and defence against both) and The First
    Wave (since 2026-09-24), and from Sand in the Engines a quarter of the Eighties' rifles (guard
    100), paid as one mirelurk per five (it was 600); else +50 PP. Until 2026-09-24 the rifles had
    a floor of +25 PP, EHT lost 3 % war support, and the White Legs' gods paid +50 PP and WHT -4 %
    stability (else +30 PP), both previewed until WHT had taken a god
- `mltd_hea_whispers_in_the_steam`
  - Gate: none
  - Payoff: foothold; shelters HEA's cult. From A Second Schism: +40 PP; HEA -35 PP, -6 % stability
    (until 2026-09-24 -2 % war support more once HEA had `hea_war_in_heaven`). LaR and HEA:
    `token_army` + civ 10 / army 5, else +25 PP and an electronics tech bonus 50 %
- `mltd_hea_the_crusade_turns_south` (war)
  - Gate: HEA has `hea_war_in_heaven` or `hea_attack_utah`, is at war with WHT / EHT / NCN, is
    gone, or after 2280.1.1
  - Payoff: declares war on HEA; against a Heaven's Guard that is not MLT's subject,
    `mltd_hea_pilgrims_of_the_steam` (now with +10 % attack and defence against HEA) and The First
    Wave (since 2026-09-24), and from Steam for the Deep a quarter of its rifles (guard 100), paid
    as one mirelurk per five (it was 600); else +50 PP. LaR steals an industry tech bonus from HEA,
    else industry 50 %. Until 2026-09-24 the rifles had a floor of +25 PP, and the Utah war paid 40
    army XP and 120 caps (else +50 PP), previewed as a condition
- `mltd_when_the_legion_breaks` (close), after any one war
  - Gate: the Legion beaten (`mltd_legion_beaten_tt`)
  - Payoff: permanent idea `mltd_mars_beneath_the_waves` (army attack, war support, recruitable
    population). Event `mltd.51`, the pens of Flagstaff (`[520.GetName]`), a choice (round 28b;
    until then the capital's population and stability, or manpower). Option a, from The Chained Are
    Given to the Tide, `mltd_legion_pens_freed`: the chained are freed - the permanent
    `mltd_the_unchained` (stability, compliance growth); the AI picks it 2 times in 3. Option b,
    `mltd_legion_pens_fed`: they are fed to the pools - the 730-day `mltd_the_pens_emptied`, a
    build-cost cut on the three creature archetypes (round 28c's review: half 28b's cut, twice its
    length). The close previews both by calling the two effects. News `mltd.52`

**Act VI - All Waters Are One** (`mltd_act6_focus.txt`): `TBH` and `LNS`, `ATE`, Tlaloc's `TLA`,
`MAX`, `MOC`, `ZAP` and `ARM`

- `mltd_the_southern_deep` (chapter)
  - Gate: none
  - Payoff: +50 PP; event `mltd.60`
- `mltd_tex_all_waters_are_one` (icon `GFX_goal_LNS_texan_dollar` since round 28c)
  - Gate: none
  - Payoff: foothold. TBH or LNS alive: shelters both cults; LaR: `token_army` + civ 15 / army 10
    on each, else +50 PP; each -4 % stability and -25 PP (from The Silent Partner). Both gone: +50
    PP (`mltd_tex_texas_gone_tt`). +80 caps either way
- `mltd_tex_black_water_rising` (war)
  - Gate: `texas_formed`, TBH or LNS gone, or after 2280.1.1
  - Payoff: declares war on TBH and LNS; against either that is not MLT's subject,
    `mltd_tex_black_water` (now with +10 % attack and defence against both) and The First Wave
    (since 2026-09-24), and from Wreckers on the Trinity a quarter of each Texan tag's rifles
    (guard 100), summed and paid as one mirelurk per five (it was 800 rifles from TBH, else LNS);
    else +50 PP. LaR: civ/army 20 on each. Round 28b dropped round 27's +3 permanent `energy` in
    the capital, and round 28c's review the creature build-cost cut first staged for the idea.
    Until 2026-09-24 each Texan tag lost 6 % stability and 3 % war support (and 2 % more war
    support if robbed), the rifles had a floor of +30 PP, and the focus paid 30 army XP
- `mltd_ate_the_feathered_tide` (new)
  - Gate: none
  - Payoff: foothold. ATE alive and not MLT's subject: shelters its cult; LaR civ/army 10, else +25
    PP; ATE -4 % stability (until 2026-09-24 -2 % war support more while its blind Speaker,
    `ATE_speaker_yesenia_aztlanl`, still ruled). Else +25 PP
- `mltd_ate_the_serpent_drowns` (new, war)
  - Gate: none
  - Payoff: ATE alive and not MLT's subject: declares war (`annex_everything`),
    `mltd_ate_the_serpent_hunted` (180 days, +10 % attack and defence against ATE) and The First
    Wave (since 2026-09-24). Else +50 PP. Until 2026-09-24 ATE lost 6 % stability and 3 % war
    support, the focus paid 40 army XP, and +20 navy experience once ATE had `ate_serpent_rises`
    (OWB's Aztlan navy, "the Frogs")
- `mltd_tla_the_iron_god_dreams`
  - Gate: none (since round 27 no Kingdom or existence gate)
  - Payoff: foothold; shelters the cults of TLA, MAX, MOC, ZAP and ARM; while TLA lives, the
    tooltip prints `TLA.current_databanks`. From The Three Voices: -6 % stability and -25 PP on
    TLA, else on each heir, else on ARM. LaR: one intel grant per living tag - the voices get civ
    15 / army 10 + `token_army`, every other tag civ/army 10 (army only on ARM). None alive, or no
    DLC: electronics 50 % and +50 PP
- `mltd_tla_the_drowned_god_sleeps` (war)
  - Gate: none
  - Payoff: declares war on TLA, MAX, MOC and ZAP. From Picking the Iron Bones: a quarter of
    Tlaloc's rifles, or once he is gone of each heir's, and a quarter of ARM's support equipment
    (each store guarded at 100), paid as one mirelurk per five, all behind one tooltip (it was 800,
    or 300 from each heir, and 200), with `mltd_tla_dreams_of_wire` (now with +10 % attack and
    defence against TLA, MAX, MOC and ZAP) and The First Wave, against any of the four that is not
    MLT's subject (since 2026-09-24; else +50 PP). TLA alive and still draining above 100: -64
    `current_databanks` (Gotchas). Until 2026-09-24 the focus also paid 20 army XP and +100 caps,
    and cost TLA 6 % stability when the drain could not run, or each heir and ARM 4 % once he was
    gone. LaR: steals an engineering/industry tech bonus from the first living of TLA / MAX / MOC /
    ZAP / ARM (electronics 75 % if none lives), else electronics 75 %
- `mltd_the_last_king_kneels` (close), after any one war; icon `GFX_goal_TBH_The_Last_Piece` since
  round 28c's balance review
  - Gate: Texas beaten (`mltd_texas_beaten`, `mltd_texas_beaten_tt`)
  - Payoff: permanent idea `mltd_the_drowned_south` (factory output, stability); event `mltd.61`,
    news `mltd.62`. Its research slot moved to The Tide Turns South in round 28c's balance review;
    MLT still ends the campaign on five

**The finale - R'lyeh Rises** (`mltd_finale_focus.txt`)

- `mltd_rlyeh_rises`
  - Gate: 300 controlled states
  - Payoff: +15 victory points in M'lyeh (province 1983), on top of the Kingdom's +15, followed by
    `mltd_newline_tt`; the global flag `mltd_rlyeh_risen` (nothing reads it yet: it is a hook for
    later content); event `mltd.70`, news `mltd.71`
- `mltd_ending_the_dreamer_wakes` (icon `GFX_goal_MDT_gorgon_eye` since round 28c)
  - Gate: the endings each name both others in `mutually_exclusive`
  - Payoff: permanent idea `mltd_the_dreamer_wakes` (war: army attack and defence, war support, a
    stability cost); event `mltd.72`
- `mltd_ending_the_priestess_reigns`
  - Gate: as above
  - Payoff: permanent idea `mltd_the_priestess_reigns` (rule: stability, political power, lower
    consumer goods); event `mltd.73`
- `mltd_ending_return_to_the_sea`
  - Gate: as above
  - Payoff: permanent idea `mltd_the_return_to_the_sea` (the deep: monthly population growth and,
    since round 28c, a build-cost cut on the three creature archetypes in place of recruitable
    population). While MLT holds Mireport when the focus completes (`mltd_leviathan_can_surface`):
    two Leviathans there, through `mltd_spawn_leviathan` twice; the first is the pride of the fleet
    if none has surfaced yet. Otherwise `mltd_return_to_the_sea_no_mireport_tt`. Event `mltd.74`

The endings' ideas are the tree's one place for large bonuses. Each act idea stays inside +-5-10 %;
the Northern Waters' justification time is the exception. Three rewards cut the creature
archetypes' build cost and stack - Feed the Spawning Pools, `mltd_the_pens_emptied` and
`mltd_the_return_to_the_sea` (Project > *Rewards scale to when they are taken*).

*The invitations* (round 28). Act III holds three: The Drowned Covenant (the Broken Coast,
`mltd.21`), Hail the Drowned King (the Bone Dancers, `mltd.24`) and Terms for the Citadel (the
Brotherhood in Washington, `mltd.32`). Each focus sends the invitee an event whose two options are
its answer, and the answer reaches MLT as an event of its own (`mltd.22` / `.23`, `.25` / `.26`,
`.33` / `.34`). Since rounds 28b and 28c each invitation is one half of its nation's pair: taking
it closes its war twin (The Tide-Wall, The Coast Goes Under, Drown the Dance) for good, whatever
the answer.

- The Drowned Covenant, answered by BRK
  - Historical focuses: always accepts (50 against 0)
  - Unhistorical: half the time (50 against 50)
- Hail the Drowned King, answered by BDT
  - Historical focuses: always accepts (100 against 0)
  - Unhistorical: always accepts
- Terms for the Citadel, answered by WBH, or TCA as the Northwestern Brotherhood
  - Historical focuses: never accepts (0 against 50)
  - Unhistorical: WBH half the time (50 against 50), TCA a tenth (10 against 90)

How the three work:

- **One set of gates** (round 28c's balance review; the user's own design, not the review's). All
  three ask the same three things of the faithful, inside the La Resistance `if` (*The DLC idiom*):
  the invitee's cult at 40 % (`mltd_brk_strong_cult_tt`, `mltd_bdt_strong_cult_tt`), that country's
  civilian infiltration token, and `network_national_coverage` over 0.25 (`mltd_brk_network_tt`,
  `mltd_bdt_network_tt`); Terms for the Citadel writes all three per tag behind one line,
  `mltd_wbh_terms_faithful_tt`. Each also carries one **rival gate**, the god or table the invitee
  will not share: the Covenant refuses a Brotherhood already sworn (`mltd_wbh_alliance`), Terms a
  Broken Coast already sworn (`mltd_brk_covenant_joined`), and Hail the Drowned King a Bone Dancers
  sworn to Heaven's Guard's seraph lords, or an MLT allied to Heaven's Guard
  (`bdt_listen_to_the_pilgrims`, `mltd_bdt_not_pilgrims_tt`). What went: the Covenant's
  `brk_nf_pirate_coast` coast test and its civilian intel over 50 %, its higher cult and coverage,
  and Hail's demand that the Bone Dancers had crowned OWB's Odious King - each of them a gate that
  rested on the invitee's own tree or conquests, so a game could close the door before MLT ever
  knocked. Terms, which had no intelligence gate, gained the set, and an AI can now reach it (MLT's
  AI > *The invitations' war goals*).
- **The odds.** An AI invitee picks by its options' `ai_chance`, which reads the game's
  historical-focus setting through `is_historical_focus_on` (OWB's idiom,
  `events/nevada_pact_events.txt:15-22`); a human answers freely. The weights are relative: the
  Broken Coast's refusal drops to nothing on historical (a `modifier` with `factor = 0`), and the
  Brotherhood's acceptance starts at 0 and gains its unhistorical chance through `add` modifiers,
  TCA's refusal rising with it.
- **The odds in the description.** Each invitation's `_desc` ends with its odds line -
  `[GetMltdBrkOdds]`, `[GetMltdBdtOdds]` or `[GetMltdWbhOdds]` (`mltd_scripted_localisation.txt`) -
  which reads the same rule, so it is true in the game being played. Each first says when a human
  answers, the Broken Coast's and the Brotherhood's also when there is no one left to ask, and the
  Brotherhood's names whichever of WBH and TCA would be asked. No line gives a bare percentage.
- **Which Brotherhood.** `mltd_wbh_terms_target`: the Washington Brotherhood unless it is gone or
  someone's subject, else TCA as the Northwestern Brotherhood. OWB lets TCA form it while WBH is
  its subject, and then both pass `mltd_wbh_brotherhood`; the subject is never asked, and one offer
  goes to one Brotherhood.
- **Its faction comes with it** (2026-09-25; the user: a yes should pull WBH out of its league and
  every other member into the Covenant). `mltd_wbh_terms_target` accepts a Brotherhood that leads
  its faction, and `mltd_wbh_join_the_covenant` moves the faction over: first the independent
  members at peace with MLT and with every country in MLT's faction, each through OWB's
  `leave_current_faction` - which keeps OWB's faction arrays and ally strategies in step; a plain
  `leave_faction` for a faction OWB does not track - and into the Covenant with
  `mltd_drowned_covenant` both ways (`mltd_wbh_bring_into_the_covenant`); then the Brotherhood,
  after handing its old faction to a member that stays behind at war with MLT, if one does; then
  the subjects, each only if its overlord has not brought it. Vanilla's `faction_traitor` opinions,
  which leaving a faction earns from its leader (`on_leave_faction`), are cleared between the
  Brotherhood and each member - unverified: whether the on_action has run by then. OWB never clears
  `GLOBAL.northern_league_leader`, its test that the league exists and the country every later
  joiner is added through, so the effect re-points it at the new leader, or clears it once the
  league is empty. Who can be in the league: Gotchas > *OWB's Brotherhood leads the Northern
  League*.
- **Within a nation, `mutually_exclusive`; across nations, a flag.** An invitation and its war twin
  exclude each other both ways, because they are two roads to one nation. Across nations only an
  acceptance closes the other door, and a refusal leaves it open, so that exclusion is a flag:
  `mltd_brk_join_the_covenant` sets `mltd_brk_covenant_joined` on MLT when the Broken Coast
  actually joins MLT's faction, and `mltd_wbh_join_the_covenant` sets `mltd_wbh_alliance` when the
  Brotherhood does, each in its `add_to_faction` branch only. Since round 28b each join is written
  as a line (`mltd_<tag>_joins_covenant_tt`) under the test the join will pass once the faction
  exists, with `add_to_faction` and the flags in `hidden_effect`: previewed plainly, a faction
  founded in the same effect showed nobody joining it. The events' options keep those lines. The
  focuses' previews since 2026-09-24 draw the join natively instead, in an `effect_tooltip` with no
  limit on it (vanilla's `EFFECT_ADD_TO_FACTION`, "X joins faction.", which needs no faction's
  name) - unverified: if the join line is missing in game while MLT leads no faction, the round-28b
  line `mltd_<tag>_joins_covenant_tt` under "If they accept:" is the fallback.
  - `mltd_brk_covenant_joined` closes Terms (`mltd_wbh_terms_no_covenant_tt`; the Covenant's
    tooltip said so until 2026-09-24).
  - `mltd_wbh_alliance` closes the Covenant (`mltd_brk_no_brotherhood_table_tt`, inside the
    Covenant's courtship `if`, so its +50 PP with the Broken Coast gone survives). Round 28 also
    closed The Tide-Wall on it; since round 28b Terms excludes the wall outright, and the wall's
    gate and `mltd_wbh_tide_wall_no_alliance_tt` are gone.
  - The Bone Dancers sit beside either.
- **The race.** A focus can be picked while the other invitation's answer is on its way - a day for
  an AI, as long as a human takes - and `continue_if_invalid` lets the world change while a focus
  runs. So:
  - all three rewards test the invitee and MLT's faction again before sending, the Covenant and
    Terms the other flag too, and pay +50 PP otherwise (Hail the Drowned King since round 28c's
    review). Since 2026-09-25 the preview shows that fallback only while the focus runs and the
    offer can no longer go - an `if` of its own over `focus_progress`, beside the real `if` /
    `else` in `hidden_effect`, both reading the focus's trigger (`mltd_wbh_terms_can_offer`,
    `mltd_brk_covenant_can_offer`, `mltd_bdt_covenant_can_offer`); the Covenant's also while the
    raiders are MLT's subject, when the focus is open and pays only that. Read off the real `if` /
    `else` on 2026-09-24 it showed only the fallback whenever the invitee was in a faction or at
    war with MLT, and from round 28c's review to 2026-09-23 beside the offer, under a line saying
    when it is paid. A fallback of the Covenant or Hail sets `mltd_brk_covenant_lapsed` /
    `mltd_bdt_covenant_lapsed` on MLT: no offer can come again (the events are `fire_only_once`),
    so the AI's courtship of that nation ends there (MLT's AI > *The Broken Coast*);
  - the acceptance options of all three events carry a `trigger` (the invitee free and at peace
    with MLT, MLT free or leading its faction; `mltd.21` and `mltd.32` also the other flag unset;
    `mltd.24` since round 28c's review), so an invitee that can no longer join is left only the
    refusal;
  - the three wars never declare on, or penalise, a country in MLT's faction (Drown the Dance since
    round 28c): a player can still invite one from the diplomacy screen while a war focus runs.
- **What a refusal costs.** The offer is the slow road: each invitation takes twice as long as its
  war twin (since 2026-09-25; until then Terms was the longer of its pair, and the Covenant and
  Hail the Drowned King as long as theirs), and no invitation grants a timed idea. A refusal leaves
  MLT only an `annex_everything` war goal on the refuser that expires after 365 days - and, since
  the invitation has closed its war twin, that war goal is the tree's one road left to that war.
  - It is created in the refuser's own option (`mltd.21` b, `mltd.24` b, `mltd.32` b), so the
    invitee sees it before it chooses, as
    `FROM = { create_wargoal = { ... target = ROOT expire = 365 } }`, and only while the two are
    not already at war. The option shows vanilla's expiry line (`mltd_refusal_wargoal_expires_tt`,
    after `BUL_total_war_wargoal_expires_tt`).
  - It comes on top of the old penalties: `mltd_drowned_covenant_refused` and the global flags
    `mltd_brk_refused_covenant` / `mltd_bdt_refused_covenant`.
  - A refused Terms also sets `mltd_wbh_refused_terms`, which since round 28b only MLT's AI reads
    (its refusal holds). Round 28 left The Tide-Wall open after a refused Terms, without its war
    bonus (`mltd_wbh_tide_wall_refused_tt`, since deleted); since round 28b Terms has closed the
    wall already, so a refused Terms leaves only the war goal - no bunkers in The Warren, no claim
    removed, no idea.
  - Each focus's tooltip names the gamble in three parts since 2026-09-24 (the user: it only needs
    the invitation, what a yes founds and who joins, and the war goal a no leaves): the offer
    (`mltd_brk_covenant_offer_tt`, `mltd_bdt_covenant_offer_tt`, `mltd_wbh_terms_offer_tt`), "If
    they accept:" (`mltd_invitation_if_accepted_tt`; Terms' `mltd_wbh_terms_if_accepted_tt`) over
    the native lines of the faction founded and the invitee joining - an `effect_tooltip`, since
    the answer runs in the invitee's event - with Terms' claims line (`mltd_wbh_terms_claims_tt`),
    and "If they refuse:" (`mltd_invitation_if_refused_tt`, `mltd_wbh_terms_if_refused_tt`, each
    saying the war goal expires after a year) over the native war-goal line. The opinion modifiers
    and the flags come with the answer and are no longer previewed.
- **The AI.** An AI MLT reaches Terms only through its hold (*The AI*, above), and a refusal's war
  goal is held until its own gates allow that war (MLT's AI > *The invitations' war goals*).

*The spoils* (round 28; restructured in round 28c; `mltd_spoils_focus.txt`). Optional focuses that
pay off the land the acts conquer. No other focus names one, so the spine never waits on them; they
also fill some of the months the focus slot idles while a close waits on its war (Plan). Ten
focuses in four groups, one group after each of Acts III-VI's closes: two for the north, the
interior and the south each, four for the NCR's California, the first true superpower MLT fights.
None is chained to another.

- The north
  - Prerequisite (close): `mltd_the_tide_turns_south`
  - Anchor (chapter): `mltd_ncr_a_mole_in_shady_sands` (15,28)
  - Focuses, cell and gate: `mltd_spoils_the_scribes_vaults` (13,28), owns Seattle (84) or East
    Portland (37); `mltd_spoils_the_drowned_sound` (17,28), 80 controlled states
- California
  - Prerequisite (close): `mltd_when_shady_sands_falls`
  - Anchor (chapter): `mltd_mars_in_the_water` (15,32)
  - Focuses, cell and gate: `mltd_spoils_the_canals_run_salt` "Salt in the Canals" (11,32), owns
    Shady Sands (253) or San Francisco (163); `mltd_spoils_the_foundries_relit` (13,32), owns The
    Boneyard (350); `mltd_spoils_the_office_of_salt` "The Office of Salt and Industry" (17,32, new
    in round 28c), owns The Hub (1) or Sac-City (135); `mltd_spoils_the_drowned_harvest` (19,32),
    120 controlled states
- The interior
  - Prerequisite (close): `mltd_when_the_legion_breaks`
  - Anchor (chapter): `mltd_the_southern_deep` (15,36)
  - Focuses, cell and gate: `mltd_spoils_the_legions_armouries` (13,36), owns Flagstaff (520);
    `mltd_spoils_the_iron_tithe` (17,36), 180 controlled states
- The south
  - Prerequisite (close): `mltd_the_last_king_kneels`
  - Anchor (chapter): `mltd_rlyeh_rises` (15,40)
  - Focuses, cell and gate: `mltd_spoils_the_black_water_wells` (13,40), owns Dallas (892) or Lone
    Star (921); `mltd_spoils_the_salt_road` (17,40), 250 controlled states

How the groups work:

- **Layout** (the user's round-28c note: the side branches felt awkward; each group now sits on the
  main line). Each group flanks, on the spine's own row, the chapter that follows its close - two
  columns out on each side, California's also four - so it lies beside the act during which it is
  worked: the north's during the NCR's war, California's during the Legion's, the interior's during
  Texas's, the south's in the wait before R'lyeh Rises and after the ending. A spoils focus takes
  that chapter as its `relative_position_id` (x = -4 / -2 / 2 / 4, y = 0) but its act's close as
  its prerequisite, so it draws a line from the close as its chapter does and gates nothing.
  One-offs sit on the left, each group's idea focus on the right. Round 28 had twelve focuses in
  four chained branches of three down x = 20, each root at (5,1) of its close.

- **Round 28c's merge.** Each old chain of three became two focuses: the third focus of each chain
  kept its id and its idea and took in the middle focus's works or hatch -
  `mltd_spoils_beyond_the_cascades` into The Drowned Sound, `mltd_spoils_the_forges_of_the_bull`
  into The Iron Tithe, `mltd_spoils_the_gulf_yards` into The Salt Road - and the three ids, with
  their loc, are gone. Their tech bonuses (industry; production and construction) were dropped: a
  group keeps one tech bonus at most. California kept its three and gained The Office of Salt and
  Industry.

- **Gates** ask for land actually held - `owns_state` on a theatre state, or a controlled-state
  count in a `custom_trigger_tooltip` - and never for a war's outcome, so a group can be worked
  while the next act's war is fought.

- **Payoffs** (round 28b's rule: they scale with the economy they land in, or are sized to their
  moment from the plan's snapshots):

  - compliance or resistance in every conquered core MLT owns and controls - the Brotherhoods' and
    the Bone Dancers' (The Scribes' Vaults), the NCR's (Salt in the Canals), the Legion's (The
    Legion's Armouries); OWB's coring asks for high compliance and low resistance
    (`coring_button_scripted_triggers.txt:32-73`);
  - a hatch of MLT's best mirelurks (the archetype `amphibious_beast_equipment`), counted at run
    time: per held NCR core (Salt in the Canals), per held Gulf port - Port Lavaca (799), The
    Corpse (903), Richmond (904), Houston (880) - (The Salt Road);
  - relit works: an extra shared building slot and an instantly built factory in each listed works
    state MLT owns and controls - civilian factories in 350, 253 and 163 (The Foundries Relit),
    arms factories in Spokane (332) and Crowshaven (71) (The Drowned Sound) and two each in 520,
    518 and 522 (The Iron Tithe). OWB's PMR idiom. Decimation leaves little to answer: under OWB's
    default game rule (Factory Decimation-Only, `common/scripted_effects/exodus_effects.txt`) every
    conquered person stays, and a factory goes only from a state far larger than most. What halves
    a conquered state's factories, resources and building slots is OWB's non-core penalty
    (`non_core_controller`, `common/modifiers/00_static_modifiers.txt`), eased by the occupation
    law and compliance until MLT cores the state, and a relit factory there shares it;
  - two 50 % tech bonuses: electronics (The Scribes' Vaults) and construction (The Foundries
    Relit). Construction is a single line of techs, so its bonus is granted only while
    `construction_industry_tech_6`, the line's last, is unresearched, and pays +50 PP otherwise,
    since a group may open years after its close. The tech can be researched while the focus runs,
    so since round 28c's review the preview shows both outcomes while it is unresearched
    (`mltd_spoils_foundries_bonus_if_tt`, `mltd_spoils_foundries_bonus_else_tt`);
  - two 365-day ideas (round 28b): `mltd_the_legions_steel` (The Legion's Armouries; defence and
    armour on the three creature archetypes since round 28c's review, in place of 28b's build-cost
    cut, which came from the same close as `mltd.51` b's and stacked with it) and
    `mltd_the_black_water_visions` (The Black Water Wells; research speed);
  - one permanent idea per group from its idea focus, two in California, 2-3 modifiers each inside
    +-5-10 %: `mltd_the_drowned_sound`, `mltd_the_office_of_salt`, `mltd_the_drowned_harvest`,
    `mltd_the_iron_tithe` and `mltd_the_salt_road` (Layout, `mltd_ideas.txt`). The Salt Road's
    `core_creation_cost_factor` is OWB's own coring-cost modifier, and its `caps_income_modifier`
    does nothing with the caps rule off.

  No resources since round 28b - by 2280 MLT holds the north's water and metal, and its creature
  lines burn only water - and no research slots: the only two are Act III's close and `mltd.40`
  option a (round 28c's balance review moved the fourth slot forward to The Tide Turns South).
  Every one-off whose preview the engine cannot draw (a state loop whose limit may match nothing
  yet, an owns-dependent `if`, a count made at completion) is a custom tooltip over `hidden_effect`
  (*Numbers in two places*).

- **Icons.** No spoils icon is tall, and the cell directly above every spoils focus is empty; six
  cells directly below one hold other files' focuses (Drowned Delegates, Salt on the Caravan Roads,
  All Waters Are One, The Iron God Dreams, The Dreamer Wakes, Return to the Sea), whose icons must
  stay normal height too (Gotchas).

- **Every spoils focus** has `cancel_if_invalid = no` + `continue_if_invalid = yes`, `ai_will_do` 2
  (below the heads' 3 and the chapters' and closes' 10), an OWB icon with its `_shine` and, the
  first in our shared-focus files, `search_filters` Industry (and Research on The Scribes' Vaults,
  The Drowned Sound, The Office of Salt and Industry and The Black Water Wells). The spoils fire no
  events, so `mltd.35-39` stay free.

*The Broken Coast's volunteers* are the engine's own: MLT sends divisions of its choosing - Deep
Ones and Star Spawn included - through the diplomacy screen's Send Volunteers. The engine's limit
(a share of the sender's divisions and of the target's provinces, vanilla
`VOLUNTEERS_PER_COUNTRY_ARMY` / `_PER_TARGET_PROVINCE`) is raised by `send_volunteer_size`;
volunteers go home when the sender goes to war or the target makes peace, and cannot go to an ally,
so they stop once BRK joins the Covenant. The modifier also raises the limit towards any other
country at war. Since round 27 The Deep Ones Sail North calls `mltd_brk_add_volunteer_size` twice,
for +6, because it absorbed Star Spawn over the Strait's call. With BRK gone, the focus pays
political power instead, so the modifier never comes without the raiders. The literals:

- the +3 per call: `mltd_brk_add_volunteer_size` and `mltd_brk_volunteer_size_tt`;
- the +6: `mltd_brk_volunteer_size_6_tt`, the one line that stands for both calls;
- the Covenant's 40 % and 25 % (round 28c's balance review): `mltd_brk_strong_cult_tt` and
  `mltd_brk_network_tt`.

*The Broken Coast off Haida Gwaii* (round 25). BRK's own OWB focus `brk_nf_lessons_of_war` grants
it war goals on the Haida Confederation (`HAI`), whose whole country is one island: states 9 and
398, a landmass of their own (measured from OWB's `map/provinces.bmp` - BRK's own home, capital 492
included, is continental, bar the one-state Frozen Isles, 188). All nine of its land provinces are
coastal, so each is a valid beach, but only 5123 and 5130 have a port. BRK's AI lands wherever its
planner picks - usually a portless beach - and the landing starves (no supply, little supply
grace), is thrown back, and lands again; MLT's volunteers, commanded by BRK while they serve, go
down with every landing. **Nothing in script can aim a naval invasion at a province**: the engine
picks the landing site, and the AI levers stop at the state or region (`invasion_unit_request`) or
at the whole target country (`invade`, which with a negative value forbids invading it at all). So
`on_daily_MLT` watches instead: while MLT has taken `mltd_brk_salt_on_the_broken_coast` (since
round 27 an Act II head, after The Deep Ones Walk, so the watch starts later than it did) and
**both** BRK and HAI are AIs, it sets the global flag `mltd_brk_landed_on_haida` the day BRK holds
any Haida province (`mltd_brk_on_haida_gwaii`, province-level, since a landing takes a beach and
not a state), and fires `mltd.27` to HAI the day it holds none again. *Pushed off* has to mean
landed-then-lost: BRK holds no Haida province before its first landing either, so a plain control
test would end the war the day it began. The watch is daily so that a landing thrown back within
the week is not missed; the flag is cleared whenever that war is not running, so a later war starts
clean. Round 28c: the watch is off, and the flag cleared, while MLT itself is at war with the
Broken Coast - The Coast Goes Under and a refused Covenant's war goal make that war a road of the
tree, MLT's volunteers come home the day it starts, and a peace with the Haida would only free the
raiders' army against MLT - and `mltd.27` tests the same war as a backstop. The same round fixed
the clearing test: it read
`NOT = { country_exists = BRK country_exists = HAI BRK = { has_war_with = HAI } }`, and a `NOT`
over several triggers is a NOR (Gotchas), so the flag cleared only once both countries were gone
and a war that ended with the raiders ashore left it set for the next one; it is now
`NOT = { AND = { ... } }`. `white_peace` changes no ownership - HAI keeps its island, BRK its coast
\- and HAI is ROOT, the nominal winner, having thrown the landing back. The province list is a
literal in the trigger; re-measure it if OWB redraws Haida Gwaii. Whether BRK can declare on HAI
again afterwards is unverified: its war goals came from a one-time focus and are spent by the
declaration, and OWB's AI justifies only on a neighbour
(`diplomacy_scripted_triggers.txt:1210-1216`), which HAI is not.

**Flavour events** (`mltd.9-18`; a monthly pool, not MTTH).

*The pool.* `on_monthly_MLT` (`mltd_on_actions.txt:87-114`) rolls
`random_events = { 50 = 0  10 = mltd.9 ... 10 = mltd.19 }` once a month. The `0` entry is the
no-event sink (vanilla `00_on_actions.txt:374`, `17000 = 0`), so each roll has a 50-in-160 chance
of nothing and 10-in-160 for each event (`mltd.19` is *Hail M'lyeh*, below). Like `on_daily_MLT`,
it rolls only while the tag is literally `MLT`.

*The gate.* Each event is `is_triggered_only` + `fire_only_once` and has
`trigger = { mltd_flavour_can_fire = yes ... }` (`mltd_scripted_triggers.txt:7-12`:
`original_tag = MLT`, Kingdom complete, `has_capitulated = no`, no `mltd_flavour_cooldown`). Its
`immediate` sets `mltd_flavour_cooldown` for 120 days inside `hidden_effect`. `mltd.1` sets the
same flag for 90 days (`mltd_events.txt:8`), so no flavour event lands on top of the Kingdom beats.
Four events add a gate of their own: `mltd.11` and `mltd.16` need `mltd_deep_ones_summon_unlocked`
(set by `mltd.7`, the Call); `mltd.14` needs `mltd_books_read > 0`; `mltd.18` needs
`capital_scope = { is_fully_controlled_by = ROOT }`.

*Pacing.* From a 20,000-run simulation, medians counted from when the 90-day guard lapses, assuming
a roll that picks an already-fired or blocked event fires nothing (unverified): first event after
~1 month, fifth ~25 months, tenth ~77 months, and never two closer than ~5 months (the cooldown
plus the wait for the next roll). A sink of 200 pushes the tenth to ~117 months. These figures
predate *Hail M'lyeh*, whose extra entry makes any given roll a little less likely to land on each
of the ten. The tunables are the sink, the eleven weights and the cooldown. The cooldown is a
literal in eleven `immediate` blocks (`mltd.9-18` and *Hail M'lyeh*'s `mltd.19`), plus `mltd.1`'s
90, and is repeated in the trigger-file and on_actions comments.

*Size.* Effects stay at or below OWB's own `flavour.2` (`events/flavour_events.txt:39`): political
power 10-40, stability and war support 0.01-0.03, caps 10-20 through `add_caps`, country manpower
+20 / -50, +500 capital population (`add_state_population`, OWB `00_scripted_effects.txt:509`), and
two timed ideas (`mltd_flavour_strange_harvest` 90 days, `mltd_flavour_unnamed_colour` 120 days).
The one caps cost (`mltd.9` option c) is gated by `caps_cost_trigger` with a `caps_diff` temp
variable (OWB `nf_bis.txt:721-723`). The safer option carries `ai_chance` base 2, the rest base 1.

*Presentation.* Pictures are reused OWB `GFX_event_*` sprites, so nothing new goes into
`event_images/SOURCES.md`; `mltd.8`'s `GFX_event_mirelurk_red_death_shipwrecker` is deliberately
not reused. `.d` text uses only `§o` / `§c` and option text no colour codes, as for `mltd.1-8`.
Lovecraft is named only from stories published before 1930; later stories (Innsmouth, The Whisperer
in Darkness) and modern games (The Sinking City, Dredge, Bloodborne) are only alluded to, under
original names.

*Why not MTTH* (OWB's house idiom): non-triggered events are checked for every country every 20
days (`EVENT_PROCESS_OFFSET`, vanilla `00_defines.lua:301`) across ~424 OWB tags, and their timing
cannot be paced. OWB's own `flavour.2` (Pacific trade, MTTH 24 months) can probably already fire
for MLT and counts against the same budget.

**Hail M'lyeh** (`mltd.19`, round 15; a *Hail Hydra* homage). The eleventh entry in the flavour
pool and the only one without `fire_only_once`: our agents find that a trusted counsellor of a
foreign leader has been one of the faithful all along. Its `trigger` adds to
`mltd_flavour_can_fire` La Resistance, an agency, no `mltd_hail_cooldown` (365 days, set in
`immediate` beside the shared 120-day cooldown) and at least one country passing
`mltd_hail_candidate` (`mltd_scripted_triggers.txt`): not MLT, MLT's `network_national_coverage`
there above 0 (OWB's own visibility gate for `operation_infiltrate_civilian`,
`00_operations.txt:135-138`), and no `token_civilian` on it yet. `immediate` saves a random such
country as `mltd_hail_target`; the text names it (`[mltd_hail_target.GetNameDef]`) and its leader
(`[mltd_hail_target.GetLeader]`), and the single option gives MLT that country's `token_civilian`
plus 10 civilian intel through the Lost Hills scope switch
(`event_target:mltd_hail_target = { ROOT = { add_operation_token = { tag = PREV ... } } }`,
`Lost Hills (BOS) Focus.txt:1789-1797`), hidden behind `mltd_hail_token_tt`. The token opens OWB's
own steal-tech operation against that country. Against the Broken Coast or the Bone Dancers it also
satisfies one of their invitation's courtship lines; the story acts have no other intel gates since
round 27. The picture is OWB's `GFX_event_csis_prime_minister`, a suited silhouette; the text
follows the event colour rules (`§o` / `§c` only, a plain option).

**Book expeditions** (round 13). Since round 14 a Book's `available` accepts control of its state
or, with La Resistance, a full-strength network in it:
`network_strength = { state = N value > 99.9 }`, the target-free per-state form (vanilla
`achievements.txt:2296-2299`) - a network in a state whose controller has changed drains at 10 a
day, so it measures the network against whoever holds the state now. The check sits in an
`if`/`else` on `has_dlc` under the tooltip `mltd_<n>_book_reach_tt`, never inside the OR (Gotchas).
The five Books also carry `cancel_if_invalid = no` + `continue_if_invalid = yes`, like the rituals
and the story acts' focuses: 100 % is the scale's cap and drops the moment the operative moves on,
so a Book in progress keeps going. A Book focus no longer reads its Book. Its `completion_reward`
only previews the reward - `mltd_<n>_book_expedition_tt`, then *When the book is found:*
(`mltd_when_book_found_tt`), the gift unlock, the modifier preview and `mltd_book_found_read_tt` -
and fires the expedition's first event two days later. Each expedition is three `country_event`s
(`is_triggered_only` + `fire_only_once`), chained by
`hidden_effect = { country_event = { id = ... days = 7 random_days = 7 } }` in every option behind
`mltd_expedition_continues_tt`, so a Book arrives 2-4 weeks after its focus: Tide `mltd.101-103`
(Arago), Shell `201-203` (The Warren), Current `301-303` (Paisley Pit), Brood `401-403` (Arroyo),
Abyss `501-503` (The Maw).

- *Choices.* War support against stability (101, 501); army XP against stability (102, 201);
  political power against stability (301); force against caps (401, the caps option gated by
  `caps_cost_trigger`); +500 capital population against stability (402). In three chains **one of
  two named advisors dies**: Asenath or Obed (`MLT_TERROR` / `MLT_TIDE_HUNTER`, 202), She Who Knows
  of Ways or M'lulu's Knowledge (`MLT_KNOWS` / `MLT_MUTANTS`, 302), the Aspect of the Killclaw or
  of the King (`MLT_KILLCLAW` / `MLT_KING`, 502). Those options run `retire_character` (vanilla
  `effects_documentation.md:6436`), each gated by `has_character`, and a third option appears only
  when neither advisor is left, so the event always has a valid option. Sizes follow the flavour
  events: 0.02-0.03 stability or war support, 10-30 PP or army XP, 250-500 manpower.
- *The Book.* The third event of each chain sets `mltd_<n>_book_found` and adds 1 to
  `mltd_books_read` inside a `hidden_effect`, then repeats the unlock and preview lines the focus
  showed. The five gift decisions are `visible` on that flag (they used to test
  `has_completed_focus`), and the centre column's 1 / 3 / 5 gates count the variable, so both open
  when an expedition ends rather than when its focus completes.
- *Text.* The same event rules as `mltd.1-8`: `.d` text uses only `§o` / `§c`, options no codes.
  Advisor names in option text are the characters' own names through their tokens
  (`[MLT_TERROR.GetName]`, ...), so OWB's display names (`characters_MLT_l_english.yml`) show; OWB
  already named three of them after *The Shadow over Innsmouth* (Asenath, Obed, Robert Olmstead).
  Pictures are reused OWB sprites plus `GFX_mltd_event_final_ritual` for the Abyss.

**Cult Infiltration** (`mltd_cult_infiltration_cat`, opened by the focus *The Spreading Cult*,
which also founds a cult at 20 % in every neighbouring major through `every_country` +
`mltd_cult_neighbouring_major`). A cult lives **on the country that holds it**:
`mltd_cult_strength` (0-100, a percentage), its weekly decay `mltd_cult_decay`, the war penalties
in percentage points `mltd_cult_threat_big` / `_small` / `_air`, and the five modifier inputs
`mltd_cult_{stability,war_support,org,factory,air}_var`. Round 17 replaced round 14's five targeted
decisions - and every caps cost - with two operations and two untargeted decisions:

- *Found a Cult* (`mltd_op_found_a_cult`, `common/operations/mltd_operations.txt`): any country
  MLT's network covers that has no cult - no neighbour or major test; paid in infantry and support
  equipment. The cult starts at 10 % (20 % on a critical success) and the target gets the dynamic
  modifier `mltd_cult_infiltration`.
- *Nurture the Cult* (`mltd_op_nurture_the_cult`): a country whose cult is below 100 %; paid in
  infantry and support equipment; +12 (+20 on a critical success). Its `available` tests
  `has_variable = mltd_cult_strength` as well (round 24): `visible` is not re-checked once an
  operation is running, and a cult that withered to nothing mid-operation left a cleared variable,
  which reads 0 and passed `< 100` - re-founding the cult at the nurture price. Both operations
  need La Resistance, network coverage above 0 and *The Spreading Cult*, and `cost_multiplier = 0`
  keeps their price flat on repeats.
- *Call for People* / *Call for Equipment* (`mltd_cult_call_for_people` / `_equipment`):
  untargeted, each on a timed-flag cooldown. They pay per point of **total** cult strength,
  `mltd_cult_total_strength` (summed on MLT by `mltd_cult_rebuild_list`): 10 manpower, or 4
  infantry + 1 support equipment (archetypes, so MLT's best variant; OWB
  `_MOT_decisions.txt:156-163` pays the same pair by variable). Three cults at 50 % (150 points)
  pay 1,500 manpower, or 600 + 150 equipment, a call. From Act V's chapter,
  `mltd_mars_in_the_water`, *Call for Equipment* pays 1 mirelurk a point instead - the archetype
  `amphibious_beast_equipment`, MLT's best breed, about the same IC a point - because from then on
  the tribe fields creatures, not rifles (round 28b; its own tooltip, `mltd_cult_call_beasts_tt`).
- Without La Resistance only *The Spreading Cult* plants cults, and they wither away; the Calls
  work while any remain.
- *Decay* (`mltd_cult_weekly`, `on_weekly_MLT`): `0.1 + s*s/3000` points a week - 0.13 at 10 %,
  0.63 at 40 %, 0.93 at 50 %, 2.8 at 90 %, 3.43 at 100 % - **halved** in a country a story act's
  spying head has sheltered (country flag `mltd_cult_sheltered`, round 17; a conflict sub-tree's
  root until round 27) and **x3 at war with MLT**. One operative running *Nurture the Cult* back to
  back holds a cult near 62 % (90 % sheltered), two ~90 % (100 % sheltered), at 60 days an
  operation; operations that run longer hold less (one at 90 days: ~50 %, ~73 % sheltered). Until
  2026-09-23 the decay was `0.5 + s*s/2500` (0.54 at 10 %, 1.5 at 50 %), under which one operative
  held only ~47 % on paper, and in play - where operations ran long - a young cult faded faster
  than it was nurtured. Below 1 % the cult dissolves (`mltd_cult_dissolve`) and *Found a Cult* can
  target the country again.
- *War* (`mltd_cult_infiltration`, `mltd_dynamic_modifiers.txt`):
  `enable = { has_war_with = MLT }`, and `mltd_cult_refresh` zeroes the inputs outside such a war
  as well, so nothing shows or applies at peace. At war, per point: -0.25 % stability and war
  support, -0.15 % division organisation and factory output, and +0.5 % air accidents (-25 % / -15
  % / +50 % at 100 %). `on_war_relation_added` refreshes the enemy's cult the moment the war starts
  (ROOT attacker, FROM defender), rather than at the next weekly tick.
- *The list* (round 16): the category's description ends with every cult abroad, strongest first -
  flag, name and strength, at most 8 rows, then "...and N more". It is rebuilt by
  `mltd_cult_rebuild_list` (every existing country with `mltd_cult_strength`, selection-sorted with
  `find_highest_in_array`, OWB's own tools at `caps_scripted_ai.txt:161-218`) every day once *The
  Spreading Cult* is done (`on_daily_MLT`, so an annexed country drops out the next day), weekly
  after the decay loop, after every cult operation and after *The Spreading Cult* itself (one more
  override line). The rebuild writes the first eight into slots on MLT - `mltd_cult_row_<k>` (the
  country) and `mltd_cult_row_<k>_str` (its strength) - plus `mltd_cult_count` and
  `mltd_cult_more`, and `GetMltdCultList`
  (`common/scripted_localisation/mltd_scripted_localisation.txt`) prints one row per filled slot
  from those plain variables, through `ROOT` (see Gotchas). At war the target's *Drowned Faithful*
  modifier shows the penalties.
- *Numbers in several places*: the operations' gains in their outcome blocks and in `mltd_op_*_tt`;
  their equipment in each `equipment` block (shown natively); the Call rates in the decisions'
  temp-variable lines and in `mltd_cult_call_*_tt` (the late mirelurk a point also in
  `mltd_cult_call_for_equipment_desc`); the cooldowns in the flags and in
  `mltd_cult_call_*_again_tt`; the decay and penalty rates in `mltd_cult_refresh` and the
  dynamic-modifier comment. The Spreading Cult's founding strength (`mltd_cult_gain = 20` in the
  focus) is repeated as a literal in `mltd_spreading_cult_founds_tt`; change both. The category
  description quotes none of these numbers. **The Wet Market** (`mltd_the_wet_market`,
  Kingdom-relative (1,2), round 14). OWB's *Organization Marketplace* sellers are not countries but
  five organisations - Gun Runners, Chop Shop, Van Graffs, Butcher Pete's and Vancouver Mavens,
  renamed by region through OWB's `Get*RunnerName` scripted loc - held per country as indices 1-5
  in the array `country_organizations` (`organization_scripted_effects.txt:81-113`). No country
  opinion modifier reaches them (OWB's own node opinion modifiers are defined but never used). So
  the focus uses OWB's idiom, Eagle Rock's (`Eagle Rock (EAG) Focus.txt:3215-3221`):
  `org_influence_amount = 40`, then a `for_each_loop` over `country_organizations` with
  `org_selector = v` calling `organization_add_influence`, which clamps influence to [-100, 300].
  Influence lowers prices by 0.04 % a point and opens purchase tiers. The array only exists with
  the caps rule on, so the loop sits behind `has_global_flag = caps_enabled_global_flag` and pays
  +50 PP otherwise. The idea `mltd_the_wet_market` is permanent: +20 % `caps_income_modifier`
  (multiplies every caps income entry) and a `consumer_goods_factor` penalty (scales the economy
  law's base). The 40 is repeated in `mltd_the_wet_market_orgs_tt`; change both. The idea's +20 %
  multiplies caps *income entries* only (`caps_scripted_effects.txt:386-395`); OWB adds the flat
  currency income after it (`:396`), so the bonus bites only on node income, exports and subject
  taxes - since round 17 chiefly the Kingdom's node at M'lyeh (~3.4 caps a tick at level 0, ~17 at
  level 3; promotion is OWB's button in the state view). *The seller* (round 16). The focus also
  opens **The Wet Market** as a seller in OWB's Organization Marketplace (`trade_ledger_window`).
  It is not a sixth OWB organisation - that would mean overriding OWB's 1,883-line
  `_organization_scripted_localization.txt`, which East Coast Rebirth and Rustbelt Rising already
  override - but two child scripted GUIs of OWB's window (`parent_window_name`, OWB's own precedent
  at `_organization_market_gui.txt:5`) in new files, `common/scripted_guis/mltd_wet_market_gui.txt`
  and `interface/mltd_wet_market.gui`:
- *The button* sits in the fourth slot of the seller bar's second row (free until OWB has eight
  sellers; it has five). It sets our own `mltd_wm_selected` and clears OWB's
  `selected_market_organization` and item list. Everyone sees it once the market is open; MLT also
  sees it before, with every item locked. Its tooltip has the shape of OWB's seller tabs
  (`organization_ledger_opinion_tt`): *Market Open* (`GetMltdWmMarketOpen`, the focus's global
  flag) in place of OWB's opinion, and *Available for transaction* (`GetMltdWmAvailability`, the
  trade cooldown with the days remaining), reusing OWB's `org_available` for the yes branches.
- *The panel* covers OWB's item list while `mltd_wm_selected` is set and no OWB seller is, so
  selecting an OWB seller hides it; closing the window keeps our selection, so the panel is back
  when the window reopens. (A first draft stored 99 in OWB's `selected_market_organization`
  instead, which OWB's organisation events would have read back as an organisation index - see
  Gotchas.) Four rows, one per mirelurk variant - `amphibious_beast_equipment_1` / `_2` / `_armor`
  / `_king` (a lot of 250 each, priced at OWB's own caps-per-IC rate; a smaller lot was tried and
  reverted), delivered with `producer = MLT`. Each row copies OWB's `trade_ledger_entry` element
  for element: the icon in the dark 150x45 inset, *In Stock*, a *Requires: The Wet Market* line
  (green or red, `GetMltdWmRequirement`) where OWB's rows show *Minimum Opinion*, and stacked *Buy
  For* / *Sell For* buttons in OWB's price colours (`§G..k§!` / `§R..k§!`). The first version drew
  the icon unboxed and oversized, had one centred buy button with a caps icon and a header text
  box, and looked nothing like OWB's rows in game.
- *Conditions* (`mltd_wet_market_can_buy`, one OWB-style tooltip line each): the global flag
  `mltd_wet_market_open`, which the focus sets ("[MLT.GetNameWithFlag] has completed The Wet
  Market"); the caps (`caps_cost_trigger`); at least 250 in the global stock
  `global.mltd_wet_market_stock` (1,000 when the focus completes, +250 each month from
  `on_monthly_MLT` while MLT exists and the stock is below 2,500); and no recent trade
  (`mltd_wet_market_recent_trade`, a timed flag shared by buying and selling).
  `mltd_wet_market_pay` pays through OWB's `transaction_caps`. Selling a lot back pays OWB's base
  share of its buy price and needs the market open, no recent trade and 250 of that variant
  (`mltd_wet_market_can_sell` plus the row's `has_equipment`); the 250 go into the stock
  (`mltd_wet_market_receive`), which sales may push past 2,500.
- *Left out*: opinion tiers, discounts and other countries' AI buyers (OWB's AI trades only with
  sellers 1, 2 and 4); an AI MLT buys through `on_weekly_MLT` (see MLT's AI). Each buy price is a
  literal in its button's trigger and effect (`mltd_wet_market_gui.txt`), in `mltd_wm_buy_<n>_text`
  and in that AI buyer; each sell price in its effect and in `mltd_wm_sell_<n>_text`; change them
  together.

**MLT's AI** (round 18). An AI MLT follows `CONQUEST_PLAN.txt` broadly and adapts where a game
drifts from it; Project says how the two are kept in step. It lives in new files - the five AI
files, which need load-after-OWB because OWB `replace_path`s their folders, and the conquest-stage
triggers - and in `ai_will_do` / `ai_chance` weights in our own files. OWB's global AI still
applies to MLT on top: its generic unit and production strategies, its caps division limiter after
2280 (creature roles are exempt) and its generic operations.

- *Fair play* (the rule every AI change follows): the AI gets nothing a human player would not. It
  is steered only through preferences - `ai_strategy`, strategy plans, templates, `ai_will_do` /
  `ai_chance`, peace desires, scorers - and through the same actions a human can take, at the same
  cost and under the same conditions (the Wet Market buyer and the cult operations run the player's
  own triggers and prices). No AI-only effect may give it claims, cores, war goals, units,
  equipment, manpower, political power or caps, or skip a cost; round 19's war driver, which handed
  an AI MLT claims and war goals, was removed for exactly this. A change that would alter other
  countries or the human game (a global define, a new mechanic both sides use) is the user's call,
  not a tuning step.

- *Focus order* (`common/ai_strategy_plans/mltd_MLT.txt`): three chained plans - the Oregon opening
  until `mlt_kingdom_of_mlyeh`, the Kingdom and the Books until `mltd_the_final_ritual`, then the
  late game - each plan's `abort` the next one's `enable`, all three off while MLT is a subject.
  `ai_national_focuses` is the plan's focus order; the engine takes the first available entry, so
  the `lurk_` and `mlt_` fillers at the end run while a conquest, egg, Book or population gate
  holds everything above them. The claim focuses (Expanding M'lulu's Domain, Cascadian Current, Sea
  of Cortez, Tropic of Cancer) gate an AI on `mltd_ai_may_press_claims` (round 20) instead of OWB's
  `ai_has_no_other_wars_or_wargoals`, which asked for peace and no war goal: an AI MLT may take
  them while it is not losing (surrender progress 15 %), holds no war goal against a country it is
  not at war with, and has no enemy it can still fight - each has capitulated or is cut off. Humans
  were never gated. `focus_factors` zeroes the Muttfruit trades (they spend the capital's water)
  and Defensive Mindset, and nothing else - though whether a zero there actually holds a focus is
  untested (*The AI* under The story acts), so nothing load-bearing rests on one. Since 2026-09-25
  owning Cannibal Territories no longer bypasses the first trade by itself, nor can it be bypassed
  once the Barrows are dug: run 8's AI dug them on day 322, had the trade bypassed on day 1792, and
  then took the Muttfruit branch's focuses as well (Gotchas > *A bypass fires by itself*). Whether
  an AI ever bypasses a focus by hand is unverified; the plan lists the Barrows, so it has no cause
  to. Until round 27 the second plan also zeroed every conflict capstone but WBH's, because each
  started a war years before its stage. In the story acts each chapter waits for the previous close
  and each war focus holds itself (The story acts > *The AI*). The Kingdom-and-Books plan takes Act
  II's Broken Coast branch after The Grand Ritual and OWB's claim focuses (after the Walk until
  2026-09-24), then Act III - since 2026-09-24 before The Deep Ones Walk and The Final Ritual,
  which it takes the day each opens - the three invitations first, each after the Act II branch it
  hangs off (Terms for the Citadel after the other two, round 28), and the three wars after them,
  The Coast Goes Under last (round 28c). The late plan lists the acts in order, with The Dreamer
  Wakes as its ending, what the north has left before The Turbines Sing and its wars after, and
  each spoils group after the next act's war focuses (The story acts > *The AI*). Each plan also
  weights technology categories (industry, electronics, creatures and amphibious units, Outsider
  Warfare over its four rival doctrine roots; naval and air down, because OWB inflates a naval
  tag's naval weights) and advisors by idea token.

- *Conquest* (`common/ai_strategy/mltd_MLT.txt`, section B): one block per target,
  `mltd_ai_conquer_<tag>`, on while the target exists and is neither MLT's subject nor in its
  faction, and: MLT is already at war with it; or its stage has come - the previous target gone or
  at war with MLT, a focus, or a fallback date that only unsticks a stalled game - and it is a safe
  target (`mltd_ai_safe_target`: not on the NCR's side before the NCR's stage, and no ally -
  faction member, overlord or subject - at half MLT's estimated strength); or the frontier calls
  for it (*When the game drifts*). Each stage is a scripted trigger, `mltd_ai_stage_<tag>`
  (`common/scripted_triggers/mltd_ai_triggers.txt`). Each stacks `conquer`, `antagonize`, a large
  `consider_weak` (OWB's `DECLARE_WAR_RELATIVE_FORCE_FACTOR` lets relative force dominate the
  decision to declare), `declare_war` (it acts only once a war goal exists, i.e. a justification;
  the story acts' war focuses declare their wars themselves), `front_unit_request` and, on each
  stage's main target, `prepare_for_war`. The stages are the plan's: CCW from day 0; TRL, RBT and
  MDT, each from the war before it; PMR and ARR (Books 5 and 4) after the Kingdom - ARR only while
  it stands apart from the NCR; the Oregon ring (TIM, KLA, TCA); Cascadia (WBH first) once MLT
  holds enough states and The Grand Ritual is done (The Deep Ones Walk until 2026-09-24, when the
  Walk moved below Act III: The Tide-Wall, an AI's usual road through Act III, needs this stage,
  and the Walk now needs Act III); MXS, FOU and TDN, from The Grand Ritual as well, the stepping
  stones to the NCR (an OWB AI may justify only on a neighbour,
  `diplomacy_scripted_triggers.txt:1210-1216`); New Reno, when Vault City, Elko or S'Lanter stands
  on the NCR's side and New Reno does not (its land is the only way to them); the NCR, MOT, NAT and
  SHI (which borders only the NCR and NAT) after The Final Ritual, once the Broken Coast has had
  its volunteers (`mltd_ai_brk_helped`, round 21), the north is consolidated (`mltd_ai_north_done`,
  set by the weekly survey while MLT owns more than 70 of the north's 79 states or none is left to
  a safe target), the NCR's cult stands at 40 % (`mltd_ai_ncr_cult_ready`) and New Reno is out of
  the way (`mltd_ai_new_reno_first`) - or from 2284; the Legion and the interior once the NCR is
  beaten (`mltd_ai_ncr_beaten`: gone or capitulated - a capitulated country stays at war while an
  ally holds out); Texas, Mexico and the north once the Legion is (`mltd_ai_legion_beaten`). Since
  round 27 both triggers also count a capitulation to MLT at any time (the flag `on_capitulation`
  records) and a subject. They are the gates of Act IV's and Act V's closes, so each stage opens
  with the act that follows. The stages' 2283 and 2286 fallback dates only let the conquest blocks
  justify; the tree's Act V and VI wars still wait for the closes. From Cascadia on no stage opens
  while The Final Ritual runs, and a war goal alone never opens one. `mltd_ai_hold_late_wargoals`
  and `mltd_ai_hold_south_wargoals` veto declaring on a war goal from anywhere else (a
  justification, an OWB event) before its stage - the interior's until the NCR is beaten, the
  south's until the Legion is (a negative `declare_war`, vanilla `GER.txt:2175-2189`).
  `mltd_ai_hold_ncr_side_<tag>` holds each of the 29 countries OWB can bring into the NCR's faction
  while it stands on the NCR's side (`mltd_ai_in_ncr_bloc`: faction, subject or guarantee) and the
  NCR's stage is closed: `ignore_claim`, because claims drive OWB's AI justification, and a
  negative `declare_war` (run 2 declared on Arroyo, a member, in 2279 and fought the NCR's faction
  for six years). `mltd_ai_stay_on_plan` (`avoid_starting_wars`, targetless and added to every
  `conquer`) keeps every country outside the open stages below zero until The Final Ritual, and
  `mltd_ai_no_new_wars_when_losing` stops new wars while MLT is losing one.

- *When the game drifts*: a target that dies, or a war that starts early, moves the next stage on
  at once. DIS offers itself (OWB's `nf_dis.4`) only while it holds `DIS_mend_schism`, which OWB
  sets for an AI MLT only on a random roll, and a war with MLT cancels the offer:
  `mltd_ai_spare_dis` forbids that war while the offer can still come, and `mltd_ai_conquer_dis`
  takes DIS by force after RBT once it cannot (no flag, `lake_preemptive_defenses`, or the fallback
  date). `mltd_ai_guard_the_warren` mans the WBH front as soon as WBH justifies on, holds a war
  goal against or fights MLT (WBH's claim on The Warren, see Gotchas). The frontier
  (`common/ai_strategy/mltd_MLT_frontier.txt`, round 20) follows the map rather than the plan: a
  country that holds land of the north once the Kingdom stands becomes a target (run 2 lost the
  Oregon ring to MOD, BDT and SYN), and so does one that stands between MLT and an enemy MLT cannot
  reach (`mltd_ai_cuts_off_an_enemy`; the survey's flag `mltd_ai_pocket`) once 90 days of
  military-access requests (`mltd_ai_access_<tag>`, `diplo_action_desire`, OWB's own idiom at
  `CYC.txt:23-33`) have not opened a way - both only against a safe target
  (`mltd_ai_frontier_target`). Its conquest candidates are the 55 countries without a stage that
  border the north or the NCR's possible side at game start, or can join that side; access is asked
  of every target past the Oregon opening. Run 2's NCR war never ended because Vault City, Elko and
  S'Lanter held a pocket touching only New Reno, EAS, BDT and Ouroboros. At war
  `mltd_ai_every_front` asks for troops on every enemy's front and pushes on enemies under half
  MLT's strength (run 2 left Baja's front unmanned for a year after the NCR fell). A Book whose
  owner is not a safe target - Arroyo on the NCR's side, The Maw behind a strong ally - is read
  through a full intelligence network in its state instead (`mltd_ai_book_network_arr` / `_pmr`, La
  Resistance).

- *The army* (`common/ai_templates/mltd_MLT.txt` and section A): five roles, all
  `available_for = { MLT }` - `mltd_coral_host` (mirelurks and infantry), `mltd_shell_levy` (one
  mirelurk and militia, the egg ritual's manpower sink), `mltd_tide_wall` (M'lulu's Clutch until
  The Deep Ones Walk, then the all-mirelurk Tide Wall), and `mltd_deep_ones` / `mltd_star_spawn`,
  whose targets are exactly the scripted templates, so a summoned division is a full match.
  `role_ratio` (`mltd_ai_unit_mix*`) cancels OWB's generic infantry and marines for MLT (a role's
  share is 100 plus the values, so -137 and -115, and `build_army -999` stops those two and OWB's
  motorised and mechanised roles), trims its amphibious-beast ratio and switches our roles on as
  their tech or focus arrives; the weekly survey sets the army's size, `mltd_ai_army_target`, from
  the frontage (round 21): half the combat width of every border province at peace - two divisions
  an 80-wide tile - and three quarters at war, at least 12. Script sees no provinces, so
  `build_ai_frontage.py` measures each state once from OWB's map into
  `common/scripted_effects/mltd_ai_frontage_effects.txt` (`mltd_ai_edge`, the divisions filling its
  provinces that touch another state, and `mltd_ai_nbs`, its neighbouring states), which the survey
  writes to the states once a game and reads as `mltd_ai_edge` x foreign neighbours / `mltd_ai_nbs`
  (run 3's save: 343 estimated against 400 measured); below the target `mltd_ai_army_short` raises
  `ai_wanted_divisions_factor`, a quarter above it (`mltd_ai_army_cap`) `mltd_ai_army_full` lowers
  it, stops training the line roles and spends army experience on templates (run 2's AI, left to
  the engine's factory-weighted count, held 402 divisions on 57 border states; run 3's, at two a
  border state, stopped at 51 on 100 border provinces and lost to Broken Coast); until the late
  army `mltd_ai_unit_mix_line` puts the factories on infantry weapons, cancels OWB's
  amphibious-beast role and leaves the Tide Wall role to `mltd_ai_unit_mix_late`, while Shell
  Levies (`role_ratio` 200) and Coral Hosts hold the line and the summons still raise Deep Ones and
  Star Spawn; once the NCR is beaten and the king or armour form is researched
  (`mltd_ai_late_army`), the Coral Host and Shell Levy roles target 8 mirelurks and upgrade their
  divisions in the field (`can_upgrade_in_field`, `replace_with`);
  `equipment_production_factor infantry` undoes OWB's cut, which hits creature equipment too (every
  creature archetype is `type = infantry`). `research_tech` forces the plan's techs - the mirelurk
  line by date, to stay clear of the ahead-of-time penalty - and from The Final Ritual on
  `mltd_ai_research_king_form` weights the king form over the armour form (they are XOR and share
  every category, so a plan's `research` block cannot choose).

- *The opening's order, and the enemy's other wars* (round 23, section B0): run 6 held a war goal
  on The Warren from day 630 while TRL fought Medford, and declared on Medford first.
  `mltd_ai_strike_<tag>_at_war` adds `declare_war`, `consider_weak` and `prepare_for_war` on a
  target that is already at war with a third country while MLT holds the war goal and is not at war
  with it; `mltd_ai_opening_order_trl` / `_rbt` push the later opening targets' `antagonize` below
  OWB's `MIN_ANTAGONIZE_FOR_WARGOAL_JUSTIFICATION` (-1000) while an earlier one stands unfought, so
  the AI stops fabricating on Medford before The Warren is settled. The engine still owns the final
  call - a declaration is a weight comparison, not a script - so the order is a preference, not a
  guarantee.

- *Anti-tank* (round 23): MLT holds `support_tech_level_tribal` from game start, so
  `anti_tank_equipment_tech_1` (2276) and `anti_tank_tech_1` are two cheap techs that open the
  `anti_tank_company`; `mltd_ai_research_anti_tank` forces both, and every line role carries an
  anti-tank variant behind `enable = { has_tech = anti_tank_equipment_tech_1 }`
  (`mltd_coral_host_at`, `mltd_shell_levy_at`, and the late all-mirelurk templates). Without
  piercing, militia, infantry and mirelurks alike bounce off OWB's power armour.

- *The war focuses declare* (round 22): every war focus - a conflict capstone until round 27 -
  starts its war itself, so no AI can sit on a war goal (run 5 held one on The Warren and one on
  Arago for months). Each is unavailable to an AI while its war would come too early, through a
  hidden AI-only trigger in its `available` (round-27 review; until then an `ai_will_do` modifier
  reading 0, which run 8 showed is no hold) - see The story acts > *The AI*.

- *Ready before the war, militia first* (round 22): run 4 took The Tide-Wall's war goal on the
  Washington Brotherhood and declared seven days later with 35 divisions against a target of 78,
  its armies elsewhere, while it was 200 days into a manual justification on Eureka. From the
  Kingdom on, `mltd_ai_not_ready_for_war` discourages a new war (`avoid_starting_wars` -200 against
  OWB's war-goal base of 500) while the army is under the readiness line - half the survey's
  target, capped at 20 divisions, so the early wars the plan fights with a dozen divisions still go
  ahead (`mltd_ai_army_ready` / `mltd_ai_army_ready_at`); under that half `mltd_ai_army_very_short`
  doubles the wanted-division push and keeps the factories on infantry weapons;
  `mltd_ai_unit_mix_fill` puts the Shell Levy (militia) ahead of the Coral Host until the target is
  met, and the levy's first target template is **pure militia** (`mltd_shell_levy_militia`, until
  200 mirelurks are in stock) because every earlier template asked for a mirelurk - run 5 sat on
  4,000 infantry weapons and 9,000 manpower without raising a division; and every frontier conquest
  now carries `prepare_for_war`, as the staged ones do, so the army moves to that border first.
  Justification itself is the engine's: its length scales with MLT's own production and rises 1.5x
  per war or justification already running (vanilla `WARGOAL_JUSTIFY_TENSION_FROM_PRODUCTION`,
  `WARGOAL_PER_JUSTIFY_AND_WAR_COST_FACTOR`), and claims do not shorten it - they lower the tension
  bar and the annexation's threat.

- *The Bone Dancers* (round 22): while the invitation can still be made - since round 28c's balance
  review that is the invitation's own rival gate, BDT not sworn to Heaven's Guard's seraph lords
  (`bdt_listen_to_the_pilgrims`) and MLT not allied to Heaven's Guard, in place of round 22's wait
  on OWB's Odious King (`bdt_hail_to_the_king`, or neither of the two focuses that ruled it out),
  which an AI BDT crowns only on its own behaviour roll - and BDT has neither refused the Covenant
  nor been chosen for Drown the Dance, `mltd_ai_courting_bdt` keeps it off `mltd_ai_safe_target`
  and `mltd_ai_court_bdt` ignores its claims, vetoes a declaration and befriends it; the plans list
  the invitation before the war focus, and Drown the Dance is unavailable to an AI while the
  courtship holds, so the AI takes Hail the Drowned King when it can and fights when it cannot.
  Since round 28b the two exclude each other both ways: once Hail is taken the war can come only
  from a refusal's war goal (*The invitations' war goals*). Since the round-27 review
  `mltd_ai_network_bdt` and `mltd_ai_infiltrate_bdt` build their network and take their civilian
  token, as the plan does, so Hail's gates are reachable, and since round 28c's balance review they
  rest on nothing but MLT's own work and the pilgrims' rule. The courtship holds the war only until
  2281 (`mltd_ai_may_drown_the_dance`). Since round 28c's review the courtship also ends once Hail
  has completed without sending its offer (`mltd_bdt_covenant_lapsed`), and pauses while the Bone
  Dancers are another country's subject.

- *The Broken Coast* (round 21): run 3's AI declared on Broken Coast, 47 states, and lost to it.
  From the Kingdom on an AI MLT courts it instead - since round 28c the raiders are courted first
  and fought only by choice (`mltd_ai_courting_brk`: BRK exists, at peace with MLT, not in its
  faction, no `mltd_brk_refused_covenant`, since round 28 no alliance with the Brotherhood in
  Washington, `mltd_wbh_alliance`, and since round 28c The Coast Goes Under not taken - each of the
  last two closes the Covenant for good, and a courtship resumed after a war with BRK would
  otherwise never end): `mltd_ai_safe_target` refuses BRK, so neither its stage nor the frontier
  opens a war on it and the north counts as consolidated without its land; `mltd_ai_court_brk`
  ignores its claims, vetoes a declaration and befriends it; `mltd_ai_network_brk` builds a network
  there (below the Book networks) and `mltd_ai_infiltrate_brk` runs OWB's
  `operation_infiltrate_civilian` for the Covenant's civilian token (round-27 review), both at the
  player's own cost; the weekly on_action points the cult operations at BRK while its cult is under
  60 % (not over the NCR's before the NCR's cult reaches 40 %); and the Kingdom-and-Books plan
  takes Act II's Broken Coast branch first, right after the Walk, and the Covenant first in Act
  III. The raiders are helped before the NCR: the NCR's stage also needs `mltd_ai_brk_helped` - 26
  weeks with at least four of MLT's divisions volunteering in BRK (`mltd_ai_brk_volunteer_weeks`,
  counted by the weekly survey through `has_volunteers_amount_from`), or no courtship, BRK at
  peace, capitulated or holding its coast (`brk_nf_pirate_coast`), the Covenant taken, or 2283 -
  and `mltd_ai_help_brk` sets `send_volunteers_desire` on BRK while it fights, MLT is at peace and
  The Deep Ones Sail North is done. A BRK war on MLT, a refusal or BRK in MLT's faction ends the
  courtship. Since round 28c's review it also ends for good once the Covenant can never be offered
  again - completed on its +50 PP fallback without sending the offer (`mltd_brk_covenant_lapsed`),
  or the raiders once sworn to it (`mltd_brk_covenant_joined`) - and pauses while BRK is another
  country's subject (the Covenant cannot be offered to one); a bare `has_completed_focus` would end
  it the day the Covenant completes, before BRK answers, and let the AI offer Terms for the Citadel
  into that answer. The weekly cult-target override stops pointing at BRK once the Covenant is
  taken. Since round 28 an unhistorical AI Broken Coast refuses the Covenant half the time, so the
  courtship can end in a refusal against an AI too. The Covenant's war twin, The Coast Goes Under
  (round 28c), is held for an AI while the courtship lasts, with no date
  (`mltd_ai_may_drown_the_coast`: also the army ready, MLT not losing, BRK a safe target and no NCR
  war running); a refusal has already excluded it, and the AI offers Terms for the Citadel, whose
  acceptance would end the courtship, only once the courtship is over - so in practice an AI takes
  the twin only as a payout in a war the raiders already fight with MLT, and never starts that war
  with it (a `# AI deviation:` line in the plan).

- *The invitations' war goals* (round 28): every refusal hands MLT - an AI one too - an
  `annex_everything` war goal on the refuser for a year (The story acts > *The invitations*). A war
  goal is enough for OWB's AI to declare at once (run 4), a declaration on one skips every conquest
  block's safe-target test, and the refusal also ends the courtship whose -1000 was the only veto
  (`mltd_ai_court_brk`, `mltd_ai_court_bdt`). So `mltd_ai_hold_refusal_wargoal_brk`, `_bdt`, `_wbh`
  and `_tca` (section C2) veto that declaration (`declare_war` -1000) while MLT holds such a war
  goal and the war is not one its own gates would allow: the hold on that nation's war twin - for
  the Broken Coast The Coast Goes Under's (`mltd_ai_may_drown_the_coast`, round 28c: the army
  ready, not losing, a safe target, no NCR war) together with its stage (`mltd_ai_stage_brk` - run
  3 declared on the 47-state Broken Coast and lost); for the Bone Dancers Drown the Dance's
  (`mltd_ai_may_drown_the_dance`); for the Brotherhood The Tide-Wall's
  (`mltd_ai_may_raise_the_tide_wall`). Since rounds 28b and 28c each invitation and its twin
  exclude each other, so after a refusal the twin is closed for good, but its hold still says when
  the war may start. Each lasts at most the year. The Brotherhood has a block per tag, so that a
  war goal on a plain TCA from anywhere else is left alone. Terms for the Citadel itself waits on
  `mltd_ai_may_offer_the_citadel` (The story acts > *The AI*), so an AI makes the offer only on
  unhistorical focuses, only to WBH itself, only once the Covenant is off the table (no courtship
  of the Broken Coast: the raiders have refused it, are at war with MLT or are gone), and only when
  the war after a no could be fought. While that offer is still to come (`mltd_ai_terms_pending`,
  which since 2026-09-24 starts with The Grand Ritual, when Act II opens, and since round 28b also
  ends once The Tide-Wall is taken, since the wall closes Terms), `mltd_ai_hold_wbh_for_terms`
  keeps the Washington conquest block from justifying on WBH (`antagonize` below OWB's -1000
  justification floor, as `mltd_ai_opening_order_trl` does) or declaring on a war goal already
  held, since a Brotherhood at war with MLT can be offered nothing; once Terms is taken the hold
  lifts. Since round 28c's balance review Terms has intelligence gates of its own, so
  `mltd_ai_terms_pending` also turns the Order on Washington while the offer is still to come, in
  the shape of the other two courtships: `mltd_ai_network_wbh` builds the network there,
  `mltd_ai_infiltrate_wbh` runs OWB's `operation_infiltrate_civilian` for the civilian token, and a
  third branch of the weekly cult-target override points the cult operations at WBH while its cult
  is under 50 %, behind the Broken Coast's and the Bone Dancers'. All three are WBH only - an AI
  never offers Terms to the Northwestern Brotherhood - and all at the player's own cost. The two
  Brotherhoods' strikes (`mltd_ai_strike_wbh_at_war` / `_tca`, section B0) never fall on an ally in
  the Covenant, nor on a refused Terms' war goal before The Tide-Wall's own hold would allow that
  war (their +600 would otherwise outweigh the refusal holds), and WBH's also waits while Terms is
  pending. An accepted Terms ends the Broken Coast's courtship for good (`mltd_ai_courting_brk`).
  And the weekly survey's north-consolidated test now skips a country in MLT's faction: a
  Brotherhood or Broken Coast in the Covenant holds northern land without being a target. Since
  2026-09-25 WBH may be asked while it leads the Northern League, so `mltd_ai_terms_pending` -
  which until then never held in a game where WBH stood in its league, almost every game - holds on
  unhistorical focuses from The Grand Ritual until Terms or The Tide-Wall is taken, and an accepted
  Terms brings the league's members into the Covenant, off every target list.

- *Decisions and events*: `ai_will_do` on the gifts (at war, with manpower to spare), the summons
  and the offerings (each guarded so that the AI never pulls the population back under the next
  ritual's gate; after The Final Ritual the Drowned only with caps under 50, and the Tides and -
  since they no longer retire (2026-09-23) - the two land summons only over 300,000 people - run 2
  made 39 offerings after it) and the Calls (equipment always, people only when short); from the
  Kingdom on, `pp_spend_amount` / `pp_spend_priority` save political power for decisions (OWB's
  `ARR.txt` idiom). `events/nf_mlt.txt` weights the plan's picks in `nf_mlt.1-3`, and in the Book
  expeditions (202, 302, 502) the AI avoids killing a hired advisor (`is_hired_as_advisor`, vanilla
  `AST.txt:1813-1816`).

- *Cults and the market* (`on_weekly_MLT`): with La Resistance, an agency and *The Spreading Cult*,
  an AI MLT stores a cult target in `mltd_ai_cult_target` through `get_highest_scored_country` and
  `common/scorers/country/mltd_ai_cult_target_scorer.txt` (OWB's `update_operation_ai` pattern,
  `operation_strat_effects.txt:5-24`; majors, neighbours, sheltered and existing cults score
  higher, the NCR six times from The Deep Ones Walk on so that its cult stands before its war, and
  a country already at war with MLT a quarter, because war triples a cult's decay), and
  `mltd_ai_cult_found` / `mltd_ai_cult_nurture` run *Found a Cult* on it while it has no cult and
  *Nurture the Cult* while its cult is under 100 %, ahead of OWB's generic operations (one
  operation per block, switched on by that operation's own condition, as vanilla's are). Three
  overrides follow the scorer, in order, because an invitation's cult gate is a target the scorer's
  own arrays seldom reach: the Broken Coast, then the Bone Dancers, then - since round 28c's
  balance review gave Terms for the Citadel the same gates - the Washington Brotherhood while
  `mltd_ai_terms_pending` holds. Each waits for the NCR's own cult first, from The Deep Ones Walk
  on. Their `ai_will_do` must stay above `OPERATION_AI_MINIMUM_SCORE`, or the AI scraps what it
  prepares. The same on_action buys the line's weapons (round 21, `mltd_ai_buy_line_equipment` in
  `mltd_ai_survey_effects.txt`): from Butcher Pete's the best melee weapon its influence opens and
  from the Gun Runners support equipment or the best ballistic weapon or pipe guns, while it holds
  under 2,000 infantry weapons (300 support), through exactly the player's buy button (OWB
  `__trade_ledger_gui.txt:56-217`: discount, opinion tier, stock, the 40-day
  `recent_transaction_with_<n>` flag, `transaction_caps`, influence) - OWB's own AI buyer never
  buys with negative caps income, which MLT's army always gives it. From the late army on, it buys
  one Wet Market lot - the GUI is `is_ai = no` - of the best variant it has the tech for, with caps
  in hand and OWB's AI caps floor left after paying - not OWB's positive-income test: army upkeep
  turns MLT's caps income negative, while the Drowned Hoard's caps, which are not income, fill the
  purse. *Indoctrinate the Faithful* gets no strategy: manpower is not MLT's bottleneck (a
  `# AI deviation:` line in the plan). With La Resistance and an agency, `mltd_ai_save_for_castro`
  holds political power back from our decisions until Old Castro is hired and raises the spending
  priority of his slot, `pp_spend_priority id = cultural_advisor value = 200` (since round 28c's
  balance review his `ai_will_do` is 10003, OWB's own weight for an advisor it means to guarantee,
  because a plain 100 sat under vanilla's `CRITICAL_IDEA_PRIORITY` and no run ever hired him; the
  plans' `ideas` 60). Until 2026-09-24 he was MLT's only cultural advisor, so the weight chose
  whether to spend at all, not between candidates. The Tide-Speaker (-30 % justification time,
  hireable from the Kingdom) now stands beside him: his 10003 against her 100 puts him first when
  both can be had, and `mltd_ai_hire_tide_speaker` raises the same category (to 100) for her only
  once he is in post, or from the Kingdom where there is no La Resistance and so no Old Castro; the
  plans' `ideas` give her 40. **Each advisor slot is a political-power category of its own, named
  after the slot** - vanilla hires navy chiefs with `id = navy_chief` (`JAP.txt:2697-2701`,
  `USA.txt:1674-1678`), and `navy_chief` is declared exactly as `cultural_advisor` is, a
  `character_slot` in `common/idea_tags`. No run hired him until this was known: run 2 and run
  `20260917-212246` (853 political power banked) never raised the category at all, and round 24
  raised `idea` instead, which is not his - run `20260918-170847` then spent its power on other
  ideas and a military advisor and never held the 150 he costs. He was MLT's only civilian advisor,
  so no run had shown a civilian hire working for this AI. unverified: that `cultural_advisor` is
  accepted as a `pp_spend` id (no vanilla or OWB file uses it; `navy_chief` and
  `supportive_scientist` are the precedent).

- *Peace* (`common/peace_conference/ai_peace/mltd_MLT_peace.txt`): negotiating for itself, MLT
  wants states and refuses puppets - the ritual gates, the summons and the Books count only what it
  holds.

- *Telemetry* (round 19): while MLT exists, `common/scripted_effects/mltd_telemetry_effects.txt`
  writes one-line records to `game.log` with the `log` effect. Its own
  `common/on_actions/mltd_telemetry_on_actions.txt` hooks it (on_actions merge across files, so it
  adds to ours rather than replacing them), and the kill switch `mltd_telemetry_on`
  (`common/scripted_triggers/mltd_telemetry_triggers.txt`) silences it. Each line is
  `MLTD <day> <KIND> key=value ...`, where `<day>` counts days from 2275-01-01 (`mltd_tm_day`, +1 a
  day): START once (AI or human, La Resistance, the caps rule, DIS's schism flag); a monthly SNAP
  (states, population in thousands, manpower, divisions, factories, caps, political power,
  stability, war support, Books, cults and the cult target, subjects, enemies, equipment) with one
  CULT line per cult; and weekly first-seen lines for every focus MLT can take, the plan's and the
  AI's techs, the conscription law, justifications, war goals, wars (start and end), the fall of
  each of the AI's conquest targets (with the owner of its last capital), the rituals, the cooldown
  decisions, the gifts and Wet Market trades. Round 20 adds a monthly ENEMY line per enemy
  (capitulated, the states it controls, whether its land touches MLT's), the survey's border
  states, army target and northern states and the agency's operatives and slots to SNAP, and weekly
  first-seen STAGE lines (each conquest stage, and `id=north` for the north consolidated), POCKET
  lines (an enemy out of reach: start and end) and ADVISOR lines (each of MLT's advisors first
  hired). Round 25 adds HAIDA lines, `state=landed` and `state=pushed_off` (the Broken Coast's
  landings on Haida Gwaii, and the white peace that follows) - written by `on_daily_MLT` in
  `mltd_on_actions.txt` rather than by the generated file, so they are not in that file's header
  list of kinds; `ai_run_report.py` knows them. It changes nothing else: every flag and variable it
  writes is `mltd_tm_`. The long lists are generated: `python build_telemetry.py` rebuilds the file
  from the focus tree, the plan, MLT's AI and OWB, checking every id, and `check_plan_sync.py`
  fails when the telemetry misses a focus, tech or conquest target the plan or the AI uses. After a
  spectator run (Testing), `python ai_run_report.py` prints the run against the plan - focuses,
  wars, annexations and snapshots with their deltas, the AI's timeline, the enemies it fought, and
  seventeen automated checks that each name the strategy block to look at - and `--save` archives
  the report and the raw lines in `ai_runs/`, one row per run in `ai_runs/runs.csv`, so iterations
  can be compared. The report calibrates its days on `game.log`'s own dates. Unverified until the
  first run: whether `game.log` gets the lines without `-debug`; how `[?x|0]` rounds and whether it
  groups thousands; whether `manpower_k` is the pool the top bar shows; `num_equipment@<archetype>`
  across every variant; a state id through `GetID`; and the order of the daily, weekly and monthly
  pulses within a day.

- *Unverified* (each marked unverified in the files; watch them in the AI runs): how far `conquer`
  alone moves the AI to justify - run 1 never justified, run 2 justified where claims or a
  neighbour's border let it (MDT, Arroyo) - and no fix may give it claims or war goals a human
  would not have (Testing, AI spectator runs); that the holds' negative `declare_war` outweighs
  OWB's war-goal base and relative-force term (vanilla and our DIS veto use a larger one); that
  plain `get_highest_scored_country` leaves a lasting variable, unchanged when no country scores;
  whether `research_tech` weighs the ahead-of-time penalty (hence the mirelurk line's dates); what
  negative `research` weights do; `equipment_variant_production_factor` on a modded archetype; that
  the AI trains the scripted Deep Ones / Star Spawn templates for their roles. Round 20 adds:
  `ai_wanted_divisions_factor`'s unit (read as a percentage change) and `build_army` on our roles;
  `front_unit_request` and `front_control` with a `country_trigger` on every enemy; that
  `diplo_action_desire` with `military_access` makes MLT ask, and what a refusal does; that
  `strength_ratio` on a target's allies judges a faction the way a player would; that the AI
  field-upgrades a role's divisions into a different composition (`can_upgrade_in_field` with
  `replace_with`); that the AI's network grows in the state an `operative_mission` names; and the
  weekly survey's cost. Round 21 adds: that `mltd_ai_buy_line_equipment` runs OWB's
  `calculate_deal_percentage` and `get_minimum_organization_opinion` outside the GUI as the buy
  button does, and that the survey's state variables survive a load; that `strength_ratio` against
  ROOT judges a stronger target the way run 3 needed; `send_volunteer_size` from a variable-backed
  dynamic modifier outside OWB's Brotherhood, and `send_volunteers_desire` against OWB's distance
  and major-power terms; `has_volunteers_amount_from` counting divisions;
  `create_faction_from_template` from a template in our own file; `befriend`'s weight; and whether
  the AI picks a `build_intel_network` target without a `state`. Round 27 adds three:

  - that a `hidden_trigger` hold in a *shared* focus's `available` (`mltd_ai_may_*`) behaves as it
    does in the national claim focuses (`mltd_ai_may_press_claims`) - run 8 settled that
    `ai_will_do` 0 is no hold;
  - that `has_war_with = MLT` still holds on the capitulated country inside `on_capitulation`
    (`FROM = { tag = MLT }` is the fallback), on which the stages' `mltd_ai_*_beaten` now partly
    rest;
  - that an AI MLT takes the first ending its plan lists, The Dreamer Wakes, as run 8's evidence
    for list order implies (the 3 / 2 / 1 weights would decide only for a plan that lists none of
    them).

  Round 28 adds four:

  - `has_wargoal_against` in an `ai_strategy` `enable` (the refusal holds), and that their -1000
    outweighs OWB's pull on a fresh war goal;
  - that `mltd_ai_hold_wbh_for_terms`'s `antagonize` keeps the AI from justifying on WBH while
    Terms is pending, as `mltd_ai_opening_order_trl`'s is meant to;
  - that an AI Brotherhood, once added to a mutant-led faction, stays in it: no OWB faction script
    was found that would expel it, but it has never been seen in game;
  - how an invitation resolves when a human invitee lets it time out, now that the acceptance
    option can be hidden by its `trigger` (it was already open for `mltd.21` and `mltd.24`).

  Round 28c adds two:

  - that an AI reaches The Coast Goes Under only as a payout in a war the raiders already fight
    with MLT - its hold, a refused Covenant's exclusion and Terms' own courtship line together -
    and never declares the war with it;
  - that `mltd_ai_hold_refusal_wargoal_brk`, which now reads the twin's hold, still keeps the
    refusal's war goal unused until the Broken Coast's stage and a safe target allow it.

## Encoding

These rules are measured from the files on disk, not assumed.

- `descriptor.mod`, `*.mod`
  - BOM: **No** (0 of the 55 descriptor + launcher `.mod` files belonging to the 27 installed mods)
  - Line endings: LF (same 55)
  - Indent: Tab
- `localisation/**/*.yml`
  - BOM: **Yes, required** (`EF BB BF`)
  - Line endings: LF or CRLF
  - Indent: 2 spaces
- `*.txt` script - new files
  - BOM: No (house style; 1,749 of OWB's 6,721 `.txt` do carry one and load fine)
  - Line endings: LF
  - Indent: Tab
- `*.txt` script - the seven OWB overrides
  - BOM: No, except `history/countries/MLT - Mirelurk Tribe.txt` and `events/nf_mlt.txt`, which
    keep OWB's BOM (matches OWB either way)
  - Line endings: **CRLF** (matches OWB; `.gitattributes` `* -text` keeps it)
  - Indent: Tab
- `*.gfx`
  - BOM: No (0 of 163 OWB `interface/*.gfx`, 0 of 145 vanilla; still 0 scanned recursively)
  - Line endings: Either
  - Indent: Tab
- `*.asset`
  - BOM: No (0 of OWB's 76 under `gfx/`, 0 of vanilla's 213)
  - Line endings: Either (vanilla's are LF, OWB's CRLF); ours is generated LF, and
    `build_unit_model.py` checks it
  - Indent: Tab

A localisation `.yml` without the BOM is **silently ignored** - no error, the raw key strings just
show in-game. First line must be exactly `l_english:` with no leading whitespace; entries are
`key:0 "Value"`, indented by two spaces.

Tooling traps, both verified in this environment:

- The editor/Write tool emits UTF-8 **without** a BOM. After writing any `.yml`, prepend one with
  this Python:

  ```python
  p = r"<file>"
  d = open(p, "rb").read()
  open(p, "wb").write(d if d[:3] == b"\xef\xbb\xbf" else b"\xef\xbb\xbf" + d)
  ```

- PowerShell 5.1 bare `Set-Content` writes **Windows-1252**, turning `§` into a single invalid byte
  `A7`. That is HOI4's colour-code prefix. Use `Set-Content -Encoding utf8`, `Out-File`, or the
  Write tool - never bare `Set-Content`. Conversely `>` and `Out-File` **add** a BOM, so never
  generate `.mod` files with them.

- Pillow (12.x) writes an OWB-identical uncompressed DDS with `img.convert("RGBA").save("x.dds")` -
  **no** `pixel_format` kwarg (`'RGBA'`/`'A8R8G8B8'` raise and truncate the file to 0 bytes).
  `DXT1/3/5` strings also work; `build_portrait.py` patches the DXT1 header dwords to OWB's values.

## Markdown

Every `.md` in the repo - this file, `README.md`, the specs and notes under `story_rework/`,
`event_images/SOURCES.md`, the run reports in `ai_runs/` - must read well as plain text, in a
terminal or an editor that does not wrap. Apply these rules to every `.md` you write or edit, in
the same change:

- **No line is wider than 100 characters**, table rows included. Prose is hard-wrapped - by
  mdformat, never by hand - at 99, one short, because mdformat adds a backslash in front of a
  line-leading `-` or `40.` after it has wrapped. A line whose overflow holds no space (a long URL
  or path) may run over.

- **A table stays a table only if it fits once aligned.** mdformat pads every cell to its column's
  widest, so one long cell widens every row: the width is the columns' widths, plus 3 per column,
  plus 1. A table that does not fit becomes a list, one item per row: `- <key>: <description>` for
  two columns; for more, the row's key leads the item and each other cell becomes a sub-item,
  `- <Column>: <cell>`. Keep every word, and turn `\|` in a code span into `|` once it is out of
  the table.

- **A list directly after another list merges into it**, and the merged list renders loose:
  separate the two with a paragraph (a `*` marker would keep them apart, but markdownlint's MD004
  wants every list on `-`).

- **Code.** A code span too long for a line becomes a fenced block, or is split where the code
  breaks naturally. Every fenced block names its language (`text` if none fits). A code span cannot
  start or end with a space: CommonMark strips one.

- **Format, then lint**, before the change is done. The configs are `.mdformat.toml` and
  `.markdownlint-cli2.jsonc` at the repo root, and neither tool needs installing (`uvx` and `npx`
  fetch pinned versions):

  ```sh
  uvx --from mdformat==1.0.0 --with mdformat-gfm==1.0.0 mdformat <files>
  npx --yes markdownlint-cli2@0.23.3 --no-globs <files>
  ```

  mdformat reflows paragraphs, aligns tables, numbers ordered lists (zero-padded from ten items, so
  the markers line up) and escapes a character that a wrap would leave to be misread, such as a `-`
  or `+` starting a line. It refuses to write a file whose rendered HTML would change, so a reflow
  never alters content. markdownlint must report no issues: fix the text, never disable a rule.
  Without `--no-globs` it lints every `.md` in the repo.

- **Editing wrapped text.** Edit it as it stands and re-run mdformat, which reflows the paragraph.
  A wrap can split a phrase across lines, so search for one with a pattern that allows a line break
  between its words; an identifier is never split.

- **Generated Markdown** follows the same rules. `ai_run_report.py` lays its reports out itself
  (`md_table`, `md_wrap`, `md_code`): a table that fits prints aligned, as mdformat would print it,
  and one that does not prints as a list; prose wraps at 99 with mdformat's escapes, so a fresh
  report passes `mdformat --check` unchanged, and `--selftest` checks the layout. A new script that
  writes Markdown does the same.

- Prettier is not used: its Markdown parser is not CommonMark, and on this file it glued code spans
  to the words beside them.

## Naming conventions

Use the submod prefix `mltd_` / `MLTD_` for anything new, and keep `mlt_` / `MLT_` for anything
that must interoperate with OWB's existing MLT content (the `mlt_nf` tree id, `MLT_*` character
tokens, the `nf_mlt` event namespace, the `mlt_eggs` variable).

- New file: `mltd_<kind>.txt`
  - Example: `common/ideas/mltd_ideas.txt`
- Loc: one file, `localisation/english/MLT/mltd_l_english.yml`; OWB-key overrides in
  `localisation/replace/mltd_replace_l_english.yml`
- Focus id: `mltd_<name>`
  - Example: `mltd_the_grand_ritual`
- Event: `mltd.<n>` (`add_namespace = mltd`). Taken: 1-27; 30-34, 40-41, 50-52, 60-62 and 70-74
  (the story acts, round 27: each act owns its decade - 30-39 Act III, 40-49 Act IV, 50-59 Act V,
  60-69 Act VI, 70-79 the finale; round 28's Terms for the Citadel took 32-34, and rounds 28b and
  28c added none, so 35-39 are Act III's free ids); and 101-103 ... 501-503 for the Book
  expeditions (`<book number>01-03`). The next free id outside an act's decade is 28
  - Example: `mltd.28`
- Story-act focus: aimed at one country's story: `mltd_<target tag, lower case>_<name>`
  (`mltd_wht_*` covers both Utah tags, `mltd_wbh_*` whichever Brotherhood holds Washington); a
  chapter or close: `mltd_<name>`; an ending: `mltd_ending_<name>`; a spoils focus (round 28):
  `mltd_spoils_<name>` - a focus keeps its id when it is renamed (`mltd_spoils_the_canals_run_salt`
  shows as *Salt in the Canals*), because the plan, the AI and the telemetry name it
  - Example: `mltd_brk_the_coast_goes_under`, `mltd_when_the_legion_breaks`,
    `mltd_ending_the_dreamer_wakes`, `mltd_spoils_the_office_of_salt`
- Decision / mission: `mltd_<name>` / `mltd_<name>_mission`
  - Example: `mltd_gift_of_the_tide_mission`
- Decision category: `mltd_<name>_cat`
  - Example: `mltd_children_of_the_deep_cat`
- Scripted effect: `mltd_<verb_phrase>`; state-scope effects end in `_here`
  - Example: `mltd_raise_deep_ones_here`
- Variable / flag: `mltd_<name>_var` (modifier inputs), `mltd_<name>` (counters, flags)
  - Example: `mltd_gift_tide_var`, `mltd_gifts_permanent`
- Idea / dynamic modifier: `mltd_<name>`
  - Example: `mltd_gifts_from_the_deep`
- Sub-unit: `mltd_<name>`
  - Example: `mltd_deep_ones`
- Equipment: `mltd_<name>_equipment` (archetype), `mltd_<name>_equipment_<n>` (variant)
  - Example: `mltd_star_spawn_equipment_1`
- Tech: `mltd_<name>_tech` - **exception:** the Deep Ones tech is `warbike_unlock_tech` (see above)
  - Example: `mltd_star_spawn_tech`
- Tech / equipment icon sprite: `GFX_<tech_or_equipment_id>_medium` + `alwaystransparent = yes`
  - Example: `GFX_mltd_deep_ones_equipment_1_medium`
- MLT's own icon / name for an OWB tech's equipment: sprite `GFX_MLT_<tech_id>_medium`, in
  `interface/z_mltd_technologies_faction.gfx` ->
  `gfx/interface/equipment/cosmetic/<kind>/mltd_<OWB's icon pattern>.dds`; loc
  `MLT_<equipment_id>`, `_short`, `_desc` - the engine's names, so no `mltd_` prefix
  - Example: `GFX_MLT_melee_weaponry_tech_3_medium`, `MLT_melee_equipment_3`
- Unit icon sprites: `GFX_unit_<subunit>_icon_medium` / `_medium_white` / `_small`
  - Example: `GFX_unit_mltd_deep_ones_icon_small`
- Unit 3D model: the sub-unit's `sprite = mltd_<name>`, which the engine resolves to the entity
  `mltd_<name>_entity`; pdxmesh `mltd_<name>_mesh`; files
  `gfx/models/mltd/<name>/mltd_<name>.mesh`, `mltd_<name>_d.dds` / `_n.dds` / `_s.dds` and
  `mltd_<name>_mesh.gfx` (OWB's `<name>_mesh.gfx` beside the mesh); entities in
  `gfx/entities/mltd_entities.asset`; animations `mltd_<name>_<id>_animation` in
  `mltd_<name>_animations.asset` beside their `mltd_<name>_<id>.anim`, the `<id>` being what the
  pdxmesh lists and a state plays
  - Example: `mltd_star_spawn_entity`, `mltd_star_spawn_mesh`, `mltd_star_spawn_idle_animation`
- Event picture sprite: `GFX_mltd_event_<name>` -> `gfx/event_pictures/mltd_event_<name>.dds`
  - Example: `GFX_mltd_event_kingdom`
- Decision icon sprite (new art): `GFX_decision_mltd_<name>` ->
  `gfx/interface/decisions/mltd_<name>.dds`
  - Example: `GFX_decision_mltd_cult_hood`
- Agency logo sprite: `GFX_intelligence_agency_logo_mltd_<name>` ->
  `gfx/interface/operatives/agencies/mltd_agency_logo_<name>.dds` (`noOfFrames = 2`)
  - Example: `GFX_intelligence_agency_logo_mltd_esoteric_order`
- Operation: `mltd_op_<name>` (variants of one operation: `_<variant>`, sharing the
  `mltd_op_<name>` loc keys)
  - Example: `mltd_op_indoctrinate_the_faithful_1000`
- Character: `MLT_<NAME>`
  - Example: `MLT_TIDEWARDEN`
- Advisor token: `MLT_<name>_<slot>`
  - Example: `MLT_tidewarden_high_command`
- Focus icon sprite (new art): `GFX_goal_mltd_<name>` (+ `_shine`)
  - Example: `GFX_goal_mltd_deep_currents`
- Idea sprite (new art): `GFX_idea_mltd_<name>`
  - Example: `GFX_idea_mltd_spawning_grounds`
- Portrait sprite: `GFX_Portrait_MLT_<name>`
  - Example: `GFX_Portrait_MLT_tidewarden`
- Loc key: `<id>` and `<id>_desc` (equipment variants also `_short`); tooltips `<thing>_tt`
  - Example: `mltd_deep_currents_desc`

OWB's own casing is inconsistent and must be matched exactly when extending it: portraits and
character small icons use uppercase `MLT_`, focus goal icons use lowercase `mlt_`. Focus, idea,
tech and equipment icons are reused OWB sprites; the new art is the four event pictures, the graded
portrait, the two procedurally drawn unit-icon sets, the cult-hood decision icon, the agency seal,
the Tridents tech icon, the Star Spawn's 3D model and, rendered from it, the two monsters'
equipment icons.

### Localisation: functions, not names

Loc text refers to things through a function or their own key, never by repeating a name, so it
stays right when a name changes (a cosmetic tag, an OWB rename, our own edit). Only our own keys
follow this; OWB's and vanilla's are never edited (`localisation/replace/` only overrides OWB's
`warbike_unlock_tech` strings). Round 16 rewrote ~230 keys this way.

- A country: `[TAG.GetName]`, `GetNameDef` / `GetNameDefCap` (mid-sentence / sentence start),
  `GetAdjective` for possessives and attributes ("[WBH.GetAdjective] weapons", not "the
  Brotherhood's"), `GetNameWithFlag` where a flag helps (it has no article - reword)
  - Example: `[NCR.GetNameDef]`, `[MLT.GetNameWithFlag]`
- MLT: the same. **MLT is "Mirelurk Tribe" until the Kingdom, then "M'lyeh"** (OWB's
  `set_cosmetic_tag = MLT_cosmetic_tag` in `mlt_kingdom_of_mlyeh`), so a hard-coded "the Mirelurk
  Tribe" is wrong in every post-Kingdom text
  - Example: `[MLT.GetNameDefCap] has room`
- A state: `[ID.GetName]` (vanilla/OWB precedent `[195.GetName]`); the capital
  `[MLT.Capital.GetName]`
  - Example: `[235.GetName]` (The Warren)
- A character: `[TOKEN.GetName]` (OWB precedent `[BOS_mari_torni.GetName]`)
  - Example: `[MLT_MLULU.GetName]`, `[CES_caesar.GetName]`, `[TLA_tlaloc.GetName]`
- Our focus, decision, gift, unit, category, idea, agency, Book, market item: its own key, nested:
  `$key$`
  - Example: `$mltd_the_wet_market$`, `$mltd_deep_ones$`, `$mltd_agency_name$`
- An OWB focus, idea, modifier, equipment or VP name: OWB's key, nested
  - Example: `$hea_war_in_heaven$`, `$amphibious_beast_equipment_1_short$`, `$TRADE_LEDGER_TITLE$`,
    `$VICTORY_POINTS_7064$` (Mireport)
- Our agency, once it exists: `[Root.GetAgency]` (the player may rename it); before it exists,
  `$mltd_agency_name$`
  - Example: `mltd_intel_foothold_upgrade_tt`

Kept as written, deliberately: **M'lyeh as the drowned city or the faith** (OWB has no loc key for
the city - no `VICTORY_POINTS_1983` - and `[MLT.GetName]` would read "Mirelurk Tribe" in focus
descriptions, which are readable before the Kingdom); quotations, chants and the *Hail M'lyeh*
salute; lore places and peoples with no state or country of their own (Council Hill, the Long 15,
Point Lookout, the Coral Court); and common nouns ("the tribe", "the Order", "the Texans"). Watch
the articles: several OWB definite names carry none ("Lost Hills", "Caesar's Legion", "Heaven's
Guard") or their own ("El Ejército Mexicano"), so drop ours before `GetNameDef`; and OWB's
`wht_god_old` idea is "In Honour of the Gods!", not "Great Old Ones". **Nesting is one level
deep:** a key referenced with `$...$` must be plain text. A reference to a key whose own value
contains `$...$` stays raw in game - the Wet Market's tab tooltip printed
`$mltd_wet_market_seller_name$`, whose value was `$mltd_the_wet_market$`, while the rows' one-level
references resolved. So reference the thing's own plain key: alias keys
(`mltd_wet_market_seller_name`, `mltd_wm_item_<n>`) are for GUI text only, and a name that other
strings reference (`mltd_summon_the_deep_ones`, `mltd_call_of_the_deep_ones`,
`mltd_the_deep_ones_walk`, `mltd_summon_the_star_spawn`) stays plain text even though it repeats a
unit's name. After an edit, check that every nested `$key$` resolves, to plain text.

**A `$key$` from a `localisation/replace/` file does not resolve inside a sentence.** In game,
`$amphibious_beast_equipment_1_short$` (OWB's name for Mirelurks, defined only in OWB's `replace/`
folder) printed raw in the Wet Market's buy tooltip, while the rows' pure alias
`mltd_wm_item_1:0 "$amphibious_beast_equipment_1_short$"` resolved. Vanilla never nests a replace
key in a sentence (0 of its 5,184 nested references), while 2,042 of them point at keys in files
that sort later - so order among `english/` files does not matter; only `replace/` keys do. For
such a name use a scripted-loc function that returns the key, as OWB's own `[GetMarketInventory]`
does: `[GetMltdMirelurksName]`, `[GetMltdKillclawsName]`, `[GetMltdBloodrageName]`,
`[GetMltdMirelurkKingsName]`.

## Gotchas

- **A sprite declared twice takes the declaration read last, and `interface/*.gfx` files are read
  in filename order.** That is what OWB's `z_` prefix is for: it re-declares a vanilla sprite from
  a differently named file 186 times, and 179 of those files sort after vanilla's. *OWB: Ultimate
  Tech Compatibility Mod* re-points 43 sprites of `z_fallout_technologies_faction.gfx` from
  `z_fallout_technologies_faction_mutants.gfx`. So an OWB sprite can be re-pointed without
  overriding OWB's file, but only from a file that sorts after it: `mltd.gfx` sorts before every
  `z_fallout_*.gfx` and would lose. `z_mltd_technologies_faction.gfx` does this for MLT's two knife
  icons. unverified in game - Enclave Reborn Redux and Rustbelt Rising re-declare hundreds of OWB
  sprites from files that sort *before* OWB's, which either works by mod load order instead or does
  nothing; our file name is right under both readings.

- Every `GFX_goal_*` sprite used as a focus `icon` should have a matching `GFX_goal_*_shine`: OWB
  does this for every one of its focus icons, as does vanilla. Purely decorative `GFX_goal_*`
  sprites ship with no shine. Without it the focus just renders unhighlighted - no error appears in
  `error.log`.

- A new focus tree in a *new* file must out-score OWB's, which is `factor = 0` with
  `modifier = { add = 10 tag = MLT }`. We override the existing filename instead, which avoids the
  problem entirely.

- `ritual_of_black_hollows_night` has **no** `mlt_` prefix; `mlt_kingdom_of_mlyeh`'s prerequisite
  block lists two focuses in one block (OR).

- Overriding `common/characters/MLT.txt` requires copying the whole file:
  `history/countries/MLT - Mirelurk Tribe.txt` recruits 14 characters by exact token, and any
  missing one is a hard error at game start.

- `add_dynamic_modifier` **stacks**; guard with `NOT = { has_dynamic_modifier = { ... } }` (done in
  focus 1 and in `mltd_all_gifts_permanent`).

- `activate_mission` cannot re-activate an active mission and `remove_mission` skips
  `timeout_effect` - the gift decisions gate on `NOT has_active_mission` for exactly this reason.

- `select_effect` runs every time a focus is (re)selected and is **not** shown in the focus
  tooltip; keep its contents idempotent (`set_variable`, `add_ideas`) and describe them in
  `completion_reward` with `custom_effect_tooltip` + `set_temp_variable ... tooltip =` modifier
  lines.

- A focus gated only by `available = { has_completed_focus = X }` (no `prerequisite`) draws no
  connecting line and shows greyed until X completes - that is how `mltd_gifts_from_the_deep` hangs
  below `mlt_kingdom_of_mlyeh` without a line, and how, from round 27 to 2026-09-23, Act III's
  three invitations named their Act II heads.

- Books 1-2 require *direct control* of Arago / The Warren. OWB's Kingdom gate accepts cores held
  by MLT's sphere (puppets, allies, faction members), so a player who puppeted DIS or TRL must
  still take those states - by design. Since round 14 a full-strength (100 %) La Resistance network
  in the state also opens its Book, so a spy can stand in for an army. Books 3-5 sit in MDT / ARR /
  PMR land that no OWB `ai_strategy` pushes MLT toward, so until round 18 an AI MLT usually stopped
  at the Grand Ritual (3 Books); `mltd_ai_conquer_mdt`, `_pmr` and `_arr` now take all three (see
  MLT's AI).

- The Book focuses no longer touch `mltd_books_read`: the last event of each expedition adds the
  Book (`mltd.103/203/303/403/503`), 2-4 weeks after the focus. The centre column's 1 / 3 / 5 gates
  (`check_variable = { mltd_books_read > 0 / 2 / 4 }`) and the gift decisions
  (`has_country_flag = mltd_<n>_book_found`) therefore open when an expedition ends, not when its
  focus completes. `mltd_book_read_tt` is gone.

- `create_unit ... start_equipment_factor = 1.0` gives a division only equipment the country has
  **unlocked** (a tech with `enable_equipments`); stockpiled-but-locked equipment is not used.
  Unlock first (hidden tech), then spawn.

- Decision previews render *before* the effect runs: tooltips that show a number use
  `set_temp_variable = { mltd_gift_value_temp = X }` immediately before `custom_effect_tooltip`,
  never a non-temp variable set later in the same block.

- State-scope `add_manpower` (and OWB's `add_state_population`) changes **population**;
  country-scope `add_manpower` changes the recruitable pool. `weekly_manpower` is a weekly pool
  change, `monthly_population` a growth %; neither kills people daily - hence the `on_daily_MLT`
  hook.

- Summon gates are national, at twice the population each summon takes. They used to be
  single-state thresholds, which the ritual tolls made unreachable: the Grand Ritual is a hard
  prerequisite of the Walk, so its toll always runs before the Star Spawn summon exists, and the
  Final Ritual's takes more. Spreading the toll over every state removes that failure mode, because
  no single state has to be large enough. Change the cost, the gate and the AI guard together.

- `on_daily_<TAG>` fires only while the tag is literally `MLT`; the toll, the population variable
  and the gifts pause if MLT changes tag (cosmetic tags are fine).

- `is_buildable = no` on an equipment **archetype** does not stop its variants being produced once
  a tech `enable_equipments` them (vanilla `infantry_equipment` works the same way) - so Deep Ones
  / Star Spawn equipment is producible from the first summon.

- OWB's per-unit mirelurk spirits (`modifier_army_sub_unit_amphibious_beast_creature_*`) do not
  reach `mltd_deep_ones` / `mltd_star_spawn`; adding them would need the whole-file
  `unit_modifiers.txt`. Category-keyed buffs do reach them - they are in `category_creatures`,
  `category_mutant_creatures` and `category_standard_creatures` - which is why we no longer
  override the doctrine file (next gotcha).

- **Never key doctrine or perk buffs to our sub-units by name.** The units already collect OWB's
  buffs through their categories: every Outsider Warfare tech buffs `category_mutant_creatures`,
  which all three amphibious units are in, so a block keyed by the sub-unit's name stacks on top of
  the same stat. Until 2026-09 this mod overrode `tech_fallout_land_doctrine.txt` with 16 such
  insertions. They doubled 8 stats across 7 techs (Outsider Warfare org +6 where OWB gives +3),
  changed OWB's own mirelurk for every nation, and put `max_strength = 5` into Adapted Armour
  (`we_are_enduring_doctrine`), which in OWB carries no health at all. Vanilla
  `stats_l_english.yml:218-221` gives `max_strength` no `STAT_*_MOD_VALUE` format key, so the
  tooltip renders any value as a percentage and `5` shows as "+500%" behind OWB's heart icon,
  although Paradox's own tooltips for the same script read it as flat HP (`infantry.txt:2828` ->
  `aat_ideas_l_english.yml:73`, "HP: +5"). The perk trees have the same trap.
  `creature_perk_tech_*` (`category_standard_creatures`) and `special_forces_perk_tech_*`
  (`category_special_forces`) in `fallout_perks_doctrine.txt` grant identical buffs with no XOR, so
  a unit in both categories collects every perk twice. Our units therefore follow the mirelurk and
  sit in `category_standard_creatures` only, not `category_special_forces` (they keep
  `special_forces = yes`, which only drives the special-forces cap). No OWB doctrine needs a new
  category for them: Asymmetric Warfare's Wasteland Knowledge branch reaches them through
  `category_creatures` and Outsider-Inspired Warfare through `category_mutant_creatures`. Adding a
  `category_standard_creatures` block to Outsider Warfare would re-create the stack for them and
  for every nation's mirelurks, deathclaws and ghouls, all of which are also in
  `category_mutant_creatures`. Known parity gaps, deliberately left alone, which are gaps rather
  than stacks: OWB's name-keyed mirelurk buffs (`mixed_army_doctrine` armour 0.15,
  `tech_creatures.txt` `amphibious_beast_upgrade_tech_*`, the `terrain_*_tech_6` morale lines,
  `lurk_sharpened_conch_knives` / `lurk_hardened_shell_shields`) never reach our units.

- `descriptor.mod` and the launcher `.mod` must be kept in sync by hand; the launcher rewrites its
  own copy from `descriptor.mod` on rescan, so edits made only there are lost. That includes
  `picture=`.

- There is **no `picture=` key** in either `.mod` file and **no `thumbnail.png` at the mod root**,
  on purpose: that is exactly how *The Fire Rises* (3350890356) is shaped, and it is the only
  installed mod with a working animated Workshop preview. The first publish used
  `picture="thumbnail.png"` and the item took the still. Pointing the key at a `.gif` is untried
  and no installed mod does it (all 11 that set `picture=` use a `.png`), so do not reintroduce the
  key on a hunch. If a publish still lands a still image, set the preview by hand on the Workshop
  page - no re-upload needed, and GIFs are definitely accepted there.

- The Workshop title image is the one asset that is public *before* anyone installs the mod, and it
  is currently built on the same unverified third-party art as the event pictures.
  `event_images/SOURCES.md` records the chain and the two ways out. Nothing else in the repo has
  that exposure.

- The marquee's neon bloom is a Gaussian of sigma `scf(32)` while the sign sits only 18 px from the
  edge of the 512-wide thumbnail canvas, so on that canvas the bloom is **clipped flat**. That is
  deliberate bleed for the thumbnail but a hard edge for the logo (alpha jumped 0 -> 224 in one
  column). `padded_sign_canvas` in `build_main_menu.py` re-renders the same sign on a wider canvas
  by shifting every absolute coordinate `build_sign` reads - `W`, `HEXW`, `SY0`/`SY1`/`SYM`, `GC`,
  `WM_TOP`, `SUB_TOP`. Sizes and differences (`CH`, `GAP_HALF`, `WM_W`, `SUB_W`, `SYM - SY0`) are
  translation-invariant; `SX0`/`SX1` are read only at import to build `HEXW`. The build prints the
  strongest alpha left on the crop border - ~0.02 is right, ~0.9 means it is clipping again.

- Ship the animated logo strip **uncompressed**, as OWB does its own. DXT5 quantises colour per 4x4
  block; a block straddling a neon tube and the transparent black outside it gets endpoints
  spanning cyan to black, measured at mean 6 / peak 164 error on visible pixels, which reads as a
  speckled fringe along the tubes. Trade frames for size instead - the breath is a slow ramp and 16
  frames step by under 2 luma levels each. `LOGO_FRAMES`/`LOGO_FPS` must match
  `noOfFrames`/`animation_rate_fps` in `mltd.gfx`.

- `animation = {}` blocks attach **only to `spriteType`** - ~56,000 across vanilla and all 25
  installed mods, and not one on a `corneredTileSpriteType`. `GFX_frontend_bg` is a
  `corneredTileSpriteType`, so the menu rain cannot be an animation on the background: it must be a
  second, fully transparent sprite laid over it by the gui, which is exactly how OWB's
  `GFX_frontend_bg_snow_anim` (disabled in `frontendmainview.gui`) is built.

- In an animation texture, **colour lives in RGB and shape lives in alpha** - OWB's
  `bg_snow_anim1.dds` is near-white RGB everywhere with alpha 0 except on the flakes.
  `bg_snow_anim_background.dds` is alpha 0 throughout (so only the animations draw) and
  `bg_snow_anim_mask.dds` is a flat alpha 191 (a global 75% strength). We reference both by path
  and copy neither.

- A frontend overlay `iconType` is drawn **unscaled at the size of its BASE texture**
  (`texturefile`) - *not* of its `animationtexturefile`s, which are sampled inside that rect.
  Enlarging the animation textures alone does nothing; this was found by trying it. The sprite is
  anchored to its container's top-left, and `frontend_background` is 1920x1440 scaled to *cover*,
  so it overflows vertically and its top-left is `(1440*max(W/1920,H/1440) - H)/2` px **above** the
  screen (180 at 1080p, 240 at 1440p). A base only `H` tall leaves an empty band along the bottom.
  Hence `mltd_rain_base.dds` and `mltd_rain_mask.dds` at 2560x1792 instead of OWB's 2560x1440 pair,
  which covers 16:9 up to 1440p; 4K and 21:9 need more - raise `RAIN_W`/`RAIN_H`, nothing else.
  This is almost certainly why OWB's own snow overlay is commented out.

- `build_main_menu.py --preview` models the frontend geometry (cover-scale, overflow, unscaled
  sprite rect, magnified scrolling texture, the 191 mask) and prints the rows/columns actually
  covered. It caught the band above; use it before believing any change to the rain.

- `animationtexturescale` magnifies by `1 / scale`, so OWB's snow at 0.3 is blown up 3.3x. Our rain
  uses 0.75 and `RAIN_SCALE` in `build_main_menu.py` must be changed with it, or the streaks stop
  matching their on-screen size. `animationrotation`'s convention (whether it rotates the texture
  with the scroll) is **unverified** - hence vertical, short streaks, and values inside OWB's
  known-good 210/220 range.

- `effectFile = "....lua"` resolves to a `.shader` of the same name in `gfx/FX/`; no `.lua` exists.
  Do not "fix" it.

- Steam caps a Workshop preview image at **1 MiB whether it moves or not**, and that single number
  decides the GIF's size, frame count and palette. Three things keep it under: frames are
  delta-encoded against *what is still displayed* rather than against the previous frame (per-frame
  comparison lets a pixel creep away one `GIF_TOLERANCE` step at a time and accumulates over the
  loop); dithering is off, because its noise is exactly what run-length compression cannot pack;
  and the palette is chroma-weighted, because median cut allocates by pixel count and this image is
  overwhelmingly low-chroma teal - left alone it starves the gold wordmark, the violet tube and the
  green eyes and snaps all three to grey-blue.

- The rain loop closes because the tile is periodic over `(W/2, W)` and is rolled a whole number of
  pixels per frame whose total over the loop is an exact multiple of both periods - the same trick
  as `build_animated_portrait.py`. `rain_tile()` asserts it; changing `GIF_FRAMES` to a number that
  does not divide the periods will trip it rather than silently seam.

- The OWB marquee wordmark is not shipped as a reusable asset by any mod - every submod re-creates
  or re-mattes it. Ours comes from *Fountain of Dreams* and arrives silver with a violet keyline;
  `retint_wordmark()` maps it to the house gold (hue 40-53 deg, which OWB, ECR, Rustbelt Rising and
  Over The Horizon all use). Silver is legal - NCR-vs-Legion uses it - and `--silver` keeps it.

- A continuous-focus palette cannot be extended from a separate file, and a country gets exactly
  one palette (chosen by the `country` weight block, `default = yes` as fallback) - see Overriding
  OWB.

- Script variables are **32-bit fixed point with 3 decimals**, so they overflow above
  **2,147,483.647** and wrap negative (OWB writes the number at
  `TON_farming_scripted_effects.txt:11` and detects the wrap at
  `coring_button_scripted_triggers.txt:141`; vanilla marks `manpower` and friends "DEPRECATED, MAY
  OVERFLOW" and ships `_k` variants such as `state_population_k` "to avoid variable overflows").
  Population arithmetic overflows easily: one state's population times a four-figure target is
  already hundreds of times over. **Divide before you multiply**, and keep divisors in thousands -
  `mltd_take_population_everywhere` does both, which caps its intermediate at 1,000 instead of
  448,000,000. The population sums `mltd_national_population` and `mltd_controlled_population`
  wrapped past ~2.1M people, which the later story acts reach; since the round-27 review
  `mltd_update_national_population` sums them in thousands and caps the people figure at 2,147,000,
  below which every gate and guard sits (The rituals). `mltd.73` prints no population.

- `check_variable`'s equality shorthand is `{ var = X value = N compare = equals }` or `{ X = N }`;
  **`==` is not valid** and appears nowhere in vanilla or OWB
  (`triggers_documentation.md:2110-2133`). `>` and `<` shorthand are fine.

- `add_victory_points` renders no trailing spacer in a tooltip (OWB comments on this at
  `Baggers (BAG) Focus.txt:1337`), so follow a run of them with
  `custom_effect_tooltip = mltd_newline_tt`.

- `add_caps` is OWB's, not vanilla's: it reads the temp variable `caps_to_add` set immediately
  before the call, and the displayed balance carries a "k" suffix, so `caps_to_add = 100` reads as
  "100k Bottle Caps".

- A `frameAnimatedSpriteType` strip must be exactly `frame_width x noOfFrames` wide; if the whole
  strip appears in the portrait slot, the two disagree.

- **`PdxMeshAdvanced` and `PdxMeshStandard` read the same three textures differently.**
  `PdxMeshAdvanced` defines `PDX_IMPROVED_BLINN_PHONG` and `EMISSIVE` (OWB's own
  `gfx/FX/pdxmesh.shader:764-769` - OWB overrides the file, so its copy runs): the normal map is x
  in G and y in A with **blue as the emissive mask**, the specular map G / B / A = specular,
  metalness, gloss. `PdxMeshStandard` defines nothing (`:725`) and takes the legacy path - an RGB
  normal map and the specular in A. A conventional blue-tinted RGB normal map under
  `PdxMeshAdvanced` turns the model orange at night (`:558-559`) and shades wrongly; OWB's
  creatures dodge the question with a flat (128, 128, 0, 128) normal map, and most of OWB's real
  normal maps are green-inverted against the shader, so compare with vanilla's. See The Star Spawn
  model.

- **A Blender bake does not say where it is valid.** `use_clear` fills a bake with black - a
  *tangent-space normal* bake with flat blue (0.5, 0.5, 1), an object-space one with black - so
  neither an all-zero nor a short-vector test finds the texels no ray wrote; `build_unit_model.py`
  rasterises the UV triangles instead (`uv_coverage`). And Smart UV Project's `island_margin` is
  added per island: 0.004 across 1,252 islands left 15 % of the texture in use, which is why
  `bl_unwrap` projects with no margin and lets `pack_islands` apply an exact one.

- **An animation's `file` is relative to the `.asset` that declares it** (734 of 734 declarations
  in vanilla and OWB resolve that way, none from the game root): vanilla declares beside the
  `.anim` (`gfx/models/units/railway_guns/animation_railway_gun.asset`), OWB one folder up
  (`jango_owb_base_entity_anim.asset`, `file = "mirelurk/mirelurk_idle.anim"`) - never with the
  entities in `gfx/entities`. The pdxmesh then gives each an `id`
  (`animation = { id = "idle" type = "..._animation" }`), and that id is what a state's
  `animation =` names.

- **A right-handed rotation about the model's +x pitches FORWARD**: an upright part bows, a
  forward-pointing part dips, a hanging limb swings back. The first drafts of the Star Spawn's
  clips had it the other way round and wound up by bowing; the contact sheets caught it
  (`build_unit_model.py --clip`), a number never would have.

- **A miniature's pose is not a rest pose.** The Star Spawn's sculpt has its rear leg 99 % straight
  in a lunge, so inverse kinematics has no slack: anything that moves the hips away from that foot
  locks the knee straight and the foot leaves its target. A walk has to bring its stride under the
  hips and ride lower (`unit_model_clips/move.py`); a stationary clip only ever lowers the pelvis.
  `--clip` prints each leg's straightness against its full length.

- **Pillow's DXT5 alpha is a poor quantiser.** Its encoder (12.2) writes every alpha block in
  6-value mode and never uses the block's own endpoints: a 4x4 ramp of 8 ... 248 comes back as only
  56 / 104 / 152 / 200, and every block keeps 60 % of its range. That is the channel a
  `PdxMeshAdvanced` normal map keeps its y in, and a specular map its gloss. `build_unit_model.py`
  keeps Pillow for the colour half and writes the alpha half itself (`dxt5_alpha`: 8-value mode,
  the endpoints the block's extremes), which took the normal map's median error from 4.9 to 4.0
  degrees; vanilla's own maps use 8-value mode in 99 % of blocks. None of the mod's other DXT files
  carries meaning in alpha.

- **Blender exits 0 when its Python script raises.** Pass `--python-exit-code 1`
  (`build_unit_model.py` does) or a failed stage looks like a success. `--factory-startup` keeps
  the user's add-ons and preferences out of a headless run, and the Cycles device must then be
  chosen in script (`bl_use_gpu`) - by the device's own `type`, because `prefs.devices` lists every
  backend's devices at once and a machine without OptiX would otherwise report OptiX and bake on
  the CPU. `Material.use_nodes` / `World.use_nodes` are no-ops in Blender 5 and due to go in 6.0
  (`bl_node_tree` guards them).

- Startup `error.log` triage: lines about `artful_positioning_doctrine` / `tactics_doctrine_tech` /
  `tactics_spec_ops_cap_tech` XOR paths, `occupationlawdatabase`,
  `provincegraphics ... too far away from center` and
  `remotefile.cpp ... Failed allocate data buffer` are OWB/vanilla noise, not ours. Ours would
  mention `mltd`, `MLT_DROWNED_HERALD`, `warbike_unlock_tech` or a file under our paths.

- **Shared focuses come in only through shared prerequisites.** `shared_focus = <id>` in `mlt_nf`
  pulls in that focus and every shared focus linked to it by prerequisites on other *shared*
  focuses, and nothing else. A shared focus whose only prerequisite is a national focus is never
  pulled in: vanilla has to list `CONGO_congo_investments` (sole prerequisite
  `BEL_monetary_reconstruction`, `congo_shared.txt:951`) explicitly at `belgium.txt:20`. So a story
  focus whose prerequisite is a national focus must be listed in the override, as the three Act II
  heads (The Grand Ritual; the Walk until 2026-09-24) and The Tide Turns South (The Final Ritual)
  are - four lines since 2026-09-24, nine from round 28c, when Act III's six stood in the close's
  place - following vanilla's Congo. Every other story focus must reach a listed one through shared
  prerequisites; any further dependency on a national focus goes in `available`, which draws no
  line. Never point a shared focus's `relative_position_id` at a national focus either: none of
  OWB's 464 or vanilla's 335 shared focuses does, so it is untested.

- **`network_national_coverage` is a 0-1 fraction** (`triggers_documentation.md:6503-6516`, example
  `value > 0.5`; vanilla `00_defines.lua:3637` and `:3644`, "[0, 1]"), while `network_strength` is
  0-100. OWB's one non-zero coverage test, `Lost Hills (BOS) Focus.txt:9646-9649` (`value > 30`),
  uses the wrong scale and can never pass - do not copy it. Ours use 0.25 (all three invitations
  since round 28c's balance review; the Covenant asked 0.3 before it) and 0 to 0.4 in the AI's own
  network blocks. Its native tooltip prints the raw value as a whole percent - `value > 0.25` reads
  *More than 0%* (round 16, on `mltd_ncr_salt_on_the_caravan_roads`) - so where the figure matters,
  wrap the check in a `custom_trigger_tooltip` whose loc copies the native line:
  `mltd_brk_network_tt` is
  `Network National Coverage in [BRK.GetFlag] §H[BRK.GetNameDefCap]§! More than 25%`. Round 24
  wrapped the 16 that were still bare, so all 35 coverage checks of the conflict sub-trees were
  wrapped. Round 27 took every intel gate out of the story acts except the invitations', so only
  their checks are left, all wrapped: the Covenant's (`mltd_brk_network_tt`) and Hail the Drowned
  King's (`mltd_bdt_network_tt`), and since round 28c's balance review Terms for the Citadel's two
  branches, whose figure sits in the one line `mltd_wbh_terms_faithful_tt`. All three read 25 %
  since that review. Their percentages repeat the thresholds, so change both together. The round-24
  `mltd_<tag>_network_<pct>_tt` keys went with their gates. `has_operation_token`'s native line
  (`OPERATION_HAS_TOKEN`, *Has [icon] Army Infiltration*) is fine as it stands, but names no
  country.

- **Agency upgrades from script probably cost caps.** Every OWB upgrade requires caps and pays them
  through `add_caps` in its `complete_effect` (`intelligence_agency_upgrades.txt:16-22`, `:29-34`).
  OWB's Unbound refunds its own scripted upgrades for that reason
  (`Unbound (UNB) Focus.txt:370-375`, "needed to counteract caps takeaway from spy upgrades").
  `mltd_intel_foothold` refunds that price per upgrade and skips both upgrade and refund at
  `agency_upgrade_number > 29`, OWB's ceiling (`00_scripted_effects.txt:540`), where the refund
  would be free caps. This is untested: if a spying head leaves the caps balance one price higher,
  script upgrades are not charged and the refund must go. Also, `add_caps` runs `check_bankrupt`
  against the balance *before* its own change (`caps_scripted_effects.txt:48-55`; the condition is
  balance < 0 and caps net < 0, `:126-127`). That is why the refund is paid *before* the upgrade:
  paid after it, the refund's own `add_caps` would see the dip whenever the tribe holds less than
  the price with negative caps income, and would start OWB's bankruptcy chain (`bankrupt_events.1`,
  `:166`) even though the balance ends where it started.

- **The Drowned God Sleeps brings Tlaloc's death forward.** `mltd_tla_the_drowned_god_sleeps`
  subtracts 64 from `TLA.current_databanks`, about 57 days of OWB's base drain (1.12/day,
  `history/countries/TLA - Tlaloc.txt:157`). So `nf_tlaloc.100` - the release of MAX, MOC and ZAP,
  `tlaloc_died`, the succession wars and `kill_tlaloc`'s nuke - arrives ~8 weeks sooner. It copies
  `on_daily_TLA`'s four guards (`tlaloc_on_actions.txt:276-281`), so it never drains a frozen or
  RRG-bound Tlaloc. It also runs only above 100, so it never zeroes the variable itself: OWB's own
  daily clamp (`:285-289`) and its `current_databanks = 0` check (`:318-327`) still fire the event.

- **Absorbing TRL is what turns WBH on The Warren.** `WBH_attack_the_warren` becomes available once
  `TRL = { exists = no }` (`Shared Brotherhood Focus.txt:2113`). With TRL gone,
  `grant_wargoals_on_core_states_of_prev` falls through to its no-country branch: claims on TRL's
  cores, 235 included, plus a `demand_stolen_territory` decision (`wargoal_effects.txt:69-83`).
  WBH's start-of-game truce with MLT (`nf_washington.14`) applies only when TRL is human
  (`events/nf_washington.txt:478`), so an MLT player never gets it. The Tide-Wall's
  `remove_claim_by = WBH` on 235 undoes that claim, and so does an accepted Terms for the Citadel
  (round 28): `mltd_wbh_join_the_covenant` drops every claim the Brotherhood holds on MLT's land,
  since taking Terms closes The Tide-Wall (round 28b). A refused Terms removes no claim: the
  Brotherhood's claim on The Warren stands, and only the war removes it.

- **Operation tokens are shared with OWB's operations.** A `token_army` handed out by a focus also
  opens OWB's `operation_steal_tech_army` (`00_operations.txt:2443`) and
  `operation_steal_enemy_supplies` (`operations_fallout.txt:36-38`) against that target.
  `operation_steal_tech_army` and `operation_steal_tech_civilian` use up their token
  (`00_operations.txt:2467`, `:1903`). Since round 27 no story focus waits on a `token_army`, so
  the ones the heads and beads hand out are purely for OWB's operations. The Covenant and Hail the
  Drowned King test `token_civilian`, which a steal-tech operation against BRK or BDT would spend.

- **A close strands if its OR has no takeable path.** Each act's close reconverges through one OR
  block (two `prerequisite` blocks would be AND), so any one branch opens it. Every head and bead
  must stay takeable when its target dies or becomes MLT's subject: no `country_exists` in
  `available`, and every reward has a fallback. The three war closes also wait for a war's result,
  which `has_capitulated` alone would lose at the peace - hence the `on_capitulation` flags (The
  story acts > *Never strand*). Before round 27 the same rule applied to the conflict capstones,
  most of which needed both parents. An invitation may sit in a close's OR only because its focus
  completes whatever the answer: round 28 kept Terms for the Citadel out of Act III's OR, and round
  28b put it in once its war twin could no longer be taken after it.

- **Hoover Dam flags.** The Boulder City outcome is `fbhd_boulder_city_miracle_flag` - with
  `_flag`, unlike its effect `fbhd_boulder_city_miracle`; OWB's own commented-out test at
  `Lost Hills (BOS) Focus.txt:2599` has the wrong name. The three outcome flags are set at
  `hoover_dam_scripted_effects.txt:207/255/264`. No flag records the second battle: test
  `NCR = { has_war_with = CES }` or `CES = { has_completed_focus = ces_attack_ncr }`. That focus is
  unavailable before 2279.06.01 (`Caesars Legion (CES) Focus.txt:8586`), which is why The Turbines
  Sing falls back to that date.

- **There is no `TEX` tag.** `TEX` is a tag alias for TBH or LNS while one of them wears a `TEX_*`
  / `TAA_Texas_*` cosmetic (`common/country_tag_aliases/tag_aliases.txt:93-106`). Script against
  `TBH` and `LNS` directly, and test unification with `has_global_flag = texas_formed`
  (`texan_economic_union_scripted_effects.txt:657`). Act VI's close tests both tags through
  `mltd_texas_beaten`.

- **The flavour guard has a one-day gap.** `mltd_flavour_can_fire` opens as soon as the Kingdom
  completes, but the 90-day `mltd_flavour_cooldown` is set by `mltd.1`'s `immediate`
  (`mltd_events.txt:8`), and the Kingdom fires `mltd.1` with `days = 1` (override `:1181`). A
  monthly roll inside that day can still land a flavour event before `mltd.1`. Setting the flag in
  the Kingdom's `completion_reward` would close the gap, at the cost of one more override line.

- `retire_character` removes an advisor for good; the Book expeditions use it for their deaths.
  Gate every such option with `has_character = <token>` and give the event an option that appears
  only when none of them is left, so the event always has a valid option.

- **Operative slots.** An agency starts with 1 (`00_static_modifiers.txt`,
  `created_intelligence_agency`) and upgrades add at most +1: vanilla
  `MAX_OPERATIVE_SLOT_FROM_AGENCY_UPGRADES = 1`, which OWB leaves alone (it only lowers
  `AGENCY_UPGRADE_PER_OPERATIVE_SLOT` to 4, `resistance_defines.lua:51`). So an unbuffed MLT tops
  out at 2 after its 4th upgrade, one short of the 3 that OWB's steal-tech operations need.
  Training Centers' `new_operative_slot_bonus` is "Operative recruitment choices", not slots. Old
  Castro's `mltd_keeper_of_the_order` brings MLT to 4.

- **OWB's `is_major` mostly means "at war".** `00_on_actions.txt:1362-1370` gives `set_major = yes`
  (and flag `set_as_major_for_war`) to every non-subject country when a war relation is added, and
  `:431-446` takes it away at peace; in peacetime only the top industrial powers are majors
  (`fchanges_defines.lua`: `MIN_MAJOR_COUNTRIES = 3`, `MAJOR_MIN_FACTORIES = 40`). *The Spreading
  Cult* plants its cults on plain `is_major` anyway, by choice (round 15 dropped round 14's
  "genuine major or 8+ states" filter as over-complicated), so a small neighbour at war - MLT's own
  enemy included - qualifies for a cult for as long as the war lasts, and at peace usually only
  NCR-sized neighbours qualify. A cult founded during the war outlives it: `is_major` is tested
  only by the focus's `every_country` (since round 17 the *Found a Cult* operation reaches any
  country), while the operations and `on_weekly_MLT` test only `has_variable = mltd_cult_strength`,
  and nothing reacts to OWB's `set_major = no` at peace. So it decays, now at the peace rate, and
  can be tended like any other cult until it falls below 1 %.

- **No countdown formatter for another country's flag.** The house cooldown idiom prints
  `[?<flag>:days_left|0]` for flags on ROOT; there is no precedent for a flag held by FROM, so
  round 14's targeted cult decisions (gone since round 17) kept their cooldowns as week-countdown
  variables on the target (`mltd_cult_cd_*`, lowered by `mltd_cult_weekly`) and printed them with
  `[?From.mltd_cult_cd_*|0]`, a formatter OWB uses (`[?FROM.caps_to_caf|=+2]`).

- **Hot reloads lie about new definitions.** A console reload re-parses `common/decisions` before
  the scripted effects and never reloads `common/scripted_triggers` or `common/dynamic_modifiers`,
  so anything added since launch reads as unknown. An unknown trigger inside a decision's
  `target_trigger` leaves an empty block, which passes: that is how Klamath (2 states) was offered
  a cult in round 13's test, and why its cult decisions only charged their costs. Fully restart
  after adding definitions. A fresh load tolerates forward references (OWB's scripted effects hold
  1,190, e.g. `caps_scripted_effects.txt:52` calling `:120`), but a reload registers effects in
  file order, so the cult effects are defined callee-first: dissolve, refresh, add, weekly.

- **An `if` whose limit fails and has no `else` passes.** That is what makes the Covenant's and
  Hail the Drowned King's La Resistance lines free without the DLC (deliberately; the conflict
  sub-trees' intel gates worked the same way until round 27), and why the Books' network gate is an
  `if`/`else`: a bare `if = { limit = { has_dlc = "La Resistance" } ... }` inside an OR would open
  every Book for players without La Resistance.

- **OWB's decision-category pictures cover the frame line.** `countrydecisionview.gui:148` draws
  the picture at y=3, where the description frame (`GFX_tiled_decisions_bg_small`, drawn at y=-1)
  has its orange and red lines (texture rows 4-5, so desc y 3-4). 30 of the 44 pictures OWB's own
  categories use cover it, all nine 500x200 ones included. Ours are shifted copies
  (`build_category_pictures.py`, N = 2). Do not fix it by overriding the 721-line gui.

- **Marketplace "opinion" is organisation influence, not country opinion.** The sellers are OWB's
  five organisations (`country_organizations`), reached only through `organization_add_influence`;
  `add_opinion_modifier` does nothing for them.

- **`custom_cost_text` needs a `_blocked` twin.** The engine derives `<key>_blocked` (the row text
  while `custom_cost_trigger` fails, conventionally with red numbers) and `<key>_tooltip` (the cost
  line in the hover tooltip; optional) from the key - both suffixes sit in `hoi4.exe`'s decision
  code, and vanilla defines `_blocked` for all 105 of its cost keys. A missing `_blocked` prints
  the raw key across the decision name, which is what round 14's cult decisions did.

- **OWB's `caps_cost_trigger` is a caps gate only while the caps rule is on.** With it off the
  trigger becomes `has_political_power > 1.25 x caps_diff` (`caps_scripted_triggers.txt:22-24`),
  which passes for any negative - cost - `caps_diff`, while `add_caps` charges the caps as 1.25x
  political power (`caps_scripted_effects.txt:89-92`). Gate PP + 1.25 x caps yourself in an `else`,
  as round 14's cult decisions did.

- **A targeted decision row fits ~30 characters of name.** In OWB's
  `countrydecisionview.gui:511-561` the name (`monofont_16`, 7 px a glyph, from x 62) and the
  right-aligned cost text (ending at x 432) share one line and overlap, so a long name runs under
  the cost. The cult titles therefore name no country: the row draws the target's flag, and the
  description names it.

- **`create_intelligence_agency` takes its `name` as written.** A loc key there shows raw,
  upper-cased, in the agency screen (ours read MLTD_AGENCY_NAME; OWB says as much at
  `history/countries/ORO - Ouroboros.txt:9`), while an `intelligence_agencies` entry's `names` list
  is localised. So the focus passes "The Esoteric Order of M'lyeh" and `mltd_agency_name` holds the
  same text for the entry and our tooltips - change both. An agency already founded with the raw
  key can be renamed from the agency screen (click the logo).

- **In a decision category description, scripted loc does not run in MLT's scope, and cannot step
  into an array element.** Read everything through `ROOT.`. Stepping into `var:mltd_cult_list^i`
  found nothing in game - bare, the cult list printed "...and -9 more"; inside `ROOT = { }`, still
  no row - so the list reads fixed slots instead: country variables the rebuild writes from inside
  each country (`set_variable = { ROOT.mltd_cult_row_1 = THIS }`), printed with
  `[?ROOT.mltd_cult_row_1.GetName]` (vanilla `[?ROOT.vaps_from.GetName]`).

- **Agency logos are two-frame strips.** 234x119 (two 117x119 frames), uncompressed,
  `noOfFrames = 2`. Frame 1 is drawn at 0.9x over a near-black disc in the agency header, at 0.7x
  on paper in the insignia picker, at 1x in operative events and at 0.3x on operative badges; frame
  2 adds a warm glow (the hover state, inferred). Plain black disappears in the header.
  `create_intelligence_agency`'s `icon` needs only a declared sprite; the
  `common/intelligence_agencies` entry is what a UI-founded agency and the change-insignia list
  use.

- **`$key$` loc nesting resolves one level only, and never to a `replace/` key inside a sentence.**
  A `$key$` whose own value contains another `$key$` is printed raw, and so is one defined only in
  a `localisation/replace/` file (use a scripted-loc function returning the key). See Naming
  conventions > Localisation: functions, not names.

- **Scripted localisation can walk an array.** A `defined_text` whose trigger advances a
  temp-variable cursor (`add_to_temp_variable` and `set_temp_variable` are triggers) and whose loc
  key ends by calling it again prints one row per array element (OWB
  `CAF_scripted_localisation.txt:34-67`). The engine stops the recursion at
  `MAX_SCRIPTED_LOC_RECURSION = 30` (vanilla `00_defines.lua:26`), so cap the rows. A decision
  category's description evaluates scripted loc in the viewer's scope, which the cult list first
  tried (in our category description it printed nothing - see the gotcha on decision category
  descriptions - so it now reads fixed slots) (a `scripted_gui` in the category, vanilla
  `AUS_decision_categories.txt:7`, would be the heavier alternative).

- **A child scripted GUI can extend an OWB window without overriding it.**
  `parent_window_name = "<window>"` attaches our window inside OWB's, in the parent's coordinates
  (OWB's `_organization_market_gui.txt:5` does it to the marketplace itself). The Wet Market leans
  on OWB's names `trade_ledger_window`, `selected_market_organization`,
  `temp_selected_org_inventory` and `caps_market_prevented`, and on the seller bar's layout in
  `interface/trade_ledger.gui`: if OWB renames or re-lays them, the seller silently disappears or
  sits in the wrong place (see Update process). Never store a value of our own in an OWB variable:
  OWB's organisation events (`caps_organization_flavor.txt` .11-.13) set
  `selected_market_organization` when they open and read it back as an index into a 7-slot array
  when their option is chosen, which is why the tab keeps its own `mltd_wm_selected`. Those events
  also hide the panel while one is open, since they select an OWB seller.

- **`set_nationality` moves a character with every role.** A country-leader or advisor role would
  go along with a transferred general, so the operation filters those characters out instead of
  stripping roles. A role with its own `visible` trigger can hide the character in the new country,
  which is why the operation checks visibility after the move and sends the defector back when it
  fails. What happens to the army a transferred general commanded is unverified, hence the
  preference for unassigned generals.

- **`is_historical_focus_on` weights an AI's pick, never a human's.** It reads the game's
  historical-focus setting, in any scope (vanilla `triggers_documentation.md`), and OWB puts it
  inside `ai_chance` modifiers (`events/nevada_pact_events.txt:15-22`). `ai_chance` weights are
  relative, so to make an answer certain on historical, drop the other option's weight to 0
  (`modifier = { is_historical_focus_on = yes factor = 0 }`) rather than raising this one's. Any
  text that tells the player the odds must read the same rule, or it lies in half the games: hence
  the `GetMltd*Odds` functions rather than a fixed line (The story acts > *The invitations*).

- **`create_wargoal`'s `expire` is in days,** and `expire = 0` means never (vanilla
  `bulgaria.txt:8961-8966`, 180 days with its own expiry tooltip; `germany.txt:11189`, 0). The
  effect runs in the scope of the country that gets the war goal, so a refuser's event option gives
  it to MLT as
  `FROM = { create_wargoal = { type = annex_everything target = ROOT expire = 365 } }`; guard it
  with `NOT = { has_war_with = FROM }`, as vanilla does.

- **An exclusion that only a yes should trigger needs a flag, not `mutually_exclusive`.**
  `mutually_exclusive` closes the other focus the moment this one completes, whatever the invitee
  answers - which is right within a nation's Act III pair, a choice between courting and fighting
  it, and wrong across nations. The invitations instead set a flag in the acceptance effect's
  `add_to_faction` branch (`mltd_brk_covenant_joined`, `mltd_wbh_alliance`), and every place that
  must honour it tests it again: the other focus's `available` and reward, and the acceptance
  option's `trigger`. An answer can arrive while the other focus runs (`continue_if_invalid`), so
  the `available` test alone is not enough. Name a pair in both focuses' `mutually_exclusive`: a
  one-sided line lets the unnamed focus be taken after the other.

- **An event option with a `trigger` is hidden while the trigger fails.** `mltd.21`, `mltd.24`
  (since round 28c's review) and `mltd.32` hide their acceptance once the invitee can no longer
  join, which leaves only the refusal. What the engine picks for a human who lets such an event
  time out is unverified.

- **A tall focus icon grows upward.** OWB centres a focus's icon on a point above its name box
  (`nationalfocusview.gui:518-524`), so the extra height of an icon taller than the normal ~92x90
  lands mostly in the row above, and below it the icon covers only its own box. The user's
  round-28c play-test notes: a tall icon needs one empty row above it and the next focus directly
  below it. Two stand on the spine: The Final Ritual's `GFX_goal_CHC_cultists` (266x253), with row
  26 empty above it (row 24 until 2026-09-24), and since 2026-09-24 The Deep Ones Walk's
  `GFX_goal_CHC_mother` (152x171), with row 24 empty above it, both now below Act III. Round 28b
  first left a row empty below it as well; round 28c took that out. The Last King Kneels was the
  other, `GFX_goal_MIN_fallen_kingdom` (164x146) over an empty row 39, until round 28c's balance
  review swapped it for the 100x88 `GFX_goal_TBH_The_Last_Piece` - the cheaper fix, since the art
  was not Texan either - and the spine closed up a row. Prefer that: an icon under about 130 px
  costs no row. The rule for any cell: no icon over about 130 px tall directly below another focus,
  which is why round 28c gave Salt on the Caravan Roads, All Waters Are One and The Dreamer Wakes
  normal-height icons when the spoils moved above them (all measured from the DDS headers). Until
  2026-09-24 the Walk stood directly under The Grand Ritual, an open question its move below Act
  III settled. Still open: The Grand Ritual (152x139) sits directly under the Call (138x139) on
  rows 19-20; if its icon covers the Call's name in game, the fix is an empty row above the ritual,
  or a shorter icon, as the balance review chose for The Last King Kneels.

- **A `NOT` over several triggers is a NOR.** `NOT = { A B C }` means none of them holds, not "not
  all of them" (vanilla writes `NOT = { has_government = X has_government = Y }` over a hundred
  times). To negate a conjunction, write `NOT = { AND = { A B C } }`. The Haida watch had it wrong
  from round 25 to round 28c (*The Broken Coast off Haida Gwaii*).

- **A bypass fires by itself, and ignores `available`.** A focus whose `bypass` holds is completed,
  without its reward, once its prerequisites are done - the engine's automatic bypass - whatever
  its `available` says. Run 8's AI dug the Barrows on day 322, and OWB's Cannibal Territories
  trade, whose `available` asks that the Barrows are not dug, was still bypassed on day 1792, once
  MLT held the state; the AI then took the Muttfruit branch as well. In a branch that must stay a
  choice that forces the path, because a bypassed focus reads as completed and whatever tests that
  it was not taken shuts. `enable_automatic_bypass = no` leaves the bypass to the player: the focus
  lists the condition under vanilla's `BYPASS_FOCUS_TRIGER` ("The following will bypass the focus
  (automatic bypass is disabled):") and offers `BYPASS_FOCUS` ("Bypass") - vanilla's idiom where a
  branch must stay a choice (`china_communist_sea.txt:594`, "So don't force that way"). Put the
  other branch's exclusion into the `bypass` too, since `available` does not stop one, and let
  `available` fail while the bypass holds, as vanilla does there, so that the long way is shut:
  taken the long way, the Cannibal Territories trade would send its offer to MLT itself (its reward
  sends `nf_mlt.4` to the state's owner). Since 2026-09-25 that trade does all three (Overriding
  OWB); unverified in game: how the Bypass is offered - a button, or a bypass on selection. The
  story acts' bypasses (2026-09-23) stay automatic: the two focuses of each Act III pair share one
  target and one bypass, so neither forces the other.

- **OWB's Brotherhood leads the Northern League.** `WBH - Washington Brotherhood.txt` runs
  `create_or_join_northern_league` in its 2275 history, so WBH founds and leads OWB's Northern
  League from the first day, and no focus of the shared Brotherhood tree leaves it. Until
  2026-09-25 Terms for the Citadel asked for a Brotherhood in no faction (`mltd_wbh_terms_target`),
  so it stayed shut while WBH stood in that league - in most games for good. Round 28 never
  checked; Terms' preview, which showed only +50 political power, gave it away. Since then Terms
  may ask a Brotherhood that leads its faction, and a yes brings the members over (The story acts >
  *The invitations*). Who can be in the league, by OWB's own calls to
  `create_or_join_northern_league` and `join_northern_league`:

  - WBH, its founder and leader (the template's `change_leader_rule_never`);
  - The Old Country (TOC), invited by WBH's own focus `WBH_fellow_savages` (`nf_washington.3`,
    `.4`);
  - Yakama (YAK) once it forms the Northern Federation (`formable_nations.txt:1808`), and through
    its decisions Bellingham (BEL) and the Syilx Nation (SYN) (`YAK_decisions.txt`);
  - the Bone Dancers, through `bdt_pact_of_darkness`, which asks the league's leader
    (`nf_bonedancers.8`; an AI leader always says yes) or founds the league if there is none - it
    shuts Hail the Drowned King, which asks for Bone Dancers in no faction;
  - the Swords of Hayman (SOH), through `nf_soh.23`;
  - every member's subjects (`mark_as_northern_league_member`), and anyone the leader invites from
    the diplomacy screen (OWB's `on_offer_join_faction` marks them).

  The Northwestern Brotherhood joins none: forming it (`form_northwestern_brotherhood`) leaves TCA
  outside any faction.

## Testing

After every change, launch the game and read
`C:\Users\jonat\Documents\Paradox Interactive\Hearts of Iron IV\logs\error.log` (truncated each
launch). Localisation key collisions go to `text.log` - the `warbike_unlock_tech` / `_desc`
collision there is the intentional `replace/` override. `system.log` lists `Active Mod:` lines,
which is how you confirm the submod loaded at all.

To reach the content: play MLT, complete `mlt_kingdom_of_mlyeh` (requires owning all cores of TRL,
RBT, CCW, DIS; `mltd.1`/`mltd.2` fire 1-2 days later), then Gifts, the five Books (each needs
control of its state - or, with La Resistance, a 100 % network in it - and is read only when its
three-event expedition ends, 2-4 weeks after the focus), then the centre column (Call needs 1 Book,
the Grand Ritual 3, the Walk 5; Call and the Walk each open a one-option event that applies their
effects). Since 2026-09-24 each of Act II's branches under The Grand Ritual leads to its nation's
Act III pair, any one of which opens the Walk, and the Walk the Final Ritual (from round 27, any
one Act II branch under the Walk opened the ritual), and the story acts follow down the spine (see
The story acts). Round 9 items to confirm first: **M'lulu's portrait rains** in the politics view
and the general list (and her small icon is the graded card, not a slice of the strip); the Kingdom
focus tooltip lists the two victory-point gains and the map shows M'lyeh at 25 VP; **Summon the
Deep Ones stays listed and greyed with a day count** after a summon instead of disappearing, and
reappears when its cooldown ends; the two Offerings decisions pay caps (top bar updates
immediately) and permanent water in the capital; *Feed the Spawning Pools* appears in the
continuous-focus palette for MLT (and only MLT), costs its daily political power and shows -15 % on
all three creature archetypes while selected, and the discount disappears when a different
continuous focus is chosen; a Star Spawn division still spawns fully equipped, with 16 spare in the
stockpile. Then: the startup `error.log` no longer has the four `script_enum_equipment_bonus_type`
warnings for `mltd_*_equipment*` or the two
`recruit_character should only happen in game/history files` lines for `events/mltd_events.txt`
(the last play-test's only lines that were ours); the Drowned Herald is absent from the general
list at start and appears there, 4 / 4-2-2-1 with his portrait, right after `mltd.1`; the Deep Ones
tech shows in the **Reward Technologies** tab; gifts apply the moment the decision is taken and
expire after 30 days; a summoned division spawns **with its equipment** (the hidden
`Spawn of the Deep` tech appears in the equipment's tooltip; 32 / 16 spare in Logistics) in the
state that paid for it; the ritual focus tooltip shows the red modifier lines with values; the
ritual idea appears when the focus is *selected* and disappears on completion, and the toll ticks
daily in between; the Deep Ones template becomes trainable after focus 4 and its equipment
producible; the operation appears once an agency exists (La Resistance) and MLT has a network in a
neighbour with > 1,000 manpower.

Round 13 items to confirm (the flavour events, the Book expeditions and the old conflict focuses,
which since round 27 sit in the story acts; none play-tested yet). The sub-trees' layout, root and
intel-gate checks are gone - Round 27 below replaces them:

- **Startup logs.** `error.log` has nothing naming a story-act file (`mltd_act2_focus.txt` ...
  `mltd_finale_focus.txt`), `mltd_scripted_triggers.txt`, an `mltd_ncr_` / `_tex_` / `_wbh_` /
  `_ces_` / `_bos_` / `_tla_` / `_hea_` / `_wht_` / `_ate_` id, `mltd_intel_foothold` or
  `mltd_flavour_can_fire`, and `text.log` reports no missing key for them.
- **The agency.** With La Resistance, *The Spreading Cult* founds *The Esoteric Order of M'lyeh* if
  MLT has none, and every spying head (the eleven focuses that call `mltd_intel_foothold`) taken
  once the agency exists adds exactly one upgrade, leaving the caps balance where it started; one
  taken before then pays +50 PP instead. A balance one upgrade's price higher means script upgrades
  are not charged and the refund must go; that much lower means the refund failed.
- **Intel gates.** Only the invitations have any since round 27, and since round 28c's balance
  review all three do: each stays greyed until its invitee's cult, civilian token and coverage
  lines pass. A 25 % threshold that is actually reached confirms the 0-1 scale. A focus-granted
  `token_army` opens OWB's steal operations against that target.
- **Theft.** Each theft lowers the victim's stockpile by exactly the amount taken. Act II's show in
  MLT's Logistics under the victim's name; since rounds 28b-28c those of Acts IV-VI pay mirelurks
  instead (Rounds 28, 28b and 28c below).
- **War gates** (the story acts' war focuses) follow the world: a Hoover outcome flag or 1 June
  2279; `texas_formed` or 2280; WBH's purge, war with MLT or 2280, **and** The Warren held;
  Heaven's Guard's holy wars or 2280; the Utah road war or 2280.
- **Tlaloc.** The Drowned God Sleeps cuts `TLA.current_databanks` by 64 (its tooltip prints live
  numbers), never below 36, and OWB's own death event still fires on schedule.
- **The Warren** gets its four bunkers and loses WBH's claim.
- **No DLC.** With La Resistance disabled in the launcher, every act can be taken end to end and
  pays PP and tech bonuses instead.
- **Flavour events.** No flavour event arrives within 90 days of `mltd.1`. After that they come
  every few months, never two within 120 days, each at most once. `mltd.11` / `mltd.16` appear only
  after the Call, `mltd.14` only after the first Book, `mltd.18` only with the capital controlled.
  `event mltd.9` ... `event mltd.18` in the console previews each: `.d` text readable on the pale
  paper, option text plain, and `mltd.9` option c greyed without the caps it costs.
- **Book expeditions.** Completing a Book focus fires its chain two days later; every option shows
  *The expedition presses on.* and the next event arrives one to two weeks later. The gift decision
  and `mltd_books_read` change only at the third event. In 202 / 302 / 502 the chosen advisor
  leaves the advisor list for good, their option is gone from later events, and with both gone only
  the third option shows. 401's buy option is greyed without the caps it costs; 402's first option
  adds 500 people to the capital.
- **Old Castro.** He appears among the cultural advisors only with La Resistance, greyed until MLT
  has an agency. Hiring him raises the agency screen's operative slots by 2 (to 3, or 4 after four
  upgrades), and OWB's steal-tech operations become runnable.
- **Cult Infiltration** (as of round 17). After *The Spreading Cult* the category opens with the
  two Calls, and every neighbouring major (at war, OWB makes every non-subject belligerent one)
  already holds a cult at 20 %. With La Resistance the intelligence screen offers *Found a Cult* on
  any country with network coverage and no cult (equipment, no caps; the cult starts at 10 %) and
  *Nurture the Cult* on any cult below 100 % (equipment; +12). The category lists every cult, and
  each loses about 0.1 + s\*s/3000 a week (since 2026-09-23), half that in a country a story act's
  spying head has sheltered. *Call for People* / *Call for Equipment* pay 10 manpower, or 4
  infantry + 1 support equipment (1 mirelurk from Mars in the Water on, round 28b), per point of
  total strength, and stay listed, greyed with a day count, between calls. At peace the target
  shows no *Drowned Faithful* effects; war applies them at once and triples the loss. Below 1 % the
  cult vanishes.
- **Round 14.** Fully restart first - a console reload makes new definitions look unknown. The
  Spreading Cult and The Wet Market sit side by side a row under the Kingdom's three OWB children,
  with Gifts a row lower, no overlaps, and lines from the Kingdom to both. The Spreading Cult opens
  Cult Infiltration, founds a cult at 20 % in every neighbouring major (small neighbours get none
  unless they are at war and not a subject, which makes them OWB majors), and founds the Esoteric
  Order only if MLT has no agency. The Wet Market adds its idea and, with the caps rule on, +40
  influence with all five Organization Marketplace sellers. At war with a cult's country, its
  *Drowned Faithful* modifier also shows more air accidents. A Book focus goes green with a 100 %
  network in its state (La Resistance) and shows only the control line without the DLC. The
  category pictures no longer cover the orange and red frame line.
- **Round 15.** Fully restart first. *The Spreading Cult* plants cults only in neighbouring majors
  (at war, OWB makes every belligerent that is not a subject a major). The Esoteric Order, founded
  by the focus - or from the intelligence screen, where it should be the pre-selected name and
  insignia - shows the gold-on-teal seal in the agency header, the insignia list, operative events
  and operative badges, and its hover state glows. *Hail M'lyeh*: with La Resistance, an agency and
  a network in some country without its civilian token, `event mltd.19` in the console names that
  country and its leader, the option grants its civilian infiltration token and 10 civilian intel,
  and the event cannot come again for a year.
- **Round 16.** Fully restart first.
  - The Grand Ritual's gifts give +20 weekly manpower and the Final Ritual's +40. The Wet Market
    focus shows +40 influence with each seller, +20 % caps income, a consumer-goods penalty and the
    new seller line.
  - The Cult Infiltration description ends with *The faithful abroad:* and one row per cult - flag,
    name and strength, strongest first, at most 8 and then "...and N more" - or *No cult of M'lyeh
    has taken root yet*. It updates after a cult decision, after *The Spreading Cult* and every
    day. If the flags do not render inline, drop `GetFlag` from `mltd_cult_list_row`.
  - *Indoctrinate the Faithful*: a target shows exactly one variant, by its manpower band (greyed
    below the lowest). It moves that band's manpower and nothing else, and its equipment price does
    not rise on a repeat. On a critical success (temporarily set `outcome_extra_chance = 1` to
    force one) an idle general of the target - never its leader, an advisor, a field marshal or a
    story general - appears among MLT's generals with their skills and traits and `mltd.20` names
    them; with no eligible general only the manpower moves.
  - The Organization Marketplace shows a **The Wet Market** button at the end of the seller bar's
    second row (for MLT always, for others once it opens); hovering it shows *Market Open* (No
    before the focus) and *Available for transaction* (No, with the days left, after a trade).
    Selecting it replaces OWB's item list with four mirelurk rows laid out like OWB's (the icon in
    its dark inset, *In Stock*, *Requires: The Wet Market*, *Buy For* / *Sell For*); selecting an
    OWB seller hides them again (closing the window keeps the selection). Before the focus every
    buy button is greyed with *M'lyeh has completed The Wet Market* (MLT's name and flag); after
    it, a lot costs its price in caps, adds 250 of that variant to the stockpile, lowers the stock
    by 250 and starts the trade cooldown, selling 250 back pays OWB's resale share of the price and
    adds them to the stock, and the stock rises by 250 a month while below 2,500. The button and
    panel positions are calculated, not seen: nudge `interface/mltd_wet_market.gui` if needed.
- **Round 17.** Fully restart first.
  - A summoned Deep Ones or Star Spawn division arrives fully equipped with 32 / 16 spare in
    Logistics, not a second division's worth.
  - With the caps rule on, the Kingdom's tooltip says M'lyeh becomes an economic node. Afterwards
    the node shows on the Trade Nodes map mode and in M'lyeh's state view (level, progress, value);
    *Invest Stimulus in M'lyeh* appears among the decisions; and the caps ledger shows a Trade
    Nodes line at the next tick. Note the level the node settles at: OWB's square-root helper may
    keep a new node at level 0.
  - Cult Infiltration as above: the operations appear in the intelligence screen against a country
    with a network, cost equipment and no caps, and the Calls pay on the total.
  - Each spying head's tooltip names the countries whose cults now wither half as fast; each war
    focus shows a native declaration line for each living target (round 22), and taking it starts
    that war the day it completes.
  - `python check_plan_sync.py` passes.
- **Round 18 (MLT's AI).** Fully restart first and run `python check_plan_sync.py`; `error.log`
  names none of the five AI files. Then watch an AI MLT (play a neighbour, or `observe`):
  - it justifies on CCW within the first weeks, then on TRL once it holds CCW's land and on RBT as
    that war starts, and takes the Oregon focuses in the plan's order (the Barrows, never
    Muttfruit);
  - it trains Coral Hosts, then Shell Levies after Black Hollows Night and Tide Walls and Deep Ones
    after The Deep Ones Walk, and its templates match those roles;
  - with DIS holding `DIS_mend_schism` it leaves DIS alone until `nf_dis.4`; without the flag it
    takes DIS after RBT;
  - after the Kingdom it goes for PMR and ARR, reads all five Books, and summons or makes offerings
    only with the population to spare for the next ritual;
  - with La Resistance, `mltd_ai_cult_target` appears on MLT within a week of *The Spreading Cult*
    and the agency runs *Found a Cult* / *Nurture the Cult* there; now and then it buys a Wet
    Market lot;
  - no new war starts while The Final Ritual runs, and it takes no war focus before its stage
    (since round 27 the tree itself keeps the Legion's behind the NCR's close) - since round 22 the
    war focus is the declaration;
  - its peace deals take states, never puppets. Note every construct marked unverified that visibly
    fails.
- **Round 20 (MLT's AI after run 2).** Fully restart, run `python check_plan_sync.py` and
  `python ai_run_report.py --selftest`; `error.log` names none of `mltd_MLT_frontier.txt`,
  `mltd_ai_survey_effects.txt` or `mltd_ai_triggers.txt`. Then, in a spectator run:
  - no war with the NCR or any country on its side before the report's STAGE `id=north` and STAGE
    `ncr` lines (check l), and none on Arroyo once it has joined the NCR's faction; if Vault City,
    Elko or S'Lanter are on the NCR's side, New Reno falls first;
  - whoever takes Oregon ring or Cascadian land becomes a target after the Kingdom, unless a strong
    ally stands behind it;
  - with La Resistance, Old Castro is hired within a year of *The Spreading Cult* (check o), the
    cult target moves to the NCR after The Deep Ones Walk and the NCR's cult stands at 40 % when
    that war starts (check n), and Book 4 comes through a network in Arroyo if Arroyo is on the
    NCR's side;
  - SNAP's `divs` stays near `target` (check p), and after the NCR is beaten the Shell Levies and
    Coral Hosts turn into 8-mirelurk divisions;
  - a POCKET line, if one appears, is followed within months by military-access requests (the
    diplomacy view) or a war on the country in between, and by POCKET `state=end` (check m); every
    enemy with land gets a manned front;
  - after The Final Ritual, offerings only when caps run short (check q).
- **Round 21 (after run 3).** Fully restart, run `python check_plan_sync.py` and
  `python ai_run_report.py --selftest`; `error.log` names none of `mltd_ai_frontage_effects.txt`,
  `mltd_opinion_modifiers.txt`, `mltd_factions.txt` or an `mltd_brk_` id. Then:
  - in a spectator run, SNAP's `frontage` is in the hundreds once MLT borders Cascadia, `divs`
    climbs towards `target` (check p) and the AI's caps go on OWB's sellers (their 40-day trade
    flags on MLT); it declares on no country stronger than itself after the Kingdom;
  - Salt on the Broken Coast (an Act II head since round 27) lifts the -25 opinions both ways and
    shows +25. The Deep Ones Sail North raises the Send Volunteers limit towards a warring BRK by 6
    \- it absorbed Star Spawn over the Strait's +3 in round 27 - and its tooltip shows one +6 line,
    not two +3s. The limit shows in the diplomacy action's tooltip, and the modifier *The Tide
    Sails North* appears;
  - the Covenant stays greyed until its cult, token and coverage lines pass (since round 28c's
    balance review that is all it asks: the coast and the civilian-intel lines are gone);
    `event mltd.21` sent to BRK (console as BRK, or `observe`) founds *The Drowned Covenant* with
    the Cascadia pirates' logo and BRK in it, with +75 opinion both ways; since round 28 a
    historical AI BRK never refuses and an unhistorical one refuses half the time, and a refusal
    gives -25, a war goal that expires after a year, and opens the AI MLT's conquest block for BRK
    again;
  - an AI MLT never declares on BRK after the Kingdom while courting it, and its cult target moves
    to BRK once a network exists there;
- **Round 22 (after run 4).** Fully restart, run `python check_plan_sync.py` and
  `python ai_run_report.py --selftest`; `error.log` names no `mltd_bdt_` or `mltd_wbh_brotherhood`
  id. Then:
  - taking either of Hail the Drowned King and Drown the Dance greys out the other (both ways since
    round 28b; one-sided from round 24 to round 28);
  - the Washington focuses work while either Brotherhood holds Washington, its thefts and penalties
    land on whichever does, and after TCA forms the Northwestern Brotherhood (its formable
    decision) the focuses still work and The Tide-Wall removes TCA's claim on The Warren;
  - `event mltd.24` sent to BDT founds or joins the Drowned Covenant exactly as the Broken Coast's
    does;
  - in a spectator run, the AI still declares its early wars with a dozen divisions (the readiness
    line is capped at 20), the STAGE or frontier target it declares on has its armies on that
    border first, and while the line is short its new divisions are Shell Levies - pure militia
    until it has mirelurks to spare (run 5 held 4,000 infantry weapons and 9,000 manpower without
    raising one);
  - a war focus declares its war the day it completes, and the target has had the focus's length of
    warning (`will_lead_to_war_with`). after The Final Ritual, while BRK is at war and MLT at
    peace, it sends volunteers (BRK's army list) and the report's STAGE `ncr` line comes only after
    they have served 26 weeks, BRK makes peace or holds its coast, or 2283.
- **Round 24 (the review fixes).** Fully restart, run `python check_plan_sync.py` and
  `python ai_run_report.py --selftest`; `error.log` names none of `never_return_stolen_territory`,
  `mltd_<tag>_network_<pct>_tt` or `mltd_wht_sold`. The telemetry stays **on** for these two runs;
  silence it only at the upload (Plan > High priority). Then:
  - **In a spectator run (the one that matters).** MLT's `owned=` in SNAP never falls at peace -
    that is the give-away, and the whole ritual column depends on it. Watch the day-1090-to-1130
    window of run 8's shape: a jump from `owned=15 pop_k=98` back to `owned=5 pop_k=31` with no WAR
    line means `never_return_stolen_territory` did not take. Then: check (o) - Old Castro hired
    within a year of The Spreading Cult, `slots=4` in SNAP afterwards, and political power no
    longer banking past ~500 unspent; check (i) now reads N/A until `mltd_ai_late_army` opens, so a
    FAIL there is a real buyer fault; and the AI reaches the Grand Ritual's 100,000 gate at all,
    which no run has yet.
  - **The coverage tooltips.** Since round 27 only the Covenant's and Hail the Drowned King's
    remain, and they show their real thresholds - *More than 30%* and *More than 25%*, not *More
    than 0%*. The other 33 went with the story acts' intel gates.
  - **The Wet Market with the caps rule OFF.** The focus pays +50 PP and grants **no** idea; with
    the rule on it grants the idea as before. Previously the rule-off player got the consumer-goods
    penalty and nothing else.
  - **Washington.** Once WBH is annexed, Eyes in the Sound and The Drowned Knights stop advertising
    and paying `add_intel` against it; if TCA has formed the Northwestern Brotherhood they pay
    against TCA instead. The Tide-Wall warns both Brotherhoods in its native declaration lines, and
    its idea's bonuses apply to whichever one it declares on.
  - **Guns for Both Sides** (inside The Lake God Answers since round 27) with one side already
    dead: MLT loses 200 rifles, not 400, and is paid 100 caps, not 200. Since round 27 it also
    sells nothing to a side at war with MLT.
  - **The Bone Dancers.** An AI MLT leaves BDT alone from the Kingdom on while the invitation can
    still be made, not only after `mltd_bdt_the_bone_shore`; and if BDT takes
    `bdt_listen_to_the_pilgrims`, the courtship ends and the war branch opens. (Round 24 read OWB's
    Odious King branch instead, so `bdt_road_warriors_of_the_eighty_four` also ended it; round
    28c's balance review left only the pilgrims' road.) As a human BDT, refuse the Covenant in
    `mltd.24` and confirm that MLT holds a war goal on the Bone Dancers for a year and that The
    Tide Turns South opens through Hail (since round 28b *Drown the Dance* is closed once Hail
    completes; until then a refusal had to leave it takeable).
  - **The Deep Ones summon** between the two rituals: an AI does not summon the nation back under
    200,000.
  - **Nurture the Cult** on a cult that withers away mid-operation: the operation greys out rather
    than completing and re-founding it.
- **Round 25 (the Broken Coast off Haida Gwaii).** Fully restart and run
  `python check_plan_sync.py` and `python ai_run_report.py --selftest`; `error.log` names neither
  `mltd.27` nor `mltd_brk_on_haida_gwaii`. Then, in a spectator run where MLT has taken Salt on the
  Broken Coast and the Broken Coast goes to war with the Haida Confederation: the report's timeline
  shows `HAIDA: the Broken Coast lands on Haida Gwaii`, and - if it is thrown back -
  `HAIDA: ... thrown off Haida Gwaii - white peace` on the same day the war between BRK and HAI
  ends (the `game.log` line `event mltd.27`). No repeated landings after that, and MLT's volunteers
  in BRK come home. To force it in a test, `event mltd.27 HAI` from the console makes the peace at
  once. With a human on either side the watch stays off, and a war that ends any other way leaves
  no stale flag behind - since round 28c also one that ends with the raiders still ashore (the
  `NOT = { AND = { ... } }` fix). While MLT itself is at war with the Broken Coast (The Coast Goes
  Under, or a refused Covenant's war goal) there is no HAIDA line and no peace, and
  `event mltd.27 HAI` makes none.
  - **Old Castro** (the round-25 correction). With La Resistance, the report's ADVISOR line for
    `MLT_OLD_CASTRO` appears within a year of The Spreading Cult (check o), and SNAP's `slots=`
    rises by 2 afterwards. If he is *still* never hired, `cultural_advisor` is not accepted as a
    `pp_spend` id after all - look in `error.log` for a line naming it - and the remaining lever is
    the plans' own `ideas` weight; his `ai_will_do` has already been raised to OWB's own 10003
    (round 28c's balance review), the weight this note first proposed.
  - **The report.** Check (i) reads N/A unless MLT was under 250 mirelurks with over 300 caps after
    `mltd_ai_late_army` opened - so a FAIL there is now a real buyer fault - and check (j) judges
    the Deep Ones summons between the two rituals against 200k (run `20260918-170847`'s four came
    at 245k, 235k, 227k and 216k).
- **Round 26 (the Leviathan).** Fully restart and run `python check_plan_sync.py`; `error.log`
  names no `mltd_leviathan`, `tech_naval.txt` or `history/units/mltd_leviathan*` line. Then: the
  Grand Ritual's tooltip lists the Leviathan tech, the ship and the decision; on completion one
  ship, "Father Dagon", appears in a fleet at Mireport, marked pride of the fleet (with Mireport
  lost, the tooltip says none surfaces and the first summon brings the pride instead); the naval
  tech tab shows *The Leviathan* researched below the Personal Floating Palace (and not at all for
  other countries); the ship designer offers no slot on it and the production screen cannot queue
  it; its stats read about a fitted Floating Fortress, fuel 0, visibility 8, range 6,000, and the
  navy weather penalty shows -50 %; *Summon the Leviathan* costs 24,000 people and 100 PP, adds one
  more ship at Mireport and stays listed with a 180-day countdown; with Mireport lost, the decision
  greys out. Unverified: that `load_oob` accepts a non-modular hull (the Palace's OOB, the
  precedent, loads a modular one bare), that `allow_branch` hides a path child, and how far the 2.5
  `hit_profile_mult` evens out its visibility in combat.
- **Round 27 (the story acts).** Fully restart - a console reload makes new definitions look
  unknown. Run `python check_plan_sync.py`, `python build_telemetry.py` (it must not fail its
  `STORY_FILES` assertion) and `python ai_run_report.py --selftest`. `error.log` must name none of
  the six story files, `mltd_texas_beaten`, `on_capitulation`, an event `mltd.30-74` or a round-27
  idea, and `text.log` must report no missing key for them. Then check:
  - **The layout** (rows as of 2026-09-24). MLT's tree shows one spine down x = 15 below The Grand
    Ritual, as in The story acts > *Positions*, and nothing overlaps:

    - Act II's three branches sit on rows 21-22 at x 11 / 15 / 19, with lines from The Grand
      Ritual.
    - Act III sits on row 23 at x 10-20, each pair either side of its nation's Act II bead, with a
      line from it.
    - The Deep Ones Walk sits at (15,25), under an empty row 24, with six dashed OR lines from Act
      III, and The Final Ritual at (15,27), under an empty row 26, with one line from the Walk.
    - The acts continue down to the endings on row 42, with the mutual-exclusion markers between
      the endings and within each of Act III's three pairs.
    - The old sub-tree boxes left and right of the trunk (rows 13-23) are empty.
    - DIS's tree, which shares the `lurk_` roots, shows none of it.

  - **Acts II and III.** Since 2026-09-24 The Deep Ones Walk opens after any one Act III focus (and
    five Books), The Final Ritual after the Walk (and 200,000 people), and each Act III pair only
    after its nation's Act II bead. The Deep Ones Sail North shows one "+6 volunteer divisions"
    line. With a target annexed from the console, its head and bead are still takeable and pay
    political power.

  - **Act III's close.** The Tide Turns South needs The Final Ritual and 50 controlled states, or
    the year 2281 (its tooltip names both). Its idea shows the -25 % justification time. `mltd.30`
    has two options, and `mltd.31` reaches other countries only. The Covenant pays +50 PP once the
    Broken Coast is gone or MLT's subject. Drown the Dance and The Coast Goes Under are takeable
    once their target is gone or MLT's subject, and pay +50 PP.

  - **Act IV.** The Turbines Sing opens after any one of the three beads. When Shady Sands Falls
    stays greyed until the NCR has capitulated, is gone or is MLT's subject.

    - After a peace that leaves a rump NCR alive, it is still takeable: `on_capitulation` set
      `mltd_ncr_capitulated` on MLT.
    - Its tooltip previews both of `mltd.40`'s options. Option a adds a research slot, MLT's fifth
      since round 28c's balance review; option b adds `mltd_the_drowned_rangers` and the army
      experience.

  - **Act V.** When the Legion Breaks behaves the same way for the Legion (`mltd_ces_capitulated`).
    Its tooltip previews both of `mltd.51`'s options (since round 28b the ideas
    `mltd_the_unchained` and `mltd_the_pens_emptied`, with its days - round 27's check of a
    population preview is moot). The Lake God Answers never sells guns to a side at war with MLT.

  - **Act VI.** The Feathered Tide and The Serpent Drowns work on Nuevo Aztlán:

    - the shelter;
    - the Speaker's extra war-support loss while `ATE_speaker_yesenia_aztlanl` rules;
    - the navy experience once ATE has `ate_serpent_rises`.

    The Last King Kneels opens once both TBH and LNS are gone, capitulated, recorded
    (`mltd_tbh_capitulated` / `mltd_lns_capitulated`) or MLT's subject, and adds
    `mltd_the_drowned_south` - no research slot since round 28c's balance review moved it to Act
    III's close.

  - **The finale.** R'lyeh Rises needs 300 controlled states, and the map shows M'lyeh with the
    Kingdom's and the finale's victory points. Taking one ending greys out the other two. Return to
    the Sea raises two Leviathans at Mireport (two task forces), or says why not when Mireport is
    lost. `mltd.72`'s "Iä!" renders.

  - **In a spectator run.** The report's FOCUS lines follow the acts in order. The Broken Coast
    branch comes right after The Grand Ritual, then an Act III focus, The Deep Ones Walk and The
    Final Ritual. No war focus is taken before its hold lifts - The Turbines Sing only after the
    report's STAGE `ncr`, The Tide-Wall only after STAGE `wbh`, Drown the Dance only from 2281
    while the Bone Dancers are courted - because each hold is now in the focus's `available`. Each
    close follows its capitulation. Past ~2.15M people SNAP's `pop_k` keeps climbing while the
    Leviathan summon stays available (the population cap).

  - **Unverified**, watch for:

    - the listed shared focuses whose prerequisite is a national focus, and The Deep Ones Walk's OR
      (the Final Ritual's until 2026-09-24) over shared focuses (vanilla's Congo precedent, never
      seen in OWB);
    - `relative_position_id` to a shared focus in another file;
    - a scripted-effect call inside `effect_tooltip` (When the Legion Breaks' preview of `mltd.51`,
      since round 28b; `effect_tooltip` itself is OWB's own idiom, in 45 of its focus files);
    - `has_war_with = MLT` inside `on_capitulation`;
    - two `mltd_brk_add_volunteer_size` calls making +6, and two `load_oob` calls on one day;
    - the nested trigger `if` in the Covenant's `available`;
    - an AI skipping a war focus while its `mltd_ai_may_*` hold fails (the hold is hidden in
      `available`; run 8 showed `ai_will_do` 0 is no hold).

    Expect idle stretches: the focus slot idles for months during each great war while its close
    waits, with only OWB's `lurk_` focuses to fill it (Plan).
- **Rounds 28, 28b and 28c (the invitations, the pairs, the spoils and the rewards).** Fully
  restart. Run `python check_plan_sync.py`, `python build_telemetry.py` (its `STORY_FILES`
  assertion expects seven files), `python ai_run_report.py --selftest`,
  `python story_rework/tools/grid.py` (no overlaps, no cell off SPEC_R28C) and
  `python story_rework/tools/locaudit.py` (exit 0). `error.log` must name none of
  `mltd_spoils_focus.txt`, `mltd_wbh_terms_target`, `mltd_wbh_join_the_covenant`,
  `mltd_brk_the_coast_goes_under`, `mltd_ai_may_offer_the_citadel`, `mltd_ai_may_drown_the_coast`,
  `mltd_ai_hold_refusal_wargoal_*`, `mltd_legion_pens_freed` / `_fed`, `GetMltdBrkOdds` /
  `GetMltdBdtOdds` / `GetMltdWbhOdds`, `GetMltdBunkerName`, `GetMltdArmsFactoryName` /
  `GetMltdCivilianFactoryName`, an event `mltd.32-34` or an idea of these rounds (the spoils',
  `mltd_the_unchained`, `mltd_the_pens_emptied`), and `text.log` must report no missing key for
  them. The console's `focus.autocomplete` reaches Act III quickly; `focus.nochecks` does too, but
  it skips the very gates below, so turn it off before checking one. Then:
  - **Forcing an answer.** Every effect of an answer runs through FROM, which only the focus sets
    to MLT, so let the focus send the offer - and take each invitation from a save of its own,
    since it closes its war twin.
    - *To answer it yourself*, pause on the day the focus completes and switch to the invitee:
      `tag BRK` for The Drowned Covenant (`mltd.21`), `tag BDT` for Hail the Drowned King
      (`mltd.24`), `tag WBH` for Terms for the Citadel (`mltd.32`) - `tag TCA` once WBH is gone or
      someone's subject. The invitation opens for you the next day with both options. Choose, then
      `tag MLT` to read the reply (`mltd.22` / `.23`, `.25` / `.26`, `.33` / `.34`).
    - *To see an AI's pick*, stay MLT. With historical focuses on (the game setup's setting), the
      Broken Coast accepts and the Brotherhood refuses, every time. With them off, keep a save from
      before the offer and reload it until both answers have come up. An AI Bone Dancers accepts
      either way, so their refusal can only be seen by answering as BDT.
    - `event mltd.32 WBH` from the console opens the event too, but which country it sets as FROM
      is unverified, so do not trust its effects.
  - **The layout** (round 28c; rows as of 2026-09-24). Act III on row 23 at x 10-20 in three pairs,
    an exclusion marker within each pair, a line from each nation's Act II bead to its pair and
    from all six to The Deep Ones Walk at (15,25). Rows 24 and 26 empty above the Walk's and the
    ritual's tall icons, with The Final Ritual at (15,27) and The Tide Turns South directly below
    it at (15,28), no icon covering a focus; since round 28c's balance review The Last King Kneels
    (15,40) wears a short Texan icon, its empty row is gone and R'lyeh Rises sits directly under it
    on row 41. Salt on the Caravan Roads, All Waters Are One and The Dreamer Wakes show their
    normal-height icons clear of the spoils focus above them. Look at rows 19-20 too: if The Grand
    Ritual's icon covers the Call's name, that is the open question under Gotchas > *A tall focus
    icon grows upward*.
  - **The odds lines.** Each invitation's description ends with a line that follows the setting and
    the invitee. The Covenant's reads *The raiders will take the offer* on historical and *as
    likely to take the offer as to spit on it* off it. Terms' reads *The Brotherhood will refuse*
    on historical; off it, the Washington Brotherhood's even odds or, once WBH is gone or someone's
    subject, the Northwestern Brotherhood's *perhaps one chapter in ten*. With a human invitee
    (after a `tag`), the line says the answer is theirs. The Northwestern Brotherhood's name may
    print without an article: OWB defines no `_DEF` key for its cosmetic. The Coast Goes Under's
    description has no odds line: it is a war.
  - **The pairs.** Taking any Act III focus greys out its twin with the native exclusion line, both
    ways: Terms and The Tide-Wall, the Covenant and The Coast Goes Under, Hail the Drowned King and
    Drown the Dance. The Deep Ones Walk opens through any one of the six.
  - **Terms for the Citadel** sits at (10,23). It stays greyed until The Drowned Knights is done, a
    free Brotherhood at peace with MLT holds Washington, MLT is free or leads its faction, and the
    Broken Coast has not joined the Covenant. Its tooltip shows the offer, what a yes brings and
    what a no leaves.
  - **An accepted Terms.** The Brotherhood joins *The Drowned Covenant* (founded if MLT led no
    faction; the tooltip's line names it joining), both sides show +75 opinion, its claims on MLT's
    land - The Warren's above all - are gone, and `mltd.33` arrives. The Covenant (while the Broken
    Coast lives) greys out with its alliance line. Hail the Drowned King and Drown the Dance do
    not.
  - **An accepted Covenant.** Terms greys out with its Covenant line, and The Coast Goes Under with
    the exclusion.
  - **The Coast Goes Under** (16,23), against a living Broken Coast at peace with MLT: the tooltip
    shows the native declaration, its 180-day idea and The First Wave (since 2026-09-24; the
    raiders' stability and war-support losses and the army experience before); on completion the
    war starts, MLT's volunteers in BRK come home, and the Haida watch goes quiet. With the raiders
    annexed from the console it is bypassed; with them MLT's subject it pays +50 PP; with them
    invited into MLT's faction from the diplomacy screen it greys out.
  - **A refusal**, in each of `mltd.21`, `mltd.24` and `mltd.32`. The refusing option shows
    vanilla's *War goal expiration time* line with 365 days, and afterwards MLT holds an annexation
    war goal on the refuser that is gone a year later if unused. The other nations' invitations
    stay open, the refuser's own war twin stays closed, so the war goal is the only road left to
    that war. After a refused Terms The Warren gets no bunkers and the Brotherhood keeps its claim.
  - **The race.** Answer one invitation as the invitee only after MLT has picked the other (switch
    with `tag`), and accept: the other focus completes for +50 PP and sends no offer. An invitee
    whose door closed while its offer was on the way sees only the refusal - since round 28c's
    review in `mltd.24` too: annex or bind the Bone Dancers from the console while Hail runs, and
    Hail pays +50 PP.
  - **The previews** (round 28b's rule). Every tooltip is true in every branch it names:
    - the Kingdom, the Call and the Walk show *The event brings:* and the option's effects - the
      Drowned Herald as a general with his skill and traits, the Call's army experience, the Walk's
      tech, idea, template and Star Spawn - and match the events;
    - The Drowned Knights, The Dancers Hear the Tide and The Tide-Wall show their thefts, bunkers
      and claim removal as lines that hold whatever the victim's store or The Warren's owner is on
      the day; a spying head with La Resistance and no agency yet shows both the +50 PP and the
      upgrade;
    - each Act IV-VI theft prints, in one line, the victim's share and the mirelurks paid as the
      stores stand (since 2026-09-24 with no floor; the Hoover rout, Caesar's health, Lost Hills'
      quarrel, the White Legs' gods, the Speaker and the Frogs, which round 28b previewed with
      every outcome, are gone);
    - When the Legion Breaks previews both of `mltd.51`'s ideas, `mltd_the_pens_emptied` with its
      days;
    - the offerings state the rule for their random state, and the summons' tolls read as totals;
    - since round 28c's review: *The Spreading Cult* and What the River Carries, with La Resistance
      and no agency, name both outcomes (found one from the intelligence screen while the focus
      runs: +50 PP, or the operative offered for recruitment); The Grand Ritual's Leviathan line
      says Mireport is tested again at completion; The Foundries Relit shows its construction bonus
      and the +50 PP while `construction_industry_tech_6` is unresearched; and after an accepted
      Terms or Hail, The Drowned Knights and The Dancers Hear the Tide take nothing from the ally
      and pay +25 PP.
  - **The rewards.** A theft takes exactly the share printed from the victim's store (check the
    victim's Logistics after a `tag`) and pays one mirelurk of MLT's best breed for every five
    pieces - check the breed after the king or armour form. `mltd.51` a adds `mltd_the_unchained`,
    b `mltd_the_pens_emptied`. `mltd_the_legions_steel` shows defence and armour on the three
    creature archetypes, `mltd_the_return_to_the_sea` population growth and three build-cost lines,
    and `mltd_tex_black_water` no build-cost line and no energy. *Call for Equipment* pays
    mirelurks from Mars in the Water on.
  - **The spoils** (round 28c). Ten focuses flank the chapters on rows 29, 33, 37 and 41
    (*Positions*), nothing overlapping, each with a line from the previous act's close beside its
    chapter's - check that it reads as the spoils focus's own, above all where a spoils focus sits
    directly above a chapter's child. Each stays greyed until its land is held (annex a theatre's
    owner from the console to test); the idea focuses' tooltips show their controlled-state counts,
    and The Office of Salt and Industry greys until The Hub or Sac-City is held.
    - The Drowned Sound, The Foundries Relit and The Iron Tithe add a building slot (two in the
      Legion's cities) and a finished factory (two) in each listed state MLT owns and controls, and
      nowhere else; try one in a state MLT holds without a core, whose building slots OWB's
      non-core penalty halves. Salt in the Canals and The Salt Road hatch mirelurks per held NCR
      core and per held Gulf port.
    - The Foundries' construction bonus becomes +50 PP once MLT has `construction_industry_tech_6`.
    - In the focus view's search, the Industry filter finds all ten, and the Research filter The
      Scribes' Vaults, The Drowned Sound, The Office of Salt and Industry and The Black Water
      Wells. With the caps rule off, The Salt Road's caps income does nothing while its other two
      modifiers apply.
  - **In a spectator run.** On historical focuses an AI MLT never takes Terms. Off them, it takes
    Terms only after the report's STAGE `wbh`, only with WBH itself holding Washington, and only
    once the Broken Coast has refused the Covenant, is at war with MLT or is gone. From then until
    Terms is taken the report shows no JUSTIFY or WAR_START on WBH, and after it no FOCUS line for
    The Tide-Wall. A FOCUS line for The Coast Goes Under comes, if at all, only while a war with
    the raiders already runs. After 2281 no FOCUS line for The Tide-Wall, Drown the Dance or Terms
    comes against a stronger target once another Act III focus is done (`mltd_ai_act3_path_taken`).
    After a refusal the report shows a WARGOAL line on the refuser, and no WAR_START on it within
    the year until its war twin's hold (for the Broken Coast, with its stage) has lifted; an
    earlier WAR_START means the -1000 lost to OWB's war-goal pull. Each spoils group's FOCUS lines
    come after the next act's war focuses and before its close (the south's after the ending).
  - **Unverified**, watch for:
    - an acceptance option hidden by its `trigger` when a human lets the event time out;
    - `has_wargoal_against` in an `ai_strategy` `enable`;
    - the exclusion markers on row 23, and the six lines to The Deep Ones Walk clearing its icon;
    - `search_filters` in a shared focus;
    - an instant building in a state held without a core, whose building slots OWB's non-core
      penalty halves;
    - scripted-loc calls at the end of a focus description (vanilla's focus loc uses them; OWB's
      own focus descriptions do not);
    - `add_equipment_to_stockpile` paying the archetype `amphibious_beast_equipment`, in a variable
      amount, as MLT's best unlocked breed (no OWB file pays a creature archetype);
    - `<TAG>.num_equipment@<type>` read into a temp variable in a focus preview;
    - an idea's `equipment_bonus` lines in an `add_ideas` / `add_timed_idea` preview, and a
      scripted-effect call in `effect_tooltip`;
    - that the preview draws only the branch of an `if` / `else_if` whose limit holds (the Covenant
      joins, `mltd_intel_foothold`, the Foundries);
    - `[GetMltdBunkerName]` printing OWB's "Outpost", and `add_corps_commander_role` inside
      `effect_tooltip` for a role-less character (the Kingdom).
- **Round 28c's balance review** (the research slot, the Rangers, Old Castro, one gate set for the
  invitations, the Texan icon). Fully restart. `python check_plan_sync.py`,
  `python story_rework/tools/grid.py` (no overlaps, no cell off the spec) and
  `python story_rework/tools/locaudit.py` (exit 0) all pass. `error.log` names neither
  `mltd_bdt_not_pilgrims_tt` nor `mltd_wbh_terms_faithful_tt`, and `text.log` reports no missing
  key for them or for the deleted `mltd_brk_intel_tt` / `mltd_brk_pirate_coast_tt`. Then:
  - **The fourth slot.** The Tide Turns South previews a research slot, and the research screen has
    four lines from the day it completes - before The Turbines Sing, not after `mltd.40`. The Last
    King Kneels previews only its idea and its events. `mltd.40` option a still brings the fifth.
  - **The Drowned Rangers.** `mltd.40` option b's idea shows twice the army attack and defence it
    did (organisation unchanged) and twice the army experience, and When Shady Sands Falls' preview
    says the same - the two must agree.
  - **The invitations' gates.** All three grey until the invitee's cult stands at 40 %, MLT holds
    that country's civilian infiltration token and the coverage line reads *More than 25%*. The
    Covenant asks nothing about the VIC and DRE coast or civilian intel any more; Hail the Drowned
    King nothing about the Odious King, but it greys while the Bone Dancers have taken
    `bdt_listen_to_the_pilgrims` or MLT is in a faction with Heaven's Guard; Terms for the Citadel
    prints its one line against whichever Brotherhood `mltd_wbh_terms_target` picks - check it
    after WBH becomes someone's subject, when TCA is asked. Without La Resistance none of the three
    lines shows, and the invitations gate only on their world conditions.
  - **The icon and the spine.** The Last King Kneels (15,39) shows the claw closing on the map of
    Texas, clear of the wars on row 38, with R'lyeh Rises directly below it on row 40 between the
    south's two spoils, and the endings on row 41. No empty row between the wars and the close.
  - **In a spectator run.** The report's ADVISOR line for `MLT_OLD_CASTRO` comes within a year of
    The Spreading Cult (check o) and SNAP shows `slots=4` after it - the hire that no run has yet
    made. Where the AI courts a nation, its cult should now reach the gate: watch the CULT lines
    for the Broken Coast, the Bone Dancers and, on unhistorical focuses while Terms is pending, the
    Washington Brotherhood, and a network and civilian token on each in turn.
- **2026-09-23** (the summons, the cults, bypass). Fully restart. `python check_plan_sync.py`,
  `python ai_run_report.py --selftest` and `python story_rework/tools/locaudit.py` pass;
  `error.log` names neither `mltd_summoned_host` nor `mltd_add_summoned_room`. Then:
  - **The summons' room.** After `event mltd.7` the politics view lists *The Summoned Host*,
    Special Forces Minimum Capacity +8, and the army screen's special-forces cap reads 8 higher
    than before - 28 before the Walk (OWB's 20 and the Call's division). Each summon adds 8 more,
    and a division trained afterwards still fits under the cap. The Call, the Walk and both summon
    decisions show the +8 line.
  - **The summons stay.** After `mltd.8`, *Summon the Deep Ones* is still listed, and `mltd.8`'s
    option says so; after The Final Ritual, *Summon the Star Spawn* is too. Each still costs its
    people and political power and keeps its cooldown.
  - **Cult decay.** A cult at 10 % loses about 0.13 a week - the monthly CULT lines in `game.log`
    fall ~0.6 - and one at 50 % about 0.93. One operative nurturing back to back grows a cult past
    40 %.
  - **Bypass.** With BDT annexed from the console after The Grand Ritual, The Bone Shore, The
    Dancers Hear the Tide, Hail the Drowned King and Drown the Dance show as bypassed, and The Deep
    Ones Walk waits only on its Books (since 2026-09-24; until then Hail and Drown were bypassed
    when the ritual completed, and The Tide Turns South waited only on its size gate). The same
    holds for the other nations' focuses: annex BRK for its four, WBH and TCA for Washington's
    four. A focus whose target is MLT's subject is not bypassed and pays its fallback. Unverified:
    what the engine does with a focus in progress whose target dies, and with the mutually
    exclusive twin of a bypassed focus.
  - **In a spectator run**, check (q) now also judges the summons after The Final Ritual against
    300,000 people.
  - **The equipment icons.** The production view, the division designer, logistics and the tech
    tooltips show the Star Spawn as a teal, rearing Cthulhu and the Deep Ones as a smaller green
    figure mid-stride, each whole inside its box - no longer OWB's mirelurk king and bloodrage.
    They are whole figures where OWB's creature icons are busts cut by the frame, so they sit
    smaller beside them: if they read too small, each icon's `size` in `ICONS` at the top of
    `build_equipment_icons.py` is the dial (`"max"` is the largest that keeps the figure whole).
- **2026-09-24** (Acts II and III before the Walk and the ritual, the Tide-Speaker, the wars'
  rewards, lighter tooltips). Fully restart. `python check_plan_sync.py`,
  `python build_telemetry.py`, `python ai_run_report.py --selftest`,
  `python story_rework/tools/grid.py` and `python story_rework/tools/locaudit.py` pass; `error.log`
  names none of `MLT_TIDE_SPEAKER`, `mltd_claims_of_the_tide`, `mltd_ai_hire_tide_speaker`,
  `mltd_the_first_wave` or the four new war ideas. Then:
  - **The layout.** Act II's heads and beads on rows 21-22 at x 11, 15 and 19, with lines from The
    Grand Ritual; each nation's pair on row 23, one column either side of its bead, with lines from
    the bead and an exclusion marker between the two; row 24 empty; The Deep Ones Walk at (15,25)
    with six dashed OR lines from row 23 that clear its tall icon; row 26 empty; The Final Ritual
    at (15,27) with one line from the Walk; The Tide Turns South directly below it at (15,28), and
    everything below it one row lower than round 28c's rows. Salt on the Broken Coast, directly
    under The Grand Ritual, keeps its name clear of the ritual's icon.
  - **The order.** Each Act III focus greys until its bead completes, the Walk until one of the six
    has and all five Books are read, The Final Ritual until the Walk has and the nation holds
    200,000 people, and The Tide Turns South until the ritual has. A war twin taken before the Walk
    declares its war as it did after the ritual.
  - **The Tide-Speaker.** She is in the cultural advisors' list from game start, greyed until the
    Kingdom, with a generic advisor's portrait and *Claims of the Tide*; she costs the political
    power her `cost` names (`common/characters/MLT.txt`) and can sit beside Old Castro. Hired, a
    justification's time in the diplomacy screen falls by 30 %, and by 55 % once The Northern
    Waters adds its 25 %.
  - **The wars.** Each war focus's tooltip shows its declaration, its 180-day idea - hover it for
    *Attack bonus against* and *Defence bonus against* the target, +10 % each - and The First Wave
    (60 days, Division Recovery Rate +10 %, Breakthrough +5 %), and nothing about the target's
    stability or war support. After completion both ideas sit in the politics view, and the
    targeted bonus shows in a battle against that country. With two wars inside 60 days, note
    whether The First Wave's timer restarts.
  - **The invitations.** The Drowned Covenant's tooltip reads: the Broken Coast invited to join our
    faction; *If they accept:* the faction created (while MLT leads none) and *Broken Coast joins
    faction*; *If they refuse (the war goal expires after a year):* *Gains Annex war goal against
    Broken Coast*. Hail the Drowned King the same for the Bone Dancers, Terms for the Citadel for
    the Brotherhood to be asked, with its claims line. With the invitee annexed from the console,
    the tooltip shows only the +50 political power.
  - **In a spectator run.** The report's ADVISOR line for `MLT_TIDE_SPEAKER` comes after Old
    Castro's (or from the Kingdom without La Resistance); the FOCUS lines run The Grand Ritual, the
    Broken Coast's branch, one Act III focus - most likely The Tide-Wall, in the Washington war its
    stage opens (STAGE `wbh` now comes after The Grand Ritual) - The Deep Ones Walk, then The Final
    Ritual. Watch the gap between The Grand Ritual and the Walk: an AI that reaches none of the six
    stalls there until the 2281 escape of its war holds (The story acts > *The AI*).
- **2026-09-25** (the Cannibal Territories trade). Fully restart. As MLT, with New Spawning Pools
  done, hold Cannibal Territories (186, PMR's at the start - annex PMR from the console):
  - Offer Muttfruit for the Cannibal Territories is not bypassed by itself: its tooltip lists the
    bypass under "(automatic bypass is disabled)", its *Does not own* line fails, and Dig Barrows
    for Spawning Pools is open beside it;
  - bypassing the trade completes it with no offer to anyone, opens its three focuses and greys out
    the Barrows; digging the Barrows instead leaves the trade's bypass failing on the Barrows line,
    so neither the trade nor its three focuses can be had - try it with 186 taken after the Barrows
    too;
  - without 186 the trade runs as OWB's and sends PMR its offer, and a refusal still opens the
    Barrows (OWB's `denied_muttfruit`); taking 186 while the trade runs cancels it, and it can then
    be bypassed;
  - note how the bypass is offered (a button, or on selection) and write it into Gotchas > *A
    bypass fires by itself*;
  - in a spectator run the report shows no FOCUS line for the trade or its three focuses after the
    Barrows (run 8 had them from day 1792).
- **2026-09-25, the invitations' previews.** Fully restart. At game start, and whenever an invitee
  cannot be asked, Terms for the Citadel, The Drowned Covenant and Hail the Drowned King show the
  offer, then *If it accepts:* or *If they accept:* over the faction lines and *If it refuses:* or
  *If they refuse:* over the war goal - Terms naming the Washington Brotherhood while it is free of
  any overlord - and not +50 political power. With the Broken Coast MLT's subject the Covenant
  shows the +50, which is what it pays. Start a focus, then make its offer impossible (put the
  invitee at war with MLT from the console), and the running focus's tooltip turns to the +50; at
  completion it pays that and sends no offer. Terms' Brotherhood line passes while WBH leads the
  Northern League (the league hand-over, below). Unverified: `focus_progress` read in a focus's
  tooltip.
- **2026-09-25, the league.** Fully restart. With WBH leading the Northern League (from 2275; bring
  The Old Country in through `WBH_fellow_savages`, or add a member from the console), Terms for the
  Citadel's Brotherhood line passes, and its preview shows, after the claims line, *Every other
  member of Northern League* ... with the faction's name. Answer yes as WBH (`tag WBH`, Rounds 28,
  28b and 28c > *Forcing an answer*): WBH and every other member at peace with MLT and its allies
  appear in the Drowned Covenant, the Northern League is gone from the diplomacy view, each moved
  member shows +75 *Drowned Covenant* with MLT both ways and no *Faction Traitor* toward WBH, and
  their subjects come too. A member at war with MLT stays out and leads what is left of the league.
  Afterwards Yakama's Northern Federation or the Bone Dancers' pact founds a new league instead of
  trying to join through WBH (`GLOBAL.northern_league_leader` cleared). In a spectator run on
  unhistorical focuses, the Washington conquest block no longer justifies on WBH while Terms is
  still to be offered (`mltd_ai_terms_pending` now holds while WBH leads its league). Unverified:
  `set_faction_leader` under a template with `change_leader_rule_never`, and when
  `on_leave_faction` runs.
- **2026-09-25, the focus lengths.** Every focus of ours shows 7, 30, 60, 120 or 180 days in the
  focus view: the story's heads, wars and closes 30, the invitations and Act II's merged beads 60,
  the spoils' one-offs 30 and their idea focuses 60. `python check_plan_sync.py` checks the
  numbers. In a spectator run the report's FOCUS days should sit near the re-timed plan's.
- **MLT's melee icons.** Fully restart (sprites are read at launch). As MLT, the infantry tech
  tab's third melee tech reads *Tridents* and shows the trident lying flat across its box, in the
  tree and in its tooltip; the Cultist Knife (*Basic Melee Weaponry*) and the Conch Knife are about
  three-quarters the size of another country's copy of the same icons - compare as DIS, which keeps
  OWB's - sit clear of the darker strip along the bottom of their boxes, and carry the same dark
  outline as the trident, whose two ends are whole. If the two knives are unchanged for MLT, the
  later-filename-wins rule behind `z_mltd_technologies_faction.gfx` is wrong (MLT's melee icons >
  *The two knives*). After researching the Tridents (`research_on_icon_click` in the console, then
  click it) production and logistics show the same name and icon; as any other country the tech
  still reads *Heavy Melee Weaponry*; and after the Kingdom's cosmetic tag MLT keeps both.
  `error.log` names neither `GFX_MLT_melee_weaponry_tech_3_medium` nor the texture, and `text.log`
  reports no collision on `MLT_melee_equipment_3`.
- **The Star Spawn model.** Its static first version was seen in game on 2026-09-21: it drew,
  textured and lit correctly, too large and unanimated. **The rigged version is not yet seen.**
  Fully restart; `python build_unit_model.py --check` passes. `error.log` names none of
  `mltd_star_spawn_entity`, `mltd_star_spawn_mesh`, a `mltd_star_spawn_*_animation`,
  `mltd_entities.asset` or a file under `gfx/models/mltd/`. Then, as MLT, `event mltd.8` in the
  console raises the first Star Spawn division at the capital:
  - standing, it breathes - chest, wings, beard - and now and then looks aside and bellows (`idle`,
    `idle2`); it does not freeze, pop between clips, fold up, explode into spikes or lie on its
    side (any of those is the skeleton or the skin: compare
    `event_images/unit_model/animations.mp4`, which is the same numpy skinning the checks hold the
    files to);
  - ordered to move it **walks**, facing the way it travels, both feet taking steps and staying on
    the ground, and its feet do not skate much faster or slower than the ground passes (if they do,
    `animation_speed` on the `move` state is the dial, then `STRIDE` and `SECONDS` in
    `unit_model_clips/move.py`); retreating, it walks faster;
  - in combat it rears and rakes with the raised claw or swings the right hand across (`attack`,
    `attack2`), and defending it hunkers behind its wings; the blends between states (0.3-0.4 s)
    are not abrupt;
  - it stands about 1.35 times a soldier's height and rather over a mirelurk's (it was twice a
    mirelurk's at scale 1.2); if it is still too large or now too small, `ENTITY_SCALE` is the
    dial;
  - it is teal with visible scales and a satin, wet sheen, as the static version was. **Orange at
    night** means blue crept into the normal map (OWB's emissive tint);
  - it holds up at every zoom level, at night and **in snow** (OWB's static buildings use
    `PdxMeshAdvancedSnow`; if the figure looks wrong on snow, that is the variant to try in
    `GFX_TEMPLATE`);
  - the two GUI 3D views draw it uncropped - it is 8 tall and 6.9 wide where they expect a 5.9-tall
    soldier: the division designer's model selector on the Star Spawn template, and the details
    window of *The Star Spawn* tech in the Reward Technologies tab (both after The Final Ritual);
  - a **Deep Ones** division (`event mltd.7`, the Call) is the same figure at the same size,
    walking and fighting the same way - no mirelurk.
  - Unverified until then: the skeleton, the skin and the clips in the engine at all (they are
    proven only against an emulator that reproduces OWB's mirelurk); how the walk's speed sits
    against the map's; `looping = no` idles chaining without a hitch; the attacks' chaining - ours
    blend at 0.3 s where all 180 self-chaining states in vanilla and OWB write 0.0 or nothing, so
    if chained attacks hitch set both `attack` lines to 0.0 (the two clips meet exactly in the
    sculpt's pose); and the mesh's bounding box, which is the rest pose's while the clips reach up
    to 1.0 further forward and 1.1 to the side (`check()` prints each; OWB's mirelurk is in the
    same position: its claws reach z = -6 from a box that ends at -3.3).
- **AI spectator runs (round 19).** Launch with `-debug` (this machine's Steam launch options
  already carry it). Start a new game, ironman off, as a country far from Oregon - never MLT,
  because OWB rolls DIS's schism flag at game start by whether MLT is human - then type `observe`
  in the console and run at speed 5. `game.log` is truncated at every launch, so run
  `python ai_run_report.py --save` before relaunching; `--list` shows the runs in one log. The
  first run must also settle the telemetry's unverified points: numbers print as plain digits,
  `capital=` shows a state id, and the report's summary shows no clock disagreement. Run 1 (to
  August 2276) settled those, and showed that the AI MLT never justified or went to war on its own.
  Run 2 (to October 2285) justified and fought on its claims but declared on Arroyo inside the
  NCR's faction, never ended that war (a pocket out of reach), lost the Oregon ring to others,
  never hired Old Castro and drained its people with offerings - round 20's changes answer each. It
  was started as Arroyo: pick a country far from Oregon, California and Nevada instead, since OWB
  rolls a few start-of-game weights by who is human. To read a save beyond the telemetry, set
  `save_as_binary=no` in `Documents\Paradox Interactive\Hearts of Iron IV\settings.txt` before the
  run.

## Install

1. Copy `mod_folder/descriptor.mod` to
   `C:\Users\<you>\Documents\Paradox Interactive\Hearts of Iron IV\mod\rising_tide.mod`.
2. Append one line to that copy: `path="C:/Users/<you>/Documents/rising-tide/mod_folder"` -
   absolute, **forward slashes**, no trailing slash, pointing at `mod_folder`. It is
   machine-specific, which is why it is not in the repo. (Already installed on this machine.)
3. In the launcher: **Reload Installed Mods**, then add both this mod and Old World Blues to a
   playset and enable both.
4. **Load order.** `dependencies={ "Old World Blues" }` in *both* `mod_folder/descriptor.mod` and
   the installed launcher `.mod` is what makes this mod load **after** OWB, so our files win on any
   overlap and OWB's 95 `replace_path` entries do not delete ours - see OWB's own guide,
   `<OWB>/doc/OWB_MODDING_README.txt`: "After adding this your mod will load after OWB and won't be
   replaced by files we have or our replace_paths". Keep that block in both files. If you also
   order the playset by hand, put Rising Tide **below** Old World Blues - lower in the list loads
   later.

## Workshop art

`build_workshop_thumbnail.py` renders `event_images/workshop/thumbnail.png` (512x512, ~400 KB;
Steam caps the preview at 1 MB) plus 128 px and 77 px previews under `event_images/workshop/`,
which are the sizes the Workshop grid and list actually show. **Only the GIF ships**; the still is
kept repo-side because it is what the GIF is graded against and the image to hand anyone who wants
a static one.

There is deliberately **no `picture=` key** in either `.mod` file, and no `thumbnail.png` at the
mod root. That mirrors *The Fire Rises* (Workshop item 3350890356), the one installed mod with a
working animated Workshop preview, exactly. The first publish here did set
`picture="thumbnail.png"` and the Workshop item took the still image; pointing the key at the
`.gif` instead is untried, and no installed mod does it - all 11 that set `picture=` use a `.png`.
If a publish still lands a still image, set the preview by hand on the Workshop page: that needs no
re-upload and definitely accepts a GIF.

The layout is measured off ten installed OWB submod thumbnails rather than invented. All of them
share one formula: a painted background, a band of character busts across the upper third, and a
**neon marquee** across the lower middle - a chamfered hexagon whose outline is a glowing tube with
white fluorescent-tube gaps in the centre of its top and bottom edges, carrying the shared "Old
World Blues" wordmark with the submod's own name beneath it. East Coast Rebirth and Rustbelt Rising
also hang a weathered road sign below it, which is where our "Welcome to M'lyeh" plate comes from.

No mod ships that wordmark as a reusable asset, so `event_images/workshop/owb_wordmark.png` was
matted out of *OWB - Fountain of Dreams*' thumbnail - the only one with light lettering on a dark
panel, and so the only one that mattes cleanly (the rust-panel versions do not separate). It
arrives silver with a violet keyline, which is that submod's own treatment; `retint_wordmark()`
maps it to the gold that Old World Blues, East Coast Rebirth, Rustbelt Rising and Over The Horizon
all use. `--silver` keeps the silver, which NCR-vs-Legion also uses.

Tunables live at the top of the script: `SATURATION` (the references sit at mean chroma 0.25-0.47),
`WORDMARK_GOLD`, and the layout block `SX0/SX1/SY0/SY1/CH` (the hexagon), `WM_*` / `SUB_*` (the two
type lines) and `PLATE_*` (the road sign).

### The animated preview

`python build_workshop_thumbnail.py --gif` additionally renders `mod_folder/thumbnail.gif`: the
same image with rain falling and the neon breathing, 350x350, 32 frames at 40 ms (a 1.28 s loop),
~740 KB. Steam accepts an animated GIF as a Workshop preview image - *The Fire Rises* (Workshop
item 3350890356) is the OWB-adjacent precedent, and it sets the budget: **1 MiB, moving or not**,
which is the only thing deciding the size, frame count and palette.

Three things keep it inside that budget, and all three are load-bearing:

- **Frames are delta-encoded** against what the viewer is still looking at, not against the
  previous frame - comparing per-frame would let a pixel creep away one `GIF_TOLERANCE` step at a
  time and the error would accumulate over the loop. About 9 % of each frame is redrawn; the rest
  is transparent over a non-disposed canvas.
- **Dithering is off.** Its noise is random, and random noise is exactly what run-length
  compression cannot pack.
- **The palette is chroma-weighted.** Median cut allocates entries by pixel count, and this image
  is overwhelmingly low-chroma teal, so a plain palette starves the gold wordmark, the violet outer
  tube and M'lulu's green eyes - the three things carrying the identity - and they snap to
  grey-blue. Re-feeding the most saturated decile (`CHROMA_WEIGHT`) fixes it.

The rain loop closes because the streaks are drawn into a tile periodic over `(W/2, W)` and rolled
by a whole number of pixels per frame whose total over the loop is an exact multiple of both
periods; `rain_tile()` asserts this. The neon breath uses `0.5 - 0.5*cos(2*pi*f/frames)`, which is
0 with zero slope at both ends, so any frame count closes.

The GIF is the only thumbnail in `mod_folder/`, and there is no `picture=` key - see **Workshop
art** above for why, and for the fallback if a publish still lands a still image. It costs every
subscriber ~740 KB of download.

### Page images

The thumbnail is one image; the **Additional Previews** gallery on the item page is another thing
entirely, and lives in `workshop_page/`:

```sh
python build_workshop_page.py "<screenshot>" --name 02_something
```

1920x1080, scaled preserving aspect and centre-cropped only if the source is not already 16:9 (game
screenshots at 2560x1440 are, so nothing is cropped). **JPEG, not PNG** - Steam caps a Workshop
image at 1 MiB and a 1920x1080 PNG of a scene this grainy is ~2.9 MB, so PNG cannot be used at this
size; quality is searched down from 95 until the file fits 900 KB, at 4:4:4 because these frames
are mostly UI text and thin neon.

**Read `event_images/SOURCES.md` before uploading.** The title image is built on the same
unverified third-party art as the event pictures, and it is the one asset that is public before
anyone installs the mod.

## Main menu

`python build_main_menu.py` replaces the Old World Blues main menu with this mod's:

- `gfx/loadingscreens/mltd_main.dds` (1910x1440, 10.5 MB): The background -
  `event_images/call_src.jpg`, the flooded street from *Call of the Deep Ones*, graded colder
- `gfx/interface/logo_game_static.dds` (443x303, 0.5 MB): The header logo - the *Rising Tide*
  marquee, transparent
- `gfx/interface/mltd_logo_animated.dds` (7088x303 uncompressed, 8.2 MB): The same marquee as a
  16-frame strip, neon breathing
- `gfx/interface/mltd_rain_anim{1,2}.dds` (2560x1792 DXT5, 4.4 MB each): Two scrolling rain sheets
- `gfx/interface/mltd_rain_{base,mask}.dds` (2560x1792 DXT5, 4.4 MB each): The sprite's rect:
  transparent base, flat mask

**1910x1440 and 443x303 are not choices** - they are what OWB's `load_colorado.dds` and
`logo_game_static.dds` are, and tnkd's `tnk_main.dds` matches the first. The frontend scales the
background to *cover*, so on a 16:9 screen only the middle ~1074 rows are ever seen; the painting
is placed exactly there and the bands above and below are mirrored, blurred extension for 4:3.

Three script files do the wiring, and they are deliberately separable:

- `interface/z_fallout_ui.gfx` - **OVERRIDE** of OWB's file, one line changed: `GFX_frontend_bg`
  now points at `mltd_main.dds`. This is what tnkd does. Only OWB and tnkd ship this file, so the
  collision risk is low. (Copy OWB's *current* bytes when re-diffing - tnkd's copy is stale and is
  missing `GFX_generic_text_bg_48_owb`.)
- `interface/mltd.gfx` - **new sprite** `GFX_frontend_bg_mltd_rain`, cloned from OWB's
  `GFX_frontend_bg_snow_anim`.
- `interface/frontendmainview.gui` - **OVERRIDE** of OWB's file, re-enabling the overlay `iconType`
  that OWB ships commented out and pointing it at our rain sprite. **This file is the only reason
  the rain moves, and the only high-collision file here** - OWB, East Coast Rebirth, Enclave Reborn
  Redux, Rustbelt Rising and Monarchs and Margaritas all ship it, and whichever loads last wins the
  whole main menu. Delete our copy and the background and logo still work; only the rain stops.
  (ECR, Rustbelt and Monarchs override it for exactly this purpose, each pointing at their own
  `GFX_frontend_bg_*`, so this is the house idiom and the "one menu wins" outcome is unavoidable.)

The header logo ships twice. The static texture is a **texture-path override** of OWB's
`gfx/interface/logo_game_static.dds`, the way tnkd does it - no `.gfx` change (NCR-vs-Legion,
Enclave Reborn Redux and Fountain of Dreams also ship that path, so last loaded wins). Our
`frontendmainview.gui` then points the logo at `GFX_frontend_game_logo_mltd_animated` instead, a
16-frame strip at 8 fps whose neon swells and settles on a raised cosine - 0 with zero slope at
both ends, so the loop closes. The static file is the fallback if another submod's gui wins.

**The strip is uncompressed, like OWB's own `logo_game_animated.dds`.** DXT5 costs a quarter of the
size but quantises colour per 4x4 block, and a block straddling a bright neon edge and the
transparent black outside it gets endpoints spanning cyan to black: measured error on visible
pixels was mean 6 and peak **164**, which shows as a speckled fringe along every tube. Frames are
traded away instead - the breath is a slow, smooth ramp, so 16 frames step by under 2 luma levels
each and the joins are invisible. `LOGO_FRAMES` and `LOGO_FPS` must match `noOfFrames` and
`animation_rate_fps` in `interface/mltd.gfx`.

**The marquee's glow needs a bigger canvas than the thumbnail gives it.** The sign is laid out to
sit 18 px from the edge of a 512-wide thumbnail it is meant to bleed off, but its outer bloom is a
Gaussian of sigma 32, so on that canvas the bloom is cut flat - which as a logo showed up as a hard
vertical edge where alpha jumped 0 to 224 in a single column. `padded_sign_canvas` re-renders the
same sign on a canvas widened by `LOGO_PAD`, shifting every absolute coordinate the sign builder
reads (`W`, `HEXW`, `SY0/SY1/SYM`, `GC`, `WM_TOP`, `SUB_TOP`); sizes and differences are
translation-invariant and are left alone. The crop then crosses the bloom at `LOGO_EDGE`, low
enough that the step is invisible - the build prints the strongest alpha left on the crop border,
which should read ~0.02 rather than ~0.9.

### How the rain works

`animation = {}` blocks attach **only to `spriteType`** - across vanilla and all 25 installed mods
there are ~56,000 of them and not one sits on a `corneredTileSpriteType`, which is what
`GFX_frontend_bg` is. So the rain cannot be an animation on the background itself; it has to be a
second, fully transparent sprite laid over it, which is precisely how OWB's (disabled) snow works.
Ours reuses OWB's `bg_snow_anim_background.dds` (alpha 0 everywhere, so only the animations draw)
and `bg_snow_anim_mask.dds` (a flat 191, so they draw at 75% over the whole screen) unchanged and
by path, without copying either.

Colour lives in RGB and shape lives in **alpha**, which is how OWB's snow textures are built.
Streaks are stamped with modular indexing so they wrap in both axes - a seam would otherwise sweep
across the screen once per cycle - and tapered along their length so they fade in and out instead
of ending square. Coverage is 2.4% and 4.9% of alpha, against OWB's snow at 1.7% and 3.2%.

### Why the rain textures are taller than the screen

The overlay sprite is drawn **unscaled, at exactly the size of its BASE texture** - the one named
by `texturefile`, *not* the scrolling animation textures, which are sampled inside the rect the
base defines. It is anchored to the top-left of the `frontend_background` container, and that
container is 1920x1440 scaled to **cover**, so on anything wider than 4:3 it overflows vertically
and its top-left sits **above** the top of the screen:

```text
scale    = max(W / 1920, H / 1440)
overflow = (1440 * scale - H) / 2      # 180 px at 1080p, 240 px at 1440p
```

A sprite only `H` tall therefore runs out `overflow` px short of the bottom, leaving an empty band.
That is why the base and mask here are **ours and 2560x1792** rather than OWB's
`bg_snow_anim_background.dds` and `bg_snow_anim_mask.dds`, which are 2560x1440 and 240 px short on
a 1440p screen - and almost certainly why OWB ships its snow overlay commented out, since it has
exactly the same shortfall.

This was established by experiment, not from documentation: enlarging the animation sheets alone
changed nothing, which is what identified the base texture as the thing that sets the rect.

For 16:9 the requirement is `height >= 7/6 * H` and `width >= W`. At the fixed 2560 width the worst
case is 1440p, needing 1680; 1792 leaves margin for an overflow up to 352 px. **4K (needs
3840x2520) and 21:9 (needs 3440x2010) still fall short** - raise `RAIN_W` and `RAIN_H` in
`build_main_menu.py` and nothing else; streak counts are per 2560x1440 and rescale with the canvas,
so the rain does not get heavier. The cost is four textures, so 3840x2560 would be ~9.8 MB each
instead of 4.4.

`build_main_menu.py --preview` models this geometry rather than guessing at it: it reads the rect
off the base texture that actually ships, prints the rows and columns covered, and warns if they do
not reach every edge. Pass a different `screen=` to `build_preview()` to check another display.

`animationtexturescale` must stay in step with `RAIN_SCALE` in `build_main_menu.py`, which sizes
the streaks for it: the sprite magnifies by `1 / scale`, so at 0.75 a 60 px streak is 80 px on
screen. **`animationrotation` is the one parameter here that cannot be checked without launching
the game** - whether it rotates the texture along with the scroll direction is unknown, so the
streaks are drawn vertical and kept short, which reads as rain either way. 205 and 212 sit just
inside the range OWB's snow uses (210 and 220), which is known to fall downward.

## Update process

OWB updates silently invalidate every file we override, so re-diff after each one.

1. Get [WinMerge](https://winmerge.org/).
2. Compare every file in the submod against its OWB counterpart and update.
   1. 1st folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196\`
   2. 2nd folder: `C:\Users\jonat\Documents\rising-tide\mod_folder\`
   3. Untick `View > Show Left Unique Items`.
   4. The seven overrides (`Mirelurk Tribe (MLT) Focus.txt`, `continuous_focus/generic.txt`,
      `common/characters/MLT.txt`, `history/countries/MLT - Mirelurk Tribe.txt`,
      `common/script_enums.txt`, `events/nf_mlt.txt`, `common/technologies/tech_naval.txt`) must
      end up as OWB's new file **plus only the edits listed under Overriding OWB** - our
      insertions, the replaced character, portrait and claim-focus lines, and the two deletions
      (`itz_civilizing` and `nf_mlt.7`'s law block) - keep each file's original line endings and
      BOM state.
   5. Re-check what round 16's new files lean on: OWB's `trade_ledger_window`,
      `selected_market_organization`, `temp_selected_org_inventory`, `caps_market_prevented` and
      the seller-bar layout in `interface/trade_ledger.gui` (The Wet Market), and OWB's story
      generals for `mltd_defector_story_character` (the operation). And what the spoils lean on
      (rounds 28 and 28c): the OWB states they name (their gates, effects and descriptions - the
      NCR's and the Legion's cores, the works cities, the Gulf ports, The Hub and Sac-City),
      `construction_industry_tech_6` as the last tech of its line, OWB's coring-cost modifier
      `core_creation_cost_factor`, and OWB's key `osi_research_pact`, which The Office of Salt and
      Industry's description nests (it must stay plain text in OWB's `english/` folder). And what
      the story acts' previews lean on (round 28b): OWB's `bunker` name in `replace/`
      (`GetMltdBunkerName`), and the icons whose heights set the layout (Gotchas > *A tall focus
      icon grows upward*) - an OWB redraw of `GFX_goal_CHC_cultists` or
      `GFX_goal_MIN_fallen_kingdom` may need the empty rows moved.
   6. For the Star Spawn's model run `python build_unit_model.py --check` (it compares against
      OWB's `mirelurk.mesh` and `mirelurk_d.dds` and looks for a name clash), and re-diff OWB's
      `gfx/FX/pdxmesh.shader` and `standardfuncsgfx.fxh` against the decode documented under The
      Star Spawn model: `UnpackRRxGNormal`, the emissive read of the normal map's B, the specular
      map's G / B / A maths and `PdxMeshAdvanced`'s defines. If OWB changes the mirelurk's texture
      or its entity's scale, re-read the luma comparison the build prints and the *Pose and size*
      figures.
   7. Delete the `.bak` files afterwards.
3. Play the game to test, then read `...\Hearts of Iron IV\logs\error.log` (and `text.log` for
   localisation - the `warbike_unlock_tech` collision there is intentional) and confirm
   `system.log` lists both `Old World Blues` and `OWB - Rising Tide` as active mods.

## Compatibility

- Any submod that ships its own `common/continuous_focus/generic.txt` conflicts: whichever loads
  later wins the whole palette, so either its continuous focuses or *Feed the Spawning Pools* will
  be missing.
- The
  [OWB Official NCR versus Caesar's Legion submod](https://steamcommunity.com/sharedfiles/filedetails/?id=3010015443)
  ships its own `Mirelurk Tribe (MLT) Focus.txt`, which Rising Tide overrides too; whichever mod
  loads later wins the whole file, so run one or the other, not both. (It also ships
  `tech_fallout_land_doctrine.txt`, which Rising Tide no longer touches.)
- With *OWB: Ultimate Tech Compatibility Mod* (3462816659), which re-lays the whole Reward
  Technologies tab, the Deep Ones / Star Spawn techs land on its `robco_unlock_tech` (4,24) and
  `FNR_bollinger_shipyards_unlock_tech` (4,28) in its "Schematics" row and overlap them. Cosmetic
  only - both stay grantable. No slot next to Faeries is free under both layouts.
- With *OWB Tech Expansion* (2821243420) loaded after this mod, its `countrytechtreeview.gui` has
  no `warbike_unlock_tech_tree` gridbox, so neither reward tech renders in the tab (they still work
  when granted by focus).
- The intelligence operation needs the La Resistance DLC; without it the file loads silently and
  the operation never appears.
- The Star Spawn's textures are laid out for `PdxMeshAdvanced` as OWB's `gfx/FX/pdxmesh.shader`
  reads it. A mod that ships its own `gfx/FX/pdxmesh.shader` and loads later governs how they are
  read.
- Since round 26 Rising Tide overrides `common/technologies/tech_naval.txt`, which *OWB: Ultimate
  Tech Compatibility Mod* and the NCR-vs-Legion submod also ship. If theirs loads later, the
  Leviathan tech loses its path from the Palace and no longer renders in the naval tab (it still
  works when granted); if ours loads later, their naval-tree changes are lost.

## Plan

### High priority

- [ ] Before the next Workshop upload, set `mltd_telemetry_on`
  (`common/scripted_triggers/mltd_telemetry_triggers.txt`) to `always = no`, or the AI telemetry
  writes into every player's `game.log`.
- [ ] Re-test round 9: M'lulu's portrait rains and her small icon is right; the Deep Ones summon
  stays visible and greyed with a countdown instead of vanishing; the two Offerings decisions pay
  caps and capital water; *Feed the Spawning Pools* shows up in the continuous-focus palette and
  discounts creature equipment while selected; the Kingdom focus adds the victory points; a Star
  Spawn division still spawns fully equipped now that a battalion needs ten pieces instead of
  forty.
- [ ] Re-test the startup fixes: `error.log` must no longer list the four
  `script_enum_equipment_bonus_type` warnings or the two `recruit_character` errors for
  `events/mltd_events.txt` (the only lines in the last log that were ours), and the Drowned Herald
  must show up as a general once the *Kingdom of M'lyeh* event fires.
- [ ] Re-test after round 3: a summoned / focus-spawned division arrives **with** its equipment (32
  / 16 spare in Logistics, hidden `Spawn of the Deep` tech in the equipment tooltip); the Grand /
  Final Ritual focus tooltips show the red modifier lines with values; the five focuses render as a
  column below the tree with no overlaps and no line from the Kingdom to Gifts; then the rest of
  the chain - Deep Ones tech in the Reward Technologies tab, gifts apply instantly and expire at 30
  days, the toll ticks daily, the Deep Ones template is trainable after *The Deep Ones Walk*, the
  operation appears with an agency.
- [ ] Tune the toll and the population gates (`mltd_ritual_toll_factor`, 100,000 / 200,000 - see
  CLAUDE.md > The rituals) once you have seen them in play.
- [ ] Play-test round 27, the story acts (Testing > Round 27), including a spectator run that
  reaches at least Act V.
- [ ] Play-test rounds 28, 28b and 28c (Testing > Rounds 28, 28b and 28c): each invitation's answer
  under both historical-focus settings, a refusal's expiring war goal, the three two-way pairs and
  the flags that make the Covenant and Terms for the Citadel exclude each other, The Coast Goes
  Under's war, the tall icons' empty rows, the spoils beside the chapters, and the rescaled rewards
  and their previews - above all the thefts paid in mirelurks through the archetype
  `amphibious_beast_equipment`, which no OWB file does.
- [ ] Play-test round 28c's balance review (Testing > Round 28c's balance review): the fourth
  research slot at Act III's close, the Drowned Rangers worth taking against `mltd.40` a, the one
  gate set on all three invitations, The Last King Kneels' Texan icon and the closed-up spine, and
  a spectator run that finally hires Old Castro.
- [ ] See the Star Spawn's **rigged and animated** model in game (Testing > The Star Spawn model;
  its static first version drew correctly on 2026-09-21), and before the next Workshop upload
  record the sculpt's designer, download page and licence in `event_images/SOURCES.md` - it is the
  one source there with no origin at all.
- [x] Fix the population sums' overflow (round-27 review): `mltd_update_national_population` now
  sums `state_population_k` into `_k` variables and copies them back into people capped at
  2,147,000 (The rituals). Confirm in a late game that the Leviathan summon stays available past
  ~2.15M people.

### Medium priority

- [ ] The focus slot idles while an act's close waits for its great war, with only OWB's `lurk_`
  focuses to fill it. The spoils fill part of each stretch - the north's during the NCR's war,
  California's during the Legion's, the interior's during Texas's - and `CONQUEST_PLAN.txt` now
  leaves roughly 550 idle days in the NCR's war (530 until the focus lengths of 2026-09-25, 620 on
  2026-09-23, when Act II's Washington branch, 91 of them, became bypassed once both Brotherhoods
  fall; since 2026-09-24 that branch is taken before the ritual and the Bone Dancers' fills its 91
  days), 215 in the Legion's and 290 in Texas's [M] (150 and 245 until 2026-09-25; round 27: 630,
  320 and 340; the ten spoils focuses take 450 days since 2026-09-25, and round 28c's took 469
  against round 28's twelve's 504, and California's four sit in the Legion's war). Consider a
  continuous focus or a longer group for the NCR's war.
- [ ] Is The Grand Ritual's icon (152x139) clear of the Call's name on the consecutive rows 19-20?
  If not, give the ritual an empty row above it or a shorter icon (Gotchas > *A tall focus icon
  grows upward*). The Walk's own question went with its move below Act III, under an empty row
  (2026-09-24).
- [ ] Balance levers left open by the review of rounds 28b-28c (`story_rework/BALANCE_REVIEW.md`,
  2026-09-22; its section 0 records the user's decisions, and nothing in it is play-tested).
  **Applied**: the fourth research slot moved forward to Act III's close, the Drowned Rangers
  doubled, and Old Castro's `ai_will_do` raised to OWB's 10003 (Project > *Round 28c's balance
  review*). **Open**: the gift rentals - 30-day missions renewable at once, where OWB's rentable
  attack buffs carry a cooldown or a malus - on which the user asked for a fuller description
  before deciding. **Declined, so left as they are**: the Offering of the Drowned's cooldown (the
  Drowned Hoard feeding the Wet Market is the build-up's strongest loop); tech gates on the Wet
  Market's better lots, which sell the king and armour forms years before OWB dates them; a cap on
  the Star Spawn summons; and a cap on the Leviathan fleet. Also left: The Priestess Reigns'
  stability lands on a cap at peace and fills only the last points at war; the manpower rewards add
  little, since manpower never binds after 2276; and the permanent gifts are two to four times any
  act idea, on purpose. Move none of the rest before a play-test says so.
- [ ] The global flag `mltd_rlyeh_risen` (R'lyeh Rises) is set but read by nothing - a hook for
  later content (flavour events, other countries' reactions); delete it if nothing ever uses it.
- [ ] Bespoke art: focus icons (currently reused OWB sprites), a decision-category banner,
  cult-flavoured operation phases, and a properly repainted M'lulu (the shipped one is a colour
  grade).
- [x] Add the Workshop preview image (`mod_folder/thumbnail.gif`; deliberately **no** `picture=`
  key - see Workshop art). Published as Workshop item
  [3798403425](https://steamcommunity.com/sharedfiles/filedetails/?id=3798403425); the launcher
  wrote `remote_file_id` into both files on upload. Image licences in `event_images/SOURCES.md` are
  **still unresolved**.
