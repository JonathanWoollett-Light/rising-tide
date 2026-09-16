# -*- coding: utf-8 -*-
"""
ai_run_report.py -- compare an AI Mirelurk Tribe's game with CONQUEST_PLAN.txt.

    python ai_run_report.py                     # the last run in game.log
    python ai_run_report.py --list              # every run in game.log
    python ai_run_report.py --run 2 --out r.md --csv snaps.csv
    python ai_run_report.py --save              # archive the run under ai_runs/
    python ai_run_report.py --plan-only         # the plan's own timeline
    python ai_run_report.py --selftest

Rising Tide's telemetry writes one line to game.log with the `log` effect for
everything an AI (or human) MLT does that the plan cares about.  This script
reads those lines back, splits them into runs, and prints a markdown report:
the run's summary, seventeen automated checks (each naming the AI block to
look at), the plan against the run (focuses, wars, enemies, annexations,
snapshots, research, laws, decisions, rituals, cults) and the run's own
timeline.

**The line contract.**  Every telemetry line renders as one game.log line
that contains

    MLTD <day> <KIND> <key=value ...> [date=<text>]

where <day> is MLT's own counter `mltd_tm_day` (whole days since 2275.1.1,
+1 each on_daily_MLT tick from 0) and <KIND> one upper-case word: START, SNAP,
FOCUS, TECH, LAW, JUSTIFY, WARGOAL, WAR_START, WAR_END, GONE, RITUAL,
DECISION, GIFT, MARKET, CULT, ENEMY, STAGE, POCKET, ADVISOR.  game.log puts its own prefix in front
(`[08:18:02][2275.01.01.12][effectbase.cpp:1783]: `, sometimes glued behind
a dangling `...[effectbase.cpp:1799]: `), so the line is found by `MLTD `
anywhere in it.  Parsing is tolerant: thousands separators, decimals, K/M
suffixes and colour codes in numbers, missing and unknown keys and unknown
kinds are all accepted; identical lines are folded.

**Days.**  HOI4's calendar has 365-day years and no leap day, day 0 is
2275-01-01.  The counter is calibrated against the dates game.log prints in
its own prefix (failing those SNAP's date=, then START's), so a counter that
starts a day late, a weekly or monthly pulse that runs before the daily one,
or a run begun from a save made before the telemetry existed still lands on
calendar days; START, written before the counter's first +1, keeps its own
date.  Every day in the report is a calendar day.  A run is split at START; a
day that goes backwards inside a run is a reloaded save, and what the
abandoned timeline logged from that day on is dropped.

**The plan.**  CONQUEST_PLAN.txt is read as a timeline with a running clock:
`# ---- <date> [day N]` headers set it, `wait N days` advances it, a `focus`
starts when the clock and the focus slot are both free and ends after its
`cost` (read from the focus files; OWB's FOCUS_POINT_DAYS = 1, so cost is
days), and `justify` / `declare war` / `peace with` / `law` / `decision`
lines take the clock - or the `# ~day A-B` (or `# 2281-12`, `# mid-2279`)
estimate comment just above them, which is the plan's own model of when they
happen.  `# snapshot` comments give the numbers the run is compared with.

Nothing here ships: only mod_folder/ does.  Python 3 standard library only.
"""

import argparse
import csv
import glob
import io
import os
import re
import sys
import tempfile
import time
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(BASE, "mod_folder")
PLAN = os.path.join(BASE, "CONQUEST_PLAN.txt")
RUNS_DIR = os.path.join(BASE, "ai_runs")
OWB = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\2265420196"
FOCUS_FILES = [os.path.join(OWB, "common", "national_focus", "Shared Oregon Coastals Focus.txt")] \
    + sorted(glob.glob(os.path.join(MOD, "common", "national_focus", "*.txt")))
TAG_FILES = os.path.join(OWB, "common", "country_tags", "*.txt")


def default_log():
    """game.log under Documents; OneDrive-redirected Documents as a fallback."""
    tail = os.path.join("Paradox Interactive", "Hearts of Iron IV", "logs", "game.log")
    roots = [os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Documents")]
    for var in ("OneDrive", "OneDriveConsumer"):
        if os.environ.get(var):
            roots.append(os.path.join(os.environ[var], "Documents"))
    paths = [os.path.join(r, tail) for r in roots]
    return next((p for p in paths if os.path.exists(p)), paths[0])


# ---- the line contract ---------------------------------------------------------------------------------------
KINDS = ("START", "SNAP", "FOCUS", "TECH", "LAW", "JUSTIFY", "WARGOAL", "WAR_START", "WAR_END", "GONE",
         "RITUAL", "DECISION", "GIFT", "MARKET", "CULT", "ENEMY", "STAGE", "POCKET", "ADVISOR")
# SNAP keys the plan's snapshots are compared on: plan metric -> SNAP key
METRIC_KEYS = (("states", "owned"), ("people", "pop_k"), ("divisions", "divs"), ("civ", "civ"),
               ("mil", "mil"), ("dock", "dock"), ("manpower", "mp_k"), ("caps", "caps"), ("books", "books"))
METRIC_UNITS = {"people": "k", "manpower": "k"}

# ---- calendar: 365-day years, day 0 = 2275-01-01 -------------------------------------------------------------
EPOCH = 2275
MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
CUM = tuple(sum(MONTH_DAYS[:i]) for i in range(12))
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september",
          "october", "november", "december")

# ---- the automated checks ------------------------------------------------------------------------------------
CCW_JUSTIFY_BY = 60                             # (a) days from 2275-01-01
CCW_WARGOAL_BY = 75                             # (a) or a war goal or a war by then
EARLY_WARS = ("CCW", "TRL", "RBT", "MDT")        # (b) the plan's war order
INTERIOR = ("CES", "BOS", "WHT", "EHT", "HEA")   # (f) held until the NCR is beaten (gone or capitulated) ...
INTERIOR_UNTIL = (2283, 1, 1)                    # ... or this date (mltd_ai_hold_late_wargoals)
SOUTH = ("TBH", "LNS", "TLA", "MAX", "MOC", "ZAP")   # (f) held until the Legion is beaten ...
SOUTH_UNTIL = (2286, 1, 1)                       # ... or this date (mltd_ai_hold_south_wargoals)
CULT_TARGET_WITHIN = 14                          # (g) days after The Spreading Cult
MARKET_GRACE = 60                                # (i) days after The Wet Market before "no trade" fails
RITUAL_GATES = (("grand", 100.0, "Grand Ritual"), ("final", 200.0, "Final Ritual"))   # (j) pop_k gates
POPULATION_DECISIONS = ("mltd_summon_the_deep_ones", "mltd_summon_the_star_spawn",
                        "mltd_offering_of_the_drowned", "mltd_offering_of_the_tides")
DIS_OFFER_UNTIL = (2276, 10, 1)                  # (k) mltd_ai_spare_dis stops waiting for nf_dis.4 here
BOOK_EXPEDITION_DAYS = 28                        # (d) a Book is read 2-4 weeks after its focus
# (d) Book focus, the state it needs, who holds that state at start
BOOKS = (("mltd_first_book", "Arago 150", "DIS"), ("mltd_second_book", "The Warren 235", "TRL"),
         ("mltd_third_book", "Paisley Pit 231", "MDT"), ("mltd_fourth_book", "Arroyo 337", "ARR"),
         ("mltd_fifth_book", "The Maw 274", "PMR"))
POCKET_LIMIT = 365                               # (m) days an enemy may stay out of MLT's reach
NCR_CULT_READY = 40                              # (n) the NCR's cult when its war starts (mltd_ai_ncr_cult_ready)
CASTRO_WITHIN = 365                              # (o) days after The Spreading Cult (which founds the agency)
ARMY_WINDOW = 365                                # (p) the last days of SNAPs judged ...
ARMY_RANGE = (0.75, 1.5)                         # ... on divisions / mltd_ai_army_target (target=)
OFFERING_CAPS_AFTER = 200                        # (q) the Drowned after the Final Ritual: caps logged after its +100
TIDES_POP_K = 300                                # (q) the Tides after the Final Ritual: people it needs (thousands)
SNAP_MATCH_WINDOW = 45                           # a plan snapshot matches the nearest SNAP this close
FIRST_POLL_DAYS = 7                              # a weekly poll reports everything already true


def day_of(y, m=1, d=1):
    return (y - EPOCH) * 365 + CUM[m - 1] + d - 1


def iso(day):
    if day is None:
        return "-"
    y, r = divmod(int(day), 365)
    m = max(i for i in range(12) if CUM[i] <= r)
    return "%04d-%02d-%02d" % (EPOCH + y, m + 1, r - CUM[m] + 1)


def month_index(name):
    name = name.lower()
    for i, full in enumerate(MONTHS):
        if len(name) >= 3 and full.startswith(name):
            return i + 1
    return None


def valid(y, m, d):
    return 1000 <= y <= 9999 and 1 <= m <= 12 and 1 <= d <= MONTH_DAYS[m - 1]


def parse_game_date(text):
    """Calendar day of a date the game prints: ' 12:00, 1 January, 2275' (GetDateText), '2275.1.1.12'
    (GetDate, the log prefix), '2275-01-01', '1 January 2275' or 'January 1, 2275'. None if unreadable."""
    if not text:
        return None
    text = strip_codes(text)
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]{3,})\.?,?\s+(\d{4})\b", text)
    if m and month_index(m.group(2)):
        y, mo, d = int(m.group(3)), month_index(m.group(2)), int(m.group(1))
    else:
        m = re.search(r"\b([A-Za-z]{3,})\.?\s+(\d{1,2}),?\s+(\d{4})\b", text)
        if m and month_index(m.group(1)):
            y, mo, d = int(m.group(3)), month_index(m.group(1)), int(m.group(2))
        else:
            m = re.search(r"\b(\d{4})[.\-](\d{1,2})[.\-](\d{1,2})\b", text)
            if not m:
                return None
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return day_of(y, mo, d) if valid(y, mo, d) else None


# ---- numbers -------------------------------------------------------------------------------------------------
def strip_codes(s):
    """Drop HOI4 colour codes (§Y ... §!), also when the § arrived mangled."""
    return re.sub("[\u00a7\ufffd].?", "", s or "")


def parse_num(s):
    """A number as the log may print it: '1,234', '1.234.567', '12,5', '§Y120§!', '12.5K', '1.50M', '45%',
    '+3'. None when it is not a number (a tag, yes/no, none, empty)."""
    if s is None:
        return None
    s = strip_codes(str(s)).strip().replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
    s = s.rstrip("%").lstrip("+")
    scale = 1.0
    if s[-1:] in ("K", "k"):
        s, scale = s[:-1], 1e3
    elif s[-1:] in ("M", "m"):
        s, scale = s[:-1], 1e6
    if not re.fullmatch(r"-?[\d.,]*\d[\d.,]*", s):
        return None
    if "," in s and "." in s:                      # the later separator is the decimal one
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", "") if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s) else s.replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s) * scale
    except ValueError:
        return None


def fmt_num(x):
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    if abs(x - round(x)) < 1e-9:
        return "%d" % round(x)
    return ("%.2f" % x).rstrip("0").rstrip(".")


def fmt_delta(ai, plan):
    if ai is None or plan is None:
        return "-"
    d = int(round(ai - plan))
    return "%+d" % d if d else "0"


# ---- game.log --------------------------------------------------------------------------------------------------
MLTD_AT = re.compile(r"(?<![A-Za-z0-9_])MLTD\s")
LOG_PREFIX = re.compile(r"\[\d{1,2}:\d\d:\d\d\]\[")
PREFIX_DATE = re.compile(r"\[(\d{4})\.(\d{1,2})\.(\d{1,2})(?:\.\d{1,2})?\]")
PAYLOAD = re.compile(r"^MLTD\s+(?P<day>.*?)\s+(?P<kind>[A-Z][A-Z_]{2,})(?=\s|$)(?P<rest>.*)$")
KEY = re.compile(r"(?:^|(?<=\s))([A-Za-z_][A-Za-z0-9_]*)=")


class Line(object):
    """One contract line."""
    __slots__ = ("order", "lineno", "raw", "day", "kind", "kv", "log_day", "cal", "key")

    def __init__(self, order, lineno, raw, day, kind, kv, log_day):
        self.order, self.lineno, self.raw = order, lineno, raw
        self.day, self.kind, self.kv, self.log_day = day, kind, kv, log_day
        self.cal = day
        self.key = " ".join(raw.split())

    def get(self, key, default=None):
        return self.kv.get(key, default)

    def num(self, key):
        return parse_num(self.kv.get(key))

    def text(self, skip=("date",)):
        return " ".join("%s=%s" % kv for kv in self.kv.items() if kv[0] not in skip)


def decode(raw):
    raw = raw.rstrip(b"\r\n")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def parse_payload(payload):
    """(day, kind, kv) of one payload 'MLTD <day> <KIND> k=v ...', or None if it breaks the contract."""
    m = PAYLOAD.match(payload)
    if not m:
        return None
    day = parse_num(m.group("day"))
    if day is None:
        return None
    rest, kv = m.group("rest").strip(), {}
    keys = list(KEY.finditer(rest))
    for i, k in enumerate(keys):
        end = keys[i + 1].start() if i + 1 < len(keys) else len(rest)
        name = k.group(1).lower()
        if name not in kv:
            value = rest[k.end():end].strip()
            kv[name] = value if name == "date" else strip_codes(value).strip()
    return int(round(day)), m.group("kind"), kv


def extract(lines):
    """Every contract line in (line number, text) pairs: (good lines, malformed payloads)."""
    good, bad = [], []
    for lineno, text in lines:
        hits = list(MLTD_AT.finditer(text))
        for i, hit in enumerate(hits):
            end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
            nxt = LOG_PREFIX.search(text, hit.end(), end)
            payload = text[hit.start():nxt.start() if nxt else end].strip()
            dates = list(PREFIX_DATE.finditer(text, 0, hit.start()))
            log_day = None
            if dates:
                y, mo, d = (int(g) for g in dates[-1].groups())
                log_day = day_of(y, mo, d) if valid(y, mo, d) else None
            parsed = parse_payload(payload)
            if parsed is None:
                bad.append((lineno, payload))
            else:
                good.append(Line(len(good), lineno, payload, parsed[0], parsed[1], parsed[2], log_day))
    return good, bad


def read_log(path):
    """(line number, text) of every game.log line that mentions MLTD, streamed: game.log grows large."""
    with open(path, "rb") as f:
        for n, raw in enumerate(f, 1):
            if b"MLTD" in raw:
                yield n, decode(raw)


# ---- runs ----------------------------------------------------------------------------------------------------
class Run(object):
    """The lines from one START to the next. `kept` is the run's one timeline: duplicates folded, and a
    reloaded save's abandoned future dropped."""

    def __init__(self, index, start):
        self.index, self.start = index, start
        self.raw, self.kept, self.seen = [], [], set()
        self.max_day, self.folded, self.reloads = None, 0, []
        self.offset, self.offset_source, self.clock_mismatch = 0, None, 0

    def add(self, ln):
        self.raw.append(ln)
        if self.max_day is not None and ln.day < self.max_day:
            # a save was reloaded. The load re-runs the tick this line was logged in, so whatever the abandoned
            # timeline logged with this counter or a later one was written after the save and never happened
            dropped = sum(1 for k in self.kept if k.day >= ln.day)
            self.reloads.append((self.max_day, ln.day, ln.lineno, dropped))
            self.kept = [k for k in self.kept if k.day < ln.day]
            self.seen = set(k.key for k in self.kept)
            self.max_day = max([k.day for k in self.kept] or [ln.day])
        if ln.key in self.seen:
            self.folded += 1
            return
        self.seen.add(ln.key)
        self.kept.append(ln)
        self.max_day = ln.day if self.max_day is None else max(self.max_day, ln.day)

    def finish(self):
        """Calibrate the day counter and give every line its calendar day. game.log's own dates win, then SNAP's
        date=: whether a weekly or monthly line carries its day's counter or the day before's depends on the
        unverified order of the pulses, and those dates show which. START's date is the fallback. START, and
        anything else logged with its counter, was written before the counter's first +1: it keeps START's date."""
        diffs = Counter(k.log_day - k.day for k in self.kept if k.log_day is not None and k.day > 0)
        from_log = bool(diffs)
        for k in self.kept:
            d = parse_game_date(k.get("date")) if k.kind == "SNAP" and k.day > 0 else None
            if d is not None:
                diffs[d - k.day] += 1
        start_cal = None
        if self.start is not None:
            start_cal = parse_game_date(self.start.get("date"))
            if start_cal is None:
                start_cal = self.start.log_day
        if diffs:
            self.offset = diffs.most_common(1)[0][0]
            self.offset_source = "game.log's dates" if from_log else "SNAP date="
        elif start_cal is not None:
            self.offset = start_cal - self.start.day
            self.offset_source = "START's date alone (a day either way: nothing later shows the pulse order)"
        for k in self.kept:
            k.cal = start_cal if start_cal is not None and k.day == self.start.day else k.day + self.offset
            if k.log_day is not None and k.log_day != k.cal:
                self.clock_mismatch += 1
        self.kept.sort(key=lambda k: (k.cal, k.order))
        return self

    @property
    def first_day(self):
        return self.kept[0].cal if self.kept else None

    @property
    def last_day(self):
        return self.kept[-1].cal if self.kept else None

    def info(self, key, default="?"):
        return self.start.get(key, default) if self.start is not None else default


def split_runs(lines):
    runs, cur = [], None
    for ln in lines:
        if ln.kind == "START" or cur is None:
            cur = Run(len(runs) + 1, ln if ln.kind == "START" else None)
            runs.append(cur)
        cur.add(ln)
    return [r.finish() for r in runs]


# ---- the plan ------------------------------------------------------------------------------------------------
TAG_RE = re.compile(r"\b([A-Z][A-Z0-9]{2})\b(?!'s)")
DECISION_ID = re.compile(r"[a-z][a-z0-9]*_[a-z0-9_]+$")
HEADER = re.compile(r"^#\s*-{3,}\s*(.*)$")
SNAPSHOT = re.compile(r"^#\s*snapshot\b(?P<spec>[^:]*):(?P<text>.*)$")
CONTINUATION = re.compile(r"^#\s{2,}\S")
ESTIMATE = re.compile(r"^#\s*(?:~\s*day\s*(?P<d1>\d+)(?:\s*-\s*(?P<d2>\d+))?"
                      r"|(?P<mid>mid-)?~?(?P<y1>\d{4})(?:-(?P<m1>\d{2})(?!\d))?(?:\s*-\s*~?(?P<y2>\d{4}))?)"
                      r"\s*(?:\[[A-Z]\])?\s*:(?P<text>.*)$")
INLINE_ESTIMATE = re.compile(r"~\s*day\s*(\d+)(?:\s*-\s*(\d+))?")
# verbs whose day is the estimate comment above them when there is one; focus and research follow the clock
ESTIMATED = ("justify", "declare", "peace", "law", "decision", "event")
UNTRACKED = ("production", "template", "train", "army", "market", "operation", "operative")
NUMTOK = r"~?\d[\d,]*(?:\.\d+)?"
SNAP_METRICS = (
    ("states", r"(%s(?:\s*-\s*%s)?)\s+states\b" % (NUMTOK, NUMTOK)),
    ("people", r"(%s[kKM]?(?:\s*-\s*%s[kKM]?)?)\s+people\b" % (NUMTOK, NUMTOK)),
    ("divisions", r"(%s(?:\s*-\s*%s)?)\s+divisions\b" % (NUMTOK, NUMTOK)),
    ("civ", r"(%s)\s+civ\b" % NUMTOK),
    ("mil", r"(%s)\s+mil\b" % NUMTOK),
    ("dock", r"(%s)\s+dock\b" % NUMTOK),
    ("manpower", r"(%s[kKM]?)\s+free manpower\b" % NUMTOK),
    ("caps", r"(%s)\s+caps\b" % NUMTOK),
)


def script_text(path):
    """A script file's text without its # comments (a # inside quotes stays)."""
    out = []
    for line in open(path, "rb").read().decode("utf-8-sig", errors="replace").split("\n"):
        quoted = False
        for i, ch in enumerate(line):
            if ch == '"':
                quoted = not quoted
            elif ch == "#" and not quoted:
                line = line[:i]
                break
        out.append(line)
    return "\n".join(out)


def block(text, start):
    """The contents of the block whose opening brace ends at index start."""
    i, depth = start, 1
    while depth and i < len(text):
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i - 1]


def load_focus_costs(files=None):
    """focus id -> cost in days, from every focus and shared_focus block (later files win)."""
    costs = {}
    for path in files if files is not None else FOCUS_FILES:
        if not os.path.exists(path):
            continue
        text = script_text(path)
        for m in re.finditer(r"(?<![A-Za-z0-9_])(?:shared_)?focus\s*=\s*\{", text):
            flat = block(text, m.end())
            while True:                                  # keep only the block's own keys
                inner = re.sub(r"\{[^{}]*\}", " ", flat)
                if inner == flat:
                    break
                flat = inner
            fid = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+)", flat)
            cost = re.search(r"\bcost\s*=\s*(-?\d+(?:\.\d+)?)", flat)
            if fid and cost:
                costs[fid.group(1)] = float(cost.group(1))
    return costs


def load_country_tags():
    tags = set()
    for path in glob.glob(TAG_FILES):
        tags |= set(re.findall(r"(?m)^\s*([A-Z][A-Z0-9]{2})\s*=", script_text(path)))
    return tags or None


def header_day(text):
    """(day, approx, the date's own day or None) of a dated section header; None for a continuation line."""
    m = re.match(r"(\d{4})-(\d{2})(?:-(\d{2}))?(?:\s+day\s+(~?)(\d+))?", text)
    if m and 2200 <= int(m.group(1)) <= 2400 and 1 <= int(m.group(2)) <= 12:
        dated = day_of(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
        if m.group(5):
            return int(m.group(5)), bool(m.group(4)), dated if m.group(3) else None
        return dated, False, None
    m = re.match(r"~?(\d{4})(?:\s+to\s+~?\d{4})?\s*(?::|$)", text)
    if m and 2200 <= int(m.group(1)) <= 2400:
        return day_of(int(m.group(1))), False, None
    return None


def plan_range(s, thousands=False):
    """(lo, hi, approx) of '12-15', '~90k', '1.3-1.7M', '11,009'; a suffix on the last part applies to all."""
    approx = "~" in s
    parts = [p.strip().lstrip("~") for p in re.split(r"\s*-\s*", s.strip())]
    last = parts[-1][-1:] if parts[-1][-1:] in ("k", "K", "M") else ""
    vals = []
    for p in parts:
        suffix = p[-1:] if p[-1:] in ("k", "K", "M") else last
        v = parse_num(p.rstrip("kKM"))
        if v is None:
            return None
        v *= {"k": 1e3, "K": 1e3, "M": 1e6, "": 1.0}[suffix]
        vals.append(v / 1000.0 if thousands else v)
    return min(vals), max(vals), approx


def snapshot_metrics(text):
    out = {}
    for name, pattern in SNAP_METRICS:
        m = re.search(pattern, text)
        if m:
            r = plan_range(m.group(1), thousands=name in METRIC_UNITS)
            if r:
                out[name] = r
    if "people" not in out:
        m = re.search(r"population\b[^,;]*?\bto\s+(~?\d[\d.,]*[kKM]?)", text)
        if m:
            out["people"] = plan_range(m.group(1), thousands=True)
    m = re.search(r"\b(\d+)\s+Books\s+read(\s+or\s+reading)?", text) or \
        re.search(r"\bBooks\s+\d+\s*-\s*(\d+)\s+read()", text)
    if m:
        out["books"] = (float(m.group(1)), float(m.group(1)), bool(m.group(2)))
    return out


class Plan(object):
    """CONQUEST_PLAN.txt as a timeline. Timed items are dicts: day, approx (from an estimate), line."""

    def __init__(self):
        self.path = None
        self.focuses, self.focus = [], {}
        self.justify, self.declare, self.peace, self.annex = {}, {}, {}, {}
        self.research, self.laws, self.decisions, self.market = [], [], {}, None
        self.snapshots, self.notes, self.consistency = [], [], []
        self.verbs, self.untracked = Counter(), Counter()
        self.end = 0

    def done(self, fid):
        return self.focus[fid]["done"] if fid in self.focus else None

    def begun(self, fid):
        return self.focus[fid]["start"] if fid in self.focus else None


def parse_plan(text, costs, tags=None):
    """The plan's timeline. `costs` maps focus id -> days; `tags` (a set) filters what counts as a country."""
    plan = Plan()
    clock = section = focus_free = 0
    pending = None                # the estimate comment above: (lo, hi)
    snap = None                   # the snapshot a continuation line extends
    is_tag = (lambda t: t != "MLT" and (tags is None or t in tags))

    def item(day, approx, n, **more):
        more.update(day=int(day), approx=approx, line=n)
        return more

    def add_snapshot(day, n, body, source):
        entry = dict(day=int(day), line=n, text=body.strip(), metrics=snapshot_metrics(body), source=source)
        plan.snapshots.append(entry)
        return entry

    for n, line in enumerate(text.split("\n"), 1):
        s = line.rstrip()
        if not s.strip():
            snap = None
            continue
        if s.lstrip().startswith("#"):
            s = s.lstrip()
            h = HEADER.match(s)
            if h:
                hd = header_day(h.group(1))
                if hd is None:                                   # a header's continuation line
                    if snap is not None and snap["source"] == "header":
                        snap["text"] += " " + h.group(1).strip()
                        snap["metrics"] = snapshot_metrics(snap["text"])
                    continue
                if hd[2] is not None and hd[2] != hd[0]:
                    why = "the date is day %d in the 365-day calendar; the header says day %d" % (hd[2], hd[0])
                    if clock == hd[0]:              # the clock the header before set, plus the waits since
                        why += ", as the plan's clock does: correct the date"
                    elif clock == hd[2]:
                        why += ", but the plan's clock reaches day %d: correct the day" % clock
                    plan.consistency.append((n, s, why))
                clock = section = hd[0]
                pending, snap = None, None
                body = h.group(1).split(":", 1)[1] if ":" in h.group(1) else ""
                metrics = snapshot_metrics(body)
                if "states" in metrics and ("people" in metrics or "divisions" in metrics):
                    snap = add_snapshot(clock, n, body, "header")
                continue
            m = SNAPSHOT.match(s)
            if m:
                spec = m.group("spec")
                d = re.search(r"\bday\s*~?(\d+)", spec)
                dt = re.search(r"(\d{4})-(\d{2})(?:-(\d{2}))?", spec)
                day = int(d.group(1)) if d else day_of(int(dt.group(1)), int(dt.group(2)), int(dt.group(3) or 1)) \
                    if dt else section
                snap = add_snapshot(day, n, m.group("text"), "snapshot")
                continue
            if CONTINUATION.match(s) and snap is not None:
                snap["text"] += " " + s.lstrip("#").strip()
                snap["metrics"] = snapshot_metrics(snap["text"])
                continue
            snap = None
            e = ESTIMATE.match(s)
            if e:
                if e.group("d1"):
                    lo, hi = int(e.group("d1")), int(e.group("d2") or e.group("d1"))
                else:
                    y1 = int(e.group("y1"))
                    lo = day_of(y1, 7, 1) if e.group("mid") else day_of(y1, int(e.group("m1") or 1))
                    hi = day_of(int(e.group("y2"))) if e.group("y2") else lo
                pending = (lo, hi)
                # a clause saying who capitulates or is annexed gives those countries' plan annexation days
                for clause in e.group("text").split(";"):
                    if re.search(r"\b(capitulat\w*|annexed)\b", clause):
                        for t in TAG_RE.findall(clause):
                            if is_tag(t) and t not in plan.annex:
                                plan.annex[t] = item((lo + hi) // 2, True, n, how="comment")
            continue

        # ---- an operation
        snap = None
        op, _, comment = s.partition("#")
        op = op.strip()
        words = op.split()
        verb = words[0].lower().rstrip(":")
        plan.verbs[verb] += 1
        inline = INLINE_ESTIMATE.search(comment)
        if inline:
            when = item((int(inline.group(1)) + int(inline.group(2) or inline.group(1))) // 2, True, n)
        elif pending and verb in ESTIMATED:
            when = item((pending[0] + pending[1]) // 2, True, n)
        else:
            when = item(clock, False, n)

        if verb == "focus":
            fid = words[1] if len(words) > 1 else None
            start = max(clock, focus_free)
            cost = costs.get(fid)
            done = start + cost if cost is not None else None
            if cost is None:
                plan.notes.append((n, s, "no cost found for focus %s" % fid))
            focus_free = done if done is not None else start
            f = dict(id=fid, start=int(start), done=None if done is None else int(done), cost=cost, line=n)
            plan.focuses.append(f)
            plan.focus.setdefault(fid, f)
        elif verb == "wait":
            m = re.match(r"wait\s+(\d+)\s+days?\b", op)
            if m:
                clock += int(m.group(1))
                pending = None
            else:
                plan.notes.append((n, s, "a wait without a number of days"))
        elif verb in ("justify", "declare", "peace"):
            found = [t for t in TAG_RE.findall(op) if is_tag(t)]
            if not found:
                plan.notes.append((n, s, "no country tag on the line"))
            target = {"justify": plan.justify, "declare": plan.declare, "peace": plan.peace}[verb]
            for t in found:
                target.setdefault(t, dict(when))
                if verb == "peace":
                    plan.annex[t] = dict(when, how="peace")
        elif verb == "research":
            m = re.match(r"research\s+slot\s+\d+\s+(\S+)", op)
            if not m:
                plan.notes.append((n, s, "research without a slot and a tech"))
            else:
                start = int(inline.group(1)) if inline else clock
                dur = re.search(r"->\s*~?(\d+)\s*days", comment)
                plan.research.append(dict(id=m.group(1), start=start, line=n,
                                          done=start + int(dur.group(1)) if dur else None))
        elif verb == "law":
            if len(words) > 1:
                plan.laws.append(dict(when, id=words[1]))
            else:
                plan.notes.append((n, s, "a law without an id"))
        elif verb == "decision":
            gift = re.match(r"decision\s+gift\s+of\s+the\s+(\w+)", op, re.I)
            if len(words) > 1 and DECISION_ID.match(words[1]):
                plan.decisions.setdefault(words[1], dict(when, id=words[1]))
            elif gift:
                gid = "mltd_gift_of_the_" + gift.group(1).lower()
                plan.decisions.setdefault(gid, dict(when, id=gid))
            elif re.match(r"decision\s+the\s+wet\s+market\b", op, re.I):
                plan.market = plan.market or dict(when)
            else:
                plan.untracked["decision (no id)"] += 1
        elif verb == "event":
            for t in re.findall(r"\b([A-Z][A-Z0-9]{2}) is annexed\b", s):
                if is_tag(t):
                    plan.annex[t] = dict(when, how="event")
            plan.untracked["event"] += 1
        elif verb in UNTRACKED:
            plan.untracked[verb] += 1
        else:
            plan.notes.append((n, s, "unknown verb %r" % words[0]))
    for snap_entry in plan.snapshots:
        if not any(k in snap_entry["metrics"] for k in ("states", "people", "divisions")):
            plan.notes.append((snap_entry["line"], snap_entry["text"],
                               "a snapshot with no states, people or divisions"))
    plan.end = int(max([clock, focus_free] + [f["done"] or 0 for f in plan.focuses]))
    return plan


def load_plan(path=PLAN):
    if not os.path.exists(path):
        plan = Plan()
        plan.notes.append((0, path, "the plan file does not exist"))
        return plan
    text = open(path, "rb").read().decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    plan = parse_plan(text, load_focus_costs(), load_country_tags())
    plan.path = path
    return plan


# ---- one run against the plan ---------------------------------------------------------------------------------
class Analysis(object):
    """Queries on one run. Every day here is a calendar day."""

    def __init__(self, run, plan):
        self.run, self.plan = run, plan
        self.by_kind = defaultdict(list)
        for ln in run.kept:
            self.by_kind[ln.kind].append(ln)
        self.snaps = self.by_kind["SNAP"]

    def find(self, kind, **match):
        return [ln for ln in self.by_kind.get(kind, ())
                if all(ln.get(k, "").upper() == str(v).upper() for k, v in match.items())]

    def first_day(self, kind, **match):
        hits = self.find(kind, **match)
        return hits[0].cal if hits else None

    def focus_day(self, fid):
        return self.first_day("FOCUS", id=fid)

    def war_starts(self, tag):
        return [ln.cal for ln in self.find("WAR_START", tag=tag)]

    def war_start(self, tag):
        starts = self.war_starts(tag)
        return starts[0] if starts else None

    def gone(self, tag):
        """(day, capital owner, capital) once tag no longer exists: its GONE line, else a WAR_END exists=no."""
        hits = self.find("GONE", tag=tag)
        if hits:
            owner = hits[0].get("owner")
            return hits[0].cal, None if (owner or "none").lower() == "none" else owner, hits[0].get("capital")
        ends = [ln for ln in self.find("WAR_END", tag=tag) if ln.get("exists", "").lower() == "no"]
        return (ends[0].cal, None, None) if ends else None

    def gone_day(self, tag):
        g = self.gone(tag)
        return g[0] if g else None

    def capitulated_day(self, tag):
        """The first monthly ENEMY line that found tag capitulated."""
        hits = [ln.cal for ln in self.find("ENEMY", tag=tag) if (ln.get("cap") or "").lower() == "yes"]
        return hits[0] if hits else None

    def beaten_day(self, tag):
        """Gone or capitulated, whichever came first (mltd_ai_ncr_beaten / mltd_ai_legion_beaten)."""
        days = [d for d in (self.gone_day(tag), self.capitulated_day(tag)) if d is not None]
        return min(days) if days else None

    def ritual(self, rid, state):
        hits = self.find("RITUAL", id=rid, state=state)
        return hits[0] if hits else None

    def goal_before(self, tag, day):
        """The first day MLT justified on or held a war goal against tag, if that was on or before day."""
        days = [ln.cal for ln in self.find("JUSTIFY", tag=tag) + self.find("WARGOAL", tag=tag) if ln.cal <= day]
        return min(days) if days else None

    def who_declared(self, tag, day):
        g = self.goal_before(tag, day)
        if g is not None:
            return " (MLT had a war goal from day %d)" % g
        return " (no MLT war goal logged first: %s may have declared)" % tag

    def snap_near(self, day, window=SNAP_MATCH_WINDOW):
        best = min(self.snaps, key=lambda s: (abs(s.cal - day), s.cal), default=None)
        return best if best is not None and abs(best.cal - day) <= window else None


def has_target(snap):
    v = (snap.get("cult_target") or "").strip()
    return bool(v) and v.lower() != "none" and parse_num(v) != 0


def cal(ln):
    return ln.cal if ln is not None else None


# ---- the automated checks: each returns (result, reason[, more to look at]) -----------------------------------
PASS, FAIL, NA = "PASS", "FAIL", "N/A"


def check_a(an):
    j, w, first, last = an.first_day("JUSTIFY", tag="CCW"), an.war_start("CCW"), an.run.first_day, an.run.last_day
    goals = [(d, why) for d, why in ((an.first_day("WARGOAL", tag="CCW"), "a war goal"),
                                     (w, "war")) if d is not None]
    g = min(goals) if goals else None
    if j is not None and j <= CCW_JUSTIFY_BY:
        return PASS, "justifying on CCW from day %d" % j
    if g is not None and g[0] <= CCW_WARGOAL_BY:
        return PASS, "%s on CCW from day %d%s" % (g[1], g[0], "" if j is None else "; justifying from day %d" % j)
    if j is not None or g is not None:
        late = []
        if j is not None:
            late.append("justifying from day %d" % j)
        if g is not None:
            late.append("%s from day %d" % (g[1], g[0]))
        return FAIL, "late on CCW: %s" % "; ".join(late)
    if first > CCW_JUSTIFY_BY:
        return NA, "the run starts on day %d (no START: continued from a save)" % first
    if an.gone_day("CCW") is not None and an.gone_day("CCW") <= CCW_WARGOAL_BY:
        return NA, "CCW was gone by day %d" % an.gone_day("CCW")
    if last < CCW_WARGOAL_BY:
        return NA, "the run ends on day %d, before day %d" % (last, CCW_WARGOAL_BY)
    return FAIL, "no justification, war goal or war on CCW by day %d" % CCW_WARGOAL_BY


def check_b(an):
    seen = [(t, an.war_start(t)) for t in EARLY_WARS if an.war_start(t) is not None]
    if len(seen) < 2:
        return NA, "only %s of the CCW, TRL, RBT and MDT wars happened" % (" and ".join(t for t, _ in seen) or "none")
    bad = ["%s (day %d) before %s (day %d)%s" % (b, db, a, da, an.who_declared(b, db))
           for i, (a, da) in enumerate(seen) for b, db in seen[i + 1:] if db < da]
    if bad:
        return FAIL, "; ".join(bad)
    return PASS, "wars began " + ", ".join("%s day %d" % td for td in seen)


def check_c(an):
    plan_day, k, last = an.plan.done("mlt_kingdom_of_mlyeh"), an.focus_day("mlt_kingdom_of_mlyeh"), an.run.last_day
    if k is not None:
        return PASS, "completed on day %d%s" % (
            k, " (plan day %d, %s)" % (plan_day, fmt_delta(k, plan_day)) if plan_day is not None else "")
    if plan_day is not None and last < plan_day:
        return NA, "the run ends on day %d, before the plan's day %d" % (last, plan_day)
    why = []
    if an.focus_day("ritual_of_black_hollows_night") is None:
        why.append("Black Hollows Night (the eggs) not done")
    standing = [t for t in ("CCW", "TRL", "RBT", "DIS") if an.gone_day(t) is None]
    if standing:
        why.append("still standing: " + ", ".join(standing))
    return FAIL, "not completed by day %d (plan day %s)%s" % (
        last, fmt_num(plan_day), "; " + "; ".join(why) if why else "")


def check_d(an):
    books = [(s.cal, s.num("books")) for s in an.snaps if s.num("books") is not None]
    five = next((d for d, b in books if b >= 5), None)
    if five is not None:
        return PASS, "books=5 from the SNAP of day %d" % five
    missing = [(i + 1, state, tag) for i, (fid, state, tag) in enumerate(BOOKS) if an.focus_day(fid) is None]
    if not books and not missing:
        return PASS, "no SNAP carries books=, but all five Book focuses are done (the last on day %d)" % max(
            an.focus_day(fid) for fid, _, _ in BOOKS)
    due = an.plan.done(BOOKS[-1][0])
    due = due + BOOK_EXPEDITION_DAYS if due is not None else None
    have = "%s read at the SNAP of day %d" % (fmt_num(books[-1][1]), books[-1][0]) if books else \
        "no SNAP carries books="
    todo = "; Book focuses not taken: " + ", ".join("Book %d (%s, %s's at start)" % m for m in missing) \
        if missing else ""
    look = " / ".join("`mltd_ai_conquer_%s`" % tag.lower() for _, _, tag in missing)
    if due is not None and an.run.last_day < due:
        return NA, "the run ends on day %d, before the plan's fifth Book (~day %d); %s" % (an.run.last_day, due, have)
    return FAIL, have + todo, look


def check_e(an):
    s, e = an.ritual("final", "start"), an.ritual("final", "end")
    if s is None:
        return NA, "the Final Ritual never started"
    end = cal(e)
    span = "days %d-%s" % (s.cal, end if end is not None else "%d, still running" % an.run.last_day)
    bad = [ln for ln in an.by_kind.get("WAR_START", ()) if ln.cal >= s.cal and (end is None or ln.cal < end)]
    if bad:
        return FAIL, "%s during the Final Ritual (%s); WAR_START also counts an enemy that joins or declares" % (
            ", ".join("%s day %d%s" % (ln.get("tag", "?"), ln.cal, an.who_declared(ln.get("tag", "?"), ln.cal))
                      for ln in bad), span)
    return PASS, "no war began during the Final Ritual (%s)" % span


def check_f(an):
    bad, state = [], []
    for group, anchor, until in ((INTERIOR, "NCR", INTERIOR_UNTIL), (SOUTH, "CES", SOUTH_UNTIL)):
        limit, g = day_of(*until), an.beaten_day(anchor)
        if g is not None:
            limit = min(limit, g)
        state.append("%s %s" % (anchor, "beaten on day %d" % g if g is not None else "standing"))
        bad += ["%s day %d%s" % (t, d, an.who_declared(t, d)) for t in group for d in an.war_starts(t) if d < limit]
    if bad:
        return FAIL, "war on %s before its hold lifted (%s; the holds lift on %s and %s)" % (
            ", ".join(bad), ", ".join(state), iso(day_of(*INTERIOR_UNTIL)), iso(day_of(*SOUTH_UNTIL)))
    return PASS, "no early war on %s or %s (%s; the run ends on day %d)" % (
        "/".join(INTERIOR), "/".join(SOUTH), ", ".join(state), an.run.last_day)


def check_g(an):
    lar = an.run.info("lar", None)
    if lar is None:
        return NA, "no START line, so La Resistance is unknown"
    if lar.lower() != "yes":
        return NA, "La Resistance is off (lar=%s)" % lar
    f = an.focus_day("mltd_the_spreading_cult")
    if f is None:
        return NA, "The Spreading Cult was not completed"
    due = f + CULT_TARGET_WITHIN
    early = [s for s in an.snaps if f <= s.cal <= due and has_target(s)]
    if early:
        return PASS, "cult_target=%s on day %d, %d days after The Spreading Cult (day %d)" % (
            early[0].get("cult_target"), early[0].cal, early[0].cal - f, f)
    after = next((s for s in an.snaps if s.cal >= due), None)
    if after is None:
        return NA, "no SNAP %d or more days after The Spreading Cult (day %d)" % (CULT_TARGET_WITHIN, f)
    if "cult_target" not in after.kv:
        return NA, "the SNAP of day %d carries no cult_target=" % after.cal
    if not has_target(after):
        return FAIL, "cult_target=%s on day %d, %d days after The Spreading Cult (day %d)" % (
            after.get("cult_target") or "none", after.cal, after.cal - f, f)
    return PASS, "cult_target=%s on day %d, the first SNAP %d+ days after The Spreading Cult (day %d; SNAPs are " \
                 "monthly)" % (after.get("cult_target"), after.cal, CULT_TARGET_WITHIN, f)


def check_h(an):
    vals = [(s.cal, s.num("subjects")) for s in an.snaps if s.num("subjects") is not None]
    if not vals:
        return NA, "no SNAP carries subjects="
    bad = [(d, v) for d, v in vals if v > 0]
    if bad:
        return FAIL, "subjects=%s first on day %d (at most %s)" % (
            fmt_num(bad[0][1]), bad[0][0], fmt_num(max(v for _, v in bad)))
    return PASS, "subjects=0 in all %d SNAPs" % len(vals)


def check_i(an):
    rule = an.run.info("caps_rule", None)
    if rule is not None and rule.lower() == "no":
        return NA, "the caps rule is off, and the Wet Market's AI buyer spends caps"
    f = an.focus_day("mltd_the_wet_market")
    if f is None:
        return NA, "The Wet Market was not completed"
    trades = [ln.cal for ln in an.by_kind.get("MARKET", ()) if ln.cal >= f]
    if trades:
        return PASS, "first trade on day %d, %d days after the focus; %d trade(s)" % (trades[0], trades[0] - f,
                                                                                     len(trades))
    if an.run.last_day - f < MARKET_GRACE:
        return NA, "the run ends %d days after The Wet Market (day %d)" % (an.run.last_day - f, f)
    caps = [s.num("caps") for s in an.snaps if s.cal >= f and s.num("caps") is not None]
    return FAIL, "no trade in the %d days after The Wet Market (day %d)%s; the AI buyer needs over 300 caps and " \
                 "under 250 mirelurks in stock" % (an.run.last_day - f, f,
                                                   "; caps peaked at %s" % fmt_num(max(caps)) if caps else "")


def check_j(an):
    gs, ge, fs = an.ritual("grand", "start"), an.ritual("grand", "end"), an.ritual("final", "start")
    (_, grand_gate, grand), (_, final_gate, final) = RITUAL_GATES
    judged, bad, during, deep, after, nopop = 0, [], 0, 0, 0, 0
    for ln in an.by_kind.get("DECISION", ()):
        if ln.get("id") not in POPULATION_DECISIONS:
            continue
        if gs is None or ln.cal < gs.cal:
            gate, name = grand_gate, grand
        elif ge is None or ln.cal < ge.cal:
            during += 1                 # the AI guards the Final Ritual's gate only once the Grand Ritual is over
            continue
        elif fs is None or ln.cal < fs.cal:
            if ln.get("id") == "mltd_summon_the_deep_ones":
                deep += 1               # its AI guards only the Grand Ritual's gate; mltd.8 hides it at the Walk
                continue
            gate, name = final_gate, final
        else:
            after += 1
            continue
        pop = ln.num("pop_k")
        if pop is None:
            nopop += 1
            continue
        judged += 1
        if pop < gate:
            bad.append("%s on day %d left %sk (the %s needs %sk)" % (ln.get("id"), ln.cal, fmt_num(pop), name,
                                                                     fmt_num(gate)))
    skipped = [x for x in ("%d during the Grand Ritual" % during if during else "",
                           "%d Deep Ones summon(s) after it (their AI guards only the Grand Ritual's gate)" % deep
                           if deep else "",
                           "%d after the Final Ritual began" % after if after else "",
                           "%d without pop_k=" % nopop if nopop else "") if x]
    tail = "; not judged: " + ", ".join(skipped) if skipped else ""
    if not judged:
        return NA, "no summon or offering was taken while a ritual lay ahead" + tail
    if bad:
        return FAIL, "; ".join(bad) + tail
    return PASS, "all %d taken at or above the next ritual's gate%s" % (judged, tail)


def check_k(an):
    schism = (an.run.info("schism", "") or "").lower()
    if an.run.start is None:
        return NA, "no START line, so the schism flag is unknown"
    if schism not in ("yes", "no"):
        return NA, "schism=%s: DIS did not exist at the start" % (schism or "?")
    wars, g, last, deadline = an.war_starts("DIS"), an.gone("DIS"), an.run.last_day, day_of(*DIS_OFFER_UNTIL)
    owner = " (its capital is held by %s)" % g[1] if g and g[1] else ""
    if schism == "yes":
        if wars and wars[0] < deadline:
            return FAIL, "war on DIS on day %d%s, before %s; a war cancels DIS's offer (nf_dis.4) - unless DIS had " \
                         "taken lake_preemptive_defenses, which the telemetry does not log" % (
                             wars[0], an.who_declared("DIS", wars[0]), iso(deadline))
        if wars:
            return PASS, "no offer taken by %s: war on DIS from day %d, `mltd_ai_conquer_dis`'s fallback" % (
                iso(deadline), wars[0])
        if g and g[1] and g[1].upper() != "MLT":
            return FAIL, "DIS gone on day %d without a war, but not to MLT%s" % (g[0], owner)
        if g:
            return PASS, "DIS gone on day %d without a war%s" % (g[0], owner)
        if last < deadline:
            return NA, "DIS still stands on day %d; the offer can come until %s" % (last, iso(deadline))
        return FAIL, "DIS still stands on day %d, with no war and no offer taken" % last
    if wars:
        return PASS, "war on DIS from day %d" % wars[0]
    if g:
        return FAIL, "DIS gone on day %d without a war with MLT%s" % (g[0], owner)
    if last < deadline:
        return NA, "no war on DIS by day %d, before the fallback date %s" % (last, iso(deadline))
    return FAIL, "no war on DIS by day %d" % last


def lar_na(an):
    """N/A for a run without La Resistance (or without a START line to say), else None."""
    lar = an.run.info("lar", None)
    if lar is None:
        return NA, "no START line, so La Resistance is unknown"
    if lar.lower() != "yes":
        return NA, "La Resistance is off (lar=%s)" % lar
    return None


def check_l(an):
    ncr, north = an.war_start("NCR"), an.first_day("STAGE", id="north")
    if not an.by_kind.get("STAGE"):
        return NA, "no STAGE lines (telemetry from before round 20)"
    if ncr is None:
        return NA, "no war with the NCR%s" % ("; the north was consolidated on day %d" % north if north is not None else "")
    if north is None or ncr < north:
        return FAIL, "war with the NCR from day %d%s, %s" % (
            ncr, an.who_declared("NCR", ncr), "before the north was consolidated (day %d)" % north
            if north is not None else "and the north was never consolidated")
    return PASS, "the north consolidated on day %d, the NCR war from day %d" % (north, ncr)


def check_m(an):
    pockets, start = [], None
    for ln in an.by_kind.get("POCKET", ()):
        state = (ln.get("state") or "").lower()
        if state == "start" and start is None:
            start = ln.cal
        elif state == "end" and start is not None:
            pockets.append((start, ln.cal))
            start = None
    if start is not None:
        pockets.append((start, None))
    cut = sorted(set(ln.get("tag", "?") for ln in an.by_kind.get("ENEMY", ())
                     if (ln.get("cap") or "").lower() == "no" and (ln.get("reach") or "").lower() == "no"
                     and (ln.num("states") or 0) > 0))
    who = "; out of reach at a monthly ENEMY line: " + ", ".join(cut) if cut else ""
    if not pockets:
        if not an.by_kind.get("ENEMY"):
            return NA, "no ENEMY or POCKET lines (no war, or telemetry from before round 20)"
        return PASS, "no enemy was out of reach at a weekly survey%s" % who
    last = an.run.last_day
    spans = ", ".join("days %d-%s" % (s, e if e is not None else "%d, still open" % last) for s, e in pockets)
    if any(((e if e is not None else last) - s) > POCKET_LIMIT for s, e in pockets):
        return FAIL, "an enemy out of reach for over %d days (%s)%s" % (POCKET_LIMIT, spans, who)
    return PASS, "every pocket closed within %d days (%s)%s" % (POCKET_LIMIT, spans, who)


def check_n(an):
    na = lar_na(an)
    if na:
        return na
    ncr = an.war_start("NCR")
    if ncr is None:
        return NA, "no war with the NCR"
    cults = [ln for ln in an.find("CULT", tag="NCR") if ncr - SNAP_MATCH_WINDOW <= ln.cal <= ncr]
    if not cults:
        return FAIL, "no cult in the NCR in the %d days before its war (day %d)" % (SNAP_MATCH_WINDOW, ncr)
    st = cults[-1].num("str")
    if st is not None and st >= NCR_CULT_READY:
        return PASS, "the NCR's cult at %s on day %d; the war from day %d" % (fmt_num(st), cults[-1].cal, ncr)
    return FAIL, "the NCR's cult at %s on day %d, under %d; the war from day %d" % (
        fmt_num(st), cults[-1].cal, NCR_CULT_READY, ncr)


def check_o(an):
    na = lar_na(an)
    if na:
        return na
    f = an.focus_day("mltd_the_spreading_cult")
    if f is None:
        return NA, "The Spreading Cult, which founds the agency, was not completed"
    a = an.first_day("ADVISOR", id="MLT_OLD_CASTRO")
    if a is not None:
        return (PASS if a <= f + CASTRO_WITHIN else FAIL), "hired on day %d, %d days after The Spreading Cult (day %d)" % (
            a, a - f, f)
    if not an.by_kind.get("ADVISOR") and not an.by_kind.get("STAGE"):
        return NA, "no ADVISOR lines (telemetry from before round 20)"
    if an.run.last_day - f < CASTRO_WITHIN:
        return NA, "not hired yet; the run ends %d days after The Spreading Cult" % (an.run.last_day - f)
    return FAIL, "never hired in the %d days after The Spreading Cult (day %d)" % (an.run.last_day - f, f)


def check_p(an):
    snaps = [s for s in an.snaps if (s.num("target") or 0) > 0 and s.num("divs") is not None]
    if not snaps:
        return NA, "no SNAP carries target= (telemetry from before round 20, or a human MLT)"
    recent = [s for s in snaps if s.cal >= snaps[-1].cal - ARMY_WINDOW]
    ratios = sorted(s.num("divs") / s.num("target") for s in recent)
    median, last = ratios[len(ratios) // 2], recent[-1]
    text = "divisions / target over %d SNAP(s) in the last %d days: median %.2f (%.2f-%.2f); day %d: %s of %s" % (
        len(recent), ARMY_WINDOW, median, ratios[0], ratios[-1], last.cal, fmt_num(last.num("divs")),
        fmt_num(last.num("target")))
    return (PASS if ARMY_RANGE[0] <= median <= ARMY_RANGE[1] else FAIL), text


def check_q(an):
    e = an.ritual("final", "end")
    if e is None:
        return NA, "the Final Ritual was not completed"
    bad, fine = [], 0
    for ln in an.by_kind.get("DECISION", ()):
        if ln.cal < e.cal:
            continue
        if ln.get("id") == "mltd_offering_of_the_drowned":
            caps = ln.num("caps")
            if caps is not None and caps >= OFFERING_CAPS_AFTER:
                bad.append("the Drowned on day %d (%s caps after it)" % (ln.cal, fmt_num(caps)))
            else:
                fine += 1
        elif ln.get("id") == "mltd_offering_of_the_tides":
            pop = ln.num("pop_k")
            if pop is not None and pop < TIDES_POP_K:
                bad.append("the Tides on day %d (%sk people)" % (ln.cal, fmt_num(pop)))
            else:
                fine += 1
    if bad:
        return FAIL, "%d offering(s) after the Final Ritual (day %d) without the need: %s" % (
            len(bad), e.cal, "; ".join(bad[:5]) + ("; ..." if len(bad) > 5 else ""))
    return PASS, "%d offering(s) after the Final Ritual (day %d), each when caps were short or people plenty" % (
        fine, e.cal)


CHECKS = (
    # key, runs.csv column, what, check, the AI block to look at
    ("a", "a_justify_ccw", "MLT moves on CCW: justifying by day %d, or a war goal or war by day %d" % (CCW_JUSTIFY_BY, CCW_WARGOAL_BY), check_a,
     "`mltd_ai_conquer_ccw` (common/ai_strategy/mltd_MLT.txt)"),
    ("b", "b_war_order", "The early wars start in the plan's order: CCW, TRL, RBT, MDT", check_b,
     "the `enable` stages of `mltd_ai_conquer_ccw` / `_trl` / `_rbt` / `_mdt`"),
    ("c", "c_kingdom", "The Kingdom of M'lyeh is completed", check_c,
     "the focus plan `mltd_MLT_oregon_opening` (common/ai_strategy_plans/mltd_MLT.txt); the CCW, TRL, RBT and DIS "
     "conquests"),
    ("d", "d_books", "All five Books are read", check_d,
     "the focus plan `mltd_MLT_kingdom_and_books`; the conquests of the Books' states"),
    ("e", "e_ritual_peace", "No war begins while the Final Ritual runs", check_e,
     "the stage conditions of `mltd_ai_conquer_*`; `mltd_ai_stay_on_plan`"),
    ("f", "f_holds", "No war on CES/BOS/WHT/EHT/HEA before the NCR is beaten (or 2283), nor on TBH/LNS/TLA/MAX/MOC/ZAP "
     "before the Legion is (or 2286)", check_f, "`mltd_ai_hold_late_wargoals` / `mltd_ai_hold_south_wargoals`"),
    ("g", "g_cult_target", "A cult target within %d days of The Spreading Cult (La Resistance)" % CULT_TARGET_WITHIN,
     check_g, "the target pick in `on_weekly_MLT` (common/on_actions/mltd_on_actions.txt) and "
     "`mltd_ai_cult_target_scorer`; `mltd_ai_cult_found` / `mltd_ai_cult_nurture`"),
    ("h", "h_no_subjects", "MLT never holds a subject", check_h,
     "`mltd_mlt_no_puppets` (common/peace_conference/ai_peace/mltd_MLT_peace.txt)"),
    ("i", "i_market", "The Wet Market is used after its focus", check_i,
     "the AI buyer at the end of `on_weekly_MLT` (common/on_actions/mltd_on_actions.txt)"),
    ("j", "j_ritual_gates", "Summons and offerings keep the next ritual's population gate (100k, then 200k)", check_j,
     "the summons' and offerings' `ai_will_do` (common/decisions/mltd_decisions.txt)"),
    ("k", "k_dis_path", "DIS: annexed through its offer with the schism flag, conquered without it", check_k,
     "`mltd_ai_spare_dis` / `mltd_ai_conquer_dis`"),
    ("l", "l_north_first", "The NCR war starts only once the north is consolidated", check_l,
     "`mltd_ai_stage_ncr` and `mltd_ai_north_done` (common/scripted_triggers/mltd_ai_triggers.txt); `mltd_ai_hold_ncr_side_*`"),
    ("m", "m_pockets", "No enemy stays out of MLT's reach for over %d days" % POCKET_LIMIT, check_m,
     "`mltd_ai_access_*` and the frontier conquests (common/ai_strategy/mltd_MLT_frontier.txt); `mltd_ai_new_reno_first`"),
    ("n", "n_ncr_cult", "The NCR's cult stands at %d %% or more when that war starts (La Resistance)" % NCR_CULT_READY,
     check_n, "`mltd_ai_cult_target_scorer`; `mltd_ai_cult_found` / `mltd_ai_cult_nurture`; `mltd_ai_ncr_cult_ready`"),
    ("o", "o_castro", "Old Castro is hired within %d days of The Spreading Cult (La Resistance)" % CASTRO_WITHIN, check_o,
     "`mltd_ai_save_for_castro`; his `ai_will_do` (common/characters/MLT.txt) and the plans' `ideas`"),
    ("p", "p_army_size", "The army stays at %.2f-%.2fx its target over the last %d days" % (
        ARMY_RANGE[0], ARMY_RANGE[1], ARMY_WINDOW), check_p,
     "`mltd_ai_army_short` / `mltd_ai_army_full`; the target in `mltd_ai_survey` (mltd_ai_survey_effects.txt)"),
    ("q", "q_offerings", "After the Final Ritual, offerings only when caps are short or people plentiful", check_q,
     "the offerings' `ai_will_do` (common/decisions/mltd_decisions.txt)"),
)


def run_checks(an):
    out = []
    for key, column, what, fn, look in CHECKS:
        try:
            got = fn(an)
        except Exception as exc:                 # a broken check must not cost the rest of the report
            got = ("ERROR", "%s: %s" % (type(exc).__name__, exc))
        more = got[2] if len(got) > 2 and got[2] else ""
        out.append(dict(key=key, column=column, what=what, result=got[0], reason=got[1],
                        look=look + ("; " + more if more else "")))
    return out


def milestones(an):
    """The days runs.csv keeps, so iterations can be compared."""
    return (("ccw_war", an.war_start("CCW")), ("trl_war", an.war_start("TRL")),
            ("kingdom", an.focus_day("mlt_kingdom_of_mlyeh")),
            ("grand_ritual_end", cal(an.ritual("grand", "end"))), ("final_ritual_end", cal(an.ritual("final", "end"))),
            ("north", an.first_day("STAGE", id="north")), ("ncr_war", an.war_start("NCR")),
            ("ncr_capitulated", an.capitulated_day("NCR")), ("ncr_gone", an.gone_day("NCR")))


# ---- the report ------------------------------------------------------------------------------------------------
LOGGED_DECISIONS = POPULATION_DECISIONS + ("mltd_cult_call_for_people", "mltd_cult_call_for_equipment")
BOOK_NAMES = dict((fid, "Book %d" % (i + 1)) for i, (fid, _, _) in enumerate(BOOKS))


def md_table(header, rows, align=None):
    align = align or "l" * len(header)
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---:" if a == "r" else "---" for a in align) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows]
    return out


def pday(it):
    """A plan day: '591', or '~200' when it comes from the plan's estimate comments."""
    if it is None:
        return "-"
    if isinstance(it, dict):
        return ("~%d" if it.get("approx") else "%d") % it["day"]
    return fmt_num(it)


def adays(days):
    if not days:
        return "-"
    return "%d" % days[0] + (" (x%d)" % len(days) if len(days) > 1 else "")


def plan_text(rng):
    lo, hi, approx = rng
    return ("~" if approx else "") + (fmt_num(lo) if lo == hi else "%s-%s" % (fmt_num(lo), fmt_num(hi)))


def compare(rng, value):
    """'12-15 / 11 (-8%)': the plan's range, the run's value, and how far outside the range it is."""
    lo, hi = rng[0], rng[1]
    if value is None:
        return plan_text(rng) + " / -"
    if lo <= value <= hi:
        verdict = "ok"
    else:
        bound = lo if value < lo else hi
        verdict = "%+d%%" % round((value - bound) * 100.0 / bound) if bound else \
            ("+" if value > bound else "") + fmt_num(value - bound)
    return "%s / %s (%s)" % (plan_text(rng), fmt_num(value), verdict)


def snap_iso(s):
    d = parse_game_date(s.get("date"))
    return iso(d if d is not None else s.cal)


def cult_series(an):
    """Timeline entries for cults that take root or vanish, and per-country (first, peak, last) (day, str)."""
    by_day = defaultdict(dict)
    for ln in an.by_kind.get("CULT", ()):
        by_day[ln.cal][ln.get("tag", "?")] = ln.num("str")
    events, stats, prev = [], {}, {}
    for d in sorted(set(by_day) | set(s.cal for s in an.snaps)):
        cur = by_day.get(d, {})
        for tag, st in cur.items():
            if tag not in prev:
                events.append((d, "CULT %s takes root (str %s)" % (tag, fmt_num(st))))
            s = stats.setdefault(tag, dict(first=(d, st), peak=(d, st), last=(d, st)))
            if st is not None and (s["peak"][1] is None or st > s["peak"][1]):
                s["peak"] = (d, st)
            s["last"] = (d, st)
        for tag in prev:
            if tag not in cur:
                events.append((d, "CULT %s is gone (last seen at str %s)" % (tag, fmt_num(prev[tag]))))
        prev = cur
    return events, stats


def describe(ln, an):
    """One timeline entry's text."""
    k, plan, tag = ln.kind, an.plan, ln.get("tag", "?")
    if k == "FOCUS":
        fid = ln.get("id", "?")
        done = plan.done(fid)
        return "FOCUS %s%s" % (fid, " (plan %d, %s)" % (done, fmt_delta(ln.cal, done)) if done is not None
                               else " (not in the plan)")
    if k in ("JUSTIFY", "WARGOAL", "WAR_START"):
        ref = (plan.declare if k == "WAR_START" else plan.justify).get(tag)
        return "%s %s%s" % (k, tag, " (plan %s)" % pday(ref) if ref else "")
    if k == "WAR_END":
        return "WAR_END %s%s" % (tag, ": it no longer exists" if ln.get("exists", "").lower() == "no" else "")
    if k == "GONE":
        owner = ln.get("owner") or "none"
        return "GONE %s: its last capital, %s, is %s" % (tag, ln.get("capital") or "?",
                                                         "unowned" if owner.lower() == "none" else "%s's" % owner)
    if k in ("TECH", "LAW", "GIFT"):
        return "%s %s" % (k, ln.get("id", "?"))
    if k == "RITUAL":
        return "RITUAL %s %s, %sk people" % (ln.get("id", "?"), ln.get("state", "?"), ln.get("pop_k", "?"))
    if k == "DECISION":
        rest = " ".join("%s=%s" % kv for kv in ln.kv.items() if kv[0] not in ("id", "date"))
        return "DECISION %s%s" % (ln.get("id", "?"), " (" + rest + ")" if rest else "")
    if k == "STAGE":
        sid = ln.get("id", "?")
        return "STAGE north: the north is consolidated" if sid == "north" else "STAGE %s opens" % sid
    if k == "POCKET":
        state = (ln.get("state") or "?").lower()
        return {"start": "POCKET: an enemy is out of MLT's reach", "end": "POCKET closed"}.get(state, "POCKET %s" % state)
    if k == "ADVISOR":
        return "ADVISOR %s hired" % ln.get("id", "?")
    if k not in KINDS:
        return "%s %s (unknown kind)" % (k, ln.text())
    return ("%s %s" % (k, ln.text())).strip()


def summary_rows(runs, run, bad):
    rows = []
    who = run.info("ai", None)
    rows.append(("MLT played by", {"yes": "the AI (ai=yes)", "no": "a human (ai=no)"}.get(
        (who or "").lower(), "unknown: no START line" if who is None else "ai=%s" % who)))
    rows.append(("La Resistance", run.info("lar")))
    rows.append(("Caps rule", run.info("caps_rule")))
    rows.append(("DIS schism flag", run.info("schism")))
    rows.append(("Telemetry version", run.info("v")))
    rows.append(("First line", "day %d, %s" % (run.first_day, iso(run.first_day))))
    rows.append(("Last line", "day %d, %s" % (run.last_day, iso(run.last_day))))
    extra = []
    if run.folded:
        extra.append("%d identical line(s) folded" % run.folded)
    for frm, to, lineno, dropped in run.reloads:
        extra.append("a save reloaded at game.log line %d (counter %d back to %d): %d later line(s) dropped"
                     % (lineno, frm, to, dropped))
    rows.append(("Lines", "%d kept%s" % (len(run.kept), "; " + "; ".join(extra) if extra else "")))
    if run.offset_source is None:
        rows.append(("Day counter", "no date to calibrate against: days are the counter's own"))
    else:
        text = "calibrated on %s: calendar day = counter %s" % (
            run.offset_source, "%+d" % run.offset if run.offset else "(no offset)")
        if run.start is not None and run.start.cal != run.start.day + run.offset:
            text += "; START keeps its own date, day %d (it is written before the counter's first +1)" % run.start.cal
        rows.append(("Day counter", text))
    if run.clock_mismatch:
        rows.append(("Clock check", "%d line(s) disagree with the date game.log gives them" % run.clock_mismatch))
    kinds = Counter(ln.kind for ln in run.kept)
    rows.append(("Kinds", ", ".join("%s %d" % (k, kinds[k]) for k in KINDS if kinds[k]) or "-"))
    unknown = sorted(k for k in kinds if k not in KINDS)
    if unknown:
        rows.append(("Unknown kinds", ", ".join("%s %d" % (k, kinds[k]) for k in unknown)))
    if bad:
        rows.append(("Malformed", "%d MLTD line(s) in the log break the contract, e.g. game.log line %d: `%s`"
                     % (len(bad), bad[0][0], bad[0][1][:80])))
    rows.append(("Runs in the log", "%d; this is run %d" % (len(runs), run.index)))
    return rows


def plan_sections(plan, an=None):
    """The plan's timeline, set against the run when there is one."""
    out = []
    ai = an is not None
    # focuses
    rows, seen = [], set()
    for f in plan.focuses:
        if f["id"] in seen:
            continue
        seen.add(f["id"])
        if ai:
            d = an.focus_day(f["id"])
            due = f["done"] is not None and an.run.last_day >= f["done"]
            rows.append((f["id"], f["start"], fmt_num(f["done"]), fmt_num(d) if d is not None else
                         "not done" if due else "-", fmt_delta(d, f["done"])))
        else:
            rows.append((f["id"], f["start"], fmt_num(f["done"]), fmt_num(f["cost"]), f["line"]))
    out += ["### Focuses", ""]
    out += md_table(("Focus", "Plan start", "Plan done", "AI done", "Delta") if ai else
                    ("Focus", "Start", "Done", "Days", "Plan line"), rows, "lrrrr")
    if ai:
        extra = [ln for ln in an.by_kind.get("FOCUS", ()) if ln.get("id") not in plan.focus]
        out += ["", "AI focuses the plan does not take, in order: " +
                (", ".join("%s (%d)" % (ln.get("id", "?"), ln.cal) for ln in extra) or "none") + ".",
                "", "The AI's day is the weekly poll that first saw the focus done, up to 6 days after it."]
    # wars
    tags = sorted(set(plan.declare) | set(plan.justify),
                  key=lambda t: ((plan.declare.get(t) or plan.justify[t])["day"], t))
    if ai:
        logged = set(ln.get("tag") for ln in an.by_kind.get("WAR_START", ())) - {None}      # a line may lack tag=
        tags += sorted((t for t in logged if t not in tags), key=lambda t: (an.war_start(t), t))
    rows = []
    for t in tags:
        pj, pw = plan.justify.get(t), plan.declare.get(t)
        if ai:
            ws = an.war_starts(t)
            ends = [ln.cal for ln in an.find("WAR_END", tag=t)]
            rows.append((t, pday(pj), adays([ln.cal for ln in an.find("JUSTIFY", tag=t)]), pday(pw), adays(ws),
                         fmt_delta(ws[0] if ws else None, pw["day"] if pw else None), adays(ends)))
        else:
            rows.append((t, pday(pj), pday(pw), pday(plan.annex.get(t))))
    out += ["", "### Wars", ""]
    out += md_table(("Tag", "Plan justify", "AI justify", "Plan war", "AI war", "Delta", "AI war end") if ai else
                    ("Tag", "Justify", "War", "Annexed"), rows, "lrrrrrr" if ai else "lrrr")
    out += ["", "A `~` day is the plan's own estimate comment; the others run on its clock. (xN): it happened N times."]
    if ai and an.by_kind.get("ENEMY"):
        per = {}
        for ln in an.by_kind["ENEMY"]:
            d = per.setdefault(ln.get("tag", "?"), dict(first=ln.cal, cap=None, out=0, last=ln))
            cap, reach = (ln.get("cap") or "").lower(), (ln.get("reach") or "").lower()
            if cap == "yes" and d["cap"] is None:
                d["cap"] = ln.cal
            if cap == "no" and reach == "no" and (ln.num("states") or 0) > 0:
                d["out"] += 1
            d["last"] = ln
        rows = [(tag, d["first"], fmt_num(d["cap"]), d["out"], "%d: %s state(s), cap=%s, reach=%s" % (
                    d["last"].cal, d["last"].get("states", "?"), d["last"].get("cap", "?"), d["last"].get("reach", "?")))
                for tag, d in sorted(per.items(), key=lambda kv: (kv[1]["first"], kv[0]))]
        out += ["", "### Enemies", ""]
        out += md_table(("Tag", "First seen", "Capitulated", "Months out of reach", "Last seen"), rows, "lrrrl")
        out += ["", "From the monthly ENEMY lines: each country at war with MLT, whether it has capitulated, the states it "
                "controls, and whether any of them touches land MLT controls (reach)."]
    if ai and an.by_kind.get("STAGE"):
        out += ["", "Stages opened (STAGE, first seen): " + ", ".join(
            "%s %d" % (ln.get("id", "?"), ln.cal) for ln in an.by_kind["STAGE"]) + "."]
    # annexations
    if ai:
        gone = set(ln.get("tag") for ln in an.by_kind.get("GONE", ())) | set(
            ln.get("tag") for ln in an.by_kind.get("WAR_END", ()) if ln.get("exists", "").lower() == "no")
        gone.discard(None)
        tags = sorted(set(plan.annex), key=lambda t: (plan.annex[t]["day"], t))
        tags += sorted((t for t in gone if t not in plan.annex), key=lambda t: (an.gone_day(t), t))
        rows = []
        for t in tags:
            g = an.gone(t)
            cap = "-" if not g else "%s: %s" % (g[2] or "?", g[1] or "unowned") if g[2] else (g[1] or "-")
            rows.append((t, pday(plan.annex.get(t)), fmt_num(g[0]) if g else "-",
                         fmt_delta(g[0] if g else None, plan.annex[t]["day"] if t in plan.annex else None), cap))
        out += ["", "### Annexations", ""]
        out += md_table(("Tag", "Plan", "AI gone", "Delta", "Last capital: owner now"), rows, "lrrrl")
    # snapshots
    rows = []
    for s in plan.snapshots:
        m = s["metrics"]
        if ai:
            near = an.snap_near(s["day"])
            if near is None:
                rows.append((s["day"], iso(s["day"]), "no SNAP within %d days" % SNAP_MATCH_WINDOW, "", "", "", ""))
                continue
            main = dict((metric, compare(m[metric], near.num(key))) for metric, key in METRIC_KEYS[:3] if metric in m)
            other = ", ".join("%s %s" % (metric, compare(m[metric], near.num(key))) for metric, key in METRIC_KEYS[3:]
                              if metric in m and near.num(key) is not None)
            rows.append((s["day"], iso(s["day"]), "%d (%s)" % (near.cal, snap_iso(near)), main.get("states", "-"),
                         main.get("people", "-"), main.get("divisions", "-"), other or "-"))
        else:
            cell = lambda k: plan_text(m[k]) if k in m else "-"
            other = ", ".join("%s %s" % (k, plan_text(m[k])) for k, _ in METRIC_KEYS[3:] if k in m)
            rows.append((s["day"], iso(s["day"]), cell("states"), cell("people"), cell("divisions"), other or "-",
                         s["line"]))
    out += ["", "### Snapshots", ""]
    if ai:
        out += md_table(("Plan day", "Date", "AI SNAP", "States: plan / AI", "People (k)", "Divisions", "Other"),
                        rows, "rllllll")
        out += ["", "Each plan snapshot against the run's nearest SNAP: `ok` inside the plan's range, else the "
                "distance from its nearer end. States are owned states; manpower is free manpower in thousands."]
    else:
        out += md_table(("Day", "Date", "States", "People (k)", "Divisions", "Other", "Plan line"), rows, "rllllll")
    # rituals
    rows = []
    for rid, name, fid in (("grand", "Grand Ritual", "mltd_the_grand_ritual"),
                           ("final", "Final Ritual", "mltd_the_final_ritual")):
        if ai:
            s, e = an.ritual(rid, "start"), an.ritual(rid, "end")
            rows.append((name, fmt_num(plan.begun(fid)), "%d (%sk)" % (s.cal, s.get("pop_k", "?")) if s else "-",
                         fmt_num(plan.done(fid)), "%d (%sk)" % (e.cal, e.get("pop_k", "?")) if e else "-"))
        else:
            rows.append((name, fmt_num(plan.begun(fid)), fmt_num(plan.done(fid))))
    out += ["", "### Rituals", ""]
    out += md_table(("Ritual", "Plan start", "AI start (people)", "Plan end", "AI end (people)") if ai else
                    ("Ritual", "Start", "End"), rows, "lrrrr" if ai else "lrr")
    # research
    rows, seen = [], set()
    for r in plan.research:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        if ai:
            d = an.first_day("TECH", id=r["id"])
            rows.append((r["id"], r["start"], fmt_num(r["done"]), fmt_num(d), fmt_delta(d, r["done"])))
        else:
            rows.append((r["id"], r["start"], fmt_num(r["done"]), r["line"]))
    out += ["", "### Research", ""]
    out += md_table(("Tech", "Plan start", "Plan done", "AI researched", "Delta") if ai else
                    ("Tech", "Start", "Done (when the plan says)", "Plan line"), rows, "lrrrr" if ai else "lrrr")
    if ai:
        extra = [ln for ln in an.by_kind.get("TECH", ()) if ln.get("id") not in seen]
        out += ["", "AI techs the plan does not research: " +
                (", ".join("%s (%d)" % (ln.get("id", "?"), ln.cal) for ln in extra) or "none") +
                ". A tech seen in the first week was owned at the start."]
    # laws
    out += ["", "### Conscription", "", "Plan: " + (", ".join("%s %s" % (x["id"], pday(x)) for x in plan.laws) or
                                                  "no law lines") + "."]
    if ai:
        out += ["", "AI: " + (", ".join("%s %d" % (ln.get("id", "?"), ln.cal) for ln in an.by_kind.get("LAW", ()))
                              or "no LAW lines") + "."]
    # decisions
    ids = sorted(plan.decisions, key=lambda i: (plan.decisions[i]["day"], i))
    if ai:
        ids += sorted(set(ln.get("id") for ln in an.by_kind["DECISION"] + an.by_kind["GIFT"]) - set(ids) - {None})
    rows = []
    for i in ids:
        logged = i in LOGGED_DECISIONS or (i or "").startswith("mltd_gift_of_the_")
        if ai:
            days = [ln.cal for ln in an.find("DECISION", id=i) + an.find("GIFT", id=i)]
            rows.append((i, pday(plan.decisions.get(i)), fmt_num(days[0]) if days else "-" if logged else
                         "not logged", len(days) if logged else "-"))
        else:
            rows.append((i, pday(plan.decisions.get(i)), plan.decisions[i]["line"]))
    if ai:
        trades = [ln.cal for ln in an.by_kind.get("MARKET", ())]
        rows.append(("The Wet Market: a trade", pday(plan.market), fmt_num(trades[0]) if trades else "-",
                     len(trades)))
    elif plan.market:
        rows.append(("The Wet Market: a trade", pday(plan.market), plan.market["line"]))
    out += ["", "### Decisions, gifts and the Wet Market", ""]
    out += md_table(("Decision", "Plan first", "AI first", "AI times") if ai else ("Decision", "First", "Plan line"),
                    rows, "lrrr" if ai else "lrr")
    if ai:
        # cults
        _, stats = cult_series(an)
        if stats:
            rows = [(t, "%d (%s)" % (s["first"][0], fmt_num(s["first"][1])), "%d (%s)" % (s["peak"][0],
                    fmt_num(s["peak"][1])), "%d (%s)" % (s["last"][0], fmt_num(s["last"][1])))
                    for t, s in sorted(stats.items(), key=lambda kv: (kv[1]["first"][0], kv[0]))]
            out += ["", "### Cults", ""]
            out += md_table(("Country", "First (str)", "Peak (str)", "Last seen (str)"), rows, "lrrr")
    return out


def plan_notes(plan):
    out = []
    if plan.notes:
        out += ["", "### Plan lines the parser could not use", ""]
        out += ["- line %d: %s - `%s`" % (n, why, text.strip()[:110]) for n, text, why in plan.notes]
    if plan.consistency:
        out += ["", "### Plan headers whose date and day disagree", ""]
        out += ["- line %d: `%s` - %s" % (n, text.strip(), why) for n, text, why in plan.consistency]
        out += ["", "The report uses the header's day, not its date. Dates count in HOI4's calendar: 365-day years, "
                "no leap day."]
    return out


def plan_line(plan):
    if plan.path is None:
        return "Plan: not found."
    return "Plan: `%s` - %d focuses, %d wars, %d snapshots; %s op lines understood, %d not." % (
        os.path.basename(plan.path), len(plan.focuses), len(plan.declare), len(plan.snapshots),
        sum(plan.verbs.values()) - len([n for n in plan.notes if "verb" in n[2]]), len(plan.notes))


def render_report(runs, run, plan, log_path, bad):
    an = Analysis(run, plan)
    out = ["# MLT AI run report", "",
           "Log: `%s` - run %d of %d. %s" % (log_path, run.index, len(runs), plan_line(plan)), "",
           "## Run summary", ""]
    out += md_table(("", ""), summary_rows(runs, run, bad))
    if run.start is None:
        out += ["", "**No START line**: this run continues a save, so its first weekly poll re-logs everything "
                "already true then (focuses, techs, wars) as if it had just happened."]
    if an.snaps:
        s = an.snaps[-1]
        out += ["", "Final SNAP, day %d (%s): %s" % (s.cal, snap_iso(s), s.text() or "(no keys)")]
    checks = run_checks(an)
    out += ["", "## Automated checks", ""]
    if (run.info("ai", "") or "").lower() == "no":
        out += ["START says ai=no: MLT was played by a human, so these describe the player, not the AI.", ""]
    out += md_table(("", "Check", "Result", "Why", "Look at"),
                    [("(%s)" % c["key"], c["what"], c["result"], c["reason"], c["look"]) for c in checks])
    out += ["", "## Plan vs AI", ""]
    out += plan_sections(plan, an)
    events = [(ln.cal, ln.order, describe(ln, an)) for ln in run.kept if ln.kind not in ("SNAP", "CULT", "ENEMY")]
    events += [(d, 10 ** 9, text) for d, text in cult_series(an)[0]]
    events.sort(key=lambda e: (e[0], e[1]))
    out += ["", "## AI timeline", "",
            "Every line but SNAP and ENEMY, in day order; CULT lines only where a cult takes root or vanishes (the "
            "Cults and Enemies tables have the rest).", ""]
    out += md_table(("Day", "Date", "What"), [(d, iso(d), text) for d, _, text in events], "rll")
    notes = plan_notes(plan)
    if notes:
        out += ["", "## Plan notes"] + notes
    return "\n".join(out) + "\n", an, checks


def render_plan_only(plan, lead):
    out = ["# MLT AI run report", ""] + lead + ["", plan_line(plan), "", "## The plan's timeline", ""]
    out += plan_sections(plan)
    notes = plan_notes(plan)
    if notes:
        out += ["", "## Plan notes"] + notes
    return "\n".join(out) + "\n"


def list_runs(runs):
    out = []
    for r in runs:
        out.append("run %d: day %d-%d (%s to %s), ai=%s, %d line(s)%s" % (
            r.index, r.first_day, r.last_day, iso(r.first_day), iso(r.last_day), r.info("ai"), len(r.kept),
            "" if r.start is not None else ", no START (continued from a save)"))
    return "\n".join(out) + "\n"


def write_csv(an, f):
    """The SNAP series: calendar day, date, the counter, every SNAP key in first-seen order, the game's date text."""
    keys = []
    for s in an.snaps:
        keys += [k for k in s.kv if k != "date" and k not in keys]
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["day", "date", "counter"] + keys + ["date_text"])
    for s in an.snaps:
        row = [s.cal, snap_iso(s), s.day]
        for k in keys:
            v = s.get(k)
            n = parse_num(v) if v is not None else None
            row.append(fmt_num(n) if n is not None else (v or ""))
        w.writerow(row + [(s.get("date") or "").strip()])


# ---- --save ----------------------------------------------------------------------------------------------------
def append_row(path, row):
    """Add one row to a CSV, widening the header when this script has grown new columns since the file began."""
    fields, rows = [k for k, _ in row], []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            old = reader.fieldnames or []
            rows = list(reader)
        fields = old + [k for k in fields if k not in old]
    rows.append(dict((k, "" if v is None else v) for k, v in row))
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def save_run(report, run, an, checks, log_path, folder=RUNS_DIR):
    """<stamp>_day<last>.md (the report), .log (the run's raw MLTD lines) and a row in runs.csv."""
    os.makedirs(folder, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    base = os.path.join(folder, "%s_day%d" % (stamp, run.last_day))
    with open(base + ".md", "w", encoding="utf-8", newline="\n") as f:
        f.write(report)
    with open(base + ".log", "w", encoding="utf-8", newline="\n") as f:
        f.write("".join(ln.raw + "\n" for ln in run.raw))
    row = [("timestamp", stamp), ("log", log_path), ("run", run.index), ("first_day", run.first_day),
           ("last_day", run.last_day)] + [(k, run.info(k, "")) for k in ("ai", "lar", "caps_rule", "schism")]
    row += list(milestones(an)) + [(c["column"], c["result"]) for c in checks]
    append_row(os.path.join(folder, "runs.csv"), row)
    return base


# ---- --selftest ------------------------------------------------------------------------------------------------
SELFTEST_PLAN = """# a plan in miniature: every header, estimate and snapshot form CONQUEST_PLAN.txt uses
# ---- 2275-01-01 day 0: 2 states, 11,009 people, 7 divisions
# ---- ~900 free manpower, 0 caps
justify take_state on CCW, state 437 Feeding Grounds   # ~70-100 days [M]
focus aaa
wait 7 days
focus bbb
focus ccc
# ~day 20-30 [M]: CCW capitulates, before TRL's war
peace with CCW: annex
# ---- 2275-03 day ~60
declare war on TRL and RBT   # ~day 65 [M]
# snapshot [M]: 12-15 states, 1.3-1.7M people, 42-46 divisions,
#   ~2,500 free manpower, Books 1-3 read
# ---- 2276-01: next
focus mlt_kingdom_of_mlyeh
# mid-2276 [M]: TRL and RBT annexed; then XYZ
# ---- 2277-01-16 day 746
focus mltd_fifth_book
frobnicate the widgets
"""
SELFTEST_COSTS = {"aaa": 7, "bbb": 10, "ccc": 5, "mlt_kingdom_of_mlyeh": 30, "mltd_fifth_book": 30}


def selftest_log():
    """A game.log in miniature: engine lines, two runs, glued and duplicated lines, a colour code, commas and a
    K suffix in numbers, missing and unknown keys, an unknown kind, a reloaded save and two broken lines."""
    def at(cal, text, glued=False):
        stamp = "[10:00:00][%s.00]" % iso(cal).replace("-", ".")
        pre = stamp + "[effectbase.cpp:1783]: "
        return (stamp + "[effectbase.cpp:1799]: " + pre if glued else pre) + text

    a = [(0, "START ai=yes lar=yes caps_rule=no schism=yes v=1 date= 12:00, 1 January, 2275"),
         (31, "SNAP owned=2 controlled=2 pop_k=11 divs=7 subjects=0 caps=0 date= 00:00, 1 February, 2275"),
         (70, "JUSTIFY tag=CCW"), (100, "WAR_START tag=TRL"), (120, "WAR_START tag=CCW"),
         (130, "WAR_START tag=DIS"), (151, "SNAP owned=4 subjects=1 pop_k=20 divs=9"),
         (160, "FOCUS id=mlt_sanity_lost"), (170, "FOCUS id=mlt_sanity_found"),
         (165, "FOCUS id=mlt_the_coral_court")]
    b = [(0, "START ai=yes lar=yes caps_rule=yes schism=no v=1 date= 12:00, 2 January, 2275"),
         (0, "LAW id=born_warriors"), (6, "TECH id=amphibious_beast_unlock_tech"), (19, "JUSTIFY tag=CCW"),
         (30, "SNAP owned=2 controlled=2 pop_k=1,234.5 mp_k=12.5K divs=7 caps=\u00a7Y1,200\u00a7! subjects=0 books=0 "
              "cult_target=none foo=bar date= 00:00, 1 February, 2275"),
         (94, "WAR_START tag=CCW"), (149, "WAR_START tag=TRL"), (159, "WAR_END tag=CCW exists=no"),
         (159, "GONE tag=CCW capital=437 owner=MLT"), (199, "WEIRD x=1"), (299, "WAR_START tag=RBT"),
         (499, "WAR_START tag=DIS"), (519, "WAR_START tag=MDT"), (599, "FOCUS id=mlt_kingdom_of_mlyeh"),
         (710, "FOCUS id=mltd_the_wet_market"),
         (719, "DECISION id=mltd_offering_of_the_drowned pop_k=120 mp_k=5 caps=300"), (729, "MARKET caps=150"),
         (799, "FOCUS id=mltd_the_spreading_cult"),
         (818, "SNAP owned=20 pop_k=150 subjects=0 books=2 cult_target=NCR"), (818, "CULT tag=NCR str=10"),
         (848, "SNAP owned=21 pop_k=140 subjects=0 books=3 cult_target=NCR"), (848, "CULT tag=NCR str=18"),
         (848, "CULT tag=TIM str=10"), (849, "DECISION id=mltd_summon_the_deep_ones pop_k=95 mp_k=9 caps=20"),
         (850, "ADVISOR id=MLT_OLD_CASTRO"),
         (879, "SNAP owned=22 pop_k=130 subjects=0 books=3 cult_target=TIM"),
         (899, "RITUAL id=grand state=start pop_k=150"), (999, "SNAP owned=30 pop_k=160 subjects=0 books=5"),
         (1000, "STAGE id=north"), (1019, "RITUAL id=grand state=end pop_k=130"),
         (1090, "SNAP owned=40 pop_k=170 subjects=0 books=5 divs=64 target=60 border=30"), (1090, "CULT tag=NCR str=45"),
         (1100, "WAR_START tag=NCR"), (1120, "ENEMY tag=NCR cap=no states=60 reach=yes"),
         (1200, "POCKET state=start"), (1250, "ENEMY tag=VLT cap=no states=8 reach=no"),
         (1299, "RITUAL id=final state=start pop_k=210"), (1300, "POCKET state=end"),
         (1349, "WAR_START tag=TCA"), (1479, "RITUAL id=final state=end pop_k=140"),
         (1490, "DECISION id=mltd_offering_of_the_drowned pop_k=140 mp_k=9 caps=120"), (1499, "WAR_START tag=CES")]
    lines = ["[08:15:53][no_game_date][defines.cpp:270]: 4469 defines loaded",
             at(0, "EXODUS - Total weighting of 0 detected")]
    lines += [at(day, "MLTD %d %s" % (day, text), glued=i % 3 == 1) for i, (day, text) in enumerate(a)]
    lines += [at(1, "MLTD SNAP owned=2"), at(1, "MLTD twelve FOCUS id=x")]          # broken: no day, a word
    for i, (day, text) in enumerate(b):
        lines.append(at(day + 1, "MLTD %d %s" % (day, text), glued=i % 2 == 0))
        if day == 30:
            lines.append(at(day + 1, "MLTD %d %s" % (day, text), glued=True))       # the same line twice
    return "\r\n".join(lines) + "\r\n"


def selftest():
    failures, count = [], [0]

    def ok(cond, what):
        count[0] += 1
        if not cond:
            failures.append(what)

    for text, want in (("1,234", 1234), ("1.234.567", 1234567), ("12,5", 12.5), ("\u00a7Y120\u00a7!", 120),
                       ("12.5K", 12500), ("1.50M", 1.5e6), ("45%", 45), ("+3", 3), ("-5", -5), ("12.000", 12),
                       ("1\u00a0234", 1234), ("none", None), ("", None), ("CCW", None)):
        ok(parse_num(text) == want, "parse_num(%r) = %r, want %r" % (text, parse_num(text), want))
    for text, want in ((" 12:00, 1 January, 2275", 0), ("12:00, 2 January, 2275", 1), ("2276.8.15.12", 591),
                       ("2276-08-15", 591), ("1 February 2275", 31), ("February 1, 2275", 31), ("soon", None)):
        ok(parse_game_date(text) == want, "parse_game_date(%r) = %r" % (text, parse_game_date(text)))
    ok(iso(0) == "2275-01-01" and iso(591) == "2276-08-15" and iso(day_of(2279, 1, 1)) == "2279-01-01",
       "iso / day_of disagree")

    good, bad = extract(enumerate(selftest_log().split("\r\n"), 1))
    ok(len(bad) == 2, "2 broken lines, got %d" % len(bad))
    two, _ = extract([(1, "[..][2275.01.05.00][effectbase.cpp:1783]: MLTD 4 FOCUS id=a"
                          "[10:00:01][2275.01.05.00][effectbase.cpp:1783]: MLTD 4 TECH id=b")])
    ok([(ln.kind, ln.get("id")) for ln in two] == [("FOCUS", "a"), ("TECH", "b")], "two payloads on one line")
    runs = split_runs(good)
    ok(len(runs) == 2, "2 runs, got %d" % len(runs))
    ra, rb = runs[0], runs[-1]
    ok(ra.offset == 0 and rb.offset == 1, "offsets %r %r, want 0 1" % (ra.offset, rb.offset))
    ok(len(ra.reloads) == 1 and ra.reloads[0][3] == 1, "run 1: one reload dropping one line, got %r" % ra.reloads)
    ok([ln.get("id") for ln in ra.kept if ln.kind == "FOCUS"] == ["mlt_sanity_lost", "mlt_the_coral_court"],
       "run 1 keeps the reloaded timeline")
    ok(rb.folded == 1, "run 2 folds 1 duplicate, got %d" % rb.folded)
    ok(rb.clock_mismatch == 0, "run 2's lines agree with their log dates")
    s0 = [ln for ln in rb.kept if ln.kind == "SNAP"][0]
    ok(s0.cal == 31 and s0.num("pop_k") == 1234.5 and s0.num("caps") == 1200 and s0.num("mp_k") == 12500,
       "SNAP numbers: %r" % s0.kv)
    ok(s0.get("foo") == "bar" and s0.get("date").endswith("2275"), "unknown key and date= kept")
    ok(any(ln.kind == "WEIRD" for ln in rb.kept), "unknown kind kept")

    plan = parse_plan(SELFTEST_PLAN, SELFTEST_COSTS)
    ok([(f["id"], f["start"], f["done"]) for f in plan.focuses] ==
       [("aaa", 0, 7), ("bbb", 7, 17), ("ccc", 17, 22), ("mlt_kingdom_of_mlyeh", 365, 395),
        ("mltd_fifth_book", 746, 776)], "plan focus clock: %r" % [(f["id"], f["start"], f["done"])
                                                                  for f in plan.focuses])
    ok(plan.justify["CCW"]["day"] == 0 and not plan.justify["CCW"]["approx"], "a '~70-100 days' duration is no date")
    ok(plan.peace["CCW"]["day"] == 25 and plan.annex["CCW"]["how"] == "peace", "estimate comment on peace")
    ok(plan.declare["TRL"]["day"] == 65 and plan.declare["RBT"]["day"] == 65, "every tag on a declare line")
    ok(plan.annex["TRL"]["day"] == day_of(2276, 7, 1) and "XYZ" not in plan.annex, "mid-2276 annexations")
    head, snap = plan.snapshots
    ok(head["day"] == 0 and head["metrics"]["people"][:2] == (11.009, 11.009) and
       head["metrics"]["manpower"][:2] == (0.9, 0.9) and head["metrics"]["caps"][:2] == (0, 0), "header snapshot")
    ok(snap["day"] == 60 and snap["metrics"]["states"][:2] == (12, 15) and
       snap["metrics"]["people"][:2] == (1300, 1700) and snap["metrics"]["divisions"][:2] == (42, 46) and
       snap["metrics"]["books"][:2] == (3, 3) and snap["metrics"]["manpower"][:2] == (2.5, 2.5),
       "snapshot ranges: %r" % snap["metrics"])
    ok(any("frobnicate" in n[1] for n in plan.notes), "an unknown verb is noted")
    ok(len(plan.consistency) == 1 and plan.consistency[0][0] == 18, "the 2277 header's leap day is noted")

    want = {1: dict(a=FAIL, b=FAIL, c=NA, d=NA, e=NA, f=PASS, g=NA, h=FAIL, i=NA, j=NA, k=FAIL, l=NA, m=NA, n=NA, o=NA,
                    p=NA, q=NA),
            2: dict(a=PASS, b=PASS, c=PASS, d=PASS, e=FAIL, f=FAIL, g=PASS, h=PASS, i=PASS, j=FAIL, k=PASS, l=PASS, m=PASS,
                    n=PASS, o=PASS, p=PASS, q=PASS)}
    for r in runs:
        report, an, checks = render_report(runs, r, plan, "selftest.log", bad)
        got = dict((c["key"], c["result"]) for c in checks)
        ok(got == want[r.index], "run %d checks %r" % (r.index, got))
        ok("## Automated checks" in report and "## AI timeline" in report, "run %d report sections" % r.index)
        if r is rb:
            ok("CULT TIM is gone" in report and "CULT NCR takes root" in report, "cult entries in the timeline")
            ok("### Enemies" in report and "STAGE north: the north is consolidated" in report and
               "ADVISOR MLT_OLD_CASTRO hired" in report, "the Enemies table and the STAGE and ADVISOR entries")
            ok("WEIRD x=1 (unknown kind)" in report, "unknown kind in the timeline")
            buf = io.StringIO()
            write_csv(an, buf)
            rows = buf.getvalue().splitlines()
            ok(rows[0].startswith("day,date,counter,owned,controlled,pop_k") and rows[1].startswith("31,2275-02-01,30,")
               and len(rows) == 7, "SNAP CSV: %r" % rows[:2])
            with tempfile.TemporaryDirectory() as tmp:
                base = save_run(report, r, an, checks, "selftest.log", tmp)
                save_run(report, r, an, checks, "selftest.log", tmp)
                with open(os.path.join(tmp, "runs.csv"), encoding="utf-8") as f:
                    saved = list(csv.DictReader(f))
                ok(os.path.exists(base + ".md") and os.path.exists(base + ".log"), "--save writes .md and .log")
                ok(len(saved) == 2 and saved[0]["kingdom"] == "600" and saved[0]["e_ritual_peace"] == FAIL,
                   "runs.csv rows: %r" % saved[:1])
    alone = render_plan_only(plan, ["No MLTD lines."])
    ok("## The plan's timeline" in alone and "| mlt_kingdom_of_mlyeh | 365 | 395 |" in alone and
       "frobnicate" in alone, "the plan-only report: its focus table and its notes")
    ok("run 1: day 0-165" in list_runs(runs), "--list: %r" % list_runs(runs))

    def mini(rows):
        """One run from (counter, the day game.log dates the line, payload) rows."""
        lines = [(i, "[10:00:00][%s.00][effectbase.cpp:1783]: MLTD %d %s" % (iso(logged).replace("-", "."), day, text))
                 for i, (day, logged, text) in enumerate(rows, 1)]
        return split_runs(extract(lines)[0])[0]

    begin = "START ai=yes lar=yes caps_rule=yes schism=%s v=1 date= 00:00, 2 January, 2275"
    # the daily pulse first: every line but START carries its own day; a reload drops the reloaded day's old lines
    rl = mini([(0, 1, begin % "no"), (10, 10, "FOCUS id=a"), (20, 20, "FOCUS id=x"), (25, 25, "WAR_START tag=YAK"),
               (20, 20, "TECH id=b")])
    ok(rl.reloads == [(25, 20, 5, 2)] and [ln.kind for ln in rl.kept] == ["START", "FOCUS", "TECH"],
       "a reload drops what the abandoned timeline logged on the reloaded day: %r" % rl.reloads)
    ok(rl.offset == 0 and [ln.cal for ln in rl.kept] == [1, 10, 20] and rl.clock_mismatch == 0,
       "calibrated on game.log's dates, START on its own: %r" % [(ln.day, ln.cal) for ln in rl.kept])
    arch = split_runs(extract([(1, "MLTD 0 " + begin % "no"), (2, "MLTD 7 FOCUS id=a"),
                               (3, "MLTD 31 SNAP owned=2 date= 00:00, 1 February, 2275")])[0])[0]
    ok(arch.offset == 0 and arch.offset_source == "SNAP date=" and [ln.cal for ln in arch.kept] == [1, 7, 31],
       "without log dates, calibrated on SNAP's date=: %r" % [(ln.day, ln.cal) for ln in arch.kept])
    deadline = day_of(*DIS_OFFER_UNTIL)
    kr = mini([(0, 1, begin % "yes"), (deadline + 14, deadline + 14, "JUSTIFY tag=DIS"),
               (deadline + 70, deadline + 70, "WAR_START tag=DIS")])
    ok(check_k(Analysis(kr, plan))[0] == PASS, "(k): a war on DIS after the offer's deadline is the AI's fallback")
    jr = mini([(0, 1, begin % "no"), (800, 800, "RITUAL id=grand state=start pop_k=150"),
               (920, 920, "RITUAL id=grand state=end pop_k=140"),
               (930, 930, "DECISION id=mltd_summon_the_deep_ones pop_k=142"),
               (940, 940, "DECISION id=mltd_offering_of_the_drowned pop_k=190")])
    got = check_j(Analysis(jr, plan))
    ok(got[0] == FAIL and "mltd_offering_of_the_drowned on day 940" in got[1] and "deep_ones on day" not in got[1]
       and "1 Deep Ones summon" in got[1], "(j): the Deep Ones summon is not held to 200k: %r" % (got,))
    pr = mini([(0, 1, begin % "no"), (100, 100, "WAR_START tag=VLT"), (130, 130, "ENEMY tag=VLT cap=no states=8 reach=no"),
               (140, 140, "POCKET state=start"), (600, 600, "STAGE id=ncr"), (620, 620, "WAR_START tag=NCR")])
    got = check_m(Analysis(pr, plan))
    ok(got[0] == FAIL and "VLT" in got[1] and "still open" in got[1], "(m): a pocket open 480 days fails: %r" % (got,))
    got = check_l(Analysis(pr, plan))
    ok(got[0] == FAIL and "never consolidated" in got[1], "(l): the NCR war with no north fails: %r" % (got,))
    nr = mini([(0, 1, begin % "no"), (100, 100, "WAR_START"), (105, 105, "WAR_START tag=DIS"),
               (106, 106, "WAR_END exists=no"), (107, 107, "GONE capital=1 owner=MLT"),
               (108, 108, "GONE tag=TIM capital=51 owner=MLT"), (110, 110, "DECISION pop_k=120"),
               (111, 111, "GIFT id=mltd_gift_of_the_brood"), (112, 112, "GIFT")])
    try:
        render_report([nr], nr, plan, "selftest.log", [])
        crash = None
    except Exception as exc:
        crash = exc
    ok(crash is None, "lines without tag= or id= break the report: %r" % crash)

    for f in failures:
        print("FAIL:", f)
    print("selftest: %d of %d assertions passed" % (count[0] - len(failures), count[0]))
    return 1 if failures else 0


# ---- main ------------------------------------------------------------------------------------------------------
def emit(text, out):
    sys.stdout.write(text)
    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        sys.stderr.write("wrote %s\n" % out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--log", help="the game.log to read (default: %s)" % default_log())
    ap.add_argument("--run", type=int, help="the run to report: 1 is the first in the log, -1 the last (default)")
    ap.add_argument("--list", action="store_true", help="list the runs in the log and stop")
    ap.add_argument("--out", help="also write the report to this file")
    ap.add_argument("--csv", help="write the run's SNAP series to this CSV file")
    ap.add_argument("--save", action="store_true",
                    help="archive the report and the run's raw lines in ai_runs/ and add a row to ai_runs/runs.csv")
    ap.add_argument("--plan-only", action="store_true", help="print the plan's own timeline and stop")
    ap.add_argument("--selftest", action="store_true",
                    help="test the parser and the checks on a built-in log; exits 1 on a failure")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    if args.selftest:
        return selftest()
    plan = load_plan()
    if args.plan_only:
        emit(render_plan_only(plan, ["The plan alone (--plan-only)."]), args.out)
        return 0
    path = args.log or default_log()
    if not os.path.exists(path):
        sys.stderr.write("no game.log at %s (use --log PATH)\n" % path)
        return 2
    good, bad = extract(read_log(path))
    runs = split_runs(good)
    if not runs:
        with open(path, "rb") as f:
            n_lines = sum(1 for _ in f)
        if args.list:
            sys.stdout.write("no runs: %s holds no MLTD lines (%d lines in all)\n" % (path, n_lines))
            return 0
        lead = ["**No MLTD telemetry lines in `%s`** (%d lines, last written %s)." % (
                    path, n_lines, time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path)))), "",
                "The telemetry writes them while MLT exists: start or load a game with Rising Tide's telemetry, let "
                "it run, and run this report before the game is launched again - every launch empties game.log. "
                "Until then, here is the plan's timeline alone."]
        if bad:
            lead += ["", "%d line(s) mention MLTD but break the contract, e.g. game.log line %d: `%s`" % (
                len(bad), bad[0][0], bad[0][1][:100])]
        emit(render_plan_only(plan, lead), args.out)
        if args.list or args.csv or args.save:
            sys.stderr.write("no run to list, export or save\n")
        return 0
    if args.list:
        sys.stdout.write(list_runs(runs))
        return 0
    pick = args.run if args.run is not None else -1
    if not (1 <= pick <= len(runs) or -len(runs) <= pick <= -1):
        sys.stderr.write("--run %d: the log holds runs 1-%d\n" % (pick, len(runs)))
        return 2
    run = runs[pick - 1 if pick > 0 else pick]
    report, an, checks = render_report(runs, run, plan, path, bad)
    emit(report, args.out)
    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            write_csv(an, f)
        sys.stderr.write("wrote %s (%d SNAPs)\n" % (args.csv, len(an.snaps)))
    if args.save:
        try:
            base = save_run(report, run, an, checks, path)
            sys.stderr.write("saved %s.md and .log; added a row to %s\n" % (base, os.path.join(RUNS_DIR, "runs.csv")))
        except OSError as exc:                  # runs.csv open in a spreadsheet, say
            sys.stderr.write("could not save: %s\n" % exc)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
