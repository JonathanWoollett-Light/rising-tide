"""(c) brace balance of the touched files, (d) loc keys referenced by the story acts, events, ideas and triggers are
defined, and nested $key$ in new or replaced values resolve one level to plain text, (e) events fired by the act files
exist and none is defined twice."""
import glob
import json
import os
import re
from collections import Counter

REPO = r'C:\Users\jonat\Documents\rising-tide'
MOD = os.path.join(REPO, 'mod_folder')
OWB = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196'
VAN = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
HERE = os.path.dirname(os.path.abspath(__file__))
NF = os.path.join(MOD, 'common', 'national_focus')
ACTS = [os.path.join(NF, f) for f in ('mltd_act2_focus.txt', 'mltd_act3_focus.txt', 'mltd_act4_focus.txt',
                                      'mltd_act5_focus.txt', 'mltd_act6_focus.txt', 'mltd_finale_focus.txt')]
OVERRIDE = os.path.join(NF, 'Mirelurk Tribe (MLT) Focus.txt')
EVENTS = os.path.join(MOD, 'events', 'mltd_events.txt')
IDEAS = os.path.join(MOD, 'common', 'ideas', 'mltd_ideas.txt')
TRIG = os.path.join(MOD, 'common', 'scripted_triggers', 'mltd_scripted_triggers.txt')
EFF = os.path.join(MOD, 'common', 'scripted_effects', 'mltd_scripted_effects.txt')
ONA = os.path.join(MOD, 'common', 'on_actions', 'mltd_on_actions.txt')
LOC = os.path.join(MOD, 'localisation', 'english', 'MLT', 'mltd_l_english.yml')
TOUCHED = ACTS + [OVERRIDE, EVENTS, IDEAS, TRIG, EFF, ONA,
                  os.path.join(MOD, 'common', 'dynamic_modifiers', 'mltd_dynamic_modifiers.txt'),
                  os.path.join(MOD, 'common', 'opinion_modifiers', 'mltd_opinion_modifiers.txt'),
                  os.path.join(MOD, 'common', 'scripted_effects', 'mltd_telemetry_effects.txt')]


def rd(p):
    return open(p, 'rb').read().decode('utf-8-sig', 'replace')


def strip(t):
    t = re.sub(r'"[^"\n]*"', '""', t)
    return re.sub(r'#[^\n]*', '', t)


problems = []
print('(c) braces')
for p in TOUCHED:
    raw = open(p, 'rb').read()
    t = strip(raw.decode('utf-8-sig'))
    depth, low, line = 0, 0, None
    for i, ch in enumerate(t):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < low:
                low = depth
                line = t.count('\n', 0, i) + 1
    enc = '%s %s' % ('BOM' if raw[:3] == b'\xef\xbb\xbf' else 'noBOM',
                     'CRLF' if b'\r\n' in raw else 'LF')
    ok = depth == 0 and low == 0
    print('  %-40s open=%d close=%d end=%d min=%d %s %s' % (os.path.basename(p), t.count('{'), t.count('}'), depth, low,
                                                          enc, 'OK' if ok else 'BAD at %s' % line))
    if not ok:
        problems.append('braces ' + p)
    if b'\r' in raw and b'\r\n' not in raw:
        problems.append('stray CR ' + p)
    if b'\r\n' in raw and raw.count(b'\n') != raw.count(b'\r\n'):
        problems.append('mixed line endings ' + p)


# ---------------------------------------------------------------- loc
KEY = re.compile(r'^\s*([^\s:#"]+):\d*\s*"(.*)"\s*$')


def load(paths):
    out = {}
    for p in paths:
        try:
            lines = rd(p).split('\n')
        except OSError:
            continue
        for l in lines:
            m = KEY.match(l)
            if m:
                out[m.group(1)] = m.group(2)
    return out


ours = load([LOC])
our_replace = load(glob.glob(os.path.join(MOD, 'localisation', 'replace', '**', '*.yml'), recursive=True))
owb_all = glob.glob(os.path.join(OWB, 'localisation', '**', '*.yml'), recursive=True)
owb_replace = load([p for p in owb_all if os.sep + 'replace' + os.sep in p])
owb = load([p for p in owb_all if os.sep + 'replace' + os.sep not in p and 'english' in p.lower()])
van = load(glob.glob(os.path.join(VAN, 'localisation', 'english', '**', '*.yml'), recursive=True))
defined = {}
for src, d in (('vanilla', van), ('owb', owb), ('owb-replace', owb_replace), ('our-replace', our_replace), ('ours', ours)):
    for k, v in d.items():
        defined[k] = (src, v)

# duplicate keys in our file
keys_in_file = re.findall(r'(?m)^\s+([^\s:#"]+):\d*\s*"', rd(LOC))
dup = [k for k, c in Counter(keys_in_file).items() if c > 1]
print('\n(d) loc: our file has %d keys, duplicates: %s' % (len(keys_in_file), dup))
if dup:
    problems.append('duplicate loc keys %s' % dup)
raw = open(LOC, 'rb').read()
print('  BOM', raw[:3] == b'\xef\xbb\xbf', 'CR', raw.count(b'\r'), 'first line', raw[3:].split(b'\n')[0])
bad_lines = [l for l in rd(LOC).split('\n')[1:] if l.strip() and not l.strip().startswith('#') and not KEY.match(l)]
print('  malformed lines:', bad_lines[:5])

refs = {}  # key -> where


def ref(k, where):
    refs.setdefault(k, set()).add(where)


def nocomment(t):
    return re.sub(r'#[^\n]*', '', t)


def blocks(text):
    out = []
    tok = re.compile(r'([A-Za-z0-9_.]+)\s*=\s*\{|\{|\}')
    depth, cur = 0, None
    for m in tok.finditer(text):
        s = m.group(0)
        if s == '}':
            depth -= 1
            if depth == 0 and cur:
                out.append((cur[0], text[cur[1]:m.start()]))
                cur = None
        else:
            if depth == 0 and m.group(1):
                cur = (m.group(1), m.end())
            depth += 1
    return out


TT = [r'\bcustom_effect_tooltip\s*=\s*([A-Za-z0-9_.]+)', r'\btooltip\s*=\s*([A-Za-z0-9_.]+)',
      r'\btitle\s*=\s*([A-Za-z0-9_.]+)', r'\bdesc\s*=\s*([A-Za-z0-9_.]+)', r'\bname\s*=\s*([A-Za-z0-9_.]+)',
      r'\btext\s*=\s*([A-Za-z0-9_.]+)', r'\blocalization_key\s*=\s*([A-Za-z0-9_.]+)']
story_ids = []
for p in ACTS:
    t = nocomment(rd(p))
    for k, b in blocks(t):
        if k == 'shared_focus':
            fid = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', b).group(1)
            story_ids.append(fid)
            ref(fid, os.path.basename(p))
            ref(fid + '_desc', os.path.basename(p))
    for pat in TT:
        for m in re.finditer(pat, t):
            v = m.group(1)
            if v in ('yes', 'no') or re.match(r'^-?[\d.]+$', v):
                continue
            ref(v, os.path.basename(p))
    for m in re.finditer(r'\b(?:add_ideas|idea)\s*=\s*([A-Za-z0-9_]+)', t):
        ref(m.group(1), os.path.basename(p))
# the override's own mltd_ focuses and its tooltips
t = nocomment(rd(OVERRIDE))
for k, b in blocks([bb for kk, bb in blocks(t) if kk == 'focus_tree'][0]):
    if k == 'focus':
        fid = re.search(r'\bid\s*=\s*([A-Za-z0-9_]+)', b).group(1)
        if fid.startswith('mltd_'):
            ref(fid, 'override')
            ref(fid + '_desc', 'override')
            for pat in TT[:2]:
                for m in re.finditer(pat, b):
                    ref(m.group(1), 'override')
# events: every event's title/desc/option names
t = nocomment(rd(EVENTS))
for k, b in blocks(t):
    if k in ('country_event', 'news_event'):
        for pat in (r'\btitle\s*=\s*([A-Za-z0-9_.]+)', r'\bdesc\s*=\s*([A-Za-z0-9_.]+)', r'\bname\s*=\s*([A-Za-z0-9_.]+)',
                    r'\bcustom_effect_tooltip\s*=\s*([A-Za-z0-9_.]+)', r'\btooltip\s*=\s*([A-Za-z0-9_.]+)'):
            for m in re.finditer(pat, b):
                ref(m.group(1), 'mltd_events.txt')
# ideas: names and descs of the country ideas
t = nocomment(rd(IDEAS))
for k, b in blocks(t):
    for k2, b2 in blocks(b):
        if k2 == 'country':
            for k3, b3 in blocks(b2):
                ref(k3, 'mltd_ideas.txt')
                ref(k3 + '_desc', 'mltd_ideas.txt')
                for m in re.finditer(r'\bcustom_modifier_tooltip\s*=\s*([A-Za-z0-9_.]+)', b3):
                    ref(m.group(1), 'mltd_ideas.txt')
# triggers: tooltips
for p in (TRIG, EFF, ONA):
    t = nocomment(rd(p))
    for pat in TT[:2]:
        for m in re.finditer(pat, t):
            ref(m.group(1), os.path.basename(p))

missing = {k: sorted(w) for k, w in refs.items() if k not in defined}
# name = X in the act files also names tech bonuses/operatives/factions; report them separately
print('  referenced keys: %d, missing: %d' % (len(refs), len(missing)))
for k, w in sorted(missing.items()):
    print('   MISSING', k, w)
from_owb = sorted(k for k in refs if k in defined and defined[k][0] != 'ours')
print('  resolved outside our file:', from_owb)

# nested $key$ in new or replaced values
merge = json.load(open(os.path.join(HERE, 'loc_merge.json')))
changed = [k for a, k in merge['replaced']] + [k for a, k in merge['new']]
print('  new or replaced values checked for $key$:', len(changed))
nest_bad = []
for k in changed:
    v = ours.get(k)
    if v is None:
        nest_bad.append((k, 'value gone'))
        continue
    for n in re.findall(r'\$([A-Za-z0-9_.]+)(?:\|[^$]*)?\$', v):
        if n in ours:
            src, nv = 'ours', ours[n]
        elif n in owb:
            src, nv = 'owb', owb[n]
        elif n in van:
            src, nv = 'vanilla', van[n]
        elif n in owb_replace or n in our_replace:
            nest_bad.append((k, n, 'only in a replace/ file'))
            continue
        else:
            nest_bad.append((k, n, 'undefined'))
            continue
        if '$' in nv:
            nest_bad.append((k, n, 'nested value is not plain text: ' + nv[:60]))
print('  nested $key$ problems:', nest_bad or 'none')
if missing:
    problems.append('missing loc keys %s' % sorted(missing))
if nest_bad:
    problems.append('nesting %s' % nest_bad)

# ---------------------------------------------------------------- events
t = nocomment(rd(EVENTS))
ev_ids = re.findall(r'(?m)^\s*id\s*=\s*(mltd\.\d+)\s*$', t)
dups = [e for e, c in Counter(ev_ids).items() if c > 1]
fired = {}
for p in ACTS + [OVERRIDE, EVENTS, ONA]:
    s = nocomment(rd(p))
    for m in re.finditer(r'\b(country_event|news_event)\s*=\s*\{\s*id\s*=\s*(mltd\.\d+)', s):
        fired.setdefault(m.group(2), set()).add((m.group(1), os.path.basename(p)))
    for m in re.finditer(r'\b(country_event|news_event)\s*=\s*(mltd\.\d+)\b', s):
        fired.setdefault(m.group(2), set()).add((m.group(1), os.path.basename(p)))
# kind check: a news_event fired must be defined as news_event
kinds = {}
for k, b in blocks(t):
    if k in ('country_event', 'news_event'):
        m = re.search(r'\bid\s*=\s*(mltd\.\d+)', b)
        kinds[m.group(1)] = k
print('\n(e) events: %d defined, duplicates: %s' % (len(ev_ids), dups or 'none'))
act_fired = {e: w for e, w in fired.items() if any(f in [os.path.basename(a) for a in ACTS] for _, f in w)}
print('  fired by the act files:', sorted(act_fired, key=lambda e: int(e.split('.')[1])))
for e, w in sorted(fired.items()):
    if e not in kinds:
        print('   NOT DEFINED', e, w)
        problems.append('event not defined ' + e)
    else:
        for kind, f in w:
            if kind != kinds[e]:
                print('   KIND MISMATCH', e, kind, 'fired from', f, 'defined as', kinds[e])
                problems.append('event kind ' + e)
story_ev = ['mltd.%d' % n for n in (30, 31, 40, 41, 50, 51, 52, 60, 61, 62, 70, 71, 72, 73, 74)]
print('  story events never fired:', [e for e in story_ev if e not in fired])
if dups:
    problems.append('duplicate events %s' % dups)
print('\nPROBLEMS:', problems or 'none')
