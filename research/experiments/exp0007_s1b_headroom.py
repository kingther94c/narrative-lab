"""EXP-0007: S1-b headroom. The S1 ladder zero-shot on EarningsExam v0 development items.

Pre-registered in research/registry/experiment_registry.md (commit 8e2db31, pushed before any
model saw a sampled item). Descriptive: accuracy per rung, the gaps that gate S1-c, the
disagreement rates that size the S1 test set, and answer lengths.

  draw    the 600-item draw from post-cutoff development items (rules in the registry entry)
  run     one model in one mode over the draw; resumable, one JSON line per item with the raw
          response, so every score can be traced to it
  queue   every pre-registered run in the registered order, one MLX process at a time
  score   scores, intervals, gates, test-set size and answer lengths, to scores.json

`run --limit N` is a smoke test on N pre-cutoff development items outside the draw, written apart.

Run::

    conda run --no-capture-output -n py313 python research/experiments/exp0007_s1b_headroom.py draw
    conda run --no-capture-output -n py313 python research/experiments/exp0007_s1b_headroom.py queue
    conda run --no-capture-output -n py313 python research/experiments/exp0007_s1b_headroom.py score

Only development items are read; test items are never opened.
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

GIB = 2**30
BUDGET_GIB = 12.0
DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA")
HF = DRIVE / "huggingface"
ITEMS = DRIVE / "narrative_lab" / "s1" / "exam_v0_1" / "items_dev.jsonl"  # amended 2026-11-17 (EXP-0008)
OUT = DRIVE / "narrative_lab" / "s1" / "exp0007"
DRAW = OUT / "draw.jsonl"

QUOTA = {
    "B1:revenue:p1": 90, "B1:operating_income:p1": 90, "B1:net_income:p1": 90,
    "B1:eps_diluted:p1": 90,
    "B2:revenue_growth:p1": 80, "B2:operating_margin:p1": 80, "B2:eps_change:p1": 80,
}
PER_COMPANY = 2
THINKING_SUBSET = 300
CUTOFF = "2026-07-01"  # releases accepted after 2026-06-30

MODELS = {  # key: (snapshot folder, revision, family)
    "qwen3.5-0.8b": ("models--Qwen--Qwen3.5-0.8B", "2fc06364715b967f1860aea9cf38778875588b17", "qwen"),
    "qwen3.5-2b": ("models--mlx-community--Qwen3.5-2B-MLX-4bit", "93760be4f1f69842a46bc13dbdc0f19e291392a3", "qwen"),
    "qwen3.5-4b": ("models--mlx-community--Qwen3.5-4B-MLX-4bit", "32f3e8ecf65426fc3306969496342d504bfa13f3", "qwen"),
    "qwen3.5-9b": ("models--mlx-community--Qwen3.5-9B-MLX-4bit", "938d8919941c6e7efd3c7150eff7fe9d12afa631", "qwen"),
    "olmoe-1b-7b": ("models--mlx-community--OLMoE-1B-7B-0125-Instruct-4bit", "e23844197887b031e7ddddbb0b8959c5a6853a7b", "olmoe"),
}
CAP = {"off": 256, "on": 2_048}
FORCE_TOKENS = 48
CUE = "\n\n**Final answer:** \\boxed{"
INSTRUCTION = "Reason briefly, then give the final number in \\boxed{}."
QUEUE = [(m, "off") for m in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b", "olmoe-1b-7b")] + [
    (m, "on") for m in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b")
]
BOOT, BOOT_SEED = 2_000, 20261117
PAIRS_GATE = [("qwen3.5-9b", "qwen3.5-4b"), ("qwen3.5-9b", "qwen3.5-0.8b"), ("qwen3.5-4b", "qwen3.5-0.8b")]


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted")
    OUT.mkdir(parents=True, exist_ok=True)


def responses_path(model: str, mode: str) -> Path:
    return OUT / "responses" / f"{model}-{mode}.jsonl"


# ---------------------------------------------------------------- draw


def draw(_: argparse.Namespace) -> None:
    need_drive()
    if DRAW.exists():
        sys.exit(f"{DRAW} exists; the draw is made once")
    rows = []
    with open(ITEMS, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            assert r["side"] == "dev"
            if r["post_cutoff"] and r["acceptance"] >= CUTOFF:
                rows.append(r)
    key = lambda r: hashlib.sha256(f"exp0007:{r['id']}".encode()).hexdigest()
    queues = {t: sorted((r for r in rows if r["template"] == t), key=key) for t in QUOTA}
    quota = dict(QUOTA)
    per_co: collections.Counter = collections.Counter()
    rel_sec: set = set()
    got: collections.Counter = collections.Counter()
    chosen: list[dict] = []

    def admissible(r) -> bool:
        return per_co[r["cik"]] < PER_COMPANY and (r["accession"], r["section"]) not in rel_sec

    def next_of(t):
        q = queues[t]
        while q and not admissible(q[0]):
            q.pop(0)
        return q.pop(0) if q else None

    active = list(QUOTA)
    while active:
        for t in list(active):
            if got[t] >= quota[t]:
                active.remove(t)
                continue
            r = next_of(t)
            if r is None:  # template exhausted: its remaining places go to its section's others
                short = quota[t] - got[t]
                quota[t] = got[t]
                active.remove(t)
                others = [o for o in QUOTA if o.split(":")[0] == t.split(":")[0] and o != t and o in active]
                for i in range(short):
                    if others:
                        quota[others[i % len(others)]] += 1
                continue
            per_co[r["cik"]] += 1
            rel_sec.add((r["accession"], r["section"]))
            got[t] += 1
            chosen.append(r)
    with open(DRAW, "w", encoding="utf-8") as fh:
        for i, r in enumerate(chosen):
            fh.write(json.dumps({"order": i, "id": r["id"], "template": r["template"], "cik": r["cik"]}) + "\n")
    digest = hashlib.sha256("\n".join(r["id"] for r in chosen).encode()).hexdigest()
    summary = {"items": len(chosen), "by_template": dict(got), "quota_after_redistribution": quota,
               "companies": len(per_co), "pool": len(rows), "sha256_of_ids": digest}
    (OUT / "draw_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def load_draw() -> list[dict]:
    order = [json.loads(l) for l in DRAW.read_text().splitlines()]
    wanted = {o["id"] for o in order}
    items = {}
    with open(ITEMS, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["id"] in wanted:
                items[r["id"]] = r
    return [items[o["id"]] for o in order]


# ---------------------------------------------------------------- run


def model_path(key: str) -> Path:
    folder, rev, _ = MODELS[key]
    path = HF / folder / "snapshots" / rev
    if not path.is_dir():
        sys.exit(f"{path} missing; nothing is downloaded")
    return path


def build_prompt(tok, family: str, item: dict, mode: str) -> str:
    msg = [{"role": "user", "content": f"{item['excerpt']}\n\n{item['question']} {INSTRUCTION}"}]
    if family == "qwen":
        return tok.apply_chat_template(msg, add_generation_prompt=True, tokenize=False,
                                       enable_thinking=(mode == "on"))
    assert mode == "off"
    return tok.apply_chat_template(msg, add_generation_prompt=True, tokenize=False)


def generate(model, tok, prompt: str, max_tokens: int) -> tuple[str, int, str]:
    from mlx_lm import stream_generate

    text, n, reason = [], 0, None
    for resp in stream_generate(model, tok, prompt, max_tokens=max_tokens):
        text.append(resp.text)
        n = resp.generation_tokens
        reason = resp.finish_reason
    return "".join(text), n, reason


def run(args: argparse.Namespace) -> None:
    import mlx.core as mx
    from learnai.finbench import last_boxed
    from mlx_lm import load

    need_drive()
    key, mode = args.model, args.mode
    family = MODELS[key][2]
    items = load_draw()
    if mode == "on":
        items = items[:THINKING_SUBSET]
    if args.limit:  # smoke test on pre-cutoff development items, never on the draw
        with open(ITEMS, encoding="utf-8") as fh:
            pre = [r for r in map(json.loads, fh) if not r["post_cutoff"]]
        pre.sort(key=lambda r: hashlib.sha256(f"smoke:{r['id']}".encode()).hexdigest())
        items = pre[: args.limit]
    path = responses_path(key, mode) if not args.limit else OUT / "smoke" / f"{key}-{mode}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if path.exists():
        done = {json.loads(l)["id"] for l in path.read_text().splitlines() if l.strip()}
    mx.set_memory_limit(int(BUDGET_GIB * GIB))
    mx.set_cache_limit(GIB)
    model, tok = load(str(model_path(key)))
    import mlx_lm

    for item in items:
        if item["id"] in done:
            continue
        prompt = build_prompt(tok, family, item, mode)
        t0 = time.time()
        out, n_gen, reason = generate(model, tok, prompt, CAP[mode])
        forced, cont, n_force = None, "", 0
        if reason == "length":  # the cap was reached: force an answer if none was given
            closed = mode == "off" or "</think>" in out
            answer_part = out.split("</think>")[-1] if mode == "on" else out
            if not closed:
                forced = "\n</think>" + CUE
            elif last_boxed(answer_part) is None:
                forced = CUE
            if forced:
                cont, n_force, _ = generate(model, tok, prompt + out + forced, FORCE_TOKENS)
        row = {
            "id": item["id"], "model": key, "revision": MODELS[key][1], "mode": mode,
            "prompt_tokens": len(tok.encode(prompt)), "generated_tokens": n_gen, "finish": reason,
            "forced": bool(forced), "forced_tokens": n_force,
            "response": out + (forced or "") + cont, "seconds": round(time.time() - t0, 2),
            "peak_gib": round(mx.get_peak_memory() / GIB, 2),
            "mlx": mx.__version__, "mlx_lm": getattr(mlx_lm, "__version__", "?"),
        }
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        if args.limit:
            print(json.dumps({k: row[k] for k in ("generated_tokens", "finish", "forced", "seconds")}),
                  "|", row["response"][-300:].replace("\n", " "))


def queue(_: argparse.Namespace) -> None:
    need_drive()
    for key, mode in QUEUE:
        n_target = THINKING_SUBSET if mode == "on" else sum(QUOTA.values())
        path = responses_path(key, mode)
        n_done = len(path.read_text().splitlines()) if path.exists() else 0
        if n_done >= n_target:
            continue
        print(f"{time.strftime('%H:%M:%S')} {key} {mode}: {n_done} done", flush=True)
        subprocess.run([sys.executable, __file__, "run", "--model", key, "--mode", mode], check=False)


# ---------------------------------------------------------------- score


def grade(item: dict, response: str, mode: str) -> dict:
    from learnai.finbench import last_boxed, parse_number, split_thinking

    reasoning, answer = split_thinking(response, thinking=(mode == "on"))
    boxed = last_boxed(answer if answer is not None else reasoning)
    parsed = parse_number(boxed) if boxed is not None else None
    value = parsed[0] if parsed else None
    correct = value is not None and abs(value - float(item["gold"])) <= item["tolerance"]["abs"]
    return {"boxed": boxed, "value": value, "valid": value is not None, "correct": bool(correct)}


def score(_: argparse.Namespace) -> None:
    import numpy as np

    need_drive()
    items = {it["id"]: it for it in load_draw()}
    ids = list(items)
    company = np.array([items[i]["cik"] for i in ids])
    section = np.array([items[i]["section"] for i in ids])
    cos = sorted(set(company))
    co_idx = {c: [k for k, x in enumerate(company) if x == c] for c in cos}
    rng = np.random.default_rng(BOOT_SEED)
    boot = [rng.integers(0, len(cos), len(cos)) for _ in range(BOOT)]

    runs: dict = {}
    for key, mode in QUEUE:
        path = responses_path(key, mode)
        if not path.exists():
            continue
        rows = {r["id"]: r for r in map(json.loads, path.read_text().splitlines())}
        g = {i: {**grade(items[i], rows[i]["response"], mode), **{k: rows[i][k] for k in
             ("generated_tokens", "forced", "seconds", "peak_gib")}} for i in rows}
        runs[(key, mode)] = g

    def vec(key, mode, field="correct"):
        g = runs[(key, mode)]
        return np.array([float(g[i][field]) if i in g else np.nan for i in ids])

    def ci(values_fn, mask):
        """Company bootstrap of a statistic over the masked items; values_fn(index array) -> float."""
        stats = []
        for b in boot:
            idx = np.concatenate([co_idx[cos[j]] for j in b])
            idx = idx[mask[idx]]
            if len(idx):
                stats.append(values_fn(idx))
        return [round(float(np.percentile(stats, 2.5)) * 100, 1), round(float(np.percentile(stats, 97.5)) * 100, 1)]

    out: dict = {"draw": json.loads((OUT / "draw_summary.json").read_text()), "runs": {}, "gates": {}}
    for (key, mode), g in runs.items():
        c = vec(key, mode)
        have = ~np.isnan(c)
        entry = {"n": int(have.sum())}
        for sec in ("B1", "B2", "all"):
            m = have & ((section == sec) if sec != "all" else True)
            if m.sum() == 0:
                continue
            entry[sec] = {"acc": round(float(np.nanmean(c[m])) * 100, 1), "n": int(m.sum()),
                          "ci95": ci(lambda idx: np.mean(c[idx]), m)}
        tmpl = collections.defaultdict(list)
        for k, i in enumerate(ids):
            if have[k]:
                tmpl[items[i]["template"]].append(c[k])
        entry["by_template"] = {t: round(float(np.mean(v)) * 100, 1) for t, v in sorted(tmpl.items())}
        conv = [c[k] for k, i in enumerate(ids) if have[k] and items[i]["section"] == "B1" and items[i]["scale_conversion"]]
        entry["b1_scale_conversion_acc"] = round(float(np.mean(conv)) * 100, 1) if conv else None
        toks = np.array([g[i]["generated_tokens"] for i in ids if i in g])
        entry["generated_tokens"] = {"median": int(np.median(toks)), "p90": int(np.percentile(toks, 90))}
        entry["forced_rate"] = round(float(np.mean([g[i]["forced"] for i in g])) * 100, 1)
        entry["invalid_rate"] = round(float(np.mean([not g[i]["valid"] for i in g])) * 100, 1)
        entry["seconds_median"] = float(np.median([g[i]["seconds"] for i in g]))
        entry["peak_gib"] = max(g[i]["peak_gib"] for i in g)
        if mode == "off" and key in ("qwen3.5-9b", "qwen3.5-4b"):
            right = [g[i]["generated_tokens"] for i in g if g[i]["correct"]]
            entry["correct_within"] = {b: round(float(np.mean([t <= b for t in right])) * 100, 1) for b in (64, 128)} if right else None
        out["runs"][f"{key}/{mode}"] = entry

    def gap(a, b, mode, sec):
        ca, cb = vec(a, mode), vec(b, mode)
        m = ~np.isnan(ca) & ~np.isnan(cb) & ((section == sec) if sec != "all" else True)
        d = ca - cb
        return {"gap": round(float(np.mean(d[m])) * 100, 1), "ci95": ci(lambda idx: np.mean(d[idx]), m),
                "discordant": round(float(np.mean(ca[m] != cb[m])), 3), "n": int(m.sum())}

    # Criterion 1: distillation gate per pair, thinking off.
    for a, b in PAIRS_GATE:
        if (a, "off") in runs and (b, "off") in runs:
            res = {sec: gap(a, b, "off", sec) for sec in ("B1", "B2")}
            res["passes"] = any(r["gap"] >= 5.0 and r["ci95"][0] > 0 for r in res.values())
            out["gates"][f"{a} -> {b}"] = res
    # Thinking on, reported beside.
    out["gaps_thinking_on"] = {f"{a} -> {b}": {sec: gap(a, b, "on", sec) for sec in ("B1", "B2")}
                               for a, b in PAIRS_GATE if (a, "on") in runs and (b, "on") in runs}
    # Criterion 2: ceiling and floor, thinking off.
    out["ceiling_floor"] = {}
    for (key, mode), _ in runs.items():
        if mode != "off":
            continue
        for sec in ("B1", "B2"):
            acc = out["runs"][f"{key}/off"][sec]["acc"]
            out["ceiling_floor"][f"{key}/{sec}"] = "ceiling" if acc > 95 else "floor" if acc < 20 else "ok"
    # Criterion 3: test-set size.
    from statistics import NormalDist

    z = NormalDist().inv_cdf(1 - 0.0125 / 2) + NormalDist().inv_cdf(0.80)
    dense_mem = {k: out["runs"][f"{k}/off"]["peak_gib"] for k in ("qwen3.5-0.8b", "qwen3.5-2b", "qwen3.5-4b", "qwen3.5-9b")
                 if f"{k}/off" in out["runs"]}
    sizing = {}
    stand_ins = {"H1/H2": ("qwen3.5-4b", "qwen3.5-0.8b"), "H5": ("qwen3.5-4b", "qwen3.5-2b")}
    if "olmoe-1b-7b/off" in out["runs"] and dense_mem:
        moe = out["runs"]["olmoe-1b-7b/off"]["peak_gib"]
        stand_ins["H8"] = ("olmoe-1b-7b", min(dense_mem, key=lambda k: abs(dense_mem[k] - moe)))
    for h, (a, b) in stand_ins.items():
        if (a, "off") not in runs or (b, "off") not in runs:
            continue
        ca, cb = vec(a, "off"), vec(b, "off")
        m = ~np.isnan(ca) & ~np.isnan(cb)
        d = (ca - cb)[m]
        disc = float(np.mean(d != 0))
        iid_var = float(np.var(d, ddof=1)) / m.sum()
        boot_var = float(np.var([np.mean((ca - cb)[np.concatenate([co_idx[cos[j]] for j in b_])][m[np.concatenate([co_idx[cos[j]] for j in b_])]]) for b_ in boot], ddof=1))
        de = boot_var / iid_var if iid_var > 0 else 1.0
        sizing[h] = {"pair": f"{a} vs {b}", "discordant": round(disc, 3), "design_effect": round(de, 2),
                     "n": int(np.ceil(de * z**2 * disc / 0.03**2))}
    out["test_size"] = {"per_pair": sizing, "n": max((s["n"] for s in sizing.values()), default=None)}
    (OUT / "scores.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("draw").set_defaults(fn=draw)
    r = sub.add_parser("run")
    r.add_argument("--model", choices=list(MODELS), required=True)
    r.add_argument("--mode", choices=("off", "on"), required=True)
    r.add_argument("--limit", type=int, default=0, help="smoke test on the first N items; separate output")
    r.set_defaults(fn=run)
    sub.add_parser("queue").set_defaults(fn=queue)
    sub.add_parser("score").set_defaults(fn=score)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
