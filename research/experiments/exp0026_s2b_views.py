"""EXP-0026: which element of blinding removes outcome leakage from the PM's call? (S2-b step 3)

Pre-registration: research/registry/experiment_registry.md, EXP-0026 (2026-11-21). Old and clean
earnings releases of large companies, each in the eight views of EXP-0022, plus a transplant arm
(a wrong identity asserted on the fully blinded view) and a no-document prior. The readout is the
probability the model gives to the direction that happened.

1. ``prepare``: draws the episodes by seed, builds the views, writes the items (id, agent, prompt)
   for EXP-0023's ``emit`` and, apart from them, the key with labels and baselines.
2. Calls are carried headless by EXP-0025's ``run`` and checked by EXP-0023's ``ingest``.
3. ``score``: the pre-registered criteria.

    conda run --no-capture-output -n nlab python research/experiments/exp0026_s2b_views.py prepare
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run exp0026 --items <items>
    conda run --no-capture-output -n nlab python research/experiments/exp0025_s2a_cli_dispatch.py run --run exp0026
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run exp0026
    conda run --no-capture-output -n nlab python research/experiments/exp0026_s2b_views.py score
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import statistics
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0024_s2b_recall_probe as e24  # noqa: E402

DRIVE = e23.DRIVE
OUT = DRIVE / "s2" / "exp0026"
RUN = "exp0026"
SEED = 20261122
MAX_CHARS = 80_000
SHEET = 2
OLD_PER_CELL, CLEAN_PER_DIR = 15, 15
PM, RECALL = "roster-claude-opus-5-5", "s2-recall-claude-opus-5-5"
EARNINGS = re.compile(r"\b(revenue|revenues|net sales|net income|net loss|earnings per share)\b", re.I)

QUESTION = """Question: will the company's year-on-year revenue growth in the NEXT quarter be higher or lower than the year-on-year revenue growth of the quarter {this}?

Reply in exactly this format:
PROBABILITY: <a whole number from 0 to 100: the probability that next quarter's growth is HIGHER>
RATIONALE: <at most three sentences>"""

DOC_PROMPT = """You are an analyst working for a portfolio manager. Below are ratios from earlier filings and an earnings release for one quarter of one company. Names, dates or figures may have been replaced or rescaled; work with the text as it is given.

""" + QUESTION.format(this="this release reports") + """

{extra}{doc}"""

PRIOR_PROMPT = """You are an analyst working for a portfolio manager. No document is attached.

Company: {name} (ticker {ticker})
Quarter: the fiscal quarter that ended on {end}

""" + QUESTION.format(this="named above")

TRANSPLANT = "This is the earnings release of {name} (ticker {ticker}) for the fiscal quarter that ended on {end}.\n\n"


def load(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l]


def candidates() -> tuple[list[dict], list[dict]]:
    lab = {(e["cik"], e["end"]): e for e in load(DRIVE / "s2" / "exp0020" / "labels.jsonl")}

    def keep(r: dict) -> dict | None:
        e = lab.get((r["cik"], r["quarter_end"]))
        if r["tier"] == "the rest" or not e or e["y_accelerates"] is None:
            return None
        p = e22.text_path(r)
        if p is None:
            return None
        t = p.read_text(encoding="utf-8")
        if len(t) > MAX_CHARS or not EARNINGS.search(t):
            return None
        return {**r, "accelerates": e["y_accelerates"], "g": e["g"], "g_next": e["g_next"], "accel_prev": e["accel_prev"]}

    old = [x for x in map(keep, load(DRIVE / "s2" / "exp0021" / "draw.jsonl")) if x]
    clean = [x for x in map(keep, (r for r in load(e22.LIST) if r["post_cutoff"] and r["labelled"] and r["on_drive"])) if x]
    return old, clean


def prepare(_: argparse.Namespace) -> None:
    e22.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    e22.SHEET_QUARTERS = SHEET
    rng = random.Random(SEED)
    old, clean = candidates()
    series = e22.load_series()
    zf = zipfile.ZipFile(e22.BULK)
    skipped = []

    def build(ep: dict, idx: int) -> list[tuple[str, dict]] | None:
        raw = e22.text_path(ep).read_text(encoding="utf-8")
        ident = e22.identity(ep["cik"], zf)
        try:
            return [(t, {**k, "identity": ident}) for t, k in (
                e22.make_view(raw, ep, ident, series.get(ep["cik"], []), bits, SEED * 1000 + idx * 10 + v)
                for v, bits in enumerate(e22.VIEWS))]
        except Exception as err:
            skipped.append({"cik": ep["cik"], "accession": ep["accession"], "error": f"{type(err).__name__}: {str(err)[:80]}"})
            return None

    chosen: list[tuple[dict, str, list]] = []

    def take(pool: list[dict], n: int, group: str, used: set[str]) -> None:
        pool = sorted(pool, key=lambda r: r["accession"])
        rng.shuffle(pool)
        got = 0
        for ep in pool:
            if got == n:
                break
            if ep["cik"] in used:
                continue
            views = build(ep, len(chosen))
            if views is None:
                continue
            used.add(ep["cik"])
            chosen.append((ep, group, views))
            got += 1
        if got < n:
            sys.exit(f"only {got} of {n} episodes for {group}")

    used_old: set[str] = set()
    for tier in ("top 50", "51 to 250"):
        for acc in (True, False):
            take([r for r in old if r["tier"] == tier and r["accelerates"] == acc], OLD_PER_CELL, "old", used_old)
    used_clean: set[str] = set()
    for acc in (True, False):
        take([r for r in clean if r["accelerates"] == acc], CLEAN_PER_DIR, "clean", used_clean)

    items, key = [], []
    for i, (ep, group, views) in enumerate(chosen):
        name, ticker = e24.company(zf, ep["cik"])
        k = {"episode": i, "group": group, "cik": ep["cik"], "accession": ep["accession"], "tier": ep["tier"],
             "filing_date": ep["filing_date"], "quarter_end": ep["quarter_end"], "accelerates": ep["accelerates"],
             "g": ep["g"], "g_next": ep["g_next"], "accel_prev": ep["accel_prev"], "name": name, "ticker": ticker,
             "names_hidden": views[7][1]["identity"]["names"] + views[7][1]["identity"]["tickers"],
             "chars": [len(t) for t, _ in views]}
        for v, (text, vk) in enumerate(views):
            items.append({"id": f"v{i:03d}-{v}", "agent": PM, "prompt": DOC_PROMPT.format(extra="", doc=text)})
        if group == "old":
            others = sorted((r for r in old if r["cik"] != ep["cik"] and r["accelerates"] != ep["accelerates"]),
                            key=lambda r: r["accession"])
            o = rng.choice(others)
            oname, oticker = e24.company(zf, o["cik"])
            k["asserted"] = {"cik": o["cik"], "name": oname, "ticker": oticker, "quarter_end": o["quarter_end"],
                             "accelerates": o["accelerates"]}
            extra = TRANSPLANT.format(name=oname, ticker=oticker, end=o["quarter_end"])
            items.append({"id": f"t{i:03d}", "agent": PM, "prompt": DOC_PROMPT.format(extra=extra, doc=views[7][0])})
        items.append({"id": f"n{i:03d}", "agent": RECALL, "prompt": PRIOR_PROMPT.format(name=name, ticker=ticker, end=ep["quarter_end"])})
        key.append(k)
    with open(OUT / "items.jsonl", "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    with open(OUT / "key.jsonl", "w", encoding="utf-8") as fh:
        for k in key:
            fh.write(json.dumps(k) + "\n")

    def base(ks: list[dict]) -> dict:
        pers = [(k["accel_prev"] > 0) == k["accelerates"] for k in ks if k["accel_prev"]]
        return {"n": len(ks), "accelerates": sum(k["accelerates"] for k in ks),
                "persistence_acc": round(sum(pers) / len(pers), 3) if pers else None,
                "reversal_acc": round(1 - sum(pers) / len(pers), 3) if pers else None, "with_prior_change": len(pers)}

    summary = {"candidates": {"old": len(old), "clean": len(clean)}, "items": len(items),
               "by_agent": dict(collections.Counter(it["agent"] for it in items)),
               "prompt_chars_total": sum(len(it["prompt"]) for it in items),
               "median_view_chars": statistics.median(c for k in key for c in k["chars"]),
               "baselines": {g: base([k for k in key if k["group"] == g]) for g in ("old", "clean")},
               "by_cell": dict(collections.Counter(f"{k['group']} | {k['tier']} | {'up' if k['accelerates'] else 'down'}" for k in key)),
               "years_old": dict(sorted(collections.Counter(k["filing_date"][:4] for k in key if k["group"] == "old").items())),
               "skipped": skipped}
    (OUT / "prepare_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


PROB = re.compile(r"PROBABILITY:\s*(\d{1,3})", re.I)


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in load(OUT / "key.jsonl")}
    p: dict[str, float] = {}
    why: dict[str, str] = {}
    recs = e23.records(e23.ROOT / RUN)
    for r in recs:
        if not r["canary_ok"]:
            continue
        m = PROB.search(r["reply"])
        if m and 0 <= int(m.group(1)) <= 100:
            p[r["id"].split(".")[0]] = int(m.group(1)) / 100
            why[r["id"].split(".")[0]] = r["reply"]
    rng = random.Random(SEED)

    def ro(i: int, pid: str) -> float | None:  # probability given to the direction that happened
        x = p.get(pid)
        return None if x is None else (x if key[i]["accelerates"] else 1 - x)

    def ci(xs: list[float], ys: list[float] | None = None) -> dict:
        est = statistics.mean(xs) - (statistics.mean(ys) if ys else 0)
        draws = sorted(statistics.mean(rng.choices(xs, k=len(xs))) - (statistics.mean(rng.choices(ys, k=len(ys))) if ys else 0)
                       for _ in range(10_000))
        return {"est": round(est, 3), "ci90": [round(draws[499], 3), round(draws[9499], 3)], "n": len(xs), "n_ref": len(ys) if ys else None}

    grp = {g: [i for i, k in key.items() if k["group"] == g] for g in ("old", "clean")}

    def col(g: str, f) -> list[float]:
        return [x for x in (f(i) for i in grp[g]) if x is not None]

    out: dict = {"parsed": len(p), "records": len(recs), "canary_failures": sum(1 for r in recs if not r["canary_ok"])}
    out["mean_readout_by_view"] = {g: {str(e22.VIEWS[v]): round(statistics.mean(col(g, lambda i: ro(i, f"v{i:03d}-{v}"))), 3)
                                       for v in range(8)} for g in grp}
    # 1. leakage on raw text
    c1 = ci(col("old", lambda i: ro(i, f"v{i:03d}-0")), col("clean", lambda i: ro(i, f"v{i:03d}-0")))
    c1["holds"] = c1["est"] >= 0.10 and c1["ci90"][0] > 0
    out["criterion_1_raw_old_minus_clean"] = c1

    # 2. element effects, old minus clean
    def effect(i: int, s: int) -> float | None:
        on = [ro(i, f"v{i:03d}-{v}") for v, b in enumerate(e22.VIEWS) if b[s]]
        off = [ro(i, f"v{i:03d}-{v}") for v, b in enumerate(e22.VIEWS) if not b[s]]
        if None in on or None in off:
            return None
        return statistics.mean(on) - statistics.mean(off)

    out["criterion_2_element_effects"] = {}
    for s, nm in enumerate(("names", "periods", "scaling", "noise")):
        c = ci(col("old", lambda i: effect(i, s)), col("clean", lambda i: effect(i, s)))
        c["old_only"] = ci(col("old", lambda i: effect(i, s)))
        c["removes_leakage"] = c["est"] <= -0.05 and c["ci90"][1] < 0
        out["criterion_2_element_effects"][nm] = c
    ee = out["criterion_2_element_effects"]
    out["h2_period_more_negative_than_name"] = ee["periods"]["est"] < ee["names"]["est"]
    # 3. fully blinded view
    c3 = ci(col("old", lambda i: ro(i, f"v{i:03d}-7")), col("clean", lambda i: ro(i, f"v{i:03d}-7")))
    c3["no_leakage_detected"] = c3["ci90"][0] <= 0 <= c3["ci90"][1]
    out["criterion_3_blinded_old_minus_clean"] = c3

    # 4. transplant
    def toward(i: int) -> float | None:
        a, b = p.get(f"t{i:03d}"), p.get(f"v{i:03d}-7")
        if a is None or b is None:
            return None
        up = key[i]["asserted"]["accelerates"]
        return (a if up else 1 - a) - (b if up else 1 - b)

    c4 = ci(col("old", toward))
    c4["holds"] = c4["est"] >= 0.10 and c4["ci90"][0] > 0
    out["criterion_4_transplant"] = c4

    # 6. information kept, clean episodes
    def acc(g: str, f) -> float | None:
        xs = [(x > 0.5) for x in col(g, f) if x != 0.5]
        return round(sum(xs) / len(xs), 3) if xs else None

    def blind_mean(i: int) -> float | None:
        xs = [ro(i, f"v{i:03d}-{v}") for v in range(1, 8)]
        return None if None in xs else statistics.mean(xs)

    out["criterion_6_accuracy"] = {g: {"raw": acc(g, lambda i: ro(i, f"v{i:03d}-0")), "blinded": acc(g, lambda i: ro(i, f"v{i:03d}-7")),
                                       "mean_of_blinded": acc(g, blind_mean), "prior": acc(g, lambda i: ro(i, f"n{i:03d}"))} for g in grp}
    # also: prior subtracted, tiers, rationale leaks
    def net(i: int, v: int) -> float | None:
        a, b = ro(i, f"v{i:03d}-{v}"), ro(i, f"n{i:03d}")
        return None if a is None or b is None else a - b

    out["prior_mean_readout"] = {g: round(statistics.mean(col(g, lambda i: ro(i, f"n{i:03d}"))), 3) for g in grp}
    out["raw_minus_prior_old_minus_clean"] = ci(col("old", lambda i: net(i, 0)), col("clean", lambda i: net(i, 0)))
    out["raw_readout_by_tier"] = {f"{g} | {t}": round(statistics.mean(xs), 3) for g in grp for t in ("top 50", "51 to 250")
                                  if (xs := [x for x in (ro(i, f"v{i:03d}-0") for i in grp[g] if key[i]["tier"] == t) if x is not None])}
    named = collections.Counter()
    dated = collections.Counter()
    for i, k in key.items():
        for v, b in enumerate(e22.VIEWS):
            t = why.get(f"v{i:03d}-{v}")
            if t is None:
                continue
            if b[0]:
                named["views"] += 1
                named["leaks"] += bool(e22.find_terms(t, k["names_hidden"]))
            if b[1]:
                dated["views"] += 1
                dated["leaks"] += bool(re.search(r"\b(19|20)\d\d\b", t))
    out["rationale_names_company_when_hidden"] = dict(named)
    out["rationale_gives_year_when_hidden"] = dict(dated)
    (OUT / "score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(fn=prepare)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
