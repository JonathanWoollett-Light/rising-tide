export const meta = {
  name: 'story-acts-integrate',
  description: 'Integrate the six built story acts into the mod: shared files, AI, plan, docs; then review and fix',
  phases: [
    { title: 'Integrate', detail: 'merge staging into shared files, delete the old sub-trees, telemetry, grid check' },
    { title: 'AI and plan', detail: 'AI focus plans, other AI references, CONQUEST_PLAN, check_plan_sync' },
    { title: 'Docs', detail: 'CLAUDE.md and README for the story acts' },
    { title: 'Review', detail: 'three-lens adversarial review of the integrated rework' },
    { title: 'Fix', detail: 'apply confirmed findings' },
  ],
}

const SPEC = 'C:\\Users\\jonat\\AppData\\Local\\Temp\\claude\\c--Users-jonat-Documents-rising-tide\\71877056-fecf-418a-a4f4-50b7c28bba62\\scratchpad\\story\\SPEC.md'
const STAGE = 'C:\\Users\\jonat\\AppData\\Local\\Temp\\claude\\c--Users-jonat-Documents-rising-tide\\71877056-fecf-418a-a4f4-50b7c28bba62\\scratchpad\\story\\'
const BUILD = 'C:\\Users\\jonat\\AppData\\Local\\Temp\\claude\\c--Users-jonat-Documents-rising-tide\\71877056-fecf-418a-a4f4-50b7c28bba62\\tasks\\w5gfb0k14.output'
const REPO = 'C:\\Users\\jonat\\Documents\\rising-tide'
const OWB = 'C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\394360\\2265420196'

const CONTEXT = `Context: the HOI4 submod "OWB - Rising Tide" (repo ${REPO}) is being reworked from ten side-by-side conflict sub-trees into one narrative spine of story acts. The build spec is ${SPEC} (read it fully). Six agents have built the acts: each wrote mod_folder/common/national_focus/mltd_act2_focus.txt ... mltd_act6_focus.txt and mltd_finale_focus.txt, and put everything meant for SHARED files in staging folders ${STAGE}act2\\ ... act6\\ and finale\\ (events.txt, loc.yml, ideas.txt, triggers.txt, effects.txt, notes.md). Their full reports (focus lists, deleted ids and where their effects went, new and replaced loc keys, events, ideas, keys made unused, unverified points) are the JSON in ${BUILD}. The orchestrator already edited the override mod_folder/common/national_focus/Mirelurk Tribe (MLT) Focus.txt: the ten old shared_focus root lines are replaced by the seven new listed roots, and mltd_the_final_ritual now sits at (0,3) from the Walk with an OR prerequisite over the three Act II ends. OWB is at ${OWB}.`

const INTEGRATE_SCHEMA = {
  type: 'object',
  properties: {
    done: { type: 'array', items: { type: 'string' } },
    removed_keys: { type: 'array', items: { type: 'string' } },
    kept_despite_listed_unused: { type: 'array', items: { type: 'string' } },
    grid_check: { type: 'string' },
    pull_in_check: { type: 'string' },
    problems: { type: 'array', items: { type: 'string' } },
  },
  required: ['done', 'removed_keys', 'kept_despite_listed_unused', 'grid_check', 'pull_in_check', 'problems'],
}
const AIPLAN_SCHEMA = {
  type: 'object',
  properties: {
    done: { type: 'array', items: { type: 'string' } },
    ai_order: { type: 'string' },
    plan_changes: { type: 'string' },
    deviations: { type: 'array', items: { type: 'string' } },
    check_plan_sync: { type: 'string' },
    problems: { type: 'array', items: { type: 'string' } },
  },
  required: ['done', 'ai_order', 'plan_changes', 'deviations', 'check_plan_sync', 'problems'],
}
const DOCS_SCHEMA = {
  type: 'object',
  properties: { done: { type: 'array', items: { type: 'string' } }, problems: { type: 'array', items: { type: 'string' } } },
  required: ['done', 'problems'],
}
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      file: { type: 'string' }, where: { type: 'string' }, problem: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['severity', 'file', 'where', 'problem', 'evidence', 'fix'] } },
    checked: { type: 'string' },
  },
  required: ['findings', 'checked'],
}
const FIX_SCHEMA = {
  type: 'object',
  properties: {
    applied: { type: 'array', items: { type: 'string' } },
    rejected: { type: 'array', items: { type: 'string' } },
    final_checks: { type: 'string' },
  },
  required: ['applied', 'rejected', 'final_checks'],
}

phase('Integrate')
const integ = await agent(`${CONTEXT}

Your job: integrate the staged work into the mod's shared files. Do NOT touch the AI files (common/ai_strategy*, common/ai_templates, scripted_triggers/mltd_ai_triggers.txt, scripted_effects/mltd_ai_survey_effects.txt), CONQUEST_PLAN.txt, CLAUDE.md or README.md - later agents do those.

1. Delete mod_folder/common/national_focus/mltd_conflicts_focus.txt (every focus it held is either rebuilt in an act file or merged away - confirm by listing its 46 ids against the act files and the reports' deleted_ids before deleting).
2. Merge each staging events.txt into mod_folder/events/mltd_events.txt (append after the existing events, in id order mltd.30-31, 40-41, 50-52, 60-62, 70-74, under one comment header per act), each staging ideas.txt into mod_folder/common/ideas/mltd_ideas.txt (inside the right block - read the file's structure), and staging triggers.txt / effects.txt into mltd_scripted_triggers.txt / mltd_scripted_effects.txt. Keep each file's line endings, BOM state and style.
3. Merge each staging loc.yml into mod_folder/localisation/english/MLT/mltd_l_english.yml: a key that already exists is REPLACED in place (never duplicated), new keys go at the end under a '  ### Round 27: the story acts' comment, grouped by act. The file must keep its UTF-8 BOM and LF; write with Python in binary, and make sure non-ASCII characters (§, ä, ') arrive as correct UTF-8.
4. Delete the loc keys, tooltips, scripted effects/triggers and comments that the reports list as now_unused - but ONLY after grepping the whole mod_folder (script, gui, loc values' $key$ references, scripted_localisation) and the repo's python tools to confirm nothing references them; list any you kept. Also scan mltd_l_english.yml for any key whose name starts with a deleted focus id (e.g. mltd_ces_the_drowned_frumentarius_*) or a sub-tree tooltip only the old file used. Fix comments in non-AI files that still describe the deleted focuses or 'the conflict sub-trees' (e.g. mltd_scripted_effects.txt near mltd_brk_add_volunteer_size, mltd_on_actions.txt's Haida watch, mltd_ideas.txt headers), briefly and accurately.
5. build_telemetry.py hard-codes mltd_conflicts_focus.txt (around line 140) and ai_run_report.py may too: make them read the story acts (the pulled-in shared focuses now come from mltd_act*_focus.txt and mltd_finale_focus.txt - group them as one 'story acts' list in act order), then run 'python build_telemetry.py' from the repo root and fix what it reports. (check_plan_sync.py will still fail on the plan and AI - that is the next agent's job; do not edit the plan or AI to make it pass.)
6. Verify, with scripts you write: (a) every focus of mlt_nf - OWB's national ones in the override plus every shared focus pulled in (listed roots, then transitively through shared prerequisites) - resolves to a unique grid cell (resolve relative_position_id chains across files); report any overlap. (b) Every one of the 39 story focuses in the spec is pulled in, and nothing that should not be. (c) Brace balance of every file you or the builders touched. (d) Every loc key referenced by the act files, events, ideas and triggers (focus ids and their _desc, custom_effect_tooltip, custom_trigger_tooltip, tooltip =, event titles/descs/options, idea names) is defined; every $key$ nested in a new or replaced value resolves one level to a plain-text key. (e) Every country_event / news_event id fired by an act file exists in mltd_events.txt, and none is defined twice.
Return the JSON.`, { label: 'integrate', phase: 'Integrate', schema: INTEGRATE_SCHEMA })

phase('AI and plan')
const aiplan = await agent(`${CONTEXT}

The integration agent has now merged everything into the shared files and deleted mltd_conflicts_focus.txt. Its report: ${JSON.stringify(integ)}.

Your job: bring MLT's AI and CONQUEST_PLAN.txt in step with the new tree (CLAUDE.md > Project: the plan, the code and the AI must agree; and 'MLT's AI', 'Fair play').
1. mod_folder/common/ai_strategy_plans/mltd_MLT.txt: remove every deleted focus id; re-order ai_national_focuses to follow the acts. In the Kingdom-and-Books plan, after the Grand Ritual and the Walk, take the Broken Coast pair first (mltd_brk_salt_on_the_broken_coast, mltd_brk_the_deep_ones_sail_north - it reconverges into the Final Ritual and it is the volunteers the NCR's stage waits on), then mltd_the_final_ritual, then the other Act II beads as fillers. In the late plan: Act III (the Covenant and Hail before Drown the Dance, The Tide-Wall), mltd_the_tide_turns_south, Act IV, Act V, Act VI, the finale and the endings, keeping OWB's claim focuses where they sit today. Review focus_factors: capstones that were zeroed because they were reachable years early are now reachable only after their act's chapter - keep a zero only where it still guards something, and explain each change in a comment.
2. Grep all AI files (common/ai_strategy/*.txt, scripted_triggers/mltd_ai_triggers.txt, scripted_effects/mltd_ai_survey_effects.txt, on_actions, scorers) for deleted focus ids and for logic that assumed the old sub-trees (e.g. 'a volunteer focus is done', the cult scorer's shelter logic, mltd_ai_brk_helped, the capstones' stage gates) and update them. Fair play applies: nothing AI-only that a human would not get.
3. CONQUEST_PLAN.txt: re-cut every focus line and its # comments from the Walk to the end so the plan takes the acts in order (Act II between the Walk and the Final Ritual; Act III after it, then The Tide Turns South; the NCR act; the Legion act; the south act; the finale and an ending). Keep dates and snapshots consistent (the focus days changed; the two research slots at When Shady Sands Falls and The Last King Kneels change the plan's research - update 'Research is fixed at 3 slots' and the research lines); update the notes at the end (the focus-slot saturation paragraph: count the new story's focus days from the act files) and every '# AI deviation:' line that names a deleted focus. Where the AI deliberately differs from the plan, add a deviation line.
4. Run 'python build_telemetry.py' and 'python check_plan_sync.py' from the repo root and iterate until check_plan_sync prints OK. Also run 'python ai_run_report.py --selftest'.
Return the JSON.`, { label: 'ai-and-plan', phase: 'AI and plan', schema: AIPLAN_SCHEMA })

const LENSES = [
  { key: 'script', prompt: `Lens: SCRIPT CORRECTNESS AND CROSS-FILE CONSISTENCY. Check every story file (mod_folder/common/national_focus/mltd_act*_focus.txt, mltd_finale_focus.txt, the override's story roots and the Final Ritual) and everything they reference in mltd_events.txt, mltd_ideas.txt, mltd_scripted_triggers.txt / _effects.txt and the loc: syntax, scopes, effect/trigger/modifier names against vanilla documentation (C:\\Program Files (x86)\\Steam\\steamapps\\common\\Hearts of Iron IV\\documentation\\*.md) and OWB, every loc key and sprite (icons and their _shine, event pictures, idea pictures) existing, events defined once and fired correctly, the pull-in rule (a shared focus enters only through a listed root or shared prerequisites), grid overlaps (write a resolver), relative_position_id only onto shared focuses, nothing left anywhere in mod_folder or the python tools that names a deleted focus id or mltd_conflicts_focus.txt.` },
  { key: 'progression', prompt: `Lens: PROGRESSION AND AI. Simulate the tree as a human and as an AI MLT through every act, including the bad cases: a target annexed by someone else (NCR, CES, BOS, WHT/EHT, HEA, TBH/LNS, TLA and heirs, ATE, WBH/TCA, BRK, BDT), a target that became MLT's subject, MLT at war with BRK, The Warren lost, Mireport lost, population gates, the Hoover/texas/2280 date gates. Find any OR reconvergence or close that can be stranded, any focus an AI will never take or will take too early (read mod_folder/common/ai_strategy_plans/mltd_MLT.txt, the ai_will_do blocks, and mltd_ai_triggers.txt's stages), anything AI-only (fair play), and any mismatch between CONQUEST_PLAN.txt and the AI or the code (ids, order, numbers the plan quotes). Run python check_plan_sync.py.` },
  { key: 'story', prompt: `Lens: NARRATIVE AND LOCALISATION. Read the whole story from Act I (the override's trunk and its loc) through the finale in order - focus names and descriptions, every event (.t/.d/.a), idea names - as a player would, and judge whether it reads as ONE coherent story with rising stakes, consistent names and lore (M'lulu, M'lyeh vs R'lyeh, the Esoteric Order, Father Dagon the Leviathan, the Deep Ones, the Star Spawn), no contradictions between acts, and each close feeling like a payoff. Check the house loc rules in CLAUDE.md: countries/states/characters through functions, our own things through $key$ nesting one level deep to plain-text keys (never a localisation/replace key inside a sentence), event .d text only §o and §c, option text no colour codes, no hard-coded 'Mirelurk Tribe', Lovecraft named only from pre-1930 stories, encoding (UTF-8 with BOM, non-ASCII characters intact). Report concrete text fixes.` },
]

const [docs, reviews] = await Promise.all([
  agent(`${CONTEXT}

The integration and AI/plan agents are done. Integration report: ${JSON.stringify(integ)}. AI/plan report: ${JSON.stringify(aiplan)}.

Your job: update CLAUDE.md (and README.md where it describes the focus tree) for round 27, the story acts. CLAUDE.md is the project's single reference: keep its style (explain mechanisms and name the file, effect, variable or loc key; the code is the source of truth for costs - do not restate focus lengths or prices beyond what the existing text already does for comparable content), its tables and its tone. At least: the Project section's current-state paragraph (add round 27, not play-tested) and the beat table (the Final Ritual's new prerequisite; the story acts after it), the 'Round 13' paragraph about the conflict sub-trees (now history - say what replaced them), the Layout table (the per-act focus files replace mltd_conflicts_focus.txt; events, ideas, triggers rows), 'Overriding OWB' (the override's root lines and the Final Ritual edit), the whole 'Conflict sub-trees' mechanics section rewritten as 'The story acts' (the spine/fan/close structure, the pull-in and listed roots, the positions table, the never-strand rule and the dropped intel gates, the AI's order, and a per-act table of focuses with gates and payoffs taken from the act files - keep the useful per-focus facts of the old table that still hold), the Gotchas that mention the sub-trees, Naming conventions (event ids now taken: 1-27, 30-31, 40-41, 50-52, 60-62, 70-74, 101-503; next free), the MLT's AI section where it describes the capstones' stage gates and the plans' focus order, a 'Round 27' Testing entry (what to confirm in game), and the Plan section if relevant. Read the act files, the merged events/ideas/loc and the AI plan to describe what is really there. Return the JSON.`, { label: 'docs', phase: 'Docs', schema: DOCS_SCHEMA }),
  parallel(LENSES.map(l => () => agent(`${CONTEXT}

Integration report: ${JSON.stringify(integ)}. AI/plan report: ${JSON.stringify(aiplan)}.

You are an adversarial reviewer of the integrated rework. ${l.prompt}
Report only real problems, each with evidence (file:line, command output) and a concrete fix. Do not edit files. Return the JSON.`, { label: `review:${l.key}`, phase: 'Review', schema: REVIEW_SCHEMA }))),
])

const findings = reviews.filter(Boolean).flatMap((r, i) => r.findings.map(f => ({ ...f, lens: LENSES[i].key })))
log(`${findings.length} review findings (${findings.filter(f => f.severity === 'blocker').length} blockers, ${findings.filter(f => f.severity === 'major').length} major)`)

phase('Fix')
let fix = null
if (findings.length) {
  fix = await agent(`${CONTEXT}

Everything is integrated, the AI and plan are updated and CLAUDE.md is being/has been updated (docs report: ${JSON.stringify(docs)}). Three adversarial reviewers found: ${JSON.stringify(findings)}.

For each finding: verify it yourself against the files, OWB and vanilla. If real, fix it (any file in the repo, keeping encodings, line endings and the house rules; if a fix changes something CLAUDE.md or CONQUEST_PLAN.txt describes, update them too). If wrong, reject it with the reason. Afterwards run 'python build_telemetry.py', 'python check_plan_sync.py' (must print OK) and 'python ai_run_report.py --selftest', and re-run a brace-balance check on every file you touched. Return the JSON.`, { label: 'fix', phase: 'Fix', schema: FIX_SCHEMA })
}

return { integ, aiplan, docs, findings, fix }
