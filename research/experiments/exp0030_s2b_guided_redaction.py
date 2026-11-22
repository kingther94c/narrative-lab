"""EXP-0030: does redaction guided by the attacker's own clues stop it? (S2-b)

Pre-registration: research/registry/experiment_registry.md, EXP-0030 (2026-11-21). The attacker
of EXP-0028 is also asked to copy out the words that gave the company away. Code removes those
words from the text and the attacker tries again: three attacks, two removals between them.

    conda run --no-capture-output -n nlab python research/experiments/exp0030_s2b_guided_redaction.py prepare
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py emit --run exp0030 --items <items_r1>
    conda run --no-capture-output -n nlab python research/experiments/exp0027_s2a_cli_dispatch_v2.py run --run exp0030
    conda run --no-capture-output -n nlab python research/experiments/exp0023_s2a_dispatch.py ingest --run exp0030
    conda run --no-capture-output -n nlab python research/experiments/exp0030_s2b_guided_redaction.py advance --round 1
    (emit, run, ingest with <items_r2>; advance --round 2; emit, run, ingest with <items_r3>)
    conda run --no-capture-output -n nlab python research/experiments/exp0030_s2b_guided_redaction.py score
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

OUT = e23.DRIVE / "s2" / "exp0030"
RUN = "exp0030"
SEED = 20261125
ROUNDS = 3
KINDS = ("PERSON", "BRAND", "PLACE", "NUMBER", "EVENT", "OTHER")

PROMPT = e28.PROMPT.rstrip("\n") + """
Then list up to 20 words or phrases, strongest first, each copied exactly from the text, that helped you identify the company or the quarter, one per line:
T1 | <PERSON, BRAND, PLACE, NUMBER, EVENT or OTHER> | <the word or phrase, at most eight words>
T2 | ...

"""

TERM = re.compile(r"^T\d{1,2}\s*\|\s*(" + "|".join(KINDS) + r")\s*\|\s*(.+?)\s*$", re.I | re.M)


def doc_path(r: int, i: int) -> Path:
    return OUT / f"round{r}" / f"{i:03d}.txt"


def write_round(r: int, docs: dict[int, str]) -> None:
    (OUT / f"round{r}").mkdir(parents=True, exist_ok=True)
    with open(OUT / f"items_r{r}.jsonl", "w", encoding="utf-8") as fh:
        for i, doc in sorted(docs.items()):
            doc_path(r, i).write_text(doc, encoding="utf-8")
            fh.write(json.dumps({"id": f"r{r}-{i:03d}", "agent": e28.AGENT, "prompt": PROMPT + doc}, ensure_ascii=False) + "\n")
    print(f"[round {r}] {len(docs)} items -> {OUT / f'items_r{r}.jsonl'}")


def prepare(_: argparse.Namespace) -> None:
    e23.need_drive()
    write_round(1, {k["episode"]: e29.document(k["episode"], 7) for k in e26.load(e26.OUT / "key.jsonl")})


def replies(r: int) -> dict[int, str]:
    out = {}
    for rec in e23.records(e23.ROOT / RUN):
        if rec["canary_ok"] and rec["id"].startswith(f"r{r}-"):
            out[int(rec["id"].split(".")[0].split("-")[1])] = rec["reply"]
    return out


def fold(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def hit(line: str, k: dict) -> bool:
    """EXP-0028's rule, plus a match after folding case and punctuation (EXP-0029: it scored
    "HP Inc.", "C.H. Robinson" and "PG&E" as misses)."""
    if e28.hit(line, k):
        return True
    core = fold(re.sub(r",?\s+(inc|corp|corporation|co|ltd|plc|llc|group|holdings)\b\.?.*$", "", k["name"], flags=re.I))
    return len(core) >= 2 and core in fold(line)


def read(reply: str, k: dict) -> dict:
    g = {m.group(1): m.group(2) for m in re.finditer(r"COMPANY_([123]):\s*(.*)", reply)}
    q = re.search(r"QUARTER_END:\s*(\d{4})-(\d{2})", reply)
    c = re.search(r"CONFIDENCE:\s*(\d{1,3})", reply)
    return {"top1": hit(g.get("1", ""), k), "top3": any(hit(g.get(j, ""), k) for j in "123"),
            "quarter": bool(q) and f"{q.group(1)}-{q.group(2)}" == k["quarter_end"][:7],
            "confidence": int(c.group(1)) if c else None,
            "terms": [(m.group(1).upper(), m.group(2).strip().strip('"')) for m in TERM.finditer(reply)]}


def redact(doc: str, terms: list[tuple[str, str]]) -> tuple[str, list[dict]]:
    log = []
    for kind, term in sorted(terms, key=lambda t: -len(t[1])):
        forms = [term]
        if kind == "PERSON" and len(term.split()) >= 2 and len(term.split()[-1]) >= 4:
            forms.append(term.split()[-1])
        n = 0
        for f in forms:
            if not 3 <= len(f) <= 80:
                continue
            pat = r"(?<![A-Za-z0-9])" + r"\s+".join(re.escape(w) for w in f.split()) + r"(?![A-Za-z0-9])"
            doc, m = re.subn(pat, "[number]" if kind == "NUMBER" else "[removed]", doc, flags=re.I)
            n += m
        log.append({"kind": kind, "term": term, "replaced": n})
    return doc, log


def advance(a: argparse.Namespace) -> None:
    e23.need_drive()
    r = a.round
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    got = replies(r)
    nxt, logs = {}, []
    for i, reply in sorted(got.items()):
        x = read(reply, key[i])
        doc = doc_path(r, i).read_text(encoding="utf-8")
        new, log = redact(doc, x["terms"])
        logs.append({"episode": i, "round": r, "top3": x["top3"], "chars_before": len(doc), "chars_after": len(new), "terms": log})
        if x["top3"]:  # an episode the attacker missed leaves the loop and counts as a miss from here on
            nxt[i] = new
    with open(OUT / f"redaction_r{r}.jsonl", "w", encoding="utf-8") as fh:
        for l in logs:
            fh.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(f"[advance] round {r}: {len(got)} replies, {len(nxt)} still recognised")
    if r < ROUNDS:
        write_round(r + 1, nxt)


def score(_: argparse.Namespace) -> None:
    key = {k["episode"]: k for k in e26.load(e26.OUT / "key.jsonl")}
    rng = random.Random(SEED)

    def rate(v: list[float]) -> dict:
        d = sorted(statistics.mean(rng.choices(v, k=len(v))) for _ in range(10_000))
        return {"rate": round(statistics.mean(v), 3), "ci90": [round(d[499], 3), round(d[9499], 3)], "n": len(v)}

    cells = {"all": lambda k: True, "old": lambda k: k["group"] == "old", "clean": lambda k: k["group"] == "clean",
             "old top 50": lambda k: k["group"] == "old" and k["tier"] == "top 50",
             "old 51 to 250": lambda k: k["group"] == "old" and k["tier"] == "51 to 250"}
    out: dict = {}
    rows = []
    for r in range(1, ROUNDS + 1):
        got = {i: read(t, key[i]) for i, t in replies(r).items()}
        asked = sum(1 for _ in open(OUT / f"items_r{r}.jsonl", encoding="utf-8")) if (OUT / f"items_r{r}.jsonl").exists() else 0
        o: dict = {"asked": asked, "answered": len(got)}
        for name, f in cells.items():
            ids = [i for i, k in key.items() if f(k)]
            o[name] = {m: rate([float(i in got and got[i][m]) for i in ids]) for m in ("top1", "top3", "quarter")}
        conf = [x["confidence"] for x in got.values() if x["confidence"] is not None]
        o["median_confidence_when_asked"] = statistics.median(conf) if conf else None
        p = OUT / f"redaction_r{r}.jsonl"
        if p.exists():
            logs = e26.load(p)
            terms = [t for l in logs for t in l["terms"]]
            o["terms_listed"] = len(terms)
            o["terms_found_verbatim"] = round(sum(t["replaced"] > 0 for t in terms) / max(1, len(terms)), 3)
            o["terms_by_kind"] = dict(collections.Counter(t["kind"] for t in terms))
            o["median_share_of_characters_removed"] = round(statistics.median(1 - l["chars_after"] / l["chars_before"] for l in logs), 4)
        out[f"round_{r}"] = o
        rows += [{"round": r, "episode": i, **{m: x[m] for m in ("top1", "top3", "quarter", "confidence")}} for i, x in got.items()]
    last = out[f"round_{ROUNDS}"]["all"]["top1"]["rate"]
    out["criterion_1"] = "stopped" if last <= 0.20 else "not stopped" if last >= 0.50 else "undecided"
    (OUT / "score.json").write_text(json.dumps({**out, "rows": rows}, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").set_defaults(fn=prepare)
    s = sub.add_parser("advance")
    s.add_argument("--round", type=int, required=True, choices=range(1, ROUNDS + 1))
    s.set_defaults(fn=advance)
    sub.add_parser("score").set_defaults(fn=score)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
