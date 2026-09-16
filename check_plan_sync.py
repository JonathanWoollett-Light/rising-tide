"""Check that CONQUEST_PLAN.txt, the mod's code and MLT's AI agree.

CONQUEST_PLAN.txt is the simplified ideal strategy for MLT - one human conquest, one operation a line - and MLT's
AI (mod_folder/common/ai_strategy_plans, ai_strategy and ai_templates, the mltd_*.txt files) follows it broadly.
CLAUDE.md requires the three to stay in step. This script prints every place they have drifted apart and exits 1:

- an id the plan names that OWB or the mod does not define: focus, tech, decision, operation, event, equipment,
  sub-unit, law or country; a state the plan gives to a country ("on TAG, state N", "TAG N") that the country does
  not own at game start; a state written "N Name" whose real name is different;
- an id the AI names that nothing defines: a focus, a tech, a country, an operation;
- a focus the plan takes that no ai_national_focuses list holds;
- a country the plan justifies on, declares war on or makes peace with that no conquer strategy targets, and a
  country the AI conquers that the plan never names;
- a tech the plan researches with no research_tech strategy;
- an mltd_op_ operation the plan runs with no operative_operation strategy;
- a division template the plan designs (template "X" = ...) that no ai_templates target_template matches.
- a focus, tech or conquest target the plan or the AI uses that the telemetry (mltd_telemetry_effects.txt) does not
  poll; python build_telemetry.py regenerates it.

An intended difference is a comment line in the plan, which exempts its ids:

    # AI deviation: <focus|war|research|operation|template> <id> [<id> ...] - <why>

Template names go in double quotes. A deviation line that no longer applies is reported as well.
Numbers are not checked: keeping the plan's costs, dates and snapshots right stays a reading job.

Usage: python check_plan_sync.py
"""
import glob
import os
import re
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(BASE, "mod_folder")
PLAN = os.path.join(BASE, "CONQUEST_PLAN.txt")
OWB = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196"
VAN = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV"
KINDS = ("focus", "war", "research", "operation", "template")
TAG = r"[A-Z][A-Z0-9]{2}"


def rd(path):
    return open(path, "rb").read().decode("utf-8-sig", errors="replace")


def script(path):
    """A script file's text without its # comments."""
    lines = []
    for line in rd(path).split("\n"):
        if "#" in line:
            if '"' not in line:
                line = line.split("#", 1)[0]
            else:
                quoted = False
                for i, ch in enumerate(line):
                    if ch == '"':
                        quoted = not quoted
                    elif ch == "#" and not quoted:
                        line = line[:i]
                        break
        lines.append(line)
    return "\n".join(lines)


def body(text, start):
    """The contents of the block whose opening brace ends at index start."""
    i, depth = start, 1
    while depth and i < len(text):
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i - 1]


REPLACED = {p.replace("\\", "/").strip("/") for p in
            re.findall(r'replace_path\s*=\s*"([^"]+)"', rd(os.path.join(OWB, "descriptor.mod")))}


def loaded(rel):
    """The .txt files the game loads from one folder: vanilla's unless OWB replaces the folder, then OWB's, then
    ours, a later file replacing an earlier one of the same name."""
    files = {}
    for root in ([] if rel in REPLACED else [VAN]) + [OWB, MOD]:
        for path in glob.glob(os.path.join(root, *rel.split("/"), "*.txt")):
            files[os.path.basename(path).lower()] = path
    return list(files.values())


def keys(rel, depth):
    """Every key that opens a block (key = {) at the given brace depth, in one folder."""
    found = set()
    for path in loaded(rel):
        text, level = re.sub(r'"[^"\n]*"', '""', script(path)), 0
        for m in re.finditer(r"([A-Za-z0-9_.@:\-]+)\s*=\s*\{|[{}]", text):
            if m.group(1):
                if level == depth:
                    found.add(m.group(1))
                level += 1
            else:
                level += 1 if m.group(0) == "{" else -1
    return found


def ids(rel, pattern):
    found = set()
    for path in loaded(rel):
        found |= set(re.findall(pattern, script(path)))
    return found


def mine(rel):
    return sorted(glob.glob(os.path.join(MOD, *rel.split("/"), "mltd_*.txt")))


# ---- what the game defines
defined = {
    "focus": ids("common/national_focus", r"(?m)^\s*id\s*=\s*([A-Za-z0-9_]+)"),
    "tech": keys("common/technologies", 1),
    "decision": keys("common/decisions", 1),
    "operation": keys("common/operations", 0),
    "event": ids("events", r"(?m)^\s*id\s*=\s*([A-Za-z0-9_]+\.\d+)"),
    "equipment": keys("common/units/equipment", 1),
    "sub-unit": keys("common/units", 1),
    "law": keys("common/ideas", 2),
    "country": ids("common/country_tags", r"(?m)^\s*(" + TAG + r")\s*="),
}
owner, name = {}, {}
for path in glob.glob(os.path.join(OWB, "history", "states", "*.txt")):
    sid = re.match(r"\d+", os.path.basename(path))
    if sid:
        m = re.search(r"\bowner\s*=\s*(" + TAG + ")", script(path))
        owner[int(sid.group())] = m.group(1) if m else None
for path in sorted(glob.glob(os.path.join(OWB, "localisation", "**", "*_l_english.yml"), recursive=True),
                   key=lambda p: "replace" in p.lower()):
    for m in re.finditer(r'(?m)^\s*STATE_(\d+):\d*\s*"([^"]*)"', rd(path)):
        name[int(m.group(1))] = m.group(2)

# ---- what the plan uses
problems = []
deviations = {kind: set() for kind in KINDS}
used = {kind: {} for kind in defined}
templates = {}
plan_text = rd(PLAN)


def use(kind, x, n):
    used[kind].setdefault(x, n)


for n, line in enumerate(plan_text.split("\n"), 1):
    dev = re.match(r"#\s*AI deviation:\s*(\S+)\s+(.+?)\s+-\s", line)
    if dev:
        if dev.group(1) in KINDS:
            deviations[dev.group(1)] |= {x.strip('"') for x in re.findall(r'"[^"]+"|[A-Za-z0-9_.]+', dev.group(2))}
        else:
            problems.append("line %d: deviation kind %r is not one of %s" % (n, dev.group(1), ", ".join(KINDS)))
        continue
    op = line.split("#", 1)[0].strip()
    if not op:
        continue
    words = op.split()
    if words[0] == "focus":
        use("focus", words[1], n)
    elif words[:2] == ["research", "slot"]:
        use("tech", words[3], n)
    elif words[0] in ("event", "law"):
        use(words[0], words[1], n)
    elif words[0] == "decision" and re.fullmatch(r"[a-z][a-z0-9]*_[a-z0-9_]+", words[1]):
        use("decision", words[1], n)
    elif words[0] == "production":
        for eq in re.findall(r"\b[a-z][a-z0-9_]*_equipment(?:_[a-z0-9]+)*\b", op):
            use("equipment", eq, n)
    elif words[0] == "template":
        m = re.match(r'template "([^"]+)"\s*(\+?=)\s*(.+)', op)
        comp = Counter()
        for count, unit in re.findall(r"(\d+)\s*(?:x\s+)?([a-z][a-z0-9_]*)", m.group(3)):
            comp[unit] += int(count)
            use("sub-unit", unit, n)
        if m.group(2) == "=":
            templates[m.group(1)] = (comp, n)
    for o in re.findall(r"\bmltd_op_[a-z0-9_]+", op):
        use("operation", o, n)
    if re.match(r"(justify|declare war|peace with)\b", op):
        for t in re.findall(r"\b" + TAG + r"\b", op):
            use("country", t, n)
        for t, sid in re.findall(r"\b(" + TAG + r"),? (?:state )?(\d+)\b", op):
            if owner.get(int(sid)) != t:
                problems.append("line %d: state %s belongs to %s at game start, not %s" % (n, sid, owner.get(int(sid)), t))
    for sid, nm in re.findall(r"\b(\d+) ([A-Z][a-z'][A-Za-z']*(?: [A-Z][A-Za-z']*)*)", op):
        if int(sid) not in name:
            problems.append("line %d: state %s does not exist" % (n, sid))
        elif name[int(sid)] != nm:
            problems.append("line %d: state %s is %r, not %r" % (n, sid, name[int(sid)], nm))

for kind, pool in defined.items():
    for x, n in sorted(used[kind].items(), key=lambda kv: kv[1]):
        if x not in pool:
            problems.append("line %d: %s %s is not defined" % (n, kind, x))

# ---- what the AI does
ai_focuses = set()
for path in mine("common/ai_strategy_plans"):
    for block in re.findall(r"\bai_national_focuses\s*=\s*\{([^}]*)\}", script(path)):
        ai_focuses |= set(block.split())
strategies = []
for path in mine("common/ai_strategy") + mine("common/ai_strategy_plans"):
    for block in re.findall(r"\bai_strategy\s*=\s*\{([^{}]*)\}", script(path)):
        strategies.append(dict(re.findall(r'(\w+)\s*=\s*"?([^\s{}"]+)"?', block)))


def value(s):
    try:
        return float(s.get("value", 0))
    except ValueError:
        return 0.0


def targets(kind, key="id", positive=True):
    return {s[key] for s in strategies if s.get("type") == kind and key in s and (value(s) > 0 or not positive)}


conquer, research, operations = targets("conquer"), targets("research_tech"), targets("operative_operation", "operation")
ai_templates = []
for path in mine("common/ai_templates"):
    text = script(path)
    for m in re.finditer(r"\btarget_template\s*=\s*\{", text):
        tt = body(text, m.end())
        r = re.search(r"\bregiments\s*=\s*\{", tt)
        comp = Counter()
        if r:
            reg = body(tt, r.end())
            for unit in re.findall(r"([a-z][a-z0-9_]*)\s*=\s*\{[^{}]*\}", reg):
                comp[unit] += 1
            flat = re.sub(r"[a-z][a-z0-9_]*\s*=\s*\{[^{}]*\}", "", reg)
            for unit, count in re.findall(r"([a-z][a-z0-9_]*)\s*=\s*(\d+)", flat):
                comp[unit] += int(count)
        ai_templates.append(comp)

for f in sorted(ai_focuses - defined["focus"]):
    problems.append("AI: focus %s is not defined" % f)
for t in sorted({s["id"] for s in strategies if re.fullmatch(TAG, s.get("id", ""))} - defined["country"]):
    problems.append("AI: country %s is not defined" % t)
for t in sorted(targets("research_tech", positive=False) - defined["tech"]):
    problems.append("AI: tech %s is not defined" % t)
for o in sorted(targets("operative_operation", "operation", positive=False) - defined["operation"]):
    problems.append("AI: operation %s is not defined" % o)


# ---- plan against AI
def cover(kind, planned, ai, what):
    for x, n in sorted(planned.items(), key=lambda kv: kv[1]):
        if x not in ai and x not in deviations[kind]:
            problems.append("line %d: %s %s has no %s and no '# AI deviation: %s' line" % (n, kind, x, what, kind))
    for x in sorted(deviations[kind]):
        if (x in planned) == (x in ai):
            problems.append("'# AI deviation: %s %s' no longer applies" % (kind, x))


cover("focus", used["focus"], ai_focuses, "ai_national_focuses entry")
cover("war", used["country"], conquer, "conquer strategy")
cover("research", used["tech"], research, "research_tech strategy")
cover("operation", used["operation"], operations, "operative_operation strategy")
for t in sorted(conquer - set(re.findall(r"\b" + TAG + r"\b", plan_text)) - deviations["war"]):
    problems.append("the AI conquers %s, which the plan never names" % t)
for nm, (comp, n) in templates.items():
    if nm not in deviations["template"] and comp not in ai_templates:
        problems.append("line %d: template %r (%s) matches no ai_templates target_template"
                        % (n, nm, " + ".join("%d %s" % (c, u) for u, c in comp.items())))
for nm in sorted(deviations["template"]):
    if nm not in templates or templates[nm][0] in ai_templates:
        problems.append("'# AI deviation: template \"%s\"' no longer applies" % nm)

# ---- plan and AI against the telemetry, which build_telemetry.py generates from them
TELEMETRY = os.path.join(MOD, "common", "scripted_effects", "mltd_telemetry_effects.txt")
if os.path.exists(TELEMETRY):
    logged = script(TELEMETRY)
    polled = {kind: set(re.findall(r"\b%s (?:id|tag)=([A-Za-z0-9_]+)" % kind, logged)) for kind in ("FOCUS", "TECH", "GONE")}
    for f in sorted((set(used["focus"]) | ai_focuses) - polled["FOCUS"]):
        problems.append("telemetry: focus %s is not polled (python build_telemetry.py)" % f)
    for t in sorted((set(used["tech"]) | research) - polled["TECH"]):
        problems.append("telemetry: tech %s is not polled (python build_telemetry.py)" % t)
    for t in sorted(conquer - polled["GONE"]):
        problems.append("telemetry: country %s is not tracked (python build_telemetry.py)" % t)
    print("telemetry: %d focuses, %d techs, %d countries polled"
          % (len(polled["FOCUS"]), len(polled["TECH"]), len(polled["GONE"])))
else:
    print("telemetry: absent")

print("plan: %d focuses, %d techs, %d wars, %d templates, %d deviations; AI: %d focuses, %d conquer targets, "
      "%d research_tech, %d operations, %d templates"
      % (len(used["focus"]), len(used["tech"]), len(used["country"]), len(templates),
         sum(len(v) for v in deviations.values()), len(ai_focuses), len(conquer), len(research), len(operations),
         len(ai_templates)))
for p in problems:
    print("PROBLEM:", p)
print("OK" if not problems else "%d problem(s)" % len(problems))
sys.exit(1 if problems else 0)
