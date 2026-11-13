"""EXP-0002: SEC EDGAR censuses for the data audit (work package 2 of Phase 0).

An engineering measurement with no hypothesis. It answers two questions the research design needs
before Benchmark v0 can be specified:

  hard-events  How many 8-K filings carry the four hard-event items (1.03, 2.06, 3.01, 4.02), and
               out of how many companies, after the models' knowledge cutoff and in the year
               before it. Also counts earnings releases (Item 2.02), the benchmark's raw material.
               Reads SEC's bulk submissions archive offline; no per-filing requests.
  guidance     For a stratified random sample of 50 listed companies, fetch the press release
               (EX-99.1) of each of their last 8 earnings 8-Ks and flag, by rule, whether it gives
               numeric guidance, only qualitative guidance, or none, plus revision words.

Run it through the conda env that has edgartools (see AGENTS.md):

    conda run --no-capture-output -n nlab python research/experiments/exp0002_edgar_census.py hard-events
    conda run --no-capture-output -n nlab python research/experiments/exp0002_edgar_census.py guidance
    conda run --no-capture-output -n nlab python research/experiments/exp0002_edgar_census.py report

Rules it keeps:

* the SEC contact string comes from ``EDGAR_IDENTITY`` in the environment, never from this file;
* requests are limited to 5 a second, below SEC's 10;
* everything fetched or computed is written to the external drive, never into the repo;
* the guidance flags come from keyword rules, not from a model, so no model on the evaluation
  roster reads the post-cutoff releases that may later become test items.

The rules are crude by design. Their error rate is part of what the census reports: the owner
checks a random sample of flagged releases by hand before any number here is relied on.
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
import zipfile
from pathlib import Path

os.environ.setdefault("EDGAR_RATE_LIMIT_PER_SEC", "5")

DRIVE = Path("/Volumes/Seagate Backup Plus Drive")
ROOT = DRIVE / "DATA" / "narrative_lab" / "edgar"
BULK = ROOT / "bulk" / "submissions-2026-11-12.zip"
OUT = ROOT / "census"
CUTOFF = dt.date(2026, 6, 30)  # latest knowledge cutoff on the evaluation roster (roadmap v2)
DATA_END = dt.date(2026, 11, 11)  # the bulk archive was built early on 2026-11-12 UTC
HARD_ITEMS = {
    "1.03": "bankruptcy or receivership",
    "2.06": "material impairment",
    "3.01": "delisting notice or transfer",
    "4.02": "non-reliance on prior financials",
}
EARNINGS_ITEM = "2.02"
SEED = 20261113
N_COMPANIES = 50
N_RELEASES = 8
LISTED = {"NYSE", "Nasdaq", "NYSE American", "NYSE Arca", "CBOE"}


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- bulk submissions


def companies():
    """Yield one dict per company from the bulk archive: identity plus its recent filings."""
    with zipfile.ZipFile(BULK) as zf:
        for name in zf.namelist():
            if not name.endswith(".json") or "-submissions-" in name:
                continue  # overflow files hold filings older than the ~1,000 most recent
            try:
                d = json.loads(zf.read(name))
            except Exception:
                continue
            recent = (d.get("filings") or {}).get("recent") or {}
            if not recent.get("form"):
                continue
            yield {
                "cik": d.get("cik"),
                "name": d.get("name"),
                "sic": d.get("sic") or "",
                "category": d.get("category") or "",
                "exchanges": [e for e in (d.get("exchanges") or []) if e],
                "tickers": [t for t in (d.get("tickers") or []) if t],
                "recent": recent,
            }


def rows(recent: dict):
    keys = ("form", "filingDate", "acceptanceDateTime", "items", "accessionNumber", "primaryDocument")
    for vals in zip(*(recent.get(k, []) for k in keys)):
        yield dict(zip(keys, vals))


def size_band(category: str) -> str:
    c = category.lower()
    if "large accelerated" in c:
        return "large accelerated"
    if "non-accelerated" in c or "smaller reporting" in c:
        return "non-accelerated or smaller"
    if "accelerated" in c:
        return "accelerated"
    return "unknown"


def hard_events(_: argparse.Namespace) -> None:
    need_drive()
    windows = {
        "post_cutoff": (CUTOFF + dt.timedelta(days=1), DATA_END),
        "year_before": (CUTOFF - dt.timedelta(days=364), CUTOFF),
    }
    days = {w: (b - a).days + 1 for w, (a, b) in windows.items()}
    counts = {w: collections.Counter() for w in windows}
    filers = {w: collections.defaultdict(set) for w in windows}
    by_band = {w: collections.defaultdict(collections.Counter) for w in windows}
    events: list[dict] = []
    n = 0
    for co in companies():
        n += 1
        listed = bool(set(co["exchanges"]) & LISTED)  # listing status today, not at the time
        band = size_band(co["category"])
        # Point-in-time universe: the company published an earnings release (an Item 2.02 8-K) in
        # the 365 days before the window opened. Unlike today's listing status, this does not drop
        # companies that have since failed and been delisted.
        release_days = []
        for r in rows(co["recent"]):
            if r["form"] == "8-K" and EARNINGS_ITEM in (r["items"] or ""):
                try:
                    release_days.append(dt.date.fromisoformat(r["filingDate"]))
                except ValueError:
                    pass
        in_universe = {
            w: any(a - dt.timedelta(days=365) <= d < a for d in release_days)
            for w, (a, _) in windows.items()
        }
        for w in windows:
            if in_universe[w]:
                filers[w]["universe"].add(co["cik"])
        for r in rows(co["recent"]):
            form = r["form"]
            try:
                day = dt.date.fromisoformat(r["filingDate"])
            except ValueError:
                continue
            for w, (a, b) in windows.items():
                if not a <= day <= b:
                    continue
                if form in ("10-K", "10-Q", "20-F", "40-F"):
                    filers[w]["periodic"].add(co["cik"])
                    if listed:
                        filers[w]["periodic_listed"].add(co["cik"])
                if form not in ("8-K", "8-K/A"):
                    continue
                items = {i.strip() for i in (r["items"] or "").split(",") if i.strip()}
                if EARNINGS_ITEM in items and form == "8-K":
                    counts[w]["2.02 filings"] += 1
                    filers[w]["2.02"].add(co["cik"])
                    if listed:
                        counts[w]["2.02 filings, listed"] += 1
                        filers[w]["2.02_listed"].add(co["cik"])
                for item in HARD_ITEMS:
                    if item in items:
                        counts[w][f"{item} filings{' (8-K/A)' if form == '8-K/A' else ''}"] += 1
                        if form == "8-K":
                            filers[w][item].add(co["cik"])
                            if in_universe[w]:
                                filers[w][f"{item}_universe"].add(co["cik"])
                            if listed:
                                filers[w][f"{item}_listed"].add(co["cik"])
                                by_band[w][item][band] += 1
                            if w == "post_cutoff":
                                events.append(
                                    {
                                        "item": item,
                                        "cik": co["cik"],
                                        "name": co["name"],
                                        "listed": listed,
                                        "size_band": band,
                                        "sic": co["sic"],
                                        "filing_date": r["filingDate"],
                                        "acceptance": r["acceptanceDateTime"],
                                        "accession": r["accessionNumber"],
                                    }
                                )
    rates = {}
    for w in windows:
        u = len(filers[w]["universe"]) or 1
        rates[w] = {
            item: round(100 * len(filers[w][f"{item}_universe"]) / u * 365 / days[w], 2)
            for item in HARD_ITEMS
        }
    summary = {
        "source": BULK.name,
        "universe_note": "companies with an Item 2.02 8-K in the 365 days before the window opened",
        "annualised_pct_of_universe": rates,
        "companies_in_archive": n,
        "windows": {w: [str(a), str(b), days[w]] for w, (a, b) in windows.items()},
        "counts": {w: dict(c) for w, c in counts.items()},
        "companies": {w: {k: len(v) for k, v in f.items()} for w, f in filers.items()},
        "listed_events_by_size_band": {
            w: {item: dict(c) for item, c in d.items()} for w, d in by_band.items()
        },
    }
    (OUT / "hard_events_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with open(OUT / "hard_events_post_cutoff.jsonl", "w", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps(e) + "\n")
    print(json.dumps(summary, indent=2))


# ---------------------------------------------------------------- guidance census

SAFE_HARBOR = re.compile(
    r"forward[- ]looking statements|private securities litigation reform act|safe harbor", re.I
)
GUIDE_WORD = re.compile(
    r"\b(outlook|guidance|expects?|expected|anticipates?|projects?|forecasts?|targets?|now sees?)\b", re.I
)
FUTURE = re.compile(
    r"\b(fiscal (year )?20\d\d|full[- ]year|fy ?20\d\d|fy\d\d|20\d\d|next quarter|(first|second|third|fourth) quarter|q[1-4]|coming year|remainder of the year)\b",
    re.I,
)
NUMBER = re.compile(
    r"(\$\s?\d[\d,]*(\.\d+)?\s*(million|billion|thousand|[mbk])?\b|\b\d+(\.\d+)?\s?%|\b\d+(\.\d+)?\s?(percent|basis points|bps)\b)",
    re.I,
)
RANGE = re.compile(
    r"(\$?\s?\d[\d,]*(\.\d+)?\s*(million|billion|%|percent)?\s*(to|-|–|—|and)\s*\$?\s?\d[\d,]*(\.\d+)?)", re.I
)
REVISION = {
    "raised": re.compile(r"\b(rais(e|es|ed|ing)|increas(e|es|ed|ing)|improv(e|es|ed|ing)|lift(s|ed)?)\b[^.]{0,40}\b(outlook|guidance|expectations?|forecast)\b", re.I),
    "lowered": re.compile(r"\b(lower(s|ed|ing)?|reduc(e|es|ed|ing)|cut(s|ting)?|revis(e|es|ed|ing) down)\b[^.]{0,40}\b(outlook|guidance|expectations?|forecast)\b", re.I),
    "reaffirmed": re.compile(r"\b(reaffirm(s|ed|ing)?|reiterat(e|es|ed|ing)|maintain(s|ed|ing)?|confirm(s|ed|ing)?)\b[^.]{0,40}\b(outlook|guidance|expectations?|forecast)\b", re.I),
    "withdrawn": re.compile(r"\b(withdr(a|e)w(s|n|ing)?|suspend(s|ed|ing)?|no longer (provid|giv)(e|es|ing))\b[^.]{0,40}\b(outlook|guidance|forecast)\b", re.I),
}
HEADING = re.compile(
    r"^\s*((fiscal|full[- ]year|20\d\d|business|financial|company|updated|quarterly|annual)\s+)*(outlook|guidance)\b.{0,40}$",
    re.I | re.M,
)


def is_heading(para: str) -> bool:
    words = para.split()
    return 0 < len(words) <= 8 and not para.rstrip().endswith((".", ":", ";", ","))


def sentences(text: str) -> list[str]:
    """Sentences outside the safe-harbor section.

    A paragraph that mentions the safe harbor is dropped, and so is everything after a safe-harbor
    heading up to the next heading that is not about the safe harbor.
    """
    paras, skipping = [], False
    for para in re.split(r"\n\s*\n", text):
        if SAFE_HARBOR.search(para):
            skipping = skipping or is_heading(para)
            continue
        if skipping and is_heading(para):
            skipping = False
        if not skipping:
            paras.append(para)
    out: list[str] = []
    for p in paras:
        out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(])", p) if s.strip())
    return out


def flag(text: str) -> dict:
    sents = sentences(text)
    guide = [s for s in sents if GUIDE_WORD.search(s) and FUTURE.search(s)]
    numeric = [s for s in guide if NUMBER.search(s) or RANGE.search(s)]
    revisions = {k: bool(p.search(" ".join(sents))) for k, p in REVISION.items()}
    if numeric:
        kind = "numeric"
    elif guide:
        kind = "qualitative_only"
    else:
        kind = "none"
    return {
        "kind": kind,
        "outlook_heading": bool(HEADING.search(text)),
        "n_guidance_sentences": len(guide),
        "n_numeric_sentences": len(numeric),
        "revision_words": [k for k, v in revisions.items() if v],
        "example": (numeric or guide or [""])[0][:300],
        "chars": len(text),
    }


def pick_sample() -> list[dict]:
    """Listed companies with at least 8 earnings 8-Ks in the archive, stratified by size band."""
    pool = collections.defaultdict(list)
    for co in companies():
        if not set(co["exchanges"]) & LISTED:
            continue
        releases = [
            r for r in rows(co["recent"])
            if r["form"] == "8-K" and EARNINGS_ITEM in (r["items"] or "")
            and dt.date.fromisoformat(r["filingDate"]) <= DATA_END
        ]
        if len(releases) < N_RELEASES:
            continue
        releases.sort(key=lambda r: r["filingDate"], reverse=True)
        band = size_band(co["category"])
        if band == "unknown":
            continue
        pool[band].append(
            {
                "cik": co["cik"],
                "name": co["name"],
                "ticker": co["tickers"][0] if co["tickers"] else "",
                "sic": co["sic"],
                "size_band": band,
                "releases": releases[:N_RELEASES],
            }
        )
    rng = random.Random(SEED)
    bands = sorted(pool)
    per = {b: N_COMPANIES // len(bands) for b in bands}
    for b in bands[: N_COMPANIES - sum(per.values())]:
        per[b] += 1
    sample = []
    for b in bands:
        cos = sorted(pool[b], key=lambda c: c["cik"])
        sample.extend(rng.sample(cos, per[b]))
    print("pool sizes:", {b: len(pool[b]) for b in bands}, "| sampled:", per, flush=True)
    return sample


def guidance(_: argparse.Namespace) -> None:
    need_drive()
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    from edgar import get_by_accession_number

    texts = OUT / "guidance_texts"
    texts.mkdir(exist_ok=True)
    sample_path = OUT / "guidance_sample.json"
    if sample_path.exists():
        sample = json.loads(sample_path.read_text(encoding="utf-8"))
    else:
        sample = pick_sample()
        sample_path.write_text(json.dumps(sample, indent=1), encoding="utf-8")
    results_path = OUT / "guidance_flags.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(l)["accession"] for l in results_path.read_text(encoding="utf-8").splitlines() if l}
    with open(results_path, "a", encoding="utf-8") as fh:
        for co in sample:
            for k, r in enumerate(co["releases"]):
                acc = r["accessionNumber"]
                if acc in done:
                    continue
                row = {
                    "cik": co["cik"], "name": co["name"], "ticker": co["ticker"], "sic": co["sic"],
                    "size_band": co["size_band"], "position": k, "accession": acc,
                    "filing_date": r["filingDate"], "acceptance": r["acceptanceDateTime"],
                    "post_cutoff": dt.date.fromisoformat(r["filingDate"]) > CUTOFF,
                }
                path = texts / f"{co['cik']}_{acc}.txt"
                try:
                    if not path.exists():
                        f = get_by_accession_number(acc)
                        prs = f.obj().press_releases if f is not None else None
                        text = prs[0].text() if prs else ""
                        row["has_ex99"] = bool(prs)
                        path.write_text(text or "", encoding="utf-8")
                    text = path.read_text(encoding="utf-8")
                    row["has_ex99"] = row.get("has_ex99", bool(text))
                    row.update(flag(text) if text else {"kind": "no_press_release"})
                except Exception as err:
                    row["kind"] = "error"
                    row["error"] = f"{type(err).__name__}: {str(err)[:160]}"
                fh.write(json.dumps(row) + "\n")
                fh.flush()
            print(f"[guidance] {co['ticker'] or co['cik']} done", flush=True)


def report(_: argparse.Namespace) -> None:
    need_drive()
    s = json.loads((OUT / "hard_events_summary.json").read_text(encoding="utf-8"))
    print("## Hard events and earnings releases\n")
    print(json.dumps(s, indent=1))
    path = OUT / "guidance_flags.jsonl"
    if not path.exists():
        return
    rs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l]
    print(f"\n## Guidance census: {len(rs)} releases, {len({r['cik'] for r in rs})} companies\n")
    for label, sub in (("all", rs), ("pre-cutoff", [r for r in rs if not r["post_cutoff"]]),
                       ("post-cutoff", [r for r in rs if r["post_cutoff"]])):
        c = collections.Counter(r["kind"] for r in sub)
        print(label, len(sub), dict(c))
    print("\nby size band:")
    for band in sorted({r["size_band"] for r in rs}):
        sub = [r for r in rs if r["size_band"] == band]
        print(" ", band, len(sub), dict(collections.Counter(r["kind"] for r in sub)))
    print("\nrevision words (releases with any guidance):")
    g = [r for r in rs if r.get("kind") in ("numeric", "qualitative_only")]
    print(" ", dict(collections.Counter(w for r in g for w in r.get("revision_words", []))), "of", len(g))
    print("\nupdating routine (releases with numeric guidance, of 8):")
    per = collections.defaultdict(int)
    for r in rs:
        per[r["cik"]] += r.get("kind") == "numeric"
    routine = collections.Counter(
        "every release" if v >= 7 else "some releases" if v >= 1 else "never" for v in per.values()
    )
    print(" ", dict(routine))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("hard-events")
    sub.add_parser("guidance")
    sub.add_parser("report")
    args = parser.parse_args()
    {"hard-events": hard_events, "guidance": guidance, "report": report}[args.cmd](args)


if __name__ == "__main__":
    main()
