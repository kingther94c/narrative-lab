"""EXP-0020: episodes, candidate labels and rule baselines for sub-study S2 (step S2-a).

Design: research/design/substudy_s2_blind_replay.md, §8 and §10. An engineering measurement with
no hypothesis and no model call. It reads two archives already on the external drive, the XBRL
company facts snapshot of 2026-11-14 and the bulk submissions archive of 2026-11-12, and pulls
nothing from the network.

It answers three questions the design needs before any Claude call is spent:

1. ``series``: can a quarterly series be built for each company from values as they were filed
   at the time? Each quarter is taken from the first 10-Q or 10-K that reports it, and its
   year-on-year comparison uses the prior-year figure printed in that same filing, so a growth
   rate here is the one a reader saw then. A fiscal fourth quarter is the year less nine months.
2. ``label``: which next-quarter label has a base rate near 50% and leaves a simple rule little
   to gain? Four candidates, each with its majority rate and its best rule.
3. ``targets``: how many earnings releases (8-K, Item 2.02) from 2019 on exist for these
   companies, how many map to a labelled quarter, and how many are on the drive already? This is
   the list the owner needs for the pull decision (design, decision 4). Nothing is fetched.

Only training and development companies of split v1 are read. Test companies are never opened:
Claude does not read post-cutoff test items (changelog, 2026-11-14).

    conda run --no-capture-output -n nlab python research/experiments/exp0020_s2a_episodes.py series
    conda run --no-capture-output -n nlab python research/experiments/exp0020_s2a_episodes.py label
    conda run --no-capture-output -n nlab python research/experiments/exp0020_s2a_episodes.py targets
    conda run --no-capture-output -n nlab python research/experiments/exp0020_s2a_episodes.py audit
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import random
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as e5  # noqa: E402

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
FACTS_ZIP = e5.FACTS_ZIP
BULK = DRIVE / "edgar" / "bulk" / "submissions-2026-11-12.zip"
SPLIT = DRIVE / "splits" / "split_v1_exp0003_companies.jsonl"
TEXTS = DRIVE / "edgar" / "releases"
OUT = DRIVE / "s2" / "exp0020"

CUTOFF = "2026-06-30"  # latest knowledge cutoff on the evaluation roster
DATA_END = "2026-11-11"  # last filing date in the bulk submissions archive
FIRST_END = "2018-01-01"  # quarters ending from here, so that growth rates exist from 2019
FIRST_RELEASE = "2019-01-01"
SIDES = ("train", "dev")
BAND = 0.02  # dead band on acceleration, in growth-rate points; provisional, see the design §8
SEED = 20261119
METRICS = ("revenue", "operating_income", "net_income")
FORMS = ("10-Q", "10-K")  # amendments are later filings and never the first to report a quarter


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


def universe() -> dict[str, dict]:
    """Training and development companies of split v1, keyed by 10-digit CIK."""
    out = {}
    for line in open(SPLIT, encoding="utf-8"):
        r = json.loads(line)
        if r["side"] in SIDES:
            out[r["cik"]] = r
    return out


# ---------------------------------------------------------------------------------------------
# Quarterly values as filed


def span(r: dict) -> int:
    return e5.days(r["start"], r["end"])


def is_quarter(r: dict) -> bool:
    return 80 <= span(r) <= 100


def is_nine_months(r: dict) -> bool:
    return 260 <= span(r) <= 285


def is_year(r: dict) -> bool:
    return 350 <= span(r) <= 380


def year_apart(later_end: str, earlier_end: str) -> bool:
    """52- and 53-week fiscal calendars move a period end by up to a week."""
    return abs(e5.days(earlier_end, later_end) - 365) <= 12


def rows_by_accession(gaap: dict, metric: str) -> tuple[dict[str, list[dict]], list[dict]]:
    """Rows of a metric per filing, from the first concept (in priority order) that filing tags.

    Also returns every row of every concept, for the nine-month figures a fourth quarter needs.
    """
    spec = e5.METRICS[metric]
    per: dict[str, dict[str, list[dict]]] = {}
    every: list[dict] = []
    for c in spec["concepts"]:
        for r in gaap.get(c, {}).get("units", {}).get(spec["unit"], []):
            if "start" not in r or r.get("form") not in FORMS:
                continue
            if r["end"] > r["filed"]:  # a mistagged period: no filing reports a quarter still to end
                continue
            per.setdefault(r["accn"], {}).setdefault(c, []).append(r)
            every.append(r)
    chosen = {a: next(cs[c] for c in spec["concepts"] if c in cs) for a, cs in per.items()}
    return chosen, every


def latest_with_prior(rows: list[dict], pred) -> tuple[dict, dict | None] | None:
    cand = [r for r in rows if pred(r)]
    if not cand:
        return None
    cur = max(cand, key=lambda r: r["end"])
    prior = [r for r in cand if year_apart(cur["end"], r["end"])]
    return cur, (prior[0] if prior else None)


def nine_months_before(every: list[dict], year_row: dict, same_accn: str | None = None) -> dict | None:
    """The first-filed nine-month figure of the fiscal year `year_row` covers."""
    cand = [r for r in every if is_nine_months(r) and abs(e5.days(r["start"], year_row["start"])) <= 5]
    if same_accn:
        same = [r for r in cand if r["accn"] == same_accn]
        if same:
            return same[0]
    return min(cand, key=lambda r: r["filed"]) if cand else None


def quarter_of(rows: list[dict], every: list[dict], form: str) -> dict | None:
    """The quarter a filing reports and its prior-year comparison: {end, cur, prior, derived}."""
    if form == "10-Q":
        got = latest_with_prior(rows, is_quarter)
        if not got:
            return None
        cur, prior = got
        return {"end": cur["end"], "cur": cur["val"], "prior": prior["val"] if prior else None, "derived": False}
    year = latest_with_prior(rows, is_year)
    if not year:
        return None
    fy, fy_prior = year
    direct = [r for r in rows if is_quarter(r) and abs(e5.days(r["end"], fy["end"])) <= 5]
    if direct:  # some 10-Ks tag the fourth quarter itself
        prior = [r for r in rows if is_quarter(r) and year_apart(direct[0]["end"], r["end"])]
        return {"end": fy["end"], "cur": direct[0]["val"], "prior": prior[0]["val"] if prior else None,
                "derived": False}
    nine = nine_months_before(every, fy)
    if not nine:
        return None
    out = {"end": fy["end"], "cur": fy["val"] - nine["val"], "prior": None, "derived": True}
    if fy_prior:
        nine_prior = nine_months_before(every, fy_prior, same_accn=nine["accn"])
        if nine_prior:
            out["prior"] = fy_prior["val"] - nine_prior["val"]
    return out


def company_series(gaap: dict) -> list[dict]:
    """One record per fiscal quarter, from the first filing that reports it, oldest first."""
    per_metric = {m: rows_by_accession(gaap, m) for m in METRICS}
    rev_rows, rev_every = per_metric["revenue"]
    found: list[dict] = []
    for accn, rows in rev_rows.items():
        form, filed = rows[0]["form"], min(r["filed"] for r in rows)
        q = quarter_of(rows, rev_every, form)
        if not q or q["end"] < FIRST_END or not q["cur"] or q["cur"] <= 0:
            continue
        rec = {"end": q["end"], "accn": accn, "form": form, "filed": filed, "derived": q["derived"],
               "rev": q["cur"], "rev_prior": q["prior"]}
        for m in ("operating_income", "net_income"):
            m_rows, m_every = per_metric[m]
            mq = quarter_of(m_rows[accn], m_every, form) if accn in m_rows else None
            ok = mq is not None and abs(e5.days(mq["end"], q["end"])) <= 5
            rec[m], rec[m + "_prior"] = (mq["cur"], mq["prior"]) if ok else (None, None)
        found.append(rec)
    found.sort(key=lambda r: (r["end"], r["filed"]))
    series: list[dict] = []
    for rec in found:  # a quarter keeps its first filing
        if series and abs(e5.days(series[-1]["end"], rec["end"])) <= 5:
            if rec["filed"] < series[-1]["filed"]:
                series[-1] = rec
            continue
        series.append(rec)
    for rec in series:
        p = rec["rev_prior"]
        rec["g"] = rec["rev"] / p - 1 if p and p > 0 else None
    return series


def series(_: argparse.Namespace) -> None:
    need_drive()
    uni = universe()
    zf = zipfile.ZipFile(FACTS_ZIP)
    names = set(zf.namelist())
    n_co = n_rec = 0
    with open(OUT / "series.jsonl", "w", encoding="utf-8") as f:
        for i, (cik, co) in enumerate(sorted(uni.items())):
            name = f"CIK{cik}.json"
            if name not in names:
                continue
            gaap = json.loads(zf.read(name)).get("facts", {}).get("us-gaap", {})
            recs = company_series(gaap)
            if not recs:
                continue
            n_co += 1
            n_rec += len(recs)
            for rec in recs:
                f.write(json.dumps({"cik": cik, "side": co["side"], "size_band": co["size_band"], **rec}) + "\n")
            if i % 200 == 0:
                print(f"[series] {i}/{len(uni)} companies read", flush=True)
    summary = {"companies_in_universe": len(uni), "companies_with_series": n_co, "quarters": n_rec}
    (OUT / "series_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


# ---------------------------------------------------------------------------------------------
# Labels and rule baselines


def load_series() -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = collections.defaultdict(list)
    for line in open(OUT / "series.jsonl", encoding="utf-8"):
        r = json.loads(line)
        by[r["cik"]].append(r)
    return by


def margin_up(r: dict) -> bool | None:
    o, op = r.get("operating_income"), r.get("operating_income_prior")
    if o is None or op is None or not r.get("rev_prior") or r["rev_prior"] <= 0:
        return None
    return o / r["rev"] > op / r["rev_prior"]


def income_up(r: dict) -> bool | None:
    n, np_ = r.get("net_income"), r.get("net_income_prior")
    return None if n is None or np_ is None else n > np_


def episodes(by: dict[str, list[dict]]) -> list[dict]:
    """One episode per quarter that has a following quarter: what was known, and what came next."""
    out = []
    for cik, recs in by.items():
        for i, r in enumerate(recs[:-1]):
            nxt = recs[i + 1]
            if not 80 <= e5.days(r["end"], nxt["end"]) <= 100 or r["g"] is None or nxt["g"] is None:
                continue
            if nxt["filed"] <= r["filed"]:  # a late filer catching up: the next quarter was not unknown
                continue
            prev = recs[i - 1] if i and 80 <= e5.days(recs[i - 1]["end"], r["end"]) <= 100 else None
            accel = nxt["g"] - r["g"]
            out.append({
                "cik": cik, "side": r["side"], "size_band": r["size_band"], "end": r["end"],
                "filed": r["filed"], "next_end": nxt["end"], "next_filed": nxt["filed"],
                "derived": r["derived"] or nxt["derived"], "g": r["g"], "g_next": nxt["g"],
                "accel_prev": (r["g"] - prev["g"]) if prev and prev["g"] is not None else None,
                "y_positive": nxt["g"] > 0,
                "y_accelerates": None if abs(accel) <= BAND else accel > 0,
                "y_margin_up": margin_up(nxt), "y_income_up": income_up(nxt),
                "x_margin_up": margin_up(r), "x_income_up": income_up(r),
            })
    return out


def rate(pairs: list[tuple[bool, bool]]) -> dict:
    """Base rate of the label and accuracy of a rule, on the items where both are defined."""
    n = len(pairs)
    if not n:
        return {"n": 0}
    base = sum(y for y, _ in pairs) / n
    return {"n": n, "base_rate": round(base, 4), "majority": round(max(base, 1 - base), 4),
            "rule": round(sum(y == p for y, p in pairs) / n, 4)}


def table(eps: list[dict]) -> dict:
    def pairs(y, x):
        return [(e[y], x(e)) for e in eps if e[y] is not None and x(e) is not None]

    def sign(v):
        return None if v is None else v > 0

    return {
        "growth_positive / persistence": rate(pairs("y_positive", lambda e: e["g"] > 0)),
        "growth_accelerates / persistence": rate(pairs("y_accelerates", lambda e: sign(e["accel_prev"]))),
        "growth_accelerates / reversal": rate(pairs(
            "y_accelerates", lambda e: None if e["accel_prev"] is None else e["accel_prev"] < 0)),
        "margin_up / persistence": rate(pairs("y_margin_up", lambda e: e["x_margin_up"])),
        "income_up / persistence": rate(pairs("y_income_up", lambda e: e["x_income_up"])),
    }


def label(_: argparse.Namespace) -> None:
    need_drive()
    eps = [e for e in episodes(load_series()) if e["end"] >= "2019-01-01"]
    with open(OUT / "labels.jsonl", "w", encoding="utf-8") as f:
        for e in eps:
            f.write(json.dumps(e) + "\n")
    old = [e for e in eps if e["filed"] <= CUTOFF]
    clean = [e for e in eps if e["filed"] > CUTOFF]  # by the 10-Q date; `targets` uses the release date
    dead = sum(e["y_accelerates"] is None for e in eps)
    summary = {
        "band": BAND, "episodes": len(eps), "companies": len({e["cik"] for e in eps}),
        "in_dead_band": dead, "derived_share": round(sum(e["derived"] for e in eps) / max(len(eps), 1), 4),
        "all": table(eps), "report_filed_by_cutoff": table(old), "report_filed_after_cutoff": table(clean),
        "by_year": {y: table([e for e in eps if e["end"][:4] == y])
                    for y in sorted({e["end"][:4] for e in eps})},
        "by_size_band": {b: table([e for e in eps if e["size_band"] == b])
                         for b in sorted({e["size_band"] for e in eps})},
        "by_side": {s: table([e for e in eps if e["side"] == s]) for s in SIDES},
    }
    (OUT / "label_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("episodes", "companies", "in_dead_band", "derived_share")}))
    for scope in ("all", "report_filed_by_cutoff", "report_filed_after_cutoff"):
        print(f"\n{scope}")
        for name, r in summary[scope].items():
            print(f"  {name:36s} {r}")


# ---------------------------------------------------------------------------------------------
# Earnings releases since 2019


def filings(zf: zipfile.ZipFile, cik: str):
    """Every filing of a company, the overflow files of the bulk archive included."""
    d = json.loads(zf.read(f"CIK{cik}.json"))
    blocks = [(d.get("filings") or {}).get("recent") or {}]
    for extra in (d.get("filings") or {}).get("files") or []:
        if extra.get("filingTo", "9999") >= FIRST_RELEASE:
            blocks.append(json.loads(zf.read(extra["name"])))
    keys = ("form", "filingDate", "acceptanceDateTime", "items", "accessionNumber")
    for b in blocks:
        for vals in zip(*(b.get(k, []) for k in keys)):
            yield dict(zip(keys, vals))


TIERS = (("top 50", 50), ("51 to 250", 250))  # by revenue; a stand-in for how well a company is known


def tier_of(by: dict[str, list[dict]]) -> dict[str, str]:
    """Rank companies by their largest quarterly revenue in their last four quarters."""
    ranked = sorted(by, key=lambda c: -max(r["rev"] for r in by[c][-4:]))
    out = {}
    for i, cik in enumerate(ranked):
        out[cik] = next((name for name, top in TIERS if i < top), "the rest")
    return out


def targets(_: argparse.Namespace) -> None:
    need_drive()
    uni = universe()
    by = load_series()
    eps = {(e["cik"], e["end"]): e for e in episodes(by)}
    labelled = set(eps)
    tier = tier_of(by)
    zf = zipfile.ZipFile(BULK)
    names = set(zf.namelist())
    rows = []
    for cik, co in sorted(uni.items()):
        if f"CIK{cik}.json" not in names:
            continue
        seen = set()
        for r in filings(zf, cik):
            acc, day = r["accessionNumber"], r["filingDate"]
            if r["form"] != "8-K" or "2.02" not in (r["items"] or "") or acc in seen:
                continue
            if not FIRST_RELEASE <= day <= DATA_END:
                continue
            seen.add(acc)
            ends = [q["end"] for q in by.get(cik, []) if 0 <= e5.days(q["end"], day) <= 120]
            end = max(ends) if ends else None
            rows.append({
                "cik": cik, "side": co["side"], "size_band": co["size_band"], "accession": acc,
                "filing_date": day, "acceptance": r["acceptanceDateTime"], "post_cutoff": day > CUTOFF,
                "quarter_end": end, "labelled": (cik, end) in labelled, "tier": tier.get(cik),
                "on_drive": (TEXTS / f"{cik}_{acc}.txt").exists(),
            })
    with open(OUT / "releases.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    def count(sel):
        return {"releases": len(sel), "companies": len({r["cik"] for r in sel}),
                "with_quarter": sum(r["quarter_end"] is not None for r in sel),
                "labelled": sum(r["labelled"] for r in sel), "on_drive": sum(r["on_drive"] for r in sel),
                "labelled_not_on_drive": sum(r["labelled"] and not r["on_drive"] for r in sel)}

    summary = {
        "all": count(rows),
        "by_year": {y: count([r for r in rows if r["filing_date"][:4] == y])
                    for y in sorted({r["filing_date"][:4] for r in rows})},
        "post_cutoff_by_month": {m: count([r for r in rows if r["post_cutoff"] and r["filing_date"][:7] == m])
                                 for m in sorted({r["filing_date"][:7] for r in rows if r["post_cutoff"]})},
        "by_size_band": {b: count([r for r in rows if r["size_band"] == b])
                         for b in sorted({r["size_band"] for r in rows})},
        "by_side": {s: count([r for r in rows if r["side"] == s]) for s in SIDES},
    }
    # Episodes dated by their release, one per labelled quarter: the first release that reports it.
    first: dict[tuple[str, str], dict] = {}
    for r in sorted(rows, key=lambda r: r["acceptance"]):
        if r["labelled"]:
            first.setdefault((r["cik"], r["quarter_end"]), r)
    cells: dict[str, dict[str, list[dict]]] = collections.defaultdict(lambda: collections.defaultdict(list))
    for key, r in first.items():
        period = "released after the cutoff" if r["post_cutoff"] else "released by the cutoff"
        cells[period]["all"].append(eps[key])
        cells[period][r["tier"]].append(eps[key])
    summary["episodes_by_release"] = {
        period: {name: {"episodes": len(sel), "companies": len({e["cik"] for e in sel}),
                        "outside_dead_band": sum(e["y_accelerates"] is not None for e in sel),
                        "labels": table(sel)}
                 for name, sel in sorted(by_tier.items())}
        for period, by_tier in sorted(cells.items())}
    (OUT / "targets_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("all", "by_year", "post_cutoff_by_month", "by_side")}, indent=1))
    for period, by_tier in summary["episodes_by_release"].items():
        for name, cell in by_tier.items():
            acc = cell["labels"]["growth_accelerates / reversal"]
            print(f"{period:26s} {name:10s} episodes {cell['episodes']:6d} companies {cell['companies']:5d} "
                  f"outside dead band {cell['outside_dead_band']:6d} acceleration {acc}")


# ---------------------------------------------------------------------------------------------
# Checks


def audit(_: argparse.Namespace) -> None:
    need_drive()
    uni = universe()
    assert all(c["side"] in SIDES for c in uni.values())
    by = load_series()
    assert set(by) <= set(uni), "a company outside the training and development sides was read"
    recs = [r for rs in by.values() for r in rs]
    for rs in by.values():  # one record per quarter, oldest first, first filing kept
        ends = [r["end"] for r in rs]
        assert ends == sorted(ends) and len(set(ends)) == len(ends)
        assert all(e5.days(a, b) > 5 for a, b in zip(ends, ends[1:]))
    assert all(r["filed"] >= r["end"] for r in recs), "a quarter filed before it ended"
    gs = sorted(r["g"] for r in recs if r["g"] is not None)
    median = gs[len(gs) // 2]
    assert -0.05 < median < 0.20, f"median year-on-year growth {median:.3f} is implausible"
    # Recompute a sample of quarterly-report growth rates straight from the archive.
    zf = zipfile.ZipFile(FACTS_ZIP)
    rng = random.Random(SEED)
    sample = rng.sample([r for r in recs if r["form"] == "10-Q" and r["g"] is not None], 40)
    for r in sample:
        gaap = json.loads(zf.read(f"CIK{r['cik']}.json"))["facts"]["us-gaap"]
        rows = [x for c in e5.METRICS["revenue"]["concepts"]
                for x in gaap.get(c, {}).get("units", {}).get("USD", [])
                if x["accn"] == r["accn"] and "start" in x and is_quarter(x)]
        cur = [x["val"] for x in rows if x["end"] == r["end"]]
        assert r["rev"] in cur, (r["cik"], r["accn"])
        assert any(abs(r["rev"] / x["val"] - 1 - r["g"]) < 1e-9 for x in rows
                   if x["val"] > 0 and year_apart(r["end"], x["end"])), (r["cik"], r["accn"])
    eps = [json.loads(line) for line in open(OUT / "labels.jsonl", encoding="utf-8")]
    assert all(e["next_filed"] > e["filed"] for e in eps), "a next quarter filed before its predecessor"
    print(json.dumps({
        "companies": len(by), "quarters": len(recs), "derived_quarters": sum(r["derived"] for r in recs),
        "quarters_without_growth": sum(r["g"] is None for r in recs), "median_growth": round(median, 4),
        "growth_p05_p95": [round(gs[len(gs) // 20], 3), round(gs[-len(gs) // 20], 3)],
        "episodes": len(eps), "recomputed_ok": len(sample),
    }, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("series", series), ("label", label), ("targets", targets), ("audit", audit)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
