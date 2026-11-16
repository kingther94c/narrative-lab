"""EXP-0005: EarningsExam v0 generator (sub-study S1, step S1-a.1).

Builds auto-graded questions from 8-K earnings releases (Exhibit 99.1) already on the external
drive (fetched by EXP-0003), with gold answers from SEC XBRL company facts. An answer is kept only
when two sources agree. XBRL gives the value tagged in the 10-Q or 10-K for the same period, first
filed on or after the release. The release must show that same figure in a table row whose label
names the metric, at the table's stated scale.

Sections (plan: docs/plans/2026-11-15_substudy_s1_plan.md, §3):

- B1 lookup: one reported figure for a stated period (revenue, operating income, net income,
  diluted EPS, gross profit).
- B2 computation: gross, operating and net margin, year-on-year revenue growth, year-on-year
  change in diluted EPS. Every input is itself verified as in B1, in the same excerpt.

Held-out templates (rule 3 of plan §3): the metric "gross profit", the "net margin" item and the
second phrasing appear only on the test side.

Splits come from ``split_v1``. Train items come from pre-cutoff releases of training companies;
development items from development companies; test items from post-cutoff releases of test
companies. Post-cutoff releases of training companies and pre-cutoff releases of test companies
are not used.

Gold values are the figures as the release displays them, at the scale asked; the XBRL value
confirms them. An answer is right when ``|answer - gold| <= tolerance["abs"]``: half a unit of the
displayed figure for B1, 0.15 percentage points for percentages, half a cent for EPS changes.

An engineering measurement: it reports yield by side and section, with no hypothesis. Claude
must not read test items (changelog, 2026-11-14), so ``--show`` refuses the test side.

    conda run --no-capture-output -n py313 python research/experiments/exp0005_earnings_exam.py build
    conda run --no-capture-output -n py313 python research/experiments/exp0005_earnings_exam.py show --side dev --n 12
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import hashlib
import json
import random
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import split_v1  # noqa: E402

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
PAIRS = DRIVE / "edgar" / "pairs"
TEXTS = DRIVE / "edgar" / "releases"
FACTS_ZIP = DRIVE / "edgar" / "xbrl" / "companyfacts-2026-11-14.zip"
OUT = DRIVE / "s1" / "exam_v0"
TOKENIZER = "/Volumes/Seagate Backup Plus Drive/DATA/huggingface/models--Qwen--Qwen3.5-0.8B"
CUTOFF = "2026-06-30"
MAX_TOKENS = 400  # excerpt budget, plan §3 rule 4

METRICS = {
    "revenue": {
        "name": "total revenue",
        "concepts": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                     "RevenueFromContractWithCustomerIncludingAssessedTax", "RevenuesNetOfInterestExpense"],
        "label": re.compile(r"^(total\s+)?(net\s+)?(operating\s+)?(revenues?|sales|net\s+sales)(,?\s*net)?\b(?!.*\b(cost|marketing|expense))", re.I),
        "unit": "USD",
    },
    "operating_income": {
        "name": "operating income (loss)",
        "concepts": ["OperatingIncomeLoss"],
        "label": re.compile(r"^(total\s+)?(operating\s+(income|profit|loss|earnings)|(income|loss|earnings)\s*(\(loss\)\s*)?from\s+operations)", re.I),
        "unit": "USD",
    },
    "net_income": {
        "name": "net income (loss) attributable to the company",
        "concepts": ["NetIncomeLoss"],
        "label": re.compile(r"^net\s+(income|earnings|loss)", re.I),
        "unit": "USD",
    },
    "eps_diluted": {
        "name": "diluted earnings (loss) per share",
        "concepts": ["EarningsPerShareDiluted"],
        "label": re.compile(r"diluted", re.I),
        "unit": "USD/shares",
    },
    "gross_profit": {
        "name": "gross profit",
        "concepts": ["GrossProfit"],
        "label": re.compile(r"^(total\s+)?gross\s+(profit|margin)\b", re.I),
        "unit": "USD",
    },
}
HELD_OUT_METRICS = {"gross_profit"}
HELD_OUT_B2 = {"net_margin"}

NUM = re.compile(r"\(?-?\$?\s?\d[\d,]*(?:\.\d+)?\)?%?")
SCALE = re.compile(r"\bin\s+(thousands|millions|billions)\b", re.I)
SCALES = {"thousands": 1e3, "millions": 1e6, "billions": 1e9}


# ---------------------------------------------------------------------------------------------
# Release text

def parse_number(tok: str) -> tuple[float, int] | None:
    """Value and number of decimals shown, or None for years, percentages and the like."""
    if tok.endswith("%"):
        return None
    neg = tok.startswith("(") and tok.endswith(")")
    core = tok.strip("()$ ").replace(",", "")
    if core.startswith("-"):
        neg, core = True, core[1:]
    if not re.fullmatch(r"\d+(\.\d+)?", core):
        return None
    dec = len(core.split(".")[1]) if "." in core else 0
    v = float(core)
    return (-v if neg else v), dec


def table_rows(lines: list[str]) -> list[tuple[int, str, list[tuple[float, int, int]]]]:
    """(line index, label, [(value, decimals, significant digits)]) for lines that look like rows."""
    rows = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or len(s) > 400:
            continue
        m = re.search(r"(\s{2,}|\$|\t)", s)
        if not m:
            continue
        label = s[: m.start()].strip(" .:–-")
        rest = s[m.start():]
        if not label or not re.search(r"[A-Za-z]", label) or len(label) > 120:
            continue
        vals = []
        for tok in NUM.findall(rest):
            p = parse_number(tok.strip())
            if p is None:
                continue
            digits = len(re.sub(r"\D", "", tok).lstrip("0")) or 1
            vals.append((p[0], p[1], digits))
        if vals:
            rows.append((i, label, vals))
    return rows


def scale_for(lines: list[str], i: int) -> tuple[float | None, int | None]:
    for j in range(i, max(-1, i - 60), -1):
        m = SCALE.search(lines[j])
        if m:
            return SCALES[m.group(1).lower()], j
    return None, None


def matches(value: float, decimals: int, digits: int, scale: float, target: float, per_share: bool) -> bool:
    if per_share:
        if decimals < 2 and abs(value) < 10:
            return False
        return abs(value - target) <= 0.5 * 10 ** (-decimals) + 1e-9
    if digits < 3:
        return False
    return abs(value * scale - target) <= 0.5 * 10 ** (-decimals) * scale + 1e-6


# ---------------------------------------------------------------------------------------------
# XBRL company facts

class Facts:
    def __init__(self):
        self.z = zipfile.ZipFile(FACTS_ZIP)
        self.names = set(self.z.namelist())

    def load(self, cik: str) -> dict:
        name = f"CIK{split_v1.cik10(cik)}.json"
        if name not in self.names:
            return {}
        return json.loads(self.z.read(name)).get("facts", {}).get("us-gaap", {})


def days(a: str, b: str) -> int:
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def period_for(gaap: dict, filed_on: str) -> tuple[str, str, str] | None:
    """The (start, end, kind) of the latest quarter or year the release reports.

    Taken from facts of the core metrics whose period ended within 120 days before the release and
    that were first filed in a 10-Q or 10-K from 3 days before to 75 days after it.
    """
    best = None
    for spec in METRICS.values():
        for c in spec["concepts"]:
            for r in gaap.get(c, {}).get("units", {}).get(spec["unit"], []):
                if "start" not in r or r.get("form") not in ("10-Q", "10-K", "10-Q/A", "10-K/A"):
                    continue
                lag = days(r["end"], filed_on)
                gap = days(filed_on, r["filed"])
                if not (0 <= lag <= 120 and -3 <= gap <= 75):
                    continue
                d = days(r["start"], r["end"])
                kind = "quarter" if 80 <= d <= 100 else "year" if 350 <= d <= 380 else None
                if kind is None:
                    continue
                key = (r["end"], kind == "quarter")
                if best is None or key > best[0]:
                    best = (key, (r["start"], r["end"], kind))
    return best[1] if best else None


def value_for(gaap: dict, metric: str, start: str, end: str, filed_on: str, first_filed_any: bool = False):
    """First-filed value of a metric for an exact period: (value, concept, accession) or None."""
    spec = METRICS[metric]
    for c in spec["concepts"]:
        rows = [r for r in gaap.get(c, {}).get("units", {}).get(spec["unit"], [])
                if r.get("start") and abs(days(r["start"], start)) <= 3 and abs(days(r["end"], end)) <= 3]
        if not first_filed_any:
            rows = [r for r in rows if days(filed_on, r["filed"]) >= -3]
        if rows:
            r = min(rows, key=lambda r: r["filed"])
            return r["val"], c, r["accn"]
    return None


def shift_year(d: str) -> str:
    x = dt.date.fromisoformat(d)
    try:
        return x.replace(year=x.year - 1).isoformat()
    except ValueError:
        return x.replace(year=x.year - 1, day=28).isoformat()


# ---------------------------------------------------------------------------------------------
# Items

def long_date(d: str) -> str:
    x = dt.date.fromisoformat(d)
    return f"{x.strftime('%B')} {x.day}, {x.year}"


def find_row(lines, rows, metric: str, target: float):
    """(line index, value, column) of the first row whose label and figure match the target."""
    per_share = METRICS[metric]["unit"] == "USD/shares"
    for i, label, vals in rows:
        if not METRICS[metric]["label"].search(label):
            continue
        if metric == "eps_diluted" and not re.search(r"diluted", label, re.I):
            continue
        if metric != "eps_diluted" and re.search(r"per\s+share|margin\s*%|%", label, re.I) and metric != "gross_profit":
            continue
        scale, _ = (1.0, None) if per_share else scale_for(lines, i)
        if scale is None:
            continue
        for col, (v, dec, digits) in enumerate(vals):
            if matches(v, dec, digits, scale, target, per_share):
                return i, v, col, scale, dec
    return None


TITLE = re.compile(r"statements?\s+of|balance\s+sheets?|\breports?\b|^page\s+\d+|framework|guidance|reconciliation|non-gaap", re.I)


def keep(line: str) -> bool:
    """Excerpt lines: drop contact lines (e-mail addresses, phone numbers)."""
    return bool(line.strip()) and "@" not in line and not re.search(r"\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}", line)


def excerpt(lines: list[str], need: list[int], count) -> tuple[str, int] | None:
    """Lines from just above the scale header to the last needed row, within the token budget."""
    lines = [l if keep(l) else "" for l in lines]
    lo, hi = min(need), max(need)
    _, sline = scale_for(lines, lo)
    start = max(0, (sline if sline is not None else lo) - 4)
    # walk back to the table title: stop at a blank line followed by text
    for j in range(start, max(-1, start - 6), -1):
        if lines[j].strip() == "":
            start = j + 1
            break
    end = hi + 1
    text = "\n".join(l.rstrip() for l in lines[start:end] if l.strip())
    n = count(text)
    if n > MAX_TOKENS:
        # drop lines between the header block and the needed rows, keeping the first 8 lines
        head = [l.rstrip() for l in lines[start:min(start + 8, lo)] if l.strip()]
        body = [l.rstrip() for l in lines[lo:end] if l.strip()]
        text = "\n".join(head + ["[...]"] + body)
        n = count(text)
        if n > MAX_TOKENS:
            return None
    # extend downwards while the budget allows, so the needed row is not always the last line
    k = end
    while k < len(lines) and k < end + 12:
        if not lines[k].strip():
            if k + 1 < len(lines) and not lines[k + 1].strip():
                break
            k += 1
            continue
        if not NUM.search(lines[k]) and (TITLE.search(lines[k]) or lines[k].strip().isupper()):
            break  # the next table or section starts here
        cand = text + "\n" + lines[k].rstrip()
        m = count(cand)
        if m > MAX_TOKENS:
            break
        text, n, k = cand, m, k + 1
    return text, n


PHRASING = {
    "p1": "According to the excerpt from {company}'s earnings release, what was its {what} for the {period}?",
    "p2": "From the financial statements below, report {company}'s {what} for the {period}.",
}


def unit_text(metric: str, ask_scale: str) -> str:
    if METRICS[metric]["unit"] == "USD/shares":
        return "Give the answer in US dollars per share."
    return f"Give the answer in {ask_scale} of US dollars."


def make_items(t: dict, text: str, gaap: dict, count, rng: random.Random, side: str) -> tuple[list[dict], str]:
    per = period_for(gaap, t["filing_date"])
    if per is None:
        return [], "no XBRL period"
    start, end, kind = per
    period = f"three months ended {long_date(end)}" if kind == "quarter" else f"fiscal year ended {long_date(end)}"
    lines = text.splitlines()
    rows = table_rows(lines)
    found = {}
    for m in METRICS:
        v = value_for(gaap, m, start, end, t["filing_date"])
        if v is None:
            continue
        hit = find_row(lines, rows, m, v[0])
        if hit:
            found[m] = (v, hit)
    if not found:
        return [], "no verified figure"
    items = []
    company = t["name"]

    def emit(section, template, metric, question, gold, tol, need, extra):
        ex = excerpt(lines, need, count)
        if ex is None:
            return
        body, n = ex
        uid = hashlib.sha256(f"{t['accession']}|{template}".encode()).hexdigest()[:16]
        items.append({
            "id": uid, "side": side, "cik": t["cik"], "company": company, "accession": t["accession"],
            "acceptance": t["acceptance"], "post_cutoff": t["post_cutoff"], "section": section,
            "template": template, "metric": metric, "period": {"start": start, "end": end, "kind": kind},
            "question": question, "excerpt": body, "excerpt_tokens": n, "gold": gold, "tolerance": tol,
            **extra,
        })

    phr = "p2" if (side == "test" and rng.random() < 0.5) else "p1"
    for m, (v, hit) in found.items():
        if m in HELD_OUT_METRICS and side != "test":
            continue
        val, concept, accn = v
        i, shown, col, scale, dec = hit
        if METRICS[m]["unit"] == "USD/shares":
            gold, tol, ask = shown, {"abs": round(0.5 * 10 ** (-dec) * 1.01, 6)}, None
        else:
            ask = rng.choice(["millions", "thousands"]) if scale == 1e3 else "millions"
            if scale == 1e9:
                ask = rng.choice(["millions", "billions"])
            gold = shown * scale / SCALES[ask]
            # half a unit of the figure as displayed, in the asked unit
            tol = {"abs": 0.5 * 10 ** (-dec) * scale / SCALES[ask] * 1.01}
        q = PHRASING[phr].format(company=company, what=METRICS[m]["name"], period=period) + " " + unit_text(m, ask or "")
        emit("B1", f"B1:{m}:{phr}", m, q, gold, tol, [i],
             {"xbrl": {"concept": concept, "accession": accn, "value": val}, "table_scale": scale,
              "asked_scale": ask, "scale_conversion": bool(ask) and SCALES.get(ask) != scale, "column": col})

    # B2: margins
    rev = found.get("revenue")
    for name, num in (("gross_margin", "gross_profit"), ("operating_margin", "operating_income"), ("net_margin", "net_income")):
        if rev is None or num not in found:
            continue
        if (name in HELD_OUT_B2 or num in HELD_OUT_METRICS) and side != "test":
            continue
        r_shown = rev[1][1] * rev[1][3]
        if r_shown == 0:
            continue
        gold = round(100 * found[num][1][1] * found[num][1][3] / r_shown, 4)
        what = name.replace("_", " ") + " (as a percentage of total revenue, one decimal place)"
        q = PHRASING[phr].format(company=company, what=what, period=period) + " Give the answer as a percentage."
        emit("B2", f"B2:{name}:{phr}", name, q, gold, {"abs": 0.15}, [rev[1][0], found[num][1][0]], {})

    # B2: year-on-year revenue growth and EPS change, against the prior-year period in the same row
    for m, name in (("revenue", "revenue_growth"), ("eps_diluted", "eps_change")):
        if m not in found:
            continue
        prior = value_for(gaap, m, shift_year(start), shift_year(end), t["filing_date"], first_filed_any=True)
        if prior is None or prior[0] == 0:
            continue
        i = found[m][1][0]
        row = next(r for r in rows if r[0] == i)
        per_share = METRICS[m]["unit"] == "USD/shares"
        scale = found[m][1][3]
        hits = [v for v, d, g in row[2] if matches(v, d, g, scale, prior[0], per_share)]
        if not hits or hits[0] == 0:
            continue
        cur, prv = found[m][1][1], hits[0]
        if name == "revenue_growth":
            gold = round(100 * (cur / prv - 1), 4)
            what = "year-over-year growth in total revenue against the same period a year earlier (percent, one decimal place)"
            tol, unit = {"abs": 0.15}, " Give the answer as a percentage."
        else:
            gold = round(cur - prv, 4)
            what = "change in diluted earnings per share against the same period a year earlier"
            tol, unit = {"abs": 0.005}, " Give the answer in US dollars per share; use a minus sign for a decrease."
        q = PHRASING[phr].format(company=company, what=what, period=period) + unit
        emit("B2", f"B2:{name}:{phr}", name, q, gold, tol, [i], {"prior": prior[0]})
    return items, "ok" if items else "excerpt too long"


# ---------------------------------------------------------------------------------------------

def side_of(t: dict, group_of: dict) -> str | None:
    s = split_v1.assign(t["cik"], group_of)
    if s == "test":
        return "test" if t["post_cutoff"] else None
    if s == "train":
        return None if t["post_cutoff"] else "train"
    return "dev"


def build(a: argparse.Namespace) -> None:
    if not DRIVE.exists():
        sys.exit("external drive not mounted")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(glob.glob(f"{TOKENIZER}/snapshots/*/tokenizer.json")[0])
    count = lambda s: len(tok.encode(s).ids)  # noqa: E731
    targets = json.loads((PAIRS / "targets.json").read_text(encoding="utf-8"))
    group_of = split_v1.groups((t["accession"], t["cik"]) for t in targets)
    flags = {json.loads(l)["accession"]: json.loads(l) for l in open(PAIRS / "flags_v2.jsonl", encoding="utf-8")}
    sides = set(a.sides.split(","))
    facts = Facts()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261115)
    seen, out, why = set(), collections.defaultdict(list), collections.Counter()
    cache_cik, gaap = None, {}
    for t in sorted(targets, key=lambda t: (t["cik"], t["acceptance"])):
        if t["accession"] not in flags or t["accession"] in seen:
            continue  # co-registrant duplicates were dropped by EXP-0003
        seen.add(t["accession"])
        s = side_of(t, group_of)
        if s is None or s not in sides:
            continue
        path = TEXTS / f"{t['cik']}_{t['accession']}.txt"
        if not path.exists():
            why[(s, "no text")] += 1
            continue
        if t["cik"] != cache_cik:
            cache_cik, gaap = t["cik"], facts.load(t["cik"])
        if not gaap:
            why[(s, "no company facts")] += 1
            continue
        items, reason = make_items(t, path.read_text(encoding="utf-8"), gaap, count, rng, s)
        why[(s, reason)] += 1
        out[s].extend(items)
    report = {"sides": sorted(sides), "releases": {f"{k[0]}: {k[1]}": v for k, v in sorted(why.items())}}
    for s, items in out.items():
        with open(OUT / f"items_{s}.jsonl", "w", encoding="utf-8") as fh:
            for it in items:
                fh.write(json.dumps(it) + "\n")
        report[f"{s}: items"] = len(items)
        report[f"{s}: companies"] = len({i["cik"] for i in items})
        report[f"{s}: by template"] = dict(sorted(collections.Counter(i["template"] for i in items).items()))
        report[f"{s}: scale conversion (B1)"] = sum(1 for i in items if i.get("scale_conversion"))
        toks = sorted(i["excerpt_tokens"] for i in items)
        report[f"{s}: excerpt tokens median / max"] = [toks[len(toks) // 2], toks[-1]] if toks else None
    (OUT / f"yield_{'_'.join(sorted(sides))}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


def show(a: argparse.Namespace) -> None:
    if a.side == "test":
        sys.exit("refused: test items are not read (changelog 2026-11-14)")
    items = [json.loads(l) for l in open(OUT / f"items_{a.side}.jsonl", encoding="utf-8")]
    rng = random.Random(a.seed)
    for it in rng.sample(items, min(a.n, len(items))):
        print("=" * 100)
        print(it["id"], it["template"], it["company"], it["accession"], it["period"], "gold:", it["gold"], it["tolerance"])
        print("Q:", it["question"])
        print(it["excerpt"])


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build")
    b.add_argument("--sides", default="train,dev")
    b.set_defaults(fn=build)
    s = sub.add_parser("show")
    s.add_argument("--side", default="dev")
    s.add_argument("--n", type=int, default=10)
    s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=show)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
