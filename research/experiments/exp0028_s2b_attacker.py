"""EXP-0028: does the model recognise the company behind a fully blinded release? (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0028 (2026-11-21). The fully
blinded views of EXP-0026's 90 episodes are shown to the recall definition, which is asked to
name the company and the quarter.

    conda run --no-capture-output -n nlab python research/experiments/exp0028_s2b_attacker.py prepare
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run exp0028 --items <items>
    conda run --no-capture-output -n nlab python research/experiments/exp0027_s2a_cli_dispatch_v2.py run --run exp0028
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run exp0028
    conda run --no-capture-output -n nlab python research/experiments/exp0028_s2b_attacker.py score
"""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0028"
RUN = "exp0028"
SEED = 20261123
AGENT = "s2-recall-claude-opus-5-5"
MARK = "RATIONALE: <at most three sentences>\n\n"

PROMPT = """Below are ratios from earlier filings and an earnings release for one quarter of one real public company. Names, dates and figures may have been replaced or rescaled. From what you know, identify the real company and the real quarter.

Reply in exactly this format:
COMPANY_1: <your best guess: company name and ticker>
COMPANY_2: <second guess, or NONE>
COMPANY_3: <third guess, or NONE>
QUARTER_END: <year and month of the quarter end, as YYYY-MM, or UNKNOWN>
CONFIDENCE: <a whole number from 0 to 100 that COMPANY_1 is right>
CLUES: <at most two sentences on what gave it away>

"""


def prepare(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(OUT / "items.jsonl", "w", encoding="utf-8") as fh:
        for k in e26.load(e26.OUT / "key.jsonl"):
            i = k["episode"]
            c = json.loads((e23.ROOT / e26.RUN / "outbox" / f"v{i:03d}-7.json").read_text(encoding="utf-8"))
            doc = c["prompt"].split(MARK, 1)[1].rsplit(e23.CANARY.format(code=c["canary"]), 1)[0]
            fh.write(json.dumps({"id": f"a{i:03d}", "agent": AGENT, "prompt": PROMPT + doc}, ensure_ascii=False) + "\n")
            n += 1
    print(f"[prepare] {n} items -> {OUT / 'items.jsonl'}")


def hit(line: str, k: dict) -> bool:
    names = [x for x in k["names_hidden"] if len(x) >= 4 and x != k["ticker"]]
    return bool(e22.find_terms(line, names)) or bool(re.search(rf"(?<![A-Za-z]){re.escape(k['ticker'])}(?![A-Za-z])", line))


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    p26 = {}
    for r in e23.records(e23.ROOT / e26.RUN):
        m = e26.PROB.search(r["reply"])
        if r["canary_ok"] and m:
            p26[r["id"]] = int(m.group(1)) / 100
    rows = []
    for r in e23.records(e23.ROOT / RUN):
        if not r["canary_ok"]:
            continue
        i = int(r["id"][1:4])
        k = key[i]
        g = {m.group(1): m.group(2) for m in re.finditer(r"COMPANY_([123]):\s*(.*)", r["reply"])}
        q = re.search(r"QUARTER_END:\s*(\d{4})-(\d{2})", r["reply"])
        c = re.search(r"CONFIDENCE:\s*(\d{1,3})", r["reply"])
        x = p26.get(f"v{i:03d}-7")
        rows.append({"episode": i, "group": k["group"], "tier": k["tier"],
                     "top1": hit(g.get("1", ""), k), "top3": any(hit(g.get(j, ""), k) for j in "123"),
                     "year_pm1": bool(q) and abs(int(q.group(1)) - int(k["quarter_end"][:4])) <= 1,
                     "quarter": bool(q) and f"{q.group(1)}-{q.group(2)}" == k["quarter_end"][:7],
                     "confidence": int(c.group(1)) if c else None,
                     "readout7": None if x is None else (x if k["accelerates"] else 1 - x)})
    rng = random.Random(SEED)

    def rate(xs: list[bool]) -> dict:
        v = [1.0 if x else 0.0 for x in xs]
        d = sorted(statistics.mean(rng.choices(v, k=len(v))) for _ in range(10_000))
        return {"rate": round(statistics.mean(v), 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(v)}

    out: dict = {"records": len(rows)}
    for g in ("old", "clean"):
        rs = [r for r in rows if r["group"] == g]
        out[g] = {f: rate([r[f] for r in rs]) for f in ("top1", "top3", "year_pm1", "quarter")}
        out[g]["by_tier_top1"] = {t: rate([r["top1"] for r in rs if r["tier"] == t]) for t in ("top 50", "51 to 250")}
        out[g]["median_confidence"] = statistics.median(r["confidence"] for r in rs if r["confidence"] is not None)
    t1 = out["old"]["top1"]["rate"]
    out["criterion_1"] = "reading 1 (recognised)" if t1 >= 0.5 else "reading 2 (not recognised)" if t1 <= 0.2 else "undecided"
    yes = [r["readout7"] for r in rows if r["group"] == "old" and r["top1"] and r["readout7"] is not None]
    no = [r["readout7"] for r in rows if r["group"] == "old" and not r["top1"] and r["readout7"] is not None]
    if len(yes) >= 10 and len(no) >= 10:
        d = sorted(statistics.mean(rng.choices(yes, k=len(yes))) - statistics.mean(rng.choices(no, k=len(no))) for _ in range(10_000))
        out["criterion_3_readout_recognised_minus_not"] = {"est": round(statistics.mean(yes) - statistics.mean(no), 3),
                                                           "ci90": [round(d[499], 3), round(d[9499], 3)], "n": [len(yes), len(no)]}
    else:
        out["criterion_3_readout_recognised_minus_not"] = {"not_reported": [len(yes), len(no)]}
    (OUT / "score.json").write_text(json.dumps({**out, "rows": rows}, indent=2), encoding="utf-8")
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
