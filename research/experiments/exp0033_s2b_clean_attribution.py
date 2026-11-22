"""EXP-0033: what makes a post-cutoff call right? Slices of existing records (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0033 (2026-11-22). No model call.
Reads EXP-0026 (raw-view call, no-document prior) and EXP-0029 (structured evidence on the raw and
the fully blinded view, and the flip question) for the 30 clean and 60 old episodes.

    conda run --no-capture-output -n nlab python research/experiments/exp0033_s2b_clean_attribution.py check
    conda run --no-capture-output -n nlab python research/experiments/exp0033_s2b_clean_attribution.py slices
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
import exp0029_s2b_rationale_audit as e29  # noqa: E402

OUT = e23.DRIVE / "s2" / "exp0033"
SEED = 20261128
CATS = (
    ("guidance and outlook", re.compile(r"\b(guidance|outlook|expects?|expected|expecting|anticipates?|anticipated|forecasts?|targets?|full[- ]year|next quarter|second half|will)\b", re.I)),
    ("orders, backlog and pipeline", re.compile(r"\b(backlog|bookings|orders|book-to-bill|pipeline|remaining performance obligations?|RPO|deferred revenue|awards|subscribers)\b", re.I)),
    ("announced changes", re.compile(r"\b(acquisitions?|acquired|acquire|divest\w*|spin-?off|price increases?|pricing actions?|launch\w*)\b", re.I)),
)
FORWARD = {c for c, _ in CATS}


CLAIM_FORWARD = re.compile(r"\b(guid\w*|outlook|full[- ]year|backlog|pipeline|bookings|orders|book-to-bill|to be installed|remaining performance)\b", re.I)
RULE = "quote"  # "claim": exploratory rule added after the hand check (registry, EXP-0033)


def category(item: dict) -> str:
    if item["source"] != "DOCUMENT":
        return item["source"]
    for name, pat in CATS:
        if item["quote"] and pat.search(item["quote"]):
            return name
    if RULE == "claim" and CLAIM_FORWARD.search(item["claim"] or ""):
        return "guidance and outlook" if re.search(r"guid|outlook|full[- ]year", item["claim"], re.I) else "orders, backlog and pipeline"
    return "this quarter's results"


def load() -> tuple[dict, dict, dict]:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    p26 = {r["id"].split(".")[0]: r["reply"] for r in e23.records(e23.ROOT / e26.RUN) if r["canary_ok"]}
    return key, p26, e29.replies()


def prob(reply: str | None, pat=e26.PROB) -> float | None:
    m = pat.search(reply or "")
    return int(m.group(1)) / 100 if m and int(m.group(1)) <= 100 else None


def check(_: argparse.Namespace) -> None:
    key, _, got = load()
    items = []
    for rid, reply in sorted(got.items()):
        if rid.startswith("s"):
            i, v = int(rid[1:4]), int(rid[-1])
            items += [{**x, "rid": rid, "cat": category(x)} for x in e29.parse_a(reply, e29.document(i, v))["items"] if x["source"] == "DOCUMENT"]
    sample = random.Random(SEED).sample(items, 25)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "check_sample.jsonl", "w", encoding="utf-8") as fh:
        for x in sample:
            fh.write(json.dumps({"rid": x["rid"], "cat": x["cat"], "quote": x["quote"], "claim": x["claim"]}, ensure_ascii=False) + "\n")
            print(f"[{x['cat']}] {x['quote']}\n    claim: {x['claim'][:160]}\n")


def slices(a: argparse.Namespace) -> None:
    global RULE, OUT
    RULE = a.rule
    if RULE == "claim":
        OUT = OUT / "rule_claim"
    key, p26, got = load()
    rng = random.Random(SEED)
    out: dict = {}

    def toward(i: int, x: float | None) -> float | None:
        return None if x is None else (x if key[i]["accelerates"] else 1 - x)

    def right(i: int, x: float | None) -> bool | None:
        return None if x is None or x == 0.5 else (x > 0.5) == key[i]["accelerates"]

    def ci(xs: list[float]) -> dict:
        if not xs:
            return {"n": 0}
        d = sorted(statistics.mean(rng.choices(xs, k=len(xs))) for _ in range(10_000))
        return {"est": round(statistics.mean(xs), 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(xs)}

    grp = {g: [i for i in key if key[i]["group"] == g] for g in ("old", "clean")}
    # 1. document against company
    for g in ("clean", "old"):
        cells = collections.Counter()
        diffs = []
        for i in grp[g]:
            r, n = prob(p26.get(f"v{i:03d}-0")), prob(p26.get(f"n{i:03d}"))
            cells[f"doc {'right' if right(i, r) else 'wrong' if right(i, r) is False else 'even'} / prior {'right' if right(i, n) else 'wrong' if right(i, n) is False else 'even'}"] += 1
            if r is not None and n is not None:
                diffs.append(toward(i, r) - toward(i, n))
        out[f"s1_document_vs_prior_{g}"] = {"cells": dict(sorted(cells.items())), "readout_raw_minus_prior": ci(diffs)}
    # 2 and 3. evidence
    rows = []
    for g in ("clean", "old"):
        for i in grp[g]:
            for v in (0, 7):
                reply = got.get(f"s{i:03d}-{v}")
                if reply is None:
                    continue
                a = e29.parse_a(reply, e29.document(i, v))
                for x in a["items"]:
                    rows.append({"group": g, "view": v, "episode": i, "cat": category(x), "weight": x["weight"],
                                 "agrees": (x["sign"] > 0) == key[i]["accelerates"], "answer_right": right(i, a["p"]),
                                 "quote": x["quote"], "claim": x["claim"], "n": x["n"]})
    for g in ("clean", "old"):
        for v in (0, 7):
            rs = [r for r in rows if r["group"] == g and r["view"] == v]
            tw = sum(r["weight"] for r in rs)
            tab = {}
            for c in ("MEMORY", "GENERAL") + tuple(FORWARD) + ("this quarter's results",):
                cs = [r for r in rs if r["cat"] == c]
                w = sum(r["weight"] for r in cs)
                tab[c] = {"items": len(cs), "weight_share": round(w / tw, 3) if tw else None,
                          "weighted_share_pointing_right": round(sum(r["weight"] for r in cs if r["agrees"]) / w, 3) if w else None,
                          "episodes_with_one": len({r["episode"] for r in cs})}
            fw = [r for r in rs if r["cat"] in FORWARD]
            w = sum(r["weight"] for r in fw)
            tab["forward-looking, all"] = {"items": len(fw), "weight_share": round(w / tw, 3) if tw else None,
                                           "weighted_share_pointing_right": round(sum(r["weight"] for r in fw if r["agrees"]) / w, 3) if w else None}
            out[f"s2_evidence_{g}_view{v}"] = tab
            share = collections.defaultdict(lambda: {"right": [], "wrong": []})
            for i in grp[g]:
                es = [r for r in rs if r["episode"] == i]
                if not es or es[0]["answer_right"] is None:
                    continue
                tot = sum(r["weight"] for r in es)
                side = "right" if es[0]["answer_right"] else "wrong"
                for lab, f in (("forward-looking", lambda r: r["cat"] in FORWARD), ("this quarter's results", lambda r: r["cat"] == "this quarter's results"),
                               ("MEMORY", lambda r: r["cat"] == "MEMORY"), ("GENERAL", lambda r: r["cat"] == "GENERAL")):
                    share[lab][side].append(sum(r["weight"] for r in es if f(r)) / tot)
            out[f"s3_weight_share_right_vs_wrong_{g}_view{v}"] = {lab: {s: ci(x) for s, x in d.items()} for lab, d in share.items()}
            # per-category direction from that category alone, against the outcome, by episode
            alone = {}
            for c in ("forward-looking", "this quarter's results", "MEMORY", "GENERAL"):
                hits = []
                for i in grp[g]:
                    es = [r for r in rs if r["episode"] == i and ((r["cat"] in FORWARD) if c == "forward-looking" else r["cat"] == c)]
                    up = sum(r["weight"] for r in es if (r["agrees"] == key[i]["accelerates"]))  # weight pointing HIGHER
                    dn = sum(r["weight"] for r in es) - up
                    if up != dn:
                        hits.append(float((up > dn) == key[i]["accelerates"]))
                alone[c] = ci(hits)
            out[f"s2b_category_alone_calls_right_{g}_view{v}"] = alone
    # 4. flip item
    for g in ("clean", "old"):
        flips = collections.defaultdict(collections.Counter)
        for i in grp[g]:
            m = re.search(r"^FLIP:\s*E(\d)", got.get(f"c{i:03d}-0", ""), re.I | re.M)
            es = [r for r in rows if r["group"] == g and r["view"] == 0 and r["episode"] == i]
            if not m or not es or es[0]["answer_right"] is None:
                continue
            hit = [r for r in es if r["n"] == int(m.group(1))]
            flips["right" if es[0]["answer_right"] else "wrong"][hit[0]["cat"] if hit else "unmatched"] += 1
        out[f"s4_flip_item_category_{g}"] = {k: dict(v) for k, v in flips.items()}
    # 5. examples
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "clean_top_items.jsonl", "w", encoding="utf-8") as fh:
        for i in grp["clean"]:
            es = sorted((r for r in rows if r["group"] == "clean" and r["view"] == 0 and r["episode"] == i), key=lambda r: -r["weight"])
            if es:
                fh.write(json.dumps({"episode": i, "accelerates": key[i]["accelerates"], "answer_right": es[0]["answer_right"],
                                     "p_raw": prob(got.get(f"s{i:03d}-0")), "p_prior": prob(p26.get(f"n{i:03d}")),
                                     "items": [{k: r[k] for k in ("cat", "weight", "agrees", "quote", "claim")} for r in es]},
                                    ensure_ascii=False) + "\n")
    (OUT / "slices.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=check)
    sl = sub.add_parser("slices")
    sl.add_argument("--rule", choices=("quote", "claim"), default="quote")
    sl.set_defaults(fn=slices)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
