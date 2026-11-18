"""EXP-0013: does the 4B stay accurate when asked for a terse worked answer?

S1-c trains the 0.8B on the 4B's answers (owner, 2026-11-18). LoRA on Qwen3.5 fits 512 tokens,
and a 400-token excerpt with its question leaves about 70 for the answer, but EXP-0011 found the
4B's correct answers run to a median of about 240 tokens. The owner chose to ask the teacher for a
terse worked answer and keep only correct answers that fit. This probe measures what that costs.

Design, fixed before the run:

* Items: 300 EarningsExam v0.2 development items from releases accepted before 2026-07-01, so
  none is in the S1-b draw. Quotas per template as S1-b scaled by half (B1 4 × 45, B2 3 × 40),
  ordered by SHA-256 of ``"exp0013:" + id``, at most 2 items per company.
* Prompts, one user turn, thinking off, greedy, the 4B at revision ``32f3e8e``:
  ``standard`` is EXP-0011's instruction; ``terse`` replaces it with ``TERSE`` below.
  At most 512 generated tokens, then EXP-0007's forced answer.
* Graded by ``exp0010.grade``. A training sequence is the chat-templated prompt plus the answer;
  it fits if prompt tokens + generated tokens (+ forced tokens) + 1 <= 512.
* Adoption rule: terse is adopted for S1-c if its accuracy is no more than 3.0 points below
  standard on the same items and at least 70% of its correct answers fit. Otherwise the owner
  chooses again. Engineering measurement, no hypothesis; 95% intervals by company bootstrap
  (2,000 resamples, seed 20261118).

    conda run --no-capture-output -n py313 python research/experiments/exp0013_terse_teacher.py run --limit 3
    conda run --no-capture-output -n py313 python research/experiments/exp0013_terse_teacher.py run
    conda run --no-capture-output -n py313 python research/experiments/exp0013_terse_teacher.py score
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0007_s1b_headroom as S  # noqa: E402
import exp0010_earnings_exam_v0_2 as V  # noqa: E402

ITEMS = V.OUT / "items_dev.jsonl"
OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0013"
MODEL = "qwen3.5-4b"
CAP = 512
SEQ = 512
QUOTA = {t: (45 if t.startswith("B1") else 40) for t in S.QUOTA}
PROMPTS = {
    "standard": S.INSTRUCTION,
    "terse": ("Answer tersely: name the table row and column you use, show any arithmetic in one "
              "line, then give the final number in \\boxed{}. No other text."),
}
BOOT, SEED = 2_000, 20261118


def pick() -> list[dict]:
    rows = [r for r in map(json.loads, open(ITEMS, encoding="utf-8")) if r["acceptance"] < S.CUTOFF]
    rows.sort(key=lambda r: hashlib.sha256(f"exp0013:{r['id']}".encode()).hexdigest())
    per_co: collections.Counter = collections.Counter()
    got: collections.Counter = collections.Counter()
    chosen = []
    for r in rows:
        t = r["template"]
        if t in QUOTA and got[t] < QUOTA[t] and per_co[r["cik"]] < 2:
            chosen.append(r)
            got[t] += 1
            per_co[r["cik"]] += 1
    assert all(got[t] == q for t, q in QUOTA.items()), dict(got)
    return chosen


def run(a: argparse.Namespace) -> None:
    import mlx.core as mx
    import mlx_lm
    from learnai.finbench import last_boxed
    from mlx_lm import load

    S.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)
    items = pick()
    if a.limit:
        items = items[: a.limit]
    mx.set_memory_limit(int(S.BUDGET_GIB * S.GIB))
    mx.set_cache_limit(S.GIB)
    model, tok = load(str(S.model_path(MODEL)))
    for variant, instruction in PROMPTS.items():
        S.INSTRUCTION = instruction
        path = OUT / ("smoke" if a.limit else "responses") / f"{variant}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        done = {json.loads(l)["id"] for l in path.read_text().splitlines()} if path.exists() and not a.limit else set()
        if a.limit and path.exists():
            path.unlink()
        for item in items:
            if item["id"] in done:
                continue
            prompt = S.build_prompt(tok, "qwen", item, "off")
            t0 = time.time()
            out, n_gen, reason = S.generate(model, tok, prompt, CAP)
            forced, cont, n_force = None, "", 0
            if reason == "length" and last_boxed(out) is None:
                forced = S.CUE
                cont, n_force, _ = S.generate(model, tok, prompt + out + forced, S.FORCE_TOKENS)
            row = {"id": item["id"], "variant": variant, "model": MODEL, "revision": S.MODELS[MODEL][1],
                   "prompt_tokens": len(tok.encode(prompt)), "generated_tokens": n_gen, "finish": reason,
                   "forced": bool(forced), "forced_tokens": n_force, "response": out + (forced or "") + cont,
                   "seconds": round(time.time() - t0, 2), "peak_gib": round(mx.get_peak_memory() / S.GIB, 2),
                   "mlx": mx.__version__, "mlx_lm": getattr(mlx_lm, "__version__", "?")}
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
            if a.limit:
                print(variant, n_gen, "|", row["response"][-240:].replace("\n", " "))


def score(_: argparse.Namespace) -> None:
    import numpy as np

    items = {it["id"]: it for it in pick()}
    ids = list(items)
    res = {}
    for variant in PROMPTS:
        rows = {r["id"]: r for r in map(json.loads, (OUT / "responses" / f"{variant}.jsonl").read_text().splitlines())}
        g = {i: V.grade(items[i], rows[i]["response"], "off") for i in ids}
        total = {i: rows[i]["prompt_tokens"] + rows[i]["generated_tokens"] + rows[i]["forced_tokens"] + 1 for i in ids}
        res[variant] = {"correct": np.array([g[i]["correct"] for i in ids], dtype=float),
                        "fits": np.array([total[i] <= SEQ for i in ids], dtype=float),
                        "gen": np.array([rows[i]["generated_tokens"] for i in ids]),
                        "forced": np.array([rows[i]["forced"] for i in ids], dtype=float),
                        "seconds": np.array([rows[i]["seconds"] for i in ids])}
    section = np.array([items[i]["section"] for i in ids])
    cos = sorted({items[i]["cik"] for i in ids})
    co_idx = {c: [k for k, i in enumerate(ids) if items[i]["cik"] == c] for c in cos}
    rng = np.random.default_rng(SEED)
    boot = [np.concatenate([co_idx[cos[j]] for j in rng.integers(0, len(cos), len(cos))]) for _ in range(BOOT)]

    def ci(v, m):
        st = [v[b][m[b]].mean() for b in boot]
        return [round(100 * float(np.percentile(st, 2.5)), 1), round(100 * float(np.percentile(st, 97.5)), 1)]

    out = {"items": len(ids), "by_template": dict(collections.Counter(items[i]["template"] for i in ids)),
           "companies": len(cos), "variants": {}}
    for variant, r in res.items():
        c, f = r["correct"], r["fits"]
        e = {}
        for sec in ("B1", "B2", "all"):
            m = section == sec if sec != "all" else np.ones(len(ids), bool)
            e[sec] = {"acc": round(100 * float(c[m].mean()), 1), "ci95": ci(c, m)}
        e["generated_tokens"] = {"median": int(np.median(r["gen"])), "p90": int(np.percentile(r["gen"], 90))}
        e["forced_rate"] = round(100 * float(r["forced"].mean()), 1)
        e["correct_and_fits"] = round(100 * float((c * f).mean()), 1)
        e["share_of_correct_that_fit"] = round(100 * float((c * f).sum() / c.sum()), 1) if c.sum() else None
        e["seconds_median"] = float(np.median(r["seconds"]))
        out["variants"][variant] = e
    d = res["terse"]["correct"] - res["standard"]["correct"]
    out["terse_minus_standard"] = {sec: {"gap": round(100 * float(d[(section == sec) if sec != "all" else slice(None)].mean()), 1),
                                         "ci95": ci(d, (section == sec) if sec != "all" else np.ones(len(ids), bool))}
                                   for sec in ("B1", "B2", "all")}
    t = out["variants"]["terse"]
    out["adopt_terse"] = bool(out["terse_minus_standard"]["all"]["gap"] >= -3.0 and (t["share_of_correct_that_fit"] or 0) >= 70.0)
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(required=True)
    r = sub.add_parser("run")
    r.add_argument("--limit", type=int, default=0, help="smoke test on the first N items; separate output")
    r.set_defaults(fn=run)
    sub.add_parser("score").set_defaults(fn=score)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
