p = r'C:\Users\jonat\Documents\rising-tide\CLAUDE.md'
s = open(p, encoding='utf-8', newline='').read()
reps = [
# beat table row 6
("(*The Stars Are Right*, closed by The Tide Turns South at 50 controlled states)",
 "(*The Stars Are Right*, closed by The Tide Turns South at 50 controlled states or from 2281)"),
# Layout: mltd_ai_triggers.txt
("the NCR's readiness and the late army. Two of its triggers are not AI-only:",
 "the NCR's readiness and the late army. Section W (round-27 review) holds `mltd_ai_may_*`, one per story war focus: the AI's hold on that focus, called from the focus's own `available` (The story acts > *The AI*). Two of its triggers are not AI-only:"),
# The rituals: population variable
("`mltd_national_population` is recomputed every day by `mltd_update_national_population` (`every_owned_state = { add_to_variable = { PREV.mltd_national_population = state_population } }`, OWB `exodus_effects.txt:385` precedent) and reads 0 until the first daily tick.",
 "`mltd_national_population` is recomputed every day by `mltd_update_national_population` and reads 0 until the first daily tick. Since the round-27 review it is summed in thousands (`every_owned_state = { add_to_variable = { PREV.mltd_national_population_k = state_population_k } }`, OWB `exodus_effects.txt:385` precedent), then copied back into people and capped at 2,147,000, as is `mltd_controlled_population` (the summons' pool): a raw sum of `state_population` wrapped negative past ~2.1M people (Gotchas), which the later story acts reach, and would have failed the Final Ritual's gate - and every act after it - for good. Every gate and AI guard on the two variables sits below the cap, so the cap changes no test; the ritual tooltips' *currently* simply stops at 2,147,000. The `_k` variables keep the true figure."),
# Size gates
("- **Size gates.** Two focuses count land instead of a war: The Tide Turns South needs 50 controlled states (`num_of_controlled_states > 49`, repeated in `mltd_tide_turns_south_states_tt`) and R'lyeh Rises 300 (`> 299`, repeated in `mltd_rlyeh_rises_states_tt`). Change each pair together.",
 "- **Size gates.** Two focuses count land instead of a war: The Tide Turns South needs 50 controlled states (`num_of_controlled_states > 49`) or the year 2281 (round-27 review: run 8's AI held 35-39 states for two years after its Final Ritual, which would have shut Acts IV-VI for the whole game), both repeated in `mltd_tide_turns_south_states_tt`; R'lyeh Rises needs 300 (`> 299`, repeated in `mltd_rlyeh_rises_states_tt`) and has no fallback - it is the finale. Change each pair together."),
# The AI table
("*The AI.* Each war focus's `ai_will_do` reads 0 for an AI while its war would come too early:\n\n| War focus | Reads 0 for an AI while |\n| --- | --- |\n| The Tide-Wall | `mltd_ai_stage_wbh` or `mltd_ai_army_ready` fails - only while a Brotherhood it would declare on exists |\n| Drown the Dance | `mltd_ai_courting_bdt` holds or the army is not ready - only while BDT exists and is not MLT's subject |\n| The Turbines Sing | `mltd_ai_stage_ncr` or readiness fails - lifted once MLT is at war with the NCR or the NCR is beaten, because the close needs the focus and an AI must not be held off it after the war |\n| The Serpent Drowns | `mltd_ai_stage_ate` or readiness fails; also while ATE fails `mltd_ai_safe_target` (its declaration skips that check), or while an uncapitulated Texan tag is at war with MLT |\n| Act V's four wars, Black Water Rising, The Drowned God Sleeps | readiness fails - nothing else |\n",
 "*The AI.* Each war focus is **unavailable** to an AI while its war would come too early. The hold is a scripted trigger in the focus's own `available`, `mltd_ai_may_*` (`mltd_ai_triggers.txt`, section W): a `hidden_trigger` whose `if = { limit = { is_ai = yes ... } }` a human always passes - the idiom of the claim focuses' `mltd_ai_may_press_claims`. Each holds only while the focus would start a war: with every target gone, already at war with MLT or its subject, the focus is a payout and nothing waits. Until the round-27 review the holds were `ai_will_do` modifiers reading 0, and that is not a hold: an AI takes every entry of its plan's `ai_national_focuses` that is available, whatever its `ai_will_do` reads. Run 8 (`ai_runs/20260918-170847`, round-24 code) completed The Tide-Wall on day 1715 with Washington's stage closed and The Turbines Sing on day 2513 with the NCR's never open, and took both Muttfruit trades through a `focus_factors` 0.\n\n| War focus | Trigger | Unavailable to an AI while |\n| --- | --- | --- |\n| The Tide-Wall | `mltd_ai_may_raise_the_tide_wall` | `mltd_ai_stage_wbh` or `mltd_ai_army_ready` fails - only while a Brotherhood it would declare on stands at peace with MLT |\n| Drown the Dance | `mltd_ai_may_drown_the_dance` | the army is not ready, or `mltd_ai_courting_bdt` holds before 2281 - only while BDT exists, is at peace with MLT and is not its subject. With La Resistance no AI strategy builds the Bone Dancers' network or takes their civilian token, so an AI seldom meets Hail the Drowned King's gates; from 2281 it stops waiting for them |\n| The Turbines Sing | `mltd_ai_may_start_ncr_war` | `mltd_ai_stage_ncr` or readiness fails - lifted once MLT is at war with the NCR or the NCR is beaten, because the close needs the focus and an AI must not be held off it after the war |\n| The Serpent Drowns | `mltd_ai_may_start_ate_war` | `mltd_ai_stage_ate` or readiness fails; also while ATE fails `mltd_ai_safe_target` (its declaration skips that check), or while an uncapitulated Texan tag is at war with MLT |\n| Act V's four wars, Black Water Rising, The Drowned God Sleeps | `mltd_ai_may_start_<ces\\|bos\\|utah\\|hea\\|texas\\|tla>_war` | readiness fails - nothing else |\n"),
("unverified: that the engine skips a listed focus whose `ai_will_do` reads 0, rather than taking it. The holds rely on this now that no `focus_factors` zero backs them.\n",
 "Settled by run 8: the engine does **not** skip a listed focus whose `ai_will_do` reads 0, which is why the holds are in `available`.\n"),
# Per-act table: the close
("| `mltd_the_tide_turns_south` (close) | any one of the four (one OR block); 50 controlled states |",
 "| `mltd_the_tide_turns_south` (close) | any one of the four (one OR block); 50 controlled states, or from 2281 |"),
# per-act conventions: note the AI holds
("- \"alive\" means the target exists; when it does not, the focus pays the fallback named.\n",
 "- \"alive\" means the target exists; when it does not, the focus pays the fallback named.\n- Every war focus's `available` also holds an AI through its `mltd_ai_may_*` trigger (*The AI*, above); the table lists only what a human sees.\n"),
# MLT's AI: the war focuses declare
("Each carries an `ai_will_do` modifier that reads 0 for an AI while its war would come too early - see The story acts > *The AI*.",
 "Each is unavailable to an AI while its war would come too early, through a hidden AI-only trigger in its `available` (round-27 review; until then an `ai_will_do` modifier reading 0, which run 8 showed is no hold) - see The story acts > *The AI*."),
# MLT's AI: Bone Dancers
("the plans list the invitation before the war focus, and Hail's `ai_will_do` is above Drown the Dance's, so the AI takes the Covenant when it can and fights when it cannot.",
 "the plans list the invitation before the war focus, and Drown the Dance is unavailable to an AI while the courtship holds, so the AI takes the Covenant when it can and fights when it cannot. The courtship holds the war only until 2281 (`mltd_ai_may_drown_the_dance`): with La Resistance no AI strategy builds the Bone Dancers' network or takes their civilian token, so an AI seldom meets Hail's gates."),
# MLT's AI unverified list
("  - that the engine skips a listed focus whose `ai_will_do` reads 0, rather than taking it - the war holds rely on this now that no `focus_factors` zero backs them;\n",
 "  - that a `hidden_trigger` hold in a *shared* focus's `available` (`mltd_ai_may_*`) behaves as it does in the national claim focuses (`mltd_ai_may_press_claims`) - run 8 settled that `ai_will_do` 0 is no hold;\n"),
# Gotchas: overflow
("The raw sums `mltd_national_population` and `mltd_controlled_population` themselves wrap past ~2.1M people, which the finale's 300 states reach (Plan > High priority); `mltd.73` prints no population for that reason.",
 "The population sums `mltd_national_population` and `mltd_controlled_population` wrapped past ~2.1M people, which the later story acts reach; since the round-27 review `mltd_update_national_population` sums them in thousands and caps the people figure at 2,147,000, below which every gate and guard sits (The rituals). `mltd.73` prints no population."),
# Testing round 27: Act III
("  - **Act III.** The Tide Turns South needs any one of the four and 50 controlled states.",
 "  - **Act III.** The Tide Turns South needs any one of the four and 50 controlled states, or the year 2281 (its tooltip names both)."),
# Testing round 27: spectator
("No war focus is taken before its hold lifts - The Turbines Sing only after the report's STAGE `ncr`. Each close follows its capitulation.",
 "No war focus is taken before its hold lifts - The Turbines Sing only after the report's STAGE `ncr`, The Tide-Wall only after STAGE `wbh`, Drown the Dance only from 2281 while the Bone Dancers are courted - because each hold is now in the focus's `available`. Each close follows its capitulation. Past ~2.15M people SNAP's `pop_k` keeps climbing while the Leviathan summon stays available (the population cap)."),
("    - an AI skipping a listed focus whose `ai_will_do` reads 0.\n",
 "    - an AI skipping a war focus while its `mltd_ai_may_*` hold fails (the hold is hidden in `available`; run 8 showed `ai_will_do` 0 is no hold).\n"),
# Plan: overflow item done
("- [ ] Fix the population sums' overflow. `mltd_update_national_population` sums raw `state_population` into `mltd_national_population` and `mltd_controlled_population`, and both wrap negative past ~2.1M people (Gotchas > script variables). The finale's 300 states reach that, and the plan puts MLT at 3-4M there. Once they wrap:\n  - the Leviathan summon's `available` (`mltd_controlled_population > 47999`) greys the decision out for a human too;\n  - the AI's late guards on both variables in `mltd_decisions.txt` switch off.\n\n  Suggested fix: sum `state_population_k` into `_k` twins beside the raw sums (OWB `exodus_effects.txt:385` idiom), and move the late tests to them. Keep the raw sums for the ritual gates, which sit far below the ceiling.\n",
 "- [x] Fix the population sums' overflow (round-27 review): `mltd_update_national_population` now sums `state_population_k` into `_k` variables and copies them back into people capped at 2,147,000 (The rituals). Confirm in a late game that the Leviathan summon stays available past ~2.15M people.\n"),
]
for a, b in reps:
    c = s.count(a)
    assert c == 1, (c, a[:100])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok', len(reps))
