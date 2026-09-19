export const meta = {
  name: 'story-acts-finish',
  description: 'Finish round 27: confirm the 20 review findings, review the fixer\'s own changes, verify new findings, fix',
  phases: [
    { title: 'Confirm', detail: 'one agent per earlier review finding: resolved, partly, or not' },
    { title: 'Review', detail: 'fresh lenses on the state after the fixer' },
    { title: 'Verify', detail: 'two refuters per new finding' },
    { title: 'Fix', detail: 'one agent applies everything confirmed' },
  ],
}

const REPO = 'C:\\Users\\jonat\\Documents\\rising-tide'
const OWB = 'C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\394360\\2265420196'
const VAN = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\Hearts of Iron IV'
const CTX = `Context: the HOI4 submod "OWB - Rising Tide" (repo ${REPO}; OWB at ${OWB}; vanilla at ${VAN}, its documentation/*.md lists every effect, trigger and modifier). Round 27 rebuilt MLT's ten conflict sub-trees into one narrative spine of story acts (six files mod_folder/common/national_focus/mltd_act2_focus.txt ... mltd_act6_focus.txt and mltd_finale_focus.txt, 39 shared focuses), merged into the shared files, updated the AI, CONQUEST_PLAN.txt and CLAUDE.md. CLAUDE.md > "The story acts" describes the result. The handoff is ${REPO}\\story_rework\\HANDOFF.md, the build spec ${REPO}\\story_rework\\SPEC.md (where they differ, the code wins). A fixer applied most of an adversarial review's 20 findings and was stopped before reporting; its edit scripts are ${REPO}\\story_rework\\runs\\fix_loc.py, fix_plan.py, fix_claude.py. Nothing has been run in the game. Work from the files as they are now.`

const FINDINGS = [
  { id: 'F1', lens: 'script', sev: 'major', text: 'mltd_update_national_population summed raw state_population; the variables wrap negative past ~2,147,483 people, which the late acts reach, breaking the Final Ritual gate, the Leviathan summon (mltd_decisions.txt) and the AI guards.' },
  { id: 'F2', lens: 'script', sev: 'minor', text: 'mltd_ncr_beaten_tt said the NCR "has capitulated to us" while mltd_ai_ncr_beaten also passes on a capitulation to anyone (e.g. to the Legion). Also CONQUEST_PLAN.txt wording.' },
  { id: 'F3', lens: 'script', sev: 'minor', text: 'Comments in the act files and elsewhere still name deleted focus ids or mltd_conflicts_focus.txt; nothing in mod_folder or the python tools should reference a deleted focus id as if it existed.' },
  { id: 'F4', lens: 'progression', sev: 'blocker', text: 'Every story war focus is listed in the AI late plan and was held only by an ai_will_do modifier reading 0, which does not stop the AI (run 8 took The Tide-Wall and The Turbines Sing early). Holds must be in available (the mltd_ai_may_* triggers, section W of mltd_ai_triggers.txt).' },
  { id: 'F5', lens: 'progression', sev: 'major', text: 'mltd_the_tide_turns_south needs 50 controlled states with no fallback; an AI that stalls in the north never gets past Act III.' },
  { id: 'F6', lens: 'progression', sev: 'major', text: 'Same population overflow as F1, seen from the AI guards (mltd_decisions.txt summon/offering ai_will_do).' },
  { id: 'F7', lens: 'progression', sev: 'minor', text: 'With La Resistance, no AI strategy builds a network in BDT, points the cult operations at it or obtains its civilian token, so an AI can essentially never meet Hail the Drowned King\'s gates; Drown the Dance\'s AI hold then waits forever on the courtship.' },
  { id: 'F8', lens: 'progression', sev: 'minor', text: 'CONQUEST_PLAN.txt\'s day-0 header says 3 research slots for the whole game; the plan now adds a 4th at When Shady Sands Falls and a 5th at The Last King Kneels.' },
  { id: 'F9', lens: 'progression', sev: 'minor', text: 'The plan takes both invitations (Covenant, Hail) but never sets up their La Resistance gates (BDT network, cult operation, civilian token; BRK civilian token/intel).' },
  { id: 'F10', lens: 'story', sev: 'major', text: 'mltd_the_final_ritual_desc and mltd.6.d were written when the Final Ritual was the climax; the city now only rises at R\'lyeh Rises (row 39), so they promise what completion does not deliver.' },
  { id: 'F11', lens: 'story', sev: 'major', text: 'Act VI\'s opening (mltd_the_southern_deep_desc, mltd.60.d, mltd_ate_the_feathered_tide_desc) describes Tlaloc as alive/dying, but on the plan\'s timeline OWB\'s drain kills him years before Act VI.' },
  { id: 'F12', lens: 'story', sev: 'major', text: 'mltd_the_last_king_kneels_desc and mltd.61.d state an order of fallen kings (Texas last) the tree does not enforce.' },
  { id: 'F13', lens: 'story', sev: 'minor', text: 'mltd.70.a chants that M\'lulu waits dreaming in R\'lyeh, but the finale reveals the Dreamer waits and M\'lulu stands awake.' },
  { id: 'F14', lens: 'story', sev: 'minor', text: 'mltd.24.d (the Bone Dancers\' invitation) says an older king "is awake", contradicting the finale where the Dreamer sleeps until one optional ending.' },
  { id: 'F15', lens: 'story', sev: 'minor', text: 'The Tide Turns South texts (desc, mltd.30.d, mltd.31.d) assert all three northern peoples have answered, but the close opens after any one of four and 50 states.' },
  { id: 'F16', lens: 'story', sev: 'minor', text: 'Act III fan texts (mltd_wbh_the_tide_wall_desc, mltd.21.d, mltd_bdt_drown_the_dance_desc) lean on Act II beads the new prerequisites no longer require.' },
  { id: 'F17', lens: 'story', sev: 'minor', text: 'Act VI\'s opening (mltd.60.a, mltd_the_southern_deep_desc) repeats Act III\'s "the tide turns south" beat almost word for word.' },
  { id: 'F18', lens: 'story', sev: 'minor', text: 'Payoff events repeat their focus descriptions (mltd_when_shady_sands_falls_desc vs mltd.40.d; mltd_rlyeh_rises_desc vs mltd.70.d; others) instead of paying them off.' },
  { id: 'F19', lens: 'story', sev: 'minor', text: 'mltd_ncr_beaten_tt understates its trigger (same as F2) compared with mltd_legion_beaten_tt.' },
  { id: 'F20', lens: 'story', sev: 'minor', text: 'Act V\'s order is backwards in the text: mltd.50.d (chapter, row 31) is written by an oracle ferryman while mltd_ces_what_the_river_carries_desc (row 32) has the frumentarii hanging ferrymen.' },
]

const CONFIRM_SCHEMA = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    status: { type: 'string', enum: ['resolved', 'partly', 'unresolved', 'finding_was_wrong'] },
    evidence: { type: 'string' },
    remaining_fix: { type: 'string' },
    fix_introduced_problem: { type: 'string' },
  },
  required: ['id', 'status', 'evidence', 'remaining_fix', 'fix_introduced_problem'],
}
const FIND_SCHEMA = {
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
const VOTE_SCHEMA = {
  type: 'object',
  properties: { refuted: { type: 'boolean' }, reason: { type: 'string' } },
  required: ['refuted', 'reason'],
}
const FIX_SCHEMA = {
  type: 'object',
  properties: {
    applied: { type: 'array', items: { type: 'string' } },
    rejected: { type: 'array', items: { type: 'string' } },
    checks: { type: 'string' },
  },
  required: ['applied', 'rejected', 'checks'],
}

const LENSES = [
  { key: 'script', prompt: `Lens: SCRIPT CORRECTNESS of what changed since the review. Focus on the fixer's and integrator's own edits, which nobody has reviewed: section W of mod_folder/common/scripted_triggers/mltd_ai_triggers.txt (the mltd_ai_may_* holds) and how each story war focus calls it from available (is hidden_trigger / if / is_ai valid there, in a shared focus; does the trigger's tooltip leak; does each hold lift exactly when CLAUDE.md > The story acts > The AI says); mltd_update_national_population's _k rewrite (clamp_variable syntax, every reader of mltd_national_population / mltd_controlled_population and their _k twins incl. telemetry and ai_run_report); the on_capitulation block in mltd_on_actions.txt (scopes ROOT/FROM, has_war_with inside it, the four flags) and mltd_ai_ncr_beaten / mltd_ai_legion_beaten / mltd_texas_beaten; the Tide Turns South date fallback; every loc key referenced by the six story files, events mltd.30-74, the ideas and triggers existing, and every $key$ nest one level deep to a plain key. Write small scripts to check references mechanically; check scripting constructs against vanilla documentation and OWB usage.` },
  { key: 'progression', prompt: `Lens: PROGRESSION, AI AND FAIR PLAY after the fixes. Walk each act as a human and as an AI MLT, including annexed/subject targets, BRK war, Warren/Mireport lost, and a peace that leaves a rump NCR/CES/Texas alive (the on_capitulation flags). Check the AI plans' ai_national_focuses order (mod_folder/common/ai_strategy_plans/mltd_MLT.txt) against the holds so the AI neither strands nor jumps a stage; that the AI-only holds in available only restrict the AI and never give it anything a human would not get (CLAUDE.md > MLT's AI > Fair play); and that CONQUEST_PLAN.txt, the AI and the code agree on ids, order and the numbers the plan quotes for the story acts. Run python check_plan_sync.py and python ai_run_report.py --selftest.` },
  { key: 'docs', prompt: `Lens: DOCUMENTATION ACCURACY. CLAUDE.md is the project's single reference and was heavily rewritten for round 27 (Project, Layout, Overriding OWB, The story acts, MLT's AI, Gotchas, Naming, Testing > Round 27, Plan) and README.md. Check every round-27 claim against the code: ids, cells, prerequisites, gates, payoffs in the per-act table, event ids, idea names and modifiers mentioned, trigger names, file names, the listed-root line numbers, the population cap, the holds table, the plans' order, the unverified list. Also flag contradictions left between older sections and round 27 (e.g. text that still speaks of conflict sub-trees as current, counts that changed), and anything CLAUDE.md's own rule forbids (restating costs the code holds, beyond what comparable text already does). Report precise corrections.` },
  { key: 'story', prompt: `Lens: NARRATIVE AFTER THE FIXES. Read the story from the Kingdom (mod_folder/localisation/english/MLT/mltd_l_english.yml; the trunk focuses and mltd.1-8) through every act's focus names and descriptions, events mltd.21-26 and mltd.30-74 and the act ideas, in tree order, as a player would. Judge whether it now reads as one coherent story with rising stakes and consistent lore (M'lulu, M'lyeh vs R'lyeh, the Esoteric Order, Father Dagon, the Dreamer, Tlaloc's fate on the plan's timeline, Nuevo Aztlan's own OWB lore - check its loc names), whether each close pays off rather than repeats, and whether the house loc rules hold (CLAUDE.md > Localisation: functions not names; event .d only §o and §c, options no colour codes; no hard-coded "Mirelurk Tribe"; Lovecraft only pre-1930 by name; UTF-8 with BOM intact, non-ASCII like the a-umlaut in mltd.72.a and the o-acute in Aztlán correct). Report concrete text fixes, quoting the current text.` },
]

phase('Confirm')
const confirmP = parallel(FINDINGS.map(f => () => agent(`${CTX}

An earlier adversarial review found this (${f.id}, ${f.lens} lens, ${f.sev}): ${f.text}

Determine from the CURRENT files whether it is resolved. Look at exactly the places named, and at anything the fix should have touched. Say 'resolved' only with concrete evidence (file:line and what it now says); 'partly' or 'unresolved' with the exact remaining fix; 'finding_was_wrong' if on inspection it never held. Also report any problem the fix itself introduced (syntax, a broken reference, a contradiction with CLAUDE.md or CONQUEST_PLAN.txt), or an empty string. Do not edit files.`, { label: `confirm:${f.id}`, phase: 'Confirm', schema: CONFIRM_SCHEMA })))

const reviewP = parallel(LENSES.map(l => () => agent(`${CTX}

You are an adversarial reviewer. ${l.prompt}
Report only real problems, each with evidence (file:line, command output, quoted text) and a concrete fix. Do not edit files.`, { label: `review:${l.key}`, phase: 'Review', schema: FIND_SCHEMA })))

const [confirms, reviews] = await Promise.all([confirmP, reviewP])

const open = confirms.filter(Boolean).filter(c => c.status === 'partly' || c.status === 'unresolved' || (c.fix_introduced_problem && c.fix_introduced_problem.trim().length > 3))
log(`earlier findings: ${confirms.filter(Boolean).filter(c => c.status === 'resolved').length} resolved, ${open.length} still open or with a fix-introduced problem`)

const fresh = reviews.filter(Boolean).flatMap((r, i) => r.findings.map(f => ({ ...f, lens: LENSES[i].key })))
log(`${fresh.length} new findings to verify`)

phase('Verify')
const verified = await parallel(fresh.map((f, i) => () => parallel([0, 1].map(k => () => agent(`${CTX}

A reviewer (${f.lens} lens) claims: [${f.severity}] ${f.file} @ ${f.where}: ${f.problem}
Evidence given: ${f.evidence}
Proposed fix: ${f.fix}

Try to REFUTE it. Check the actual files, OWB and vanilla documentation yourself. It is refuted if the problem does not exist, is already handled elsewhere, rests on a wrong reading of the engine or the code, or the proposed fix would be wrong or make things worse (say which). If the problem is real but the fix is wrong, it is NOT refuted - give the right fix in your reason. If uncertain after checking, lean refuted=true. Do not edit files.`, { label: `verify:${i}:${k}`, phase: 'Verify', schema: VOTE_SCHEMA })))
  .then(vs => ({ f, votes: vs.filter(Boolean) }))))

const confirmedNew = verified.filter(Boolean).filter(v => v.votes.filter(x => !x.refuted).length >= 1 && v.votes.filter(x => x.refuted).length < 2)
log(`${confirmedNew.length} of ${fresh.length} new findings survive verification`)

phase('Fix')
let fix = null
if (open.length || confirmedNew.length) {
  fix = await agent(`${CTX}

Apply these confirmed items, and nothing else.

A. Earlier findings still open, or whose fix introduced a problem (from verifiers): ${JSON.stringify(open)}

B. New findings that survived two independent refutation attempts (each with the verifiers' reasons - where a verifier said the problem is real but the proposed fix is wrong, follow the verifier's fix): ${JSON.stringify(confirmedNew.map(v => ({ ...v.f, verifier_reasons: v.votes.map(x => x.reason) })))}

For each: re-check it against the files, then fix it, keeping encodings (the loc file UTF-8 with BOM and LF; the override focus file CRLF; new script files LF, no BOM), the house loc rules and CLAUDE.md's conventions. If a change alters something CLAUDE.md, README.md or CONQUEST_PLAN.txt describes, update them in the same pass; keep the plan, the code and the AI in step (CLAUDE.md > Project). Items that are the user's design decision (e.g. whether AI-only holds are acceptable, balance numbers, filling the idle focus slot) must NOT be changed - list them as rejected with 'user decision'. Afterwards run from the repo root: python build_telemetry.py, python check_plan_sync.py (must print OK), python ai_run_report.py --selftest, python story_rework/tools/grid.py (fix its paths if needed; must report no overlaps and exactly 39 story focuses pulled in), and a brace-balance check over every .txt under mod_folder. Report each item applied or rejected with the reason.`, { label: 'fix', phase: 'Fix', schema: FIX_SCHEMA })
}

return { confirms, fresh, verified, fix }
