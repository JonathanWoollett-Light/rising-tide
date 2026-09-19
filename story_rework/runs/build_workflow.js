export const meta = {
  name: 'story-acts-build',
  description: 'Build the six story acts of the MLT focus rework in parallel, then review and fix each act',
  phases: [
    { title: 'Build', detail: 'one agent per act writes its focus file and staging parts' },
    { title: 'Review', detail: 'adversarial reviewer per act' },
    { title: 'Fix', detail: 'apply confirmed review findings to that act' },
  ],
}

const SPEC = 'C:\\Users\\jonat\\AppData\\Local\\Temp\\claude\\c--Users-jonat-Documents-rising-tide\\71877056-fecf-418a-a4f4-50b7c28bba62\\scratchpad\\story\\SPEC.md'
const STAGE = 'C:\\Users\\jonat\\AppData\\Local\\Temp\\claude\\c--Users-jonat-Documents-rising-tide\\71877056-fecf-418a-a4f4-50b7c28bba62\\scratchpad\\story\\'
const REPO = 'C:\\Users\\jonat\\Documents\\rising-tide'

const ACTS = [
  { key: 'act2', title: 'ACT II - "The Northern Waters"', file: 'mltd_act2_focus.txt' },
  { key: 'act3', title: 'ACT III - "The Stars Are Right"', file: 'mltd_act3_focus.txt' },
  { key: 'act4', title: 'ACT IV - "The Drowned Republic"', file: 'mltd_act4_focus.txt' },
  { key: 'act5', title: 'ACT V - "The Sea Against Mars"', file: 'mltd_act5_focus.txt' },
  { key: 'act6', title: 'ACT VI - "All Waters Are One"', file: 'mltd_act6_focus.txt' },
  { key: 'finale', title: 'FINALE - "R\'lyeh Rises"', file: 'mltd_finale_focus.txt' },
]

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    act: { type: 'string' },
    files_written: { type: 'array', items: { type: 'string' } },
    focuses: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, cell: { type: 'string' }, prerequisites: { type: 'string' }, status: { type: 'string' } },
      required: ['id', 'cell', 'prerequisites', 'status'] } },
    deleted_ids: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, merged_into: { type: 'string' }, what_moved: { type: 'string' } },
      required: ['id', 'merged_into', 'what_moved'] } },
    loc_keys_new: { type: 'array', items: { type: 'string' } },
    loc_keys_replaced: { type: 'array', items: { type: 'string' } },
    events: { type: 'array', items: { type: 'string' } },
    ideas: { type: 'array', items: { type: 'string' } },
    scripted_triggers: { type: 'array', items: { type: 'string' } },
    scripted_effects: { type: 'array', items: { type: 'string' } },
    now_unused: { type: 'array', items: { type: 'string' } },
    unverified: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['act', 'files_written', 'focuses', 'deleted_ids', 'loc_keys_new', 'loc_keys_replaced', 'events', 'ideas',
    'scripted_triggers', 'scripted_effects', 'now_unused', 'unverified', 'notes'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
      file: { type: 'string' }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } },
      required: ['severity', 'file', 'where', 'problem', 'fix'] } },
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

function buildPrompt(a) {
  return `You are implementing ${a.title} of a focus-tree rework for the HOI4 submod "OWB - Rising Tide" (repo ${REPO}).

Read the whole build spec first: ${SPEC}. It defines the new story structure, the architecture rules every act follows, your act's table (ids, cells, prerequisites, content), and exactly where your output goes. Then read the parts of CLAUDE.md you need (Conflict sub-trees, Events, Localisation: functions not names, Gotchas) and the blocks of your kept focuses in mod_folder/common/national_focus/mltd_conflicts_focus.txt (READ-ONLY), plus the blocks of the focuses the merge map deletes into yours, and their loc in mod_folder/localisation/english/MLT/mltd_l_english.yml. Use OWB (C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\394360\\2265420196) and vanilla HOI4 (C:\\Program Files (x86)\\Steam\\steamapps\\common\\Hearts of Iron IV, see documentation/*.md) to check every effect, trigger, modifier, sprite and idea picture you use.

Write:
- mod_folder/common/national_focus/${a.file} (your act's shared focuses, LF, no BOM, tabs, a header comment explaining the act and the merges),
- your staging folder ${STAGE}${a.key}\\ with events.txt, loc.yml, ideas.txt, triggers.txt, effects.txt, notes.md as the spec's table says (create only the ones you need; notes.md always).
Do not edit any other file in mod_folder/.

Write the loc for every new focus (name + _desc, evocative, in the mod's existing voice - read a few existing descs first), every new tooltip, event and idea. Where a merge changes what a kept focus does, rewrite its _desc if it no longer fits, as a replacement key in loc.yml. Keep every existing number that you carry over; the spec's balance guide sets new ones.

Before returning, check your own work: brace balance of every file (count { and } outside comments and strings with a short python script), every loc key you reference is defined (in the main yml or your loc.yml), every scripted effect/trigger you call exists (grep mod_folder and OWB) or is in your staging, every cell and prerequisite matches the spec table. Then return the JSON.`
}

function reviewPrompt(a, built) {
  return `You are an adversarial reviewer of ${a.title} of the MLT focus-tree rework (repo ${REPO}). Assume it is wrong until you have checked it. The build spec is ${SPEC} - read it fully. The builder's report: ${JSON.stringify(built)}.

Review mod_folder/common/national_focus/${a.file} and the staging folder ${STAGE}${a.key}\\ against the spec, CLAUDE.md, OWB (C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\394360\\2265420196) and vanilla (C:\\Program Files (x86)\\Steam\\steamapps\\common\\Hearts of Iron IV, documentation/*.md). Check at least:
1. Syntax: brace balance (script it), no stray tokens, LF/no BOM/tabs for the focus file; staging loc lines are '  key:0 "..."' with escaped inner quotes.
2. Structure: every focus in the spec table exists with the exact id, cell (absolute or the given relative_position_id + offset), prerequisites (AND = separate blocks, OR = one block), mutually_exclusive where specified; no extra focuses; kept ids unchanged; listed roots and tide_turns_south absolute, everything else relative to a SHARED focus.
3. Never strand: every fan bead takeable when its target is gone (fallback reward); no has_operation_token / network_national_coverage / intel_level_over in any available (except Covenant and Hail); cancel_if_invalid = no and continue_if_invalid = yes on every focus.
4. AI: ai_will_do per spec rule 7; war capstones keep their stage/readiness modifiers; no round-23 'wait for an earlier act' modifiers left.
5. Every effect, trigger, modifier key, idea, tech, sprite (focus icon AND its _shine, event pictures, idea pictures), character token, state/province id and country tag used really exists - grep mod_folder, OWB and vanilla; scopes are right (e.g. OWB add_state_population is a state-scope scripted effect reading temp pop_add; add_research_slot is country scope; declare_war_on syntax; will_lead_to_war_with).
6. Loc: every key referenced (focus name/_desc, custom_effect_tooltip, custom_trigger_tooltip, event .t/.d/.a..., ideas, news) is defined in mod_folder/localisation/english/MLT/mltd_l_english.yml or the staging loc.yml; $key$ nesting only one level deep to a plain-text key and never to a localisation/replace key inside a sentence; countries/states/characters named through functions ([TAG.GetNameDef], [ID.GetName], [TOKEN.GetName]); event .d text uses only §o and §c, options no colour codes; no hard-coded 'Mirelurk Tribe'.
7. Merges: each deleted focus named in the spec's merge map has its distinctive effects in the right kept focus, with guards (has_equipment thresholds >= the amount taken, theft pairs without producer on the removal), La Resistance-only effects inside has_dlc ifs with non-DLC fallbacks.
8. Events: ids per the spec's allocation, country events is_triggered_only + fire_only_once + the log line, news events delivered to every_other_country by the focus; every option name defined; ai_chance where the spec asks.
9. Balance per the spec's guide; fair play (nothing AI-only).
Only report real problems, each with a concrete fix. Return the JSON.`
}

function fixPrompt(a, built, review) {
  return `You are fixing ${a.title} of the MLT focus-tree rework (repo ${REPO}). The build spec is ${SPEC}. The builder's report: ${JSON.stringify(built)}.

An adversarial review found these problems: ${JSON.stringify(review.findings)}.

For each finding: verify it against the files (mod_folder/common/national_focus/${a.file} and ${STAGE}${a.key}\\), OWB and vanilla. If it is real, fix it - editing ONLY those files. If it is wrong, reject it with the reason. Then re-run the brace-balance check and a check that every loc key you reference is defined, and update ${STAGE}${a.key}\\notes.md if anything the integrator must know changed (new keys, unused keys, unverified constructs). Return the JSON.`
}

phase('Build')
const results = await pipeline(
  ACTS,
  a => agent(buildPrompt(a), { label: `build:${a.key}`, phase: 'Build', schema: BUILD_SCHEMA }),
  (built, a) => agent(reviewPrompt(a, built), { label: `review:${a.key}`, phase: 'Review', schema: REVIEW_SCHEMA })
    .then(review => ({ built, review })),
  (br, a) => {
    if (!br || !br.review || br.review.findings.length === 0) return { act: a.key, built: br && br.built, review: br && br.review, fix: null }
    return agent(fixPrompt(a, br.built, br.review), { label: `fix:${a.key}`, phase: 'Fix', schema: FIX_SCHEMA })
      .then(fix => ({ act: a.key, built: br.built, review: br.review, fix }))
  },
)
return results
