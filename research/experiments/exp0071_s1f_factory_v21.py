"""EXP-0071: data factory v2.1, three fixes forward of EXP-0070 after its pilots (S1 main experiment).

EXP-0070's pilots (2026-11-26, 200 items, 4 samples each; 818 math problems) found:

1. **A false arithmetic failure.** A result written as the start of a further expression,
   "(7,676 - 6,659) / 6,659 = 1,017 / 6,659 ≈ 15.27%", was read as the result 1,017. 15 of the 148
   samples failing the arithmetic check failed only this way; the other 133 hold a real slip
   (15.4% written for 15.27%). Now a written number followed by an operator and another number is
   not checked as a result; the expression it starts is checked on its own, and "≈" now marks a
   result as "=" and "\\approx" do (EXP-0016 read only those two), so "1,017 / 6,659 ≈ 15.27%" is
   checked.
2. **Derived periods.** One of 11 derived items got a kept chain (43 of 44 samples wrong). EXP-0050
   showed why: the 4B scores 10 on R1.7 plainly and 82 with the hint "The N-month total minus the
   latest three months gives the earlier period." The teacher now gets that method for derived
   items, after BRIEF; the student never sees it (as it never sees BRIEF). The chain is still
   written forward from the excerpt and checked by EXP-0056's rules.
3. **Math.** The released 0.8B under "Solve this step by step" hit the 320-token cap on 709 of 814
   problems (GSM8K 212 of 300; MATH 497 of 514); 80 were right. Now GSM8K only (MATH's answers
   are mostly not plain numbers and its solutions long), the instruction MATH_BRIEF, and the cap is
   the full room left by the prompt in 640 tokens (at most 600).

Everything else is EXP-0070's (pool, BRIEF, sampling, other kinds, B answers, the 640-token fit).
Outputs go to ``s1/exp0071/``; the pool stays EXP-0070's.

    conda run --no-capture-output -n py313 python research/experiments/exp0071_s1f_factory_v21.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0071_s1f_factory_v21.py chains --items 200 --k 4 --batch 16 --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0071_s1f_factory_v21.py verify --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0071_s1f_factory_v21.py math --n 300 --batch 16 --dir pilot
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0070_s1f_factory_v2 as F  # noqa: E402  (frozen; pool, generation, verification, B answers)

X56, D14, E = F.X56, F.D14, F.E
OUT = E.DRIVE / "s1" / "exp0071"
MATH_BRIEF = "Solve this briefly, in a few short lines, then give the final number in \\boxed{}."
MATH_CAP = 600
GSM8K = [f for f in F.MATH_FILES if "gsm8k" in f.name]
CHAINED = re.compile(r"\s*[-+*/×÷]\s*\$?\s*\(?\s*\d")
TRIGGER = re.compile(r"=|\\approx|≈")  # EXP-0016's "=" and "\approx", plus "≈"


def find_call(text: str, start: int):
    """EXP-0018's inline finder with "≈" also read as the start of a result."""
    C = X56.C16
    for m in TRIGGER.finditer(text, start):
        suf = C.ARITH_SUFFIX.search(text[: m.start()])
        if suf:
            stretch = suf.group(0)
            for k in [0] + [k for k in range(1, len(stretch)) if stretch[k - 1] in "\n$"]:
                r = C.evaluate(stretch[k:])
                if r:
                    return m.end(), r[0], r[1], "inline"
    return None


def derived_hint(it: dict) -> str:
    months = it["graph"]["ytd_months"]
    return f"Method: the {months}-month total minus the latest three months gives the earlier period."


def teacher_text(it: dict) -> str:
    extra = " " + derived_hint(it) if it["kind"] == "derived" else ""
    return F.BRIEF + extra + "\n\n" + it["prompt"]


def arithmetic(text: str) -> list[dict]:
    """EXP-0056's check, except that a written number that starts a further expression is not a result."""
    out, pos = [], 0
    while True:
        hit = find_call(text, pos)
        if hit is None:
            return out
        end, expr, value, _ = hit
        pos = end
        if X56.DATE.match(expr.replace(" ", "")):
            continue
        m = X56.WRITTEN.match(text, end)
        if not m:
            out.append({"expr": expr, "value": value, "written": None, "ok": None})
            continue
        if CHAINED.match(text, m.end()):
            out.append({"expr": expr, "value": value, "written": None, "chained": True, "ok": None})
            continue
        w = float(m.group(1).replace(",", ""))
        dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
        slack = 0.5 * 10 ** (-dec) + 1e-9
        ok = (abs(w - value) <= slack + X56.REL_TOL * abs(value)
              or (m.group(2) is not None and abs(w - 100 * value) <= slack + X56.REL_TOL * abs(100 * value)))
        out.append({"expr": expr, "value": value, "written": w, "percent": m.group(2) is not None, "ok": ok})


X56.arithmetic = arithmetic  # EXP-0056's verify_one looks it up at call time


def chains(a):
    F.need_drive()
    model, tok = D14.load_model(D14.TEACHER)
    base = OUT / "chains" / a.dir
    base.mkdir(parents=True, exist_ok=True)
    path = base / "samples.jsonl"
    done = {r["id"] for r in F.jl(path)}
    jobs, skipped = [], 0
    for it in X56.pool(a.items):
        if it["id"] in done:
            continue
        cap = F.room(len(tok.encode(F.chat(tok, it["prompt"]))))
        if cap < F.MIN_ROOM:
            skipped += 1
            continue
        jobs += [{"key": {"id": it["id"]}, "prompt": F.chat(tok, teacher_text(it)), "cap": cap, "sample": s}
                 for s in range(a.k)]
    st = F.generate(model, tok, jobs, a.batch, path, F.sampled)
    print(json.dumps({**st, "items skipped, prompt too long": skipped}), flush=True)


def verify(a):
    F.OUT = OUT  # EXP-0070's verify reads OUT/chains/<dir>; the pool path was bound at import
    F.verify(a)


def math_cmd(a):
    F.OUT = OUT
    F.MATH_INSTRUCTION = MATH_BRIEF
    F.CHAIN_MAX = MATH_CAP  # room() caps at CHAIN_MAX; chains are not generated in this process
    if not a.files:
        a.files = ",".join(str(f) for f in GSM8K)
    F.math_cmd(a)


def check(_):
    t = "growth = (7,676 - 6,659) / 6,659 = 1,017 / 6,659 ≈ 15.27%. So 15.27% is not above 17%."
    r = arithmetic(t)
    assert [x["ok"] for x in r] == [None, True], r
    t2 = "growth = (7,676 - 6,659) / 6,659 = 15.4%."
    assert [x["ok"] for x in arithmetic(t2)] == [False]
    t3 = "operating income = 2,312 - 5,837 + 7,754 - 6,671 = 2,312 (as gross profit less SG&A)"
    assert [x["ok"] for x in arithmetic(t3)] == [False]
    it = {"kind": "derived", "graph": {"ytd_months": 6}, "prompt": "P"}
    assert teacher_text(it).endswith("gives the earlier period.\n\nP") and "6-month" in teacher_text(it)
    assert teacher_text({"kind": "growth", "prompt": "P"}) == F.BRIEF + "\n\nP"
    assert X56.verify_one.__globals__["arithmetic"] is arithmetic
    X56.check(None)
    print(json.dumps({"checks": "pass", "GSM8K files": [f.name for f in GSM8K]}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    sub.add_parser("check").set_defaults(fn=check)
    c = sub.add_parser("chains"); c.add_argument("--items", type=int, required=True); c.add_argument("--k", type=int, default=4)
    c.add_argument("--batch", type=int, default=16); c.add_argument("--dir", required=True); c.set_defaults(fn=chains)
    v = sub.add_parser("verify"); v.add_argument("--dir", required=True); v.set_defaults(fn=verify)
    m = sub.add_parser("math"); m.add_argument("--n", type=int, required=True); m.add_argument("--k", type=int, default=1)
    m.add_argument("--keep", type=int, default=1); m.add_argument("--batch", type=int, default=16)
    m.add_argument("--files", default=""); m.add_argument("--dir", required=True); m.set_defaults(fn=math_cmd)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
