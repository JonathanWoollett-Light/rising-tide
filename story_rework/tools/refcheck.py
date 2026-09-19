"""Which loc keys, scripted effects and scripted triggers of the mod are referenced, with and without the old
mltd_conflicts_focus.txt. Prints the keys that only the old file used."""
import glob
import json
import os
import re
import sys

REPO = r'C:\Users\jonat\Documents\rising-tide'
MOD = os.path.join(REPO, 'mod_folder')
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, 'mltd_conflicts_focus.txt')
LOC = os.path.join(MOD, 'localisation', 'english', 'MLT', 'mltd_l_english.yml')
KEY = re.compile(r'^\s+([^\s:#"]+):\d*\s*"(.*)"\s*$')

AI_PARTS = ('ai_strategy', 'ai_templates', 'mltd_ai_triggers.txt', 'mltd_ai_survey_effects.txt', 'scorers',
            'peace_conference', 'mltd_telemetry_effects.txt')


def rd(p):
    return open(p, 'rb').read().decode('utf-8-sig', 'replace')


def nocomment(t):
    return re.sub(r'#[^\n]*', '', t)


def loc_entries(path):
    out = {}
    for line in rd(path).split('\n'):
        m = KEY.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


loc = loc_entries(LOC)
replace = {}
for p in glob.glob(os.path.join(MOD, 'localisation', 'replace', '*.yml')):
    replace.update(loc_entries(p))

deleted_focus = set()
old_ids = set(re.findall(r'(?m)^\s*id\s*=\s*([A-Za-z0-9_]+)', nocomment(rd(OLD))))
now_ids = set()
for p in glob.glob(os.path.join(MOD, 'common', 'national_focus', '*.txt')):
    now_ids |= set(re.findall(r'(?m)^\s*id\s*=\s*([A-Za-z0-9_]+)', nocomment(rd(p))))
deleted_focus = old_ids - now_ids


def corpus(with_old):
    files = []
    for p in glob.glob(os.path.join(MOD, '**', '*'), recursive=True):
        if os.path.isdir(p) or os.path.abspath(p) == os.path.abspath(LOC):
            continue
        if os.path.splitext(p)[1].lower() not in ('.txt', '.gui', '.gfx', '.yml', '.mod', '.lua', '.csv'):
            continue
        files.append(p)
    files += glob.glob(os.path.join(REPO, '*.py'))
    if with_old:
        files.append(OLD)
    out = []
    for p in files:
        t = rd(p)
        if p.endswith('.txt') or p.endswith('.gui') or p.endswith('.gfx'):
            t = nocomment(t)
        is_ai = any(a in p.replace('\\', '/') for a in AI_PARTS)
        out.append((p, t, is_ai))
    return out


TOK = re.compile(r'[A-Za-z0-9_.\-]+')
TOK2 = re.compile(r'[A-Za-z0-9_\-]+')


def referenced(with_old):
    tokens = {}
    for p, t, is_ai in corpus(with_old):
        for tok in set(TOK.findall(t)) | set(TOK2.findall(t)):
            tokens.setdefault(tok, []).append((p, is_ai))
    ref = {}
    for k in loc:
        hits = tokens.get(k, [])
        if k in deleted_focus or (k.endswith('_desc') and k[:-5] in deleted_focus):
            hits = [h for h in hits if not h[1]]
        if hits:
            ref[k] = sorted({os.path.relpath(h[0], REPO) for h in hits})
    # suffix keys follow their base
    changed = True
    while changed:
        changed = False
        for k in loc:
            if k in ref:
                continue
            for suf in ('_desc', '_short', '_blocked', '_tooltip', '_long'):
                if k.endswith(suf) and k[:-len(suf)] in ref and k[:-len(suf)] not in deleted_focus:
                    ref[k] = ['(suffix of %s)' % k[:-len(suf)]]
                    changed = True
                    break
            else:
                # event keys mltd.N.x follow the event id
                m = re.match(r'^(mltd\.\d+)\.[a-z]+$', k)
                if m and m.group(1) in tokens:
                    ref[k] = ['(event %s)' % m.group(1)]
                    changed = True
                    continue
                # nested $key$ in a referenced value
                for kk in list(ref):
                    if '$' + k + '$' in loc.get(kk, ''):
                        ref[k] = ['(nested in %s)' % kk]
                        changed = True
                        break
    return ref, tokens


if __name__ == '__main__':
    ref_old, tok_old = referenced(True)
    ref_new, tok_new = referenced(False)
    became = sorted(k for k in loc if k in ref_old and k not in ref_new)
    never = sorted(k for k in loc if k not in ref_old)
    print('deleted focus ids:', len(deleted_focus))
    print('BECAME UNUSED (%d):' % len(became))
    for k in became:
        print('  ', k, ref_old[k])
    print('UNREFERENCED EVEN BEFORE (%d):' % len(never))
    for k in never:
        print('  ', k)
    json.dump({'became': became, 'never': never}, open(os.path.join(HERE, 'refcheck.json'), 'w'), indent=1)
