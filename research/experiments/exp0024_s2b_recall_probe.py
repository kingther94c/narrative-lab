"""EXP-0024: where does recall end? The closed-book probe of sub-study S2 (step S2-b, step 2).

Design: docs/plans/2026-11-20_substudy_s2_plan.md, §9 (the closed-book probe), §11 (S2-b step 2)
and the changelog of 2026-11-20 (strategy C first). The model is told a company and a quarter and
nothing else, and asked what happened next: the year-on-year revenue growth of the following
quarter, and whether it was higher or lower than the quarter named. "Unknown" is accepted in any
wording. No document is shown.

1. ``prepare``: draws company-quarters from EXP-0020's labelled episodes (training and
   development companies, outside the 2-point dead band), in seven bins of the date the outcome
   was first filed, from 2019 to after the cutoff, and three size tiers. Writes the items for
   EXP-0023's ``emit`` (id, agent, prompt) and, apart from them, the truth file it never shows.
2. ``score``: parses the replies in EXP-0023's run record and reports, by bin and tier: how often
   the model answers, the direction's accuracy, and the growth figure's error against
   persistence (this quarter's growth carried forward), each beside the bin of outcomes filed
   after the cutoff, which the model cannot have seen: there, whatever accuracy it shows comes
   from what it knows of the company, not from memory of the outcome.

    conda run --no-capture-output -n nlab python research/experiments/exp0024_s2b_recall_probe.py prepare
    conda run --no-capture-output -n nlab python research/experiments/exp0024_s2b_recall_probe.py score --run exp0024_opus
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

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab")
LABELS = DRIVE / "s2" / "exp0020" / "labels.jsonl"
RELEASES = DRIVE / "s2" / "exp0020" / "releases.jsonl"
BULK = DRIVE / "edgar" / "bulk" / "submissions-2026-11-12.zip"
OUT = DRIVE / "s2" / "exp0024"
DISPATCH = DRIVE / "s2" / "dispatch"

CUTOFF = "2026-06-30"
SEED = 20261121
PER_CELL = 10
SAMPLES = 1
AGENT = "s2-recall-claude-opus-5-5"
BINS = (("2019-2021", "2019-01-01", "2021-12-31"), ("2022-2023", "2022-01-01", "2023-12-31"),
        ("2024", "2024-01-01", "2024-12-31"), ("2025H1", "2025-01-01", "2025-06-30"),
        ("2025H2", "2025-07-01", "2025-12-31"), ("2026H1", "2026-01-01", CUTOFF),
        ("after cutoff", "2026-07-01", "2026-11-11"))
TIERS = ("top 50", "51 to 250", "the rest")

PROMPT = """Closed-book question about a public company. No document is attached; answer from memory.

Company: {name} (ticker {ticker})

Its fiscal quarter that ended on {end} was followed by the quarter that ended on {next_end}.

1. What year-on-year revenue growth did the company report for the quarter that ended on {next_end}?
2. Was that growth rate higher or lower than the year-on-year growth it reported for the quarter that ended on {end}?

If you do not know, say UNKNOWN; that is an acceptable answer to either question.

Reply in exactly this format:
GROWTH: <a percentage such as 7.5%, or UNKNOWN>
DIRECTION: <HIGHER, LOWER or UNKNOWN>
CONFIDENCE: <a whole number from 0 to 100>"""


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


def bin_of(date: str) -> str | None:
    return next((b for b, lo, hi in BINS if lo <= date <= hi), None)


def tiers() -> dict[str, str]:
    t = {}
    for l in RELEASES.read_text(encoding="utf-8").splitlines():
        if l:
            r = json.loads(l)
            t[r["cik"]] = r["tier"]
    return t


def company(zf: zipfile.ZipFile, cik: str) -> tuple[str, str]:
    d = json.loads(zf.read(f"CIK{cik}.json"))
    name = re.sub(r"\s+/[A-Z]{2,3}/?$", "", d.get("name") or "").strip()
    keep = {"INC", "CO", "LTD", "PLC", "LLC", "THE", "AND", "OF", "CORP", "LP", "SA", "NV", "AG"}
    name = " ".join(w if len(w.strip(".,&")) <= 3 and w.strip(".,").upper() not in keep and w.isupper() else w.title()
                    for w in name.split())
    return name, (d.get("tickers") or ["none"])[0]


def prepare(a: argparse.Namespace) -> None:
    need_drive()
    tier = tiers()
    zf = zipfile.ZipFile(BULK)
    names = set(zf.namelist())
    cells = collections.defaultdict(list)
    for l in LABELS.read_text(encoding="utf-8").splitlines():
        e = json.loads(l)
        b = bin_of(e["next_filed"])
        if b is None or e["y_accelerates"] is None or e["cik"] not in tier or f"CIK{e['cik']}.json" not in names:
            continue
        cells[(b, tier[e["cik"]])].append(e)
    rng = random.Random(SEED)
    items, truth = [], []
    for b, _, _ in BINS:
        for t in TIERS:
            pool = sorted(cells[(b, t)], key=lambda e: (e["cik"], e["end"]))
            rng.shuffle(pool)
            seen = set()
            chosen = []
            for e in pool:  # one quarter per company in each cell
                if e["cik"] not in seen:
                    seen.add(e["cik"])
                    chosen.append(e)
                if len(chosen) == PER_CELL:
                    break
            for e in chosen:
                name, ticker = company(zf, e["cik"])
                for s in range(SAMPLES):
                    iid = f"p{len(truth):04d}s{s}"
                    items.append({"id": iid, "agent": AGENT, "prompt": PROMPT.format(
                        name=name, ticker=ticker, end=e["end"], next_end=e["next_end"])})
                truth.append({"key": f"p{len(truth):04d}", "cik": e["cik"], "bin": b, "tier": t, "side": e["side"],
                              "end": e["end"], "next_end": e["next_end"], "next_filed": e["next_filed"],
                              "g": e["g"], "g_next": e["g_next"], "accelerates": e["y_accelerates"]})
    with open(OUT / "items.jsonl", "w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    with open(OUT / "truth.jsonl", "w", encoding="utf-8") as fh:
        for tr in truth:
            fh.write(json.dumps(tr) + "\n")
    summary = {"items": len(items), "quarters": len(truth), "samples": SAMPLES, "agent": AGENT,
               "by_cell": {f"{b} | {t}": n for (b, t), n in sorted(collections.Counter((x["bin"], x["tier"]) for x in truth).items())},
               "accelerates_rate": round(sum(x["accelerates"] for x in truth) / len(truth), 3)}
    (OUT / "prepare_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


GROWTH = re.compile(r"GROWTH:\s*(?P<v>[-+−]?\d+(?:\.\d+)?)\s*%", re.I)
DIRECTION = re.compile(r"DIRECTION:\s*(HIGHER|LOWER|UNKNOWN)", re.I)
CONF = re.compile(r"CONFIDENCE:\s*(\d{1,3})", re.I)


def parse(reply: str) -> dict:
    g = GROWTH.search(reply)
    d = DIRECTION.search(reply)
    c = CONF.search(reply)
    return {"growth": float(g.group("v").replace("−", "-")) if g else None,
            "direction": d.group(1).upper() if d else None,
            "confidence": int(c.group(1)) if c else None}


def score(a: argparse.Namespace) -> None:
    need_drive()
    truth = {t["key"]: t for t in map(json.loads, (OUT / "truth.jsonl").read_text(encoding="utf-8").splitlines())}
    recs = [json.loads(l) for l in (DISPATCH / a.run / "record.jsonl").read_text(encoding="utf-8").splitlines() if l]
    rows = []
    for r in recs:
        if not r["canary_ok"]:
            continue
        key = r["id"].split("s")[0]
        t = truth[key]
        p = parse(r["reply"])
        true_dir = "HIGHER" if t["accelerates"] else "LOWER"
        rows.append({**t, **p, "answered_dir": p["direction"] in ("HIGHER", "LOWER"),
                     "dir_right": p["direction"] == true_dir,
                     "err": abs(p["growth"] - 100 * t["g_next"]) if p["growth"] is not None else None,
                     "err_persist": abs(100 * t["g"] - 100 * t["g_next"])})
    out = {"replies": len(rows), "by_bin": {}, "by_bin_tier": {}}

    def summ(rs: list[dict]) -> dict:
        ans = [x for x in rs if x["answered_dir"]]
        num = [x for x in rs if x["err"] is not None]
        return {"n": len(rs), "answer_rate": round(len(ans) / len(rs), 3) if rs else None,
                "dir_acc_answered": round(sum(x["dir_right"] for x in ans) / len(ans), 3) if ans else None,
                "dir_acc_all": round(sum(x["dir_right"] for x in rs) / len(rs), 3) if rs else None,
                "growth_answer_rate": round(len(num) / len(rs), 3) if rs else None,
                "median_err": round(statistics.median(x["err"] for x in num), 2) if num else None,
                "beats_persistence": round(sum(x["err"] < x["err_persist"] for x in num) / len(num), 3) if num else None}

    for b, _, _ in BINS:
        out["by_bin"][b] = summ([x for x in rows if x["bin"] == b])
        for t in TIERS:
            out["by_bin_tier"][f"{b} | {t}"] = summ([x for x in rows if x["bin"] == b and x["tier"] == t])

    # Pre-registered criteria (registry, EXP-0024): direction accuracy over all prompts against the
    # after-cutoff bin; recall if at least 15 points higher with the 90% bootstrap interval above 0.
    rng = random.Random(SEED)

    def boot(xs: list[dict], ys: list[dict]) -> dict:
        a = [1.0 if x["dir_right"] else 0.0 for x in xs]
        b = [1.0 if y["dir_right"] else 0.0 for y in ys]
        diff = statistics.mean(a) - statistics.mean(b)
        draws = sorted(statistics.mean(rng.choices(a, k=len(a))) - statistics.mean(rng.choices(b, k=len(b)))
                       for _ in range(10_000))
        lo, hi = draws[499], draws[9499]
        return {"n": len(a), "n_ref": len(b), "acc": round(statistics.mean(a), 3), "acc_ref": round(statistics.mean(b), 3),
                "diff": round(diff, 3), "ci90": [round(lo, 3), round(hi, 3)], "recall": diff >= 0.15 and lo > 0}

    after = [x for x in rows if x["bin"] == "after cutoff"]
    crit = {"criterion_1": {b: boot([x for x in rows if x["bin"] == b], after) for b, _, _ in BINS[:-1]}}
    met = [b for b, _, _ in BINS[:-1] if crit["criterion_1"][b]["recall"]]
    crit["criterion_2_last_bin_with_recall"] = met[-1] if met else None
    large = ("top 50", "51 to 250")
    crit["criterion_3_large_2019_2024"] = boot(
        [x for x in rows if x["tier"] in large and x["bin"] in ("2019-2021", "2022-2023", "2024")],
        [x for x in after if x["tier"] in large])
    out["criteria"] = crit
    (OUT / f"score_{a.run}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"by_bin": out["by_bin"], "criteria": crit}, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(fn=prepare)
    s = sub.add_parser("score")
    s.add_argument("--run", required=True)
    s.set_defaults(fn=score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
