"""EXP-0032: the rewrite template, version 2 (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0032 (2026-11-22). EXP-0031's
template lost guidance (stated in dollars, it had no field) and leaked segment revenue shares.
Version 2, on the same 90 episodes:

- the reader also copies guided revenue amounts exactly as printed, with their unit; code turns
  them into growth against the year-ago period as first filed (EXP-0020's series), so no amount
  reaches the brief: next quarter against the quarter three before this one; full year (the
  fiscal year in progress after the release; after a fourth-quarter release, the next one)
  against the four quarters of the last completed fiscal year;
- segments keep their growth and their order, not their share of revenue;
- two ratio sheets: EXP-0026's (two earlier quarters, noised; arm "s2") and a new one with four
  earlier quarters, noised the same way (arm "s4").
The brief is EXP-0031's FULL form (facts plus the reader's judgements and next-quarter effects).

    conda run --no-capture-output -n nlab python research/experiments/exp0032_s2b_rewrite_v2.py prepare-e
    (emit, run with exp0027, ingest: run exp0032, items_e)
    conda run --no-capture-output -n nlab python research/experiments/exp0032_s2b_rewrite_v2.py build
    (emit, run, ingest: items_ap)
    conda run --no-capture-output -n nlab python research/experiments/exp0032_s2b_rewrite_v2.py score
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402
import exp0029_s2b_rationale_audit as e29  # noqa: E402
import exp0030_s2b_guided_redaction as e30  # noqa: E402
import exp0031_s2b_rewrite as e31  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0032"
RUN = "exp0032"
SEED = 20261127
UNITS = {"thousand": 1e3, "million": 1e6, "billion": 1e9}
ARMS = ("s2", "s4")

_seg_old = '"segments": [{"share_of_revenue": <number or null>, "growth": <number or null>}],'
_basis = ' "next_quarter_guidance_basis": "<' + " | ".join(e31.CHOICES["next_quarter_guidance_basis"]) + '>",\n'
_rule = "- Segments: at most four, largest share of revenue first. Do not name them.\n"
assert _seg_old in e31.E_PROMPT and _basis in e31.E_PROMPT and _rule in e31.E_PROMPT
E_PROMPT = (e31.E_PROMPT
            .replace(_seg_old, '"segments": [{"growth": <number or null>}],')
            .replace(_basis, _basis
                     + ' "next_quarter_revenue_guidance_amount": {"low": <number as printed or null>, "high": <number as printed or null>, "unit": "<thousand | million | billion>"},\n'
                     + ' "full_year_revenue_guidance_amount": {"low": <number as printed or null>, "high": <number as printed or null>, "unit": "<thousand | million | billion>"},\n')
            .replace(_rule, _rule + "- Revenue guidance: the company's own guidance for total revenue (or net sales) for the next fiscal quarter, and for the fiscal year in progress after this release (after a release for the fourth fiscal quarter, the next fiscal year). Give growth rates where the release states them; give amounts exactly as printed, with their unit, where it states amounts, keyed in quotes as \"next_quarter_revenue_guidance_amount.low\" and so on. Do not convert amounts yourself. Leave both empty if the guidance is for another measure.\n"))


def prepare_e(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "items_e.jsonl", "w", encoding="utf-8") as fh:
        for k in e26.load(e26.OUT / "key.jsonl"):
            fh.write(json.dumps({"id": f"e{k['episode']:03d}", "agent": e26.PM, "prompt": E_PROMPT + e31.raw_release(k["episode"])},
                                ensure_ascii=False) + "\n")
    print(f"[prepare-e] {OUT / 'items_e.jsonl'}")


def replies() -> dict[str, str]:
    return {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / RUN) if r["canary_ok"]}


def bases(series: list[dict], quarter_end: str) -> dict:
    """Year-ago revenue for next-quarter and full-year guidance, from the as-filed series."""
    by_back = {e22.quarters_between(r["end"], quarter_end): r for r in series}
    nq = by_back.get(3)
    fy_ends = [r for r in series if r["form"] == "10-K" and r["end"] < quarter_end]
    out = {"next_quarter": nq["rev"] if nq and nq.get("rev") else None, "full_year": None}
    if fy_ends:
        k = e22.quarters_between(fy_ends[-1]["end"], quarter_end)
        end_back = 0 if k == 4 else k  # after a fourth-quarter release the guided year follows the one just reported
        quarters = [by_back.get(end_back + j) for j in range(4)]
        if all(q and q.get("rev") for q in quarters):
            out["full_year"] = sum(q["rev"] for q in quarters)
    return out


def amount(j: dict, field: str, release: str, log: collections.Counter) -> tuple[float | None, float | None]:
    a = j.get(field) or {}
    if not isinstance(a, dict) or a.get("unit") not in UNITS:
        return None, None
    nd, quotes = e29.norm(release), j.get("quotes") or {}
    vals = []
    for side in ("low", "high"):
        x = a.get(side)
        if x is None:
            vals.append(None)
            continue
        q = quotes.get(f"{field}.{side}")
        ok = isinstance(x, (int, float)) and isinstance(q, str) and e29.norm(q).strip(" .…\"'") in nd and e31.num_in(float(x), q)
        log["amounts_kept" if ok else "amounts_dropped"] += 1
        vals.append(float(x) * UNITS[a["unit"]] if ok else None)
    lo, hi = vals
    return (lo if lo is not None else hi), (hi if hi is not None else lo)


def implied(lo: float | None, hi: float | None, base: float | None, log: collections.Counter, tag: str) -> tuple[float | None, float | None]:
    if lo is None or not base:
        return None, None
    g = (100 * (lo / base - 1), 100 * (hi / base - 1))
    if not all(-50 < x < 100 for x in g):  # a unit or measure mismatch, not a forecast
        log[f"{tag}_conversion_out_of_range"] += 1
        return None, None
    log[f"{tag}_converted"] += 1
    return g


def render(v: dict) -> str:
    v = {**v, "segments": [{"share_of_revenue": None, "growth": s["growth"]} for s in v["segments"]]}
    text = e31.render(v, True)
    text = text.replace("share of revenue not stated, ", "")
    for tag, label in (("next_quarter", "Next quarter revenue growth"), ("full_year", "Full year revenue growth")):
        src = v.get(f"{tag}_guidance_source")
        if src == "implied":
            rng = e31.rng_text(v[f"{tag}_guidance_growth_low"], v[f"{tag}_guidance_growth_high"])
            old = next(l for l in text.splitlines() if l.startswith(f"  {label}:"))
            text = text.replace(old, f"  {label}: {rng} (implied by the guided amount, against the year-ago period as first filed)")
    return text


def build(_: argparse.Namespace) -> None:
    e23.need_drive()
    got = replies()
    series = e22.load_series()
    e22.SHEET_QUARTERS = 4
    briefs, bad, tot = {}, [], collections.Counter()
    for k in e26.load(e26.OUT / "key.jsonl"):
        i = k["episode"]
        j = e31.as_json(got.get(f"e{i:03d}", ""))
        if j is None:
            bad.append(i)
            continue
        rel = e31.raw_release(i)
        v, log = e31.verify(j, rel)
        b = bases(series.get(k["cik"], []), k["quarter_end"])
        for tag, f in (("next_quarter", "next_quarter_revenue_guidance_amount"), ("full_year", "full_year_revenue_guidance_amount")):
            if v[f"{tag}_guidance_growth_low"] is not None or v[f"{tag}_guidance_growth_high"] is not None:
                v[f"{tag}_guidance_source"] = "stated"
                log[f"{tag}_stated"] += 1
                continue
            lo, hi = amount(j, f, rel, log)
            glo, ghi = implied(lo, hi, b[tag], log, tag)
            if glo is not None:
                v[f"{tag}_guidance_growth_low"], v[f"{tag}_guidance_growth_high"] = glo, ghi
                v[f"{tag}_guidance_source"] = "implied"
                if tag == "next_quarter":
                    v["next_quarter_guidance_basis"] = "reported"
            elif lo is not None:
                log[f"{tag}_amount_without_base"] += 1
        sheet4 = e22.sheet(series.get(k["cik"], []), k["filing_date"], k["quarter_end"], True, True,
                           random.Random(SEED * 1000 + i), e22.SIGMA).rstrip()
        briefs[i] = {"brief": render(v), "form": v, "sheet2": e31.sheet(i), "sheet4": sheet4}
        tot.update(log)
    (OUT / "briefs.json").write_text(json.dumps(briefs, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(OUT / "items_ap.jsonl", "w", encoding="utf-8") as fh:
        for i, b in sorted(briefs.items()):
            for arm, sh in (("s2", b["sheet2"]), ("s4", b["sheet4"])):
                text = sh + "\n\nThe summary:\n\n" + b["brief"]
                fh.write(json.dumps({"id": f"a{arm}-{i:03d}", "agent": e31.e28.AGENT, "prompt": e31.A_PROMPT + text}, ensure_ascii=False) + "\n")
                fh.write(json.dumps({"id": f"p{arm}-{i:03d}", "agent": e26.PM, "prompt": e31.P_PROMPT + text}, ensure_ascii=False) + "\n")
    forms = [b["form"] for b in briefs.values()]
    rep = {"briefs": len(briefs), "unparsed": bad, "log": dict(tot),
           "coverage": {"next_quarter_guidance": sum(f["next_quarter_guidance_growth_low"] is not None for f in forms),
                        "full_year_guidance": sum(f["full_year_guidance_growth_low"] is not None for f in forms),
                        "segments": sum(bool(f["segments"]) for f in forms)}}
    (OUT / "build_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    got = replies()
    got31 = e31.replies()
    briefs = {int(i): b for i, b in json.loads((OUT / "briefs.json").read_text(encoding="utf-8")).items()}
    rng = random.Random(SEED)
    p26 = {}
    for r in e23.records(e23.ROOT / e26.RUN):
        m = e26.PROB.search(r["reply"])
        if r["canary_ok"] and m:
            p26[r["id"].split(".")[0]] = int(m.group(1)) / 100

    def prob(reply: str | None) -> float | None:
        m = e26.PROB.search(reply or "")
        return int(m.group(1)) / 100 if m and int(m.group(1)) <= 100 else None

    def toward(i: int, x: float | None) -> float | None:
        return None if x is None else (x if key[i]["accelerates"] else 1 - x)

    def ci(xs: list[float], ys: list[float] | None = None) -> dict:
        if not xs or (ys is not None and not ys):
            return {"n": len(xs)}
        est = statistics.mean(xs) - (statistics.mean(ys) if ys else 0)
        d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) - (statistics.mean(rng.choices(ys, k=len(ys))) if ys else 0)
                   for _ in range(10_000))
        return {"est": round(est, 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(xs), "n_ref": len(ys) if ys else None}

    grp = {g: [i for i in briefs if key[i]["group"] == g] for g in ("old", "clean")}
    raw = {i: toward(i, p26.get(f"v{i:03d}-0")) for i in briefs}
    v31 = {i: toward(i, prob(got31.get(f"pf{i:03d}"))) for i in briefs}
    out: dict = {"briefs": len(briefs), "coverage": json.loads((OUT / "build_summary.json").read_text())["coverage"]}
    hits_by, ro_by = {}, {}
    for arm in ARMS:
        o: dict = {}
        hits = {i: e30.read(got[f"a{arm}-{i:03d}"], key[i]) for i in briefs if f"a{arm}-{i:03d}" in got}
        ro = {i: toward(i, prob(got.get(f"p{arm}-{i:03d}"))) for i in briefs}
        hits_by[arm], ro_by[arm] = hits, ro
        cells = {"all": list(briefs), "old": grp["old"], "clean": grp["clean"],
                 "top 50": [i for i in briefs if key[i]["tier"] == "top 50"], "51 to 250": [i for i in briefs if key[i]["tier"] == "51 to 250"]}
        o["c1_attacker"] = {c: {m: ci([float(hits[i][m]) for i in ids if i in hits]) for m in ("top1", "top3", "quarter")} for c, ids in cells.items()}
        conf = [h["confidence"] for h in hits.values() if h["confidence"] is not None]
        o["c1_median_confidence"] = statistics.median(conf) if conf else None
        t1 = o["c1_attacker"]["all"]["top1"].get("est")
        o["c1_verdict"] = None if t1 is None else "stopped" if t1 <= 0.20 else "not stopped" if t1 >= 0.50 else "undecided"
        col = lambda g, d: [d[i] for i in grp[g] if d.get(i) is not None]  # noqa: E731
        c2 = ci(col("old", ro), col("clean", ro))
        c2["no_leak_detected"] = "ci90" in c2 and c2["ci90"][0] <= 0 <= c2["ci90"][1]
        o["c2_leak_old_minus_clean"] = c2
        pair = [ro[i] - raw[i] for i in grp["clean"] if ro.get(i) is not None and raw.get(i) is not None]
        c3 = ci(pair)
        c3["verdict"] = None if "est" not in c3 else ("retains" if c3["est"] >= -0.03 and c3["ci90"][0] > -0.10
                                                      else "loses" if c3["ci90"][1] < 0 else "undecided")
        o["c3_clean_readout_minus_raw_paired"] = c3
        o["c3_clean_readout_minus_exp0031_full_paired"] = ci([ro[i] - v31[i] for i in grp["clean"] if ro.get(i) is not None and v31.get(i) is not None])
        o["c3_clean_accuracy"] = ci([float(x > 0.5) for x in col("clean", ro)])
        o["old_accuracy"] = ci([float(x > 0.5) for x in col("old", ro)])
        o["usable"] = (o["c1_verdict"] != "not stopped") and c2["no_leak_detected"] and c3.get("verdict") != "loses"
        rec = [ro[i] for i in grp["old"] if i in hits and hits[i]["top1"] and ro.get(i) is not None]
        non = [ro[i] for i in grp["old"] if i in hits and not hits[i]["top1"] and ro.get(i) is not None]
        o["exploratory_old_readout_recognised_vs_not"] = {"recognised": ci(rec), "not": ci(non)}
        out[arm] = o
    out["c5_sheet_effect_s4_minus_s2"] = {
        "attacker_top1": ci([float(hits_by["s4"][i]["top1"]) - float(hits_by["s2"][i]["top1"]) for i in briefs if i in hits_by["s4"] and i in hits_by["s2"]]),
        "clean_readout": ci([ro_by["s4"][i] - ro_by["s2"][i] for i in grp["clean"] if ro_by["s4"].get(i) is not None and ro_by["s2"].get(i) is not None])}
    out["c1_exp0031_full_top1_same_episodes"] = ci([float(e30.read(got31[f"af{i:03d}"], key[i])["top1"]) for i in briefs if f"af{i:03d}" in got31])
    (OUT / "score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare-e").set_defaults(fn=prepare_e)
    sub.add_parser("build").set_defaults(fn=build)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
