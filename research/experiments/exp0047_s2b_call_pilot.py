"""EXP-0047: does the earnings call add to the release? Clean-quarter pilot (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0047 (approved 2026-11-24). On
EXP-0036's clean episodes with an EXP-0045 call document:

- A : EXP-0036's A1 prompt, unchanged (release, skill v1 block, code facts from EXP-0036's
      built.json), re-run so both arms come from one run.
- X : A plus the transcript of the call held after the release (A1C).
- R : reader on the release and the call: skill v1 Part D form, quotes checked against the call.

    conda run --no-capture-output -n nlab python research/experiments/exp0047_s2b_call_pilot.py prepare [--dry]
    (exp0023 emit --run exp0047 --items s2/exp0047/items.jsonl; exp0027 run; exp0023 ingest)
    conda run --no-capture-output -n nlab python research/experiments/exp0047_s2b_call_pilot.py score
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0023_s2a_dispatch as e23  # noqa: E402
import exp0026_s2b_views as e26  # noqa: E402
import exp0031_s2b_rewrite as e31  # noqa: E402
import exp0036_s2b_skill_v1 as e36  # noqa: E402
import exp0045_s2a_call_texts as e45  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0047"
RUN = "exp0047"
SEED = 20261128
LABELS = e36.LABELS
LM_CSV = e23.DRIVE / "corpora" / "lexicons" / "loughran_mcdonald" / "Loughran-McDonald_MasterDictionary_1993-2025.csv"
LM_SHA256 = "e2d1328682bab7d2187684fb9f5420bb730401c9eefc00daf835edd203f4859d"

FACTS_NOTE = ", and facts computed by code from earlier filings and from this release"
CALL_NOTE = ", followed by the transcript of the earnings call held after the release"
D1 = ("more downbeat than the numbers", "in line", "more upbeat than the numbers")
D3 = ("most", "some", "few", "no questions and answers")
D4 = ("negative", "neutral", "positive", "no questions and answers")

R_PROMPT = f"""You are reading an earnings release and the transcript of the earnings call held after it, for an analyst. Fill in the form below. Every quote must be copied exactly from the call transcript.

Reply with one JSON object and nothing else:
{{"d1_tone_against_numbers": "<{' | '.join(D1)}>",
 "d1_quote": "<one short quote from management on the call that shows the tone>",
 "d2_extreme_negative_quotes": ["<up to five short quotes in which management uses strongly negative words>"],
 "d3_scripted_answers": "<{' | '.join(D3)}>",
 "d4_analyst_tone": "<{' | '.join(D4)}>",
 "d5_refusals": ["<up to five short quotes in which management declines to answer a question directly>"]}}

Rules:
- d1: does management on the call talk about the business more gloomily or more cheerfully than the release's numbers justify, or in line with them?
- d3: the share of management's answers that read as prepared statements rather than replies to the question asked.
- d4: the overall tone of the analysts' questions.
- Use an empty list when there is nothing to quote.

"""


def a_prompt(rel: str, facts: str) -> str:
    return e36.pm_prompt("a1", rel, facts, None)


def x_prompt(rel: str, facts: str, call: str) -> str:
    p = a_prompt(rel, facts)
    old, new = e36.A_INTRO.format(facts_note=FACTS_NOTE), e36.A_INTRO.format(facts_note=FACTS_NOTE + CALL_NOTE)
    assert p.startswith(old)
    return new + p[len(old):] + "\n\nThe earnings call (transcript):\n\n" + call


def r_prompt(rel: str, call: str) -> str:
    return R_PROMPT + "The earnings release:\n\n" + rel + "\n\nThe earnings call (transcript):\n\n" + call


def call_docs() -> dict[int, dict]:
    out = {}
    for line in open(e45.OUT / "calls.jsonl", encoding="utf-8"):
        x = json.loads(line)
        if x["stage"] == "clean":
            out[int(x["episode"])] = x
    return out


def prepare(a: argparse.Namespace) -> None:
    e23.need_drive()
    key36 = [k for k in e26.load(e36.OUT / "key.jsonl") if k["group"] == "clean"]
    built = {int(i): b for i, b in json.loads((e36.OUT / "built.json").read_text(encoding="utf-8")).items()}
    docs = call_docs()
    _, digest = e36.considerations()
    sent36 = {json.loads(line)["id"]: json.loads(line)["prompt"] for line in open(e36.OUT / "items_cb.jsonl", encoding="utf-8")}
    same = []
    items, key, sizes = [], [], collections.defaultdict(list)
    for k in key36:
        d = docs.get(k["i"])
        if d is None:
            continue
        rel = e36.release_text(k)
        call = (e45.DOCS / d["file"]).read_text(encoding="utf-8")
        facts = built[k["i"]]["facts"]
        same.append(a_prompt(rel, facts) == sent36.get(f"c{k['i']:03d}"))
        for tag, prompt in (("a", a_prompt(rel, facts)), ("x", x_prompt(rel, facts, call)), ("r", r_prompt(rel, call))):
            items.append({"id": f"{tag}{k['i']:03d}", "agent": e26.PM, "prompt": prompt})
            sizes[tag].append(len(prompt) // 4)
        key.append({"i": k["i"], "cik": k["cik"], "rank": k["rank"], "quarter_end": k["quarter_end"], "labels": k["labels"],
                    "source": d["source"], "partial": d["partial"], "file": d["file"], "qa_found": d["qa_found"]})
    rep = {"episodes": len(key), "full": sum(not k["partial"] for k in key), "partial": sum(k["partial"] for k in key),
           "full_top250": sum(not k["partial"] and k["rank"] < 250 for k in key),
           "by_source": dict(collections.Counter(k["source"] for k in key)), "calls": len(items),
           "approx_prompt_tokens": {t: {"median": statistics.median(v), "max": max(v), "sum": sum(v)} for t, v in sizes.items()},
           "skill_block_sha256_16": digest, "a_prompt_equals_exp0036_a1": f"{sum(same)} of {len(same)}"}
    assert all(same), "A must be EXP-0036's A1 prompt verbatim"
    if a.dry:
        print(json.dumps(rep, indent=2))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "items.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), encoding="utf-8")
    (OUT / "key.jsonl").write_text("".join(json.dumps(k) + "\n" for k in key), encoding="utf-8")
    (OUT / "prepare_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))


# ---------------------------------------------------------------------------------------------
# Scoring


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def read_form(reply: str, call: str) -> dict | None:
    j = e31.as_json(reply)
    if j is None:
        return None
    text = norm(call)

    def ok(q):
        return isinstance(q, str) and len(q.strip()) >= 8 and norm(q) in text

    def quotes(v):
        return [q for q in (v if isinstance(v, list) else [])[:5] if ok(q)]

    return {"d1": j.get("d1_tone_against_numbers") if j.get("d1_tone_against_numbers") in D1 and ok(j.get("d1_quote")) else None,
            "d2": len(quotes(j.get("d2_extreme_negative_quotes"))),
            "d3": j.get("d3_scripted_answers") if j.get("d3_scripted_answers") in D3 else None,
            "d4": j.get("d4_analyst_tone") if j.get("d4_analyst_tone") in D4 else None,
            "d5": len(quotes(j.get("d5_refusals"))),
            "quotes_dropped": sum(1 for f in ("d2_extreme_negative_quotes", "d5_refusals") for q in (j.get(f) or [])[:5] if not ok(q))}


def lm_lists() -> dict[str, set]:
    h = hashlib.sha256(LM_CSV.read_bytes()).hexdigest()
    assert h == LM_SHA256, f"dictionary file changed: {h}"
    out = {"Negative": set(), "Positive": set(), "Uncertainty": set()}
    with open(LM_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            for c in out:
                if row[c] not in ("0", ""):
                    out[c].add(row["Word"])
    return out


def shares(text: str, lm: dict) -> dict:
    w = re.findall(r"[A-Za-z]+", text)
    n = len(w) or 1
    u = [x.upper() for x in w]
    neg, pos, unc = (sum(x in lm[c] for x in u) for c in ("Negative", "Positive", "Uncertainty"))
    return {"words": len(w), "tone": (pos - neg) / n, "neg": neg / n, "unc": unc / n}


TURN = re.compile(r"^\[([^,\]]*), ([^\]]*)\]: (.*)$", re.S)


def management_parts(doc: str) -> tuple[str, str | None]:
    """(management's prepared remarks, management's answers in the Q&A or None where speakers are not labelled)."""
    prep, _, qa = doc.partition("\n\nQUESTIONS AND ANSWERS\n\n")
    prep = prep.replace("PREPARED REMARKS\n\n", "", 1)
    paras = [p for p in prep.split("\n\n") if p.strip()]
    if not paras or not TURN.match(paras[0]):
        return prep, None  # IR file: no speaker labels

    def mgmt(ps):
        out = []
        for p in ps:
            m = TURN.match(p)
            if m and "analyst" not in m[2].lower() and "operator" not in (m[1] + m[2]).lower():
                out.append(m[3])
        return "\n".join(out)

    return mgmt(paras), mgmt([p for p in qa.split("\n\n") if p.strip()])


def boot(xs: list[float], rng: random.Random) -> dict:
    if not xs:
        return {"n": 0}
    d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) for _ in range(10_000))
    p = 2 * min(sum(v <= 0 for v in d), sum(v >= 0 for v in d)) / len(d)
    return {"est": round(statistics.mean(xs), 4), "ci90": [round(d[499], 4), round(d[9499], 4)], "n": len(xs), "p_boot": round(min(1.0, p), 4)}


def bh(ps: dict[str, float], q: float = 0.10) -> dict[str, bool]:
    order = sorted(ps, key=ps.get)
    m, cut = len(order), 0
    for r, k in enumerate(order, 1):
        if ps[k] <= q * r / m:
            cut = r
    return {k: order.index(k) < cut for k in ps}


def thirds(pairs: list[tuple[float, bool]]) -> dict:
    """Outcome rate in the lowest and highest third of a feature, and their difference."""
    if len(pairs) < 9:
        return {"n": len(pairs)}
    s = sorted(pairs, key=lambda t: t[0])
    k = len(s) // 3
    lo, hi = [y for _, y in s[:k]], [y for _, y in s[-k:]]
    return {"n": len(s), "rate_low_third": round(statistics.mean(lo), 3), "rate_high_third": round(statistics.mean(hi), 3),
            "high_minus_low": round(statistics.mean(hi) - statistics.mean(lo), 3)}


def corr(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) * statistics.pstdev(xs) * statistics.pstdev(ys)), 3)


def score(_: argparse.Namespace) -> None:
    e23.need_drive()
    key = {k["i"]: k for k in e26.load(OUT / "key.jsonl")}
    got = {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / RUN) if r["canary_ok"]}
    old_a1 = {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / e36.RUN) if r["canary_ok"]}
    rng = random.Random(SEED)
    full = [i for i, k in key.items() if not k["partial"]]
    part = [i for i, k in key.items() if k["partial"]]

    def prob(reply: str | None, lab: str) -> float | None:
        m = e36.PROB[lab].search(reply or "")
        if not m or m.group(1).upper() == "NA" or int(m.group(1)) > 100:
            return None
        return int(m.group(1)) / 100

    def readout(p: float | None, y) -> float | None:
        return None if p is None or y is None else (p if y else 1 - p)

    _, eps = e36.pool()
    base = e36.baselines(eps)
    out: dict = {"skill_block_sha256_16": e36.considerations()[1], "replies": len(got),
                 "episodes": {"full": len(full), "partial": len(part)}}
    for lab in LABELS:
        o: dict = {}
        y = {i: key[i]["labels"][lab] for i in key}
        pa = {i: prob(got.get(f"a{i:03d}"), lab) for i in key}
        px = {i: prob(got.get(f"x{i:03d}"), lab) for i in key}
        pc = {i: base[lab].get((key[i]["cik"], key[i]["quarter_end"])) for i in key}
        ro = {"A1": {i: readout(pa[i], y[i]) for i in key}, "A1C": {i: readout(px[i], y[i]) for i in key},
              "code": {i: readout(pc[i], y[i]) for i in key}}
        pair = lambda ids: [ro["A1C"][i] - ro["A1"][i] for i in ids if ro["A1C"][i] is not None and ro["A1"][i] is not None]  # noqa: E731
        c1 = boot(pair(full), rng)
        c1["verdict"] = None if "est" not in c1 else "helps" if c1["ci90"][0] > 0 else "hurts" if c1["ci90"][1] < 0 else "undecided"
        o["c1_A1C_minus_A1_full"] = c1
        o["partial_A1C_minus_A1"] = boot(pair(part), rng)
        o["c3_full"] = {a: {"readout": boot([d[i] for i in full if d[i] is not None], rng),
                            "accuracy": boot([float(d[i] > 0.5) for i in full if d[i] is not None and d[i] != 0.5], rng),
                            "brier": boot([(1 - d[i]) ** 2 for i in full if d[i] is not None], rng)} for a, d in ro.items()}
        pold = {i: prob(old_a1.get(f"c{i:03d}"), lab) for i in full}
        both = [i for i in full if pa[i] is not None and pold[i] is not None]
        o["c4_run_to_run_vs_exp0036_A1"] = {"n": len(both),
                                            "same_side": round(statistics.mean([(pa[i] > 0.5) == (pold[i] > 0.5) for i in both]), 3) if both else None,
                                            "mean_abs_prob_diff": round(statistics.mean([abs(pa[i] - pold[i]) for i in both]), 4) if both else None}
        o["c5_slices"] = {f"source={s}": boot(pair([i for i in full if key[i]["source"] == s]), rng) for s in ("alpha_vantage", "ir_site")}
        o["c5_slices"]["top250"] = boot(pair([i for i in full if key[i]["rank"] < 250]), rng)
        o["c5_slices"]["rank250_499"] = boot(pair([i for i in full if key[i]["rank"] >= 250]), rng)
        o["_diff"] = {i: ro["A1C"][i] - ro["A1"][i] for i in full if ro["A1C"][i] is not None and ro["A1"][i] is not None}
        o["_spread"] = {i: abs(px[i] - 0.5) for i in full if px[i] is not None}
        out[lab] = o
    out["c2_secondary_bh_q10"] = bh({lab: out[lab]["c1_A1C_minus_A1_full"].get("p_boot", 1.0) for lab in LABELS[1:]})
    # criterion 6: reader features (exploratory)
    forms = {}
    for i in full:
        call = (e45.DOCS / key[i]["file"]).read_text(encoding="utf-8")
        forms[i] = read_form(got.get(f"r{i:03d}", ""), call)
    c6: dict = {"parsed": sum(f is not None for f in forms.values()), "of": len(full),
                "quotes_dropped": sum(f["quotes_dropped"] for f in forms.values() if f)}
    for lab in ("revenue", "net_income"):
        y = {i: key[i]["labels"][lab] for i in full}
        c6[f"d1_vs_{lab}"] = {v: (lambda ys: {"n": len(ys), "rate": round(statistics.mean(ys), 3) if ys else None})(
            [bool(y[i]) for i in full if forms[i] and forms[i]["d1"] == v and y[i] is not None]) for v in D1}
        c6[f"d2_vs_{lab}"] = thirds([(forms[i]["d2"], bool(y[i])) for i in full if forms[i] and y[i] is not None])
    c6["d5_vs_A1C_spread_revenue"] = corr(*zip(*[(forms[i]["d5"], out["revenue"]["_spread"][i]) for i in full
                                                if forms[i] and i in out["revenue"]["_spread"]])) if full else None
    out["c6_exploratory_reader"] = c6
    # criterion 7: Loughran-McDonald shares (exploratory)
    lm = lm_lists()
    feats = {}
    for i in full:
        doc = (e45.DOCS / key[i]["file"]).read_text(encoding="utf-8")
        prep, answers = management_parts(doc)
        feats[i] ={"prep": shares(prep, lm), "answers": shares(answers, lm) if answers else None}
    key36 = {k["i"]: k for k in e26.load(e36.OUT / "key.jsonl")}
    for i in full:
        feats[i]["release"] = shares(e36.release_text(key36[i]), lm)
        feats[i]["gloom_beyond_release"] = feats[i]["prep"]["tone"] - feats[i]["release"]["tone"]
    c7: dict = {"dictionary_sha256": LM_SHA256}
    for lab in ("revenue", "net_income"):
        y = {i: key[i]["labels"][lab] for i in full}
        c7[f"tone_gap_vs_{lab}"] = thirds([(feats[i]["gloom_beyond_release"], bool(y[i])) for i in full if y[i] is not None])
        c7[f"answers_neg_vs_{lab}"] = thirds([(feats[i]["answers"]["neg"], bool(y[i])) for i in full if feats[i]["answers"] and y[i] is not None])
        c7[f"answers_unc_vs_{lab}"] = thirds([(feats[i]["answers"]["unc"], bool(y[i])) for i in full if feats[i]["answers"] and y[i] is not None])
    d = out["revenue"]["_diff"]
    ids = [i for i in full if i in d]
    c7["tone_gap_vs_A1C_minus_A1_revenue_corr"] = corr([feats[i]["gloom_beyond_release"] for i in ids], [d[i] for i in ids])
    out["c7_exploratory_lm"] = c7
    for lab in LABELS:
        out[lab].pop("_diff")
        out[lab].pop("_spread")
    (OUT / "features.json").write_text(json.dumps({"forms": forms, "lm": feats}, indent=1), encoding="utf-8")
    (OUT / "score.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--dry", action="store_true", help="count and size the items; write nothing")
    p.set_defaults(fn=prepare)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
