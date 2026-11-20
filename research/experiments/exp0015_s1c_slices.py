"""EXP-0015: slices of the EXP-0014 responses. Read-only; no model is run.

EXP-0014 (frozen) scored its runs to ``scores.json``. Its pre-registration also lists, as
descriptive, accuracy by template and filer size, invalid rates, training loss curves and label
yields per attempt, which its score step does not compute. This script adds them, and one
exploratory slice the results raised: on B2, the trained arms write a one-line calculation, and
the question is whether their wrong answers set up the right calculation and get the arithmetic
wrong. Writes ``slices.json`` beside ``scores.json``. Only counts and rates are printed; no test
item or test response is shown.

    conda run --no-capture-output -n py313 python research/experiments/exp0015_s1c_slices.py
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as E  # noqa: E402
from exp0009_s1b_slices import COMPANIES, kind_of_error, pct  # noqa: E402

V = E.V
CONFIGS = ["D0-0.8b", "D0-4b"] + [f"{a}-s{s}" for a in E.ARMS for s in E.SEEDS]
# the last "<expression> = <number>" written before the boxed answer
CALC = re.compile(r"([-\d.,()\s+*/×÷]+?)\s*=\s*(-?[\d.,]+)\s*%?[^=]*\\boxed", re.S)


def written_calculation(response: str) -> float | None:
    """Evaluate the student's own one-line expression, or None if there is none to evaluate."""
    m = None
    for m in CALC.finditer(response):
        pass
    if m is None:
        return None
    expr = m.group(1).replace(",", "").replace("×", "*").replace("÷", "/").strip()
    if not re.search(r"\d\s*[-+*/]\s*[\d(]", expr) or not re.fullmatch(r"[-\d.()\s+*/]+", expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))  # digits, brackets and + - * / only
    except Exception:
        return None


def setup_vs_arithmetic(item: dict, g: dict, response: str) -> str:
    """For a wrong B2 answer: did the written expression evaluate to the gold (by magnitude)?"""
    v = written_calculation(response)
    if v is None:
        return "no evaluable calculation"
    gold, tol = abs(float(item["gold"])), item["tolerance"]["abs"]
    if abs(abs(v) - gold) <= tol or abs(abs(100 * v) - gold) <= tol:
        return "right setup, wrong arithmetic"
    return "wrong setup"


def main() -> None:
    items = {i["id"]: i for i in E.load_ids(E.TEST_DRAW, E.TEST_ITEMS)}
    band = {r["cik"]: r["size_band"] for r in map(json.loads, COMPANIES.read_text().splitlines())}
    out: dict = {"pre-registered (descriptive)": {"by_template": {}, "by_filer_size": {}, "invalid_rate": {},
                                                    "training_loss": {}, "label_yield": {}},
                 "exploratory": {"wrong_by_kind": {}, "B2_wrong_setup_vs_arithmetic": {}, "B2_by_template_compact": {}}}
    pre, exp = out["pre-registered (descriptive)"], out["exploratory"]
    for c in CONFIGS:
        rows = E.jl(E.OUT / "test" / f"{c}.jsonl")
        assert len(rows) == len(items), (c, len(rows))
        g = {r["id"]: V.grade(items[r["id"]], r["response"], "off") for r in rows}
        resp = {r["id"]: r["response"] for r in rows}
        pre["by_template"][c] = {t: pct(g[i]["correct"] for i in g if items[i]["template"] == t)
                                 for t in sorted({it["template"] for it in items.values()})}
        pre["by_filer_size"][c] = {b: pct(g[i]["correct"] for i in g if band.get(items[i]["cik"], "unknown") == b)
                                   for b in sorted({band.get(it["cik"], "unknown") for it in items.values()})}
        pre["invalid_rate"][c] = pct(not x["valid"] for x in g.values())
        wrong = [i for i in g if not g[i]["correct"]]
        exp["wrong_by_kind"][c] = dict(collections.Counter(kind_of_error(items[i], g[i]) for i in wrong).most_common())
        b2_wrong = [i for i in wrong if items[i]["section"] == "B2"]
        exp["B2_wrong_setup_vs_arithmetic"][c] = {"wrong": len(b2_wrong), **dict(collections.Counter(
            setup_vs_arithmetic(items[i], g[i], resp[i]) for i in b2_wrong).most_common())}
        exp["B2_by_template_compact"][c] = {m: pct(g[i]["correct"] for i in g if items[i]["template"].split(":")[1] == m
                                                    and items[i]["section"] == "B2")
                                             for m in ("eps_change", "revenue_growth", "operating_margin",
                                                       "gross_margin", "net_margin")}
    pre["by_filer_size"]["items_per_band"] = dict(collections.Counter(band.get(it["cik"], "unknown")
                                                                      for it in items.values()))
    for arm in E.ARMS:
        for s in E.SEEDS:
            log = json.loads((E.OUT / "checkpoints" / f"{arm}-s{s}" / "train_log.json").read_text())
            losses = [x for x in log["log"] if "train_loss" in x]
            pts = losses[:: max(1, len(losses) // 8)] + losses[-1:]
            pre["training_loss"][f"{arm}-s{s}"] = {"iters": log["iters"], "hours": round(log["wall_s"] / 3600, 2),
                                                   "peak_gib": log["peak_gib"],
                                                   "loss": {x["iteration"]: round(x["train_loss"], 3) for x in pts}}
    for who in ("teacher", "student"):
        key = E.TEACHER if who == "teacher" else E.STUDENT
        rows = E.jl(E.OUT / "labels" / f"{key}.jsonl")
        pre["label_yield"][key] = {"items": len(rows), "correct_on_attempt": dict(sorted(collections.Counter(
            next((str(k + 1) for k, t in enumerate(r["attempts"]) if t["correct"]), "none")
            for r in rows).items()))}
    (E.OUT / "slices.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
