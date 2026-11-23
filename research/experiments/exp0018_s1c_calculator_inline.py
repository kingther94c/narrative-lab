"""EXP-0018: the 4B with the calculator's inline rule only (4I), a fair comparator for S1.

Pre-registered in research/registry/experiment_registry.md. Nothing is trained. EXP-0016's calculator
has two rules. The "chained" rule, added on development for the 4B's layout, evaluates the previous
line's arithmetic, often including its ``\\times 100``, at a point where the 4B expects the fraction;
the 4B then multiplies by 100 again (41 of the 44 B2 test items the calculator cost the 4B, counted by
program). The chained rule never fired for the 0.8B (0 of 3,000 test responses per seed). This
script reruns the 4B on EXP-0016's test draw with the inline rule alone; everything else is EXP-0016's
code, imported unchanged.

  check   parser cases: EXP-0016's inline cases as before, every chained case now finds nothing
  repro   the first 50 development items, against EXP-0016's inline-only development run (dev_v1)
  test    4I on EXP-0016's test draw
  seca    4I on section A
  queue   repro gate, test, section A, score
  score   HE1, HE2, the mechanisms, the re-analyses, to scores.json

Test items are read by the program only; nothing here prints their text.

    conda run --no-capture-output -n py313 python research/experiments/exp0018_s1c_calculator_inline.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0018_s1c_calculator_inline.py queue
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0016_s1c_calculator as C  # noqa: E402

E, S, V = C.E, C.S, C.V
OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0018"
X17 = S.DRIVE / "narrative_lab" / "s1" / "exp0017"
DEV_V1 = C.OUT / "dev_v1" / "4C.jsonl"  # EXP-0016's development run before the chained rule existed
BOOT, BOOT_SEED = 10_000, 20261123
REPRO_N, REPRO_MIN = 50, 48


def find_call_inline(text: str, start: int):
    """EXP-0016's find_call with the chained rule removed."""
    for m in C.TRIGGER.finditer(text, start):
        before = text[: m.start()]
        suf = C.ARITH_SUFFIX.search(before)
        if suf:
            stretch = suf.group(0)
            starts = [0] + [k for k in range(1, len(stretch)) if stretch[k - 1] in "\n$"]
            for k in starts:
                r = C.evaluate(stretch[k:])
                if r:
                    return m.end(), r[0], r[1], "inline"
    return None


C.find_call = find_call_inline  # gen_calc looks the name up in its module at call time


def answer(model, tok, item):
    return C.answer(model, tok, item, E.STANDARD, 512, True)


def run(items, path: Path) -> None:
    import mlx.core as mx

    done = {r["id"] for r in E.jl(path)} if path.exists() else set()
    todo = [i for i in items if i["id"] not in done]
    if not todo:
        return
    model, tok = E.load_model(E.TEACHER, None)
    for it in todo:
        row = answer(model, tok, it)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        E.append(path, row)


# ------------------------------------------------------------------ checks


def check(_: argparse.Namespace) -> None:
    bad = 0
    chained_start = next(k for k, (t, _) in enumerate(C.CASES) if "\\text{Change} = (-0.52)" in t)
    for k, (text, want) in enumerate(C.CASES):
        if k >= chained_start:
            want = None
        hit = find_call_inline(text, text.rfind("\n") + 1)
        got = None if hit is None else round(hit[2], 4)
        ok = (got is None and want is None) or (got is not None and want is not None and abs(got - want) < 1e-4)
        bad += not ok
        print("ok " if ok else "BAD", repr(text[-60:]), "->", None if hit is None else (hit[1], C.fmt(hit[2])))
    print(f"{len(C.CASES) - bad} of {len(C.CASES)} cases pass")
    if bad:
        sys.exit(1)


def repro(_: argparse.Namespace) -> None:
    S.need_drive()
    items = E.load_ids(C.DEV_DRAW, V.OUT / "items_dev.jsonl")[:REPRO_N]
    path = OUT / "repro" / "4I.jsonl"
    run(items, path)
    old = {r["id"]: r for r in E.jl(DEV_V1)}
    same = sum(r["response"] == old[r["id"]]["response"] for r in E.jl(path))
    res = {"items": REPRO_N, "identical": same, "gate": REPRO_MIN, "pass": same >= REPRO_MIN}
    (OUT / "repro.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res))
    if not res["pass"]:
        sys.exit("repro gate failed: the owner decides before any test item is run")


def test(_: argparse.Namespace) -> None:
    S.need_drive()
    run(E.load_ids(C.TEST_DRAW, E.TEST_ITEMS), OUT / "test" / "4I.jsonl")


def seca(_: argparse.Namespace) -> None:
    import mlx.core as mx
    from learnai.finbench import load_problems

    S.need_drive()
    path = OUT / "seca" / "4I.jsonl"
    done = {r["uid"] for r in E.jl(path)} if path.exists() else set()
    probs = [p for p in load_problems(E.SECA_N, seed=E.BOOT_SEED) if p.uid not in done]
    if not probs:
        return
    model, tok = E.load_model(E.TEACHER, None)
    for p in probs:
        prompt = tok.apply_chat_template([{"role": "user", "content": p.prompt}], add_generation_prompt=True,
                                         tokenize=False, enable_thinking=False)
        t0 = time.time()
        g = C.gen_calc(model, tok, prompt, 512, True)
        E.append(path, {"uid": p.uid, "generated_tokens": g["generated_tokens"], "finish": g["finish"],
                        "calls": g["calls"], "response": g["text"], "seconds": round(time.time() - t0, 2),
                        "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]
    for step in ("repro", "test", "seca", "score"):
        print(time.strftime("%m-%d %H:%M:%S"), step, flush=True)
        if subprocess.run(me + [step]).returncode != 0:
            sys.exit(f"step failed: {step}")


# ------------------------------------------------------------------ score

NUM = r"\(?-?\d+(?:\.\d+)?\)?"


def mechanisms(row: dict) -> set[str]:
    """The registered detectors of how a calculator answer goes wrong (EXP-0018, criterion 3)."""
    calls, resp, out = row.get("calls") or [], row["response"], set()
    for a in calls:
        if re.search(r"\*\s*100\s*\)?\s*$", a["expr"]) and a["value"]:
            for m in re.finditer(r"(-?\d[\d,]*(?:\.\d+)?)\s*(?:\.\.\.)?\s*(?:\\times|×|\*|\\cdot)\s*100\b", resp[a["at"]:]):
                if abs(float(m.group(1).replace(",", "")) - a["value"]) <= 0.01 * abs(a["value"]):
                    out.add("x100 twice")
    for c in calls:
        if re.fullmatch(r"\s*\d+000\s*/\s*1000\s*", c["expr"]) or re.fullmatch(r"\s*\d+(\.\d+)?\s*\*\s*1000\s*", c["expr"]):
            out.add("literal unit conversion")
    if re.search(r"[Rr]ound(ing|ed|s)? to (two|one) decimal places? \((standard|typical)|standard for financial reporting", resp):
        out.add("extra rounding")
    if row.get("forced"):
        out.add("cap hit, answer forced")
    return out or {"none of these"}


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from learnai.finbench import grade as fgrade, problem_for

    items = E.load_ids(C.TEST_DRAW, E.TEST_ITEMS)
    ids = [i["id"] for i in items]
    by = {i["id"]: i for i in items}
    section = np.array([by[i]["section"] for i in ids])
    metric = np.array([by[i]["metric"] for i in ids])
    cos = sorted({by[i]["cik"] for i in ids})
    co_idx = {c: np.array([k for k, i in enumerate(ids) if by[i]["cik"] == c]) for c in cos}
    rng = np.random.default_rng(BOOT_SEED)
    boot = [np.concatenate([co_idx[cos[j]] for j in rng.integers(0, len(cos), len(cos))]) for _ in range(BOOT)]
    allm, b1, b2 = np.ones(len(ids), bool), section == "B1", section == "B2"

    sources = {n: C.OUT / "test" / f"{n}.jsonl" for n in ("4B", "4C", "C-s1", "C-s2")}
    sources["4I"] = OUT / "test" / "4I.jsonl"
    for n in ("K2-s1", "K2-s2"):
        if (X17 / "test" / f"{n}.jsonl").exists():
            sources[n] = X17 / "test" / f"{n}.jsonl"
    rows, grades, vec = {}, {}, {}
    for n, p in sources.items():
        rows[n] = {r["id"]: r for r in E.jl(p)}
        grades[n] = {i: V.grade(by[i], rows[n][i]["response"], "off") for i in ids}
        vec[n] = np.array([float(grades[n][i]["correct"]) for i in ids])
    vec["C"] = (vec["C-s1"] + vec["C-s2"]) / 2
    if "K2-s1" in vec and "K2-s2" in vec:
        vec["K2"] = (vec["K2-s1"] + vec["K2-s2"]) / 2

    def stats(d, m=allm):
        bs = np.array([d[b][m[b]].mean() for b in boot])
        return {"value": round(100 * float(d[m].mean()), 2),
                "ci97_5": [round(100 * float(np.percentile(bs, 1.25)), 2), round(100 * float(np.percentile(bs, 98.75)), 2)],
                "p_le_0": round(float(np.mean(bs <= 0)), 5)}

    out: dict = {"repro": json.loads((OUT / "repro.json").read_text()), "accuracy": {}}
    for n, v in vec.items():
        acc = {"all": allm, "B1": b1, "B2": b2}
        acc.update({f"{s}:{m}": (section == s) & (metric == m) for s in ("B1", "B2") for m in sorted(set(metric[section == s]))})
        out["accuracy"][n] = {k: round(100 * float(v[m].mean()), 1) for k, m in acc.items() if m.any()}

    he1 = stats(vec["4I"] - vec["4C"], b2)
    he1["supported"] = he1["p_le_0"] < 0.0125
    he1["refuted"] = he1["ci97_5"][1] <= 0
    he2 = stats(vec["4I"] - vec["4B"], b2)
    he2["non_inferior"] = he2["ci97_5"][0] > -1.5
    he2["refuted"] = he2["ci97_5"][1] < -1.5
    out["HE1"], out["HE2"] = he1, he2
    out["also"] = {"4I-4B all": stats(vec["4I"] - vec["4B"]), "4I-4B B1": stats(vec["4I"] - vec["4B"], b1),
                   "4I-4C all": stats(vec["4I"] - vec["4C"]), "4I-4C B1": stats(vec["4I"] - vec["4C"], b1)}
    out["reanalysis"] = {"EXP-0016 HC2 with 4I: C-4I all": stats(vec["C"] - vec["4I"]),
                         "C-4I B2": stats(vec["C"] - vec["4I"], b2)}
    if "K2" in vec:
        out["reanalysis"]["EXP-0017 HD3 with 4I: K2-4I all"] = stats(vec["K2"] - vec["4I"])
        out["reanalysis"]["K2-4I B2"] = stats(vec["K2"] - vec["4I"], b2)

    mech = {}
    for calc in ("4C", "4I"):
        t = collections.Counter()
        for i in ids:
            bf, bc = grades["4B"][i]["correct"], grades[calc][i]["correct"]
            kind = "hurt" if bf and not bc else "helped" if bc and not bf else None
            t[(by[i]["section"], "items", kind or "same")] += 1
            if kind:
                for k in mechanisms(rows[calc][i]):
                    t[(by[i]["section"], k, kind)] += 1
        mech[calc] = {f"{s} | {k} | {h}": v for (s, k, h), v in sorted(t.items())}
    out["mechanisms_against_4B"] = mech
    rs = rows["4I"]
    out["calls_4I"] = {s: {"with_call": round(100 * float(np.mean([bool(rs[i]["calls"]) for i in ids if by[i]["section"] == s])), 1),
                           "calls_mean": round(float(np.mean([len(rs[i]["calls"]) for i in ids if by[i]["section"] == s])), 2)}
                       for s in ("B1", "B2")}
    out["forced_invalid"] = {n: {"forced": round(100 * float(np.mean([rows[n][i]["forced"] for i in ids])), 1),
                                 "invalid": round(100 * float(np.mean([not grades[n][i]["valid"] for i in ids])), 1)}
                             for n in ("4B", "4C", "4I")}
    wrong = [i for i in ids if not grades["4I"][i]["correct"]]
    out["errors_4I"] = {s: dict(collections.Counter(C.error_kind(by[i], grades["4I"][i], rs[i])
                                                    for i in wrong if by[i]["section"] == s).most_common())
                        for s in ("B1", "B2")}
    p = OUT / "seca" / "4I.jsonl"
    if p.exists():
        c: dict = collections.defaultdict(list)
        for r in E.jl(p):
            prob = problem_for(r["uid"])
            c[prob.source].append(fgrade(prob, r["response"], thinking=False)["correct"])
        out["section_A_4I"] = {s: round(100 * sum(v) / len(v), 1) for s, v in c.items()}
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(required=True)
    for name, fn in (("check", check), ("repro", repro), ("test", test), ("seca", seca), ("queue", queue), ("score", score)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
