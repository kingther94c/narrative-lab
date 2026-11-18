"""EXP-0009: slices of the EXP-0007 responses. Read-only; no model is run.

EXP-0007 (frozen) scored its runs to ``scores.json``. Its score step left out one slice the
pre-registration lists as descriptive (accuracy by filer size), and the run raised questions the
pre-registration did not ask: how much of the error is a dropped minus sign or a wrong unit, how
forced answers score against answers the model finished itself, and how thinking on compares with
thinking off on the same 300 items. This script answers those from the saved raw responses, with
EXP-0007's own grader, and writes ``slices.json`` beside ``scores.json``.

Everything here except the filer-size slice is exploratory and labelled so.

    conda run --no-capture-output -n py313 python research/experiments/exp0009_s1b_slices.py
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0007_s1b_headroom as S  # noqa: E402

COMPANIES = S.DRIVE / "narrative_lab" / "splits" / "split_v1_exp0003_companies.jsonl"


def kind_of_error(item: dict, g: dict) -> str:
    """Why a wrong answer is wrong, checked in this order."""
    if not g["valid"]:
        return "no number"
    gold, v, tol = float(item["gold"]), g["value"], item["tolerance"]["abs"]
    if gold < 0 and abs(v + gold) <= tol:
        return "minus sign dropped"
    if gold != 0 and v != 0:
        r = math.log10(abs(v / gold))
        k = round(r)
        if k != 0 and abs(r - k) < 0.005:
            if k % 3 == 0:
                return "unit off by 10^3k"
            if abs(k) == 2:
                return "percent off by 100"
    return "other"


def pct(xs) -> float | None:
    xs = list(xs)
    return round(100 * sum(xs) / len(xs), 1) if xs else None


def main() -> None:
    S.need_drive()
    items = {it["id"]: it for it in S.load_draw()}
    order = list(items)
    subset = set(order[: S.THINKING_SUBSET])
    band = {r["cik"]: r["size_band"] for r in map(json.loads, COMPANIES.read_text().splitlines())}

    graded: dict = {}
    for key, mode in S.QUEUE:
        rows = {r["id"]: r for r in map(json.loads, S.responses_path(key, mode).read_text().splitlines())}
        graded[(key, mode)] = {
            i: {**S.grade(items[i], r["response"], mode), "forced": r["forced"],
                "never_closed": mode == "on" and ("\n</think>" + S.CUE) in r["response"]}
            for i, r in rows.items()
        }

    out: dict = {"filer_size_off (pre-registered, descriptive)": {}, "exploratory": {}}
    bands = sorted({band.get(items[i]["cik"], "unknown") for i in order})
    out["filer_size_off (pre-registered, descriptive)"]["items_per_band"] = dict(
        collections.Counter(band.get(items[i]["cik"], "unknown") for i in order))
    ex = out["exploratory"]
    for (key, mode), g in graded.items():
        name = f"{key}/{mode}"
        if mode == "off":
            out["filer_size_off (pre-registered, descriptive)"][key] = {
                b: pct(g[i]["correct"] for i in g if band.get(items[i]["cik"], "unknown") == b) for b in bands}
        wrong = [i for i in g if not g[i]["correct"]]
        kinds = collections.Counter(kind_of_error(items[i], g[i]) for i in wrong)
        neg = [i for i in g if float(items[i]["gold"]) < 0]
        conv = [i for i in g if items[i]["section"] == "B1" and items[i]["scale_conversion"]]
        e = {
            "wrong": len(wrong),
            "wrong_by_kind": dict(kinds.most_common()),
            "negative_gold": {"n": len(neg), "acc": pct(g[i]["correct"] for i in neg),
                              "minus_sign_dropped": pct(kind_of_error(items[i], g[i]) == "minus sign dropped" for i in neg)},
            "b1_scale_conversion": {"n": len(conv), "acc": pct(g[i]["correct"] for i in conv),
                                    "unit_off": pct(not g[i]["correct"] and kind_of_error(items[i], g[i]) == "unit off by 10^3k" for i in conv)},
            "forced": {"n": sum(g[i]["forced"] for i in g), "acc": pct(g[i]["correct"] for i in g if g[i]["forced"])},
            "finished": {"n": sum(not g[i]["forced"] for i in g), "acc": pct(g[i]["correct"] for i in g if not g[i]["forced"])},
        }
        if mode == "on":
            e["thinking_never_closed"] = pct(g[i]["never_closed"] for i in g)
        else:
            e["on_thinking_subset_acc"] = pct(g[i]["correct"] for i in g if i in subset)
        ex[name] = e
    for key in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b"):
        off, on = graded[(key, "off")], graded[(key, "on")]
        both = [i for i in order if i in subset]
        ex[f"{key} on minus off, same 300 items"] = {
            sec: round((pct(on[i]["correct"] for i in both if items[i]["section"] == sec) or 0)
                       - (pct(off[i]["correct"] for i in both if items[i]["section"] == sec) or 0), 1)
            for sec in ("B1", "B2")}

    # Sensitivity of the gates to the sign rule (exploratory). "registered" is EXP-0007's scoring.
    # "parentheses negative" also reads an accounting negative, (1,234) or -(5.6), as negative;
    # learnai.finbench.parse_number reads both as positive. "sign blind" counts |value| = |gold|
    # as right, an upper bound on what any sign instruction could recover.
    import numpy as np

    paren = re.compile(r"^\s*-?\s*\\?\$?\s*\(")
    cos = sorted({items[i]["cik"] for i in order})
    co_idx = {c: [k for k, i in enumerate(order) if items[i]["cik"] == c] for c in cos}
    rng = np.random.default_rng(S.BOOT_SEED)
    boot = [rng.integers(0, len(cos), len(cos)) for _ in range(S.BOOT)]
    section = np.array([items[i]["section"] for i in order])

    def right(key: str, rule: str) -> np.ndarray:
        g = graded[(key, "off")]
        v = []
        for i in order:
            it, x = items[i], g[i]
            gold, tol = float(it["gold"]), it["tolerance"]["abs"]
            if rule == "registered" or not x["valid"]:
                v.append(x["correct"])
            elif rule == "parentheses negative":
                val = -abs(x["value"]) if x["boxed"] and paren.search(x["boxed"]) else x["value"]
                v.append(abs(val - gold) <= tol)
            else:
                v.append(abs(abs(x["value"]) - abs(gold)) <= tol)
        return np.array(v, dtype=float)

    sens: dict = {}
    for rule in ("registered", "parentheses negative", "sign blind"):
        acc = {k: right(k, rule) for k in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b", "olmoe-1b-7b")}
        r = {"accuracy_off": {k: {s: round(100 * float(a[section == s].mean()), 1) for s in ("B1", "B2")}
                              for k, a in acc.items()}, "gates_off": {}}
        for t, s_ in S.PAIRS_GATE:
            d = acc[t] - acc[s_]
            gate = {}
            for sec in ("B1", "B2"):
                m = section == sec
                stats = []
                for b in boot:
                    idx = np.concatenate([co_idx[cos[j]] for j in b])
                    idx = idx[m[idx]]
                    stats.append(d[idx].mean())
                lo, hi = np.percentile(stats, [2.5, 97.5])
                gate[sec] = {"gap": round(100 * float(d[m].mean()), 1), "ci95": [round(100 * lo, 1), round(100 * hi, 1)]}
            gate["passes"] = any(v["gap"] >= 5.0 and v["ci95"][0] > 0 for v in gate.values())
            r["gates_off"][f"{t} -> {s_}"] = gate
        sens[rule] = r
    ex["sign_rule_sensitivity"] = sens
    ex["boxed_in_parentheses_off"] = {k: sum(bool(graded[(k, "off")][i]["boxed"] and paren.search(graded[(k, "off")][i]["boxed"]))
                                             for i in order) for k in acc}

    path = S.OUT / "slices.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
