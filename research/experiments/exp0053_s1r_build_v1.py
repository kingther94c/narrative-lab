"""EXP-0053: EarningsExam section R v1 generator (S1 re-plan, the R test builder fix).

The re-plan (``research/design/s1_finance_distillation_replan.md`` §4.3, approved 2026-11-26,
"全案推荐来") tests on section R after "R1.7 reworded and R1.8 limited to sensible margins by a new
builder first". EXP-0050's verdict found R1.7's golds right but its question sending every model to
"cannot be determined": the shared escape clause was read as "not stated" rather than "not
derivable". R1.8's all-wrong items were companies with almost no revenue (operating margins of
thousands of percent). An engineering step with no hypothesis and no model.

Everything is EXP-0019's builder (imported, unchanged: releases, sides, the two-source rule, the
excerpt, the twins, the identity checker), except:

* **The escape clause, on every template.** v0: "If the excerpt does not give enough information
  to answer, answer \\boxed{cannot be determined}." v1: "If the answer can neither be read from
  the excerpt nor worked out from its figures, answer \\boxed{cannot be determined}." The clause
  stays on every template, so its presence still says nothing about the gold. Dropping it from
  R1.7 alone, as EXP-0050's verdict floated, would make its absence a cue that R1.7 is answerable
  and its presence a cue for R1.9.
* **R1.8 margins.** An item is kept only if the margin is between -100% and +100% in both years
  (gross or operating income no larger in size than revenue).
* **Ids and version.** Ids hash "Rv1|accession|template|variant", so no v1 id equals a v0 id;
  ``exam_version`` is "R v1". Output in ``s1/exam_r_v1/``.

Claude must not read test items: ``show`` refuses the test side; ``build`` prints counts only.

    conda run --no-capture-output -n py313 python research/experiments/exp0053_s1r_build_v1.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0053_s1r_build_v1.py build --sides train,dev
    conda run --no-capture-output -n py313 python research/experiments/exp0053_s1r_build_v1.py build --sides test
    conda run --no-capture-output -n py313 python research/experiments/exp0053_s1r_build_v1.py show --side dev --template R1.7 --n 3
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0019_s1r_build as V0  # noqa: E402  (frozen; everything not changed below)

E = V0.E
TAIL_V0 = V0.TAIL
TAIL = ("If the answer can neither be read from the excerpt nor worked out from its figures, "
        "answer \\boxed{cannot be determined}.")
V0.TAIL = TAIL  # read at call time by every template of EXP-0019's Builder
V0.OUT = E.DRIVE / "s1" / "exam_r_v1"
MARGIN_LIMIT = 100.0


def sensible(n, rev):
    """Both years' margins within +-100%."""
    return all(abs(V0.margin(n, rev, w)) <= MARGIN_LIMIT for w in ("cur", "prior"))


class Builder(V0.Builder):
    def emit(self, template, variant, *a, **k):
        it = super().emit(template, variant, *a, **k)
        if it is not None:
            it["id"] = hashlib.sha256(f"Rv1|{self.t['accession']}|{template}|{variant}".encode()).hexdigest()[:16]
            it["exam_version"] = "R v1"
        return it

    def r18(self):
        rev = self.P.get("revenue")
        for name, num in (("gross", "gross_profit"), ("operating", "operating_income")):
            if rev is None or num not in self.P or rev["prior"] <= 0 or rev["cur"] <= 0:
                continue
            n = self.P[num]
            if not sensible(n, rev):
                self.why[f"R1.8: {name} margin beyond 100% in size in a year"] += 1
                continue
            d = V0.margin(n, rev, "cur") - V0.margin(n, rev, "prior")
            what = "profit" if name == "gross" else "income"
            ask = (f"by how many percentage points did its {name} margin ({name} {what} as a percentage of total revenue) "
                   f"change in the {self.period}, compared with the same period a year earlier? Give the answer in "
                   f"percentage points, one decimal place. {V0.SIGN} " + V0.TAIL)
            self.emit("R1.8", name, ask, round(d, 4), [rev["line"], n["line"]],
                      {"figures": [self.step(rev), self.step(n)], "change_points": round(d, 4)}, "number", tol={"abs": 0.15},
                      hint=f"{name.capitalize()} margin = {name} {what} / total revenue x 100, for each year; subtract.")


V0.Builder = Builder  # EXP-0019's build() looks the class up at call time


def check(_):
    def P(cur, prior):
        return {"cur": cur, "prior": prior}
    cases = [
        (sensible(P(30, 25), P(100, 90)), True),
        (sensible(P(-149, -120), P(1.6, 2.0)), False),   # EXP-0050's example: revenue 1.6 against a loss of 149
        (sensible(P(-100, -50), P(100, 100)), True),     # exactly -100% is kept
        (sensible(P(20, -101), P(100, 100)), False),     # the prior year alone is enough to drop
    ]
    bad = [i for i, (got, want) in enumerate(cases) if got != want]
    print("margin rule cases:", len(cases), "failures:", bad)
    print("tail v0:", TAIL_V0)
    print("tail v1:", V0.TAIL)
    print("output:", V0.OUT)
    print("EXP-0019's own checks:")
    V0.check(_)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build"); b.add_argument("--sides", default="train,dev"); b.set_defaults(fn=V0.build)
    s = sub.add_parser("show"); s.add_argument("--side", default="dev"); s.add_argument("--template", default="")
    s.add_argument("--twin", default=""); s.add_argument("--n", type=int, default=5); s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=V0.show)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
