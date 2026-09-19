"""Resolve every focus of mlt_nf to its grid cell: the override's national focuses plus every shared focus pulled in
(the listed roots, then transitively through prerequisites on pulled shared focuses). Reports overlaps, the story
focuses pulled in against the spec's 39, and each story focus's cell."""
import glob
import os
import re
import sys

MOD = r'C:\Users\jonat\Documents\rising-tide\mod_folder'
OWB = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196'


def rd(p):
    return open(p, 'rb').read().decode('utf-8-sig', 'replace')


def nocomment(t):
    return re.sub(r'#[^\n]*', '', t)


def blocks(text):
    """top-level key = { body } pairs of text"""
    out, i, n = [], 0, len(text)
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


def flat(body):
    prev = None
    while prev != body:
        prev = body
        body = re.sub(r'\{[^{}]*\}', ' ', body)
    return body


def focus_info(body):
    f = flat(body)
    get = lambda k: (re.search(r'(?:^|\s)%s\s*=\s*([-A-Za-z0-9_.]+)' % k, f) or [None, None])[1]
    pre = []
    for k, b in blocks(body):
        if k == 'prerequisite':
            pre.append(re.findall(r'\bfocus\s*=\s*([A-Za-z0-9_]+)', b))
    offsets = [b for k, b in blocks(body) if k == 'offset']
    me = []
    for k, b in blocks(body):
        if k == 'mutually_exclusive':
            me += re.findall(r'\bfocus\s*=\s*([A-Za-z0-9_]+)', b)
    return {'id': get('id'), 'x': int(get('x') or 0), 'y': int(get('y') or 0), 'rel': get('relative_position_id'),
            'pre': pre, 'offsets': len(offsets), 'me': me}


tree_path = os.path.join(MOD, 'common', 'national_focus', 'Mirelurk Tribe (MLT) Focus.txt')
tree = [b for k, b in blocks(nocomment(rd(tree_path))) if k == 'focus_tree'][0]
national = {}
for k, b in blocks(tree):
    if k == 'focus':
        fi = focus_info(b)
        fi['src'] = 'override'
        assert fi['id'] not in national, fi['id']
        national[fi['id']] = fi
roots = re.findall(r'(?m)^\s*shared_focus\s*=\s*([A-Za-z0-9_]+)', flat(tree))

files = {}
for root in (OWB, MOD):
    for p in glob.glob(os.path.join(root, 'common', 'national_focus', '*.txt')):
        files[os.path.basename(p).lower()] = p
shared = {}
dups = []
for p in sorted(files.values()):
    for k, b in blocks(nocomment(rd(p))):
        if k == 'shared_focus':
            fi = focus_info(b)
            fi['src'] = os.path.basename(p)
            if fi['id'] in shared:
                dups.append((fi['id'], shared[fi['id']]['src'], fi['src']))
            shared[fi['id']] = fi
pulled = set(roots)
changed = True
while changed:
    changed = False
    for fid, fi in shared.items():
        if fid not in pulled and any(set(g) & pulled for g in fi['pre']):
            pulled.add(fid)
            changed = True
missing_roots = [r for r in roots if r not in shared]

allf = dict(national)
for fid in pulled:
    if fid in shared:
        assert fid not in allf, 'national and shared ' + fid
        allf[fid] = shared[fid]

pos = {}


def resolve(fid, stack=()):
    if fid in pos:
        return pos[fid]
    fi = allf[fid]
    if fid in stack:
        raise SystemExit('cycle ' + ' -> '.join(stack + (fid,)))
    x, y = fi['x'], fi['y']
    if fi['rel']:
        if fi['rel'] not in allf:
            raise SystemExit('%s: relative_position_id %s not in the tree' % (fid, fi['rel']))
        rx, ry = resolve(fi['rel'], stack + (fid,))
        x, y = x + rx, y + ry
    pos[fid] = (x, y)
    return pos[fid]


for fid in allf:
    resolve(fid)
cells = {}
for fid, c in pos.items():
    cells.setdefault(c, []).append(fid)
overlaps = {c: v for c, v in cells.items() if len(v) > 1}

SPEC = {
    'mltd_wbh_eyes_in_the_sound': (13, 22), 'mltd_wbh_the_drowned_knights': (13, 23),
    'mltd_brk_salt_on_the_broken_coast': (15, 22), 'mltd_brk_the_deep_ones_sail_north': (15, 23),
    'mltd_bdt_the_bone_shore': (17, 22), 'mltd_bdt_the_dancers_hear_the_tide': (17, 23),
    'mltd_wbh_the_tide_wall': (12, 25), 'mltd_brk_the_drowned_covenant': (14, 25),
    'mltd_bdt_hail_the_drowned_king': (16, 25), 'mltd_bdt_drown_the_dance': (18, 25),
    'mltd_the_tide_turns_south': (15, 26),
    'mltd_ncr_a_mole_in_shady_sands': (15, 27), 'mltd_ncr_drowned_delegates': (13, 28),
    'mltd_ncr_sleepers_on_the_long_15': (15, 28), 'mltd_ncr_salt_on_the_caravan_roads': (17, 28),
    'mltd_ncr_the_turbines_sing': (15, 29), 'mltd_when_shady_sands_falls': (15, 30),
    'mltd_mars_in_the_water': (15, 31),
    'mltd_ces_what_the_river_carries': (12, 32), 'mltd_ces_the_sea_against_mars': (12, 33),
    'mltd_bos_the_drowned_paladin': (14, 32), 'mltd_bos_blood_in_the_water': (14, 33),
    'mltd_wht_the_lake_god_answers': (16, 32), 'mltd_wht_rites_on_the_spiral_jetty': (16, 33),
    'mltd_hea_whispers_in_the_steam': (18, 32), 'mltd_hea_the_crusade_turns_south': (18, 33),
    'mltd_when_the_legion_breaks': (15, 34),
    'mltd_the_southern_deep': (15, 35),
    'mltd_tex_all_waters_are_one': (13, 36), 'mltd_tex_black_water_rising': (13, 37),
    'mltd_ate_the_feathered_tide': (15, 36), 'mltd_ate_the_serpent_drowns': (15, 37),
    'mltd_tla_the_iron_god_dreams': (17, 36), 'mltd_tla_the_drowned_god_sleeps': (17, 37),
    'mltd_the_last_king_kneels': (15, 38),
    'mltd_rlyeh_rises': (15, 39), 'mltd_ending_the_dreamer_wakes': (13, 40),
    'mltd_ending_the_priestess_reigns': (15, 40), 'mltd_ending_return_to_the_sea': (17, 40),
}
NATIONAL_SPEC = {'mltd_the_grand_ritual': (15, 20), 'mltd_the_deep_ones_walk': (15, 21), 'mltd_the_final_ritual': (15, 24)}

print('national focuses in the override:', len(national))
print('listed roots:', roots, 'missing:', missing_roots)
print('shared defined twice (later file wins):', dups)
story_pulled = sorted(f for f in pulled if f.startswith('mltd_'))
other_pulled = sorted(f for f in pulled if not f.startswith('mltd_'))
print('pulled shared: %d mltd_ + %d other (%s)' % (len(story_pulled), len(other_pulled),
                                                     ', '.join(sorted({shared[f]['src'] for f in other_pulled}))))
print('spec story focuses not pulled in:', sorted(set(SPEC) - set(story_pulled)))
print('pulled in but not in the spec:', sorted(set(story_pulled) - set(SPEC)))
story_files = sorted({shared[f]['src'] for f in story_pulled})
print('story focuses come from:', story_files)
unpulled_in_story_files = sorted(f for f, fi in shared.items() if fi['src'].startswith('mltd_') and f not in pulled)
print('mltd_ shared focuses defined but not pulled in:', unpulled_in_story_files)
bad = []
for f, c in sorted(SPEC.items(), key=lambda kv: (kv[1][1], kv[1][0])):
    got = pos.get(f)
    flag = '' if got == c else '   <-- SPEC %s' % (c,)
    if flag:
        bad.append(f)
    print('  %-40s %-9s %s%s' % (f, got, allf[f]['src'] if f in allf else '-', flag))
for f, c in NATIONAL_SPEC.items():
    print('  %-40s %-9s %s%s' % (f, pos.get(f), 'override', '' if pos.get(f) == c else '   <-- SPEC %s' % (c,)))
print('cells off the spec:', bad)
print('focuses with offset blocks:', [f for f, fi in allf.items() if fi['offsets']])
print('negative x:', [f for f, c in pos.items() if c[0] < 0])
print('OVERLAPS:', overlaps or 'none')
# prerequisites that name a focus not in the tree
for f, fi in allf.items():
    for g in fi['pre']:
        for q in g:
            if q not in allf:
                print('PREREQ NOT IN TREE:', f, '->', q)
    for q in fi['me']:
        if q not in allf:
            print('MUTUALLY_EXCLUSIVE NOT IN TREE:', f, '->', q)
# rows 20-40, columns 10-20: a picture of the spine
print()
for y in range(19, 41):
    row = ''
    for x in range(10, 21):
        v = cells.get((x, y))
        row += ('%-4s' % ('[%d]' % len(v) if v and len(v) > 1 else ('##' if v else '.')))
    print('%2d %s' % (y, row))
print('   ' + ''.join('%-4d' % x for x in range(10, 21)))
# anything else in rows 20-41 outside the spine window
print('other focuses in rows 19-41:', sorted((c, v) for c, v in cells.items() if 19 <= c[1] <= 41 and not 10 <= c[0] <= 20))
print('max cell:', max(c[0] for c in pos.values()), max(c[1] for c in pos.values()), 'min', min(c[0] for c in pos.values()), min(c[1] for c in pos.values()))
