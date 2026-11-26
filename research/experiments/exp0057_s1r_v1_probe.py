"""EXP-0057: validity probe of section R v1's escape clause on development items (S1 re-plan).

EXP-0053 rewords the escape clause on every R template, from "does not give enough information" to
"can neither be read from the excerpt nor worked out from its figures", because EXP-0050 found R1.7
at every arm's floor (golds right; the 4B answered "cannot be determined" on 41 of 50 items, reading
the clause as "not stated"). Before the test side is built, the new wording is run on the v1
counterparts of EXP-0050's 50 R1.7 and 50 R1.9 development items (same release, template and
variant; only the clause differs), with EXP-0050's prompt, cap, grader and arms. Descriptive, no
hypothesis; development companies only.

Rule, fixed here: the wording is kept if the better of 4B and 4I reaches at least 50 on R1.7 (from
10 in EXP-0050) and neither falls by more than 10 points on R1.9 against its EXP-0050 score on the
same items. Otherwise the wording is revisited, by a new builder, before any test item is built.

    conda run --no-capture-output -n py313 python research/experiments/exp0057_s1r_v1_probe.py match
    conda run --no-capture-output -n py313 python research/experiments/exp0057_s1r_v1_probe.py queue
    conda run --no-capture-output -n py313 python research/experiments/exp0057_s1r_v1_probe.py score
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0050_s1r_headroom as R  # noqa: E402  (frozen; arms, prompt, grader, EXP-0050's runs)
import exp0053_s1r_build_v1 as V1  # noqa: E402  (frozen; v1 output folder)

C, E, S = R.C, R.E, R.S
OUT = R.NL / "exp0057"
ITEMS_V1 = V1.V0.OUT / "items_dev.jsonl"
TEMPLATES = ["R1.7", "R1.9"]
ARMS = ["4B", "4I", "B0"]
R17_MIN, R19_DROP = 50.0, 10.0


def key(it: dict) -> tuple:
    return it["accession"], it["template"], it["variant"]


def match(_=None) -> list[dict]:
    """The v1 counterparts of EXP-0050's drawn R1.7 and R1.9 base items, in EXP-0050's order."""
    v0 = R.items_by_id()
    drawn = [v0[r["id"]] for r in R.jl(R.DRAW) if r["template"] in TEMPLATES]
    v1 = {key(i): i for i in map(json.loads, open(ITEMS_V1, encoding="utf-8")) if not i.get("twin_of")}
    pairs = [(i, v1.get(key(i))) for i in drawn]
    missing = [i["id"] for i, j in pairs if j is None]
    both = [(i, j) for i, j in pairs if j is not None]
    rep = {"drawn in EXP-0050": len(drawn), "matched in v1": len(both), "missing": missing,
           "excerpt unchanged": sum(i["excerpt"] == j["excerpt"] for i, j in both),
           "gold unchanged": sum(i["gold"] == j["gold"] for i, j in both),
           # R1.7 draws millions or thousands at random for tables in thousands; the draw order moved with R1.8's drops
           "asked scale changed": sum(i.get("asked_scale") != j.get("asked_scale") for i, j in both),
           "clause v0 in every v0 question": all(V1.TAIL_V0 in i["question"] for i, _ in pairs),
           "clause v1 in every v1 question": all(V1.TAIL in j["question"] for _, j in pairs if j)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "match.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    if _ is not None:
        print(json.dumps(rep, indent=1))
    return [{"v0": i, "v1": j} for i, j in pairs if j is not None]


def run(a):
    import mlx.core as mx

    S.need_drive()
    key_, w, ins, calc = R.arm(a.arm)
    path = OUT / "runs" / f"{a.arm}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in R.jl(path)}
    todo = [p["v1"] for p in match() if p["v1"]["id"] not in done]
    if not todo:
        return
    model, tok = E.load_model(key_, w)
    for it in todo:
        row = C.answer(model, tok, it, ins, R.CAP, calc)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        E.append(path, row)


def queue(_):
    for arm in ARMS:
        subprocess.run([sys.executable, __file__, "run", "--arm", arm], check=True)
    score(None)


def score(_):
    pairs = match()
    res, cbd = {}, {}
    for arm in ARMS:
        new = {r["id"]: r for r in R.jl(OUT / "runs" / f"{arm}.jsonl")}
        old = {r["id"]: r for r in R.jl(R.OUT / "runs" / arm / "plain.jsonl")}
        res[arm], cbd[arm] = {}, {}
        for t in TEMPLATES:
            ps = [p for p in pairs if p["v0"]["template"] == t and p["v1"]["id"] in new and p["v0"]["id"] in old]
            g1 = [R.grade_r(p["v1"], new[p["v1"]["id"]]["response"]) for p in ps]
            g0 = [R.grade_r(p["v0"], old[p["v0"]["id"]]["response"]) for p in ps]
            res[arm][t] = {"n": len(ps), "v0": round(100 * sum(g["correct"] for g in g0) / max(1, len(ps)), 1),
                           "v1": round(100 * sum(g["correct"] for g in g1) / max(1, len(ps)), 1)}
            cbd[arm][t] = {"v0": sum(g["answer"] == R.CBD for g in g0), "v1": sum(g["answer"] == R.CBD for g in g1)}
    best17 = max(res[a]["R1.7"]["v1"] for a in ("4B", "4I"))
    drop19 = max(res[a]["R1.9"]["v0"] - res[a]["R1.9"]["v1"] for a in ("4B", "4I"))
    out = {"scores": res, "answered cannot be determined": cbd,
           "rule": {"best of 4B and 4I on R1.7 (v1)": best17, "largest R1.9 fall, 4B or 4I": round(drop19, 1),
                    "keep the wording": best17 >= R17_MIN and drop19 <= R19_DROP}}
    (OUT / "scores.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    sub.add_parser("match").set_defaults(fn=match)
    r = sub.add_parser("run"); r.add_argument("--arm", required=True, choices=ARMS); r.set_defaults(fn=run)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
