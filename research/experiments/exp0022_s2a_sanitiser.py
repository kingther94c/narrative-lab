"""EXP-0022: the sanitiser of sub-study S2 (step S2-a): eight views of an earnings episode.

Design: docs/plans/2026-11-20_substudy_s2_plan.md, §5 to §7. An engineering step with no
hypothesis and no model call. It turns one earnings release, and a sheet of ratios computed from
fundamentals as first filed, into eight views: a half-fraction (I = NPSZ) of four switches.

- N, names: pseudonyms for the company, its tickers, its city, people named next to a title,
  trademarked products and capitalised words that are not common English; web sites, e-mail
  addresses and telephone numbers are removed.
- P, periods: calendar years become years relative to the episode (Year T, Year T-1), dates and
  month names are removed, quarter codes (1Q26, FY25) are relabelled.
- S, scaling: levels times f, per-share figures times g, share counts times f/g, with f and g
  drawn away from powers of ten, so that EPS = net income / shares still holds and no digit
  string survives.
- Z, noise: in each table with a known current-period column, every leaf level of that column is
  multiplied by 1 + e, e ~ U(-sigma, sigma); totals and differences found by value are re-derived
  from their parts; growth rates and margins found by value are reprinted; the last shown digit of
  the other levels is redrawn (Levy, 2026); percentages that link to nothing get additive noise
  that keeps their sign; numbers in the prose that match a table cell are reprinted from it.

The ratio sheet (strategy H: code does the arithmetic) shows, for the last eight quarters filed
before the release, year-on-year revenue growth, operating margin and net margin, from EXP-0020's
series. Under Z each ratio gets additive noise that keeps its sign; under P its rows are labelled
by distance in quarters.

    conda run --no-capture-output -n nlab python research/experiments/exp0022_s2a_sanitiser.py build
    conda run --no-capture-output -n nlab python research/experiments/exp0022_s2a_sanitiser.py check
    conda run --no-capture-output -n nlab python research/experiments/exp0022_s2a_sanitiser.py show --episode 0 --view 7

Only training and development companies are read.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import json
import math
import random
import re
import statistics
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "Foundry" / "tools"))
from tools.textmask import find_terms, redact  # noqa: E402  (sibling repo, read only)

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
BULK = DRIVE / "edgar" / "bulk" / "submissions-2026-11-12.zip"
LIST = DRIVE / "s2" / "exp0020" / "releases.jsonl"
SERIES = DRIVE / "s2" / "exp0020" / "series.jsonl"
TEXT_DIRS = (DRIVE / "edgar" / "releases", DRIVE / "s2" / "exp0021" / "releases")
OUT = DRIVE / "s2" / "exp0022"
WORDS = Path("/usr/share/dict/words")

SIDES = ("train", "dev")
SEED = 20261120
SIGMA = 0.02  # relative noise on levels; at most 2 points on a growth rate, the label's dead band
VIEWS = ((0, 0, 0, 0), (1, 1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1),
         (0, 1, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 1, 1))  # (N, P, S, Z), I = NPSZ
SHEET_QUARTERS = 8


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------------------------
# Text clean-up

WRAPPER = re.compile(r"^\s*(EX-99[\d.]*|\d{1,3}|[\w.\-]+\.html?|Document)\s*$", re.I)
PAGE = re.compile(r"^\s*(-\s*\d+\s*-|Page\s+\d+(\s+of\s+\d+)?|\d+\s*\|\s*Page)\s*$", re.I)


def clean(text: str) -> str:
    lines = text.splitlines()
    head = 0
    while head < min(12, len(lines)) and (not lines[head].strip() or WRAPPER.match(lines[head])):
        head += 1
    out = [l.rstrip() for l in lines[head:] if not PAGE.match(l)]
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


# ---------------------------------------------------------------------------------------------
# Number tokens and their types

NUM = re.compile(
    r"(?<![A-Za-z0-9.,%)/\-])"
    r"(?P<cur0>\$\s*)?(?P<open>\()?(?P<neg>[-−])?(?P<cur>\$\s*)?"
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
    r"(?P<close>\))?"
    r"(?P<pct>\s?%|\s?percent\b|\s?per\s?cent\b)?"
    r"(?P<unit>\s(?:thousand|million|billion|trillion)s?\b|\s?(?:MM|M|B|K|bn|mn)\b)?"
    r"(?![A-Za-z0-9]|-[A-Za-z]|[.,]\d)"
)
UNITS = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12,
         "k": 1e3, "m": 1e6, "mm": 1e6, "mn": 1e6, "b": 1e9, "bn": 1e9}
SCALE_HEAD = re.compile(r"\bin\s+(thousands|millions|billions)\b|\(\$\s*(?:in\s+)?(thousands|millions|billions)?|\$\s*in\s+(thousands|millions|billions)", re.I)
PCT_HEAD = re.compile(r"%|\bpercent|\bpct\b|\bchange\b|\bgrowth\b|\bbps\b|basis points", re.I)
PER_SHARE = re.compile(r"per\s+(?:diluted\s+|basic\s+|common\s+|ordinary\s+)?(?:share|unit|ads)|\beps\b|earnings\s+per|loss\s+per", re.I)
SHARES = re.compile(r"\bshares\b|\bshare\s+count\b|\bunits\s+outstanding\b", re.I)
PCT_LABEL = re.compile(r"%|\bpercent|as a percentage|\bgrowth\b|\brate\b|\bratio\b|\byield\b|return on|\bbps\b|basis points", re.I)
MARGIN = re.compile(r"\bmargin\b", re.I)
LEVELISH = ("level", "per_share", "shares", "other")
PER_SHARE_NEAR = re.compile(r"(per\s+(?:diluted\s+|basic\s+|common\s+)?share|\beps\b|a\s+share)", re.I)
PCT_AFTER = r"\s*\)?\s*(%|bps\b|bp\b|basis\s+points?|pts?\b|ppts?\b|pp\b|percentage\s+points?)"
SUB_ROW = re.compile(r"^(basic|diluted|assuming dilution|basic and diluted)\b", re.I)


@dataclasses.dataclass
class Tok:
    start: int
    end: int
    line: int
    m: dict
    value: float  # signed, in the units printed
    dec: int
    digits: int
    kind: str = "other"  # level, per_share, shares, pct, year, other
    row: int | None = None
    col: int | None = None
    new: float | None = None
    why: str = ""

    @property
    def raw(self) -> str:
        return self.m["all"]


def parse(text: str) -> tuple[list[str], list[int], list[Tok]]:
    lines = text.split("\n")
    starts, pos = [], 0
    for l in lines:
        starts.append(pos)
        pos += len(l) + 1
    toks = []
    li = 0
    for mt in NUM.finditer(text):
        while li + 1 < len(starts) and starts[li + 1] <= mt.start():
            li += 1
        g = mt.groupdict()
        num = g["num"]
        core = num.replace(",", "")
        dec = len(core.split(".")[1]) if "." in core else 0
        v = float(core)
        post = text[mt.end(): mt.end() + 24]
        late_close = bool(g["open"]) and not g["close"] and re.match(r"\s*\)", post)
        neg = bool(g["neg"]) or (bool(g["open"]) and (bool(g["close"]) or bool(late_close)))
        digits = len(re.sub(r"\D", "", num).lstrip("0")) or 1
        d = {k: (g[k] or "") for k in g}
        d["all"] = mt.group(0)
        d["pct_after"] = "1" if not g["pct"] and re.match(PCT_AFTER, post, re.I) else ""
        d["shares_after"] = "1" if re.match(r"\s*(?:million\s+|thousand\s+)?(?:common\s+|ordinary\s+)?shares\b", post, re.I) else ""
        toks.append(Tok(mt.start(), mt.end(), li, d, -v if neg else v, dec, digits))
    return lines, starts, toks


def row_label(line: str) -> tuple[str, int] | None:
    """The label of a table row and where its values start, or None for prose and headers."""
    s = line.rstrip()
    if not s.strip() or len(s) > 400:
        return None
    lead = len(s) - len(s.lstrip())
    m = re.search(r"(\s{2,}|\t)", s[lead:])
    if not m:
        return None
    label = s[lead: lead + m.start()].strip(" .:–-")
    if not label or not re.search(r"[A-Za-z]", label) or len(label) > 120:
        return None
    if re.match(rf"({MONTHS})\s+\d", label) or re.fullmatch(r"(?:(?:three|six|nine|twelve)\s+months|quarter|year)s?\s+ended.*", label, re.I):
        return None  # a column heading, not a row
    rest = s[lead + m.start():]
    words = [w for w in re.findall(r"[A-Za-z]{3,}", NUM.sub(" ", rest)) if w.lower() not in ("nmf", "n/m")]
    if len(words) > 2 or not NUM.search(rest):
        return None  # prose after the gap, or nothing to read
    return label, lead + m.start()


def is_year(t: Tok) -> bool:
    return (not t.m["cur0"] and not t.m["cur"] and not t.m["pct"] and not t.m["unit"] and t.dec == 0
            and "," not in t.m["num"] and 1990 <= t.value <= 2035 and not t.m["open"])


def tol(t: Tok) -> float:
    return 0.5 * 10 ** (-t.dec) + 1e-9


class Doc:
    """One release: lines, tokens, table rows, blocks and links found by value."""

    def __init__(self, text: str, year: int):
        self.text = text
        self.year = year
        self.lines, self.starts, self.toks = parse(text)
        self.by_line: dict[int, list[Tok]] = collections.defaultdict(list)
        for t in self.toks:
            self.by_line[t.line].append(t)
        self.rows: dict[int, tuple[str, list[Tok]]] = {}
        self.block_of: dict[int, int] = {}
        self.years: dict[int, list[int]] = {}  # block -> the years heading its period columns
        self.derived: dict[int, tuple[str, list[int]]] = {}  # row line -> ("sum"|"diff", part rows)
        self.pairs: dict[int, list[tuple[int, int]]] = {}  # row line -> (current cell, prior cell)
        self.growth: list[tuple[Tok, int, int, int]] = []  # pct token, row, current cell, prior cell
        self.change: list[tuple[Tok, int, int, int]] = []  # change token, row, current cell, prior cell
        self.change_ids: set[int] = set()
        self.margins: list[tuple[int, int, int]] = []  # pct row, numerator row, denominator row
        self._rows()
        self._blocks()
        self._type()
        self._links()

    # -- structure
    def _rows(self):
        for i, l in enumerate(self.lines):
            r = row_label(l)
            if not r:
                continue
            label, at = r
            cells = [t for t in self.by_line.get(i, []) if t.start - self.starts[i] >= at]
            cells = [t for t in cells if not is_year(t)]
            if cells:
                self.rows[i] = (label, cells)
                for c, t in enumerate(cells):
                    t.row, t.col = i, c

    def _blocks(self):
        b, last = -1, -99
        for i in range(len(self.lines)):
            if i in self.rows:
                if i - last > 4:
                    b += 1
                self.block_of[i] = b
                last = i
        for blk in set(self.block_of.values()):
            first = min(i for i, x in self.block_of.items() if x == blk)
            years = []
            for j in range(first - 1, max(-1, first - 8), -1):
                ys = [t for t in self.by_line.get(j, []) if is_year(t)]
                if len(ys) >= 2:
                    years = [int(t.value) for t in ys]
                    break
            self.years[blk] = years

    def header_mode(self, i: int) -> tuple[str | None, bool]:
        """Mode set by the nearest header above row i within its block: 'pct', 'level' or None,
        and whether a money scale is in force."""
        mode, money = None, False
        blk = self.block_of[i]
        j = i - 1
        seen = 0
        while j >= 0 and seen < 12:
            if j in self.rows and self.block_of.get(j) != blk:
                break
            if j not in self.rows:
                s = self.lines[j]
                if s.strip() and len(s.strip()) < 200:
                    if mode is None and PCT_HEAD.search(s) and not SCALE_HEAD.search(s):
                        mode = "pct"
                    if SCALE_HEAD.search(s) or "$" in s:
                        money = True
                        if mode is None:
                            mode = "level"
                elif len(s.strip()) >= 200:
                    break
            seen += 1
            j -= 1
        return mode, money

    # -- types
    def sub_row_context(self, i: int) -> str:
        """For a row labelled Basic or Diluted: 'per_share' or 'shares' from the line above."""
        j = i - 1
        while j >= 0 and i - j <= 6:
            if j in self.rows and SUB_ROW.match(self.rows[j][0]):
                j -= 1
                continue
            s = self.lines[j] if j not in self.rows else self.rows[j][0]
            if not s.strip():
                j -= 1
                continue
            if PER_SHARE.search(s):
                return "per_share"
            if SHARES.search(s):
                return "shares"
            return ""
        return ""

    def _type(self):
        for t in self.toks:
            if is_year(t) and t.row is None:
                t.kind = "year"
            elif t.m["pct"] or t.m["pct_after"]:
                t.kind = "pct"
        for i, (label, cells) in self.rows.items():
            mode, money = self.header_mode(i)
            sub = self.sub_row_context(i) if SUB_ROW.match(label) else ""
            seen_pct = False
            for t in cells:
                money_tok = bool(t.m["cur0"] or t.m["cur"])
                if t.m["pct"] or t.m["pct_after"]:
                    t.kind, seen_pct = "pct", True
                elif sub:
                    t.kind = sub
                elif PER_SHARE.search(label):
                    t.kind = "per_share"
                elif SHARES.search(label):
                    t.kind = "shares"
                elif PCT_LABEL.search(label) and not money_tok:
                    t.kind = "pct"
                elif seen_pct and not money_tok:
                    t.kind = "pct"
                elif mode == "pct" and not money_tok:
                    t.kind = "pct"
                else:
                    t.kind = "level"  # tables are statements in money or in counts; both scale by f
                t.why = f"row:{mode}"
        # prose
        for t in self.toks:
            if t.row is not None or t.kind in ("year", "pct"):
                continue
            after = self.text[t.end: t.end + 30]
            before = self.text[max(0, t.start - 50): t.start]
            if t.m["shares_after"] and not (t.m["cur0"] or t.m["cur"]):
                t.kind, t.why = "shares", "prose"
            elif t.m["cur0"] or t.m["cur"] or t.m["unit"]:
                small = not t.m["unit"] and abs(t.value) < 1000
                if small and (re.match(r"\s*(?:per\s+(?:diluted\s+|basic\s+|common\s+)?share|a\s+(?:diluted\s+)?share|per\s+diluted)", after, re.I)
                              or re.search(r"(?:\beps\b|per\s+(?:diluted\s+)?share)\s*(?:of|was|were|to|at|is)?\s*(?:approximately\s+|about\s+)?(?:\$\s*[\d.]+\s+to\s+)?$", before, re.I)
                              or re.search(r"(?:million|billion|thousand),?\s+or\s+$", before, re.I)):
                    t.kind = "per_share"
                else:
                    t.kind = "level"
                t.why = "prose"
        # a 'margin' row is a level when it is a difference of level rows (fixed in _links)

    # -- links found by value
    def vec_idx(self, r: int) -> list[int]:
        """Indices of the cells of row r that hold one value per period column."""
        if r in getattr(self, "_vec", {}):
            return self._vec[r]
        cells = self.rows[r][1]
        idx = [c for c, t in enumerate(cells) if t.kind in LEVELISH and id(t) not in self.change_ids]
        if not idx and MARGIN.search(self.rows[r][0]) and cells and all(t.kind == "pct" and not t.m["pct"] for t in cells):
            idx = list(range(len(cells)))  # a 'margin' row that may be a level difference; tested by value
        years = self.years.get(self.block_of[r]) or []
        if years and len(idx) >= len(years):
            idx = idx[: len(years)]
        return idx

    def vec(self, r: int) -> list[Tok]:
        return [self.rows[r][1][c] for c in self.vec_idx(r)]

    def _links(self):
        blocks = collections.defaultdict(list)
        for i in sorted(self.rows):
            blocks[self.block_of[i]].append(i)
        for blk, rows in blocks.items():
            for idx, r in enumerate(rows):
                v = self.vec(r)
                if not v or not any(t.value for t in v):
                    continue
                n = len(v)
                found = None
                for start in range(idx - 1, max(-1, idx - 12), -1):  # a run of rows above adding up to r
                    run = rows[start: idx]
                    if len(run) < 2:
                        continue
                    parts = [self.vec(x) for x in run]
                    if any(len(p) != n for p in parts):
                        continue
                    if all(abs(sum(p[c].value for p in parts) - v[c].value)
                           <= sum(tol(p[c]) for p in parts) + tol(v[c]) for c in range(n)):
                        found = ("sum", run)
                        break
                if not found:
                    for a in range(max(0, idx - 12), idx):  # two rows above whose difference is r
                        pa = self.vec(rows[a])
                        if len(pa) != n:
                            continue
                        for b in range(a + 1, idx):
                            pb = self.vec(rows[b])
                            if len(pb) == n and all(abs(pa[c].value - pb[c].value - v[c].value)
                                                    <= tol(pa[c]) + tol(pb[c]) + tol(v[c]) for c in range(n)):
                                found = ("diff", [rows[a], rows[b]])
                                break
                        if found:
                            break
                if found:
                    self.derived[r] = found
                    for t in v:
                        if t.kind in ("pct", "other"):
                            t.kind, t.why = "level", "derived"
            for r in rows:
                self._pairs_and_growth(blk, r)
            levrows = [r for r in rows if self.vec(r) and all(t.kind in LEVELISH for t in self.vec(r))]
            dens = [r for r in levrows if re.search(r"revenue|sales", self.rows[r][0], re.I)][:3] or levrows[:1]
            for r in rows:
                cells = self.rows[r][1]
                if not cells or not all(t.kind == "pct" for t in cells) or r in self.derived:
                    continue
                done = False
                for d in dens:
                    den = self.vec(d)
                    if len(den) != len(cells):
                        continue
                    for a in levrows:
                        num = self.vec(a)
                        if a == d or len(num) != len(cells):
                            continue
                        if all(den[c].value and abs(100 * num[c].value / den[c].value - cells[c].value) <= tol(cells[c]) + 0.05
                               for c in range(len(cells))):
                            self.margins.append((r, a, d))
                            done = True
                            break
                    if done:
                        break
        # retyping can change a row's vector: links that no longer hold are dropped, then vectors frozen
        for r, (how, parts) in list(self.derived.items()):
            v, pv = self.vec(r), [self.vec(p) for p in parts]
            ok = v and all(len(p) == len(v) for p in pv) and all(
                abs((sum(p[c].value for p in pv) if how == "sum" else pv[0][c].value - pv[1][c].value) - v[c].value)
                <= sum(tol(p[c]) for p in pv) + tol(v[c]) for c in range(len(v)))
            if not ok:
                del self.derived[r]
        self._vec = {r: self.vec_idx(r) for r in self.rows}

    def _pairs_and_growth(self, blk: int, r: int) -> None:
        cells = self.rows[r][1]
        vidx = self.vec_idx(r)
        years = self.years.get(blk) or []
        pairs = []
        if years and len(vidx) == len(years):
            cy = self.year if self.year in years else (max(years) if len(set(years)) > 1 else None)
            if cy is not None:
                for p, y in enumerate(years):
                    if y != cy:
                        continue
                    for q in (p + 1, p - 1):
                        if 0 <= q < len(years) and years[q] == cy - 1:
                            pairs.append((vidx[p], vidx[q]))
                            break
        for j, t in enumerate(cells):
            unmarked = t.kind == "level" and not (t.m["cur0"] or t.m["cur"]) and abs(t.value) < 1000 and t.dec <= 1
            if t.kind != "pct" and not unmarked and t.kind != "other":
                continue
            before = [c for c in range(j) if cells[c].kind in LEVELISH and id(cells[c]) not in self.change_ids]
            cands = [(a, b) for a, b in pairs if a < j and b < j]
            cands.sort(key=lambda ab: -max(ab))
            if not cands and len(before) >= 2:
                i1, i2 = before[-2], before[-1]
                cands = [(i1, i2), (i2, i1)]
            for a, b in cands[:2]:
                ta, tb = cells[a], cells[b]
                if not tb.value:
                    continue
                if t.kind != "pct" and abs(t.value - (ta.value - tb.value)) <= tol(t) + tol(ta) + tol(tb):
                    t.kind, t.why = "level", "change"
                    self.change.append((t, r, a, b))
                    self.change_ids.add(id(t))
                    break
                g = (ta.value / tb.value - 1) * 100 * (1 if tb.value > 0 else -1)
                if abs(abs(t.value) - abs(g)) <= tol(t) + 0.05 and (t.value == 0 or (t.value > 0) == (g > 0) or abs(g) < 0.5):
                    t.kind, t.why = "pct", "growth"
                    self.growth.append((t, r, a, b))
                    if (a, b) not in pairs:
                        pairs.append((a, b))
                    break
        self.pairs[r] = pairs


# ---------------------------------------------------------------------------------------------
# Switches S and Z on numbers

def away_from_ten(rng: random.Random, lo: float, hi: float) -> float:
    while True:
        x = math.exp(rng.uniform(math.log(lo), math.log(hi)))
        if abs(math.log10(x) - round(math.log10(x))) > 0.12:
            return x


def redraw_last_digit(rng: random.Random, t: Tok, v: float) -> float:
    if t.digits < 3:
        return v * (1 + rng.uniform(-SIGMA, SIGMA))  # a two-digit figure: small relative noise
    u = 10 ** (-t.dec)
    n = round(abs(v) / u)
    d = n % 10
    nd = rng.choice([x for x in range(10) if x != d])
    out = (n - d + nd) * u
    return math.copysign(out, v) if v else out


def growth_ok(a0: float, b0: float, a1: float, b1: float, shown: float) -> bool:
    g0 = (a0 / b0 - 1) * (1 if b0 > 0 else -1)
    g1 = (a1 / b1 - 1) * (1 if b1 > 0 else -1)
    return (g1 > 0) == (g0 > 0) and 100 * abs(g1) >= shown


def harmonise(doc: Doc, rec: collections.Counter) -> None:
    """A later total printing the same values as an earlier one (one total built from two
    breakdowns) is set equal to it, and its parts are rescaled so that they still add up."""
    seen: dict[tuple, int] = {}
    for r in sorted(doc.derived):
        v = doc.vec(r)
        if not v or not any(t.digits >= 3 for t in v):
            continue
        key = tuple(round(t.value, 6) for t in v)
        if key not in seen:
            seen[key] = r
            continue
        how, parts = doc.derived[r]
        first = doc.vec(seen[key])
        if how != "sum" or any(p in doc.derived for p in parts):
            continue
        for pos in range(len(v)):
            target, now = first[pos].new, v[pos].new
            if target is None or not now:
                continue
            for p in parts:
                pc = doc.vec(p)[pos]
                pc.new = (pc.new if pc.new is not None else pc.value) * target / now
            v[pos].new = target
        rec["harmonised"] += 1


def noise(doc: Doc, rng: random.Random, sigma: float) -> dict:
    """Sets t.new for every token Z changes. Returns a record for the key."""
    rec: collections.Counter = collections.Counter()
    growth_by_cur = collections.defaultdict(list)
    for t, r, a, b in doc.growth:
        growth_by_cur[(r, a)].append(t)
    prior_of = {(r, a): b for r, ps in doc.pairs.items() for a, b in ps}
    for r in sorted(doc.rows):  # parts come before their totals
        cells = doc.rows[r][1]
        vidx = doc.vec_idx(r)
        derived = doc.derived.get(r)
        for c, t in enumerate(cells):  # every other level: its last digit redrawn
            if t.kind not in LEVELISH or t.new is not None or id(t) in doc.change_ids:
                continue
            if (derived and c in vidx) or ((r, c) in prior_of and t.kind != "shares"):
                continue
            t.new = redraw_last_digit(rng, t, t.value)
            rec["lsd"] += 1
        if derived:  # totals and differences from their parts
            how, parts = derived
            for pos, c in enumerate(vidx):
                pv = [doc.vec(p)[pos] for p in parts]
                pv = [(x.new if x.new is not None else x.value) for x in pv]
                cells[c].new = sum(pv) if how == "sum" else pv[0] - pv[1]
                rec["derived"] += 1
        for c, t in enumerate(cells):  # current-period leaves: x (1 + e), the growth's sign kept
            if (r, c) not in prior_of or t.new is not None or t.kind == "shares":
                continue
            b = cells[prior_of[(r, c)]]
            nb = b.new if b.new is not None else b.value
            links = growth_by_cur.get((r, c), [])
            for _ in range(30):
                t.new = t.value * (1 + rng.uniform(-sigma, sigma))
                if not links or not nb or not b.value or all(growth_ok(t.value, b.value, t.new, nb, tol(g)) for g in links):
                    break
            else:
                rec["growth_redraw_failed"] += 1
            rec["leaf"] += 1
    harmonise(doc, rec)
    for t, r, a, b in doc.change:
        ta, tb = doc.rows[r][1][a], doc.rows[r][1][b]
        t.new = (ta.new if ta.new is not None else ta.value) - (tb.new if tb.new is not None else tb.value)
        rec["change"] += 1
    for t, r, a, b in doc.growth:
        ta, tb = doc.rows[r][1][a], doc.rows[r][1][b]
        na = ta.new if ta.new is not None else ta.value
        nb = tb.new if tb.new is not None else tb.value
        if nb:
            g = (na / nb - 1) * 100 * (1 if nb > 0 else -1)
            if t.value and (g > 0) != (t.value > 0):
                t.new = t.value
                rec["growth_kept"] += 1
            else:
                t.new = g
            rec["growth"] += 1
    for pr, a, d in doc.margins:
        num, den = doc.vec(a), doc.vec(d)
        for c, t in enumerate(doc.rows[pr][1]):
            nv = num[c].new if num[c].new is not None else num[c].value
            dv = den[c].new if den[c].new is not None else den[c].value
            if dv:
                t.new = 100 * nv / dv
                rec["margin"] += 1
    cell_index = []  # table cells at absolute scale, for prose that repeats them
    for i, (label, cells) in doc.rows.items():
        scale = table_scale(doc, i)
        for t in cells:
            if t.new is not None and t.kind in ("level", "per_share", "pct"):
                cell_index.append((t, scale))
    line_e: dict[int, float] = {}
    line_d: dict[int, float] = {}
    same: dict[tuple, float] = {}
    for t in doc.toks:
        if t.new is not None or t.kind not in ("level", "per_share", "pct"):
            continue
        if t.row is not None:
            if t.kind == "pct":  # a percentage in a table that links to nothing
                t.new = shift_pct(rng, t.value, 100 * sigma)
                rec["pct_free"] += 1
            continue
        hit = match_cell(t, cell_index)
        if hit is not None:
            t.new = hit
            rec["prose_matched"] += 1
            continue
        unit = UNITS.get(t.m["unit"].strip().rstrip("s").lower(), 1.0) if t.m["unit"] else 1.0
        sk = (t.kind, round(abs(t.value) * unit, 6), t.dec)
        if sk in same:  # the same figure gets the same noise wherever it is repeated
            t.new = math.copysign(same[sk], t.value) if t.value else same[sk]
            rec["prose_free"] += 1
            continue
        if t.kind == "pct":
            d = line_d.setdefault(t.line, rng.uniform(-100 * sigma, 100 * sigma))
            t.new = t.value + d if (t.value + d) * t.value > 0 or t.value == 0 else t.value
        else:
            e = line_e.setdefault(t.line, rng.uniform(-sigma, sigma))
            t.new = t.value * (1 + e)
        same[sk] = abs(t.new)
        rec["prose_free"] += 1
    return dict(rec)


def shift_pct(rng: random.Random, v: float, bound: float) -> float:
    for _ in range(20):
        nv = v + rng.uniform(-bound, bound)
        if v == 0 or (nv > 0) == (v > 0):
            return nv
    return v


def table_scale(doc: Doc, i: int) -> float:
    for j in range(i, max(-1, i - 60), -1):
        m = SCALE_HEAD.search(doc.lines[j])
        if m:
            word = next((g for g in m.groups() if g), None)
            return {"thousands": 1e3, "millions": 1e6, "billions": 1e9}.get((word or "").lower(), 1.0)
    return 1.0


def match_cell(t: Tok, index: list[tuple[Tok, float]]) -> float | None:
    """A prose number equal, at its printed precision, to a table cell: the cell's new value."""
    if t.digits < 3:
        return None  # too coarse to tie to one cell
    unit = UNITS.get(t.m["unit"].strip().rstrip("s").lower(), 1.0) if t.m["unit"] else 1.0
    hits = set()
    for c, scale in index:
        if c.kind != t.kind:
            continue
        if t.kind == "pct":
            if c.why == "growth" and abs(abs(c.value) - abs(t.value)) <= tol(t):
                hits.add(round(abs(c.new), 9))
            continue
        a, b = abs(t.value) * unit, abs(c.value) * scale
        if b and abs(a - b) <= tol(t) * unit + tol(c) * scale:
            hits.add(round(abs(c.new) * scale / unit, 9))
    if len(hits) != 1:
        return None  # no cell, or several that disagree
    h = hits.pop()
    return math.copysign(h, t.value) if t.value else h


def scale_all(doc: Doc, f: float, g: float) -> None:
    for t in doc.toks:
        base = t.new if t.new is not None else t.value
        if t.kind == "level":
            t.new = base * f
        elif t.kind == "per_share":
            t.new = base * g
        elif t.kind == "shares":
            t.new = base * f / g


def render_number(t: Tok) -> str:
    m = t.m
    v = abs(t.new)
    dec = t.dec
    if t.kind != "pct" and v and t.digits >= 2:
        while v < 10 ** (1 - dec) and dec < 3 and t.dec > 0:
            dec += 1  # keep two significant digits when a scaled figure becomes small
    commas = "," in m["num"] or (v >= 1000 and t.kind != "pct" and t.row is not None)
    s = f"{v:,.{dec}f}" if commas else f"{v:.{dec}f}"
    if m["num"].startswith(".") and s.startswith("0."):
        s = s[1:]
    sign = m["neg"] if m["neg"] else ""
    out = f"{m['cur0']}{m['open']}{sign}{m['cur']}{s}{m['close']}{m['pct']}{m['unit']}"
    return out


def apply_numbers(doc: Doc) -> tuple[str, list[dict]]:
    parts, edits, pos = [], [], 0
    for t in doc.toks:
        if t.new is None:
            continue
        new = render_number(t)
        if new == t.raw:
            continue
        parts.append(doc.text[pos: t.start])
        parts.append(new)
        edits.append({"at": t.start, "old": t.raw, "new": new, "kind": t.kind, "why": t.why})
        pos = t.end
    parts.append(doc.text[pos:])
    return "".join(parts), edits


# ---------------------------------------------------------------------------------------------
# Switch P on periods

MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
          "Jan\\.|Feb\\.|Mar\\.|Apr\\.|Jun\\.|Jul\\.|Aug\\.|Sept?\\.|Oct\\.|Nov\\.|Dec\\.")
WEEKDAYS = r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"


def rel(y: int, year: int) -> str:
    d = y - year
    return "Year T" if d == 0 else f"Year T{d:+d}"


def periods(text: str, year: int) -> tuple[str, dict]:
    counts = collections.Counter()

    def yy(s: str) -> int:
        n = int(s)
        return n if n > 1900 else 2000 + n

    def sub(pat, fn, s, name):
        new, n = re.subn(pat, fn, s, flags=re.I)
        counts[name] += n
        return new

    s = text
    s = sub(rf"\b({MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+((?:19|20)\d\d)\b", lambda m: "[date]", s, "dates")
    s = sub(rf"\b({MONTHS})\s+((?:19|20)\d\d)\b", lambda m: f"[month] {rel(int(m.group(2)), year)}", s, "month_years")
    s = sub(rf"\b({MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?\b", lambda m: "[date]", s, "dates")
    s = sub(rf"\b({MONTHS})(?![a-z])", lambda m: "[month]", s, "months")
    s = sub(WEEKDAYS, lambda m: "[day]", s, "weekdays")
    s = sub(r"\b([1-4])Q\s?['’]?(\d{2}|\d{4})\b", lambda m: f"{m.group(1)}Q {rel(yy(m.group(2)), year)}", s, "quarter_codes")
    s = sub(r"\bQ([1-4])\s?['’]?((?:19|20)?\d{2})\b", lambda m: f"Q{m.group(1)} {rel(yy(m.group(2)), year)}", s, "quarter_codes")
    s = sub(r"\b(FY|F)\s?['’]?((?:19|20)?\d{2})\b", lambda m: f"FY {rel(yy(m.group(2)), year)}", s, "fiscal_codes")
    s = sub(r"(?<![\d,.$])\b((?:199|20[0-3])\d)\b(?![\d,.%])", lambda m: rel(int(m.group(1)), year), s, "years")
    s = sub(r"['’]((?:[0-3])\d)\b", lambda m: " " + rel(2000 + int(m.group(1)), year), s, "short_years")
    return s, dict(counts)


def residual_years(text: str) -> int:
    return len(re.findall(r"(?<![\d,.$])\b(?:199|20[0-3])\d\b(?![\d,.%])", text)) + len(re.findall(rf"\b({MONTHS})(?![a-z])", text))


# ---------------------------------------------------------------------------------------------
# Switch N on names

SUFFIX = re.compile(
    r"\b(inc|incorporated|corp|corporation|co|company|companies|ltd|limited|plc|llc|lp|l\.p|n\.v|s\.a|ag|se|"
    r"holdings?|group|the|trust|bancorp|bancshares|de|new|del|md|nv|tx|ny|ca)\b\.?", re.I)
GENERIC = {"first", "american", "united", "general", "national", "international", "global", "new", "great",
           "southern", "northern", "western", "eastern", "pacific", "atlantic", "central", "capital", "financial",
           "energy", "royal", "standard", "universal", "public", "service", "services", "home", "health", "bank"}
KEEP = {"U.S", "US", "USA", "GAAP", "EBITDA", "EBIT", "EPS", "IFRS", "SEC", "CEO", "CFO", "COO", "FX", "EMEA",
        "APAC", "LATAM", "EU", "UK", "Europe", "Asia", "China", "Japan", "Canada", "Mexico", "America", "Americas",
        "North", "South", "Latin", "International", "Africa", "India", "Brazil", "Germany", "France", "Middle",
        "East", "Company", "Board", "Exchange", "Commission", "Securities", "Act", "Nasdaq", "NYSE", "Form",
        "Federal", "Reserve", "COVID", "Covid", "GDP", "AI", "Q1", "Q2", "Q3", "Q4", "T", "Year", "Inc"}
TITLES = (r"(?:chairman|chairwoman|chair|chief\s+executive\s+officer|chief\s+financial\s+officer|"
          r"chief\s+operating\s+officer|chief\s+accounting\s+officer|president|founder|ceo|cfo|coo|"
          r"executive\s+vice\s+president|senior\s+vice\s+president|vice\s+president|treasurer|investor\s+relations)")
PERSON = r"((?:Mr\.|Ms\.|Mrs\.|Dr\.)\s)?([A-Z][a-z]+(?:\s[A-Z]\.)?(?:\s[A-Z][A-Za-z'’\-]+){1,2})"
COMMON: set[str] = set()


def common_words() -> set[str]:
    if not COMMON:
        for w in WORDS.read_text(encoding="utf-8", errors="ignore").split():
            if w.islower():
                COMMON.add(w)
    return COMMON


def is_common(word: str) -> bool:
    """A word, or a plain inflection of one, that the system word list holds in lower case."""
    w = word.lower().rstrip("'’")
    if w.endswith(("'s", "’s")):
        w = w[:-2]
    c = common_words()
    forms = {w, w[:-1], w[:-2], w[:-3], w[:-3] + "y", w[:-1] + "e", w[:-2] + "e", w[:-3] + "e", w[:-4]}
    if w.endswith("ly"):
        forms |= {w[:-2], w[:-4] + "le"}
    return any(len(f) >= 3 and f in c for f in forms) or (len(w) < 3 and w in c)


def name_core(name: str) -> list[str]:
    s = re.sub(r"/[A-Z]{2,3}/?", " ", name)
    s = SUFFIX.sub(" ", s.replace("&", " & "))
    s = re.sub(r"[^\w&' -]", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" &-")
    out = []
    if len(s) >= 3:
        out.append(s)
        words = s.split()
        if len(words) > 1 and len(words[0]) >= 4 and words[0].lower() not in GENERIC:
            out.append(words[0])
        if len(words) > 1:
            out.append("".join(w[0] for w in words if w[0].isalpha()) if len(words) >= 3 else "")
    return [x for x in out if x and len(x) >= 3]


def identity(cik: str, zf: zipfile.ZipFile) -> dict:
    d = json.loads(zf.read(f"CIK{cik}.json"))
    names = [d.get("name") or ""] + [x.get("name") or "" for x in d.get("formerNames") or []]
    cores = []
    for n in names:
        cores += name_core(n)
    cities = {(a or {}).get("city") or "" for a in (d.get("addresses") or {}).values()}
    return {
        "names": sorted({c for c in cores if c}, key=len, reverse=True),
        "tickers": [t for t in d.get("tickers") or [] if t and len(t) >= 2],
        "cities": sorted(c.title() for c in cities if c and len(c) >= 4 and c.lower() not in GENERIC),
    }


def names(text: str, ident: dict, rng: random.Random) -> tuple[str, dict]:
    counts = collections.Counter()
    letter = rng.choice("BCDFGHJKLMNPQRSTVWXZ")
    pseudo = f"Company {letter}"
    s = text
    s, n = re.subn(r"\((?:NYSE|NASDAQ|Nasdaq|NYSE American|NYSE MKT|OTCQX|OTC|TSX|LSE)[^)]{0,30}\)", "", s)
    counts["exchange_tags"] += n
    s, n = re.subn(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", "[email]", s)
    counts["emails"] += n
    s, n = re.subn(r"\b(?:https?://)?(?:www\.)?[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|co|us|biz|info)(?:/[^\s)]*)?", "[website]", s, flags=re.I)
    counts["websites"] += n
    s, n = re.subn(r"\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b", "[phone]", s)
    counts["phones"] += n
    # people next to a title
    people = set()
    for m in re.finditer(PERSON + r",\s+(?:our\s+|the\s+)?(?:[\w\s,]{0,40}?)" + TITLES, s):
        people.add(m.group(2))
    for m in re.finditer(TITLES + r"\s+(?:and\s+\w+\s+)?" + PERSON, s, re.I):
        people.add(m.group(3) if m.lastindex and m.lastindex >= 3 else m.group(2))
    for m in re.finditer(r"(?:Contacts?|Media|Investors?|Investor Relations)\s*:?\s*\n?\s*" + PERSON, s):
        people.add(m.group(2))
    people = {p for p in people if p and len(p.split()) >= 2}
    people = {p for p in people if not re.search(TITLES, p, re.I)}
    pmap = {p: f"[Person {i + 1}]" for i, p in enumerate(sorted(people, key=len, reverse=True))}
    for p in people:
        last = p.split()[-1]
        if len(last) >= 4:
            pmap.setdefault(f"Mr. {last}", pmap[p])
            pmap.setdefault(f"Ms. {last}", pmap[p])
    s = redact(s, pmap, case_sensitive=True)
    counts["people"] += len(people)
    # the company, its tickers and its city
    cmap = {n: pseudo for n in ident["names"]}
    cmap |= {c: "[City]" for c in ident["cities"]}
    s = redact(s, cmap)
    s = redact(s, {t: pseudo for t in ident["tickers"]}, case_sensitive=True)
    s = re.sub(re.escape(pseudo) + r",?\s+(?:Inc|Corp|Corporation|Co|Ltd|plc|PLC|LLC|N\.V|S\.A|Holdings|Group)\b\.?\s?,?",
               pseudo + " ", s)
    # trademarks
    prods = set()
    for m in re.finditer(r"((?:[A-Z][\w+\-]*\s?){1,4})(?:™|®|℠|\(R\)|\(TM\))", s):
        prods.add(m.group(1).strip())
    prmap = {p: f"[Product {i + 1}]" for i, p in enumerate(sorted(prods, key=len, reverse=True)) if len(p) >= 3}
    s = re.sub(r"(™|®|℠|\(R\)|\(TM\))", "", s)
    s = redact(s, prmap, case_sensitive=True)
    counts["products"] += len(prmap)
    # a dateline at the start of a line
    s, n = re.subn(r"(?m)^(\s*)([A-Z][A-Z .'\-]{2,}(?:,\s*[A-Z][A-Za-z. ]+)?)\s*[,–—-]+\s*(?=(?:\[date\]|" + MONTHS + r"))",
                   r"\1[City] - ", s)
    counts["datelines"] += n
    # other capitalised words that are not common English
    other = {}
    for m in re.finditer(r"\b(?:[A-Z][A-Za-z'’]{2,}|[a-z]{1,3}[A-Z][A-Za-z]+)\b", s):
        w = m.group(0)
        base = w[:-2] if w.endswith(("'s", "’s")) else w
        if base in KEEP or is_common(base):
            continue
        if re.fullmatch(MONTHS.replace("\\.", ""), base) or base in ("Name", "Person", "Product", "City", "Company"):
            continue
        other.setdefault(base, f"[Name {len(other) + 1}]")
    s = redact(s, other, case_sensitive=True)
    counts["other_names"] += len(other)
    return s, {"pseudonym": pseudo, "people": pmap, "products": prmap, "other": other, "counts": dict(counts)}


def residual_identity(text: str, ident: dict) -> list[str]:
    return find_terms(text, ident["names"] + ident["cities"]) + find_terms(text, ident["tickers"], case_sensitive=True)


# ---------------------------------------------------------------------------------------------
# The ratio sheet

def load_series() -> dict[str, list[dict]]:
    by = collections.defaultdict(list)
    with open(SERIES, encoding="utf-8") as fh:
        for l in fh:
            r = json.loads(l)
            by[r["cik"]].append(r)
    for v in by.values():
        v.sort(key=lambda r: r["end"])
    return by


def quarters_between(a: str, b: str) -> int:
    ya, ma = int(a[:4]), int(a[5:7])
    yb, mb = int(b[:4]), int(b[5:7])
    return round(((yb - ya) * 12 + (mb - ma)) / 3)


def ratios(r: dict) -> list[float | None]:
    """Year-on-year revenue growth, operating margin and net margin of one quarter, in percent."""
    g = r.get("g")
    om = r["operating_income"] / r["rev"] if r.get("operating_income") is not None and r["rev"] else None
    nm = r["net_income"] / r["rev"] if r.get("net_income") is not None and r["rev"] else None
    return [None if v is None else 100 * v for v in (g, om, nm)]


def sheet_rows(series: list[dict], filed_before: str, quarter_end: str) -> list[dict]:
    rows = [r for r in series if r["filed"] < filed_before and r["end"] < quarter_end][-SHEET_QUARTERS:]
    return [{"end": r["end"], "back": quarters_between(r["end"], quarter_end), "x": ratios(r)} for r in reversed(rows)]


def noised(rows: list[dict], rng: random.Random, bound: float) -> list[dict]:
    return [{**r, "x": [None if v is None else (shift_pct(rng, v, bound) if bound else v) for v in r["x"]]} for r in rows]


def sheet(series: list[dict], filed_before: str, quarter_end: str, p: bool, z: bool, rng: random.Random, sigma: float) -> str:
    rows = sheet_rows(series, filed_before, quarter_end)
    if not rows:
        return "Ratios from earlier filings: none available.\n"
    if z:
        rows = noised(rows, rng, 100 * sigma)
    out = ["Ratios from filings made before this release (computed by code from values as first filed):",
           "  quarter | revenue growth, year on year | operating margin | net margin"]
    for r in rows:
        label = f"{r['back']} quarters before this one" if p else f"quarter ended {r['end']}"
        out.append(f"  {label} | " + " | ".join("n/a" if v is None else f"{v:.1f}%" for v in r["x"]))
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------------------------
# The rule attacker

DOSES = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)  # additive noise bound on each ratio, in points


class Library:
    """Every training and development company's quarterly ratios as first filed."""

    def __init__(self, series: dict[str, list[dict]]):
        import numpy as np
        self.np = np
        self.ciks, self.ends, self.x = [], [], []
        for cik, rows in series.items():
            self.ciks.append(cik)
            self.ends.append({r["end"]: i for i, r in enumerate(rows)})
            self.x.append(np.array([[np.nan if v is None else v for v in ratios(r)] for r in rows], dtype=float))

    def rank(self, query: list[dict], truth: str, dated: bool) -> int:
        """Rank of the true company by its best alignment; dated: the quarter-end dates are known."""
        np = self.np
        q = np.array([[np.nan if v is None else v for v in r["x"]] for r in query], dtype=float)
        backs = [r["back"] - query[0]["back"] for r in query]
        best = []
        for ci, cik in enumerate(self.ciks):
            x, idx = self.x[ci], self.ends[ci]
            ends = sorted(idx)
            anchors = [query[0]["end"]] if dated else ends
            d_best = np.inf
            for anchor in anchors:
                if anchor not in idx:
                    continue
                pos = ends.index(anchor)
                rows = []
                for b in backs:
                    j = pos - b
                    rows.append(x[idx[ends[j]]] if 0 <= j < len(ends) else np.full(3, np.nan))
                m = np.array(rows)
                diff = np.abs(m - q)
                ok = ~np.isnan(diff)
                if ok.sum() < max(3, q.size // 2):
                    continue
                d = diff[ok].mean()
                if d < d_best:
                    d_best = d
            best.append(d_best)
        best = np.array(best)
        t = self.ciks.index(truth)
        return int((best < best[t]).sum()) + 1 if np.isfinite(best[t]) else len(best)


def fingerprint(a: argparse.Namespace) -> None:
    need_drive()
    out = Path(a.out) if a.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    series = load_series()
    lib = Library(series)
    eps = sample(a.per_cell, SEED)
    res = collections.defaultdict(list)
    for i, ep in enumerate(eps):
        rows = sheet_rows(series.get(ep["cik"], []), ep["filing_date"], ep["quarter_end"])
        if len(rows) < 4:
            continue
        for k, dose in enumerate(DOSES):
            q = noised(rows, random.Random(SEED + 7919 * i + k), dose)
            for dated in (True, False):
                rk = lib.rank(q, ep["cik"], dated)
                res[(dose, dated, ep["tier"])].append(rk)
                res[(dose, dated, "all")].append(rk)
        print(f"[fingerprint] {i + 1}/{len(eps)}", flush=True)
    report = {"companies": len(lib.ciks), "episodes": len({0}) and len(eps), "doses_points": list(DOSES), "rows": []}
    for (dose, dated, tier), ranks in sorted(res.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0])):
        report["rows"].append({"dose": dose, "dates_shown": dated, "tier": tier, "n": len(ranks),
                               "top1": round(sum(r == 1 for r in ranks) / len(ranks), 3),
                               "top10": round(sum(r <= 10 for r in ranks) / len(ranks), 3),
                               "median_rank": statistics.median(ranks)})
    (out / "fingerprint.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for r in report["rows"]:
        if r["tier"] == "all":
            print(r)


# ---------------------------------------------------------------------------------------------
# Views

def make_view(raw: str, ep: dict, ident: dict, series: list[dict], bits: tuple[int, int, int, int], seed: int) -> tuple[str, dict]:
    n, p, s_, z = bits
    rng = random.Random(seed)
    year = int(ep["quarter_end"][:4])
    doc = Doc(clean(raw), year)
    key: dict = {"bits": bits, "seed": seed, "sigma": SIGMA if z else 0.0}
    if z:
        key["noise"] = noise(doc, rng, SIGMA)
    if s_:
        f, g = away_from_ten(rng, 0.2, 5.0), away_from_ten(rng, 0.3, 3.0)
        key["f"], key["g"] = f, g
        scale_all(doc, f, g)
    body, edits = apply_numbers(doc)
    key["edits"] = edits
    top = sheet(series, ep["filing_date"], ep["quarter_end"], bool(p), bool(z), rng, SIGMA)
    text = top + "\nThe earnings release:\n\n" + body
    if p:
        text, key["periods"] = periods(text, year)
    if n:
        text, key["names"] = names(text, ident, rng)
    key["types"] = dict(collections.Counter(t.kind for t in doc.toks))
    key["links"] = {"derived_rows": len(doc.derived), "growth": len(doc.growth), "change": len(doc.change),
                    "margin_rows": len(doc.margins), "blocks": len(set(doc.block_of.values())),
                    "rows_with_pairs": sum(1 for v in doc.pairs.values() if v), "rows": len(doc.rows)}
    return text, key


def text_path(ep: dict) -> Path | None:
    for d in TEXT_DIRS:
        p = d / f"{ep['cik']}_{ep['accession']}.txt"
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def sample(n_per_cell: int, seed: int) -> list[dict]:
    rows = [json.loads(l) for l in LIST.read_text(encoding="utf-8").splitlines() if l]
    rows = [r for r in rows if r["labelled"] and r["side"] in SIDES]
    rows = [r for r in rows if text_path(r)]
    rng = random.Random(seed)
    out = []
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r["post_cutoff"], r["tier"])].append(r)
    for key in sorted(cells):
        rs = sorted(cells[key], key=lambda r: r["accession"])
        out += rng.sample(rs, min(n_per_cell, len(rs)))
    return out


def build(a: argparse.Namespace) -> None:
    need_drive()
    eps = sample(a.per_cell, SEED)
    series = load_series()
    zf = zipfile.ZipFile(BULK)
    out = Path(a.out) if a.out else OUT
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "views.jsonl", "w", encoding="utf-8") as fv, open(out / "keys.jsonl", "w", encoding="utf-8") as fk:
        for i, ep in enumerate(eps):
            raw = text_path(ep).read_text(encoding="utf-8")
            ident = identity(ep["cik"], zf)
            for v, bits in enumerate(VIEWS):
                seed = SEED * 1000 + i * 10 + v
                text, key = make_view(raw, ep, ident, series.get(ep["cik"], []), bits, seed)
                vid = f"{i:03d}-{v}"
                fv.write(json.dumps({"id": vid, "episode": i, "view": v, "bits": bits, "text": text}) + "\n")
                fk.write(json.dumps({"id": vid, "cik": ep["cik"], "accession": ep["accession"], "tier": ep["tier"],
                                     "post_cutoff": ep["post_cutoff"], "quarter_end": ep["quarter_end"],
                                     "identity": ident, **key}) + "\n")
    print(f"[build] {len(eps)} episodes x {len(VIEWS)} views -> {out}")


# ---------------------------------------------------------------------------------------------
# Check

def check(a: argparse.Namespace) -> None:
    out = Path(a.out) if a.out else OUT
    views = {j["id"]: j for j in map(json.loads, open(out / "views.jsonl", encoding="utf-8"))}
    keys = {j["id"]: j for j in map(json.loads, open(out / "keys.jsonl", encoding="utf-8"))}
    stats = collections.defaultdict(list)
    fails = collections.Counter()
    for vid, v in views.items():
        k = keys[vid]
        n, p, s_, z = v["bits"]
        t = v["text"]
        if n:
            res = residual_identity(t, k["identity"])
            stats["residual_identity"].append(len(res))
            if res:
                fails["identity term left with N on"] += 1
        if p:
            ry = residual_years(t)
            stats["residual_years"].append(ry)
            if ry:
                fails["year or month left with P on"] += 1
        if s_ or z:
            ed = k["edits"]
            byk = collections.Counter(e["kind"] for e in ed)
            for kind in ("level", "per_share", "shares", "pct"):
                stats[f"edited_{kind}"].append(byk.get(kind, 0))
            total_levels = k["types"].get("level", 0)
            stats["levels_edited_share"].append(byk.get("level", 0) / total_levels if total_levels else 1.0)
            if s_ and not z:
                f, g = k["f"], k["g"]
                bad = 0
                for e in ed:
                    if e["kind"] == "pct":
                        bad += 1  # S alone must never touch a percentage
                stats["pct_edited_under_S"].append(bad)
                if bad:
                    fails["percentage edited under S alone"] += 1
            if z:
                flips = 0
                for e in ed:
                    if e["kind"] == "pct" and e["why"] == "growth":
                        o, nw = num_of(e["old"]), num_of(e["new"])
                        if o is not None and nw is not None and o != 0 and (nw == 0 or (o > 0) != (nw > 0)):
                            flips += 1
                stats["growth_sign_lost"].append(flips)
        for kk, vv in k["types"].items():
            stats[f"type_{kk}"].append(vv)
        for kk, vv in k["links"].items():
            stats[f"link_{kk}"].append(vv)
        stats["chars"].append(len(t))
    report = {"views": len(views), "fails": dict(fails),
              "means": {k: round(statistics.mean(v), 3) for k, v in sorted(stats.items()) if v},
              "max": {k: max(v) for k, v in sorted(stats.items()) if v}}
    (out / "check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def num_of(s: str) -> float | None:
    m = NUM.search(s)
    if not m:
        return None
    v = float(m.group("num").replace(",", ""))
    neg = bool(m.group("neg")) or (bool(m.group("open")) and bool(m.group("close")))
    return -v if neg else v


def show(a: argparse.Namespace) -> None:
    out = Path(a.out) if a.out else OUT
    vid = f"{a.episode:03d}-{a.view}"
    for j in map(json.loads, open(out / "views.jsonl", encoding="utf-8")):
        if j["id"] == vid:
            print(j["text"][: a.chars])
            return
    sys.exit(f"no view {vid}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--out", default=None, help="output directory (default: s2/exp0022 on the drive)")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--per-cell", type=int, default=4)
    b.set_defaults(fn=build)
    sub.add_parser("check").set_defaults(fn=check)
    fp = sub.add_parser("fingerprint")
    fp.add_argument("--per-cell", type=int, default=4)
    fp.set_defaults(fn=fingerprint)
    s = sub.add_parser("show")
    s.add_argument("--episode", type=int, default=0)
    s.add_argument("--view", type=int, default=7)
    s.add_argument("--chars", type=int, default=6000)
    s.set_defaults(fn=show)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
