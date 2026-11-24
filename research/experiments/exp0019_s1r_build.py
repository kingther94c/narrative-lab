"""EXP-0019: EarningsExam section R v0 generator (sub-study S1, step R-a of the reasoning exam).

Design: ``research/design/s1_reasoning_exam.md`` (owner's decisions D1 to D5, 2026-11-23). An
engineering measurement with no hypothesis: it builds the items and reports yield per template,
verification failures and twin rejections. No model is run.

What it reuses, unchanged, from EarningsExam (EXP-0005, with EXP-0008's column-heading excerpt):
the releases and their side (company split v1; train = pre-cutoff releases of training companies,
dev = development companies, test = post-cutoff releases of test companies), the table parser,
the XBRL period of the release, and the two-source rule: every figure an item uses is shown in a
table row whose label names it, at the table's scale, and equals the value first filed in XBRL for
that period. A prior-year figure must sit in the same row as the current one and equal XBRL's
prior-year value. What changes:

* the excerpt budget is 800 tokens (decision D2; B used 400), because an item needs several rows;
* seven line items beside B's five: cost of revenue, R&D, SG&A, total operating expenses, total
  costs and expenses, income before income taxes;
* the templates below, each with its rule fixed here before any item is built.

Templates (gold from the figures as the release displays them; the XBRL values only confirm):

* R1.1 margin direction (gross, operating, net margin): expanded, contracted or flat (a change
  under 0.5 points). Dropped if the change is within 0.05 points of the 0.5 threshold.
* R1.2 revenue and operating income: both rose, both fell, or which rose. Dropped if either is
  unchanged.
* R1.3 cost against sales: did total operating expenses (or total costs and expenses) grow faster
  or slower than revenue. Both positive in both years; dropped if the growth rates are within 0.5
  points, or if display rounding could flip the answer.
* R1.4 diluted EPS against net income: faster or slower. Both positive in both years; same rule.
* R1.5 net income against income before taxes: faster or slower. Same rule.
* R1.6 biggest mover in dollars among the verified lines of cost of revenue, gross profit, R&D
  and SG&A (at least three). Dropped if the top two changes are within 5% of each other.
* R1.7 derived period: the release shows the year to date (six or nine months) and the quarter;
  the item asks for the earlier part (first quarter, or first half), which the release does not
  show. The difference must equal XBRL's value for that period within display rounding.
  Revenue, operating income, net income.
* R1.8 margin change in points (gross, operating): a number, tolerance 0.15 points.
* R1.9 not answerable: the item asks for revenue two years back (the year appears nowhere in the
  excerpt) or for R&D expense (no line of the excerpt mentions research). Gold "cannot be
  determined".

Every R question ends with the same sentence, whatever the gold: answer
``\\boxed{cannot be determined}`` if the excerpt does not give enough information. Number items
also carry B's minus-sign sentence. Label items list their options.

Twins (R2), each a separate item with ``twin_of`` set:

* flip (period swap), for R1.1 not flat, R1.2 to R1.5 and R1.8: the current and prior years are
  swapped in the excerpt's column headings, so each column stays internally consistent and the
  answer reverses. Only when the heading lines carry the two years equally often. This replaces
  the design's "change one figure and recompute the totals": editing one figure in raw release
  text and every total below it cannot be done reliably, a column swap preserves every identity.
* hold (irrelevant line), for every R1 item: one row of employee counts added after the last row
  of the excerpt, laid out like a needed row. The answer does not change.
* mirror, for R1.3 to R1.5: the question with its two subjects swapped; the answer reverses.

The identity checker (gross profit = revenue - cost of revenue, per column, where all three rows
are in the excerpt) runs on each base excerpt and twin; a twin is rejected if its base passes and
it fails.

Claude must not read test items: ``show`` refuses the test side; ``build`` prints counts only.

    conda run --no-capture-output -n py313 python research/experiments/exp0019_s1r_build.py build --sides train,dev
    conda run --no-capture-output -n py313 python research/experiments/exp0019_s1r_build.py build --sides test
    conda run --no-capture-output -n py313 python research/experiments/exp0019_s1r_build.py show --side dev --template R1.4 --n 3
    conda run --no-capture-output -n py313 python research/experiments/exp0019_s1r_build.py check
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
import exp0008_earnings_exam_v0_1 as E1  # noqa: E402  (sets E.excerpt to the heading-keeping one)
import split_v1  # noqa: E402

E = E1.E
E.MAX_TOKENS = 800  # decision D2
OUT = E.DRIVE / "s1" / "exam_r_v0"
SEED = 20261124
UNDETERMINED = "cannot be determined"
TAIL = "If the excerpt does not give enough information to answer, answer \\boxed{cannot be determined}."
SIGN = "Use a minus sign for a negative value (a loss or a decrease)."

R_METRICS = {
    **E.METRICS,
    "cost_of_revenue": {
        "name": "cost of revenue",
        "concepts": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "CostOfServices"],
        "label": re.compile(r"^(total\s+)?cost\s+of\s+(total\s+)?(revenues?|sales|net\s+sales|goods\s+sold|products?\s+sold|products?|services?)\b", re.I),
        "unit": "USD",
    },
    "rd": {
        "name": "research and development expense",
        "concepts": ["ResearchAndDevelopmentExpense", "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost"],
        "label": re.compile(r"^(research\s+(and|&)\s+development|r\s*&\s*d)\b", re.I),
        "unit": "USD",
    },
    "sga": {
        "name": "selling, general and administrative expense",
        "concepts": ["SellingGeneralAndAdministrativeExpense"],
        "label": re.compile(r"^(total\s+)?(selling,?\s+general,?\s+(and|&)\s+administrative|sg\s*&\s*a)\b", re.I),
        "unit": "USD",
    },
    "opex": {
        "name": "total operating expenses",
        "concepts": ["OperatingExpenses"],
        "label": re.compile(r"^total\s+operating\s+(expenses|costs\s+and\s+expenses)\b", re.I),
        "unit": "USD",
    },
    "costs_expenses": {
        "name": "total costs and expenses",
        "concepts": ["CostsAndExpenses"],
        "label": re.compile(r"^total\s+(operating\s+)?costs\s+and\s+expenses\b", re.I),
        "unit": "USD",
    },
    "pretax": {
        "name": "income (loss) before income taxes",
        "concepts": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                     "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
        "label": re.compile(r"^(total\s+)?(income|earnings|loss|\(loss\)|profit)[\w\s()/,-]{0,40}?before\s+(provision\s+for\s+|benefit\s+from\s+|\(?provision\)?\s+)?(for\s+)?(income\s+)?tax", re.I),
        "unit": "USD",
    },
}
USD_METRICS = [m for m, s in R_METRICS.items() if s["unit"] == "USD"]

PHRASE = {
    "p1": "According to the excerpt from {company}'s earnings release, {ask}",
    "p2": "Using the financial statements below from {company}'s earnings release, {ask}",
}


# ---------------------------------------------------------------------------------------------
# Two-source figures

def value_for(gaap, metric, start, end, filed_on, first_filed_any=False, dur=None):
    """EXP-0005's value_for over R_METRICS; ``dur`` (min, max days) replaces the exact start."""
    spec = R_METRICS[metric]
    for c in spec["concepts"]:
        rows = []
        for r in gaap.get(c, {}).get("units", {}).get(spec["unit"], []):
            if not r.get("start") or abs(E.days(r["end"], end)) > 3:
                continue
            if dur is None and abs(E.days(r["start"], start)) > 3:
                continue
            if dur is not None and not (dur[0] <= E.days(r["start"], r["end"]) <= dur[1]):
                continue
            rows.append(r)
        if not first_filed_any:
            rows = [r for r in rows if E.days(filed_on, r["filed"]) >= -3]
        if rows:
            r = min(rows, key=lambda r: r["filed"])
            return r["val"], c, r["accn"], r["start"]
    return None


def find_row(lines, rows, metric, target):
    """EXP-0005's find_row over R_METRICS."""
    spec = R_METRICS[metric]
    per_share = spec["unit"] == "USD/shares"
    for i, label, vals in rows:
        if not spec["label"].search(label):
            continue
        if metric == "eps_diluted" and not re.search(r"diluted", label, re.I):
            continue
        if metric != "eps_diluted" and re.search(r"per\s+share|margin\s*%|%", label, re.I):
            continue
        scale, _ = (1.0, None) if per_share else E.scale_for(lines, i)
        if scale is None:
            continue
        for col, (v, dec, digits) in enumerate(vals):
            if E.matches(v, dec, digits, scale, target, per_share):
                return {"line": i, "label": label, "shown": v, "col": col, "scale": scale, "dec": dec, "vals": vals}
    return None


def half_unit(f):
    """Half a unit of the displayed figure, in dollars (or dollars per share)."""
    return 0.5 * 10 ** (-f["dec"]) * f["scale"]


def pair_for(gaap, lines, rows, metric, start, end, filed_on, why):
    """Current and prior-year figure of a metric, both verified, in one row: dict or None."""
    cur = value_for(gaap, metric, start, end, filed_on)
    if cur is None:
        return None
    f = find_row(lines, rows, metric, cur[0])
    if f is None:
        why[f"{metric}: current not in a row"] += 1
        return None
    prior = value_for(gaap, metric, E.shift_year(start), E.shift_year(end), filed_on, first_filed_any=True)
    if prior is None:
        why[f"{metric}: no prior-year XBRL"] += 1
        return None
    per_share = R_METRICS[metric]["unit"] == "USD/shares"
    hits = [(k, v, d) for k, (v, d, g) in enumerate(f["vals"]) if k != f["col"] and E.matches(v, d, g, f["scale"], prior[0], per_share)]
    if not hits:
        why[f"{metric}: prior year not in the row"] += 1
        return None
    k, v, d = hits[0]
    return {**f, "metric": metric, "cur": f["shown"] * f["scale"], "prior": v * f["scale"], "prior_col": k,
            "prior_dec": d, "xbrl": {"concept": cur[1], "accession": cur[2], "value": cur[0], "prior_value": prior[0]}}


# ---------------------------------------------------------------------------------------------
# Rules

def growth_bounds(p, cur, prior, cur_half, prior_half):
    """Range of growth (percent) consistent with display rounding of both figures."""
    if prior - prior_half <= 0:
        return -1e9, 1e9
    lo = 100 * ((cur - cur_half) / (prior + prior_half) - 1)
    hi = 100 * ((cur + cur_half) / (prior - prior_half) - 1)
    return lo, hi


def faster_or_slower(a, b):
    """'faster' if growth of a exceeds growth of b robustly, 'slower' if robustly below, else None."""
    if min(a["cur"], a["prior"], b["cur"], b["prior"]) <= 0:
        return None, "not positive in both years"
    ha = (half_unit(a), 0.5 * 10 ** (-a["prior_dec"]) * a["scale"])
    hb = (half_unit(b), 0.5 * 10 ** (-b["prior_dec"]) * b["scale"])
    alo, ahi = growth_bounds(None, a["cur"], a["prior"], *ha)
    blo, bhi = growth_bounds(None, b["cur"], b["prior"], *hb)
    ga, gb = 100 * (a["cur"] / a["prior"] - 1), 100 * (b["cur"] / b["prior"] - 1)
    if abs(ga - gb) < 0.5:
        return None, "growth rates within 0.5 points"
    if alo > bhi:
        return "faster", None
    if ahi < blo:
        return "slower", None
    return None, "display rounding could flip it"


def margin(num, rev, which):
    return 100 * num[which] / rev[which]


# ---------------------------------------------------------------------------------------------
# Items

class Builder:
    def __init__(self, t, text, gaap, count, rng, side, why):
        self.t, self.gaap, self.count, self.rng, self.side, self.why = t, gaap, count, rng, side, why
        self.lines = text.splitlines()
        self.rows = E.table_rows(self.lines)
        self.items = []

    def emit(self, template, variant, ask_p, gold, need, steps, kind, tol=None, options=None, hint=None, extra=None):
        ex = E.excerpt(self.lines, need, self.count)
        if ex is None:
            self.why[f"{template}: excerpt over budget or no heading"] += 1
            return None
        body, n = ex
        uid = hashlib.sha256(f"R|{self.t['accession']}|{template}|{variant}".encode()).hexdigest()[:16]
        qs = {p: PHRASE[p].format(company=self.t["name"], ask=ask_p) for p in PHRASE}
        it = {"id": uid, "side": self.side, "cik": self.t["cik"], "company": self.t["name"],
              "accession": self.t["accession"], "acceptance": self.t["acceptance"], "post_cutoff": self.t["post_cutoff"],
              "section": "R", "family": "R1", "template": template, "variant": variant, "kind": kind,
              "period": {"start": self.start, "end": self.end, "kind": self.kind},
              "question": qs["p1"], "question_p2": qs["p2"], "excerpt": body, "excerpt_tokens": n,
              "gold": gold, "tolerance": tol, "options": options, "hint": hint, "steps": steps,
              "need_lines": sorted(set(need)), "exam_version": "R v0", **(extra or {})}
        self.items.append(it)
        return it

    def build(self):
        per = E.period_for(self.gaap, self.t["filing_date"])
        if per is None:
            return "no XBRL period"
        self.start, self.end, self.kind = per
        what = "three months" if self.kind == "quarter" else "fiscal year"
        self.period = f"{what} ended {E.long_date(self.end)}"
        P = {}
        for m in R_METRICS:
            p = pair_for(self.gaap, self.lines, self.rows, m, self.start, self.end, self.t["filing_date"], self.why)
            if p:
                P[m] = p
        self.P = P
        self.r11(); self.r12(); self.r13(); self.r14(); self.r15(); self.r16(); self.r17(); self.r18(); self.r19()
        return "ok" if self.items else "no item"

    def step(self, p):
        return {"metric": p["metric"], "label": p["label"], "line": p["line"], "current": p["shown"],
                "prior": p["prior"] / p["scale"], "scale": p["scale"]}

    def r11(self):
        rev = self.P.get("revenue")
        for name, num in (("gross", "gross_profit"), ("operating", "operating_income"), ("net", "net_income")):
            if rev is None or num not in self.P or rev["prior"] <= 0 or rev["cur"] <= 0:
                continue
            n = self.P[num]
            mc, mp = margin(n, rev, "cur"), margin(n, rev, "prior")
            d = mc - mp
            if abs(abs(d) - 0.5) < 0.05:
                self.why["R1.1: within 0.05 of the threshold"] += 1
                continue
            gold = "flat" if abs(d) < 0.5 else "expanded" if d > 0 else "contracted"
            ask = (f"did its {name} margin ({name} {'profit' if name == 'gross' else 'income'} as a percentage of total revenue) "
                   f"expand, contract or stay flat in the {self.period}, compared with the same period a year earlier? "
                   "A margin that rises, including a loss margin that shrinks, has expanded; treat a change of less than "
                   "0.5 percentage points as flat. Answer with exactly one of: expanded, contracted, flat. " + TAIL)
            self.emit("R1.1", name, ask, gold, [rev["line"], n["line"]],
                      {"figures": [self.step(rev), self.step(n)], "margin_current": round(mc, 4), "margin_prior": round(mp, 4),
                       "change_points": round(d, 4)},
                      "label", options=["expanded", "contracted", "flat"],
                      hint=f"{name.capitalize()} margin = {name} {'profit' if name == 'gross' else 'income'} / total revenue x 100; compare the two years.")

    def r12(self):
        rev, oi = self.P.get("revenue"), self.P.get("operating_income")
        if not (rev and oi):
            return
        dr, do = rev["cur"] - rev["prior"], oi["cur"] - oi["prior"]
        if dr == 0 or do == 0:
            self.why["R1.2: a figure unchanged"] += 1
            return
        gold = {(True, True): "both rose", (False, False): "both fell",
                (True, False): "revenue rose and operating income fell", (False, True): "revenue fell and operating income rose"}[(dr > 0, do > 0)]
        opts = ["both rose", "both fell", "revenue rose and operating income fell", "revenue fell and operating income rose"]
        ask = (f"how did total revenue and operating income (loss) move in the {self.period}, compared with the same period a "
               "year earlier? A smaller operating loss counts as a rise in operating income. Answer with exactly one of: "
               + ", ".join(opts) + ". " + TAIL)
        self.emit("R1.2", "base", ask, gold, [rev["line"], oi["line"]],
                  {"figures": [self.step(rev), self.step(oi)], "revenue_change": dr, "operating_income_change": do},
                  "label", options=opts, hint="Compare each line with the same period a year earlier.")

    def _fs(self, template, a, b, name_a, name_b, hint):
        lab, why = faster_or_slower(a, b)
        if lab is None:
            self.why[f"{template}: {why}"] += 1
            return
        ga, gb = 100 * (a["cur"] / a["prior"] - 1), 100 * (b["cur"] / b["prior"] - 1)
        steps = {"figures": [self.step(a), self.step(b)], "growth_a": round(ga, 4), "growth_b": round(gb, 4)}

        def ask(x, y):
            return (f"compared with the same period a year earlier, did its {x} grow faster or slower than its {y} in the "
                    f"{self.period}? Compare growth rates in percent; growth can be negative, and a smaller decline counts as faster "
                    "growth. Answer with exactly one of: faster, slower. " + TAIL)
        base = self.emit(template, "base", ask(name_a, name_b), lab, [a["line"], b["line"]], steps, "label",
                         options=["faster", "slower"], hint=hint)
        if base:
            m = self.emit(template, "mirror", ask(name_b, name_a), "slower" if lab == "faster" else "faster",
                          [a["line"], b["line"]], steps, "label", options=["faster", "slower"], hint=hint)
            if m:
                m["family"], m["twin_of"], m["twin"] = "R2", base["id"], "mirror"

    def r13(self):
        rev = self.P.get("revenue")
        ox = self.P.get("opex") or self.P.get("costs_expenses")
        if rev and ox:
            self._fs("R1.3", ox, rev, R_METRICS[ox["metric"]]["name"], "total revenue",
                     "Growth = (this year / last year - 1) x 100, for each line.")

    def r14(self):
        eps, ni = self.P.get("eps_diluted"), self.P.get("net_income")
        if eps and ni:
            self._fs("R1.4", eps, ni, "diluted earnings per share", "net income attributable to the company",
                     "Growth = (this year / last year - 1) x 100; EPS grows faster than net income when the diluted share count falls.")

    def r15(self):
        ni, pt = self.P.get("net_income"), self.P.get("pretax")
        if ni and pt:
            self._fs("R1.5", ni, pt, "net income attributable to the company", "income before income taxes",
                     "Growth = (this year / last year - 1) x 100; net income grows faster than pre-tax income when the tax rate falls.")

    def r16(self):
        cands = [m for m in ("cost_of_revenue", "gross_profit", "rd", "sga") if m in self.P]
        if len(cands) < 3:
            return
        ch = {m: abs(self.P[m]["cur"] - self.P[m]["prior"]) for m in cands}
        top = sorted(cands, key=lambda m: -ch[m])
        if ch[top[0]] == 0 or ch[top[1]] >= 0.95 * ch[top[0]]:
            self.why["R1.6: top two within 5%"] += 1
            return
        names = [R_METRICS[m]["name"] for m in cands]
        ask = (f"which of these lines changed the most in US dollars (the size of the change, up or down) in the {self.period}, "
               "compared with the same period a year earlier: " + "; ".join(names) + "? Answer with exactly one of: "
               + "; ".join(names) + ". " + TAIL)
        self.emit("R1.6", f"{len(cands)}lines", ask, R_METRICS[top[0]]["name"], [self.P[m]["line"] for m in cands],
                  {"figures": [self.step(self.P[m]) for m in cands], "changes": {m: ch[m] for m in cands}},
                  "label", options=names, hint="Change = this year - last year for each line; compare their sizes.")

    def r17(self):
        if self.kind != "quarter":
            return
        for m in ("revenue", "operating_income", "net_income"):
            p = self.P.get(m)
            cur = value_for(self.gaap, m, self.start, self.end, self.t["filing_date"])
            if not p or not cur:
                continue
            for months, dur in ((6, (170, 195)), (9, (260, 285))):
                ytd = value_for(self.gaap, m, None, self.end, self.t["filing_date"], dur=dur)
                if ytd is None:
                    continue
                hits = [(k, v, d) for k, (v, d, g) in enumerate(p["vals"]) if k not in (p["col"], p["prior_col"])
                        and E.matches(v, d, g, p["scale"], ytd[0], False)]
                if not hits:
                    self.why[f"R1.7: {months}-month total not in the row"] += 1
                    continue
                k, v, d = hits[0]
                earlier_end = E.dt.date.fromisoformat(self.start) - E.dt.timedelta(days=1)
                ed = earlier_end.isoformat()
                if months == 6:
                    ref = value_for(self.gaap, m, None, ed, self.t["filing_date"], first_filed_any=True, dur=(80, 100))
                    per = f"three months ended {E.long_date(ed)}"
                else:
                    ref = value_for(self.gaap, m, None, ed, self.t["filing_date"], first_filed_any=True, dur=(170, 195))
                    per = f"six months ended {E.long_date(ed)}"
                if ref is None:
                    self.why[f"R1.7: no XBRL value for the earlier period ({months})"] += 1
                    continue
                derived = (v - p["shown"]) * p["scale"]
                slack = 0.5 * 10 ** (-d) * p["scale"] + half_unit(p)
                if abs(derived - ref[0]) > slack + 1e-6:
                    self.why[f"R1.7: difference disagrees with XBRL ({months})"] += 1
                    continue
                ask_scale = "millions" if p["scale"] >= 1e6 else self.rng.choice(["millions", "thousands"])
                gold = derived / E.SCALES[ask_scale]
                tol = {"abs": round(slack / E.SCALES[ask_scale] * 1.01, 6)}
                ask = (f"what was its {R_METRICS[m]['name']} for the {per}? Give the answer in {ask_scale} of US dollars. "
                       f"{SIGN} " + TAIL)
                self.emit("R1.7", f"{m}:{months}m", ask, gold, [p["line"]],
                          {"figures": [self.step(p)], "ytd_shown": v, "ytd_months": months, "quarter_shown": p["shown"],
                           "xbrl_earlier": ref[0]}, "number", tol=tol,
                          hint=f"The {months}-month total minus the latest three months gives the earlier period.",
                          extra={"asked_scale": ask_scale, "table_scale": p["scale"]})
                break

    def r18(self):
        rev = self.P.get("revenue")
        for name, num in (("gross", "gross_profit"), ("operating", "operating_income")):
            if rev is None or num not in self.P or rev["prior"] <= 0 or rev["cur"] <= 0:
                continue
            n = self.P[num]
            d = margin(n, rev, "cur") - margin(n, rev, "prior")
            ask = (f"by how many percentage points did its {name} margin ({name} {'profit' if name == 'gross' else 'income'} "
                   f"as a percentage of total revenue) change in the {self.period}, compared with the same period a year "
                   f"earlier? Give the answer in percentage points, one decimal place. {SIGN} " + TAIL)
            self.emit("R1.8", name, ask, round(d, 4), [rev["line"], n["line"]],
                      {"figures": [self.step(rev), self.step(n)], "change_points": round(d, 4)}, "number", tol={"abs": 0.15},
                      hint=f"{name.capitalize()} margin = {name} {'profit' if name == 'gross' else 'income'} / total revenue x 100, for each year; subtract.")

    def r19(self):
        rev = self.P.get("revenue")
        if rev is None:
            return
        y2 = str(int(self.end[:4]) - 2)
        back = f"{'three months' if self.kind == 'quarter' else 'fiscal year'} ended {E.long_date(E.shift_year(E.shift_year(self.end)))}"
        ask = f"what was its total revenue for the {back}? Give the answer in millions of US dollars. {SIGN} " + TAIL
        it = self.emit("R1.9", "two_years_back", ask, UNDETERMINED, [rev["line"]], {"figures": [self.step(rev)]}, "undetermined")
        if it and y2 in it["excerpt"]:
            self.items.remove(it)
            self.why["R1.9: the earlier year appears in the excerpt"] += 1
        ask = (f"what was its research and development expense for the {self.period}? Give the answer in millions of US "
               f"dollars. {SIGN} " + TAIL)
        it = self.emit("R1.9", "absent_line", ask, UNDETERMINED, [rev["line"]], {"figures": [self.step(rev)]}, "undetermined")
        if it and re.search(r"research", it["excerpt"], re.I):
            self.items.remove(it)
            self.why["R1.9: the excerpt mentions research"] += 1


# ---------------------------------------------------------------------------------------------
# Twins and the identity checker

def identity_ok(excerpt):
    """Gross profit = revenue - cost of revenue in every column where all three rows are present.
    Returns True, False, or None when the check does not apply."""
    lines = excerpt.split("\n")
    rows = E.table_rows(lines)
    pick = {}
    for m in ("revenue", "cost_of_revenue", "gross_profit"):
        for i, label, vals in rows:
            if R_METRICS[m]["label"].search(label) and not re.search(r"per\s+share|%", label, re.I):
                pick.setdefault(m, vals)
    if len(pick) < 3:
        return None
    n = min(len(v) for v in pick.values())
    if n == 0:
        return None
    for k in range(n):
        r, c, g = (pick[m][k] for m in ("revenue", "cost_of_revenue", "gross_profit"))
        tol = 10 ** (-min(r[1], c[1], g[1])) * 1.5
        if abs(abs(r[0]) - abs(c[0]) - g[0]) > tol:
            return False
    return True


YEAR2 = re.compile(r"(?<![\d])(?:(?<=Q[1-4]\s)|(?<=Q[1-4]')|(?<=[1-4]Q)|(?<=FY)|(?<=FY\s)|(?<=FY'))(\d{2})(?!\d)")


def swap_years(excerpt, need_first_line_text, year):
    """Swap ``year`` and ``year - 1`` in the column-heading lines above the first needed row."""
    lines = excerpt.split("\n")
    first = next((k for k, l in enumerate(lines) if l.rstrip() == need_first_line_text.rstrip()), None)
    if first is None:
        return None
    y, p = str(year), str(year - 1)
    s2y, s2p = y[2:], p[2:]
    heads = [k for k in range(first) if E1.PTOK.search(lines[k])]
    def n_of(full, short):
        return sum(len(re.findall(rf"(?<!\d){full}(?!\d)", lines[k])) + YEAR2.findall(lines[k]).count(short) for k in heads)
    cy, cp = n_of(y, s2y), n_of(p, s2p)
    if cy == 0 or cy != cp:
        return None

    def sw(line):
        line = re.sub(rf"(?<!\d)({y}|{p})(?!\d)", lambda m: p if m.group(1) == y else y, line)
        return YEAR2.sub(lambda m: s2p if m.group(1) == s2y else s2y if m.group(1) == s2p else m.group(1), line)
    for k in heads:
        lines[k] = sw(lines[k])
    return "\n".join(lines)


FLIP = {"expanded": "contracted", "contracted": "expanded", "both rose": "both fell", "both fell": "both rose",
        "revenue rose and operating income fell": "revenue fell and operating income rose",
        "revenue fell and operating income rose": "revenue rose and operating income fell",
        "faster": "slower", "slower": "faster"}


def make_twins(base, src_lines, rng, why):
    out = []
    ok0 = identity_ok(base["excerpt"])
    first_text = src_lines[base["need_lines"][0]]
    if base["template"] in ("R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.8") and base["variant"] != "mirror" and base["gold"] != "flat":
        sw = swap_years(base["excerpt"], first_text, int(base["period"]["end"][:4]))
        if sw is None:
            why[f"flip {base['template']}: heading years not symmetric"] += 1
        elif ok0 is True and identity_ok(sw) is False:
            why[f"flip {base['template']}: identity rejected"] += 1
        else:
            gold = round(-base["gold"], 4) if base["kind"] == "number" else FLIP[base["gold"]]
            out.append({**base, "id": hashlib.sha256(f"{base['id']}|flip".encode()).hexdigest()[:16], "family": "R2",
                        "twin_of": base["id"], "twin": "flip", "excerpt": sw, "gold": gold})
    # hold: an employee-count row laid out like the first needed row
    lines = base["excerpt"].split("\n")
    k = next((j for j, l in enumerate(lines) if l.rstrip() == first_text.rstrip()), None)
    if k is not None:
        tmpl = lines[k]
        m = re.search(r"(\s{2,}|\$|\t)", tmpl.strip())
        label_len = len(tmpl) - len(tmpl.lstrip()) + (m.start() if m else 0)
        a = rng.randint(1500, 60000)
        vals = [a] + [round(a * rng.uniform(0.9, 1.1)) for _ in range(40)]
        it = iter(vals)
        body = re.sub(r"\(?-?\$?\s?\d[\d,]*(?:\.\d+)?\)?", lambda _: f"{next(it, a):,}", tmpl[label_len:])
        body = body.replace("$", " ")
        indent = len(tmpl) - len(tmpl.lstrip())
        row = (" " * indent + "Employees at end of period").ljust(label_len) + body
        held = "\n".join(lines + [row])  # after the last row, where supplementary data sits
        if ok0 is True and identity_ok(held) is False:
            why[f"hold {base['template']}: identity rejected"] += 1
        else:
            out.append({**base, "id": hashlib.sha256(f"{base['id']}|hold".encode()).hexdigest()[:16], "family": "R2",
                        "twin_of": base["id"], "twin": "hold", "excerpt": held})
    return out


# ---------------------------------------------------------------------------------------------

def build(a):
    if not E.DRIVE.exists():
        sys.exit("external drive not mounted")
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(glob.glob(f"{E.TOKENIZER}/snapshots/*/tokenizer.json")[0])
    count = lambda s: len(tok.encode(s).ids)  # noqa: E731
    targets = json.loads((E.PAIRS / "targets.json").read_text(encoding="utf-8"))
    group_of = split_v1.groups((t["accession"], t["cik"]) for t in targets)
    flags = {json.loads(l)["accession"]: json.loads(l) for l in open(E.PAIRS / "flags_v2.jsonl", encoding="utf-8")}
    sides = set(a.sides.split(","))
    facts = E.Facts()
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    seen, out = set(), collections.defaultdict(list)
    why = {s: collections.Counter() for s in sides}
    cache_cik, gaap = None, {}
    for t in sorted(targets, key=lambda t: (t["cik"], t["acceptance"])):
        if t["accession"] not in flags or t["accession"] in seen:
            continue
        seen.add(t["accession"])
        s = E.side_of(t, group_of)
        if s is None or s not in sides:
            continue
        path = E.TEXTS / f"{t['cik']}_{t['accession']}.txt"
        if not path.exists():
            why[s]["release: no text"] += 1
            continue
        if t["cik"] != cache_cik:
            cache_cik, gaap = t["cik"], facts.load(t["cik"])
        if not gaap:
            why[s]["release: no company facts"] += 1
            continue
        b = Builder(t, path.read_text(encoding="utf-8"), gaap, count, rng, s, why[s])
        why[s][f"release: {b.build()}"] += 1
        twins = []
        for it in b.items:
            if it["family"] == "R1":
                twins.extend(make_twins(it, b.lines, rng, why[s]))
        out[s].extend(b.items + twins)
    report = {}
    for s in sorted(sides):
        items = out[s]
        with open(OUT / f"items_{s}.jsonl", "w", encoding="utf-8") as fh:
            for it in items:
                fh.write(json.dumps(it) + "\n")
        base = [i for i in items if i["family"] == "R1"]
        r = {"items": len(items), "base items": len(base), "companies (base)": len({i["cik"] for i in base}),
             "releases with a base item": len({i["accession"] for i in base}),
             "sha256_of_ids": hashlib.sha256("".join(i["id"] for i in items).encode()).hexdigest(),
             "base by template": dict(sorted(collections.Counter(i["template"] for i in base).items())),
             "base by template and variant": dict(sorted(collections.Counter(f"{i['template']}:{i['variant']}" for i in base).items())),
             "companies by template": {t: len({i["cik"] for i in base if i["template"] == t}) for t in sorted({i["template"] for i in base})},
             "twins": dict(sorted(collections.Counter(f"{i['template']}:{i['twin']}" for i in items if i["family"] == "R2").items())),
             "labels": {t: dict(collections.Counter(i["gold"] for i in base if i["template"] == t and i["kind"] == "label"))
                        for t in ("R1.1", "R1.2", "R1.3", "R1.4", "R1.5", "R1.6")},
             "R1.8 change points, quartiles": None,
             "excerpt tokens median / p90 / max": None,
             "identity check on base excerpts": dict(collections.Counter(str(identity_ok(i["excerpt"])) for i in base)),
             "dropped": dict(sorted(why[s].items()))}
        ch = sorted(i["gold"] for i in base if i["template"] == "R1.8")
        if ch:
            r["R1.8 change points, quartiles"] = [round(ch[len(ch) // 4], 2), round(ch[len(ch) // 2], 2), round(ch[3 * len(ch) // 4], 2)]
        tk = sorted(i["excerpt_tokens"] for i in base)
        if tk:
            r["excerpt tokens median / p90 / max"] = [tk[len(tk) // 2], tk[9 * len(tk) // 10], tk[-1]]
        report[s] = r
    (OUT / f"yield_{'_'.join(sorted(sides))}.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


def show(a):
    if a.side == "test":
        sys.exit("refused: test items are not read")
    items = [json.loads(l) for l in open(OUT / f"items_{a.side}.jsonl", encoding="utf-8")]
    items = [i for i in items if (not a.template or i["template"] == a.template) and (not a.twin or i.get("twin") == a.twin)
             and (a.twin or i["family"] == "R1")]
    rng = random.Random(a.seed)
    for it in rng.sample(items, min(a.n, len(items))):
        print("=" * 110)
        print(it["id"], it["template"], it["variant"], it.get("twin"), it["company"], it["period"], "GOLD:", it["gold"], it["tolerance"])
        print("Q:", it["question"])
        print("STEPS:", json.dumps(it["steps"])[:600])
        print(it["excerpt"])


def check(_):
    """Fixed cases for the rules and the year swap."""
    def P(cur, prior, dec=0, scale=1e6, pdec=None):
        return {"cur": cur * scale, "prior": prior * scale, "dec": dec, "prior_dec": dec if pdec is None else pdec, "scale": scale}
    cases = [
        (faster_or_slower(P(110, 100), P(105, 100))[0], "faster"),
        (faster_or_slower(P(102, 100), P(105, 100))[0], "slower"),
        (faster_or_slower(P(1.03, 1.00, 2, 1.0), P(1030, 1000))[0], None),  # within 0.5 points? 3.0 vs 3.0
        (faster_or_slower(P(0.52, 0.50, 2, 1.0), P(103, 100))[0], None),     # rounding of EPS can flip
        (faster_or_slower(P(-5, 10), P(3, 2))[0], None),
    ]
    bad = [(i, got, want) for i, (got, want) in enumerate(cases) if got != want]
    ex = "Three Months Ended\nSeptember 30,\n2026      2025\nRevenue   $ 120   $ 100"
    sw = swap_years(ex, "Revenue   $ 120   $ 100", 2026)
    ex2 = "Q3 FY26   Q3 FY25   Q2 FY26\nRevenue   120   100   110"
    sw2 = swap_years(ex2, "Revenue   120   100   110", 2026)
    ex3 = "Q3 2026  Q2 2026  Q1 2026  Q4 2025  Q3 2025\nRevenue  1  2  3  4  5"
    sw3 = swap_years(ex3, "Revenue  1  2  3  4  5", 2026)
    print("rule cases:", len(cases), "failures:", bad)
    print("swap 1:", repr(sw.split("\n")[2]) if sw else None, "(want '2025      2026')")
    print("swap 2:", sw2, "(want None: unequal years)")
    print("swap 3:", sw3, "(want None: five quarterly columns)")
    print("identity:", identity_ok("Revenue    100   90\nCost of revenue   60   50\nGross profit   40   40"), "(want True)",
          identity_ok("Revenue    100   90\nCost of revenue   60   50\nGross profit   45   40"), "(want False)")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build"); b.add_argument("--sides", default="train,dev"); b.set_defaults(fn=build)
    s = sub.add_parser("show"); s.add_argument("--side", default="dev"); s.add_argument("--template", default="")
    s.add_argument("--twin", default=""); s.add_argument("--n", type=int, default=5); s.add_argument("--seed", type=int, default=0)
    s.set_defaults(fn=show)
    sub.add_parser("check").set_defaults(fn=check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
