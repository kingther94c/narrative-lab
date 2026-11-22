"""EXP-0031: extract, then rewrite into a fixed template. Does it hide the company and keep the signal? (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0031 (2026-11-22). The owner's
idea (2026-11-22): a first layer reads the release and takes out only what the forecast needs,
numbers and descriptions, and the input to the next layer is written anew.

1. ``prepare-e``: one call per episode to the PM definition with the raw release: fill a fixed
   JSON form (numbers as percentages, choices from fixed menus, a verbatim quote for every fact).
2. ``build``: code checks every quote against the release, drops facts whose quote is not found
   (or whose number is not in its quote), rounds percentages to whole numbers and renders two
   briefs in one fixed English template: FACTS (verified numbers and facts) and FULL (FACTS plus
   the reader's three judgements and the next-quarter effects it cites). The reader's own words
   never reach a brief. The ratio sheet is the one of EXP-0026's fully blinded view.
   Then four item sets: attacker on FULL and on FACTS (EXP-0028's question), PM on FULL and on
   FACTS (EXP-0026's question).
3. ``score``.

    conda run --no-capture-output -n nlab python research/experiments/exp0031_s2b_rewrite.py prepare-e
    (emit, run with exp0027, ingest: run exp0031, items_e)
    conda run --no-capture-output -n nlab python research/experiments/exp0031_s2b_rewrite.py build
    (emit, run, ingest: items_ap)
    conda run --no-capture-output -n nlab python research/experiments/exp0031_s2b_rewrite.py score
"""

from __future__ import annotations

import argparse
import collections
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402
import exp0028_s2b_attacker as e28  # noqa: E402
import exp0029_s2b_rationale_audit as e29  # noqa: E402
import exp0030_s2b_guided_redaction as e30  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0031"
RUN = "exp0031"
SEED = 20261126
QUESTION = e26.QUESTION

SECTORS = ("energy", "materials", "industrials", "consumer discretionary", "consumer staples", "health care",
           "financials", "information technology", "communication services", "utilities", "real estate")
NUMBERS = ("revenue_growth_reported", "revenue_growth_organic_or_constant_currency", "fx_effect_points",
           "acquisitions_divestitures_effect_points", "one_off_revenue_effect_points",
           "next_quarter_guidance_growth_low", "next_quarter_guidance_growth_high",
           "full_year_guidance_growth_low", "full_year_guidance_growth_high",
           "gross_margin_change_points", "operating_margin_change_points")
CHOICES = {
    "calendar_effect": ("extra week this quarter", "extra week in year-ago quarter", "none stated"),
    "next_quarter_guidance_basis": ("reported", "organic or constant currency", "none"),
    "full_year_guidance_change": ("raised", "maintained", "lowered", "initiated", "withdrawn", "none stated"),
}
JUDGEMENTS = {"demand": ("strong", "improving", "stable", "softening", "weak", "mixed", "not stated"),
              "pricing": ("rising", "stable", "falling", "not stated"),
              "outlook_tone": ("positive", "neutral", "cautious", "not stated")}
INDICATORS = ("backlog", "bookings or orders", "remaining performance obligations or deferred revenue", "book-to-bill",
              "subscribers or customers", "same-store or comparable sales", "other")
EFFECTS = ("acquisition closing", "divestiture closing", "contract start", "contract end", "price change",
           "product launch", "regulatory change", "other")

E_PROMPT = """You are preparing a standardised summary of an earnings release for an analyst who will forecast whether the company's year-on-year revenue growth next quarter will be higher or lower than in the quarter reported. The analyst must not be able to tell which company or which period this is, so the summary holds only the facts asked for below, in a fixed form.

Rules:
- Use only what the release states. Do not use anything you know about the company or about later events.
- Percentages as plain numbers (4.5 for 4.5%, -2 for a 2% decline). Use null when the release does not state it.
- Compute a value only from two figures that are both in the release, and list such fields in "computed".
- Every non-null number, every answer to calendar_effect, full_year_guidance_change, next_quarter_guidance_basis, and every forward indicator, segment value and next-quarter effect needs a supporting quote in "quotes": at most 25 consecutive words copied exactly from the release, keyed by the field name (for list entries, the field name, the position from 0 and the value name, such as "segments.0.growth").
- Segments: at most four, largest share of revenue first. Do not name them.
- Name nothing anywhere: no company, product, person, place or date.

Reply with one JSON object and nothing else, in exactly this shape:
{
 "sector": "<one of: """ + ", ".join(SECTORS) + """>",
 "revenue_growth_reported": <number or null>,
 "revenue_growth_organic_or_constant_currency": <number or null>,
 "fx_effect_points": <number or null>,
 "acquisitions_divestitures_effect_points": <number or null>,
 "one_off_revenue_effect_points": <number or null>,
 "calendar_effect": "<""" + " | ".join(CHOICES["calendar_effect"]) + """>",
 "next_quarter_guidance_growth_low": <number or null>,
 "next_quarter_guidance_growth_high": <number or null>,
 "next_quarter_guidance_basis": "<""" + " | ".join(CHOICES["next_quarter_guidance_basis"]) + """>",
 "full_year_guidance_growth_low": <number or null>,
 "full_year_guidance_growth_high": <number or null>,
 "full_year_guidance_change": "<""" + " | ".join(CHOICES["full_year_guidance_change"]) + """>",
 "forward_indicators": [{"kind": "<""" + " | ".join(INDICATORS) + """>", "growth": <number or null>, "ratio": <number or null, book-to-bill only>}],
 "segments": [{"share_of_revenue": <number or null>, "growth": <number or null>}],
 "gross_margin_change_points": <number or null>,
 "operating_margin_change_points": <number or null>,
 "demand": "<""" + " | ".join(JUDGEMENTS["demand"]) + """>",
 "pricing": "<""" + " | ".join(JUDGEMENTS["pricing"]) + """>",
 "outlook_tone": "<""" + " | ".join(JUDGEMENTS["outlook_tone"]) + """>",
 "next_quarter_effects": [{"kind": "<""" + " | ".join(EFFECTS) + """>", "direction": "<up | down>", "size": "<small | medium | large | unknown>"}],
 "quotes": {"<field>": "<quote>"},
 "computed": ["<field>"]
}
Forward indicators and next-quarter effects: at most four each, only what the release states; empty lists if none.

THE RELEASE:

"""

P_PROMPT = """You are an analyst working for a portfolio manager. Below are ratios from earlier filings and a standardised summary of an earnings release for one quarter of one company, written by code from facts taken out of the release. Names, dates and the release's own wording have been removed; work with what is given.

""" + QUESTION.format(this="the summary reports") + """

"""

A_PROMPT = e28.PROMPT.replace(
    "Below are ratios from earlier filings and an earnings release for one quarter of one real public company. Names, dates and figures may have been replaced or rescaled.",
    "Below are ratios from earlier filings and a standardised summary of an earnings release for one quarter of one real public company, written by code from facts taken out of the release. Names, dates and the release's wording have been removed.")
assert A_PROMPT != e28.PROMPT


def raw_release(i: int) -> str:
    return e29.document(i, 0).split("\nThe earnings release:\n", 1)[1]


def sheet(i: int) -> str:
    return e29.document(i, 7).split("\nThe earnings release:", 1)[0].rstrip()


def prepare_e(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    n = chars = 0
    with open(OUT / "items_e.jsonl", "w", encoding="utf-8") as fh:
        for k in e26.load(e26.OUT / "key.jsonl"):
            it = {"id": f"e{k['episode']:03d}", "agent": e26.PM, "prompt": E_PROMPT + raw_release(k["episode"])}
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
            n, chars = n + 1, chars + len(it["prompt"])
    print(f"[prepare-e] {n} items, {chars} prompt characters")


def replies() -> dict[str, str]:
    return {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / RUN) if r["canary_ok"]}


def as_json(reply: str) -> dict | None:
    a, b = reply.find("{"), reply.rfind("}")
    try:
        return json.loads(reply[a:b + 1]) if a >= 0 and b > a else None
    except json.JSONDecodeError:
        return None


def num_in(x: float, quote: str) -> bool:
    s = f"{abs(x):.2f}".rstrip("0").rstrip(".")
    return re.search(rf"(?<![\d.]){re.escape(s)}(?:\.0+)?(?![\d])", quote.replace(",", "")) is not None


def verify(j: dict, release: str) -> tuple[dict, collections.Counter]:
    """Keep only what the release supports. Returns the cleaned form and a log of drops."""
    nd, log = e29.norm(release), collections.Counter()
    quotes = j.get("quotes") or {}
    computed = set(j.get("computed") or [])

    def quoted(field: str) -> str | None:
        q = quotes.get(field)
        if not isinstance(q, str) or not q.strip():
            return None
        return q if e29.norm(q).strip(" .…\"'") in nd else None

    def number(field: str, x) -> float | None:
        if x is None:
            return None
        if not isinstance(x, (int, float)):
            log["dropped_not_a_number"] += 1
            return None
        q = quoted(field)
        if q is None:
            log["dropped_quote_not_found"] += 1
            return None
        if field not in computed and not num_in(float(x), q):
            log["dropped_number_not_in_quote"] += 1
            return None
        log["numbers_kept"] += 1
        return float(x)

    out: dict = {"sector": j.get("sector") if j.get("sector") in SECTORS else None}
    for f in NUMBERS:
        out[f] = number(f, j.get(f))
    for f, menu in CHOICES.items():
        v = j.get(f)
        if v not in menu:
            out[f] = None
            log["dropped_off_menu"] += 1
        elif v in ("none stated", "none"):
            out[f] = v
        else:
            out[f] = v if quoted(f) else None
            log["choices_kept" if out[f] else "dropped_quote_not_found"] += 1
    out["forward_indicators"] = []
    for n, x in enumerate((j.get("forward_indicators") or [])[:4]):
        if not isinstance(x, dict) or x.get("kind") not in INDICATORS:
            log["dropped_off_menu"] += 1
            continue
        g, r = number(f"forward_indicators.{n}.growth", x.get("growth")), number(f"forward_indicators.{n}.ratio", x.get("ratio"))
        if g is not None or r is not None:
            out["forward_indicators"].append({"kind": x["kind"], "growth": g, "ratio": r})
    out["segments"] = []
    for n, x in enumerate((j.get("segments") or [])[:4]):
        if not isinstance(x, dict):
            continue
        s, g = number(f"segments.{n}.share_of_revenue", x.get("share_of_revenue")), number(f"segments.{n}.growth", x.get("growth"))
        if s is not None or g is not None:
            out["segments"].append({"share_of_revenue": s, "growth": g})
    for f, menu in JUDGEMENTS.items():
        out[f] = j.get(f) if j.get(f) in menu else "not stated"
    out["next_quarter_effects"] = []
    for n, x in enumerate((j.get("next_quarter_effects") or [])[:4]):
        if not isinstance(x, dict) or x.get("kind") not in EFFECTS or x.get("direction") not in ("up", "down"):
            log["dropped_off_menu"] += 1
            continue
        if not any(quoted(f"next_quarter_effects.{n}{s}") for s in ("", ".kind", ".direction", ".size")):
            log["dropped_quote_not_found"] += 1
            continue
        out["next_quarter_effects"].append({"kind": x["kind"], "direction": x["direction"],
                                            "size": x.get("size") if x.get("size") in ("small", "medium", "large") else "unknown"})
        log["effects_kept"] += 1
    return out, log


def pct(x: float | None, unit: str = "%") -> str:
    return "not stated" if x is None else f"{round(x):+d}{unit}" if unit == " points" else f"{round(x)}{unit}"


def rng_text(lo: float | None, hi: float | None) -> str | None:
    if lo is None and hi is None:
        return None
    lo, hi = lo if lo is not None else hi, hi if hi is not None else lo
    return pct(lo) if round(lo) == round(hi) else f"{round(lo)}% to {round(hi)}%"


def render(v: dict, full: bool) -> str:
    L = [f"Sector: {v['sector'] or 'not stated'}", "", "This quarter, year on year:",
         f"  Revenue growth as reported: {pct(v['revenue_growth_reported'])}",
         f"  Organic or constant-currency revenue growth: {pct(v['revenue_growth_organic_or_constant_currency'])}",
         f"  Effect of exchange rates on growth: {pct(v['fx_effect_points'], ' points')}",
         f"  Effect of acquisitions and divestitures on growth: {pct(v['acquisitions_divestitures_effect_points'], ' points')}",
         f"  One-off effects on revenue growth: {pct(v['one_off_revenue_effect_points'], ' points')}",
         f"  Calendar: {v['calendar_effect'] or 'not stated'}",
         f"  Gross margin change: {pct(v['gross_margin_change_points'], ' points')}",
         f"  Operating margin change: {pct(v['operating_margin_change_points'], ' points')}", ""]
    L.append("Segments, largest first:" if v["segments"] else "Segments: not stated")
    for n, s in enumerate(v["segments"]):
        L.append(f"  Segment {'ABCD'[n]}: share of revenue {pct(s['share_of_revenue'])}, revenue growth {pct(s['growth'])}")
    L.append("")
    L.append("Forward indicators:" if v["forward_indicators"] else "Forward indicators: not stated")
    for x in v["forward_indicators"]:
        parts = ([f"growth {pct(x['growth'])}"] if x["growth"] is not None else []) + ([f"ratio {x['ratio']:.1f}"] if x["ratio"] is not None else [])
        L.append(f"  {x['kind']}: {', '.join(parts)}")
    nq = rng_text(v["next_quarter_guidance_growth_low"], v["next_quarter_guidance_growth_high"])
    fy = rng_text(v["full_year_guidance_growth_low"], v["full_year_guidance_growth_high"])
    basis = v["next_quarter_guidance_basis"]
    L += ["", "Guidance:",
          f"  Next quarter revenue growth: {nq + (f' ({basis})' if basis not in (None, 'none') else '') if nq else 'not stated'}",
          f"  Full year revenue growth: {fy or 'not stated'}",
          f"  Full year guidance: {v['full_year_guidance_change'] or 'not stated'}"]
    if full:
        L += ["", "Reader's summary of the release's commentary:",
              f"  Demand: {v['demand']}", f"  Pricing: {v['pricing']}", f"  Outlook tone: {v['outlook_tone']}",
              "Effects the release expects next quarter:" if v["next_quarter_effects"] else "Effects the release expects next quarter: none stated"]
        for x in v["next_quarter_effects"]:
            L.append(f"  {x['kind']}: {x['direction']}, {x['size']}")
    return "\n".join(L)


def build(_: argparse.Namespace) -> None:
    e23.need_drive()
    got = replies()
    briefs, logs, bad = {}, [], []
    for k in e26.load(e26.OUT / "key.jsonl"):
        i = k["episode"]
        j = as_json(got.get(f"e{i:03d}", ""))
        if j is None:
            bad.append(i)
            continue
        v, log = verify(j, raw_release(i))
        briefs[i] = {"facts": render(v, False), "full": render(v, True), "form": v}
        logs.append({"episode": i, **log})
    (OUT / "briefs.json").write_text(json.dumps(briefs, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(OUT / "items_ap.jsonl", "w", encoding="utf-8") as fh:
        for i, b in sorted(briefs.items()):
            for tag, kind in (("f", "full"), ("c", "facts")):
                text = sheet(i) + "\n\nThe summary:\n\n" + b[kind]
                fh.write(json.dumps({"id": f"a{tag}{i:03d}", "agent": e28.AGENT, "prompt": A_PROMPT + text}, ensure_ascii=False) + "\n")
                fh.write(json.dumps({"id": f"p{tag}{i:03d}", "agent": e26.PM, "prompt": P_PROMPT + text}, ensure_ascii=False) + "\n")
    tot = collections.Counter()
    for l in logs:
        tot.update({a: b for a, b in l.items() if a != "episode"})
    rep = {"briefs": len(briefs), "unparsed": bad, "log": dict(tot)}
    (OUT / "build_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    got = replies()
    briefs = {int(i): b for i, b in json.loads((OUT / "briefs.json").read_text(encoding="utf-8")).items()}
    rng = random.Random(SEED)
    p26 = {}
    for r in e23.records(e23.ROOT / e26.RUN):
        m = e26.PROB.search(r["reply"])
        if r["canary_ok"] and m:
            p26[r["id"].split(".")[0]] = int(m.group(1)) / 100

    def prob(rid: str) -> float | None:
        m = e26.PROB.search(got.get(rid, ""))
        return int(m.group(1)) / 100 if m and int(m.group(1)) <= 100 else None

    def toward(i: int, x: float | None) -> float | None:
        return None if x is None else (x if key[i]["accelerates"] else 1 - x)

    def ci(xs: list[float], ys: list[float] | None = None) -> dict:
        if not xs or (ys is not None and not ys):
            return {"n": len(xs)}
        est = statistics.mean(xs) - (statistics.mean(ys) if ys else 0)
        d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) - (statistics.mean(rng.choices(ys, k=len(ys))) if ys else 0)
                   for _ in range(10_000))
        return {"est": round(est, 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(xs), "n_ref": len(ys) if ys else None}

    grp = {g: [i for i in briefs if key[i]["group"] == g] for g in ("old", "clean")}
    out: dict = {"briefs": len(briefs)}
    for tag, kind in (("f", "full"), ("c", "facts")):
        o: dict = {}
        hits = {}
        for i in briefs:
            reply = got.get(f"a{tag}{i:03d}")
            if reply is not None:
                hits[i] = e30.read(reply, key[i])
        cells = {"all": list(briefs), "old": grp["old"], "clean": grp["clean"],
                 "top 50": [i for i in briefs if key[i]["tier"] == "top 50"],
                 "51 to 250": [i for i in briefs if key[i]["tier"] == "51 to 250"]}
        o["c1_attacker"] = {c: {m: ci([float(hits[i][m]) for i in ids if i in hits]) for m in ("top1", "top3", "quarter")} for c, ids in cells.items()}
        conf = [h["confidence"] for h in hits.values() if h["confidence"] is not None]
        o["c1_median_confidence"] = statistics.median(conf) if conf else None
        t1 = o["c1_attacker"]["all"]["top1"].get("est")
        o["c1_verdict"] = None if t1 is None else "stopped" if t1 <= 0.20 else "not stopped" if t1 >= 0.50 else "undecided"
        ro = {i: toward(i, prob(f"p{tag}{i:03d}")) for i in briefs}
        col = lambda g, d: [d[i] for i in grp[g] if d.get(i) is not None]  # noqa: E731
        raw = {i: toward(i, p26.get(f"v{i:03d}-0")) for i in briefs}
        o["c2_leak_old_minus_clean"] = ci(col("old", ro), col("clean", ro))
        o["c2_leak_exp0026_raw_same_episodes"] = ci(col("old", raw), col("clean", raw))
        o["c2_no_leak_detected"] = (lambda c: c.get("ci90", [1, 1])[0] <= 0 <= c.get("ci90", [-1, -1])[1])(o["c2_leak_old_minus_clean"])
        pair = [ro[i] - raw[i] for i in grp["clean"] if ro.get(i) is not None and raw.get(i) is not None]
        c4 = ci(pair)
        c4["verdict"] = None if "est" not in c4 else ("retains" if c4["est"] >= -0.03 and c4["ci90"][0] > -0.10
                                                      else "loses" if c4["ci90"][1] < 0 else "undecided")
        o["c4_clean_readout_brief_minus_raw_paired"] = c4
        o["c4_clean_readout_brief"] = ci(col("clean", ro))
        o["c4_clean_accuracy_brief"] = ci([float(x > 0.5) for x in col("clean", ro)])
        o["c4_clean_accuracy_raw"] = ci([float(x > 0.5) for x in col("clean", raw)])
        o["old_accuracy_brief"] = ci([float(x > 0.5) for x in col("old", ro)])
        out[kind] = o
    out["c3_judgements_add_leak_full_minus_facts"] = None
    lf = out["full"]["c2_leak_old_minus_clean"].get("est")
    lc = out["facts"]["c2_leak_old_minus_clean"].get("est")
    if lf is not None and lc is not None:
        out["c3_judgements_add_leak_full_minus_facts"] = round(lf - lc, 3)
    score_of = {"strong": 1, "improving": 1, "stable": 0, "mixed": 0, "not stated": 0, "softening": -1, "weak": -1}
    out["c6_demand_score_up_minus_down"] = {}
    for g in ("old", "clean"):
        up = [score_of[briefs[i]["form"]["demand"]] for i in grp[g] if key[i]["accelerates"]]
        dn = [score_of[briefs[i]["form"]["demand"]] for i in grp[g] if not key[i]["accelerates"]]
        out["c6_demand_score_up_minus_down"][g] = ci([float(x) for x in up], [float(x) for x in dn])
    forms = [b["form"] for b in briefs.values()]
    out["c5_coverage"] = {f: round(sum(x[f] is not None for x in forms) / len(forms), 3)
                          for f in ("revenue_growth_reported", "revenue_growth_organic_or_constant_currency",
                                    "next_quarter_guidance_growth_low", "full_year_guidance_growth_low", "operating_margin_change_points")}
    out["c5_coverage"]["segments"] = round(sum(bool(x["segments"]) for x in forms) / len(forms), 3)
    out["c5_coverage"]["forward_indicators"] = round(sum(bool(x["forward_indicators"]) for x in forms) / len(forms), 3)
    out["c5_build"] = json.loads((OUT / "build_summary.json").read_text(encoding="utf-8"))["log"]
    (OUT / "score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare-e").set_defaults(fn=prepare_e)
    sub.add_parser("build").set_defaults(fn=build)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
