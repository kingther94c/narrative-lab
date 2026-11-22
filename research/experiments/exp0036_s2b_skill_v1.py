"""EXP-0036: code-stated facts, the analyst skill v1, and a blinded brief, on clean episodes (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0036 (2026-11-22). 197 clean
episodes (the 500 largest training and development companies) and EXP-0026's 60 old ones; four
labels (revenue acceleration; gross margin, operating margin and net income up year on year next
quarter). Calls:

- R  (reader): the raw release; fills skill v1's form (EXP-0032's form plus what recurs and what
  does not, exit rate, inventory and channel, management language). No probability asked.
- A0: raw release, skill v1's considerations block and four questions.
- A1: A0 plus facts computed by code (``facts``).
- B : the code facts and the code-rendered form, no release text.
- K  (attacker, EXP-0028's question) on B, for the 60 old and EXP-0026's 30 clean episodes.

    conda run --no-capture-output -n nlab python research/experiments/exp0036_s2b_skill_v1.py prepare
    (emit, run with exp0027, ingest: run exp0036, items_r and items_a0)
    conda run --no-capture-output -n nlab python research/experiments/exp0036_s2b_skill_v1.py build
    (emit, run, ingest: items_cb)
    conda run --no-capture-output -n nlab python research/experiments/exp0036_s2b_skill_v1.py score
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
import statistics
import sys
import zipfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0005_earnings_exam as e5  # noqa: E402
import exp0020_s2a_episodes as e20  # noqa: E402
import exp0022_s2a_sanitiser as e22  # noqa: E402
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402
import exp0029_s2b_rationale_audit as e29  # noqa: E402
import exp0030_s2b_guided_redaction as e30  # noqa: E402
import exp0031_s2b_rewrite as e31  # noqa: E402
import exp0032_s2b_rewrite_v2 as e32  # noqa: E402
import exp0034_s2a_base_effect as e34  # noqa: E402
import exp0035_s2a_accounting_screen as e35  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0036"
RUN = "exp0036"
SEED = 20261131
CUTOFF = "2026-06-30"
TOP = 500
SKILL = Path(__file__).resolve().parents[1] / "design" / "s2_analyst_skill.md"
LABELS = ("revenue", "gross_margin", "operating_margin", "net_income")
MARGIN_BAND, INCOME_BAND = 0.0025, 0.02


def considerations() -> tuple[str, str]:
    t = SKILL.read_text(encoding="utf-8")
    block = t.split("<!-- SKILL-V1-CONSIDERATIONS-START -->", 1)[1].split("<!-- SKILL-V1-CONSIDERATIONS-END -->", 1)[0].strip()
    return block, hashlib.sha256(block.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------------------------
# Prompts

RECUR_LINES = ("revenue", "gross margin", "operating costs", "non-operating", "tax", "net income")
RECUR_KINDS = ("acquisition or divestiture", "currency", "calendar or extra week", "one-time or catch-up revenue",
               "buying ahead or stocking", "disruption or outage", "gain or loss on investments or asset sales",
               "restructuring or impairment", "litigation or settlement", "tax item", "pricing action", "input costs", "other")
RECUR_NEXT = ("recurs", "does not recur", "partly", "starts next quarter", "unknown")
EXIT = ("above the quarter's average", "below the quarter's average", "not stated")
CHANNEL = ("building", "reducing", "normal", "not stated")
LANG = {"hedging": ("notable", "some", "little"), "extreme_negative_words": ("present", "absent"),
        "tone_against_numbers": ("gloomier than the numbers", "in line", "more upbeat than the numbers")}

_intro_old = "You are preparing a standardised summary of an earnings release for an analyst who will forecast whether the company's year-on-year revenue growth next quarter will be higher or lower than in the quarter reported."
_tail_old = ' "quotes": {"<field>": "<quote>"},'
_rule_old = "- Name nothing anywhere: no company, product, person, place or date.\n"
assert _intro_old in e32.E_PROMPT and _tail_old in e32.E_PROMPT and _rule_old in e32.E_PROMPT
R_PROMPT = (e32.E_PROMPT
            .replace(_intro_old, "You are preparing a standardised summary of an earnings release for an analyst who will forecast, for the next quarter, whether the company's year-on-year revenue growth will be higher or lower than in the quarter reported, and whether its gross margin, operating margin and net income will be higher than a year earlier. The analyst needs to know what in this quarter will recur and what will not.")
            .replace(_rule_old, _rule_old
                     + "- Recurrence: at most six entries, for items the release says raised or lowered this quarter's revenue, gross margin, operating costs, non-operating result, tax or net income, and whether the release indicates they will recur next quarter (\"starts next quarter\" for an effect it says begins then). size_points: the effect on this quarter's year-on-year growth or margin in points, only if stated. Quote each entry as \"recurrence.0\" and so on.\n"
                     + "- exit_rate and inventory_channel need a quote; management_language is your reading of the management quotes and commentary, without a quote.\n")
            .replace(_tail_old, ' "recurrence": [{"line": "<' + " | ".join(RECUR_LINES) + '>", "kind": "<' + " | ".join(RECUR_KINDS)
                     + '>", "effect_this_quarter": "<raised | lowered>", "next_quarter": "<' + " | ".join(RECUR_NEXT) + '>", "size_points": <number or null>}],\n'
                     + ' "exit_rate": "<' + " | ".join(EXIT) + '>",\n'
                     + ' "inventory_channel": "<' + " | ".join(CHANNEL) + '>",\n'
                     + ' "management_language": {' + ", ".join(f'"{k}": "<{" | ".join(v)}>"' for k, v in LANG.items()) + '},\n'
                     + _tail_old))

QUESTIONS = """Questions about the NEXT fiscal quarter, each against the same quarter a year earlier:
1. Will next quarter's year-on-year revenue growth be HIGHER than the year-on-year revenue growth of the quarter {this}?
2. Will next quarter's gross margin be higher than in the same quarter a year earlier?
3. Will next quarter's operating margin be higher than in the same quarter a year earlier?
4. Will next quarter's net income be higher than in the same quarter a year earlier?
Part of what moved this quarter may be one-off and part may recur; judge what carries into next quarter.

Reply in exactly this format, the probabilities first:
P_REVENUE: <a whole number from 0 to 100: the probability that the answer to 1 is yes>
P_GROSS_MARGIN: <0 to 100, or NA if the company reports no gross margin>
P_OPERATING_MARGIN: <0 to 100, or NA if the company reports no operating income>
P_NET_INCOME: <0 to 100>
RATIONALE: <at most four sentences>"""

A_INTRO = "You are an analyst working for a portfolio manager. Below is an earnings release for one quarter of one company{facts_note}. Work with the text as it is given."
B_INTRO = ("You are an analyst working for a portfolio manager. Below are facts computed by code from earlier filings and from an earnings release for one quarter of one company, "
           "and a standardised summary of the release written by code from facts taken out of it. Names, dates and the release's own wording have been removed; work with what is given.")
PROB = {lab: re.compile(rf"P_{lab.upper()}:\s*(\d{{1,3}}|NA)", re.I) for lab in LABELS}

A_PROMPT = e31.A_PROMPT.replace("ratios from earlier filings and a standardised summary", "facts computed by code from earlier filings and a standardised summary")
assert A_PROMPT != e31.A_PROMPT


def pm_prompt(arm: str, release: str | None, facts: str | None, brief: str | None) -> str:
    block, _ = considerations()
    if arm == "b":
        head = B_INTRO + "\n\n" + QUESTIONS.format(this="the summary reports")
        body = "Facts computed by code:\n" + facts + "\n\nThe summary:\n\n" + brief
    else:
        head = A_INTRO.format(facts_note=", and facts computed by code from earlier filings and from this release" if facts else "") + "\n\n" + QUESTIONS.format(this="this release reports")
        body = ("Facts computed by code:\n" + facts + "\n\n" if facts else "") + "The earnings release:\n\n" + release
    return head + "\n\n" + block + "\n\n" + body


# ---------------------------------------------------------------------------------------------
# Episodes and labels


def release_text(ep: dict) -> str:
    return e22.clean(e22.text_path(ep).read_text(encoding="utf-8"))


def at_back(series: list[dict], quarter_end: str, k: int) -> dict | None:
    for r in series:
        if e22.quarters_between(r["end"], quarter_end) == k:
            return r
    return None


def ratio(num, den):
    return None if num is None or not den or den <= 0 else num / den


def gross(x: dict, rev: float | None, ya: bool) -> float | None:
    s = "_ya" if ya else ""
    if x.get("gross_profit" + s) is not None:
        return x["gross_profit" + s]
    return rev - x["cost_of_revenue" + s] if x.get("cost_of_revenue" + s) is not None and rev else None


def line_values(r: dict, x: dict) -> dict:
    """Margins and net income of one series quarter and of its year-ago quarter, same filing."""
    return {"gp": gross(x, r["rev"], False), "oi": r.get("operating_income"),
            "gm": ratio(gross(x, r["rev"], False), r["rev"]), "gm_ya": ratio(gross(x, r["rev_prior"], True), r["rev_prior"]),
            "om": ratio(r.get("operating_income"), r["rev"]), "om_ya": ratio(r.get("operating_income_prior"), r["rev_prior"]),
            "ni": r.get("net_income"), "ni_ya": r.get("net_income_prior")}


def up(v: dict, line: str) -> bool | None:
    a, b = v.get(line), v.get(line + "_ya")
    if a is None or b is None:
        return None
    if line == "ni":
        return None if abs(a - b) <= INCOME_BAND * abs(b) else a > b
    return None if abs(a - b) <= MARGIN_BAND else a > b


def pool() -> tuple[dict, list[dict]]:
    """Per company, line values of every series quarter; and every EXP-0020 episode with its
    labels, comparison base and code-baseline inputs (for reference rates and baselines)."""
    path = OUT / "pool.json"
    if path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        return {tuple(k.split("|")): v for k, v in d["lines"].items()}, d["episodes"]
    by = e20.load_series()
    zf = zipfile.ZipFile(e20.FACTS_ZIP)
    lines: dict[tuple[str, str], dict] = {}
    for n, (cik, recs) in enumerate(sorted(by.items())):
        gaap = json.loads(zf.read(f"CIK{cik}.json")).get("facts", {}).get("us-gaap", {})
        xs = e35.items(gaap, recs)
        for r in recs:
            lines[(cik, r["end"])] = {**line_values(r, xs[r["end"]]), **{k: xs[r["end"]][k] for k in ("inventory", "inventory_ya", "contract_liab", "contract_liab_ya")}}
        if n % 300 == 0:
            print(f"[pool] {n}/{len(by)} companies", flush=True)
    eps = []
    for ep in e20.episodes(by):
        recs = by[ep["cik"]]
        back = {e22.quarters_between(r["end"], ep["end"]): r for r in recs if r["end"] <= ep["end"]}
        g = [back[k]["g"] if k in back and back[k]["g"] is not None else None for k in range(5)]
        cur, nxt = lines.get((ep["cik"], ep["end"]), {}), lines.get((ep["cik"], ep["next_end"]), {})
        b3 = lines.get((ep["cik"], back[3]["end"]), {}) if 3 in back else {}
        eps.append({"cik": ep["cik"], "end": ep["end"], "filed": ep["filed"], "next_filed": ep["next_filed"], "g": g,
                    "y": {"revenue": ep["y_accelerates"], "gross_margin": up(nxt, "gm"), "operating_margin": up(nxt, "om"), "net_income": up(nxt, "ni")},
                    "x": {"gross_margin": up(cur, "gm"), "operating_margin": up(cur, "om"), "net_income": up(cur, "ni")},
                    "chg": {"gross_margin": diff(cur, "gm"), "operating_margin": diff(cur, "om"), "net_income": growth(cur)},
                    "base": {"gross_margin": diff(b3, "gm"), "operating_margin": diff(b3, "om"), "net_income": growth(b3)}})
    OUT.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"lines": {"|".join(k): v for k, v in lines.items()}, "episodes": eps}), encoding="utf-8")
    return lines, eps


def diff(v: dict, line: str) -> float | None:
    a, b = v.get(line), v.get(line + "_ya")
    return None if a is None or b is None else max(-0.5, min(0.5, a - b))


def growth(v: dict) -> float | None:
    a, b = v.get("ni"), v.get("ni_ya")
    return None if a is None or b is None or b <= 0 else max(-1.0, min(2.0, a / b - 1))


def chosen() -> list[dict]:
    """60 old (EXP-0026, key order), then the clean episodes of the 500 largest companies."""
    by = e20.load_series()
    ranked = sorted(by, key=lambda c: -max(r["rev"] for r in by[c][-4:]))
    rank = {c: i for i, c in enumerate(ranked)}
    lab = {(e["cik"], e["end"]): e for e in e26.load(e26.DRIVE / "s2" / "exp0020" / "labels.jsonl")}
    k26 = e26.load(e26.OUT / "key.jsonl")
    out = [{"group": "old", "cik": k["cik"], "accession": k["accession"], "filing_date": k["filing_date"],
            "quarter_end": k["quarter_end"], "rank": rank.get(k["cik"]), "e26": k["episode"]} for k in k26 if k["group"] == "old"]
    clean = []
    for r in e26.load(e22.LIST):
        if not (r["post_cutoff"] and r["labelled"] and r["on_drive"]) or rank.get(r["cik"], 10**6) >= TOP:
            continue
        e = lab.get((r["cik"], r["quarter_end"]))
        if not e or e["y_accelerates"] is None or e22.text_path(r) is None:
            continue
        t = e22.text_path(r).read_text(encoding="utf-8")
        if len(t) > e26.MAX_CHARS or not e26.EARNINGS.search(t):
            continue
        e26n = next((k["episode"] for k in k26 if k["accession"] == r["accession"]), None)
        clean.append({"group": "clean", "cik": r["cik"], "accession": r["accession"], "filing_date": r["filing_date"],
                      "quarter_end": r["quarter_end"], "rank": rank[r["cik"]], "e26": e26n})
    clean.sort(key=lambda r: r["accession"])
    out += clean
    for i, ep in enumerate(out):
        ep["i"] = i
    return out


def labels_for(ep: dict, eps_by: dict) -> dict:
    p = eps_by.get((ep["cik"], ep["quarter_end"]))
    return p["y"] if p else {lab: None for lab in LABELS}


# ---------------------------------------------------------------------------------------------
# Facts computed by code


def shown(v: float | None, text: str) -> bool:
    """Is this amount printed in the release (in units, thousands, millions or billions)?"""
    if v is None:
        return False
    a, flat = abs(v), text.replace(" ", " ")
    cands = {f"{round(a / 1e6):,}", f"{a / 1e6:,.1f}", f"{round(a / 1e3):,}", f"{a / 1e9:.1f} billion", f"{a / 1e9:.2f} billion", f"{round(a):,}"}
    for c in cands:
        if len(c.replace(",", "").replace(".", "")) < 3:
            continue
        if re.search(rf"(?<![\d,.]){re.escape(c)}(?![\d])", flat):
            return True
    return False


def p0(x: float) -> str:
    return f"{round(100 * x):d}%"


def p1(x: float) -> str:
    return f"{100 * x:.1f}%"


def bucket(d: float) -> tuple[str, float, float]:
    """d = g(t-4) - g(t-3): how much easier next quarter's comparison is, in growth points."""
    for lo, hi, text in ((0.10, 9, "lower by 10 points or more"), (0.03, 0.10, "lower by 3 to 10 points"),
                         (-0.03, 0.03, "within 3 points"), (-0.10, -0.03, "higher by 3 to 10 points"), (-9, -0.10, "higher by 10 points or more")):
        if lo <= d < hi:
            return text, lo, hi
    return "within 3 points", -0.03, 0.03


def facts(ep: dict, series: list[dict], lines: dict, eps: list[dict], form: dict | None, release: str) -> tuple[str, dict]:
    date, qe, cik = ep["filing_date"], ep["quarter_end"], ep["cik"]
    known = [r for r in series if r["filed"] < date]
    cur = next((r for r in series if r["end"] == qe), None)
    have_cur = cur is not None and shown(cur["rev"], release)
    g = [cur["g"] if have_cur else None] + [(at_back(known, qe, k) or {}).get("g") for k in range(1, 5)]
    S, used = [], collections.Counter()

    def gtxt(x):
        return "not available" if x is None else p0(x)

    S.append(f"- Revenue growth year on year: this quarter {gtxt(g[0])}; the four quarters before, most recent first: {', '.join(gtxt(x) for x in g[1:])}.")
    used["revenue_history"] += 1
    past = [p for p in eps if p["cik"] != cik and p["next_filed"] < date]
    if g[3] is not None and g[4] is not None:
        S.append(f"- The year-ago quarter that next quarter will be compared with had grown {p0(g[3])} on its own year-ago quarter; "
                 f"the year-ago quarter this quarter was compared with had grown {p0(g[4])}.")
        text, lo, hi = bucket(g[4] - g[3])
        ref = [p["y"]["revenue"] for p in past if p["y"]["revenue"] is not None and None not in (p["g"][3], p["g"][4]) and lo <= p["g"][4] - p["g"][3] < hi]
        if len(ref) >= 50:
            S.append(f"- In {len(ref):,} past episodes of other companies, outcomes known before this release, where the first of those two figures was {text} than the second, "
                     f"next-quarter growth came in higher than the reported quarter's in {p0(statistics.mean(ref))}.")
            used["revenue_reference"] += 1
        used["comparison_base"] += 1
    # margins and net income, with their own year-ago bases and reference rates
    lc = lines.get((cik, qe), {}) if cur else {}
    r3 = at_back(known, qe, 3)
    l3 = lines.get((cik, r3["end"]), {}) if r3 else {}
    names = {"gm": "Gross margin", "om": "Operating margin"}
    for line, lab in (("gm", "gross_margin"), ("om", "operating_margin")):
        num = lc.get("gp") if line == "gm" else lc.get("oi")
        if lc.get(line) is None or lc.get(line + "_ya") is None or not have_cur or not shown(num, release):
            continue
        s = f"- {names[line]}: {p1(lc[line])} this quarter against {p1(lc[line + '_ya'])} a year earlier"
        if l3.get(line) is not None and l3.get(line + "_ya") is not None:
            s += f"; in the year-ago quarter that next quarter will be compared with it was {p1(l3[line])}, against {p1(l3[line + '_ya'])} a year before that"
        S.append(s + ".")
        used[f"{lab}_history"] += 1
        x = up(lc, line)
        if x is not None:
            ref = [p["y"][lab] for p in past if p["x"][lab] == x and p["y"][lab] is not None]
            if len(ref) >= 50:
                S.append(f"- In {len(ref):,} past episodes of other companies where the {names[line].lower()} {'rose' if x else 'fell'} year on year in the reported quarter, "
                         f"it was higher year on year the next quarter in {p0(statistics.mean(ref))}.")
                used[f"{lab}_reference"] += 1
    if have_cur and lc.get("ni") is not None and lc.get("ni_ya") is not None and shown(lc["ni"], release):
        def chg(a, b):
            if b > 0:
                return f"changed {p0(a / b - 1)} year on year" if a >= 0 else "turned from a profit to a loss year on year"
            return "moved from a loss to a profit year on year" if a > 0 else ("narrowed its loss year on year" if a > b else "widened its loss year on year")
        s = f"- Net income {chg(lc['ni'], lc['ni_ya'])} this quarter"
        if l3.get("ni") is not None and l3.get("ni_ya") is not None:
            s += f"; in the year-ago quarter that next quarter will be compared with, it had {chg(l3['ni'], l3['ni_ya'])}"
        S.append(s + ".")
        used["net_income_history"] += 1
        x = up(lc, "ni")
        if x is not None:
            ref = [p["y"]["net_income"] for p in past if p["x"]["net_income"] == x and p["y"]["net_income"] is not None]
            if len(ref) >= 50:
                S.append(f"- In {len(ref):,} past episodes of other companies where net income {'rose' if x else 'fell'} year on year in the reported quarter, "
                         f"it was higher year on year the next quarter in {p0(statistics.mean(ref))}.")
                used["net_income_reference"] += 1
    # balance-sheet leads (EXP-0035)
    if have_cur and g[0] is not None:
        for item, label in (("inventory", "Inventory"), ("contract_liab", "Deferred revenue or contract liabilities")):
            a, b = lc.get(item), lc.get(item + "_ya")
            if a is not None and b and b > 0 and shown(a, release):
                S.append(f"- {label}: {p0(a / b - 1)} year on year at the end of the quarter, against revenue growth of {p0(g[0])}.")
                used[item] += 1
    # guidance arithmetic, from the reader's verified form
    if form:
        for tag, label in (("next_quarter", "next quarter's revenue"), ("full_year", "the fiscal year's revenue")):
            lo, hi = form.get(f"{tag}_guidance_growth_low"), form.get(f"{tag}_guidance_growth_high")
            if lo is None and hi is None:
                continue
            lo, hi = (lo if lo is not None else hi), (hi if hi is not None else lo)
            rng = f"{round(lo)}%" if round(lo) == round(hi) else f"{round(lo)}% to {round(hi)}%"
            S.append(f"- The company's guidance for {label} implies year-on-year growth of {rng}.")
            used[f"{tag}_guidance"] += 1
        rest = rest_of_year(form, series, known, cur if have_cur else None, qe)
        if rest:
            S.append(f"- Full-year guidance less the year to date implies revenue growth of {rest} year on year for the rest of the fiscal year after this quarter.")
            used["rest_of_year"] += 1
    return "\n".join(S), dict(used)


def rest_of_year(form: dict, series: list[dict], known: list[dict], cur: dict | None, qe: str) -> str | None:
    lo, hi = form.get("full_year_guidance_growth_low"), form.get("full_year_guidance_growth_high")
    if cur is None or (lo is None and hi is None):
        return None
    lo, hi = (lo if lo is not None else hi), (hi if hi is not None else lo)
    fy_ends = [r for r in known if r["form"] == "10-K" and r["end"] < qe]
    if not fy_ends:
        return None
    k = e22.quarters_between(fy_ends[-1]["end"], qe)
    if k not in (1, 2, 3):
        return None
    ytd = [cur] + [at_back(known, qe, j) for j in range(1, k)]
    ya_year = [at_back(known, qe, j) for j in range(k, k + 4)]  # the last completed fiscal year, four quarters
    ya_rest = [at_back(known, qe, 4 - m) for m in range(1, 4 - k + 1)]  # year-ago quarters of the rest of this year
    if any(r is None or not r.get("rev") for r in ytd + ya_year + ya_rest):
        return None
    base = sum(r["rev"] for r in ya_year)
    done = sum(r["rev"] for r in ytd)
    rest_base = sum(r["rev"] for r in ya_rest)
    vals = [100 * ((base * (1 + x / 100) - done) / rest_base - 1) for x in (lo, hi)]
    if not all(-50 < v < 100 for v in vals):
        return None
    return f"{round(vals[0])}%" if round(vals[0]) == round(vals[1]) else f"{round(vals[0])}% to {round(vals[1])}%"


# ---------------------------------------------------------------------------------------------
# Reader form


def verify_extra(j: dict, release: str, log: collections.Counter) -> dict:
    nd, quotes = e29.norm(release), j.get("quotes") or {}

    def quoted(f: str) -> bool:
        q = quotes.get(f)
        return isinstance(q, str) and bool(q.strip()) and e29.norm(q).strip(" .…\"'") in nd

    out: dict = {"recurrence": []}
    for n, x in enumerate((j.get("recurrence") or [])[:6]):
        if not isinstance(x, dict) or x.get("line") not in RECUR_LINES or x.get("kind") not in RECUR_KINDS \
                or x.get("effect_this_quarter") not in ("raised", "lowered") or x.get("next_quarter") not in RECUR_NEXT:
            log["recurrence_off_menu"] += 1
            continue
        if not quoted(f"recurrence.{n}"):
            log["recurrence_quote_not_found"] += 1
            continue
        size = x.get("size_points")
        size = float(size) if isinstance(size, (int, float)) and e31.num_in(float(size), quotes[f"recurrence.{n}"]) else None
        out["recurrence"].append({"line": x["line"], "kind": x["kind"], "effect_this_quarter": x["effect_this_quarter"],
                                  "next_quarter": x["next_quarter"], "size_points": size})
        log["recurrence_kept"] += 1
    for f, menu in (("exit_rate", EXIT), ("inventory_channel", CHANNEL)):
        v = j.get(f)
        out[f] = v if v in menu and (v == "not stated" or quoted(f)) else "not stated"
        log[f"{f}_kept" if out[f] != "not stated" else f"{f}_none"] += 1
    ml = j.get("management_language") if isinstance(j.get("management_language"), dict) else {}
    out["management_language"] = {k: (ml.get(k) if ml.get(k) in v else "not stated") for k, v in LANG.items()}
    return out


def render_b(v: dict) -> str:
    text = e32.render(v)
    L = ["", "What moved this quarter, and whether the release says it recurs:" if v["recurrence"] else "What moved this quarter: nothing stated"]
    for x in v["recurrence"]:
        size = f", about {round(abs(x['size_points']))} points" if x["size_points"] is not None else ""
        L.append(f"  {x['line']}: {x['kind']}, {x['effect_this_quarter']} this quarter{size}; next quarter: {x['next_quarter']}")
    ml = v["management_language"]
    L += [f"Exit rate: {v['exit_rate']}", f"Inventory and channel: {v['inventory_channel']}",
          f"Management language: hedging {ml['hedging']}; extreme negative words {ml['extreme_negative_words']}; tone {ml['tone_against_numbers']}"]
    return text + "\n" + "\n".join(L)


# ---------------------------------------------------------------------------------------------
# Steps


def replies() -> dict[str, str]:
    return {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / RUN) if r["canary_ok"]}


def prepare(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    _, digest = considerations()
    lines, eps = pool()
    eps_by = {(p["cik"], p["end"]): p for p in eps}
    key = []
    with open(OUT / "items_r_a0.jsonl", "w", encoding="utf-8") as fh:
        for ep in chosen():
            rel = release_text(ep)
            fh.write(json.dumps({"id": f"r{ep['i']:03d}", "agent": e26.PM, "prompt": R_PROMPT + rel}, ensure_ascii=False) + "\n")
            fh.write(json.dumps({"id": f"a{ep['i']:03d}", "agent": e26.PM, "prompt": pm_prompt("a0", rel, None, None)}, ensure_ascii=False) + "\n")
            key.append({**ep, "labels": labels_for(ep, eps_by)})
    with open(OUT / "key.jsonl", "w", encoding="utf-8") as fh:
        for k in key:
            fh.write(json.dumps(k) + "\n")
    cov = {lab: sum(k["labels"][lab] is not None for k in key if k["group"] == "clean") for lab in LABELS}
    rep = {"episodes": len(key), "old": sum(k["group"] == "old" for k in key), "clean": sum(k["group"] == "clean" for k in key),
           "clean_top250": sum(k["group"] == "clean" and k["rank"] < 250 for k in key),
           "clean_labels_defined": cov, "clean_revenue_accelerates": sum(bool(k["labels"]["revenue"]) for k in key if k["group"] == "clean"),
           "skill_block_sha256_16": digest}
    (OUT / "prepare_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def build(_: argparse.Namespace) -> None:
    e23.need_drive()
    got = replies()
    lines, eps = pool()
    series = e22.load_series()
    key = e26.load(OUT / "key.jsonl")
    out, tot, bad = {}, collections.Counter(), []
    for k in key:
        i = k["i"]
        rel = release_text(k)
        j = e31.as_json(got.get(f"r{i:03d}", ""))
        form = None
        if j is not None:
            v, log = e31.verify(j, rel)
            b = e32.bases(series.get(k["cik"], []), k["quarter_end"])
            for tag, f in (("next_quarter", "next_quarter_revenue_guidance_amount"), ("full_year", "full_year_revenue_guidance_amount")):
                if v[f"{tag}_guidance_growth_low"] is not None or v[f"{tag}_guidance_growth_high"] is not None:
                    v[f"{tag}_guidance_source"] = "stated"
                    continue
                lo, hi = e32.amount(j, f, rel, log)
                glo, ghi = e32.implied(lo, hi, b[tag], log, tag)
                if glo is not None:
                    v[f"{tag}_guidance_growth_low"], v[f"{tag}_guidance_growth_high"] = glo, ghi
                    v[f"{tag}_guidance_source"] = "implied"
            v.update(verify_extra(j, rel, log))
            tot.update(log)
            form = v
        else:
            bad.append(i)
        ftext, used = facts(k, series.get(k["cik"], []), lines, eps, form, rel)
        out[i] = {"facts": ftext, "facts_used": used, "form": form, "brief": render_b(form) if form else None}
        tot.update({f"facts_{a}": b for a, b in used.items()})
    (OUT / "built.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    n_b = 0
    with open(OUT / "items_cb.jsonl", "w", encoding="utf-8") as fh:
        for k in key:
            i, o = k["i"], out[k["i"]]
            rel = release_text(k)
            fh.write(json.dumps({"id": f"c{i:03d}", "agent": e26.PM, "prompt": pm_prompt("a1", rel, o["facts"], None)}, ensure_ascii=False) + "\n")
            if o["brief"] is None:
                continue
            n_b += 1
            fh.write(json.dumps({"id": f"b{i:03d}", "agent": e26.PM, "prompt": pm_prompt("b", None, o["facts"], o["brief"])}, ensure_ascii=False) + "\n")
            if k["group"] == "old" or k["e26"] is not None:
                text = "Facts computed by code:\n" + o["facts"] + "\n\nThe summary:\n\n" + o["brief"]
                fh.write(json.dumps({"id": f"k{i:03d}", "agent": e31.e28.AGENT, "prompt": A_PROMPT + text}, ensure_ascii=False) + "\n")
    rep = {"episodes": len(key), "reader_unparsed": bad, "briefs": n_b, "log": dict(tot)}
    (OUT / "build_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def score(_: argparse.Namespace) -> None:
    key = {k["i"]: k for k in e26.load(OUT / "key.jsonl")}
    got = replies()
    built = {int(i): b for i, b in json.loads((OUT / "built.json").read_text(encoding="utf-8")).items()}
    rng = random.Random(SEED)
    grp = {g: [i for i, k in key.items() if k["group"] == g] for g in ("old", "clean")}

    def prob(rid: str, lab: str) -> float | None:
        m = PROB[lab].search(got.get(rid, ""))
        if not m or m.group(1).upper() == "NA" or int(m.group(1)) > 100:
            return None
        return int(m.group(1)) / 100

    def ci(xs: list[float], ys: list[float] | None = None) -> dict:
        if not xs or (ys is not None and not ys):
            return {"n": len(xs)}
        est = statistics.mean(xs) - (statistics.mean(ys) if ys else 0)
        d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) - (statistics.mean(rng.choices(ys, k=len(ys))) if ys else 0) for _ in range(10_000))
        return {"est": round(est, 4), "ci90": [round(d[499], 4), round(d[9499], 4)], "n": len(xs), "n_ref": len(ys) if ys else None}

    # code baselines, fitted on episodes resolved before the cutoff
    lines, eps = pool()
    base_p = baselines(eps)
    out: dict = {"skill_block_sha256_16": considerations()[1], "build": json.loads((OUT / "build_summary.json").read_text())["log"]}
    arms = {"A0": "a", "A1": "c", "B": "b"}
    for lab in LABELS:
        o: dict = {}
        y = {i: key[i]["labels"][lab] for i in key}
        ro = {a: {i: (None if y[i] is None or prob(f"{p}{i:03d}", lab) is None else (prob(f"{p}{i:03d}", lab) if y[i] else 1 - prob(f"{p}{i:03d}", lab))) for i in key} for a, p in arms.items()}
        code = {i: base_p[lab].get((key[i]["cik"], key[i]["quarter_end"])) for i in key}
        ro["code"] = {i: (None if y[i] is None or code[i] is None else (code[i] if y[i] else 1 - code[i])) for i in key}
        for a in arms:
            ro[f"{a}+code"] = {i: (None if ro[a][i] is None or ro["code"][i] is None else (ro[a][i] + ro["code"][i]) / 2) for i in key}
        col = lambda g, d: [d[i] for i in grp[g] if d.get(i) is not None]  # noqa: E731
        pair = lambda a, b: [ro[a][i] - ro[b][i] for i in grp["clean"] if ro[a].get(i) is not None and ro[b].get(i) is not None]  # noqa: E731
        o["c1_A1_minus_A0_clean"] = (lambda c: {**c, "verdict": None if "est" not in c else "helps" if c["ci90"][0] > 0 else "hurts" if c["ci90"][1] < 0 else "undecided"})(ci(pair("A1", "A0")))
        c2 = ci(pair("B", "A1"))
        c2["verdict"] = None if "est" not in c2 else ("retains" if c2["est"] >= -0.03 and c2["ci90"][0] > -0.10 else "loses" if c2["ci90"][1] < 0 else "undecided")
        o["c2_B_minus_A1_clean"] = c2
        o["c4_gap_old_minus_clean"] = {a: ci(col("old", ro[a]), col("clean", ro[a])) for a in arms}
        o["c4_A1_gap_minus_A0_gap"] = round(o["c4_gap_old_minus_clean"]["A1"].get("est", 0) - o["c4_gap_old_minus_clean"]["A0"].get("est", 0), 4)
        o["c5_clean"] = {a: {"readout": ci(col("clean", ro[a])), "accuracy": ci([float(x > 0.5) for x in col("clean", ro[a]) if x != 0.5]),
                             "brier": ci([(1 - x) ** 2 for x in col("clean", ro[a])])} for a in ro}
        o["c5_clean_top250"] = {a: ci([ro[a][i] for i in grp["clean"] if key[i]["rank"] < 250 and ro[a].get(i) is not None]) for a in ro}
        o["mean_probability_clean"] = {a: (lambda xs: round(statistics.mean(xs), 3) if xs else None)(
            [prob(f"{p}{i:03d}", lab) for i in grp["clean"] if prob(f"{p}{i:03d}", lab) is not None]) for a, p in arms.items()}
        out[lab] = o
    # criterion 3: B as a replay input
    k26 = {x["episode"]: x for x in e26.load(e26.OUT / "key.jsonl")}
    hits = {i: e30.read(got[f"k{i:03d}"], k26[key[i]["e26"]]) for i in key if f"k{i:03d}" in got and key[i]["e26"] is not None}
    t1 = ci([float(h["top1"]) for h in hits.values()])
    out["c3_attacker_B"] = {"all": t1, "old": ci([float(hits[i]["top1"]) for i in grp["old"] if i in hits]),
                            "clean": ci([float(hits[i]["top1"]) for i in grp["clean"] if i in hits])}
    v1 = None if "est" not in t1 else "stopped" if t1["est"] <= 0.20 else "not stopped" if t1["est"] >= 0.50 else "undecided"
    gapB = out["revenue"]["c4_gap_old_minus_clean"]["B"]
    no_leak = "ci90" in gapB and gapB["ci90"][0] <= 0 <= gapB["ci90"][1]
    out["c3_verdict"] = {"attacker": v1, "no_leak_detected": no_leak, "usable_replay_input": v1 != "not stopped" and no_leak and out["revenue"]["c2_B_minus_A1_clean"].get("verdict") != "loses"}
    # criterion 6: BH across the secondary labels for criterion 1
    out["c6_secondary_bh"] = secondary_bh({lab: out[lab]["c1_A1_minus_A0_clean"] for lab in LABELS[1:]}, rng, key, got, arms, grp)
    out["c7_exploratory_recurrence"] = recurrence_check(key, built)
    (OUT / "score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def baselines(eps: list[dict]) -> dict[str, dict]:
    """Per label, a logistic regression on episodes resolved before the cutoff; probabilities for all."""
    out: dict[str, dict] = {}
    rows35 = {(r["cik"], r["end"]): r for r in e35.build()}
    nf = {(p["cik"], p["end"]): p["next_filed"] for p in eps}
    # L1: EXP-0035's combined design
    rows = list(rows35.values())

    def x1(r):
        g = list(np.clip(np.array(r["g"], dtype=float), -1, 2))
        ex = []
        for name in e35.FEATURES:
            v = r[name]
            ex += [0.0 if v is None else v, float(v is None)]
        return [1.0] + g + ex

    tr = [r for r in rows if nf.get((r["cik"], r["end"]), "9999") <= CUTOFF]
    w = e34.fit(np.array([x1(r) for r in tr]), np.array([float(r["y"]) for r in tr]))
    out["revenue"] = {(r["cik"], r["end"]): float(1 / (1 + np.exp(-np.array(x1(r)) @ w))) for r in rows}
    for lab in LABELS[1:]:
        def x2(p):
            if None in p["g"] or p["x"][lab] is None or p["chg"][lab] is None:
                return None
            return [1.0] + list(np.clip(np.array(p["g"], dtype=float), -1, 2)) + [float(p["x"][lab]), p["chg"][lab],
                                                                               0.0 if p["base"][lab] is None else p["base"][lab], float(p["base"][lab] is None)]
        use = [(p, x2(p)) for p in eps]
        tr = [(p, x) for p, x in use if x is not None and p["y"][lab] is not None and p["next_filed"] <= CUTOFF]
        w = e34.fit(np.array([x for _, x in tr]), np.array([float(p["y"][lab]) for p, _ in tr]))
        out[lab] = {(p["cik"], p["end"]): float(1 / (1 + np.exp(-np.array(x) @ w))) for p, x in use if x is not None}
    return out


def secondary_bh(c1: dict, rng, key, got, arms, grp) -> dict:
    out = {}
    for lab in (l for l, c in c1.items() if "ci90" in c):  # p-values from a bootstrap of the paired difference
        d = []
        for i in grp["clean"]:
            y = key[i]["labels"][lab]
            pa, pc = (PROB[lab].search(got.get(f"a{i:03d}", "")), PROB[lab].search(got.get(f"c{i:03d}", "")))
            if y is None or not pa or not pc or "NA" in (pa.group(1).upper(), pc.group(1).upper()):
                continue
            a, c = int(pa.group(1)) / 100, int(pc.group(1)) / 100
            d.append((c if y else 1 - c) - (a if y else 1 - a))
        if not d:
            continue
        draws = [statistics.mean(rng.choices(d, k=len(d))) for _ in range(10_000)]
        out[lab] = {"n": len(d), "p": round(2 * min(sum(x <= 0 for x in draws), sum(x >= 0 for x in draws)) / 10_000, 4)}
    order = sorted(out, key=lambda l: out[l]["p"])
    keep = 0
    for k, lab in enumerate(order, 1):
        if out[lab]["p"] <= 0.10 * k / len(order):
            keep = k
    for k, lab in enumerate(order, 1):
        out[lab]["passes_bh_q10"] = k <= keep
    return out


def recurrence_check(key: dict, built: dict) -> dict:
    """Exploratory: a line tagged 'does not recur' after raising this quarter, against next quarter's direction."""
    m = {"revenue": "revenue", "gross margin": "gross_margin", "operating costs": "operating_margin", "net income": "net_income"}
    cells = collections.defaultdict(list)
    for i, k in key.items():
        form = (built.get(i) or {}).get("form")
        if not form or k["group"] != "clean":
            continue
        for x in form["recurrence"]:
            lab = m.get(x["line"])
            if lab is None or k["labels"][lab] is None or x["next_quarter"] not in ("does not recur", "recurs"):
                continue
            raised = x["effect_this_quarter"] == "raised"
            if x["line"] == "operating costs":
                raised = not raised  # costs raised lower the margin
            cells[f"{lab} | {'raised' if raised else 'lowered'} | {x['next_quarter']}"].append(float(k["labels"][lab]))
    return {c: {"n": len(v), "share_up_next": round(statistics.mean(v), 3)} for c, v in sorted(cells.items())}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("prepare", prepare), ("build", build), ("score", score)):
        sub.add_parser(name).set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
