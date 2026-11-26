"""EXP-0056: data factory step 3, teacher chains over EXP-0055's pool, verified by rule (S1 re-plan).

Re-plan §4.1: the teacher works through the analysis graph; every extracted figure and computed
number is checked; failed traces are dropped. This script holds the parts that need no model
(answer parsing, grading, arithmetic and figure checks: ``check``), the throughput check
(``speed``), generation (``generate``) and verification (``verify``). Generation rules and sizes
are fixed in the main pre-registration before ``generate`` runs at scale.

Teacher (proposed in the pre-registration): the released Qwen3.5-4B without the calculator,
sampled in batches, thinking off, the item's prompt after a short procedure instruction that the
student never sees. The 4B and the 4B with the inline calculator scored alike on section R
(EXP-0050: 82.0 and 82.2) and batching needs uninterrupted decoding, so arithmetic is checked
after generation instead of during it: every "expression = value" the inline calculator rule of
EXP-0018 would have caught must show the value the calculator would compute, to the precision
written or within 0.01% of it (a ratio may be written as a percentage; date-shaped expressions
such as 3/21/2020 are skipped).

A chain is kept only if (1) it finished; (2) its final answer, read in the item's format, is
right; (3) every checked calculation is right; and (4) for an answerable item, each needed
table row has its current or prior-year figure quoted. Up to two distinct kept chains per item.

    conda run --no-capture-output -n py313 python research/experiments/exp0056_s1f_chains.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0056_s1f_chains.py speed --n 16 --batch 8
    conda run --no-capture-output -n py313 python research/experiments/exp0056_s1f_chains.py generate --items 200 --k 4 --batch 8 --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0056_s1f_chains.py verify --dir pilot
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as D14  # noqa: E402  (frozen; load_model, the teacher key, sampling)
import exp0016_s1c_calculator as C16  # noqa: E402  (frozen; the arithmetic parser)
import exp0018_s1c_calculator_inline as C18  # noqa: E402  (frozen; the inline rule; sets C16.find_call)
import exp0055_s1f_items as I55  # noqa: E402  (frozen; the pool)

E = I55.E
OUT = E.DRIVE / "s1" / "exp0056"
TEACHER = D14.TEACHER
CAP = 768
TEMP, TOP_P = D14.TEMP, D14.TOP_P
SEED0 = 20261127
KEEP_PER_ITEM = 2
UNDET = I55.UNDET
PROCEDURE = ("Work through this as a financial analyst would, in short steps. First name each table row and "
             "column you use and write its figure for each period. Then write each calculation as an expression "
             "followed by = and its result. Then say in one sentence what the figures show. Finish with the "
             "final answer exactly as the question asks.")


# ---------------------------------------------------------------------------------------------
# Reading answers

def norm(s: str) -> str:
    s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s or "")
    s = re.sub(r"[\"'*`$\\]|\.$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip().lower().rstrip(".")


def final_answer(text: str, fmt: str) -> str | None:
    from learnai.finbench import last_boxed

    if fmt == "boxed":
        return last_boxed(text)
    if fmt == "answer_line":
        hits = re.findall(r"^\W*answer\W*:\s*(.+?)\s*$", text, re.I | re.M)
        return hits[-1] if hits else None
    if fmt == "json":
        for m in reversed(list(re.finditer(r"\{[^{}]*\"answer\"[^{}]*\}", text))):
            try:
                return str(json.loads(m.group(0))["answer"])
            except (ValueError, KeyError):
                continue
        return None
    if fmt == "sentence":
        body = text.strip()
        parts = re.split(r"(?<=[.!?])\s+", body)
        return parts[-1] if parts else None
    raise ValueError(fmt)


NUMBER = re.compile(r"-?\(?\$?\s?\d[\d,]*(?:\.\d+)?\)?|-?\.\d+")


def to_number(s: str) -> float | None:
    s = s.replace("−", "-")
    m = NUMBER.search(s)
    if not m:
        return None
    tok = m.group(0)
    neg = tok.startswith("-") or tok.startswith("(") and tok.endswith(")")
    v = float(re.sub(r"[^\d.]", "", tok) or "nan")
    return -v if neg else v


def pick_option(ans: str, options: list[str]) -> str | None:
    """The one option the answer names, longest match first; None if none or two different ones."""
    a = norm(ans)
    if a in [norm(o) for o in options]:
        return next(o for o in options if norm(o) == a)
    found = []
    rest = a
    for o in sorted(options, key=lambda o: -len(o)):
        if re.search(rf"(?<![a-z]){re.escape(norm(o))}(?![a-z])", rest):
            found.append(o)
            rest = rest.replace(norm(o), " ")
    return found[0] if len(found) == 1 else None


def grade(item: dict, text: str) -> dict:
    if item["atype"] == "table":
        got = {}
        for cond in item["gold"]:
            m = re.findall(rf"^\W*{re.escape(cond)}\s*:\s*(.+?)\s*$", text, re.I | re.M)
            got[cond] = norm(m[-1]) if m else None
        right = sum(got[c] == norm(v) for c, v in item["gold"].items())
        return {"answer": got, "correct": right == len(item["gold"]), "parts_right": right, "parts": len(item["gold"])}
    ans = final_answer(text, item["format"])
    if ans is None:
        return {"answer": None, "correct": False}
    says_undet = UNDET in norm(ans)
    if item["atype"] == "undetermined":
        return {"answer": ans, "correct": says_undet}
    if says_undet:
        return {"answer": ans, "correct": False}
    if item["atype"] == "number":
        v = to_number(ans)
        return {"answer": ans, "value": v, "correct": v is not None and abs(v - item["gold"]) <= item["tol"]["abs"] + 1e-9}
    opt = pick_option(ans, item["options"])
    return {"answer": ans, "option": opt, "correct": opt is not None and norm(opt) == norm(item["gold"])}


# ---------------------------------------------------------------------------------------------
# Checking the working

DATE = re.compile(r"^\(?\d{1,2}\s*/\s*\d{1,2}\s*/\s*\d{2,4}\)?$")
REL_TOL = 1e-4  # the 4B's long divisions often drift in the fifth or sixth significant digit
WRITTEN = re.compile(r"\s*(?:\\approx|≈|=)?\s*\$?\s*(-?\d[\d,]*(?:\.\d+)?)\s*(\\?%)?")


def arithmetic(text: str) -> list[dict]:
    """Each calculation EXP-0018's inline rule finds, with the value written after it and a verdict."""
    out, pos = [], 0
    while True:
        hit = C18.find_call_inline(text, pos)
        if hit is None:
            return out
        end, expr, value, _ = hit
        pos = end
        if DATE.match(expr.replace(" ", "")):
            continue  # "3/21/2020" is a date, not a division
        m = WRITTEN.match(text, end)
        if not m:
            out.append({"expr": expr, "value": value, "written": None, "ok": None})
            continue
        w = float(m.group(1).replace(",", ""))
        dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
        slack = 0.5 * 10 ** (-dec) + 1e-9
        ok = (abs(w - value) <= slack + REL_TOL * abs(value)
              or (m.group(2) is not None and abs(w - 100 * value) <= slack + REL_TOL * abs(100 * value)))
        out.append({"expr": expr, "value": value, "written": w, "percent": m.group(2) is not None, "ok": ok})


def shown_forms(v: float, dec: int) -> set[str]:
    """How a displayed table figure may be quoted: with or without thousands separators, sign or parentheses."""
    a = abs(v)
    s = f"{a:,.{dec}f}"
    return {s, s.replace(",", "")}


def figures_quoted(item: dict, sheet: dict, text: str) -> dict:
    """For each needed row, whether its current or prior-year displayed figure appears in the chain."""
    rows = {f["line"]: f for f in sheet["figures"].values()}
    res = {}
    for line in item["need"]:
        f = rows.get(line)
        if f is None:
            continue
        prior = f["vals"][f["prior_col"]][0] if f.get("prior_col") is not None else None
        forms = shown_forms(f["shown"], f["dec"]) | (shown_forms(prior, f["prior_dec"]) if prior is not None else set())
        res[f["metric"]] = any(re.search(rf"(?<![\d.,]){re.escape(x)}(?![\d]|\.\d)", text) for x in forms)
    return res


def verify_one(item: dict, sheet: dict, row: dict) -> dict:
    text = row["response"]
    g = grade(item, text)
    ar = arithmetic(text)
    fq = figures_quoted(item, sheet, text) if item["atype"] != "undetermined" else {}
    checks = {"finished": row["finish"] == "stop", "answer": g["correct"],
              "arithmetic": all(a["ok"] is not False for a in ar), "figures": all(fq.values())}
    return {"id": item["id"], "sample": row["sample"], "keep": all(checks.values()), "checks": checks, "grade": g,
            "calcs": len(ar), "calcs_wrong": sum(a["ok"] is False for a in ar), "figures_quoted": fq}


# ---------------------------------------------------------------------------------------------
# Generation

def teacher_prompt(tok, item: dict) -> str:
    return tok.apply_chat_template([{"role": "user", "content": PROCEDURE + "\n\n" + item["prompt"]}],
                                   add_generation_prompt=True, tokenize=False, enable_thinking=False)


def pool(n: int | None = None) -> list[dict]:
    items = [json.loads(l) for l in open(I55.OUT / "pool.jsonl", encoding="utf-8")]
    items.sort(key=lambda r: r["rank"])
    return items[:n] if n else items


def run_batches(model, tok, items: list[dict], k: int, batch: int, path: Path, seed0: int) -> dict:
    import mlx.core as mx
    from mlx_lm.generate import batch_generate
    from mlx_lm.sample_utils import make_sampler

    done = set()
    if path.exists():
        done = {json.loads(l)["id"] for l in open(path, encoding="utf-8")}
    jobs = [(it, s) for it in items if it["id"] not in done for s in range(k)]
    stats = {"samples": 0, "tokens": 0, "seconds": 0.0, "peak_gib": 0.0}
    with open(path, "a", encoding="utf-8") as fh:
        for b in range(0, len(jobs), batch):
            chunk = jobs[b:b + batch]
            ids = [tok.encode(teacher_prompt(tok, it)) for it, _ in chunk]
            mx.random.seed(seed0 + b)
            t0 = time.time()
            res = batch_generate(model, tok, ids, max_tokens=CAP, sampler=make_sampler(temp=TEMP, top_p=TOP_P),
                                 return_token_ids=True)
            secs = time.time() - t0
            for (it, s), text, toks, p in zip(chunk, res.texts, res.token_ids, ids):
                fh.write(json.dumps({"id": it["id"], "sample": s, "seed": seed0 + b, "prompt_tokens": len(p),
                                     "generated_tokens": len(toks), "finish": "length" if len(toks) >= CAP else "stop",
                                     "response": text, "batch_seconds": round(secs, 2)}) + "\n")
                stats["tokens"] += len(toks)
            fh.flush()
            stats["samples"] += len(chunk)
            stats["seconds"] += secs
            stats["peak_gib"] = max(stats["peak_gib"], mx.get_peak_memory() / 2 ** 30)
    return stats


def speed(a):
    if not E.DRIVE.exists():
        sys.exit("external drive not mounted")
    model, tok = D14.load_model(TEACHER)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for bs in [int(x) for x in a.batch.split(",")]:
        path = OUT / "speed" / f"b{bs}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        st = run_batches(model, tok, pool(a.n), 1, bs, path, SEED0)
        rows.append({"batch": bs, **st, "samples_per_hour": round(3600 * st["samples"] / st["seconds"]),
                     "tokens_per_second": round(st["tokens"] / st["seconds"], 1)})
        print(json.dumps(rows[-1]), flush=True)
    (OUT / "speed" / "speed.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


def generate(a):
    model, tok = D14.load_model(TEACHER)
    OUT.mkdir(parents=True, exist_ok=True)
    base = OUT / a.dir
    base.mkdir(parents=True, exist_ok=True)
    st = run_batches(model, tok, pool(a.items), a.k, a.batch, base / "samples.jsonl", SEED0)
    print(json.dumps(st), flush=True)


def verify(a):
    items = {it["id"]: it for it in pool()}
    need = {it["accession"] for it in items.values()}
    sheets = {}
    for l in open(I55.S54.SHEETS, encoding="utf-8"):
        s = json.loads(l)
        if s["accession"] in need:
            sheets[s["accession"]] = s
    base = OUT / a.dir
    rows = [json.loads(l) for l in open(base / "samples.jsonl", encoding="utf-8")]
    res = [verify_one(items[r["id"]], sheets[items[r["id"]]["accession"]], r) for r in rows]
    kept = collections.defaultdict(list)
    for r, v in zip(rows, res):
        if v["keep"] and r["response"] not in [x["response"] for x in kept[r["id"]]] and len(kept[r["id"]]) < KEEP_PER_ITEM:
            kept[r["id"]].append(r)
    with open(base / "verified.jsonl", "w", encoding="utf-8") as fh:
        for v in res:
            fh.write(json.dumps(v) + "\n")
    with open(base / "kept.jsonl", "w", encoding="utf-8") as fh:
        for i, rs in kept.items():
            for r in rs:
                fh.write(json.dumps({"id": i, "sample": r["sample"], "response": r["response"]}) + "\n")
    by_kind = collections.defaultdict(lambda: collections.Counter())
    for r, v in zip(rows, res):
        k = items[r["id"]]["kind"]
        by_kind[k]["samples"] += 1
        for c, ok in v["checks"].items():
            by_kind[k][f"fail {c}"] += not ok
        by_kind[k]["kept"] += v["keep"]
    rep = {"samples": len(rows), "items": len({r["id"] for r in rows}), "items with a kept chain": len(kept),
           "chains kept": sum(len(x) for x in kept.values()),
           "by kind": {k: dict(c) for k, c in sorted(by_kind.items())},
           "tokens per sample, mean": round(sum(r["generated_tokens"] for r in rows) / max(1, len(rows)))}
    (base / "verify_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


# ---------------------------------------------------------------------------------------------

def check(_):
    it_n = {"atype": "number", "format": "boxed", "gold": -1.2732, "tol": {"abs": 0.15}}
    it_l = {"atype": "label", "format": "sentence", "gold": "both rose", "options": ["both rose", "both fell",
            "revenue rose and net income fell", "revenue fell and net income rose"]}
    it_j = {"atype": "label", "format": "json", "gold": "more slowly", "options": ["more quickly", "more slowly"]}
    it_u = {"atype": "undetermined", "format": "answer_line", "gold": UNDET}
    it_t = {"atype": "table", "gold": {"gross margin": "contracted", "revenue and operating income": "both rose"}}
    cases = [
        (grade(it_n, "so the change is \\boxed{-1.3}")["correct"], True),
        (grade(it_n, "\\boxed{1.3}")["correct"], False),
        (grade(it_n, "\\boxed{(1.3)}")["correct"], True),
        (grade(it_l, "Revenue and net income both rose.")["correct"], True),
        (grade(it_l, "So revenue rose and net income fell.")["correct"], False),
        (grade(it_j, 'Net income fell. {"answer": "more slowly"}')["correct"], True),
        (grade(it_j, '{"answer": "more quickly"}')["correct"], False),
        (grade(it_u, "No such period.\nAnswer: Cannot be determined")["correct"], True),
        (grade(it_u, "Answer: 12.5")["correct"], False),
        (grade(it_t, "Gross margin: contracted\nRevenue and operating income: both rose")["correct"], True),
        (grade(it_t, "- gross margin: flat\n- revenue and operating income: both rose")["correct"], False),
        ([a["ok"] for a in arithmetic("Margin: 1,234 / 5,678 = 0.2173, so")], [True]),
        ([a["ok"] for a in arithmetic("Margin: 1,234 / 5,678 = 21.7%")], [True]),
        ([a["ok"] for a in arithmetic("Growth: (120 - 100) / 100 = 0.25")], [False]),
        ([a["ok"] for a in arithmetic("Change: 41,118 - 38,053 = 3,065 million")], [True]),
        ([a["ok"] for a in arithmetic("Margin: (1302 / 10377) * 100 = 12.5474")], [True]),     # drift in the 6th digit
        ([a["ok"] for a in arithmetic("Growth: ((1302 - 1375)/(1375)) = -5.29%")], [False]),   # -5.31 really
        ([a["ok"] for a in arithmetic("Margin: ((-2043)/(21713)) * 100 = -0.094089")], [False]),
        (arithmetic("Dated 3/21/2020 = 13881"), []),
    ]
    bad = [(i, got, want) for i, (got, want) in enumerate(cases) if got != want]
    print("cases:", len(cases), "failures:", bad)
    sheet = {"figures": {"revenue": {"metric": "revenue", "line": 5, "shown": 41118.0, "dec": 0, "prior_dec": 0,
                                     "prior_col": 1, "vals": [[41118.0, 0, 5], [38053.0, 0, 5]]}}}
    print("figures quoted:", figures_quoted({"need": [5]}, sheet, "Net sales were $41,118 million"), "(want revenue True)",
          figures_quoted({"need": [5]}, sheet, "Net sales were $41,1180 million"), "(want revenue False)")
    print("teacher instruction:", PROCEDURE)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    sub.add_parser("check").set_defaults(fn=check)
    s = sub.add_parser("speed"); s.add_argument("--n", type=int, default=16); s.add_argument("--batch", default="1,8")
    s.set_defaults(fn=speed)
    g = sub.add_parser("generate"); g.add_argument("--items", type=int, default=200); g.add_argument("--k", type=int, default=4)
    g.add_argument("--batch", type=int, default=8); g.add_argument("--dir", default="")
    g.set_defaults(fn=generate)
    v = sub.add_parser("verify"); v.add_argument("--dir", default=""); v.set_defaults(fn=verify)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
