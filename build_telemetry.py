"""Generate mod_folder/common/scripted_effects/mltd_telemetry_effects.txt - Rising Tide's MLT AI telemetry.

The hand-written part of the file is TEMPLATE below (written with 4-space indentation, converted to tabs here). The long,
regular blocks are generated from the mod, OWB and the plan, so every id in them is checked to exist:
  @START@      START: one log line per (ai, lar, caps_rule, schism) case
  @LAW@        LAW: the tribal conscription laws (OWB gov_manpower.txt, # TRIBAL CONSCRIPTION)
  @FOCUS@      FOCUS: every focus MLT can take (mlt_nf's own, plus the shared focuses its roots pull in)
  @TECH@       TECH: the plan's research, the AI's research_tech, OWB's mirelurk line, our two reward techs
  @GONE@       GONE: every country MLT's AI conquers (conquer > 0), with its capital as the last poll saw it
  @STAGE@      STAGE: each conquest stage (mltd_ai_stage_<tag>, common/scripted_triggers/mltd_ai_triggers.txt) first seen open
  @ADVISOR@    ADVISOR: each of MLT's advisors (common/characters/MLT.txt) first seen hired
  @DECISIONS@  DECISION: every mltd_ decision that sets a timed *_cooldown flag
  @GIFTS@      GIFT: every mltd_ decision that activates a mission
  @MARKET@     MARKET
  @SNAP@       SNAP: the four line variants (cult target or none, caps rule on or off)
Output: UTF-8 without BOM, LF, tab indentation.
Usage: python build_telemetry.py [--dry]   (--dry: print the lists, write nothing)
"""
import glob
import os
import re
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(REPO, 'mod_folder')
OWB = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196'
PLAN = os.path.join(REPO, 'CONQUEST_PLAN.txt')
OUT = os.path.join(MOD, 'common', 'scripted_effects', 'mltd_telemetry_effects.txt')


def rd(p):
    return open(p, 'rb').read().decode('utf-8-sig', errors='replace')


def nocomment(s):
    out = []
    for line in s.split('\n'):
        q = False
        for i, ch in enumerate(line):
            if ch == '"':
                q = not q
            elif ch == '#' and not q:
                line = line[:i]
                break
        out.append(line)
    return '\n'.join(out)


WARNINGS = []


def blocks(text, depth, name=''):
    """(key, body) of every `key = {` block opening at the given brace depth, comments removed. A closing brace with
    nothing open is skipped with a warning, as the game's parser carries on past one."""
    clean = nocomment(text)
    masked = re.sub(r'"[^"\n]*"', lambda m: '"' + '_' * (len(m.group(0)) - 2) + '"', clean)
    level, cur, out = 0, None, []
    for m in re.finditer(r'([A-Za-z0-9_.@:\-]+)\s*=\s*\{|\{|\}', masked):
        if m.group(0) == '}':
            if level == 0:
                WARNINGS.append('extra closing brace in %s at line %d' % (name, clean.count('\n', 0, m.start()) + 1))
                continue
            level -= 1
            if level == depth and cur:
                out.append((cur[0], clean[cur[1]:m.start()]))
                cur = None
        else:
            if level == depth:
                cur = (m.group(1), m.end())
            level += 1
    if level:
        WARNINGS.append('%d unclosed brace(s) in %s' % (level, name))
    return out


def flat(body):
    """A block's own text, nested blocks removed."""
    prev = None
    while prev != body:
        prev = body
        body = re.sub(r'\{[^{}]*\}', ' ', body)
    return body


def own_id(body):
    return re.search(r'(?:^|\s)id\s*=\s*([A-Za-z0-9_]+)', flat(body)).group(1)


def strategies(path):
    for block in re.findall(r'\bai_strategy\s*=\s*\{([^{}]*)\}', nocomment(rd(path))):
        yield dict(re.findall(r'(\w+)\s*=\s*"?([^\s{}"]+)"?', block))


def dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ------------------------------------------------------------------ focuses
tree_path = os.path.join(MOD, 'common', 'national_focus', 'Mirelurk Tribe (MLT) Focus.txt')
tree_body = [b for k, b in blocks(rd(tree_path), 0) if k == 'focus_tree'][0]
assert own_id(tree_body) == 'mlt_nf'
national = [own_id(b) for k, b in blocks(tree_body, 0) if k == 'focus']
roots = re.findall(r'(?m)^\s*shared_focus\s*=\s*([A-Za-z0-9_]+)', flat(tree_body))

nf_files = {}
for root in (OWB, MOD):  # OWB replace_paths common/national_focus, so vanilla's are not loaded
    for p in glob.glob(os.path.join(root, 'common', 'national_focus', '*.txt')):
        nf_files[os.path.basename(p).lower()] = p
shared = {}  # id -> (prerequisites, file name, position)
for p in sorted(nf_files.values()):
    for pos, (k, b) in enumerate(blocks(rd(p), 0, os.path.basename(p))):
        if k == 'shared_focus':
            pre = set()
            for pk, pb in blocks(b, 0):
                if pk == 'prerequisite':
                    pre |= set(re.findall(r'\bfocus\s*=\s*([A-Za-z0-9_]+)', pb))
            fid = own_id(b)
            assert fid not in shared, 'duplicate shared focus ' + fid
            shared[fid] = (pre, os.path.basename(p), pos)
for r in roots:
    assert r in shared, 'root not defined: ' + r
pulled = set(roots)
changed = True
while changed:  # a shared focus comes in when one of its prerequisites is a pulled shared focus
    changed = False
    for fid, (pre, fn, pos) in shared.items():
        if fid not in pulled and pre & pulled:
            pulled.add(fid)
            changed = True
groups = {}
for fid in pulled:
    groups.setdefault(shared[fid][1], []).append(fid)
for fn in groups:
    groups[fn].sort(key=lambda f: shared[f][2])
assert set(groups) == {'Shared Oregon Coastals Focus.txt', 'mltd_conflicts_focus.txt'}, groups.keys()
oregon = groups['Shared Oregon Coastals Focus.txt']
conflicts = groups['mltd_conflicts_focus.txt']
all_focuses = national + oregon + conflicts
assert len(set(all_focuses)) == len(all_focuses)

# ------------------------------------------------------------------ techs
tech_defined = set()
for root in (OWB, MOD):
    for p in glob.glob(os.path.join(root, 'common', 'technologies', '*.txt')):
        for k, b in blocks(rd(p), 0):
            if k == 'technologies':
                tech_defined |= {kk for kk, bb in blocks(b, 0)}
plan_techs = re.findall(r'(?m)^research slot \d+ ([A-Za-z0-9_]+)', rd(PLAN))
ai_techs = []
for p in sorted(glob.glob(os.path.join(MOD, 'common', 'ai_strategy', 'mltd_*.txt'))
                + sorted(glob.glob(os.path.join(MOD, 'common', 'ai_strategy_plans', 'mltd_*.txt')))):
    ai_techs += [s['id'] for s in strategies(p) if s.get('type') == 'research_tech' and 'id' in s]
creatures = [k for k, b in blocks(rd(os.path.join(OWB, 'common', 'technologies', 'tech_creatures.txt')), 1)
             if k.startswith('amphibious_beast_')]
techs = dedup(plan_techs + ai_techs + creatures + ['warbike_unlock_tech', 'mltd_star_spawn_tech'])
for t in techs:
    assert t in tech_defined, 'tech not defined: ' + t

# ------------------------------------------------------------------ laws
gm = rd(os.path.join(OWB, 'common', 'ideas', 'gov_manpower.txt'))
seg = gm[gm.index('# TRIBAL CONSCRIPTION'):gm.index('# LEGION CONSCRIPTION')]
laws = re.findall(r'(?m)^\t\t([a-z_0-9]+) = \{', seg)
assert laws == ['born_warriors', 'veteran_pathfinders', 'able_bodied_tribesmen', 'first_sons_and_daughters',
                'children_and_mothers'], laws

# ------------------------------------------------------------------ decisions, gifts, market
decisions, gifts, missions = [], [], {}
for cat, cb in blocks(rd(os.path.join(MOD, 'common', 'decisions', 'mltd_decisions.txt')), 0):
    for did, db in blocks(cb, 0):
        m = re.search(r'set_country_flag\s*=\s*\{\s*flag\s*=\s*([A-Za-z0-9_]+_cooldown)\s+value\s*=\s*1\s+days\s*=\s*(\d+)\s*\}', db)
        if m:
            decisions.append((did, m.group(1), int(m.group(2))))
        m = re.search(r'\bactivate_mission\s*=\s*([A-Za-z0-9_]+)', db)
        if m:
            gifts.append((did, m.group(1)))
        m = re.search(r'\bdays_mission_timeout\s*=\s*(\d+)', db)
        if m:
            missions[did] = int(m.group(1))
for did, mission in gifts:
    assert mission in missions, 'mission not defined: ' + mission
se = rd(os.path.join(MOD, 'common', 'scripted_effects', 'mltd_scripted_effects.txt'))
market_days = set(int(x) for x in re.findall(r'flag = mltd_wet_market_recent_trade value = 1 days = (\d+)', se))
assert len(market_days) == 1, market_days
market_days = market_days.pop()

# ------------------------------------------------------------------ tracked countries
tags = []
for p in sorted(glob.glob(os.path.join(MOD, 'common', 'ai_strategy', 'mltd_*.txt'))):
    for s in strategies(p):
        if s.get('type') == 'conquer' and float(s.get('value', 0)) > 0 and s['id'] not in tags:
            tags.append(s['id'])
states = set()
for p in glob.glob(os.path.join(OWB, 'history', 'states', '*.txt')):
    m = re.match(r'\d+', os.path.basename(p))
    if m:
        states.add(int(m.group()))
tag_caps = []
for tag in tags:
    paths = glob.glob(os.path.join(MOD, 'history', 'countries', tag + ' - *.txt')) or \
        glob.glob(os.path.join(OWB, 'history', 'countries', tag + ' - *.txt'))
    assert len(paths) == 1, (tag, paths)
    cap = int(re.search(r'(?m)^\s*capital\s*=\s*(\d+)', nocomment(rd(paths[0]))).group(1))
    assert cap in states, (tag, cap)
    tag_caps.append((tag, cap))

# ------------------------------------------------------------------ stages and advisors
ai_triggers = rd(os.path.join(MOD, 'common', 'scripted_triggers', 'mltd_ai_triggers.txt'))
stages = [k[len('mltd_ai_stage_'):] for k, b in blocks(ai_triggers, 0) if k.startswith('mltd_ai_stage_')]
assert stages and len(stages) == len(set(stages)), stages
for k in ('mltd_ai_north_done', 'mltd_ai_north_state'):
    assert re.search(r'(?m)^' + k + r' = [{]', ai_triggers), k
survey = rd(os.path.join(MOD, 'common', 'scripted_effects', 'mltd_ai_survey_effects.txt'))
for k in ('set_country_flag = mltd_ai_north_done', 'set_country_flag = mltd_ai_pocket', 'mltd_ai_border_states',
          'mltd_ai_army_target', 'mltd_ai_north_owned'):
    assert k in survey, k
chars = rd(os.path.join(MOD, 'common', 'characters', 'MLT.txt'))
advisors = []
for k, b in blocks(chars, 0):
    if k == 'characters':
        for ck, cb in blocks(b, 0):
            if any(rk == 'advisor' for rk, rb in blocks(cb, 0)):
                advisors.append(ck)
assert 'MLT_OLD_CASTRO' in advisors, advisors

# ------------------------------------------------------------------ other ids the template names
ideas = rd(os.path.join(MOD, 'common', 'ideas', 'mltd_ideas.txt'))
for idea in ('mltd_the_grand_ritual', 'mltd_the_final_ritual'):
    assert re.search(r'(?m)^\t\t' + idea + r' = \{', ideas), idea
    assert idea in national, idea  # the ritual focuses share the ideas' names
gro = rd(os.path.join(OWB, 'common', 'on_actions', '__game_rule_on_actions.txt'))
assert 'set_global_flag = caps_enabled_global_flag' in gro and 'set_country_flag = DIS_mend_schism' in gro
assert 'caps_number_display' in rd(os.path.join(OWB, 'common', 'scripted_effects', 'caps_scripted_effects.txt'))
assert 'mltd_ai_cult_target' in rd(os.path.join(MOD, 'common', 'on_actions', 'mltd_on_actions.txt'))
assert 'add_to_variable = { mltd_books_read = 1 }' in rd(os.path.join(MOD, 'events', 'mltd_events.txt'))
assert 'mltd_cult_strength' in se
eq_defined = set()
for root in (OWB, MOD):
    for p in glob.glob(os.path.join(root, 'common', 'units', 'equipment', '*.txt')):
        for k, b in blocks(rd(p), 0):
            if k == 'equipments':
                eq_defined |= {kk for kk, bb in blocks(b, 0) if re.search(r'\bis_archetype\s*=\s*yes', flat(bb))}
for eq in ('amphibious_beast_equipment', 'infantry_equipment', 'support_equipment', 'mltd_deep_ones_equipment',
           'mltd_star_spawn_equipment'):
    assert eq in eq_defined, 'archetype not defined: ' + eq


# ------------------------------------------------------------------ generated blocks
def day(root=False):
    return '[?ROOT.mltd_tm_day|0]' if root else '[?mltd_tm_day|0]'


def gen_start():
    out = []

    def w(n, s):
        out.append('\t' * n + s)

    def line(ai, lar, caps, schism):
        return ('log = "MLTD %s START ai=%s lar=%s caps_rule=%s schism=%s v=1 date=[GetDateText]"'
                % (day(), ai, lar, caps, schism))

    for ai_lim, ai in (('is_ai = yes', 'yes'), (None, 'no')):
        w(1, 'if = {') if ai_lim else w(1, 'else = {')
        if ai_lim:
            w(2, 'limit = { %s }' % ai_lim)
        for lar_lim, lar in (('has_dlc = "La Resistance"', 'yes'), (None, 'no')):
            w(2, 'if = {') if lar_lim else w(2, 'else = {')
            if lar_lim:
                w(3, 'limit = { %s }' % lar_lim)
            for caps_lim, caps in (('has_global_flag = caps_enabled_global_flag', 'yes'), (None, 'no')):
                w(3, 'if = {') if caps_lim else w(3, 'else = {')
                if caps_lim:
                    w(4, 'limit = { %s }' % caps_lim)
                w(4, 'if = {')
                w(5, 'limit = { NOT = { country_exists = DIS } }')
                w(5, line(ai, lar, caps, 'na'))
                w(4, '}')
                w(4, 'else_if = {')
                w(5, 'limit = { DIS = { has_country_flag = DIS_mend_schism } }')
                w(5, line(ai, lar, caps, 'yes'))
                w(4, '}')
                w(4, 'else = {')
                w(5, line(ai, lar, caps, 'no'))
                w(4, '}')
                w(3, '}')
            w(2, '}')
        w(1, '}')
    return out


def gen_law():
    out = []
    for k, law in enumerate(laws, 1):
        out += ['\tif = {',
                '\t\tlimit = {',
                '\t\t\thas_idea = %s' % law,
                '\t\t\tNOT = { check_variable = { mltd_tm_law = %d } }' % k,
                '\t\t}',
                '\t\tset_variable = { mltd_tm_law = %d }' % k,
                '\t\tlog = "MLTD %s LAW id=%s"' % (day(), law),
                '\t}']
    other = len(laws) + 1
    out += ['\tif = {',
            '\t\tlimit = {',
            '\t\t\tNOT = {'] + ['\t\t\t\thas_idea = %s' % law for law in laws] + [
            '\t\t\t}',
            '\t\t\tNOT = { check_variable = { mltd_tm_law = %d } }' % other,
            '\t\t}',
            '\t\tset_variable = { mltd_tm_law = %d }' % other,
            '\t\tlog = "MLTD %s LAW id=other"' % day(),
            '\t}']
    return out


def once(flag, trigger, text):
    return ['\tif = {',
            '\t\tlimit = { NOT = { has_country_flag = %s } %s }' % (flag, trigger),
            '\t\tset_country_flag = %s' % flag,
            '\t\tlog = "%s"' % text,
            '\t}']


def gen_focus():
    out = []
    for title, ids in (('mlt_nf: OWB\'s national focuses, then ours', national),
                       ('OWB\'s Shared Oregon Coastals Focus.txt, pulled in by ' + ' and '.join(
                           r for r in roots if r in oregon), oregon),
                       ('the conflict sub-trees, common/national_focus/mltd_conflicts_focus.txt', conflicts)):
        out.append('\t# %s (%d)' % (title, len(ids)))
        for fid in ids:
            out += once('mltd_tm_f_' + fid, 'has_completed_focus = ' + fid, 'MLTD %s FOCUS id=%s' % (day(), fid))
    return out


def gen_tech():
    out = []
    for t in techs:
        out += once('mltd_tm_t_' + t, 'has_tech = ' + t, 'MLTD %s TECH id=%s' % (day(), t))
    return out


def gen_gone():
    out = []
    for tag, cap in tag_caps:
        flag, var = 'mltd_tm_alive_' + tag, 'mltd_tm_cap_' + tag
        text = 'MLTD %s GONE tag=%s capital=[?ROOT.%s.GetID] owner=' % (day(True), tag, var)
        out += ['\t# %s (capital %d at the start)' % (tag, cap),
                '\tif = {',
                '\t\tlimit = { country_exists = %s }' % tag,
                '\t\tset_country_flag = %s' % flag,
                '\t\t%s = { capital_scope = { set_variable = { ROOT.%s = THIS } } }' % (tag, var),
                '\t}',
                '\telse_if = {',
                '\t\tlimit = { has_country_flag = %s }' % flag,
                '\t\tclr_country_flag = %s' % flag,
                '\t\tvar:%s = {' % var,
                '\t\t\tif = {',
                '\t\t\t\tlimit = { NOT = { any_country = { owns_state = PREV } } }',
                '\t\t\t\tlog = "%snone"' % text,
                '\t\t\t}',
                '\t\t\telse = {',
                '\t\t\t\tOWNER = { log = "%s[THIS.GetTag]" }' % text,
                '\t\t\t}',
                '\t\t}',
                '\t}']
    return out


def gen_stage():
    out = []
    for s in stages:
        out += once('mltd_tm_s_' + s, 'mltd_ai_stage_%s = yes' % s, 'MLTD %s STAGE id=%s' % (day(), s))
    out += once('mltd_tm_s_north', 'has_country_flag = mltd_ai_north_done', 'MLTD %s STAGE id=north' % day())
    return out


def gen_advisor():
    out = []
    for c in advisors:
        out += once('mltd_tm_a_' + c.lower(), '%s = { is_hired_as_advisor = yes }' % c,
                    'MLTD %s ADVISOR id=%s' % (day(), c))
    return out


def with_caps(n, text):
    """The log line twice: with caps= while OWB's caps rule is on, without it while it is off."""
    t = '\t' * n
    return [t + 'if = {',
            t + '\tlimit = { has_global_flag = caps_enabled_global_flag }',
            t + '\tlog = "%s caps=[?mltd_tm_caps|0]"' % text,
            t + '}',
            t + 'else = {',
            t + '\tlog = "%s"' % text,
            t + '}']


def gen_decisions():
    out = []
    for did, flag, days in decisions:
        marker = 'mltd_tm_d_' + did[len('mltd_'):]
        out += ['\t# %s: %s, %d days' % (did, flag, days),
                '\tif = {',
                '\t\tlimit = {',
                '\t\t\thas_country_flag = %s' % flag,
                '\t\t\tOR = {',
                '\t\t\t\tNOT = { has_country_flag = %s }' % marker,
                '\t\t\t\thas_country_flag = { flag = %s days < 7 }' % flag,
                '\t\t\t}',
                '\t\t}',
                '\t\tset_country_flag = { flag = %s value = 1 days = %d }' % (marker, days),
                '\t\tmltd_tm_update_economy = yes']
        out += with_caps(2, 'MLTD %s DECISION id=%s pop_k=[?mltd_tm_pop_k|0] mp_k=[?mltd_tm_mp_k|0]' % (day(), did))
        out.append('\t}')
    return out


def gen_gifts():
    out = []
    for did, mission in gifts:
        marker = 'mltd_tm_g_' + did[len('mltd_'):]
        out += ['\t# %s: %s, %d days' % (did, mission, missions[mission]),
                '\tif = {',
                '\t\tlimit = {',
                '\t\t\thas_active_mission = %s' % mission,
                '\t\t\tNOT = { has_country_flag = %s }' % marker,
                '\t\t}',
                '\t\tset_country_flag = { flag = %s value = 1 days = %d }' % (marker, missions[mission]),
                '\t\tlog = "MLTD %s GIFT id=%s"' % (day(), did),
                '\t}']
    return out


def gen_market():
    flag = 'mltd_wet_market_recent_trade'
    out = ['\tif = {',
           '\t\tlimit = {',
           '\t\t\thas_country_flag = %s' % flag,
           '\t\t\tOR = {',
           '\t\t\t\tNOT = { has_country_flag = mltd_tm_market }',
           '\t\t\t\thas_country_flag = { flag = %s days < 7 }' % flag,
           '\t\t\t}',
           '\t\t}',
           '\t\tset_country_flag = { flag = mltd_tm_market value = 1 days = %d }' % market_days,
           '\t\tmltd_tm_update_economy = yes']
    out += with_caps(2, 'MLTD %s MARKET' % day())
    out.append('\t}')
    return out


SNAP_KEYS = ['owned', 'controlled', 'pop_k', 'mp_k', 'divs', 'mil', 'civ', 'dock', 'caps', 'pp', 'stab', 'ws', 'books',
             'cults', 'cult_pts', 'cult_target', 'subjects', 'wars', 'eq_mirelurk', 'eq_inf', 'eq_sup', 'border', 'target',
             'north', 'frontage', 'ops', 'slots']


def gen_snap():
    def line(target, caps):
        parts = []
        for k in SNAP_KEYS:
            if k == 'caps' and not caps:
                continue
            if k == 'cult_target':
                parts.append('cult_target=' + ('[?ROOT.mltd_ai_cult_target.GetTag]' if target else 'none'))
            else:
                parts.append('%s=[?mltd_tm_%s|0]' % (k, k))
        return 'log = "MLTD %s SNAP %s date=[GetDateText]"' % (day(), ' '.join(parts))

    out = []
    for target in (True, False):
        if target:
            out += ['\tif = {',
                    '\t\tlimit = {',
                    '\t\t\thas_variable = mltd_ai_cult_target',
                    '\t\t\tNOT = { check_variable = { mltd_ai_cult_target = 0 } }',
                    '\t\t}']
        else:
            out.append('\telse = {')
        out += ['\t\tif = {',
                '\t\t\tlimit = { has_global_flag = caps_enabled_global_flag }',
                '\t\t\t' + line(target, True),
                '\t\t}',
                '\t\telse = {',
                '\t\t\t' + line(target, False),
                '\t\t}',
                '\t}']
    return out


TEMPLATE = r'''# Rising Tide - MLT AI telemetry: scripted effects
#
# Writes machine-readable lines to game.log with the log effect while MLT exists, so that a spectator (observe mode) game
# can be compared with CONQUEST_PLAN.txt by the report script at the repo root. Everything runs in MLT's scope from MLT's
# own daily, weekly and monthly pulses (common/on_actions/mltd_telemetry_on_actions.txt), behind the kill switch
# mltd_telemetry_on (common/scripted_triggers/mltd_telemetry_triggers.txt), and changes nothing but its own mltd_tm_
# variables, flags and arrays: no tooltip, nothing on screen, nothing any AI or player reads. Deleting the three
# mltd_telemetry_* files removes it; whatever it left in a save is then inert.
#
# THE LINE CONTRACT - the report parses exactly this, so the two change together:
#   MLTD <day> <KIND> <key=value ...> [date=<GetDateText>]
# - <day>: the variable mltd_tm_day on MLT, +1 on every on_daily_MLT tick from 0 - whole days since 2275.1.1 in 365-day
#   years. START is written before the first tick adds its 1, so it reads 0, although that tick is probably 2275.1.2
#   (the game starts at noon on 2275.1.1, after that day's pulses).
# - <KIND>: START SNAP FOCUS TECH LAW JUSTIFY WARGOAL WAR_START WAR_END GONE RITUAL DECISION GIFT MARKET CULT ENEMY STAGE
#   POCKET ADVISOR.
# - key=value tokens: lower-case keys; values without spaces - tags, ids, whole numbers, yes/no, none. A game value is
#   copied into a mltd_tm_ variable first and printed [?x|0], with no sign, suffix or colour flag.
# - date=, last, on START and SNAP only: [GetDateText], which prints " 12:00, 1 January, 2275", leading space included.
# game.log adds its own prefix, and each log call after the first in a burst lands on the previous call's dangling
# effectbase.cpp:1799 prefix, so the report looks for "MLTD " anywhere in a line. Log text cannot branch, so a line whose
# words depend on the game (yes or no, a tag or none, caps or not) is written out once per case.
# unverified: the order of on_daily_MLT and the weekly or monthly pulse within one day - a weekly or monthly line may
# carry the previous day's number (the date in game.log's own prefix is a second clock); whether [?x|0] rounds and
# groups thousands; and that game.log gets the lines without -debug (documented for the log effect; this machine
# launches with -debug).
#
# State, all named mltd_tm_:
# - on MLT: mltd_tm_day; mltd_tm_law; the SNAP values (mltd_tm_<key>); the last capitals seen, mltd_tm_cap_<TAG>; the
#   flags mltd_tm_f_<focus>, mltd_tm_t_<tech>, mltd_tm_alive_<TAG> and mltd_tm_ritual_<grand|final>_<start|end>; the
#   timed markers mltd_tm_d_<decision>, mltd_tm_g_<gift> and mltd_tm_market; the arrays mltd_tm_watch and mltd_tm_drop;
#   the flags mltd_tm_s_<stage>, mltd_tm_a_<advisor> and mltd_tm_pocket; mltd_tm_enemy_states.
# - on other countries: mltd_tm_justify, mltd_tm_wargoal and mltd_tm_war - MLT's relation to that country, as last logged.
# The FOCUS, TECH, GONE, DECISION and GIFT lists were generated in round 20 from the focus tree, CONQUEST_PLAN.txt, MLT's
# AI files and common/decisions/mltd_decisions.txt: a focus, tech, conquest target, cooldown decision or gift added later
# needs its own block, in the same pattern. Callees come before callers (a console reload registers effects in file order).

# ---------------------------------------------------------------- values

# pop_k: national population in thousands - state_population_k summed over every owned state into a variable on MLT
# through PREV (the idiom of mltd_take_population_everywhere; OWB exodus_effects.txt:392-396). mltd_national_population
# sums raw state_population instead, which wraps negative at the 2,147,483 variable ceiling past ~2.1 million people.
mltd_tm_update_pop_k = {
    set_variable = { mltd_tm_pop_k = 0 }
    every_owned_state = {
        add_to_variable = { PREV.mltd_tm_pop_k = state_population_k }
    }
}

# pop_k, mp_k and caps, for the SNAP, RITUAL, DECISION and MARKET lines. caps_number_display is OWB's caps balance (read
# and written by add_caps, caps_scripted_effects.txt:48-60), never set while the caps rule is off; the lines leave caps
# out then.
# unverified: that manpower_k (vanilla RAJ_GOE_scripted_effects.txt:494) is the pool the top bar shows - the
# documentation calls it "total manpower of country in thousands".
mltd_tm_update_economy = {
    mltd_tm_update_pop_k = yes
    set_variable = { mltd_tm_mp_k = manpower_k }
    set_variable = { mltd_tm_caps = 0 }
    if = {
        limit = { has_variable = caps_number_display }
        set_variable = { mltd_tm_caps = caps_number_display }
    }
}

# ---------------------------------------------------------------- START and LAW

# START, once, on the first daily tick. ai: MLT is AI-controlled, as every country is in observe mode. lar: La
# Resistance. caps_rule: OWB's caps game rule, the global flag caps_enabled_global_flag set on_startup
# (__game_rule_on_actions.txt:8058). schism: DIS holds DIS_mend_schism, without which it never offers itself to MLT
# (nf_dis.4) and which OWB rolls on_startup for an AI MLT (:6505-6526, again :8448-8469); na once DIS is gone. v: the
# contract's version.
mltd_tm_log_start = {
@START@
}

# LAW: MLT's conscription law, at START and whenever it changes (mltd_tm_law holds the law logged last: 1-5 in the order
# below, 6 for other). MLT can hold only OWB's five tribal laws - gov_manpower.txt, # TRIBAL CONSCRIPTION, allowed on
# is_tribal_nation_allowed_block, and no script outside history files clears is_tribal_nation - so "other" would mean OWB
# has changed that. A country holds one law of a category, so at most one block fires.
mltd_tm_poll_law = {
@LAW@
}

# ---------------------------------------------------------------- FOCUS and TECH

# FOCUS: every focus MLT can take, in three groups - mlt_nf's own, the shared lurk_ focuses its two Oregon roots pull in
# from OWB, and the conflict sub-trees. The flag mltd_tm_f_<id> marks a focus logged.
mltd_tm_poll_focuses = {
@FOCUS@
}

# TECH: the techs CONQUEST_PLAN.txt researches, those MLT's AI forces (research_tech, common/ai_strategy/mltd_MLT.txt),
# the rest of OWB's mirelurk line and our two reward techs. amphibious_beast_unlock_tech is a start tech (MLT's
# history), so it logs at the first poll. The flag mltd_tm_t_<id> marks a tech logged.
mltd_tm_poll_techs = {
@TECH@
}

# ---------------------------------------------------------------- JUSTIFY, WARGOAL, WAR_START, WAR_END

# A flag on the other country records what was logged last: mltd_tm_justify (MLT is justifying a war goal against it),
# mltd_tm_wargoal (MLT holds one), mltd_tm_war (they are at war). The array mltd_tm_watch on MLT lists every country
# carrying one of them, because every_other_country skips a country that no longer exists (the note on
# mltd_cult_rebuild_list): the walk still reaches it, so its war ends with exists=no and its flags are cleared, and a
# country released again starts afresh. First the walk re-arms whatever has stopped and logs WAR_END; then one scan of
# every other country logs what is new. The scan's limit holds only the three relation triggers, tested through
# ROOT = { ... PREV } as OWB's operative_mission_scorer.txt:68-71 does.
# A dead country in an array is still a scope: OWB walks GLOBAL.chiconet_nations, which holds MAX, MOC and ZAP before
# they exist, with for_each_scope_loop (tlaloc_on_actions.txt:4-26), and vanilla tests exists = no inside such a loop
# (TOA_scripted_effects.txt:1050-1055).
# unverified: that a flag can be cleared on a country that no longer exists.
mltd_tm_poll_wars = {
    clear_array = mltd_tm_drop
    for_each_scope_loop = {
        array = mltd_tm_watch
        if = {
            limit = {
                has_country_flag = mltd_tm_justify
                OR = {
                    exists = no
                    NOT = { ROOT = { is_justifying_wargoal_against = PREV } }
                }
            }
            clr_country_flag = mltd_tm_justify
        }
        if = {
            limit = {
                has_country_flag = mltd_tm_wargoal
                OR = {
                    exists = no
                    NOT = { ROOT = { has_wargoal_against = PREV } }
                }
            }
            clr_country_flag = mltd_tm_wargoal
        }
        if = {
            limit = {
                has_country_flag = mltd_tm_war
                OR = {
                    exists = no
                    NOT = { has_war_with = ROOT }
                }
            }
            clr_country_flag = mltd_tm_war
            if = {
                limit = { exists = yes }
                log = "MLTD [?ROOT.mltd_tm_day|0] WAR_END tag=[THIS.GetTag] exists=yes"
            }
            else = {
                log = "MLTD [?ROOT.mltd_tm_day|0] WAR_END tag=[THIS.GetTag] exists=no"
            }
        }
        if = {
            limit = {
                NOT = {
                    has_country_flag = mltd_tm_justify
                    has_country_flag = mltd_tm_wargoal
                    has_country_flag = mltd_tm_war
                }
            }
            add_to_array = { ROOT.mltd_tm_drop = THIS }
        }
    }
    # a country left with no flag leaves the watch list - after the walk, which must not change the array it walks
    for_each_scope_loop = {
        array = mltd_tm_drop
        remove_from_array = { ROOT.mltd_tm_watch = THIS }
    }
    clear_array = mltd_tm_drop
    every_other_country = {
        limit = {
            OR = {
                has_war_with = ROOT
                ROOT = { is_justifying_wargoal_against = PREV }
                ROOT = { has_wargoal_against = PREV }
            }
        }
        if = {
            limit = {
                NOT = { has_country_flag = mltd_tm_justify }
                ROOT = { is_justifying_wargoal_against = PREV }
            }
            set_country_flag = mltd_tm_justify
            log = "MLTD [?ROOT.mltd_tm_day|0] JUSTIFY tag=[THIS.GetTag]"
        }
        if = {
            limit = {
                NOT = { has_country_flag = mltd_tm_wargoal }
                ROOT = { has_wargoal_against = PREV }
            }
            set_country_flag = mltd_tm_wargoal
            log = "MLTD [?ROOT.mltd_tm_day|0] WARGOAL tag=[THIS.GetTag]"
        }
        if = {
            limit = {
                NOT = { has_country_flag = mltd_tm_war }
                has_war_with = ROOT
            }
            set_country_flag = mltd_tm_war
            log = "MLTD [?ROOT.mltd_tm_day|0] WAR_START tag=[THIS.GetTag]"
        }
        if = {
            limit = { NOT = { is_in_array = { ROOT.mltd_tm_watch = THIS } } }
            add_to_array = { ROOT.mltd_tm_watch = THIS }
        }
    }
}

# ---------------------------------------------------------------- GONE

# GONE: every country MLT's AI sets out to conquer (a conquer strategy above 0 in common/ai_strategy/mltd_MLT.txt).
# Each poll while it exists records its capital in mltd_tm_cap_<TAG> on MLT (vanilla india_goe.txt:12455 stores a
# capital_scope the same way). The first poll that finds it gone logs that state, a week old at most, and whoever owns
# it now, or none - tested as OWB's achievements do (03_owb_achievements_impossible.txt:250-254; 313 of OWB's states
# start with no owner). The last capital, not the one OWB's history gives (each block's comment), because capitals move:
# a peace deal that takes one moves it to another state, and OWB script moves some - the Eighties' goes from 478 to 40
# when the Thunderbirds rise (eighties_scripted_effects.txt:244-253). A country is tracked only once seen alive
# (mltd_tm_alive_<TAG>), so MAX, MOC and ZAP, which exist only after Tlaloc dies, log nothing at the start, and a
# country released again is tracked again. var:<variable> = { } scopes to the state a variable holds (vanilla
# WTT_border_conflicts.txt:408), and a state variable prints through the state's functions (vanilla
# [?ITA.state_integrated.GetName], bba_decisions_l_english.yml:169).
# unverified: that GetID, the state's id (loc_objects_documentation.md, State; OWB's one use is [From.Capital.GetID],
# decisions_TLA_l_english.yml:19), prints as a number in a log line.
mltd_tm_poll_gone = {
@GONE@
}

# ---------------------------------------------------------------- STAGE, POCKET, ADVISOR

# STAGE: each conquest stage of MLT's AI (mltd_ai_stage_<id>, common/scripted_triggers/mltd_ai_triggers.txt) the first time a
# poll finds it open, and id=north the first time the weekly survey (mltd_ai_survey) finds the north consolidated. A stage
# is MLT's plan, not its war: its conquest block still needs a safe target and a justification. The flag mltd_tm_s_<id>
# marks a stage logged. For a human MLT the lines only say what an AI would have planned (and id=north never comes: the
# survey runs for an AI alone).
mltd_tm_poll_stages = {
@STAGE@
}

# POCKET: MLT's AI has found an enemy it cannot reach by land (the flag mltd_ai_pocket, set and cleared by mltd_ai_survey):
# state=start when the flag appears, state=end when it is gone.
mltd_tm_poll_pocket = {
    if = {
        limit = {
            has_country_flag = mltd_ai_pocket
            NOT = { has_country_flag = mltd_tm_pocket }
        }
        set_country_flag = mltd_tm_pocket
        log = "MLTD [?mltd_tm_day|0] POCKET state=start"
    }
    if = {
        limit = {
            NOT = { has_country_flag = mltd_ai_pocket }
            has_country_flag = mltd_tm_pocket
        }
        clr_country_flag = mltd_tm_pocket
        log = "MLTD [?mltd_tm_day|0] POCKET state=end"
    }
}

# ADVISOR: each of MLT's advisors (common/characters/MLT.txt, a character with an advisor role) the first time a poll finds
# it hired (is_hired_as_advisor, vanilla AST.txt:1813-1816). The flag mltd_tm_a_<character> marks one logged.
mltd_tm_poll_advisors = {
@ADVISOR@
}

# ---------------------------------------------------------------- RITUAL, DECISION, GIFT, MARKET

# RITUAL: start is the ritual's idea first seen - its focus holds it only while in progress (added in the focus's
# select_effect, removed on completion) - and end the focus first seen completed.
mltd_tm_poll_rituals = {
    if = {
        limit = {
            NOT = { has_country_flag = mltd_tm_ritual_grand_start }
            has_idea = mltd_the_grand_ritual
        }
        set_country_flag = mltd_tm_ritual_grand_start
        mltd_tm_update_pop_k = yes
        log = "MLTD [?mltd_tm_day|0] RITUAL id=grand state=start pop_k=[?mltd_tm_pop_k|0]"
    }
    if = {
        limit = {
            NOT = { has_country_flag = mltd_tm_ritual_grand_end }
            has_completed_focus = mltd_the_grand_ritual
        }
        set_country_flag = mltd_tm_ritual_grand_end
        mltd_tm_update_pop_k = yes
        log = "MLTD [?mltd_tm_day|0] RITUAL id=grand state=end pop_k=[?mltd_tm_pop_k|0]"
    }
    if = {
        limit = {
            NOT = { has_country_flag = mltd_tm_ritual_final_start }
            has_idea = mltd_the_final_ritual
        }
        set_country_flag = mltd_tm_ritual_final_start
        mltd_tm_update_pop_k = yes
        log = "MLTD [?mltd_tm_day|0] RITUAL id=final state=start pop_k=[?mltd_tm_pop_k|0]"
    }
    if = {
        limit = {
            NOT = { has_country_flag = mltd_tm_ritual_final_end }
            has_completed_focus = mltd_the_final_ritual
        }
        set_country_flag = mltd_tm_ritual_final_end
        mltd_tm_update_pop_k = yes
        log = "MLTD [?mltd_tm_day|0] RITUAL id=final state=end pop_k=[?mltd_tm_pop_k|0]"
    }
}

# DECISION: a summon, offering or Call was taken - the timed cooldown flag its complete_effect sets
# (common/decisions/mltd_decisions.txt) is new since the last poll. An AI can take a decision again on the day its
# cooldown ends, before a poll sees the flag gone, so a take counts when the flag was set in the last 7 days, or when no
# marker says it was logged already. The marker mltd_tm_d_<decision> lasts as long as the cooldown, so it outlives the
# flag it logged, and nothing is logged twice.
# unverified: that days counts the whole days since the flag was set (vanilla BUL_scripted_triggers.txt:142,
# has_country_flag = { flag = X days < 365 }).
mltd_tm_poll_decisions = {
@DECISIONS@
}

# GIFT: a gift's mission became active. A mission has no age to read, so the marker mltd_tm_g_<gift> lasts as long as the
# mission: it outlives the mission it logged, so nothing is logged twice, and a gift taken again in the few days before the
# marker lapses is logged at the first poll after it lapses - at most a week later than usual.
mltd_tm_poll_gifts = {
@GIFTS@
}

# MARKET: a Wet Market trade - the timed flag mltd_wet_market_recent_trade, which a purchase and a sale alike set
# (mltd_wet_market_pay / mltd_wet_market_receive), is new since the last poll; the marker works as DECISION's does. An AI
# MLT buys in on_weekly_MLT (mltd_on_actions.txt) and never sells.
mltd_tm_poll_market = {
@MARKET@
}

# ---------------------------------------------------------------- SNAP and CULT

# SNAP: every value is copied into mltd_tm_<key> on MLT, then printed whole. stability and has_war_support are 0-1 game
# values, turned into whole percentages. wars counts the countries at war with MLT (every_enemy_country): nothing counts
# wars as such. cults and cult_pts are counted by the same loop as the CULT lines, so the two agree. cult_target is the
# country an AI MLT runs its cult operations against (mltd_ai_cult_target, re-picked weekly in on_weekly_MLT; 0 when there
# is none), printed through the variable as vanilla prints [?ROOT.vaps_from.GetName] (nsb_events_l_english.yml:309). caps
# is left out while OWB's caps rule is off.
# unverified: that num_equipment@<archetype> (OWB organization_scripted_effects.txt:588) counts every variant of the
# archetype, as has_equipment does, and only the stockpile.
mltd_tm_log_snap = {
    mltd_tm_update_economy = yes
    set_variable = { mltd_tm_owned = num_owned_states }
    set_variable = { mltd_tm_controlled = num_controlled_states }
    set_variable = { mltd_tm_divs = num_divisions }
    set_variable = { mltd_tm_mil = num_of_military_factories }
    set_variable = { mltd_tm_civ = num_of_civilian_factories }
    set_variable = { mltd_tm_dock = num_of_naval_factories }
    set_variable = { mltd_tm_pp = political_power }
    set_variable = { mltd_tm_stab = stability }
    multiply_variable = { mltd_tm_stab = 100 }
    set_variable = { mltd_tm_ws = has_war_support }
    multiply_variable = { mltd_tm_ws = 100 }
    set_variable = { mltd_tm_books = 0 }
    if = {
        limit = { has_variable = mltd_books_read }
        set_variable = { mltd_tm_books = mltd_books_read }
    }
    set_variable = { mltd_tm_cults = 0 }
    set_variable = { mltd_tm_cult_pts = 0 }
    every_country = {
        limit = { has_variable = mltd_cult_strength }
        add_to_variable = { ROOT.mltd_tm_cults = 1 }
        add_to_variable = { ROOT.mltd_tm_cult_pts = mltd_cult_strength }
    }
    set_variable = { mltd_tm_subjects = num_subjects }
    set_variable = { mltd_tm_wars = 0 }
    every_enemy_country = {
        add_to_variable = { ROOT.mltd_tm_wars = 1 }
    }
    set_variable = { mltd_tm_eq_mirelurk = num_equipment@amphibious_beast_equipment }
    set_variable = { mltd_tm_eq_inf = num_equipment@infantry_equipment }
    set_variable = { mltd_tm_eq_sup = num_equipment@support_equipment }
    # the weekly survey's readings (0 for a human MLT, which never runs it), and the agency's operatives and slots
    set_variable = { mltd_tm_border = 0 }
    set_variable = { mltd_tm_target = 0 }
    set_variable = { mltd_tm_north = 0 }
    set_variable = { mltd_tm_frontage = 0 }
    if = {
        limit = { has_variable = mltd_ai_army_target }
        set_variable = { mltd_tm_frontage = mltd_ai_frontage }
        set_variable = { mltd_tm_border = mltd_ai_border_states }
        set_variable = { mltd_tm_target = mltd_ai_army_target }
        set_variable = { mltd_tm_north = mltd_ai_north_owned }
    }
    set_variable = { mltd_tm_ops = num_of_operatives }
    set_variable = { mltd_tm_slots = num_operative_slots }
@SNAP@
}

# ENEMY: one line per country at war with MLT, after SNAP: whether it has capitulated, how many states it controls
# (num_controlled_states, copied to mltd_tm_enemy_states on MLT to print it), and whether any of its land touches land MLT
# controls (reach: is_neighbor_of compares controlled territory). An enemy that has not capitulated, holds land and is out
# of reach is the pocket that kept run 2's NCR war going for two years after the NCR fell.
mltd_tm_log_enemies = {
    every_enemy_country = {
        set_variable = { ROOT.mltd_tm_enemy_states = num_controlled_states }
        if = {
            limit = { has_capitulated = yes }
            if = {
                limit = { is_neighbor_of = ROOT }
                log = "MLTD [?ROOT.mltd_tm_day|0] ENEMY tag=[THIS.GetTag] cap=yes states=[?ROOT.mltd_tm_enemy_states|0] reach=yes"
            }
            else = {
                log = "MLTD [?ROOT.mltd_tm_day|0] ENEMY tag=[THIS.GetTag] cap=yes states=[?ROOT.mltd_tm_enemy_states|0] reach=no"
            }
        }
        else = {
            if = {
                limit = { is_neighbor_of = ROOT }
                log = "MLTD [?ROOT.mltd_tm_day|0] ENEMY tag=[THIS.GetTag] cap=no states=[?ROOT.mltd_tm_enemy_states|0] reach=yes"
            }
            else = {
                log = "MLTD [?ROOT.mltd_tm_day|0] ENEMY tag=[THIS.GetTag] cap=no states=[?ROOT.mltd_tm_enemy_states|0] reach=no"
            }
        }
    }
}

# CULT: one line per country holding a cult of M'lyeh (its mltd_cult_strength, 0-100), right after SNAP.
mltd_tm_log_cults = {
    every_country = {
        limit = { has_variable = mltd_cult_strength }
        log = "MLTD [?ROOT.mltd_tm_day|0] CULT tag=[THIS.GetTag] str=[?mltd_cult_strength|0]"
    }
}

# ---------------------------------------------------------------- the three pulses

# on_daily_MLT: the clock - and, on the first tick, before it counts, START and the first LAW line.
mltd_tm_daily = {
    if = {
        limit = { mltd_telemetry_on = yes }
        if = {
            limit = {
                OR = {
                    NOT = { has_variable = mltd_tm_day }
                    check_variable = { mltd_tm_day = 0 }
                }
            }
            mltd_tm_log_start = yes
            mltd_tm_poll_law = yes
        }
        add_to_variable = { mltd_tm_day = 1 }
    }
}

# on_weekly_MLT: every poll. The wars come before GONE, so a country annexed at the peace table ends its war before it
# is gone.
mltd_tm_weekly = {
    if = {
        limit = { mltd_telemetry_on = yes }
        mltd_tm_poll_focuses = yes
        mltd_tm_poll_techs = yes
        mltd_tm_poll_law = yes
        mltd_tm_poll_wars = yes
        mltd_tm_poll_gone = yes
        mltd_tm_poll_rituals = yes
        mltd_tm_poll_decisions = yes
        mltd_tm_poll_gifts = yes
        mltd_tm_poll_market = yes
        mltd_tm_poll_stages = yes
        mltd_tm_poll_pocket = yes
        mltd_tm_poll_advisors = yes
    }
}

# on_monthly_MLT: SNAP, then the ENEMY and CULT lines.
mltd_tm_monthly = {
    if = {
        limit = { mltd_telemetry_on = yes }
        mltd_tm_log_snap = yes
        mltd_tm_log_enemies = yes
        mltd_tm_log_cults = yes
    }
}
'''


def tabs(text):
    out = []
    for line in text.split('\n'):
        m = re.match(r'^((?:    )+)', line)
        out.append('\t' * (len(m.group(1)) // 4) + line[len(m.group(1)):] if m else line)
    return '\n'.join(out)


def build():
    text = tabs(TEMPLATE)
    for name, lines in (('START', gen_start()), ('LAW', gen_law()), ('FOCUS', gen_focus()), ('TECH', gen_tech()),
                        ('GONE', gen_gone()), ('STAGE', gen_stage()), ('ADVISOR', gen_advisor()),
                        ('DECISIONS', gen_decisions()), ('GIFTS', gen_gifts()),
                        ('MARKET', gen_market()), ('SNAP', gen_snap())):
        token = '@%s@' % name
        assert text.count(token) == 1, token
        text = text.replace(token, '\n'.join(lines))
    assert '@' not in text.replace('num_equipment@', ''), 'placeholder left'
    assert '    ' not in re.sub(r'(?m)^#.*$', '', text), 'space indentation left'
    return text


if __name__ == '__main__':
    print('focuses: %d national + %d Oregon + %d conflicts = %d' % (len(national), len(oregon), len(conflicts),
                                                                      len(all_focuses)))
    print('roots:', ' '.join(roots))
    print('techs (%d): %s' % (len(techs), ' '.join(techs)))
    print('laws:', ' '.join(laws))
    print('decisions:', decisions)
    print('gifts:', [(d, m, missions[m]) for d, m in gifts])
    print('market days:', market_days)
    print('tracked (%d): %s' % (len(tag_caps), ' '.join('%s:%d' % tc for tc in tag_caps)))
    print('stages (%d): %s' % (len(stages), ' '.join(stages)))
    print('advisors (%d): %s' % (len(advisors), ' '.join(advisors)))
    for w in WARNINGS:
        print('warning:', w)
    text = build()
    if '--dry' in sys.argv:
        sys.exit(0)
    open(OUT, 'wb').write(text.encode('utf-8'))
    print('wrote %s: %d lines, %d log lines' % (OUT, text.count('\n'), len(re.findall(r'\blog = "', text))))
