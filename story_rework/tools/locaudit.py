"""Audit Rising Tide's localisation against its script.

Repo-only. Run from anywhere: python story_rework/tools/locaudit.py [--staging DIR] [--unused]

Reports, in order:
  1. keys the script references (explicitly or implicitly) that no loc file defines - ours, OWB's or vanilla's.
     These print raw in game. Keys found only in a staging loc.yml are marked "staged".
  2. nested $key$ references that do not resolve: undefined, two levels deep (the inner value holds another $key$),
     or a key defined only in a localisation/replace/ file (CLAUDE.md > Localisation: functions, not names).
  3. [Function] calls to scripted localisation that nothing defines, and [ID.GetName] / [TAG.GetName] /
     [TOKEN.GetName] targets that do not exist.
  4. malformed lines, encoding (BOM, CRLF, tabs), duplicated keys, unbalanced colour codes, $ and brackets,
     colour codes other than o/c in event .t/.d text and any colour code in event option text.
  5. with --unused: our keys that nothing references (information only).
Exit code 1 if any of 1-4 is non-empty.
"""
import glob
import os
import re
import sys
from collections import defaultdict

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MOD = os.path.join(REPO, 'mod_folder')
OWB = r'C:/Program Files (x86)/Steam/steamapps/workshop/content/394360/2265420196'
VAN = r'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV'
KEYLINE = re.compile(r'^ +([A-Za-z0-9_\.\-\']+):\d*\s*"(.*)"\s*(#.*)?$')
KEYISH = re.compile(r'^[A-Za-z][A-Za-z0-9_\.]*[_\.][A-Za-z0-9_\.]*$')

args = sys.argv[1:]
staging_dirs = []
while '--staging' in args:
    i = args.index('--staging')
    staging_dirs.append(args[i + 1])
    del args[i:i + 2]
show_unused = '--unused' in args


def norm(p):
    return p.replace('\\', '/')


def read(path):
    return open(path, encoding='utf-8-sig', errors='replace').read()


def load_loc(pattern):
    out = {}
    for f in glob.glob(pattern, recursive=True):
        for line in open(f, encoding='utf-8-sig', errors='replace'):
            m = KEYLINE.match(line.rstrip('\r\n'))
            if m:
                out[m.group(1)] = (m.group(2), norm(f))
    return out


ours = load_loc(os.path.join(MOD, 'localisation', '**', '*.yml'))
owb = load_loc(OWB + '/localisation/**/*.yml')
van = load_loc(VAN + '/localisation/english/**/*.yml')
staged = defaultdict(list)
for d in staging_dirs:
    for f in glob.glob(os.path.join(d, '**', '*.yml'), recursive=True):
        for line in open(f, encoding='utf-8-sig', errors='replace'):
            m = KEYLINE.match(line.rstrip('\r\n'))
            if m:
                staged[m.group(1)].append(norm(os.path.relpath(f, d)))
defined = set(ours) | set(owb) | set(van)

problems = defaultdict(list)


def strip_comments(t):
    return re.sub(r'#[^\n]*', '', t)


def blocks(text, keyword_re):
    """Yield (name, body) for top-level-ish blocks `name = { ... }` matched by keyword_re's group 1."""
    for m in keyword_re.finditer(text):
        start = text.find('{', m.end() - 1)
        depth, i = 0, start
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.group(1), text[start:i + 1]


def top_level_names(text):
    """Names of blocks at depth 1 (inside one wrapping block) and depth 0."""
    res = []
    depth = 0
    for m in re.finditer(r'([A-Za-z0-9_\.]+)\s*=\s*\{|\{|\}', text):
        tok = m.group(0)
        if tok == '{':
            depth += 1
        elif tok == '}':
            depth -= 1
        else:
            res.append((depth, m.group(1)))
            depth += 1
    return res


refs = defaultdict(set)   # key -> set of 'file:what'


def ref(key, where):
    refs[key].add(where)


script_files = [f for f in glob.glob(os.path.join(MOD, 'common', '**', '*.txt'), recursive=True)]
script_files += glob.glob(os.path.join(MOD, 'events', '*.txt'))
script_files += glob.glob(os.path.join(MOD, 'history', '**', '*.txt'), recursive=True)

EXPLICIT = re.compile(
    r'\b(custom_effect_tooltip|custom_trigger_tooltip|tooltip|localization_key|text|title|desc|name|'
    r'custom_cost_text|picture_text|loc|names)\s*=\s*"?([A-Za-z][A-Za-z0-9_\.]*)"?')

for f in script_files:
    rel = norm(os.path.relpath(f, MOD))
    base = os.path.basename(f)
    raw = read(f)
    t = strip_comments(raw)
    ours_file = base.startswith(('mltd', '000_mltd')) or 'Mirelurk Tribe' in base or base in ('MLT.txt', 'nf_mlt.txt') \
        or rel.startswith('common/scripted_localisation/mltd') or 'mltd' in base
    if not ours_file:
        continue
    for m in EXPLICIT.finditer(t):
        kw, key = m.group(1), m.group(2)
        if not KEYISH.match(key):
            continue
        if kw == 'name' and not (key.startswith(('mltd', 'MLT_', 'mlt_')) or '.' in key):
            continue
        if kw in ('title', 'desc') and '.' not in key and not key.startswith('mltd'):
            continue
        if kw == 'text' and rel.startswith('common/scripted_guis'):
            continue
        ref(key, f'{rel}:{kw}')
        if kw == 'custom_cost_text':
            ref(key + '_blocked', f'{rel}:custom_cost_text(_blocked)')
    # implicit keys
    if rel.startswith('common/national_focus/'):
        for m in re.finditer(r'^\s*id\s*=\s*(mltd_\w+)', t, re.M):
            ref(m.group(1), f'{rel}:focus')
            ref(m.group(1) + '_desc', f'{rel}:focus desc')
    if rel.startswith('common/ideas/'):
        hidden = set()
        for _, body in blocks(t, re.compile(r'\b(hidden_ideas)\s*=\s*\{')):
            hidden |= {n for d, n in top_level_names(body[1:-1]) if d == 0}
        for d, n in top_level_names(t):
            if d == 2 and n.startswith('mltd') and n not in hidden:
                ref(n, f'{rel}:idea')
    if rel.startswith('common/decisions/') and 'categories' not in rel:
        for d, n in top_level_names(t):
            if d == 1 and n.startswith('mltd'):
                ref(n, f'{rel}:decision')
    if rel.startswith('common/decisions/categories/'):
        for d, n in top_level_names(t):
            if d == 0 and n.startswith('mltd'):
                ref(n, f'{rel}:category')
    if rel.startswith('common/dynamic_modifiers/') or rel.startswith('common/opinion_modifiers/'):
        for d, n in top_level_names(t):
            if d == 0 and n.startswith('mltd'):
                ref(n, f'{rel}:modifier')
    if rel.startswith('common/technologies/'):
        for d, n in top_level_names(t):
            if d == 1 and n.startswith('mltd'):
                ref(n, f'{rel}:tech')
                ref(n + '_desc', f'{rel}:tech desc')
    if rel.startswith('common/units/equipment/'):
        for d, n in top_level_names(t):
            if d == 1 and n.startswith('mltd'):
                ref(n, f'{rel}:equipment')
    if rel.startswith('common/units/') and '/equipment/' not in rel and '/names' not in rel:
        for d, n in top_level_names(t):
            if d == 1 and n.startswith('mltd'):
                ref(n, f'{rel}:sub-unit')
    if rel.startswith('common/country_leader/'):
        for d, n in top_level_names(t):
            if d == 1 and n.startswith('mltd'):
                ref(n, f'{rel}:trait')

# 1. missing referenced keys
for key, where in sorted(refs.items()):
    if key in defined:
        continue
    tag = ' (staged: ' + ', '.join(staged[key]) + ')' if key in staged else ''
    problems['1 missing key'].append(f'{key}{tag}  <- {sorted(where)[0]}' + (f' (+{len(where) - 1})' if len(where) > 1 else ''))

# 2. nested references
PLACEHOLDERS = {'VAL', 'LEFT', 'RIGHT', 'VALUE', 'TARGET', 'COUNTRY', 'NAME', 'MODIFIER', 'DATE', 'TAG', 'WHO', 'NUM',
                'AMOUNT', 'DAYS', 'STATE', 'LEADER', 'IDEA', 'TECH', 'UNIT', 'EQUIPMENT', 'ICON', 'KEY'}
for k, (v, f) in ours.items():
    for n in re.findall(r'\$([A-Za-z0-9_\.\-]+)(?:\|[^$]*)?\$', v):
        if n in PLACEHOLDERS:
            continue
        if n not in defined:
            problems['2 nested'].append(f'{k}: ${n}$ undefined' + (' (staged)' if n in staged else ''))
        elif n in ours and re.search(r'\$[A-Za-z]', ours[n][0]):
            problems['2 nested'].append(f'{k}: ${n}$ is itself nested (two levels)')
        elif n not in ours and n not in van and '/replace/' in owb.get(n, ('', ''))[1]:
            if not re.fullmatch(r'\s*\$' + re.escape(n) + r'\$\s*', v):
                problems['2 nested'].append(f'{k}: ${n}$ is a replace/ key inside a sentence')

# 3. scripted loc and targets
sl = set()
for f in glob.glob(os.path.join(MOD, 'common', 'scripted_localisation', '*.txt')) + \
        glob.glob(OWB + '/common/scripted_localisation/*.txt') + glob.glob(VAN + '/common/scripted_localisation/*.txt'):
    sl |= set(re.findall(r'\bname\s*=\s*"?(\w+)"?', read(f)))
tags = set()
for f in glob.glob(OWB + '/common/country_tags/*.txt'):
    tags |= set(re.findall(r'^\s*([A-Z0-9]{3})\s*=', read(f), re.M))
states = set()
for f in glob.glob(OWB + '/history/states/*.txt'):
    m = re.search(r'\bid\s*=\s*(\d+)', read(f))
    if m:
        states.add(m.group(1))
chars = set()
for f in glob.glob(OWB + '/common/characters/*.txt') + glob.glob(os.path.join(MOD, 'common', 'characters', '*.txt')):
    for d, n in top_level_names(strip_comments(read(f))):
        if d == 1:
            chars.add(n)
SCOPES = {'ROOT', 'Root', 'FROM', 'From', 'PREV', 'Prev', 'THIS', 'This', 'Player', 'FROM.FROM'}
for k, (v, f) in ours.items():
    for expr in re.findall(r'\[([^\[\]]+)\]', v):
        e = expr.lstrip('?!')
        if re.fullmatch(r'Get\w+', e):
            if e not in sl:
                problems['3 scripted loc'].append(f'{k}: [{expr}] not defined')
            continue
        head = e.split('.')[0].split('|')[0]
        if head in SCOPES or head.startswith(('mltd', 'var:', 'global')) or head.islower():
            continue
        if re.fullmatch(r'\d+', head):
            if head not in states:
                problems['3 scripted loc'].append(f'{k}: [{expr}] state {head} does not exist')
        elif re.fullmatch(r'[A-Z0-9]{3}', head):
            if head not in tags:
                problems['3 scripted loc'].append(f'{k}: [{expr}] tag {head} does not exist')
        elif re.fullmatch(r'[A-Z]{2,}_\w+|[A-Z]{3}_\w+', head):
            if head not in chars:
                problems['3 scripted loc'].append(f'{k}: [{expr}] character {head} does not exist')

# 4. file hygiene
for f in glob.glob(os.path.join(MOD, 'localisation', '**', '*.yml'), recursive=True):
    data = open(f, 'rb').read()
    rel = norm(os.path.relpath(f, MOD))
    if not data.startswith(b'\xef\xbb\xbf'):
        problems['4 file'].append(f'{rel}: no UTF-8 BOM (the file is silently ignored)')
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        problems['4 file'].append(f'{rel}: not valid UTF-8 ({e})')
        continue
    if b'\r\n' in data:
        problems['4 file'].append(f'{rel}: CRLF line endings (house style is LF)')
    lines = text.split('\n')
    if lines[0].strip() not in ('l_english:',):
        problems['4 file'].append(f'{rel}: first line is {lines[0]!r}, not l_english:')
    seen = {}
    for i, line in enumerate(lines[1:], 2):
        s = line.rstrip('\r')
        if not s.strip() or s.lstrip().startswith('#'):
            continue
        if '\t' in s:
            problems['4 file'].append(f'{rel}:{i}: tab character')
        m = KEYLINE.match(s)
        if not m:
            problems['4 file'].append(f'{rel}:{i}: malformed line: {s[:90]}')
            continue
        k, v = m.group(1), m.group(2)
        if k in seen:
            problems['4 file'].append(f'{rel}:{i}: duplicate key {k} (first at line {seen[k]})')
        seen[k] = i
        if v.count('$') % 2:
            problems['4 file'].append(f'{rel}:{i}: odd number of $ in {k}')
        if v.count('[') != v.count(']'):
            problems['4 file'].append(f'{rel}:{i}: unbalanced [ ] in {k}')
        opens = len(re.findall(r'§[^!]', v))
        closes = v.count('§!')
        if opens != closes:
            problems['4 file'].append(f'{rel}:{i}: {opens} colour codes opened, {closes} closed in {k}')
        if re.match(r'mltd\.\d+\.(t|d)$', k):
            bad = set(re.findall(r'§([^!oc])', v))
            if bad:
                problems['4 file'].append(f'{rel}:{i}: event text {k} uses §{"".join(sorted(bad))} (only §o / §c on event paper)')
        if re.match(r'mltd\.\d+\.[abce-su-z]$', k) and '§' in v:
            problems['4 file'].append(f'{rel}:{i}: event option {k} carries a colour code')
        if re.search(r'(?<!\\)"', v):
            problems['4 file'].append(f'{rel}:{i}: unescaped double quote inside {k}')

# 5. unused
if show_unused:
    all_script = '\n'.join(read(f) for f in script_files) + '\n'.join(read(f) for f in glob.glob(os.path.join(MOD, 'interface', '*.gui')))
    all_loc = '\n'.join(v for v, _ in ours.values())
    for k in sorted(ours):
        if '/replace/' in ours[k][1]:
            continue
        if k in refs or re.search(r'\b' + re.escape(k) + r'\b', all_script) or ('$' + k + '$') in all_loc:
            continue
        base = re.sub(r'_(desc|short|blocked|tooltip)$', '', k)
        if base in refs or re.search(r'\b' + re.escape(base) + r'\b', all_script):
            continue
        problems['5 unused (info)'].append(k)

n_bad = 0
for sec in sorted(problems):
    items = problems[sec]
    print(f'== {sec}: {len(items)}')
    for it in items:
        print('  ' + it)
    if not sec.startswith('5'):
        n_bad += len(items)
print(f'checked {len(refs)} referenced keys against {len(ours)} of ours, {len(owb)} OWB, {len(van)} vanilla')
sys.exit(1 if n_bad else 0)
