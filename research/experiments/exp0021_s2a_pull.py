"""EXP-0021: the pull of old earnings releases for sub-study S2 (step S2-a).

Design: docs/plans/2026-11-20_substudy_s2_plan.md, §10 and decision 4. An engineering step with
no hypothesis and no model call. S2 needs episodes the models remember well, and the releases of
the years before the cutoff are not on the drive: EXP-0020 found 4,404 of 33,378 labelled
releases there, nearly all from 2026.

1. ``draw``: picks the releases to fetch from EXP-0020's list (``s2/exp0020/releases.jsonl``),
   by seed, without touching the network. Candidates are labelled releases filed by the cutoff,
   not on the drive, from training and development companies. For each of the 250 largest
   companies by revenue, four releases in four different years drawn at random; for the rest,
   one release from each of 500 companies drawn at random.
2. ``fetch``: downloads the press release (Exhibit 99.1) of each drawn 8-K, with the same choice
   of document and the same text extraction as EXP-0003. Needs the owner's say-so (rule 17) and
   ``EDGAR_IDENTITY``. Resumable; errors are retried on the next run.
3. ``audit``: the draw is reproducible, every release is pre-cutoff and from the training or
   development side, and the texts are non-empty and look like earnings releases.

Test companies are never opened; EXP-0020's list holds none.

    conda run --no-capture-output -n nlab python research/experiments/exp0021_s2a_pull.py draw
    conda run --no-capture-output -n nlab python research/experiments/exp0021_s2a_pull.py fetch
    conda run --no-capture-output -n nlab python research/experiments/exp0021_s2a_pull.py audit
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0003_guidance_pairs as e3  # noqa: E402  (frozen; sets the SEC rate limit to 5 a second)

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
LIST = DRIVE / "s2" / "exp0020" / "releases.jsonl"
OUT = DRIVE / "s2" / "exp0021"
TEXTS = OUT / "releases"

CUTOFF = "2026-06-30"
SIDES = ("train", "dev")
YEARS = tuple(str(y) for y in range(2019, 2026))  # filing years; 2025 added on the owner's say-so
LARGE = ("top 50", "51 to 250")
PER_LARGE = 4
REST = 500
SEED = 20261120


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


def candidates() -> list[dict]:
    rows = [json.loads(l) for l in LIST.read_text(encoding="utf-8").splitlines() if l]
    return [
        r for r in rows
        if r["labelled"] and not r["post_cutoff"] and not r["on_drive"]
        and r["side"] in SIDES and r["filing_date"][:4] in YEARS and r["filing_date"] <= CUTOFF
    ]


def make_draw() -> list[dict]:
    rng = random.Random(SEED)
    by: dict[str, list[dict]] = collections.defaultdict(list)
    for r in candidates():
        by[r["cik"]].append(r)
    for rs in by.values():
        rs.sort(key=lambda r: r["acceptance"])
    chosen = []
    large = sorted(c for c, rs in by.items() if rs[0]["tier"] in LARGE)
    for cik in large:
        years = sorted({r["filing_date"][:4] for r in by[cik]})
        for y in sorted(rng.sample(years, min(PER_LARGE, len(years)))):
            chosen.append(rng.choice([r for r in by[cik] if r["filing_date"][:4] == y]))
    rest = sorted(c for c, rs in by.items() if rs[0]["tier"] not in LARGE)
    for cik in sorted(rng.sample(rest, min(REST, len(rest)))):
        chosen.append(rng.choice(by[cik]))
    return chosen


def draw(_: argparse.Namespace) -> None:
    need_drive()
    chosen = make_draw()
    with open(OUT / "draw.jsonl", "w", encoding="utf-8") as fh:
        for r in chosen:
            fh.write(json.dumps(r) + "\n")
    tiers = collections.Counter(r["tier"] for r in chosen)
    years = collections.Counter(r["filing_date"][:4] for r in chosen)
    by_tier_year = collections.Counter((r["tier"], r["filing_date"][:4]) for r in chosen)
    summary = {
        "candidates": len(candidates()),
        "drawn": len(chosen),
        "companies": len({r["cik"] for r in chosen}),
        "by_tier": dict(sorted(tiers.items())),
        "by_year": dict(sorted(years.items())),
        "by_tier_year": {f"{t} {y}": n for (t, y), n in sorted(by_tier_year.items())},
        "by_side": dict(collections.Counter(r["side"] for r in chosen)),
        "seed": SEED,
    }
    (OUT / "draw_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def fetch(_: argparse.Namespace) -> None:
    need_drive()
    if not os.environ.get("EDGAR_IDENTITY"):
        sys.exit("EDGAR_IDENTITY is not set")
    from edgar.documents import parse_html
    from edgar.httprequests import download_file

    TEXTS.mkdir(parents=True, exist_ok=True)
    chosen = [json.loads(l) for l in (OUT / "draw.jsonl").read_text(encoding="utf-8").splitlines() if l]
    log = OUT / "fetch_log.jsonl"
    done = set()
    if log.exists():
        done = {
            r["accession"]
            for r in (json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l)
            if not r["status"].startswith("error")
        }
    print(f"[fetch] {len(chosen)} drawn, {len(done)} done before", flush=True)
    t0, n = time.time(), 0
    with open(log, "a", encoding="utf-8") as fh:
        for r in chosen:
            acc = r["accession"]
            if acc in done:
                continue
            path = TEXTS / f"{r['cik']}_{acc}.txt"
            status = "ok"
            try:
                url = e3.press_release_url(int(r["cik"]), acc, download_file)
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
            if n % 100 == 0:
                print(f"[fetch] {n} done, {n / (time.time() - t0):.2f}/s", flush=True)
    print(f"[fetch] finished: {n} this run", flush=True)


EARNINGS = re.compile(r"\b(revenue|revenues|net sales|net income|net loss|earnings per share)\b", re.I)


def audit(_: argparse.Namespace) -> None:
    need_drive()
    chosen = [json.loads(l) for l in (OUT / "draw.jsonl").read_text(encoding="utf-8").splitlines() if l]
    again = make_draw()
    assert [r["accession"] for r in again] == [r["accession"] for r in chosen], "the draw does not reproduce"
    assert len({r["accession"] for r in chosen}) == len(chosen), "a release is drawn twice"
    for r in chosen:
        assert r["side"] in SIDES, "a test company in the draw"
        assert r["filing_date"] <= CUTOFF and not r["post_cutoff"], "a post-cutoff release in the draw"
        assert r["labelled"] and not r["on_drive"]
    report = {"drawn": len(chosen), "draw_reproduces": True}
    log = OUT / "fetch_log.jsonl"
    if log.exists():
        last = {}
        for l in log.read_text(encoding="utf-8").splitlines():
            if l:
                x = json.loads(l)
                last[x["accession"]] = x["status"]
        status = collections.Counter(s if not s.startswith("error") else "error" for s in last.values())
        lengths, earnings = [], 0
        for r in chosen:
            p = TEXTS / f"{r['cik']}_{r['accession']}.txt"
            if last.get(r["accession"]) == "ok" and p.exists():
                t = p.read_text(encoding="utf-8")
                lengths.append(len(t))
                earnings += bool(EARNINGS.search(t))
        report |= {
            "status": dict(status),
            "not_attempted": len(chosen) - len(last),
            "texts": len(lengths),
            "empty_texts": sum(1 for x in lengths if x == 0),
            "median_chars": statistics.median(lengths) if lengths else None,
            "with_earnings_words": earnings,
        }
    (OUT / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("draw", draw), ("fetch", fetch), ("audit", audit)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
