"""EXP-0003: full count of post-cutoff guidance pairs (work package 2 of Phase 0).

EXP-0002 estimated the pool of guidance pairs from 50 companies. This script counts it: it fetches
the press release of every earnings 8-K (Item 2.02) filed after the models' knowledge cutoff, plus
each of those companies' last release before the cutoff, flags guidance with revised keyword rules
("rules v2"), and counts pairs of consecutive releases.

Rules v2 fix the three weaknesses found by the hand check in EXP-0002:

1. numbers inside an "Outlook" or "Guidance" section count even without a guidance word;
2. statements about periods that have already ended are dropped;
3. expectations that are not results (deal closings, trials, savings goals, award targets) are
   dropped by requiring a results metric.

    conda run --no-capture-output -n nlab python research/experiments/exp0003_guidance_pairs.py dev
    conda run --no-capture-output -n nlab python research/experiments/exp0003_guidance_pairs.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0003_guidance_pairs.py flag
    conda run --no-capture-output -n nlab python research/experiments/exp0003_guidance_pairs.py count
    conda run --no-capture-output -n nlab python research/experiments/exp0003_guidance_pairs.py correct

Rules it keeps: identity from ``EDGAR_IDENTITY``; at most 5 requests a second; everything fetched
or computed goes to the external drive; flags come from rules, not a model, and only pre-cutoff
releases are read by hand.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import random
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path

os.environ.setdefault("EDGAR_RATE_LIMIT_PER_SEC", "5")
sys.path.insert(0, str(Path(__file__).parent))
import exp0002_edgar_census as e2  # noqa: E402  (frozen; reused for the archive readers)

OUT = e2.ROOT / "pairs"
TEXTS = e2.ROOT / "releases"
CENSUS_TEXTS = e2.OUT / "guidance_texts"
CUTOFF, DATA_END = e2.CUTOFF, e2.DATA_END

# ---------------------------------------------------------------- rules v2

SAFE_HARBOR = e2.SAFE_HARBOR
METRIC = re.compile(
    r"\b(revenues?|net sales|sales|earnings per (diluted )?share|eps|diluted earnings|net income|"
    r"net earnings|operating (income|margin|profit|expenses?)|gross (margin|profit)|(adjusted )?ebitda|"
    r"ebit|capital expenditures?|capex|free cash flow|cash flow from operations|operating cash flow|"
    r"ffo|affo|funds from operations|net interest (income|margin)|same[- ]store|organic growth|"
    r"comparable sales|bookings|backlog|segment profit|earnings)\b",
    re.I,
)
GUIDE = re.compile(
    r"\b(outlook|guidance|expects?|expected|expecting|anticipates?|anticipated|projected|projects that|"
    r"forecasts?|forecasted|now sees?|sees)\b",
    re.I,
)
FUTURE = re.compile(
    r"\b(fiscal (year )?20\d\d|full[- ]year|fy ?20\d\d|fy\d\d|20\d\d|next quarter|"
    r"(first|second|third|fourth) quarter|q[1-4]|coming year|remainder of the year|second half|"
    r"first half|year[- ]end)\b",
    re.I,
)
NUM = re.compile(
    r"(\$\s?\d|\b\d+(\.\d+)?\s?%|\b\d+(\.\d+)?\s?(percent|basis points|bps)\b|\b\d+\.\d{2}\b)", re.I
)
PAST = re.compile(
    r"\b(was|were|totaled|came in|reported|achieved|delivered|exceeded|exceeding|performing at|met|"
    r"meeting|compared with|compared to)\b",
    re.I,
)
FORWARD = re.compile(
    r"\b(expects?|expected to|anticipat\w*|now|rais\w*|reaffirm\w*|reiterat\w*|maintain\w*|provid\w*|"
    r"issu\w*|updat\w*|initiat\w*|narrow\w*|tighten\w*|lower\w*|reduc\w*|introduc\w*|establish\w*|"
    r"projected|forecast\w*|sees|guid(e|es|ing) to|withdr\w*|suspend\w*)\b",
    re.I,
)
ANNOUNCE = re.compile(
    r"\b(reaffirm\w*|reiterat\w*|maintain\w*|rais\w*|lower\w*|provid\w*|issu\w*|updat\w*|withdr\w*|"
    r"suspend\w*|introduc\w*|announc\w*|initiat\w*|narrow\w*|tighten\w*)\b",
    re.I,
)
COMP = re.compile(r"\b(restricted|performance[- ]based|performance shares|award|vesting|compensation)\b", re.I)
OUTLOOK_HEAD = re.compile(r"\b(outlook|guidance|forecast)\b", re.I)
YEAR = re.compile(r"\b(20\d\d)\b")
FY2 = re.compile(r"\bfy ?(\d\d)\b", re.I)


def is_heading(para: str) -> bool:
    """EXP-0002's heading test, plus headings that end in a colon ("Financial Outlook:"), which the
    fresh hand check of 2026-11-13 found the rule missing (Backblaze, 2026-05-04)."""
    words = para.split()
    return 0 < len(words) <= 8 and not para.rstrip().endswith((".", ";", ","))


def paragraphs(text: str) -> list[str]:
    """Paragraphs outside the safe-harbor section (same rule as EXP-0002)."""
    out, skipping = [], False
    for para in re.split(r"\n\s*\n", text):
        if SAFE_HARBOR.search(para):
            skipping = skipping or is_heading(para)
            continue
        if skipping and is_heading(para):
            skipping = False
        if not skipping:
            out.append(para)
    return out


def finished(s: str, filing_year: int) -> bool:
    years = [int(y) for y in YEAR.findall(s)] + [2000 + int(y) for y in FY2.findall(s)]
    return bool(years) and max(years) < filing_year


def backward_looking(s: str) -> bool:
    return bool(PAST.search(s)) and not FORWARD.search(s)


def flag(text: str, filing_date: str) -> dict:
    fy = int(filing_date[:4])
    paras = paragraphs(text)
    numeric, qualitative = [], []
    # 1. outlook sections: a heading about outlook or guidance, up to the next unrelated heading
    in_section, section_paras = False, 0
    for para in paras:
        if is_heading(para):
            in_section = bool(OUTLOOK_HEAD.search(para))
            section_paras = 0
            continue
        if in_section:
            section_paras += 1
            if section_paras > 15:
                in_section = False
                continue
            for line in para.split("\n"):
                if METRIC.search(line) and NUM.search(line) and not COMP.search(line):
                    if not finished(line, fy) and not backward_looking(line):
                        numeric.append(line.strip())
    # 2. sentences anywhere outside the safe harbor
    for para in paras:
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(•])|\n(?=\s*[•▪\-])", para):
            s = " ".join(s.split())
            if not s or len(s) > 700 or COMP.search(s) or finished(s, fy) or backward_looking(s):
                continue
            if not (GUIDE.search(s) and FUTURE.search(s)):
                continue
            if METRIC.search(s) and NUM.search(s):
                numeric.append(s)
            elif METRIC.search(s) and FORWARD.search(s):
                qualitative.append(s)
            elif re.search(r"\b(outlook|guidance)\b", s, re.I) and ANNOUNCE.search(s):
                qualitative.append(s)
    kind = "numeric" if numeric else "qualitative_only" if qualitative else "none"
    revisions = {k: bool(p.search(" ".join(numeric + qualitative))) for k, p in e2.REVISION.items()}
    return {
        "kind": kind,
        "n_numeric": len(numeric),
        "n_qualitative": len(qualitative),
        "revision_words": [k for k, v in revisions.items() if v],
        "evidence": (numeric or qualitative or [""])[0][:300],
    }


# ---------------------------------------------------------------- dev check on EXP-0002's hand labels

# Hand labels from the EXP-0002 check (pre-cutoff releases only), keyed by the order in which the
# draws were made. "numeric" = in-scope numeric guidance, "qualitative_only" = in-scope guidance in
# words only, "none" = no in-scope guidance (an out-of-scope numeric outlook counts as none).
HAND_NUMERIC_DRAW = [
    "numeric", "numeric", "numeric", "qualitative_only", "numeric", "numeric", "numeric", "numeric",
    "none", "none", "none", "numeric", "numeric", "numeric", "none", "none", "numeric", "numeric",
    "numeric", "numeric", "numeric", "numeric", "numeric", "none", "none",
]
HAND_NONE_DRAW = ["none"] * 12
# The second qualitative draw (Orthofix, 2025-08-05) was first labelled qualitative_only; rules v2
# found "Pro forma net sales expected to range between $808 million to $816 million" in it, and the
# text confirms numeric guidance. Corrected on 2026-11-13.
HAND_QUAL_DRAW = [
    "none", "numeric", "none", "qualitative_only", "none", "none", "qualitative_only",
    "numeric", "none", "none", "none", "none",
]


def dev(_: argparse.Namespace) -> None:
    rs = [json.loads(l) for l in open(e2.OUT / "guidance_flags.jsonl", encoding="utf-8")]
    pre = [r for r in rs if not r["post_cutoff"]]
    rng = random.Random(20261113)
    draws = list(zip(rng.sample([r for r in pre if r["kind"] == "numeric"], 25), HAND_NUMERIC_DRAW))
    rng = random.Random(20261114)
    draws += list(zip(rng.sample([r for r in pre if r["kind"] == "none"], 12), HAND_NONE_DRAW))
    draws += list(zip(rng.sample([r for r in pre if r["kind"] == "qualitative_only"], 12), HAND_QUAL_DRAW))
    conf = collections.Counter()
    for r, truth in draws:
        text = (CENSUS_TEXTS / f"{r['cik']}_{r['accession']}.txt").read_text(encoding="utf-8")
        got = flag(text, r["filing_date"])
        conf[(truth, got["kind"])] += 1
        if truth != got["kind"]:
            print(f"  miss {r['ticker']} {r['filing_date']}: truth {truth}, v1 {r['kind']}, v2 {got['kind']} | {got['evidence'][:160]}")
    kinds = ("numeric", "qualitative_only", "none")
    print("\nrows = hand label, columns = rules v2")
    print("".ljust(18) + "".join(k.ljust(18) for k in kinds))
    for t in kinds:
        print(t.ljust(18) + "".join(str(conf[(t, k)]).ljust(18) for k in kinds))
    right = sum(v for (t, k), v in conf.items() if t == k)
    print(f"\nagreement {right}/{sum(conf.values())} (v1 on the same draws: {sum(1 for r, t in draws if r['kind'] == t)}/{len(draws)})")


# ---------------------------------------------------------------- fetch


class IndexTable(HTMLParser):
    """Rows of the document table on a filing's -index.html page."""

    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._href, self._in_td = [], None, "", None, False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag == "td" and self._row is not None:
            self._in_td, self._cell, self._href = True, "", None
        elif tag == "a" and self._in_td:
            self._href = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag == "td" and self._row is not None:
            self._row.append((self._cell.strip(), self._href))
            self._in_td = False
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._in_td:
            self._cell += data


def press_release_url(cik: int, acc: str, get) -> str | None:
    """Same choice as edgartools' EightK.press_releases: an .htm document whose description
    matches 'RELEASE' or whose type is EX-99.1, EX-99 or EX-99.01; the first one wins."""
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/"
    page = get(base + f"{acc}-index.html", as_text=True)
    if not page:
        return None
    t = IndexTable()
    t.feed(page)
    for row in t.rows:
        if len(row) < 4:
            continue
        desc, (doc, href), typ = row[1][0], row[2], row[3][0]
        if not doc.lower().endswith(".htm"):
            continue
        if re.match(".*RELEASE", desc) or typ in ("EX-99.1", "EX-99", "EX-99.01"):
            return "https://www.sec.gov" + href if href and href.startswith("/") else base + doc
    return None


def targets() -> list[dict]:
    out = []
    for co in e2.companies():
        rel = []
        for r in e2.rows(co["recent"]):
            if r["form"] == "8-K" and e2.EARNINGS_ITEM in (r["items"] or ""):
                try:
                    d = dt.date.fromisoformat(r["filingDate"])
                except ValueError:
                    continue
                if d <= DATA_END:
                    rel.append((d, r))
        post = [(d, r) for d, r in rel if d > CUTOFF]
        if not post:
            continue
        pre = sorted([(d, r) for d, r in rel if d <= CUTOFF], key=lambda x: x[1]["acceptanceDateTime"])
        chosen = post + pre[-1:]
        for d, r in chosen:
            out.append(
                {
                    "cik": co["cik"], "name": co["name"], "sic": co["sic"],
                    "size_band": e2.size_band(co["category"]),
                    "listed_today": bool(set(co["exchanges"]) & e2.LISTED),
                    "accession": r["accessionNumber"], "filing_date": r["filingDate"],
                    "acceptance": r["acceptanceDateTime"], "post_cutoff": d > CUTOFF,
                }
            )
    return out


def fetch(_: argparse.Namespace) -> None:
    e2.need_drive()
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    from edgar.documents import parse_html
    from edgar.httprequests import download_file

    OUT.mkdir(parents=True, exist_ok=True)
    TEXTS.mkdir(parents=True, exist_ok=True)
    tpath = OUT / "targets.json"
    if tpath.exists():
        tg = json.loads(tpath.read_text(encoding="utf-8"))
    else:
        tg = targets()
        tpath.write_text(json.dumps(tg), encoding="utf-8")
    print(f"[fetch] {len(tg)} releases: {sum(t['post_cutoff'] for t in tg)} after the cutoff", flush=True)
    log = OUT / "fetch_log.jsonl"
    done = set()
    if log.exists():
        # Errors (mostly SEC 503s) are retried on the next run; flag_all keeps the last status.
        done = {
            r["accession"]
            for r in (json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l)
            if not r["status"].startswith("error")
        }
    t0, n = time.time(), 0
    with open(log, "a", encoding="utf-8") as fh:
        for t in tg:
            acc = t["accession"]
            if acc in done:
                continue
            path = TEXTS / f"{t['cik']}_{acc}.txt"
            old = CENSUS_TEXTS / f"{t['cik']}_{acc}.txt"
            status = "ok"
            try:
                if old.exists():
                    path.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
                    status = "reused"
                else:
                    url = press_release_url(t["cik"], acc, download_file)
                    if url is None:
                        status = "no_press_release"
                        path.write_text("", encoding="utf-8")
                    else:
                        html = download_file(url, as_text=True)
                        path.write_text(parse_html(html).text() or "", encoding="utf-8")
            except Exception as err:
                status = f"error: {type(err).__name__}: {str(err)[:120]}"
            fh.write(json.dumps({"accession": acc, "status": status}) + "\n")
            fh.flush()
            n += 1
            if n % 250 == 0:
                print(f"[fetch] {n} done, {n / (time.time() - t0):.2f}/s", flush=True)
    print(f"[fetch] finished: {n} this run", flush=True)


def flag_all(_: argparse.Namespace) -> None:
    e2.need_drive()
    tg = json.loads((OUT / "targets.json").read_text(encoding="utf-8"))
    # Co-registrants (a utility and its holding company, an airline and its parent) file one 8-K
    # under several CIKs. Keep the first company listed for an accession; drop any company that
    # shares an accession with an earlier one (79 companies, 76 of them entirely duplicates).
    first: dict[str, str] = {}
    for t in tg:
        first.setdefault(t["accession"], t["cik"])
    dup = {t["cik"] for t in tg if first[t["accession"]] != t["cik"]}
    print(f"dropping {len(dup)} co-registrant companies ({sum(t['cik'] in dup for t in tg)} rows)")
    tg = [t for t in tg if t["cik"] not in dup]
    status = {}
    for l in (OUT / "fetch_log.jsonl").read_text(encoding="utf-8").splitlines():
        if l:
            r = json.loads(l)
            status[r["accession"]] = r["status"]
    with open(OUT / "flags_v2.jsonl", "w", encoding="utf-8") as fh:
        for t in tg:
            st = status.get(t["accession"], "not_fetched")
            row = dict(t, fetch=st)
            if st in ("ok", "reused"):
                # Co-registrant 8-Ks were saved under whichever CIK reached them first.
                path = TEXTS / f"{t['cik']}_{t['accession']}.txt"
                if not path.exists():
                    path = max(TEXTS.glob(f"*_{t['accession']}.txt"), key=lambda q: q.stat().st_size)
                text = path.read_text(encoding="utf-8")
                row.update(flag(text, t["filing_date"]) if text.strip() else {"kind": "no_press_release"})
            else:
                row["kind"] = "no_press_release" if st == "no_press_release" else "unavailable"
            fh.write(json.dumps(row) + "\n")
    print("flags written:", OUT / "flags_v2.jsonl")


def count(_: argparse.Namespace) -> None:
    rows = [json.loads(l) for l in open(OUT / "flags_v2.jsonl", encoding="utf-8")]
    post = [r for r in rows if r["post_cutoff"]]
    print("releases after the cutoff:", len(post), dict(collections.Counter(r["kind"] for r in post)))
    pre = [r for r in rows if not r["post_cutoff"]]
    print("last release before the cutoff:", len(pre), dict(collections.Counter(r["kind"] for r in pre)))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["cik"]].append(r)
    g = ("numeric", "qualitative_only")
    c = collections.Counter()
    for cik, rs in by.items():
        rs.sort(key=lambda r: r["acceptance"])
        for p0, p1 in zip(rs, rs[1:]):
            if not p1["post_cutoff"]:
                continue
            both = p0["post_cutoff"]
            missing = ("unavailable", "no_press_release")
            if p0["kind"] in missing or p1["kind"] in missing:
                c[f"no text for one side ({'both_after' if both else 'p1_after only'})"] += 1
                continue
            for scope in (("p1_after", True), ("both_after", both)):
                name, ok = scope
                if not ok:
                    continue
                c[f"{name}: pairs"] += 1
                if p0["kind"] in g or p1["kind"] in g:
                    c[f"{name}: guidance in either"] += 1
                if p0["kind"] == "numeric" and p1["kind"] == "numeric":
                    c[f"{name}: numeric in both"] += 1
                if p0["kind"] in g and p1["kind"] in g:
                    c[f"{name}: guidance in both"] += 1
                if (p0["kind"] in g) != (p1["kind"] in g):
                    c[f"{name}: guidance in one only (initiated or dropped)"] += 1
    for k in sorted(c):
        print(f"  {k}: {c[k]}")
    print("\ncompanies with a post-cutoff release:", len(by))
    print("by size band, post-cutoff releases with numeric guidance:")
    for band in sorted({r["size_band"] for r in post}):
        sub = [r for r in post if r["size_band"] == band]
        k = collections.Counter(r["kind"] for r in sub)
        print(f"  {band}: {len(sub)} releases, numeric {k['numeric']}, qualitative {k['qualitative_only']}, none {k['none']}")
    (OUT / "pair_counts.json").write_text(json.dumps(dict(c), indent=1), encoding="utf-8")


# Fresh hand check of 2026-11-13: 30 pre-cutoff releases, none of them in the dev draws, read by
# hand and compared with rules v2 (before the colon-heading fix, so slightly pessimistic).
# FRESH_CHECK[rule flag][hand label] = count. Per-item labels were not kept; only this table.
KINDS = ("numeric", "qualitative_only", "none")
FRESH_CHECK = {
    "numeric": {"numeric": 10, "qualitative_only": 1, "none": 2},
    "qualitative_only": {"numeric": 0, "qualitative_only": 4, "none": 5},
    "none": {"numeric": 0, "qualitative_only": 1, "none": 7},
}


def correct(_: argparse.Namespace) -> None:
    """Turn rule flags into expected true counts using the fresh hand check.

    Each release gets P(true kind | rule flag) from its column of FRESH_CHECK. Pair counts assume
    the two releases of a pair are misread independently, which is optimistic: a company's
    releases share a template, so errors probably repeat. Intervals come from drawing each column
    from a Dirichlet(counts + 0.5) 4,000 times; they reflect the 30-item check, not the counts."""
    rows = [json.loads(l) for l in open(OUT / "flags_v2.jsonl", encoding="utf-8")]
    by = collections.defaultdict(list)
    for r in rows:
        by[r["cik"]].append(r)
    pairs = []
    for rs in by.values():
        rs.sort(key=lambda r: r["acceptance"])
        for p0, p1 in zip(rs, rs[1:]):
            if p1["post_cutoff"] and p0["kind"] in KINDS and p1["kind"] in KINDS:
                pairs.append((p0["kind"], p1["kind"], p0["post_cutoff"]))
    post = [r["kind"] for r in rows if r["post_cutoff"] and r["kind"] in KINDS]

    def estimate(m: dict) -> dict:
        def p(k):
            return m[k]
        out = {f"releases: {t}": sum(p(k)[t] for k in post) for t in KINDS}
        for scope in ("p1_after", "both_after"):
            ps = [(a, b) for a, b, both in pairs if scope == "p1_after" or both]
            g = lambda k: p(k)["numeric"] + p(k)["qualitative_only"]  # noqa: E731
            out[f"{scope}: pairs"] = len(ps)
            out[f"{scope}: numeric in both"] = sum(p(a)["numeric"] * p(b)["numeric"] for a, b in ps)
            out[f"{scope}: guidance in both"] = sum(g(a) * g(b) for a, b in ps)
            out[f"{scope}: guidance in either"] = sum(1 - (1 - g(a)) * (1 - g(b)) for a, b in ps)
            out[f"{scope}: guidance in one only"] = sum(g(a) * (1 - g(b)) + (1 - g(a)) * g(b) for a, b in ps)
        return out

    point = {k: {t: v / sum(col.values()) for t, v in col.items()} for k, col in FRESH_CHECK.items()}
    est = estimate(point)
    rng = random.Random(20261113)
    draws = collections.defaultdict(list)
    for _ in range(4000):
        m = {}
        for k, col in FRESH_CHECK.items():
            g = {t: rng.gammavariate(v + 0.5, 1) for t, v in col.items()}
            s = sum(g.values())
            m[k] = {t: v / s for t, v in g.items()}
        for name, v in estimate(m).items():
            draws[name].append(v)
    raw = collections.Counter(post)
    print("post-cutoff releases with text, rule flags:", dict(raw))
    result = {}
    for name, v in est.items():
        d = sorted(draws[name])
        lo, hi = d[int(0.05 * len(d))], d[int(0.95 * len(d)) - 1]
        result[name] = {"estimate": round(v), "p05": round(lo), "p95": round(hi)}
        print(f"  {name}: {v:,.0f}  (90% interval {lo:,.0f} to {hi:,.0f})")
    (OUT / "pair_counts_corrected.json").write_text(json.dumps(result, indent=1), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("dev", "fetch", "flag", "count", "correct"):
        sub.add_parser(name)
    a = p.parse_args()
    {"dev": dev, "fetch": fetch, "flag": flag_all, "count": count, "correct": correct}[a.cmd](a)


if __name__ == "__main__":
    main()
