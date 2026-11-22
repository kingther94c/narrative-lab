"""EXP-0017: S1-c calculator distillation. The 4B's terse answers written with the calculator, values masked.

Pre-registered in research/registry/experiment_registry.md. The teacher (Qwen3.5-4B) answers EXP-0014's
training items with the terse prompt and EXP-0016's calculator; the student (Qwen3.5-0.8B) is trained
on those answers with the inserted values left out of the loss, and evaluated with the same calculator.
Two arms at N = 1,850: K1 (D3's items where possible) and K2 (operating margins and negative answers
first). Test items are EXP-0016's draw; C, 4C, D3 and 4B are EXP-0016's responses, not rerun.

  label      teacher labels with the calculator (``--limit`` writes a smoke run to labels_smoke/)
  maskcheck  on 20 smoke labels with a call: the masked tokens are exactly the inserted values
  sets       K1 and K2 training sets (tokens, prompt offset, masked positions)
  train      one run: ``--arm K1 --seed 1``
  dev        both epochs of a run on the 600 development items, with the calculator
  choose     the epoch of each run, by development accuracy
  test       a chosen run on EXP-0016's test draw
  seca       a chosen run on section A
  queue      everything above in the registered order, then score
  score      HD1 to HD3 and the reported slices, to scores.json

Test items are read by the program only; nothing here prints their text.

    conda run --no-capture-output -n py313 python research/experiments/exp0017_s1c_calc_distillation.py label --limit 100
    conda run --no-capture-output -n py313 python research/experiments/exp0017_s1c_calc_distillation.py maskcheck
    conda run --no-capture-output -n py313 python research/experiments/exp0017_s1c_calc_distillation.py queue
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as E  # noqa: E402
import exp0016_s1c_calculator as X  # noqa: E402

S, V = E.S, E.V
OUT = S.DRIVE / "narrative_lab" / "s1" / "exp0017"
N = 1850
ARMS = ("K1", "K2")
SEEDS = E.SEEDS
EPOCHS = 2
BOOT, BOOT_SEED = 10_000, 20261122
RUNS = [f"{a}-s{s}" for a in ARMS for s in SEEDS]
COMPARATORS = ["D3-s1", "D3-s2", "C-s1", "C-s2", "4B", "4C"]  # EXP-0016 responses


# ------------------------------------------------------------------ labels


def gen_calc(model, tok, prompt: str, cap: int, seed: int | None) -> dict:
    """EXP-0016's calculator loop (both rules), greedy or sampled. Appended tokens are free."""
    import mlx.core as mx
    from mlx_lm import stream_generate
    from mlx_lm.sample_utils import make_sampler

    kw = {}
    if seed is not None:
        mx.random.seed(seed)
        kw["sampler"] = make_sampler(temp=E.TEMP, top_p=E.TOP_P)
    text, n_gen, calls, reason, last_end = "", 0, [], None, 0
    while True:
        scan_from, stopped = max(last_end, len(text) - 8), False
        for r in stream_generate(model, tok, prompt + text, max_tokens=max(1, cap - n_gen), **kw):
            text += r.text
            reason = r.finish_reason
            if len(calls) < X.MAX_CALLS:
                hit = X.find_call(text, max(0, scan_from))
                if hit:
                    end, expr, value, rule = hit
                    ins = " " + X.fmt(value)
                    text = text[:end] + ins
                    last_end = len(text)
                    calls.append({"expr": expr, "value": value, "at": end, "inserted": ins, "rule": rule})
                    n_gen += r.generation_tokens
                    stopped = True
                    break
        if not stopped:
            n_gen += r.generation_tokens
            break
        if n_gen >= cap:
            reason = "length"
            break
    return {"text": text, "generated_tokens": n_gen, "finish": reason, "calls": calls}


def label(a: argparse.Namespace) -> None:
    """Calculator labels for the training items: the first correct of up to 4 attempts, as EXP-0014."""
    import mlx.core as mx

    S.need_drive()
    smoke = bool(a.limit)
    path = OUT / ("labels_smoke" if smoke else "labels") / f"{E.TEACHER}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = {r["id"] for r in E.jl(path)} if path.exists() else set()
    items = E.jl(E.TRAIN)
    if smoke:  # a spread of templates: the first items in the order of a fixed hash
        items = sorted(items, key=lambda i: hashlib.sha256(f"exp0017-smoke:{i['id']}".encode()).hexdigest())[: a.limit]
    model, tok = E.load_model(E.TEACHER)
    for it in items:
        if it["id"] in done:
            continue
        prompt = E.prompt_for(tok, it, E.TERSE)
        tries = []
        for seed in E.ATTEMPTS:
            t0 = time.time()
            g = gen_calc(model, tok, prompt, E.LABEL_CAP, seed)
            ok = V.grade(it, g["text"], "off")["correct"]
            tries.append({"seed": seed, "response": g["text"], "tokens": g["generated_tokens"], "finish": g["finish"],
                          "calls": g["calls"], "correct": ok, "seconds": round(time.time() - t0, 2)})
            if ok:
                break
        E.append(path, {"id": it["id"], "model": E.TEACHER, "revision": S.MODELS[E.TEACHER][1], "attempts": tries,
                        "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})
    if smoke:
        rows = E.jl(path)
        by = {i["id"]: i for i in E.jl(E.TRAIN)}
        b2 = [r for r in rows if by[r["id"]]["section"] == "B2"]
        first = lambda r: r["attempts"][0]  # noqa: E731
        print(json.dumps({"items": len(rows), "first_attempt_correct": round(100 * sum(first(r)["correct"] for r in rows) / len(rows), 1),
                          "any_attempt_correct": round(100 * sum(any(t["correct"] for t in r["attempts"]) for r in rows) / len(rows), 1),
                          "B2_items": len(b2),
                          "B2_first_attempt_with_call": round(100 * sum(bool(first(r)["calls"]) for r in b2) / max(1, len(b2)), 1),
                          "B1_first_attempt_with_call": round(100 * sum(bool(first(r)["calls"]) for r in rows if r not in b2)
                                                              / max(1, len(rows) - len(b2)), 1)}, indent=1))


# ------------------------------------------------------------------ sequences and masking


def encode(tok, item: dict, attempt: dict) -> tuple[list[int], int, list[int], str]:
    """Prompt + answer + EOS; the answer tokenised in pieces split at each inserted value.

    Returns (tokens, prompt length, positions with no loss, answer text). The answer is the response
    with leading and trailing white space removed, as EXP-0014."""
    resp = attempt["response"]
    lead = len(resp) - len(resp.lstrip())
    ans = resp.strip()
    p = tok.encode(E.prompt_for(tok, item, E.TERSE))
    toks, masked, pos = list(p), [], 0
    for c in attempt["calls"]:
        a, b = c["at"] - lead, c["at"] - lead + len(c["inserted"])
        assert ans[a:b] == c["inserted"].strip() or ans[a:b] == c["inserted"], (ans[a - 5:b + 5], c["inserted"])
        toks += tok.encode(ans[pos:a], add_special_tokens=False)
        ins = tok.encode(ans[a:b], add_special_tokens=False)
        masked += list(range(len(toks), len(toks) + len(ins)))
        toks += ins
        pos = b
    toks += tok.encode(ans[pos:], add_special_tokens=False) + [tok.eos_token_id]
    return toks, len(p), masked, ans


def maskcheck(_: argparse.Namespace) -> None:
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(str(S.model_path(E.STUDENT)))
    by = {i["id"]: i for i in E.jl(E.TRAIN)}
    rows = E.jl(OUT / "labels_smoke" / f"{E.TEACHER}.jsonl")
    n = bad = 0
    for r in rows:
        win = next((t for t in r["attempts"] if t["correct"] and t["calls"]), None)
        if win is None:
            continue
        toks, off, masked, ans = encode(tok, by[r["id"]], win)
        # group consecutive masked positions into spans and compare with the inserted strings
        spans, cur = [], []
        for k in masked:
            if cur and k != cur[-1] + 1:
                spans.append(cur)
                cur = []
            cur.append(k)
        if cur:
            spans.append(cur)
        got = [tok.decode([toks[k] for k in sp]) for sp in spans]
        want = [c["inserted"] for c in win["calls"]]
        ok = len(got) == len(want) and all(g.strip() == w.strip() for g, w in zip(got, want))
        bad += not ok
        n += 1
        print("ok " if ok else "BAD", got, want)
        if n == 20:
            break
    print(f"{n - bad} of {n} labels: masked tokens are exactly the inserted values")
    if bad or n < 20:
        sys.exit(1)


def sets(_: argparse.Namespace) -> None:
    from transformers import AutoTokenizer

    S.need_drive()
    tok = AutoTokenizer.from_pretrained(str(S.model_path(E.STUDENT)))
    items = {it["id"]: it for it in E.jl(E.TRAIN)}
    c: collections.Counter = collections.Counter()
    kept = {}
    for r in E.jl(OUT / "labels" / f"{E.TEACHER}.jsonl"):
        it = items[r["id"]]
        win = next((t for t in r["attempts"] if t["correct"]), None)
        if win is None:
            c["no correct attempt"] += 1
            continue
        toks, off, masked, ans = encode(tok, it, win)
        if E.year_after(ans, it):
            c["names a later year"] += 1
            continue
        if len(toks) > E.SEQ:
            c["over 512 tokens"] += 1
            continue
        c[f"kept (attempt {r['attempts'].index(win) + 1})"] += 1
        kept[it["id"]] = {"id": it["id"], "tokens": toks, "offset": off, "masked": masked, "answer": ans,
                          "calls": len(win["calls"])}
    d3 = [r["id"] for r in E.jl(E.OUT / "sets" / "D3.jsonl")]
    h = lambda i: hashlib.sha256(f"exp0017:K1:{i}".encode()).hexdigest()  # noqa: E731
    k1_order = [i for i in d3 if i in kept] + sorted((i for i in kept if i not in set(d3)), key=h)
    margin = [i for i in k1_order if items[i]["metric"] == "operating_margin"]
    neg = [i for i in k1_order if float(items[i]["gold"]) < 0 and i not in set(margin)]
    pri = margin + neg
    k2_order = pri + [i for i in k1_order if i not in set(pri)]
    chosen = {"K1": k1_order[:N], "K2": k2_order[:N]}
    assert all(len(v) == N for v in chosen.values()), {k: len(v) for k, v in chosen.items()}
    (OUT / "sets").mkdir(parents=True, exist_ok=True)
    report = {"training_items": len(items), "kept": len(kept), "why": dict(c), "N": N,
              "K1_from_D3": sum(i in set(d3) for i in chosen["K1"]), "priority_items": len(pri)}
    for arm, ids in chosen.items():
        with open(OUT / "sets" / f"{arm}.jsonl", "w", encoding="utf-8") as fh:
            for i in ids:
                fh.write(json.dumps(kept[i]) + "\n")
        lens = sorted(len(kept[i]["tokens"]) - kept[i]["offset"] for i in ids)
        report[arm] = {"by_metric": dict(sorted(collections.Counter(items[i]["metric"] for i in ids).items())),
                       "negative_gold": sum(float(items[i]["gold"]) < 0 for i in ids),
                       "B2": sum(items[i]["section"] == "B2" for i in ids),
                       "with_call": sum(kept[i]["calls"] > 0 for i in ids),
                       "masked_tokens": sum(len(kept[i]["masked"]) for i in ids),
                       "answer_tokens_median": lens[len(lens) // 2]}
    (OUT / "sets" / "summary.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


# ------------------------------------------------------------------ training


def iterate_batches(dataset, batch_size, max_seq_length, loop=False, seed=None, comm_group=None):
    """mlx_lm's iterate_batches for batch size 1 (same order and padding), yielding a loss mask:
    target positions from the prompt end to the sequence end, as mlx_lm's default loss, minus the
    inserted values."""
    import mlx.core as mx
    import numpy as np

    assert batch_size == 1
    idx = sorted(range(len(dataset)), key=lambda j: len(dataset[j][0]))
    batch_idx = [[j] for j in idx]
    if seed is not None:
        np.random.seed(seed)
    while True:
        for i in np.random.permutation(len(batch_idx)):
            toks, off, masked = dataset[batch_idx[i][0]]
            length = min(len(toks), max_seq_length)
            width = min(1 + 32 * ((length + 31) // 32), max_seq_length)
            arr = np.zeros((1, width), np.int32)
            arr[0, :length] = toks[:length]
            steps = np.arange(1, width)  # target j is token j (inputs are tokens 0 .. width-2)
            mask = ((steps >= off) & (steps <= length)).astype(np.float32)
            for k in masked:
                if 1 <= k < width:
                    mask[k - 1] = 0.0
            yield mx.array(arr), mx.array(mask[None, :])
        if not loop:
            break


def masked_loss(model, batch, mask):
    import mlx.core as mx
    import mlx.nn as nn

    logits = model(batch[:, :-1])
    ce = nn.losses.cross_entropy(logits, batch[:, 1:]) * mask
    ntoks = mask.sum()
    return ce.astype(mx.float32).sum() / ntoks, ntoks


class Seqs:
    def __init__(self, rows):
        self.rows = [(r["tokens"], r["offset"], r["masked"]) for r in rows]

    def __getitem__(self, i):
        return self.rows[i]

    def __len__(self):
        return len(self.rows)


def run_training(arm: str, seed: int) -> dict:
    """EXP-0014's D3 training (full fine-tuning, AdamW 1e-5, 50 warm-up steps, cosine, batch 1, 512
    tokens, 2 epochs, a checkpoint each epoch), with the masked loss."""
    import mlx.core as mx
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load
    from mlx_lm.tuner.callbacks import TrainingCallback
    from mlx_lm.tuner.trainer import TrainingArgs, train

    data = Seqs(E.jl(OUT / "sets" / f"{arm}.jsonl"))
    total = EPOCHS * len(data)
    mx.set_memory_limit(int(S.BUDGET_GIB * S.GIB))
    mx.set_cache_limit(S.GIB)
    np.random.seed(seed)
    mx.random.seed(seed)
    model, _ = load(str(S.model_path(E.STUDENT)))
    model.freeze()
    for layer in model.layers:
        layer.unfreeze()
    sched = optim.join_schedules([optim.linear_schedule(1e-8, E.LR, E.WARMUP),
                                  optim.cosine_decay(E.LR, max(1, total - E.WARMUP))], [E.WARMUP])
    opt = optim.AdamW(learning_rate=sched)
    ckdir = OUT / "checkpoints" / f"{arm}-s{seed}"
    ckdir.mkdir(parents=True, exist_ok=True)
    log = []

    class Watch(TrainingCallback):
        def on_train_loss_report(self, info: dict) -> None:
            log.append({k: info.get(k) for k in ("iteration", "train_loss", "iterations_per_second", "peak_memory")})
            if mx.get_peak_memory() > S.BUDGET_GIB * S.GIB:
                raise RuntimeError(f"peak memory passed {S.BUDGET_GIB} GiB")

    args = TrainingArgs(batch_size=1, iters=total, steps_per_report=10, steps_per_eval=10**9,
                        steps_per_save=len(data), max_seq_length=E.SEQ,
                        adapter_file=str(ckdir / "final.safetensors"), grad_checkpoint=True)
    t0 = time.time()
    train(model, opt, data, None, args=args, loss=masked_loss, iterate_batches=iterate_batches,
          training_callback=Watch())
    info = {"arm": arm, "seed": seed, "items": len(data), "iters": total, "epochs": EPOCHS,
            "wall_s": round(time.time() - t0, 1), "peak_gib": round(mx.get_peak_memory() / S.GIB, 2), "log": log}
    (ckdir / "train_log.json").write_text(json.dumps(info, indent=1))
    return info


def train_cmd(a: argparse.Namespace) -> None:
    S.need_drive()
    if (OUT / "checkpoints" / f"{a.arm}-s{a.seed}" / "train_log.json").exists():
        return
    run_training(a.arm, a.seed)


def checkpoints(arm: str, seed: int) -> list[tuple[int, Path]]:
    ck = OUT / "checkpoints" / f"{arm}-s{seed}"
    return [(1, ck / f"{N:07d}_adapters.safetensors"), (2, ck / "final.safetensors")]


# ------------------------------------------------------------------ evaluation


def run_eval(items: list[dict], path: Path, weights: Path) -> None:
    import mlx.core as mx

    done = {r["id"] for r in E.jl(path)} if path.exists() else set()
    todo = [i for i in items if i["id"] not in done]
    if not todo:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    model, tok = E.load_model(E.STUDENT, weights)
    for it in todo:
        row = X.answer(model, tok, it, E.TERSE, E.LABEL_CAP, True)
        row["peak_gib"] = round(mx.get_peak_memory() / S.GIB, 2)
        E.append(path, row)


def dev(a: argparse.Namespace) -> None:
    S.need_drive()
    items = E.load_ids(E.DEV_DRAW, V.OUT / "items_dev.jsonl")
    for epoch, w in checkpoints(a.arm, a.seed):
        run_eval(items, OUT / "dev" / f"{a.arm}-s{a.seed}-e{epoch}.jsonl", w)


def choose(_: argparse.Namespace) -> None:
    items = {i["id"]: i for i in E.load_ids(E.DEV_DRAW, V.OUT / "items_dev.jsonl")}
    chosen, acc = {}, {}
    for arm in ARMS:
        for seed in SEEDS:
            best = None
            for epoch, w in checkpoints(arm, seed):
                rows = E.jl(OUT / "dev" / f"{arm}-s{seed}-e{epoch}.jsonl")
                a_ = sum(V.grade(items[r["id"]], r["response"], "off")["correct"] for r in rows) / len(rows)
                acc[f"{arm}-s{seed}-e{epoch}"] = round(100 * a_, 1)
                if best is None or a_ > best[0]:  # ties go to the earlier epoch
                    best = (a_, str(w))
            chosen[f"{arm}-s{seed}"] = best[1]
    (OUT / "dev" / "chosen.json").write_text(json.dumps(chosen, indent=1))
    (OUT / "dev" / "accuracy.json").write_text(json.dumps(acc, indent=1))
    print(json.dumps(acc, indent=1))


def chosen_weights(run: str) -> Path:
    return Path(json.loads((OUT / "dev" / "chosen.json").read_text())[run])


def test(a: argparse.Namespace) -> None:
    S.need_drive()
    run_eval(E.load_ids(X.TEST_DRAW, E.TEST_ITEMS), OUT / "test" / f"{a.config}.jsonl", chosen_weights(a.config))


def seca(a: argparse.Namespace) -> None:
    import mlx.core as mx
    from learnai.finbench import load_problems

    S.need_drive()
    path = OUT / "seca" / f"{a.config}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = {r["uid"] for r in E.jl(path)} if path.exists() else set()
    probs = [p for p in load_problems(E.SECA_N, seed=E.BOOT_SEED) if p.uid not in done]
    if not probs:
        return
    model, tok = E.load_model(E.STUDENT, chosen_weights(a.config))
    for p in probs:
        prompt = tok.apply_chat_template([{"role": "user", "content": p.prompt}], add_generation_prompt=True,
                                         tokenize=False, enable_thinking=False)
        t0 = time.time()
        g = X.gen_calc(model, tok, prompt, 512, True)
        E.append(path, {"uid": p.uid, "generated_tokens": g["generated_tokens"], "finish": g["finish"],
                        "calls": g["calls"], "response": g["text"], "seconds": round(time.time() - t0, 2),
                        "peak_gib": round(mx.get_peak_memory() / S.GIB, 2)})


def queue(_: argparse.Namespace) -> None:
    S.need_drive()
    me = [sys.executable, __file__]

    def step(*args):
        print(time.strftime("%m-%d %H:%M:%S"), *args, flush=True)
        if subprocess.run(me + list(args)).returncode != 0:
            sys.exit(f"step failed: {args}")

    step("label")
    step("sets")
    for arm in ARMS:
        for seed in SEEDS:
            step("train", "--arm", arm, "--seed", str(seed))
            step("dev", "--arm", arm, "--seed", str(seed))
    step("choose")
    for run in RUNS:
        step("test", "--config", run)
    for run in RUNS:
        step("seca", "--config", run)
    step("score")


# ------------------------------------------------------------------ score


def dropped_loss_sign(item: dict, g: dict) -> bool:
    """A wrong answer to an item with a negative gold whose boxed value is the gold without its sign."""
    gold = float(item["gold"])
    return gold < 0 and g["valid"] and g["value"] is not None and abs(g["value"] + gold) <= item["tolerance"]["abs"]


def score(_: argparse.Namespace) -> None:
    import numpy as np
    from learnai.finbench import grade as fgrade, problem_for

    items = E.load_ids(X.TEST_DRAW, E.TEST_ITEMS)
    ids = [i["id"] for i in items]
    by = {i["id"]: i for i in items}
    section = np.array([by[i]["section"] for i in ids])
    seen = np.array([by[i]["template"] in E.SEEN for i in ids])
    metric = np.array([by[i]["metric"] for i in ids])
    cos = sorted({by[i]["cik"] for i in ids})
    co_idx = {c: np.array([k for k, i in enumerate(ids) if by[i]["cik"] == c]) for c in cos}
    rng = np.random.default_rng(BOOT_SEED)
    boot = [np.concatenate([co_idx[cos[j]] for j in rng.integers(0, len(cos), len(cos))]) for _ in range(BOOT)]
    allm, b1, b2 = np.ones(len(ids), bool), section == "B1", section == "B2"

    vec, rows, grades = {}, {}, {}
    sources = {n: X.OUT / "test" / f"{n}.jsonl" for n in COMPARATORS} | {n: OUT / "test" / f"{n}.jsonl" for n in RUNS}
    for name, p in sources.items():
        rows[name] = {r["id"]: r for r in E.jl(p)}
        assert set(rows[name]) == set(ids), name
        grades[name] = {i: V.grade(by[i], rows[name][i]["response"], "off") for i in ids}
        vec[name] = np.array([float(grades[name][i]["correct"]) for i in ids])
    for arm in ("D3", "C", "K1", "K2"):
        vec[arm] = (vec[f"{arm}-s1"] + vec[f"{arm}-s2"]) / 2

    def stats(d, m=allm):
        bs = np.array([d[b][m[b]].mean() for b in boot])
        return {"value": round(100 * float(d[m].mean()), 2),
                "ci97_5": [round(100 * float(np.percentile(bs, 1.25)), 2), round(100 * float(np.percentile(bs, 98.75)), 2)],
                "p_le_0": round(float(np.mean(bs <= 0)), 5)}

    def superiority(s, margin):
        s["supported"] = s["value"] >= margin and s["p_le_0"] < 0.0125
        s["refuted"] = s["ci97_5"][1] < margin
        return s

    out: dict = {"accuracy": {}}
    masks = {"all": allm, "B1": b1, "B2": b2, "seen": seen, "unseen": ~seen}
    masks.update({f"{sec}:{m}": (section == sec) & (metric == m) for sec in ("B1", "B2") for m in sorted(set(metric[section == sec]))})
    for name, v in vec.items():
        out["accuracy"][name] = {k: round(100 * float(v[m].mean()), 1) for k, m in masks.items() if m.any()}
    out["HD1"] = superiority(stats(vec["K1"] - vec["C"], b2), 3.0)
    out["HD2"] = superiority(stats(vec["K2"] - vec["K1"], b2), 3.0)
    hd3 = stats(vec["K2"] - vec["4C"])
    hd3["non_inferior"] = hd3["ci97_5"][0] > -3.0
    hd3["refuted"] = hd3["ci97_5"][1] < -3.0
    out["HD3"] = hd3
    out["also"] = {"K1-4C": stats(vec["K1"] - vec["4C"]),
                   "K1-C B1": stats(vec["K1"] - vec["C"], b1), "K2-K1 B1": stats(vec["K2"] - vec["K1"], b1),
                   "K2-C all": stats(vec["K2"] - vec["C"]), "K2-C B2": stats(vec["K2"] - vec["C"], b2),
                   "K2-4C B1": stats(vec["K2"] - vec["4C"], b1), "K2-4C B2": stats(vec["K2"] - vec["4C"], b2)}
    out["calls"], out["forced_invalid"], out["errors"], out["dropped_loss_sign"] = {}, {}, {}, {}
    for name in sources:
        rs = rows[name]
        out["forced_invalid"][name] = {"forced": round(100 * float(np.mean([rs[i]["forced"] for i in ids])), 1),
                                       "invalid": round(100 * float(np.mean([not grades[name][i]["valid"] for i in ids])), 1)}
        wrong = [i for i in ids if not grades[name][i]["correct"]]
        out["dropped_loss_sign"][name] = {sec: sum(dropped_loss_sign(by[i], grades[name][i]) for i in wrong if by[i]["section"] == sec)
                                          for sec in ("B1", "B2")}
        if name.startswith(("C", "K")) or name == "4C":
            out["calls"][name] = {sec: {"with_call": round(100 * float(np.mean([bool(rs[i]["calls"]) for i in ids if by[i]["section"] == sec])), 1),
                                        "calls_mean": round(float(np.mean([len(rs[i]["calls"]) for i in ids if by[i]["section"] == sec])), 2)}
                                  for sec in ("B1", "B2")}
            out["errors"][name] = {sec: dict(collections.Counter(X.error_kind(by[i], grades[name][i], rs[i])
                                                                 for i in wrong if by[i]["section"] == sec).most_common())
                                   for sec in ("B1", "B2")}
    out["seed_spread"] = {arm: [out["accuracy"][f"{arm}-s{s}"]["all"] for s in SEEDS] for arm in ("C", "K1", "K2")}
    out["development"] = json.loads((OUT / "dev" / "accuracy.json").read_text())
    out["sets"] = json.loads((OUT / "sets" / "summary.json").read_text())
    labels = E.jl(OUT / "labels" / f"{E.TEACHER}.jsonl")
    out["label_yield"] = {"items": len(labels), "correct_on_attempt": dict(sorted(collections.Counter(
        next((str(k + 1) for k, t in enumerate(r["attempts"]) if t["correct"]), "none") for r in labels).items()))}
    out["training"] = {}
    for run in RUNS:
        log = json.loads((OUT / "checkpoints" / run / "train_log.json").read_text())
        losses = [x for x in log["log"] if x.get("train_loss") is not None]
        pts = losses[:: max(1, len(losses) // 8)] + losses[-1:]
        out["training"][run] = {"iters": log["iters"], "hours": round(log["wall_s"] / 3600, 2), "peak_gib": log["peak_gib"],
                                "loss": {x["iteration"]: round(x["train_loss"], 3) for x in pts}}
    seca_acc = {}
    for name, p in [(n, OUT / "seca" / f"{n}.jsonl") for n in RUNS] + [(n, X.OUT / "seca" / f"{n}.jsonl") for n in ("C-s1", "C-s2", "4C")]:
        if not p.exists():
            continue
        c: dict = collections.defaultdict(list)
        for r in E.jl(p):
            prob = problem_for(r["uid"])
            c[prob.source].append(fgrade(prob, r["response"], thinking=False)["correct"])
        seca_acc[name] = {s: round(100 * sum(v) / len(v), 1) for s, v in c.items()}
    out["section_A"] = seca_acc
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(required=True)
    q = sub.add_parser("label")
    q.add_argument("--limit", type=int, default=0)
    q.set_defaults(fn=label)
    for name, fn in (("maskcheck", maskcheck), ("sets", sets), ("choose", choose), ("queue", queue), ("score", score)):
        sub.add_parser(name).set_defaults(fn=fn)
    for name, fn in (("train", train_cmd), ("dev", dev)):
        q = sub.add_parser(name)
        q.add_argument("--arm", choices=ARMS, required=True)
        q.add_argument("--seed", type=int, choices=SEEDS, required=True)
        q.set_defaults(fn=fn)
    for name, fn in (("test", test), ("seca", seca)):
        q = sub.add_parser(name)
        q.add_argument("--config", choices=RUNS, required=True)
        q.set_defaults(fn=fn)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
