"""Rebuild the stopped story-acts-finish run's state from its journal (repo-only helper).

Writes story_rework/runs/finish_results.json (every agent's result) and story_rework/runs/finish_fix_input.json (exactly
what the run's last agent, the fixer, was given: the earlier findings still open and the new findings that survived
verification), then prints a summary. Mirrors the filters in the run's script.
"""
import json, os, sys

J = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    r'~\.claude\projects\c--Users-jonat-Documents-rising-tide\71877056-fecf-418a-a4f4-50b7c28bba62'
    r'\subagents\workflows\wf_9e6e1b83-680\journal.jsonl')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runs')
LENSES = ['script', 'progression', 'docs', 'story']

started, res = {}, {}
for line in open(J, encoding='utf-8'):
    try:
        j = json.loads(line)
    except Exception:
        continue
    if j.get('type') == 'started':
        started[j['key']] = j.get('label')
    if j.get('type') == 'result':
        res[started.get(j['key'], j['key'])] = j['result']
json.dump(res, open(os.path.join(OUT, 'finish_results.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

confirms = [res[k] for k in sorted((k for k in res if k.startswith('confirm:F')), key=lambda k: int(k[len('confirm:F'):]))]
open_items = [c for c in confirms if c['status'] in ('partly', 'unresolved')
              or (c.get('fix_introduced_problem') or '').strip().__len__() > 3]
fresh = []
for lens in LENSES:
    r = res.get('review:' + lens)
    if r:
        fresh += [dict(f, lens=lens) for f in r['findings']]
survivors = []
for i, f in enumerate(fresh):
    votes = [res[k] for k in ('verify:%d:0' % i, 'verify:%d:1' % i) if k in res]
    if sum(not v['refuted'] for v in votes) >= 1 and sum(v['refuted'] for v in votes) < 2:
        survivors.append(dict(f, verifier_reasons=[v['reason'] for v in votes]))
json.dump({'open_earlier': open_items, 'new_confirmed': survivors},
          open(os.path.join(OUT, 'finish_fix_input.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print('earlier findings:')
for c in confirms:
    print('  %-4s %-18s fix-problem: %s' % (c['id'], c['status'], (c.get('fix_introduced_problem') or '-')[:110]))
print('new findings: %d, surviving verification: %d' % (len(fresh), len(survivors)))
for f in survivors:
    print('  [%s/%s] %s | %s' % (f['lens'], f['severity'], f['where'][:60], f['problem'][:150]))
print('fixer input items: %d open earlier + %d new' % (len(open_items), len(survivors)))
