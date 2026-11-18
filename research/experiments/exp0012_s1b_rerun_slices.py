"""EXP-0012: slices of the EXP-0011 responses. Read-only; no model is run.

EXP-0011 (frozen) pre-registered accuracy by filer size as descriptive, but its score step, which
is EXP-0007's, does not compute it. This script adds it, and the exploratory error kinds of
EXP-0009 (dropped signs, units, forced against finished answers), graded with EXP-0010's grader,
to ``slices.json`` beside EXP-0011's ``scores.json``.

    conda run --no-capture-output -n py313 python research/experiments/exp0012_s1b_rerun_slices.py
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0011_s1b_headroom_v0_2 as R  # noqa: E402  (sets EXP-0007's globals to EXP-0011's)
from exp0009_s1b_slices import COMPANIES, kind_of_error, pct  # noqa: E402

S, V = R.S, R.V


def main() -> None:
    items = {it["id"]: it for it in S.load_draw()}
    band = {r["cik"]: r["size_band"] for r in map(json.loads, COMPANIES.read_text().splitlines())}
    bands = sorted({band.get(items[i]["cik"], "unknown") for i in items})
    out: dict = {"filer_size (pre-registered, descriptive)": {}, "exploratory": {}}
    for key, mode in S.QUEUE:
        rows = [json.loads(l) for l in S.responses_path(key, mode).read_text().splitlines()]
        g = {r["id"]: {**V.grade(items[r["id"]], r["response"], mode), "forced": r["forced"]} for r in rows}
        out["filer_size (pre-registered, descriptive)"][key] = {
            b: pct(g[i]["correct"] for i in g if band.get(items[i]["cik"], "unknown") == b) for b in bands}
        wrong = [i for i in g if not g[i]["correct"]]
        out["exploratory"][key] = {
            "wrong": len(wrong),
            "wrong_by_kind": dict(collections.Counter(kind_of_error(items[i], g[i]) for i in wrong).most_common()),
            "forced": {"n": sum(x["forced"] for x in g.values()), "acc": pct(x["correct"] for x in g.values() if x["forced"])},
            "finished": {"n": sum(not x["forced"] for x in g.values()), "acc": pct(x["correct"] for x in g.values() if not x["forced"])},
        }
    out["filer_size (pre-registered, descriptive)"]["items_per_band"] = dict(
        collections.Counter(band.get(items[i]["cik"], "unknown") for i in items))
    (S.OUT / "slices.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
