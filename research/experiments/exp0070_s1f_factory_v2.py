"""EXP-0070: data factory v2 for S1's main experiment: short items, short chains, general data.

Owner decisions of 2026-11-26 (changelog; re-plan §4.5): every training sequence is at most 640
tokens (EXP-0058: about 405 sequences an hour at 8.69 GiB), excerpts are cut to B's 300-token
budget, the teacher is the plain 4B with arithmetic checked after generation (EXP-0056), and 20%
of each trained arm's examples are general: half math word problems with the released 0.8B's own
correct answers, half B training items with the 4B's standard answers. An engineering step with
no hypothesis. Sizes, mixes and decision rules are fixed in the main pre-registration (EXP-0059)
before anything here runs at scale; a pilot may run first.

Fixed here:

* **Pool** (``build``): EXP-0055's item maker, unchanged (kinds, quotas, wording, answer formats;
  diluted EPS and pre-tax income held out), with the excerpt budget at 300 tokens instead of R's
  800. Ids are new ("Fv2|accession|kind"). Output ``s1/exp0070/pool.jsonl``.
* **Chains** (``chains``, ``verify``): the plain 4B in batches, thinking off, sampled as in
  EXP-0056 (temperature 0.7, top-p 0.95), after the instruction BRIEF, which the student never
  sees. Each sample's token cap is 640 less the student's prompt (the item prompt in the chat
  template, thinking off) less one for the end token, and at most 320; an item whose prompt
  leaves fewer than 64 tokens is skipped. A chain is kept by EXP-0056's four checks (finished,
  right answer in the item's format, every checked calculation right, needed figures quoted) and
  only if the student's sequence (prompt, chain, end token, as EXP-0058 builds it) fits 640.
* **Math** (``math``): word problems with a numeric reference answer, in a seeded order: GSM8K
  training problems (reference after "####") and MATH training problems (the reference's last
  \\boxed{}, kept if a plain number or a simple fraction), from the files given (default: the
  copies in learning_ai's cache, 300 GSM8K and 700 MATH). The released 0.8B, thinking off, the
  problem then MATH_INSTRUCTION; the first answer greedy, any further ones sampled; kept if it
  finished, its last \\boxed{} equals the reference (to 1e-6 relative) and the sequence fits 640.
* **B** (``bstd``): EXP-0014's B training items (300-token excerpts), in a seeded order. The 4B
  with EXP-0007's standard instruction, thinking off, greedy; kept if EXP-0010's grader marks it
  right and it finished within the cap (640 less the prompt, at most 320). The student sees the
  same prompt.

Every document here is a training company's, before the cutoff, so Claude may read items and
outputs. Outputs stay on the drive.

    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py check
    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py build
    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py chains --items 200 --k 4 --batch 16 --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py verify --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py math --n 1000 --batch 16 --dir pilot
    conda run --no-capture-output -n py313 python research/experiments/exp0070_s1f_factory_v2.py bstd --n 200 --batch 16 --dir pilot
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as D14  # noqa: E402  (frozen; models, B training items, standard prompt)
import exp0056_s1f_chains as X56  # noqa: E402  (frozen; answer reading and chain verification)

I55 = X56.I55
E, S = I55.E, D14.S
E.MAX_TOKENS = 300  # B's excerpt budget (EXP-0014); owner decision 2026-11-26
OUT = E.DRIVE / "s1" / "exp0070"
I55.OUT = OUT  # EXP-0055's build writes, and EXP-0056's pool() reads, this folder's pool
SEQ, CHAIN_MAX, MIN_ROOM = 640, 320, 64
SEED0 = 20261128
KEEP_PER_ITEM = 2
BRIEF = ("Answer briefly, in a few short lines. Write each figure you use with its period, as printed in the "
         "table. Write each calculation as an expression followed by = and its result. Then give the final "
         "answer exactly as the question asks. Nothing else.")
MATH_INSTRUCTION = "Solve this step by step, then give the final number in \\boxed{}."
LAI = Path("/Volumes/Seagate Backup Plus Drive/DATA/learning_ai/data/cache/mathbench")
MATH_FILES = [LAI / "openai--gsm8k--main--train.jsonl"] + sorted(LAI.glob("EleutherAI--hendrycks_math--*--train.jsonl"))


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8")] if path.exists() else []


def chat(tok, text: str) -> str:
    return tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True,
                                   tokenize=False, enable_thinking=False)


def room(n_prompt: int) -> int:
    """Token cap for a response after a student prompt of n_prompt tokens."""
    return min(CHAIN_MAX, SEQ - n_prompt - 1)


def fits(tok, student_prompt: str, response: str) -> int:
    """The student's sequence length as EXP-0058 builds it: prompt, response, end token."""
    return len(tok.encode(student_prompt)) + len(tok.encode(response)) + 1


def need_drive():
    if not E.DRIVE.exists():
        sys.exit("external drive not mounted")


def generate(model, tok, jobs: list[dict], batch: int, path: Path, sampler_for) -> dict:
    """jobs: {key, prompt (teacher text), cap, sample}; appends one row a job to path."""
    import mlx.core as mx
    from mlx_lm.generate import batch_generate

    stats = {"samples": 0, "tokens": 0, "seconds": 0.0, "peak_gib": 0.0}
    with open(path, "a", encoding="utf-8") as fh:
        for b in range(0, len(jobs), batch):
            chunk = jobs[b:b + batch]
            ids = [tok.encode(j["prompt"]) for j in chunk]
            caps = [j["cap"] for j in chunk]
            mx.random.seed(SEED0 + b)
            t0 = time.time()
            res = batch_generate(model, tok, ids, max_tokens=caps, sampler=sampler_for(chunk), return_token_ids=True)
            secs = time.time() - t0
            for j, text, toks in zip(chunk, res.texts, res.token_ids):
                fh.write(json.dumps({**j["key"], "sample": j["sample"], "seed": SEED0 + b, "cap": j["cap"],
                                     "generated_tokens": len(toks),
                                     "finish": "length" if len(toks) >= j["cap"] else "stop", "response": text}) + "\n")
                stats["tokens"] += len(toks)
            fh.flush()
            stats["samples"] += len(chunk)
            stats["seconds"] += secs
            stats["peak_gib"] = max(stats["peak_gib"], mx.get_peak_memory() / 2 ** 30)
    if stats["seconds"]:
        stats["samples_per_hour"] = round(3600 * stats["samples"] / stats["seconds"])
    return stats


def sampled(_chunk):
    from mlx_lm.sample_utils import make_sampler

    return make_sampler(temp=X56.TEMP, top_p=X56.TOP_P)


def greedy(_chunk):
    from mlx_lm.sample_utils import make_sampler

    return make_sampler(temp=0.0)


# ---------------------------------------------------------------------------------------------
# Pool and chains

def build(a):
    need_drive()
    I55.build(argparse.Namespace(pool=a.pool))
    rows = jl(OUT / "pool.jsonl")
    for r in rows:
        r["id"] = hashlib.sha256(f"Fv2|{r['accession']}|{r['kind']}".encode()).hexdigest()[:16]
    assert len({r["id"] for r in rows}) == len(rows)
    with open(OUT / "pool.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"{len(rows)} items, ids rewritten to Fv2")


def chains(a):
    need_drive()
    model, tok = D14.load_model(D14.TEACHER)
    base = OUT / "chains" / a.dir
    base.mkdir(parents=True, exist_ok=True)
    path = base / "samples.jsonl"
    done = {r["id"] for r in jl(path)}
    jobs, skipped = [], 0
    for it in X56.pool(a.items):
        if it["id"] in done:
            continue
        cap = room(len(tok.encode(chat(tok, it["prompt"]))))
        if cap < MIN_ROOM:
            skipped += 1
            continue
        jobs += [{"key": {"id": it["id"]}, "prompt": chat(tok, BRIEF + "\n\n" + it["prompt"]), "cap": cap, "sample": s}
                 for s in range(a.k)]
    st = generate(model, tok, jobs, a.batch, path, sampled)
    print(json.dumps({**st, "items skipped, prompt too long": skipped}), flush=True)


def verify(a):
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(str(S.model_path(D14.STUDENT)))
    items = {it["id"]: it for it in X56.pool()}
    base = OUT / "chains" / a.dir
    rows = jl(base / "samples.jsonl")
    need = {items[r["id"]]["accession"] for r in rows}
    sheets = {s["accession"]: s for s in map(json.loads, open(I55.S54.SHEETS, encoding="utf-8")) if s["accession"] in need}
    res = []
    for r in rows:
        it = items[r["id"]]
        v = X56.verify_one(it, sheets[it["accession"]], r)
        v["seq_tokens"] = fits(tok, chat(tok, it["prompt"]), r["response"])
        v["checks"]["fits"] = v["seq_tokens"] <= SEQ
        v["keep"] = all(v["checks"].values())
        res.append(v)
    kept = collections.defaultdict(list)
    for r, v in zip(rows, res):
        if v["keep"] and r["response"] not in [x["response"] for x in kept[r["id"]]] and len(kept[r["id"]]) < KEEP_PER_ITEM:
            kept[r["id"]].append({**r, "seq_tokens": v["seq_tokens"]})
    with open(base / "verified.jsonl", "w", encoding="utf-8") as fh:
        for v in res:
            fh.write(json.dumps(v) + "\n")
    with open(base / "kept.jsonl", "w", encoding="utf-8") as fh:
        for i, rs in kept.items():
            for r in rs:
                fh.write(json.dumps({"id": i, "sample": r["sample"], "seq_tokens": r["seq_tokens"],
                                     "response": r["response"]}) + "\n")
    by_kind = collections.defaultdict(collections.Counter)
    for r, v in zip(rows, res):
        k = items[r["id"]]["kind"]
        by_kind[k]["samples"] += 1
        for c, ok in v["checks"].items():
            by_kind[k][f"fail {c}"] += not ok
        by_kind[k]["kept"] += v["keep"]
    for i in {r["id"] for r in rows}:
        by_kind[items[i]["kind"]]["items"] += 1
        by_kind[items[i]["kind"]]["items with a kept chain"] += i in kept
    seq = sorted(x["seq_tokens"] for rs in kept.values() for x in rs)
    gen = sorted(r["generated_tokens"] for r in rows)
    rep = {"samples": len(rows), "items": len({r["id"] for r in rows}), "items with a kept chain": len(kept),
           "chains kept": len(seq), "samples kept": sum(v["keep"] for v in res),
           "generated tokens median / p90": [gen[len(gen) // 2], gen[9 * len(gen) // 10]] if gen else None,
           "kept sequence tokens median / p90": [seq[len(seq) // 2], seq[9 * len(seq) // 10]] if seq else None,
           "by kind": {k: dict(c) for k, c in sorted(by_kind.items())}}
    (base / "verify_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


# ---------------------------------------------------------------------------------------------
# General data

FRAC = re.compile(r"^-?\\[dt]?frac\{(-?\d+)\}\{(\d+)\}$")
PLAIN = re.compile(r"^-?\d[\d,]*(?:\.\d+)?$|^-?\.\d+$")


def math_reference(rec: dict) -> float | None:
    """The numeric reference answer of a GSM8K or MATH record, or None if not a plain number or fraction."""
    from learnai.finbench import last_boxed

    if "answer" in rec and "####" in rec["answer"]:
        ref = rec["answer"].rsplit("####", 1)[1].strip()
    elif "solution" in rec:
        ref = (last_boxed(rec["solution"]) or "").strip()
    else:
        return None
    ref = ref.replace("$", "").replace(" ", "").rstrip(".")
    m = FRAC.match(ref)
    if m:
        v = int(m.group(1)) / int(m.group(2))
        return -v if ref.startswith("-") and not m.group(1).startswith("-") else v
    if PLAIN.match(ref):
        return float(ref.replace(",", ""))
    return None


def math_problems(files: list[Path]) -> list[dict]:
    out = []
    for f in files:
        for i, rec in enumerate(jl(f)):
            ref = math_reference(rec)
            if ref is None:
                continue
            q = rec.get("question") or rec.get("problem")
            src = "gsm8k" if "gsm8k" in f.name else "math"
            out.append({"id": hashlib.sha256(f"{f.name}|{i}".encode()).hexdigest()[:16], "source": src, "file": f.name,
                        "row": i, "question": q, "reference": ref})
    random.Random(SEED0).shuffle(out)
    return out


def math_right(text: str, ref: float) -> bool:
    from learnai.finbench import last_boxed

    ans = last_boxed(text)
    if ans is None:
        return False
    ans = ans.replace("$", "").replace(" ", "").replace("\\!", "").rstrip(".")
    m = FRAC.match(ans)
    if m:
        v = int(m.group(1)) / int(m.group(2))
        v = -v if ans.startswith("-") and not m.group(1).startswith("-") else v
    else:
        v = X56.to_number(ans)
    return v is not None and abs(v - ref) <= 1e-6 * max(1.0, abs(ref))


def math_cmd(a):
    need_drive()
    files = [Path(f) for f in a.files.split(",")] if a.files else MATH_FILES
    probs = math_problems(files)[:a.n]
    model, tok = D14.load_model(D14.STUDENT)
    base = OUT / "math" / a.dir
    base.mkdir(parents=True, exist_ok=True)
    path = base / "samples.jsonl"
    done = {(r["id"], r["sample"]) for r in jl(path)}
    jobs = []
    for p in probs:
        prompt = chat(tok, f"{p['question']}\n\n{MATH_INSTRUCTION}")
        cap = room(len(tok.encode(prompt)))
        jobs += [{"key": {"id": p["id"]}, "prompt": prompt, "cap": cap, "sample": s} for s in range(a.k)
                 if (p["id"], s) not in done and cap >= MIN_ROOM]
    for s in range(a.k):  # greedy first answers, then sampled ones
        part = [j for j in jobs if j["sample"] == s]
        st = generate(model, tok, part, a.batch, path, greedy if s == 0 else sampled)
        print(json.dumps({"sample": s, **st}), flush=True)
    by = {p["id"]: p for p in math_problems(files)}
    rows = jl(path)
    kept = collections.defaultdict(list)
    for r in rows:
        p = by[r["id"]]
        ok = r["finish"] == "stop" and math_right(r["response"], p["reference"])
        if ok and r["response"] not in kept[r["id"]] and len(kept[r["id"]]) < a.keep:
            kept[r["id"]].append(r["response"])
    with open(base / "kept.jsonl", "w", encoding="utf-8") as fh:
        for i, rs in kept.items():
            for t in rs:
                fh.write(json.dumps({"id": i, "source": by[i]["source"], "file": by[i]["file"], "row": by[i]["row"],
                                     "prompt": f"{by[i]['question']}\n\n{MATH_INSTRUCTION}", "response": t}) + "\n")
    src = collections.Counter(by[r["id"]]["source"] for r in rows if r["sample"] == 0)
    rep = {"problems usable": len(by), "problems run": len({r["id"] for r in rows}), "by source": dict(src),
           "greedy right": sum(r["sample"] == 0 and r["finish"] == "stop" and math_right(r["response"], by[r["id"]]["reference"])
                               for r in rows),
           "problems with a kept answer": len(kept), "answers kept": sum(len(x) for x in kept.values()),
           "hit the cap": sum(r["finish"] == "length" for r in rows)}
    (base / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


def bstd(a):
    need_drive()
    items = jl(D14.TRAIN)
    random.Random(SEED0).shuffle(items)
    items = items[:a.n]
    model, tok = D14.load_model(D14.TEACHER)
    base = OUT / "bstd" / a.dir
    base.mkdir(parents=True, exist_ok=True)
    path = base / "samples.jsonl"
    done = {r["id"] for r in jl(path)}
    jobs = []
    for it in items:
        if it["id"] in done:
            continue
        prompt = D14.prompt_for(tok, it, D14.STANDARD)
        jobs.append({"key": {"id": it["id"]}, "prompt": prompt, "cap": room(len(tok.encode(prompt))), "sample": 0})
    st = generate(model, tok, jobs, a.batch, path, greedy)
    print(json.dumps(st), flush=True)
    by = {it["id"]: it for it in items}
    rows = [r for r in jl(path) if r["id"] in by]
    kept = 0
    with open(base / "kept.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            g = D14.V.grade(by[r["id"]], r["response"], "off")
            if r["finish"] == "stop" and g["correct"]:
                kept += 1
                fh.write(json.dumps({"id": r["id"], "response": r["response"]}) + "\n")
    rep = {"items run": len(rows), "kept": kept, "hit the cap": sum(r["finish"] == "length" for r in rows),
           "generated tokens mean": round(sum(r["generated_tokens"] for r in rows) / max(1, len(rows)))}
    (base / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))


# ---------------------------------------------------------------------------------------------

def check(_):
    assert E.MAX_TOKENS == 300 and I55.OUT == OUT and X56.I55 is I55
    assert room(400) == 239 and room(200) == 320 and room(600) < MIN_ROOM
    cases = [({"answer": "so 48+24 = <<48+24=72>>72\n#### 72"}, 72.0), ({"answer": "x\n#### 1,000"}, 1000.0),
             ({"solution": "so $\\boxed{\\frac{1}{48}}$."}, 1 / 48), ({"solution": "\\boxed{-\\frac{3}{4}}"}, -0.75),
             ({"solution": "\\boxed{2\\sqrt{3}}"}, None), ({"solution": "\\boxed{(1,2)}"}, None),
             ({"solution": "\\boxed{12.5}"}, 12.5)]
    for rec, want in cases:
        got = math_reference(rec)
        assert (got is None and want is None) or (got is not None and want is not None and abs(got - want) < 1e-12), (rec, got)
    assert math_right("... so the total is \\boxed{72}.", 72.0)
    assert math_right("\\boxed{\\dfrac{1}{48}}", 1 / 48)
    assert math_right("\\boxed{1,000}", 1000.0)
    assert not math_right("\\boxed{71}", 72.0) and not math_right("72", 72.0)
    probs = math_problems(MATH_FILES) if all(f.exists() for f in MATH_FILES) else []
    X56.check(None)
    print(json.dumps({"checks": "pass", "math problems usable on disk": len(probs),
                      "by source": dict(collections.Counter(p["source"] for p in probs)),
                      "B training items": len(jl(D14.TRAIN))}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    sub.add_parser("check").set_defaults(fn=check)
    b = sub.add_parser("build"); b.add_argument("--pool", type=int, default=I55.POOL); b.set_defaults(fn=build)
    c = sub.add_parser("chains"); c.add_argument("--items", type=int, required=True); c.add_argument("--k", type=int, default=4)
    c.add_argument("--batch", type=int, default=16); c.add_argument("--dir", required=True); c.set_defaults(fn=chains)
    v = sub.add_parser("verify"); v.add_argument("--dir", required=True); v.set_defaults(fn=verify)
    m = sub.add_parser("math"); m.add_argument("--n", type=int, required=True); m.add_argument("--k", type=int, default=1)
    m.add_argument("--keep", type=int, default=1); m.add_argument("--batch", type=int, default=16)
    m.add_argument("--files", default=""); m.add_argument("--dir", required=True); m.set_defaults(fn=math_cmd)
    s = sub.add_parser("bstd"); s.add_argument("--n", type=int, required=True); s.add_argument("--batch", type=int, default=16)
    s.add_argument("--dir", required=True); s.set_defaults(fn=bstd)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
