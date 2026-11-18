"""EXP-0014: S1-c, distilling Qwen3.5-4B into Qwen3.5-0.8B on EarningsExam v0.2.

Pre-registered in research/registry/experiment_registry.md. One script for the whole pipeline,
each step resumable and run one MLX process at a time by ``queue``:

  build      training items: v0.2 rules on the training side with a 300-token excerpt cap
  draw       the 3,000-item test draw (ids only; prints counts and a hash, never item text)
  label      terse labels by the 4B (D3) or the 0.8B (D2): up to 4 attempts, the first correct kept
  sets       N and the D1 / D2 / D3 training sets
  speed      100 training steps, to fix the number of epochs before any development evaluation
  train      full fine-tuning of the 0.8B for one arm and seed; a checkpoint after each epoch
  dev        a checkpoint on the 600 development items (terse prompt)
  test       a configuration on the test draw
  seca       a configuration on section A (100 each of FinQA, CFA-Easy, FinanceIQ)
  queue      every step above in the registered order
  score      criteria H1 to H4 and the reported slices, to scores.json (aggregates only)

Test items are read by the program only; nothing here prints their text.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import subprocess
import sys
import time
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0007_s1b_headroom as S  # noqa: E402
import exp0010_earnings_exam_v0_2 as V  # noqa: E402
import exp0013_terse_teacher as T  # noqa: E402

OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0014"
TRAIN_RAW = OUT / "train300_raw"
TRAIN = OUT / "train300" / "items_train.jsonl"
TEST_ITEMS = V.OUT / "items_test.jsonl"
DEV_DRAW = S.OUT / "draw.jsonl"  # EXP-0007's 600 development ids
TEST_DRAW = OUT / "test_draw.jsonl"
STUDENT, TEACHER = "qwen3.5-0.8b", "qwen3.5-4b"
TERSE = T.PROMPTS["terse"]
STANDARD = S.INSTRUCTION
SEQ = 512
LABEL_CAP = 160
ATTEMPTS = [None, 1, 2, 3]  # None: greedy; then sampling seeds
TEMP, TOP_P = 0.7, 0.95
LR, WARMUP = 1e-5, 50
SEEDS = (1, 2)
ARMS = ("D3", "D2", "D1")
MAX_RUN_HOURS = 8.0
BOOT, BOOT_SEED = 10_000, 20261118
SEEN = {"B1:revenue:p1", "B1:operating_income:p1", "B1:net_income:p1", "B1:eps_diluted:p1",
        "B2:revenue_growth:p1", "B2:operating_margin:p1", "B2:eps_change:p1"}
SECA_N = 100
PER_COMPANY_TEST = 3  # 2 gave 2,740 items (first attempt, counts only, before commit)


def need() -> None:
    S.need_drive()
    OUT.mkdir(parents=True, exist_ok=True)


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# ------------------------------------------------------------------ build and draw


def build(_: argparse.Namespace) -> None:
    import exp0008_earnings_exam_v0_1 as B

    need()
    if TRAIN.exists():
        sys.exit(f"{TRAIN} exists")
    B.E.OUT = TRAIN_RAW
    B.E.MAX_TOKENS = 300
    TRAIN_RAW.mkdir(parents=True, exist_ok=True)
    B.build(argparse.Namespace(sides="train"))
    TRAIN.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(TRAIN, "w", encoding="utf-8") as fh:
        for it in jl(TRAIN_RAW / "items_train.jsonl"):
            it["question"] = V.rewrite(it["question"])
            it["exam_version"] = "v0.2, 300-token excerpts (EXP-0014)"
            fh.write(json.dumps(it) + "\n")
            n += 1
    print("training items:", n)


def draw(_: argparse.Namespace) -> None:
    need()
    if TEST_DRAW.exists():
        sys.exit(f"{TEST_DRAW} exists; the draw is made once")
    items = jl(TEST_ITEMS)
    assert all(i["side"] == "test" and i["post_cutoff"] for i in items)
    group = lambda t: (t.split(":")[0], t in SEEN)  # noqa: E731
    templates = sorted({i["template"] for i in items})
    quota = {}
    for t in templates:
        sec, seen = group(t)
        if seen:
            quota[t] = 360 if sec == "B1" else 320
    for sec in ("B1", "B2"):
        unseen = [t for t in templates if group(t) == (sec, False)]
        for k, t in enumerate(unseen):
            quota[t] = 300 // len(unseen) + (1 if k < 300 % len(unseen) else 0)
    key = lambda r: hashlib.sha256(f"exp0014-test:{r['id']}".encode()).hexdigest()  # noqa: E731
    queues = {t: sorted((r for r in items if r["template"] == t), key=key) for t in templates}
    per_co: collections.Counter = collections.Counter()
    got: collections.Counter = collections.Counter()
    chosen: list[dict] = []
    active = list(templates)
    while active:
        for t in list(active):
            if got[t] >= quota[t]:
                active.remove(t)
                continue
            q = queues[t]
            while q and per_co[q[0]["cik"]] >= PER_COMPANY_TEST:
                q.pop(0)
            if not q:  # exhausted: its places go to the others of its group
                short = quota[t] - got[t]
                quota[t] = got[t]
                active.remove(t)
                others = [o for o in active if group(o) == group(t)]
                for k in range(short):
                    if others:
                        quota[others[k % len(others)]] += 1
                continue
            r = q.pop(0)
            per_co[r["cik"]] += 1
            got[t] += 1
            chosen.append(r)
    with open(TEST_DRAW, "w", encoding="utf-8") as fh:
        for k, r in enumerate(chosen):
            fh.write(json.dumps({"order": k, "id": r["id"], "template": r["template"], "cik": r["cik"]}) + "\n")
    summary = {"items": len(chosen), "companies": len(per_co), "by_template": dict(sorted(got.items())),
               "seen": sum(v for t, v in got.items() if t in SEEN),
               "sha256_of_ids": hashlib.sha256("\n".join(r["id"] for r in chosen).encode()).hexdigest()}
    (OUT / "test_draw_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def load_ids(path: Path, items_path: Path) -> list[dict]:
    want = [r["id"] for r in jl(path)]
    by = {}
    with open(items_path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            by[r["id"]] = r
    return [by[i] for i in want]


# ------------------------------------------------------------------ generation


def load_model(key: str, weights: Path | None = None):
    import mlx.core as mx
    from mlx_lm import load

    mx.set_memory_limit(int(S.BUDGET_GIB * S.GIB))
    mx.set_cache_limit(S.GIB)
    model, tok = load(str(S.model_path(key)))
    if weights is not None:
        model.load_weights(str(weights), strict=False)
    return model, tok


def gen(model, tok, prompt: str, cap: int, seed: int | None = None) -> tuple[str, int, str]:
    import mlx.core as mx
    from mlx_lm import stream_generate
    from mlx_lm.sample_utils import make_sampler

    kw = {}
    if seed is not None:
        mx.random.seed(seed)
        kw["sampler"] = make_sampler(temp=TEMP, top_p=TOP_P)
    text, n, reason = [], 0, None
    for r in stream_generate(model, tok, prompt, max_tokens=cap, **kw):
        text.append(r.text)
        n, reason = r.generation_tokens, r.finish_reason
    return "".join(text), n, reason


def prompt_for(tok, item: dict, instruction: str) -> str:
    S.INSTRUCTION = instruction
    return S.build_prompt(tok, "qwen", item, "off")


def year_after(text: str, item: dict) -> bool:
    end = int(item["period"]["end"][:4])
    return any(int(y) > end for y in re.findall(r"\b(20\d{2})\b", text))


def label(a: argparse.Namespace) -> None:
    """Terse labels for every training item: the first correct of up to 4 attempts."""
    import mlx.core as mx

    need()
    key = {"teacher": TEACHER, "student": STUDENT}[a.who]
    path = OUT / "labels" / f"{key}.jsonl"
    done = {r["id"] for r in jl(path)} if path.exists() else set()
    items = jl(TRAIN)
    model, tok = load_model(key)
    for it in items:
        if it["id"] in done:
            continue
        prompt = prompt_for(tok, it, TERSE)
        tries = []
        for seed in ATTEMPTS:
            t0 = time.time()
            out, n, reason = gen(model, tok, prompt, LABEL_CAP, seed)
            g = V.grade(it, out, "off")
            tries.append({"seed": seed, "response": out, "tokens": n, "finish": reason,
                          "correct": g["correct"], "seconds": round(time.time() - t0, 2)})
            if g["correct"]:
                break
        append(path, {"id": it["id"], "model": key, "revision": S.MODELS[key][1], "attempts": tries,
                      "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})


# ------------------------------------------------------------------ training sets


def decimals_of(item: dict) -> int:
    tol = item["tolerance"]["abs"] / 1.01
    return max(0, round(-math.log10(2 * tol)))


def gold_text(item: dict) -> str:
    d = decimals_of(item)
    return f"\\boxed{{{float(item['gold']):.{d}f}}}"


def sets(_: argparse.Namespace) -> None:
    from transformers import AutoTokenizer

    need()
    tok = AutoTokenizer.from_pretrained(str(S.model_path(STUDENT)))
    items = {it["id"]: it for it in jl(TRAIN)}

    def seq(it, answer):
        p = tok.encode(prompt_for(tok, it, TERSE))
        a = tok.encode(answer, add_special_tokens=False) + [tok.eos_token_id]
        return p + a, len(p)

    kept, why = {}, {}
    for arm, key in (("D3", TEACHER), ("D2", STUDENT)):
        c: collections.Counter = collections.Counter()
        rows = {}
        for r in jl(OUT / "labels" / f"{key}.jsonl"):
            it = items[r["id"]]
            win = next((t for t in r["attempts"] if t["correct"]), None)
            if win is None:
                c["no correct attempt"] += 1
                continue
            ans = win["response"].strip()
            if year_after(ans, it):
                c["names a later year"] += 1
                continue
            toks, off = seq(it, ans)
            if len(toks) > SEQ:
                c["over 512 tokens"] += 1
                continue
            c[f"kept (attempt {r['attempts'].index(win) + 1})"] += 1
            rows[it["id"]] = (toks, off, ans)
        kept[arm], why[arm] = rows, dict(c)
    n = min(len(kept["D3"]), len(kept["D2"])) // 50 * 50
    d1 = {}
    for i, it in items.items():
        toks, off = seq(it, gold_text(it))
        if len(toks) <= SEQ:
            d1[i] = (toks, off, gold_text(it))
    kept["D1"] = d1
    (OUT / "sets").mkdir(exist_ok=True)
    report = {"training_items": len(items), "N": n, "kept": {k: len(v) for k, v in kept.items()}, "why": why}
    for arm in ARMS:
        order = sorted(kept[arm], key=lambda i: hashlib.sha256(f"exp0014:{arm}:{i}".encode()).hexdigest())[:n]
        with open(OUT / "sets" / f"{arm}.jsonl", "w", encoding="utf-8") as fh:
            for i in order:
                toks, off, ans = kept[arm][i]
                fh.write(json.dumps({"id": i, "tokens": toks, "offset": off, "answer": ans}) + "\n")
        lens = sorted(len(kept[arm][i][0]) - kept[arm][i][1] for i in order)
        report[f"{arm} answer tokens median"] = lens[len(lens) // 2] if lens else None
    (OUT / "sets" / "summary.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


# ------------------------------------------------------------------ training


class Seqs:
    def __init__(self, rows):
        self.rows = [(r["tokens"], r["offset"]) for r in rows]

    def __getitem__(self, i):
        return self.rows[i]

    def __len__(self):
        return len(self.rows)


def run_training(arm: str, seed: int, epochs: int, iters: int | None = None) -> dict:
    import mlx.core as mx
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load
    from mlx_lm.tuner.callbacks import TrainingCallback
    from mlx_lm.tuner.trainer import TrainingArgs, train

    rows = jl(OUT / "sets" / f"{arm}.jsonl")
    data = Seqs(rows)
    total = iters or epochs * len(data)
    mx.set_memory_limit(int(S.BUDGET_GIB * S.GIB))
    mx.set_cache_limit(S.GIB)
    np.random.seed(seed)
    mx.random.seed(seed)
    model, _ = load(str(S.model_path(STUDENT)))
    model.freeze()
    for layer in model.layers:  # full fine-tuning of every block; embeddings frozen (as EXP-0006)
        layer.unfreeze()
    sched = optim.join_schedules([optim.linear_schedule(1e-8, LR, WARMUP),
                                  optim.cosine_decay(LR, max(1, total - WARMUP))], [WARMUP])
    opt = optim.AdamW(learning_rate=sched)
    tag = f"{arm}-s{seed}" if iters is None else f"speed-{arm}"
    ckdir = OUT / "checkpoints" / tag
    ckdir.mkdir(parents=True, exist_ok=True)
    log = []

    class Watch(TrainingCallback):
        def on_train_loss_report(self, info: dict) -> None:
            log.append({k: info.get(k) for k in ("iteration", "train_loss", "iterations_per_second", "peak_memory")})
            if mx.get_peak_memory() > S.BUDGET_GIB * S.GIB:
                raise RuntimeError(f"peak memory passed {S.BUDGET_GIB} GiB")

    args = TrainingArgs(batch_size=1, iters=total, steps_per_report=10, steps_per_eval=10**9,
                        steps_per_save=len(data) if iters is None else 10**9, max_seq_length=SEQ,
                        adapter_file=str(ckdir / "final.safetensors"), grad_checkpoint=True)
    t0 = time.time()
    train(model, opt, data, None, args=args, training_callback=Watch())
    info = {"arm": arm, "seed": seed, "items": len(data), "iters": total, "epochs": epochs if iters is None else None,
            "wall_s": round(time.time() - t0, 1), "peak_gib": round(mx.get_peak_memory() / S.GIB, 2), "log": log}
    (ckdir / "train_log.json").write_text(json.dumps(info, indent=1))
    return info


def speed(_: argparse.Namespace) -> None:
    need()
    info = run_training("D3", 1, 1, iters=100)
    steady = [r["iterations_per_second"] for r in info["log"][1:] if r["iterations_per_second"]]
    s_per_step = 1 / (sum(steady) / len(steady))
    n = len(jl(OUT / "sets" / "D3.jsonl"))
    hours2 = 2 * n * s_per_step / 3600
    epochs = 2 if hours2 <= MAX_RUN_HOURS else 1
    res = {"s_per_step": round(s_per_step, 2), "N": n, "hours_for_2_epochs": round(hours2, 2), "epochs": epochs,
           "peak_gib": info["peak_gib"]}
    (OUT / "speed.json").write_text(json.dumps(res, indent=1))
    import shutil
    shutil.rmtree(OUT / "checkpoints" / "speed-D3", ignore_errors=True)
    print(json.dumps(res))


def train_cmd(a: argparse.Namespace) -> None:
    need()
    epochs = json.loads((OUT / "speed.json").read_text())["epochs"]
    ck = OUT / "checkpoints" / f"{a.arm}-s{a.seed}"
    if (ck / "train_log.json").exists():
        return
    run_training(a.arm, a.seed, epochs)


def checkpoints(arm: str, seed: int) -> list[tuple[int, Path]]:
    ck = OUT / "checkpoints" / f"{arm}-s{seed}"
    n = len(jl(OUT / "sets" / f"{arm}.jsonl"))
    epochs = json.loads((OUT / "speed.json").read_text())["epochs"]
    out = [(1, ck / f"{n:07d}_adapters.safetensors")] if epochs == 2 else []
    out.append((epochs, ck / "final.safetensors"))
    return out


# ------------------------------------------------------------------ evaluation


def answer(model, tok, item: dict, instruction: str, cap: int) -> dict:
    from learnai.finbench import last_boxed

    prompt = prompt_for(tok, item, instruction)
    t0 = time.time()
    out, n, reason = gen(model, tok, prompt, cap)
    forced, cont, nf = None, "", 0
    if reason == "length" and last_boxed(out) is None:
        forced = S.CUE
        cont, nf, _ = gen(model, tok, prompt + out + forced, S.FORCE_TOKENS)
    return {"id": item["id"], "prompt_tokens": len(tok.encode(prompt)), "generated_tokens": n, "finish": reason,
            "forced": bool(forced), "forced_tokens": nf, "response": out + (forced or "") + cont,
            "seconds": round(time.time() - t0, 2)}


CONFIGS = {  # name -> (model key, weights, instruction, cap)
    "D0-0.8b": (STUDENT, None, STANDARD, 512),
    "D0-4b": (TEACHER, None, STANDARD, 512),
}


def config(name: str):
    if name in CONFIGS:
        return CONFIGS[name]
    arm, seed = name.split("-s")  # e.g. D3-s1: the checkpoint chosen on development
    best = json.loads((OUT / "dev" / "chosen.json").read_text())[name]
    return STUDENT, Path(best), TERSE, LABEL_CAP


def run_eval(items: list[dict], path: Path, model_key: str, weights, instruction: str, cap: int) -> None:
    import mlx.core as mx

    done = {r["id"] for r in jl(path)} if path.exists() else set()
    todo = [i for i in items if i["id"] not in done]
    if not todo:
        return
    model, tok = load_model(model_key, weights)
    for it in todo:
        row = answer(model, tok, it, instruction, cap)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        append(path, row)


def dev(a: argparse.Namespace) -> None:
    need()
    items = load_ids(DEV_DRAW, V.OUT / "items_dev.jsonl")
    for epoch, w in checkpoints(a.arm, a.seed):
        run_eval(items, OUT / "dev" / f"{a.arm}-s{a.seed}-e{epoch}.jsonl", STUDENT, w, TERSE, LABEL_CAP)


def choose(_: argparse.Namespace) -> None:
    items = {i["id"]: i for i in load_ids(DEV_DRAW, V.OUT / "items_dev.jsonl")}
    chosen, acc = {}, {}
    for arm in ARMS:
        for seed in SEEDS:
            best = None
            for epoch, w in checkpoints(arm, seed):
                rows = jl(OUT / "dev" / f"{arm}-s{seed}-e{epoch}.jsonl")
                a_ = sum(V.grade(items[r["id"]], r["response"], "off")["correct"] for r in rows) / len(rows)
                acc[f"{arm}-s{seed}-e{epoch}"] = round(100 * a_, 1)
                if best is None or a_ > best[0]:  # ties go to the earlier epoch
                    best = (a_, str(w))
            chosen[f"{arm}-s{seed}"] = best[1]
    (OUT / "dev" / "chosen.json").write_text(json.dumps(chosen, indent=1))
    (OUT / "dev" / "accuracy.json").write_text(json.dumps(acc, indent=1))
    print(json.dumps(acc, indent=1))


def test(a: argparse.Namespace) -> None:
    need()
    key, w, ins, cap = config(a.config)
    run_eval(load_ids(TEST_DRAW, TEST_ITEMS), OUT / "test" / f"{a.config}.jsonl", key, w, ins, cap)


def seca(a: argparse.Namespace) -> None:
    import mlx.core as mx
    from learnai.finbench import load_problems

    need()
    key, w, _, _ = config(a.config)
    path = OUT / "seca" / f"{a.config}.jsonl"
    done = {r["uid"] for r in jl(path)} if path.exists() else set()
    probs = [p for p in load_problems(SECA_N, seed=BOOT_SEED) if p.uid not in done]
    if not probs:
        return
    model, tok = load_model(key, w)
    for p in probs:
        prompt = tok.apply_chat_template([{"role": "user", "content": p.prompt}], add_generation_prompt=True,
                                         tokenize=False, enable_thinking=False)
        t0 = time.time()
        out, n, reason = gen(model, tok, prompt, 512)
        append(path, {"uid": p.uid, "generated_tokens": n, "finish": reason, "response": out,
                      "seconds": round(time.time() - t0, 2), "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})


# ------------------------------------------------------------------ queue and score


def queue(_: argparse.Namespace) -> None:
    need()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%H:%M:%S"), *args, flush=True)
        r = subprocess.run(me + list(args))
        if r.returncode != 0:
            sys.exit(f"step failed: {args}")

    if not TRAIN.exists():
        step("build")
    for who in ("teacher", "student"):
        path = OUT / "labels" / f"{(TEACHER if who == 'teacher' else STUDENT)}.jsonl"
        if not path.exists() or len(jl(path)) < len(jl(TRAIN)):
            step("label", "--who", who)
    if not (OUT / "sets" / "summary.json").exists():
        step("sets")
    if not (OUT / "speed.json").exists():
        step("speed")
    for seed in SEEDS:
        for arm in ARMS:
            step("train", "--arm", arm, "--seed", str(seed))
            step("dev", "--arm", arm, "--seed", str(seed))
    step("choose")
    for name in ["D0-0.8b", "D0-4b"] + [f"{arm}-s{s}" for arm in ARMS for s in SEEDS]:
        step("test", "--config", name)
    for name in ["D0-0.8b"] + [f"{arm}-s{s}" for arm in ("D2", "D3") for s in SEEDS]:
        step("seca", "--config", name)
    step("score")


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from learnai.finbench import grade as fgrade, problem_for

    items = load_ids(TEST_DRAW, TEST_ITEMS)
    ids = [i["id"] for i in items]
    by = {i["id"]: i for i in items}
    section = np.array([by[i]["section"] for i in ids])
    seen = np.array([by[i]["template"] in SEEN for i in ids])
    cos = sorted({by[i]["cik"] for i in ids})
    co_idx = {c: np.array([k for k, i in enumerate(ids) if by[i]["cik"] == c]) for c in cos}
    rng = np.random.default_rng(BOOT_SEED)
    boot = [np.concatenate([co_idx[cos[j]] for j in rng.integers(0, len(cos), len(cos))]) for _ in range(BOOT)]

    def correct(name):
        rows = {r["id"]: r for r in jl(OUT / "test" / f"{name}.jsonl")}
        return np.array([float(V.grade(by[i], rows[i]["response"], "off")["correct"]) for i in ids]), rows

    vec, meta = {}, {}
    for name in ["D0-0.8b", "D0-4b"] + [f"{arm}-s{s}" for arm in ARMS for s in SEEDS]:
        vec[name], meta[name] = correct(name)
    for arm in ARMS:
        vec[arm] = np.mean([vec[f"{arm}-s{s}"] for s in SEEDS], axis=0)

    def stats(d, mask=None):
        m = np.ones(len(ids), bool) if mask is None else mask
        bs = np.array([d[b][m[b]].mean() for b in boot])
        return {"value": round(100 * float(d[m].mean()), 2),
                "ci97_5": [round(100 * float(np.percentile(bs, 1.25)), 2), round(100 * float(np.percentile(bs, 98.75)), 2)],
                "p_le_0": round(float(np.mean(bs <= 0)), 5)}

    out: dict = {"test_draw": json.loads((OUT / "test_draw_summary.json").read_text()), "accuracy": {}}
    for name, v in vec.items():
        out["accuracy"][name] = {k: round(100 * float(v[m].mean()), 1) for k, m in
                                 (("all", np.ones(len(ids), bool)), ("B1", section == "B1"), ("B2", section == "B2"),
                                  ("seen", seen), ("unseen", ~seen))}
    h1 = stats(vec["D3"] - vec["D2"])
    h1["supported"] = h1["value"] >= 3.0 and h1["p_le_0"] < 0.0125
    h1["refuted"] = h1["ci97_5"][1] < 3.0
    dev_acc = json.loads((OUT / "dev" / "accuracy.json").read_text())
    h2 = stats(vec["D3"] - vec["D0-4b"])
    h2["arm"] = "D3"
    h2["non_inferior"] = h2["ci97_5"][0] > -3.0
    h2["refuted"] = h2["ci97_5"][1] < -3.0
    med = lambda name: float(np.median([r["generated_tokens"] for r in meta[name].values()]))  # noqa: E731
    d3_med = np.median([med(f"D3-s{s}") for s in SEEDS])
    h3 = {"D3_median_tokens": d3_med, "D0_median_tokens": med("D0-0.8b"),
          "accuracy_gap": round(100 * float((vec["D3"] - vec["D0-0.8b"]).mean()), 2)}
    h3["supported"] = d3_med <= 0.5 * h3["D0_median_tokens"] and h3["accuracy_gap"] >= -2.0
    out["H1"], out["H2"], out["H3"] = h1, h2, h3
    out["by_section"] = {f"{k} {sec}": stats(vec[a] - vec[b], section == sec)
                         for k, (a, b) in (("D3-D2", ("D3", "D2")), ("D3-D0_4b", ("D3", "D0-4b")),
                                           ("D3-D1", ("D3", "D1")), ("D2-D0", ("D2", "D0-0.8b")))
                         for sec in ("B1", "B2")}
    out["seed_spread"] = {arm: [out["accuracy"][f"{arm}-s{s}"]["all"] for s in SEEDS] for arm in ARMS}
    out["dev_accuracy"] = dev_acc
    out["forced_rate"] = {n: round(100 * float(np.mean([r["forced"] for r in meta[n].values()])), 1) for n in meta}
    seca_acc = {}
    for name in ["D0-0.8b"] + [f"{arm}-s{s}" for arm in ("D2", "D3") for s in SEEDS]:
        p = OUT / "seca" / f"{name}.jsonl"
        if not p.exists():
            continue
        c: dict = collections.defaultdict(list)
        for r in jl(p):
            prob = problem_for(r["uid"])
            c[prob.source].append(fgrade(prob, r["response"], thinking=False)["correct"])
        seca_acc[name] = {s: round(100 * sum(v) / len(v), 1) for s, v in c.items()}
    out["H4_section_A"] = seca_acc
    out["sets"] = json.loads((OUT / "sets" / "summary.json").read_text())
    out["speed"] = json.loads((OUT / "speed.json").read_text())
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(required=True)
    for name, fn in (("build", build), ("draw", draw), ("sets", sets), ("speed", speed), ("choose", choose),
                     ("queue", queue), ("score", score)):
        sub.add_parser(name).set_defaults(fn=fn)
    q = sub.add_parser("label")
    q.add_argument("--who", choices=("teacher", "student"), required=True)
    q.set_defaults(fn=label)
    for name, fn in (("train", train_cmd), ("dev", dev)):
        q = sub.add_parser(name)
        q.add_argument("--arm", choices=ARMS, required=True)
        q.add_argument("--seed", type=int, choices=SEEDS, required=True)
        q.set_defaults(fn=fn)
    for name, fn in (("test", test), ("seca", seca)):
        q = sub.add_parser(name)
        q.add_argument("--config", required=True)
        q.set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
