"""EXP-0055: data factory step 2, varied training items from EXP-0054's fact sheets (S1 re-plan).

Re-plan §4.1, "task variety": from each release's verified figures, items of many kinds under fixed
quotas, at least 1,000 distinct question phrasings, no single answer template. An engineering step
with no hypothesis and no model; the teacher's chains are a later step. Every item is a training
company's, before the cutoff (EXP-0052, EXP-0054), so Claude may read them.

Fixed here:

* **Held out entirely:** diluted EPS and income before taxes appear in no item, so section R's R1.4
  (EPS against net income) and R1.5 (net income against pre-tax income) test reasoning the student
  never practised (re-plan §4.1, "held out from the factory entirely"; the main pre-registration
  may still change the choice, and this script would then be rerun as a new one).
* **Kinds and quotas** (share of the pool): extract 8%, growth 10%, margin level 7%, margin change
  10%, margin direction 10%, co-movement 8%, faster or slower 10%, true-or-false claim 10%, biggest
  or smallest mover 6%, derived period 6%, cannot be determined 8%, whole-release condition table
  7%. Golds come from the verified figures with section R's rules (R1.1's 0.5-point flat band and
  0.05 guard, R1.3's growth and rounding guards, R1.6's 5% gap, R1.7's XBRL check via the sheet,
  R1.8's margin limit), widened to more line items and pairs than R uses.
* **Wording.** Lead-ins, period and comparison phrases, line-item names (including the release's
  own row label), option sets, escape clauses and answer formats are drawn at random. R's two
  lead-ins and its escape clause are not in the pool, so no factory question equals an R question.
  Every item carries an escape clause (four wordings), as every R item does.
* **Answer formats:** \\boxed{} 40%, a final "Answer:" line 25%, JSON 20%, one sentence 15% (label
  and claim items only; number items drawn for a sentence take \\boxed{} instead).
* **Pool:** 30,000 items, releases in a seeded random order, at most three items per release (one
  per kind, the kind furthest behind its quota first) and at most 30 per company. Each item has a
  rank; the teacher step takes items in rank order, so the 5,000 and 20,000 example levels are
  nested.

    conda run --no-capture-output -n py313 python research/experiments/exp0055_s1f_items.py build
    conda run --no-capture-output -n py313 python research/experiments/exp0055_s1f_items.py show --kind table --n 2
"""

from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0052_s1f_release_pull as P52  # noqa: E402  (frozen; texts)
import exp0054_s1f_sheets as S54  # noqa: E402  (frozen; sheets; imports section R v1's builder)

V0, E = S54.V0, S54.E
OUT = E.DRIVE / "s1" / "exp0055"
SEED = 20261126
POOL = 30_000
PER_COMPANY = 30
PER_RELEASE = 3
HELD_OUT_METRICS = {"eps_diluted", "pretax"}
QUOTA = {"extract": .08, "growth": .10, "margin_level": .07, "margin_change": .10, "margin_direction": .10,
         "co_movement": .08, "faster_slower": .10, "claim": .10, "mover": .06, "derived": .06,
         "undetermined": .08, "table": .07}
UNDET = "cannot be determined"

NAMES = {
    "revenue": ["total revenue", "revenue"], "cost_of_revenue": ["cost of revenue", "cost of sales"],
    "gross_profit": ["gross profit"], "rd": ["research and development expense", "R&D expense"],
    "sga": ["selling, general and administrative expense", "SG&A expense"],
    "opex": ["total operating expenses", "operating expenses"], "costs_expenses": ["total costs and expenses"],
    "operating_income": ["operating income (loss)", "operating income", "income from operations"],
    "net_income": ["net income (loss) attributable to the company", "net income"],
}
LEADS = [
    "Here is an excerpt from {co}'s earnings release.",
    "The table below comes from {co}'s results announcement.",
    "Read this excerpt from {co}'s earnings release.",
    "Below are financial statements from an earnings release by {co}.",
    "You are given part of {co}'s earnings release.",
    "An analyst is reviewing {co}'s earnings release; the relevant table is below.",
    "From {co}'s earnings release:",
    "{co} reported the following results.",
]
CMP = ["compared with the same period a year earlier", "year over year", "against the prior-year period",
       "relative to the same period of the previous year"]
CLAUSES = [
    "If the answer can neither be read from the excerpt nor worked out from its figures, the answer is \"{u}\".",
    "If the excerpt does not contain the figures needed, directly or by calculation, answer \"{u}\".",
    "Answer \"{u}\" only if the information shown, including what can be calculated from it, is not enough.",
    "When the excerpt's figures do not allow an answer, even with arithmetic, reply \"{u}\".",
]
SIGNS = ["Use a minus sign for a negative value.", "Write a decrease or a loss with a minus sign.",
         "Negative values take a leading minus sign."]
FORMATS = {
    "boxed": "Put your final answer in \\boxed{}.",
    "answer_line": "End your reply with a line of the form \"Answer: <your answer>\".",
    "json": "End your reply with a JSON object of the form {\"answer\": <your answer>}.",
    "sentence": "Finish with one sentence that states your answer.",
}
FORMAT_P = [("boxed", .40), ("answer_line", .25), ("json", .20), ("sentence", .15)]
DIRECTION_SETS = [("expanded", "contracted", "flat", "expand", "contract", "stay flat"),
                  ("widened", "narrowed", "unchanged", "widen", "narrow", "stay unchanged"),
                  ("improved", "worsened", "about the same", "improve", "worsen", "stay about the same"),
                  ("rose", "fell", "flat", "rise", "fall", "stay flat")]
FS_SETS = [("faster", "slower"), ("more quickly", "more slowly")]
TF_SETS = [("true", "false"), ("yes", "no"), ("correct", "incorrect")]
MARGIN_OF = {"gross": "gross_profit", "operating": "operating_income", "net": "net_income"}
FS_PAIRS = [("opex", "revenue"), ("costs_expenses", "revenue"), ("cost_of_revenue", "revenue"), ("sga", "revenue"),
            ("rd", "revenue"), ("gross_profit", "revenue"), ("operating_income", "revenue"), ("net_income", "revenue")]
CO_PAIRS = [("revenue", "operating_income"), ("revenue", "net_income"), ("gross_profit", "operating_income"),
            ("revenue", "gross_profit")]
MOVER_SET = ["cost_of_revenue", "gross_profit", "rd", "sga", "operating_income"]
ABSENT = [("capital expenditures", r"capital\s+expend|capex|purchases?\s+of\s+property"),
          ("research and development expense", r"research"),
          ("ending backlog", r"backlog"), ("number of employees", r"employee|headcount")]


def clean_label(s):
    s = re.sub(r"\s*\(\d\)|\s*\*+|[:\s]+$", "", s.strip())
    s = re.sub(r"\s+", " ", s)
    return s[0].lower() + s[1:] if s and not s[:2].isupper() else s


class Maker:
    """Candidate items of one release, one per kind at most."""

    def __init__(self, sheet, lines, count, rng):
        self.s, self.lines, self.count, self.rng = sheet, lines, count, rng
        self.F = {m: f for m, f in sheet["figures"].items() if m not in HELD_OUT_METRICS}
        per = sheet["period"]
        self.end, self.kind = per["end"], per["kind"]
        q = rng.random() < 0.5
        unit = ("three months" if q else "quarter") if self.kind == "quarter" else ("fiscal year" if q else "year")
        self.period = f"the {unit} ended {E.long_date(self.end)}"
        self.prior_period = f"the {unit} ended {E.long_date(E.shift_year(self.end))}"

    # -- helpers
    def name(self, m):
        opts = list(NAMES[m])
        if m in self.F:
            lab = clean_label(self.F[m]["label"])
            if lab and not re.search(r"margin|%|percent", lab, re.I):  # a row named "gross margin" reads as a ratio
                opts.append(lab)
        return self.rng.choice(opts)

    def scale_word(self, m):
        return "millions" if self.F[m]["scale"] >= 1e6 else self.rng.choice(["millions", "thousands"])

    def half(self, m, which="cur"):
        f = self.F[m]
        return 0.5 * 10 ** (-(f["dec"] if which == "cur" else f["prior_dec"])) * f["scale"]

    def growth(self, m):
        f = self.F[m]
        return 100 * (f["cur"] / f["prior"] - 1)

    def margin(self, m, which):
        return 100 * self.F[m][which] / self.F["revenue"][which]

    def margin_ok(self, m):
        r = self.F.get("revenue")
        return (r is not None and m in self.F and r["cur"] > 0 and r["prior"] > 0
                and all(abs(self.margin(m, w)) <= S54.V1.MARGIN_LIMIT for w in ("cur", "prior")))

    def item(self, kind, ask, gold, atype, need, graph, tol=None, options=None, unit=None):
        if isinstance(gold, float):
            gold = round(gold, 4)
        return {"kind": kind, "ask": ask, "gold": gold, "atype": atype, "need": sorted(set(need)), "graph": graph,
                "tol": tol, "options": options, "unit": unit}

    # -- kinds
    def extract(self):
        m = self.rng.choice(list(self.F))
        which = self.rng.choice(["cur", "prior"])
        sw = self.scale_word(m)
        gold = self.F[m][which] / E.SCALES[sw]
        tol = {"abs": round(self.half(m, which) / E.SCALES[sw] * 1.01, 6)}
        per = self.period if which == "cur" else self.prior_period
        ask = f"What was its {self.name(m)} for {per}? Give the answer in {sw} of US dollars. {self.rng.choice(SIGNS)}"
        return self.item("extract", ask, gold, "number", [self.F[m]["line"]], {"metric": m, "which": which}, tol, unit=sw)

    def growth_item(self):
        ms = [m for m in self.F if self.F[m]["cur"] > 0 and self.F[m]["prior"] > 0]
        if not ms:
            return None
        m = self.rng.choice(ms)
        lo, hi = V0.growth_bounds(None, self.F[m]["cur"], self.F[m]["prior"], self.half(m), self.half(m, "prior"))
        g = self.growth(m)
        if (hi - lo) / 2 > 1.0:
            return None  # display rounding leaves the growth rate too loose
        tol = {"abs": round(max(0.15, (hi - lo) / 2 + 0.05), 4)}
        ask = (f"By what percentage did its {self.name(m)} change in {self.period}, {self.rng.choice(CMP)}? "
               f"Give the answer in percent, one decimal place. {self.rng.choice(SIGNS)}")
        return self.item("growth", ask, round(g, 4), "number", [self.F[m]["line"]], {"metric": m, "growth": g}, tol, unit="percent")

    def _margin_pick(self):
        names = [n for n, m in MARGIN_OF.items() if self.margin_ok(m)]
        return self.rng.choice(names) if names else None

    def _margin_def(self, n):
        return f"{n} margin ({self.name(MARGIN_OF[n])} as a percentage of {self.name('revenue')})"

    def margin_level(self):
        n = self._margin_pick()
        if n is None:
            return None
        which = self.rng.choice(["cur", "prior"])
        v = self.margin(MARGIN_OF[n], which)
        per = self.period if which == "cur" else self.prior_period
        ask = f"What was its {self._margin_def(n)} in {per}? Give the answer in percent, one decimal place. {self.rng.choice(SIGNS)}"
        return self.item("margin_level", ask, round(v, 4), "number", [self.F["revenue"]["line"], self.F[MARGIN_OF[n]]["line"]],
                         {"margin": n, "which": which, "value": v}, {"abs": 0.15}, unit="percent")

    def margin_change(self):
        n = self._margin_pick()
        if n is None:
            return None
        d = self.margin(MARGIN_OF[n], "cur") - self.margin(MARGIN_OF[n], "prior")
        ask = (f"By how many percentage points did its {self._margin_def(n)} change in {self.period}, {self.rng.choice(CMP)}? "
               f"Give the answer in percentage points, one decimal place. {self.rng.choice(SIGNS)}")
        return self.item("margin_change", ask, round(d, 4), "number", [self.F["revenue"]["line"], self.F[MARGIN_OF[n]]["line"]],
                         {"margin": n, "change_points": d}, {"abs": 0.15}, unit="points")

    def direction(self, n):
        """R1.1's rule: None inside the guard band."""
        d = self.margin(MARGIN_OF[n], "cur") - self.margin(MARGIN_OF[n], "prior")
        if abs(abs(d) - 0.5) < 0.05:
            return None, d
        return (2 if abs(d) < 0.5 else 0 if d > 0 else 1), d

    def margin_direction(self):
        n = self._margin_pick()
        if n is None:
            return None
        k, d = self.direction(n)
        if k is None:
            return None
        opts = self.rng.choice(DIRECTION_SETS)
        shown = list(opts[:3])
        self.rng.shuffle(shown)
        ask = (f"Did its {self._margin_def(n)} {opts[3]}, {opts[4]} or {opts[5]} in {self.period}, {self.rng.choice(CMP)}? "
               f"A rising margin, including a loss margin that shrinks, counts as \"{opts[0]}\"; a change of less than 0.5 "
               f"percentage points counts as \"{opts[2]}\". Answer with one of: {', '.join(shown)}.")
        return self.item("margin_direction", ask, opts[k], "label", [self.F["revenue"]["line"], self.F[MARGIN_OF[n]]["line"]],
                         {"margin": n, "change_points": d}, options=shown)

    def co_movement(self):
        pairs = [p for p in CO_PAIRS if all(m in self.F for m in p)
                 and all(self.F[m]["cur"] != self.F[m]["prior"] for m in p)]
        if not pairs:
            return None
        a, b = self.rng.choice(pairs)
        na, nb = self.name(a), self.name(b)
        up = [self.F[m]["cur"] > self.F[m]["prior"] for m in (a, b)]
        opts = ["both rose", "both fell", f"{na} rose and {nb} fell", f"{na} fell and {nb} rose"]
        gold = opts[{(True, True): 0, (False, False): 1, (True, False): 2, (False, True): 3}[tuple(up)]]
        shown = list(opts)
        self.rng.shuffle(shown)
        ask = (f"How did its {na} and its {nb} move in {self.period}, {self.rng.choice(CMP)}? A smaller loss counts as a rise. "
               f"Answer with one of: {'; '.join(shown)}.")
        return self.item("co_movement", ask, gold, "label", [self.F[a]["line"], self.F[b]["line"]],
                         {"pair": [a, b], "up": up}, options=shown)

    def fs_label(self, a, b):
        return V0.faster_or_slower({**self.F[a], "metric": a}, {**self.F[b], "metric": b})[0]

    def faster_slower(self):
        pairs = [p for p in FS_PAIRS if all(m in self.F for m in p) and self.fs_label(*p)]
        if not pairs:
            return None
        a, b = self.rng.choice(pairs)
        lab = self.fs_label(a, b)
        if self.rng.random() < 0.5:
            a, b, lab = b, a, "slower" if lab == "faster" else "faster"
        words = self.rng.choice(FS_SETS)
        gold = words[0] if lab == "faster" else words[1]
        ask = (f"Did its {self.name(a)} grow {words[0]} or {words[1]} than its {self.name(b)} in {self.period}, "
               f"{self.rng.choice(CMP)}? Compare growth rates in percent; a smaller decline counts as faster growth. "
               f"Answer with one of: {words[0]}, {words[1]}.")
        return self.item("faster_slower", ask, gold, "label", [self.F[a]["line"], self.F[b]["line"]],
                         {"a": a, "b": b, "growth_a": self.growth(a), "growth_b": self.growth(b)}, options=list(words))

    def claim(self):
        cands = []
        for n, m in MARGIN_OF.items():
            if self.margin_ok(m):
                k, d = self.direction(n)
                if k in (0, 1) and abs(d) >= 0.5:
                    cands.append(("margin", n, k == 0, d))
        for a, b in FS_PAIRS:
            if all(m in self.F for m in (a, b)) and self.fs_label(a, b):
                cands.append(("fs", (a, b), self.fs_label(a, b) == "faster", None))
        for m in self.F:
            f = self.F[m]
            if f["cur"] > 0 and f["prior"] > 0:
                lo, hi = V0.growth_bounds(None, f["cur"], f["prior"], self.half(m), self.half(m, "prior"))
                cands.append(("threshold", m, (lo, hi), self.growth(m)))
        if not cands:
            return None
        c = self.rng.choice(cands)
        true_claim = self.rng.random() < 0.5
        if c[0] == "margin":
            word = "rose" if c[2] == true_claim else "fell"
            text = f"its {self._margin_def(c[1])} {word} in {self.period}, {self.rng.choice(CMP)}"
            need = [self.F["revenue"]["line"], self.F[MARGIN_OF[c[1]]]["line"]]
        elif c[0] == "fs":
            a, b = c[1]
            word = "faster" if c[2] == true_claim else "more slowly"
            text = f"its {self.name(a)} grew {word} than its {self.name(b)} in {self.period}, {self.rng.choice(CMP)}"
            need = [self.F[a]["line"], self.F[b]["line"]]
        else:
            m, (lo, hi), g = c[1], c[2], c[3]
            x = round(g + self.rng.choice([-1, 1]) * self.rng.uniform(1.5, 6))
            if lo - 1 <= x <= hi + 1:
                return None
            true_claim = g > x
            text = (f"the growth rate of its {self.name(m)} in {self.period}, {self.rng.choice(CMP)}, "
                    f"was above {x}%")
            need = [self.F[m]["line"]]
        tf = self.rng.choice(TF_SETS)
        ask = f"Claim: {text}. Is the claim {tf[0]} or {tf[1]}? Answer with one of: {tf[0]}, {tf[1]}."
        return self.item("claim", ask, tf[0] if true_claim else tf[1], "label", need,
                         {"claim": c[0], "subject": c[1] if c[0] != "threshold" else [c[1], x], "true": true_claim},
                         options=list(tf))

    def mover(self):
        ms = [m for m in MOVER_SET if m in self.F]
        if len(ms) < 3:
            return None
        ch = {m: abs(self.F[m]["cur"] - self.F[m]["prior"]) for m in ms}
        order = sorted(ms, key=lambda m: -ch[m])
        most = self.rng.random() < 0.7
        if most:
            if ch[order[0]] == 0 or ch[order[1]] >= 0.95 * ch[order[0]]:
                return None
            gold_m = order[0]
        else:
            if ch[order[-2]] == 0 or ch[order[-1]] >= 0.95 * ch[order[-2]]:
                return None
            gold_m = order[-1]
        names = {m: self.name(m) for m in ms}
        shown = list(ms)
        self.rng.shuffle(shown)
        ask = (f"Which of these lines changed the {'most' if most else 'least'} in US dollars (the size of the change, up or "
               f"down) in {self.period}, {self.rng.choice(CMP)}: {'; '.join(names[m] for m in shown)}? "
               f"Answer with one of: {'; '.join(names[m] for m in shown)}.")
        return self.item("mover", ask, names[gold_m], "label", [self.F[m]["line"] for m in ms],
                         {"changes": ch, "most": most}, options=[names[m] for m in shown])

    def derived(self):
        r7 = [i for i in self.s["r_items"] if i["template"] == "R1.7" and i["variant"].split(":")[0] in self.F]
        if not r7:
            return None
        it = self.rng.choice(r7)
        m, months = it["variant"].split(":")[0], int(it["variant"].split(":")[1].rstrip("m"))
        st = it["steps"]
        scale = st["figures"][0]["scale"]
        derived = (st["ytd_shown"] - st["quarter_shown"]) * scale
        ed = (E.dt.date.fromisoformat(self.s["period"]["start"]) - E.dt.timedelta(days=1)).isoformat()
        per = f"the {'three' if months == 6 else 'six'} months ended {E.long_date(ed)}"
        sw = "millions" if scale >= 1e6 else self.rng.choice(["millions", "thousands"])
        tol = {"abs": round((0.5 * 10 ** (-self.F[m]["dec"]) * scale * 2) / E.SCALES[sw] * 1.01, 6)}
        ask = f"What was its {self.name(m)} for {per}? Give the answer in {sw} of US dollars. {self.rng.choice(SIGNS)}"
        return self.item("derived", ask, derived / E.SCALES[sw], "number", it["need_lines"],
                         {"metric": m, "ytd_months": months, "ytd_shown": st["ytd_shown"], "quarter_shown": st["quarter_shown"],
                          "xbrl_earlier": st["xbrl_earlier"]}, tol, unit=sw)

    def undetermined(self):
        m = self.rng.choice(list(self.F))
        if self.rng.random() < 0.5:
            back = E.shift_year(E.shift_year(self.end))
            per = self.period.rsplit(" ended ", 1)[0] + f" ended {E.long_date(back)}"
            ask = f"What was its {self.name(m)} for {per}? Give the answer in millions of US dollars. {self.rng.choice(SIGNS)}"
            return self.item("undetermined", ask, UNDET, "undetermined", [self.F[m]["line"]],
                             {"why": "period not shown", "year": back[:4]})
        what, pat = self.rng.choice(ABSENT)
        ask = f"What figure does it report for its {what} for {self.period}? Give amounts in millions of US dollars."
        return self.item("undetermined", ask, UNDET, "undetermined", [self.F[m]["line"]], {"why": "line absent", "pattern": pat})

    def table(self):
        conds, need = [], []
        for n, m in MARGIN_OF.items():
            if self.margin_ok(m):
                k, d = self.direction(n)
                if k is not None:
                    conds.append((f"{n} margin", ["expanded", "contracted", "flat"][k]))
                    need += [self.F["revenue"]["line"], self.F[m]["line"]]
        if all(m in self.F for m in ("revenue", "operating_income")) and all(self.F[m]["cur"] != self.F[m]["prior"] for m in ("revenue", "operating_income")):
            up = [self.F[m]["cur"] > self.F[m]["prior"] for m in ("revenue", "operating_income")]
            conds.append(("revenue and operating income", {(True, True): "both rose", (False, False): "both fell",
                          (True, False): "revenue rose, operating income fell", (False, True): "revenue fell, operating income rose"}[tuple(up)]))
            need += [self.F["revenue"]["line"], self.F["operating_income"]["line"]]
        for a in ("opex", "costs_expenses"):
            if all(m in self.F for m in (a, "revenue")) and self.fs_label(a, "revenue"):
                conds.append((f"{NAMES[a][0]} against revenue", f"grew {self.fs_label(a, 'revenue')}"))
                need += [self.F[a]["line"], self.F["revenue"]["line"]]
                break
        if len(conds) < 3:
            return None
        rows = "\n".join(f"- {c}" for c, _ in conds)
        ask = (f"Fill in this condition table for {self.period}, {self.rng.choice(CMP)}. Margins: expanded, contracted or flat "
               f"(a change under 0.5 percentage points is flat; a shrinking loss margin has expanded). Revenue and operating "
               f"income: both rose, both fell, revenue rose, operating income fell, or revenue fell, operating income rose. "
               f"Costs against revenue: grew faster or grew slower. Conditions:\n{rows}\n"
               f"Give one line per condition, in the form \"<condition>: <value>\".")
        return self.item("table", ask, dict(conds), "table", need, {"conditions": conds})

    KINDS = {"extract": "extract", "growth": "growth_item", "margin_level": "margin_level", "margin_change": "margin_change",
             "margin_direction": "margin_direction", "co_movement": "co_movement", "faster_slower": "faster_slower",
             "claim": "claim", "mover": "mover", "derived": "derived", "undetermined": "undetermined", "table": "table"}

    def render(self, it):
        ex = E.excerpt(self.lines, it["need"], self.count)
        if ex is None:
            return None
        body, n = ex
        if it["kind"] == "undetermined":
            g = it["graph"]
            if g["why"] == "period not shown" and g["year"] in body:
                return None
            if g["why"] == "line absent" and re.search(g["pattern"], body, re.I):
                return None
        fmt = self.rng.choices([f for f, _ in FORMAT_P], [p for _, p in FORMAT_P])[0]
        if fmt == "sentence" and it["atype"] not in ("label",):
            fmt = "boxed"
        if it["atype"] == "table":
            fmt = "lines"
        lead = self.rng.randrange(len(LEADS))
        clause = self.rng.randrange(len(CLAUSES))
        parts = [it["ask"], CLAUSES[clause].format(u=UNDET)]
        if fmt != "lines":
            parts.append(FORMATS[fmt])
        q = " ".join(parts)
        lead_text = LEADS[lead].format(co=self.s["name"])
        before = self.rng.random() < 0.5
        prompt = f"{lead_text}\n\n{q}\n\n{body}" if before else f"{lead_text}\n\n{body}\n\n{q}"
        return {**it, "prompt": prompt, "format": fmt, "lead": lead, "clause": clause, "question_first": before,
                "excerpt_tokens": n}


def build(a):
    if not E.DRIVE.exists():
        sys.exit("external drive not mounted")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(glob.glob(f"{E.TOKENIZER}/snapshots/*/tokenizer.json")[0])
    count = lambda s: len(tok.encode(s).ids)  # noqa: E731
    sheets = [json.loads(l) for l in open(S54.SHEETS, encoding="utf-8")]
    sheets = [s for s in sheets if s.get("figures") and any(m not in HELD_OUT_METRICS for m in s["figures"])]
    rng = random.Random(SEED)
    rng.shuffle(sheets)
    want = {k: round(q * a.pool) for k, q in QUOTA.items()}
    got = collections.Counter()
    per_co = collections.Counter()
    why = collections.Counter()
    out = []
    for s in sheets:
        if sum(got.values()) >= a.pool:
            break
        if per_co[s["cik"]] >= PER_COMPANY:
            why["company cap"] += 1
            continue
        lines = (P52.TEXTS / f"{s['cik']}_{s['accession']}.txt").read_text(encoding="utf-8").splitlines()
        mk = Maker(s, lines, count, random.Random(f"{SEED}|{s['accession']}"))
        kinds = [k for k in QUOTA if got[k] < want[k]]
        mk.rng.shuffle(kinds)
        kinds.sort(key=lambda k: got[k] / want[k])  # the kind furthest behind its quota first
        made = 0
        for k in kinds:
            if per_co[s["cik"]] >= PER_COMPANY or made >= PER_RELEASE:
                break
            it = getattr(mk, Maker.KINDS[k])()
            if it is None:
                why[f"{k}: no candidate"] += 1
                continue
            r = mk.render(it)
            if r is None:
                why[f"{k}: excerpt failed or gave the answer away"] += 1
                continue
            r.update({"cik": s["cik"], "company": s["name"], "accession": s["accession"], "acceptance": s["acceptance"],
                      "period": s["period"], "rank": len(out),
                      "id": hashlib.sha256(f"Fv1|{s['accession']}|{k}".encode()).hexdigest()[:16]})
            out.append(r)
            got[k] += 1
            per_co[s["cik"]] += 1
            made += 1
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "pool.jsonl", "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    skel = {(r["kind"], r["lead"], r["clause"], r["format"], r["question_first"], re.sub(r"\d", "#", r["ask"][:40])) for r in out}
    rep = {"sheets usable": len(sheets), "items": len(out), "by kind (want)": {k: f"{got[k]} ({want[k]})" for k in QUOTA},
           "companies": len({r["cik"] for r in out}), "releases": len({r["accession"] for r in out}),
           "by format": dict(collections.Counter(r["format"] for r in out)),
           "distinct phrasing skeletons (kind, lead, clause, format, order, opening of the ask)": len(skel),
           "label golds": {k: dict(collections.Counter(str(r["gold"]) for r in out if r["kind"] == k).most_common(6))
                           for k in ("margin_direction", "co_movement", "faster_slower", "claim")},
           "excerpt tokens median / p90": None, "items per company max": max(per_co.values()) if per_co else 0,
           "skipped": dict(why.most_common())}
    tk = sorted(r["excerpt_tokens"] for r in out)
    if tk:
        rep["excerpt tokens median / p90"] = [tk[len(tk) // 2], tk[9 * len(tk) // 10]]
    (OUT / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


def show(a):
    items = [json.loads(l) for l in open(OUT / "pool.jsonl", encoding="utf-8")]
    items = [i for i in items if not a.kind or i["kind"] == a.kind]
    for it in random.Random(a.seed).sample(items, min(a.n, len(items))):
        print("=" * 100)
        print(it["id"], it["kind"], it["format"], "GOLD:", it["gold"], it["tol"])
        print(it["prompt"][:3000])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build"); b.add_argument("--pool", type=int, default=POOL); b.set_defaults(fn=build)
    s = sub.add_parser("show"); s.add_argument("--kind", default=""); s.add_argument("--n", type=int, default=3)
    s.add_argument("--seed", type=int, default=0); s.set_defaults(fn=show)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
