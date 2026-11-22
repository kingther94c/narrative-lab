"""EXP-0029: can the model's own stated reasons show where its call comes from? (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0029 (2026-11-21). On the raw and
the fully blinded view of EXP-0026's 90 episodes, three calls each:

A. ``s`` items, the PM definition: the call of EXP-0026, with the reasons first and structured:
   evidence items with a source tag, a direction, a weight and a verbatim quote, then the
   company the model believes it is reading, then the probability.
B. ``q`` items, the PM definition, no document: only the quotes of A's DOCUMENT items that are
   found verbatim in the text. Do the cited passages alone carry the call?
C. ``c`` items, the recall definition: the document and A's reply, then questions put from
   outside: which company and quarter, what growth the next quarter went on to show, the
   probability from the text alone and from everything the model knows.

    conda run --no-capture-output -n nlab python research/experiments/exp0029_s2b_rationale_audit.py prepare-a
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run exp0029 --items <items_a>
    conda run --no-capture-output -n nlab python research/experiments/exp0027_s2a_cli_dispatch_v2.py run --run exp0029
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run exp0029
    conda run --no-capture-output -n nlab python research/experiments/exp0029_s2b_rationale_audit.py prepare-bc
    (emit, run and ingest again with <items_bc>)
    conda run --no-capture-output -n nlab python research/experiments/exp0029_s2b_rationale_audit.py score
"""

from __future__ import annotations

import argparse
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

OUT = e23.DRIVE / "s2" / "exp0029"
RUN = "exp0029"
SEED = 20261124
VIEWS = (0, 7)  # raw; names, periods, scaling and noise all on
QUESTION = e26.QUESTION.split("\n\nReply in exactly", 1)[0]

A_PROMPT = """You are an analyst working for a portfolio manager. Below are ratios from earlier filings and an earnings release for one quarter of one company. Names, dates or figures may have been replaced or rescaled; work with the text as it is given.

""" + QUESTION.format(this="this release reports") + """

Give your reasons first, as three to six evidence items, then your answer. For each item say where it comes from:
DOCUMENT: something stated in the text below.
GENERAL: general knowledge of industries or the economy, not specific to this company.
MEMORY: something you know about this particular company or period that is not in the text.

Reply in exactly this format, one item per line:
E1 | SOURCE: <DOCUMENT, GENERAL or MEMORY> | POINTS: <HIGHER or LOWER> | WEIGHT: <1 to 5> | QUOTE: "<at most 25 consecutive words copied exactly from the text, or NONE>" | CLAIM: <one sentence>
E2 | ...
COMPANY: <the real company you believe this is, or UNKNOWN>
PROBABILITY: <a whole number from 0 to 100: the probability that next quarter's growth is HIGHER>

"""

B_PROMPT = """You are an analyst working for a portfolio manager. Below are passages quoted from an earnings release for one quarter of one company. The release itself is not available. Names, dates or figures may have been replaced or rescaled; work with the passages as they are given.

""" + QUESTION.format(this="the release reports") + """

Reply in exactly this format:
PROBABILITY: <a whole number from 0 to 100: the probability that next quarter's growth is HIGHER>
RATIONALE: <at most two sentences>

Passages:
"""

C_PROMPT = """Below are ratios from earlier filings and an earnings release for one quarter of one real public company, and after them an answer given earlier to a question about that text. Names, dates and figures in the text may have been replaced or rescaled. Answer from everything you know.

The question was: """ + QUESTION.format(this="this release reports").removeprefix("Question: ") + """

Reply in exactly this format:
COMPANY: <the real company, name and ticker, or UNKNOWN>
QUARTER_END: <year and month of the real quarter end, as YYYY-MM, or UNKNOWN>
NEXT_GROWTH: <the year-on-year revenue growth the company went on to report for the NEXT quarter, in percent, as you recall it, or UNKNOWN>
FLIP: <the one evidence item of the earlier answer that would change its probability most if it pointed the other way, as E1 to E6>
PROBABILITY_TEXT_ONLY: <a whole number from 0 to 100: the probability of HIGHER judged from the text alone, setting aside anything you recall about the company or the period>
PROBABILITY_ALL: <a whole number from 0 to 100: the probability of HIGHER using everything you know>

EARLIER ANSWER:
{answer}

TEXT:
{doc}"""

ITEM = re.compile(r"^E(\d)\s*\|\s*SOURCE:\s*(DOCUMENT|GENERAL|MEMORY)\s*\|\s*POINTS:\s*(HIGHER|LOWER)\s*\|\s*WEIGHT:\s*([1-5])"
                  r"\s*\|\s*QUOTE:\s*(.*?)\s*\|\s*CLAIM:\s*(.*)$", re.I | re.M)
PROB = re.compile(r"^PROBABILITY:\s*(\d{1,3})\s*$", re.I | re.M)


def document(i: int, v: int) -> str:
    c = json.loads((e23.ROOT / e26.RUN / "outbox" / f"v{i:03d}-{v}.json").read_text(encoding="utf-8"))
    return c["prompt"].split(e28.MARK, 1)[1].rsplit(e23.CANARY.format(code=c["canary"]), 1)[0]


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def parse_a(reply: str, doc: str) -> dict:
    nd = norm(doc)
    items = []
    for m in ITEM.finditer(reply):
        q = m.group(5).strip().strip('"').strip()
        q = None if q.upper() == "NONE" or not q else q
        found = bool(q) and norm(q).strip(" .…") in nd
        items.append({"n": int(m.group(1)), "source": m.group(2).upper(), "sign": 1 if m.group(3).upper() == "HIGHER" else -1,
                      "weight": int(m.group(4)), "quote": q, "found": found, "claim": m.group(6).strip()})
    p = PROB.search(reply)
    c = re.search(r"^COMPANY:\s*(.*)$", reply, re.I | re.M)
    return {"items": items, "p": int(p.group(1)) / 100 if p and int(p.group(1)) <= 100 else None, "company": c.group(1).strip() if c else ""}


def lean(items: list[dict]) -> float | None:  # weighted share of the stated evidence that points to HIGHER
    w = sum(x["weight"] for x in items)
    return sum(x["weight"] for x in items if x["sign"] > 0) / w if w else None


def replies() -> dict[str, str]:
    out = {}
    for r in e23.records(e23.ROOT / RUN):
        if r["canary_ok"]:
            out[r["id"].split(".")[0]] = r["reply"]
    return out


def prepare_a(_: argparse.Namespace) -> None:
    e23.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    n = chars = 0
    with open(OUT / "items_a.jsonl", "w", encoding="utf-8") as fh:
        for k in e26.load(e26.OUT / "key.jsonl"):
            for v in VIEWS:
                it = {"id": f"s{k['episode']:03d}-{v}", "agent": e26.PM, "prompt": A_PROMPT + document(k["episode"], v)}
                fh.write(json.dumps(it, ensure_ascii=False) + "\n")
                n, chars = n + 1, chars + len(it["prompt"])
    print(f"[prepare-a] {n} items, {chars} prompt characters -> {OUT / 'items_a.jsonl'}")


def prepare_bc(_: argparse.Namespace) -> None:
    e23.need_drive()
    got = replies()
    nb = nc = no_quote = missing = 0
    with open(OUT / "items_bc.jsonl", "w", encoding="utf-8") as fh:
        for k in e26.load(e26.OUT / "key.jsonl"):
            for v in VIEWS:
                i = k["episode"]
                reply = got.get(f"s{i:03d}-{v}")
                if reply is None:
                    missing += 1
                    continue
                doc = document(i, v)
                a = parse_a(reply, doc)
                quotes = [x["quote"] for x in a["items"] if x["source"] == "DOCUMENT" and x["found"]]
                if quotes:
                    body = "\n".join(f'- "{q}"' for q in quotes)
                    fh.write(json.dumps({"id": f"q{i:03d}-{v}", "agent": e26.PM, "prompt": B_PROMPT + body}, ensure_ascii=False) + "\n")
                    nb += 1
                else:
                    no_quote += 1
                answer = "\n".join(l for l in reply.splitlines() if not l.startswith("ITEM ")).strip()
                fh.write(json.dumps({"id": f"c{i:03d}-{v}", "agent": e26.RECALL, "prompt": C_PROMPT.format(answer=answer, doc=doc)},
                                    ensure_ascii=False) + "\n")
                nc += 1
    print(f"[prepare-bc] {nb} quote items, {nc} question items; {no_quote} answers without a verified quote, {missing} answers missing")


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    got = replies()
    p26 = {}
    for r in e23.records(e23.ROOT / e26.RUN):
        m = e26.PROB.search(r["reply"])
        if r["canary_ok"] and m:
            p26[r["id"].split(".")[0]] = int(m.group(1)) / 100
    rng = random.Random(SEED)

    def toward(i: int, x: float | None) -> float | None:  # probability given to the direction that happened
        return None if x is None else (x if key[i]["accelerates"] else 1 - x)

    def num(tag: str, reply: str | None) -> float | None:
        m = re.search(rf"^{tag}:\s*(-?\d+(?:\.\d+)?)", reply or "", re.I | re.M)
        return float(m.group(1)) if m else None

    rows = []
    for i, k in key.items():
        for v in VIEWS:
            reply = got.get(f"s{i:03d}-{v}")
            if reply is None:
                continue
            a = parse_a(reply, document(i, v))
            docs = [x for x in a["items"] if x["source"] == "DOCUMENT"]
            quoted = [x for x in a["items"] if x["quote"]]
            b, c = got.get(f"q{i:03d}-{v}"), got.get(f"c{i:03d}-{v}")
            pb, ng = num("PROBABILITY", b), num("NEXT_GROWTH", c)
            pt, pa = num("PROBABILITY_TEXT_ONLY", c), num("PROBABILITY_ALL", c)
            cc = re.search(r"^COMPANY:\s*(.*)$", c or "", re.I | re.M)
            fl = re.search(r"^FLIP:\s*E(\d)", c or "", re.I | re.M)
            top = max((x["weight"] for x in a["items"]), default=None)
            ln = lean(a["items"])
            rows.append({
                "episode": i, "view": v, "group": k["group"], "n_items": len(a["items"]),
                "a": toward(i, a["p"]), "a26": toward(i, p26.get(f"v{i:03d}-{v}")),
                "names_company": e28.hit(a["company"], k), "says_unknown": a["company"].upper().startswith("UNKNOWN"),
                "memory_items": sum(x["source"] == "MEMORY" for x in a["items"]),
                "quotes": len(quoted), "quotes_found": sum(x["found"] for x in quoted),
                "consistent": None if a["p"] is None or a["p"] == 0.5 or ln is None or ln == 0.5 else (ln > 0.5) == (a["p"] > 0.5),
                "lean_all": toward(i, ln), "lean_document": toward(i, lean(docs)),
                "b": toward(i, None if pb is None else pb / 100),
                "c_names_company": bool(cc) and e28.hit(cc.group(1), k),
                "recall_given": ng is not None,
                "recall_right": None if ng is None else (ng / 100 > k["g"]) == k["accelerates"],
                "recall_abs_error_pts": None if ng is None else round(abs(ng - 100 * k["g_next"]), 2),
                "c_text_only": toward(i, None if pt is None else pt / 100), "c_all": toward(i, None if pa is None else pa / 100),
                "flip_is_top_weight": None if not fl or top is None else any(x["n"] == int(fl.group(1)) and x["weight"] == top for x in a["items"]),
            })

    def sel(v: int, g: str, f: str, keep=lambda r: True) -> list[float]:
        return [float(r[f]) for r in rows if r["view"] == v and r["group"] == g and r[f] is not None and keep(r)]

    def ci(xs: list[float], ys: list[float] | None = None) -> dict:
        if not xs or (ys is not None and not ys):
            return {"n": len(xs), "n_ref": len(ys or [])}
        est = statistics.mean(xs) - (statistics.mean(ys) if ys else 0)
        d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) - (statistics.mean(rng.choices(ys, k=len(ys))) if ys else 0)
                   for _ in range(10_000))
        return {"est": round(est, 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(xs), "n_ref": len(ys) if ys else None}

    def gap(v: int, f: str, keep=lambda r: True) -> dict:
        return ci(sel(v, "old", f, keep), sel(v, "clean", f, keep))

    out: dict = {"answers": len(rows), "a_without_probability": sum(r["a"] is None for r in rows)}
    for v in VIEWS:
        o: dict = {}
        o["c1_gap_structured"] = gap(v, "a")
        o["c1_gap_exp0026_same_episodes"] = gap(v, "a26")
        o["c2_names_company"] = {g: ci(sel(v, g, "names_company")) for g in ("old", "clean")}
        o["c2_says_unknown"] = {g: ci(sel(v, g, "says_unknown")) for g in ("old", "clean")}
        o["c3_has_memory_item"] = {g: ci([float(r["memory_items"] > 0) for r in rows if r["view"] == v and r["group"] == g]) for g in ("old", "clean")}
        o["c3_gap_no_memory_item"] = gap(v, "a", lambda r: r["memory_items"] == 0)
        o["c3_gap_says_unknown"] = gap(v, "a", lambda r: r["says_unknown"])
        q = [r for r in rows if r["view"] == v]
        o["c4_quotes_found"] = round(sum(r["quotes_found"] for r in q) / max(1, sum(r["quotes"] for r in q)), 3)
        o["c4_consistent"] = ci([float(r["consistent"]) for r in q if r["consistent"] is not None])
        o["c4_gap_lean_all"] = gap(v, "lean_all")
        o["c4_gap_lean_document"] = gap(v, "lean_document")
        o["c5_gap_quotes_only"] = gap(v, "b")
        o["c5_gap_a_same_items"] = gap(v, "a", lambda r: r["b"] is not None)
        o["c6_recall_given"] = {g: ci(sel(v, g, "recall_given")) for g in ("old", "clean")}
        o["c6_recall_right_when_given"] = {g: ci(sel(v, g, "recall_right")) for g in ("old", "clean")}
        o["c6_recall_median_abs_error_pts"] = {g: (statistics.median(e) if (e := sel(v, g, "recall_abs_error_pts")) else None) for g in ("old", "clean")}
        yes, no = sel(v, "old", "a", lambda r: r["recall_right"] is True), sel(v, "old", "a", lambda r: r["recall_right"] is not True)
        o["c6_a_recall_right_minus_rest_old"] = ci(yes, no) if len(yes) >= 10 and len(no) >= 10 else {"not_reported": [len(yes), len(no)]}
        o["c6_names_company_when_asked"] = {g: ci(sel(v, g, "c_names_company")) for g in ("old", "clean")}
        o["c7_gap_text_only"] = gap(v, "c_text_only")
        o["c7_gap_all"] = gap(v, "c_all")
        o["flip_is_top_weight"] = ci([float(r["flip_is_top_weight"]) for r in q if r["flip_is_top_weight"] is not None])
        out[f"view_{v}"] = o
    (OUT / "score.json").write_text(json.dumps({**out, "rows": rows}, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare-a").set_defaults(fn=prepare_a)
    sub.add_parser("prepare-bc").set_defaults(fn=prepare_bc)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
