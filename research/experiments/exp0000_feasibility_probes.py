"""EXP-0000: feasibility probes for long-prompt inference and LoRA on this machine.

An engineering measurement with no hypothesis: what a 32 GB Apple-silicon Mac can do with the
Qwen3.5 4-bit checkpoints, so the research design does not assume more than the hardware gives.

  infer   prefill speed, decode speed and peak memory at 4k, 8k, 16k and 32k prompt tokens
  lora    peak memory and time per step of mlx_lm LoRA as the sequence length doubles from 128
          to 8k, and whether the Qwen3.5 layers accept LoRA at all

The LoRA series start at 128 tokens, and include two models with ordinary attention, because of
what the first trial showed: Qwen3.5-4B at 1,024 tokens with 16 LoRA layers died on its first
training step with "[METAL] Command buffer execution failed: Insufficient Memory". Training cannot
use mlx_lm's Metal kernel for the Gated DeltaNet layers and falls back to ``gated_delta_ops``, a
per-token loop whose every step holds a [heads, 128, 128] float32 state (2 MiB on the 4B) for the
backward pass, so memory grows with the sequence length in each of those layers. Training fewer
layers shortens the part of the network the gradient has to cross, hence the 4-layer series.

Run it through the conda env that has mlx_lm and the sibling package ``learnai``::

    conda run --no-capture-output -n py313 python research/experiments/exp0000_feasibility_probes.py queue
    conda run --no-capture-output -n py313 python research/experiments/exp0000_feasibility_probes.py report

Rules it keeps (see AGENTS.md and learning_ai/docs/FINANCE_MODEL_SELECTION.md section 1):

* one MLX job at a time: the queue runs each configuration in its own process, one after another;
* the owner's budget of 12 GiB for an MLX process: sizes go up in order, and a model's sequence
  stops at the first configuration that exceeds the budget, or that a straight-line
  extrapolation of the earlier peaks puts past the abort level;
* nothing is downloaded: a checkpoint that is not already on the external drive is an error;
* outputs go to the external drive, never into the repo; the LoRA adapters are deleted after the
  measurement, so no model comes out of this.

The filler text is the zsh manual already on this machine. Its content does not matter for speed
or memory; only the token count does.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

GIB = 2**30
BUDGET_GIB = 12.0  # the owner's budget for one MLX process
ABORT_GIB = 15.0  # a run that passes this is abandoned at its next check
CACHE_LIMIT_GIB = 1.0
PREFILL_STEP = 512
MODELS = ("qwen3.5-4b", "qwen3.5-9b")
INFER_PROMPTS = (4_000, 8_000, 16_000, 32_000)
LORA_SEQ = (128, 256, 512, 1_024, 2_048, 4_096, 8_192)
LORA_ITERS = 20
# (model, LoRA layers). Gemma 4 12B and DianJin-R1-7B (a Qwen2.5 base) have ordinary attention
# and are here as the comparison for the Gated DeltaNet layers of Qwen3.5.
LORA_SERIES = (
    ("qwen3.5-4b", 16),
    ("qwen3.5-4b", 4),
    ("qwen3.5-9b", 16),
    ("qwen3.5-9b", 4),
    ("gemma4-12b", 16),
    ("dianjin-r1-7b", 16),
)
DRIVE = Path("/Volumes/Seagate Backup Plus Drive")
DEFAULT_OUT = DRIVE / "DATA" / "narrative_lab" / "probes" / "exp0000"
INSTRUCTION = "Summarise the following manual in five sentences."


def out_dir() -> Path:
    out = Path(os.environ.get("NLAB_PROBE_DIR", DEFAULT_OUT))
    if str(out).startswith(str(DRIVE)) and not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    out.mkdir(parents=True, exist_ok=True)
    return out


def filler() -> str:
    path = out_dir() / "filler.txt"
    if not path.exists():
        text = subprocess.run(
            "man -P cat zshall | col -bx", shell=True, capture_output=True, text=True, check=True
        ).stdout
        path.write_text(text, encoding="utf-8")
    return path.read_text(encoding="utf-8")


def snapshot(key: str) -> tuple[str, Path]:
    """The Hugging Face repo and the local snapshot directory; its name is the revision."""
    import learnai.openweights as ow

    path = ow.local_path(key)
    if path is None:
        sys.exit(f"{key} is not on the external drive; this probe downloads nothing")
    return ow.resolve(key).repo, Path(path)


def set_limits():
    import mlx.core as mx

    mx.set_memory_limit(int(BUDGET_GIB * GIB))
    mx.set_cache_limit(int(CACHE_LIMIT_GIB * GIB))
    mx.reset_peak_memory()
    return mx


def versions() -> dict:
    import mlx.core as mx
    import mlx_lm

    return {"mlx": mx.__version__, "mlx_lm": getattr(mlx_lm, "__version__", "?")}


class OverBudget(RuntimeError):
    pass


# ---------------------------------------------------------------- one configuration


def infer_one(key: str, n_prompt: int, max_tokens: int) -> dict:
    import learnai.openweights as ow
    from mlx_lm import load, stream_generate

    repo, path = snapshot(key)
    mx = set_limits()
    t0 = time.time()
    model, tok = load(str(path))
    load_s = time.time() - t0

    ids = tok.encode(filler())
    frame = ow.chat_prompt(tok, [{"role": "user", "content": INSTRUCTION + "\n\n"}], think=False)
    body = tok.decode(ids[: n_prompt - len(tok.encode(frame))])
    prompt = ow.chat_prompt(
        tok, [{"role": "user", "content": INSTRUCTION + "\n\n" + body}], think=False
    )

    def watch(done: int, total: int) -> None:
        if mx.get_peak_memory() > ABORT_GIB * GIB:
            raise OverBudget(f"peak passed {ABORT_GIB} GiB after {done} of {total} prompt tokens")

    mx.reset_peak_memory()
    last, status, t1 = None, "ok", time.time()
    try:
        for last in stream_generate(
            model,
            tok,
            prompt,
            max_tokens=max_tokens,
            prefill_step_size=PREFILL_STEP,
            prompt_progress_callback=watch,
        ):
            if mx.get_peak_memory() > ABORT_GIB * GIB:
                raise OverBudget(f"peak passed {ABORT_GIB} GiB while decoding")
    except OverBudget as err:
        status = f"aborted: {err}"
    peak = mx.get_peak_memory() / GIB
    if status == "ok" and peak > BUDGET_GIB:
        status = "over budget"
    return {
        "probe": "infer",
        "model": key,
        "repo": repo,
        "revision": path.name,
        "size": n_prompt,
        "status": status,
        "prompt_tokens": getattr(last, "prompt_tokens", None),
        "prefill_tok_s": round(last.prompt_tps, 1) if last else None,
        "decode_tokens": getattr(last, "generation_tokens", None),
        "decode_tok_s": round(last.generation_tps, 1) if last else None,
        "peak_gib": round(peak, 2),
        "load_s": round(load_s, 1),
        "wall_s": round(time.time() - t1, 1),
        "prefill_step": PREFILL_STEP,
    }


def lora_one(key: str, seq_len: int, iters: int, num_layers: int) -> dict:
    import types

    from mlx_lm import lora
    from mlx_lm.tuner.callbacks import TrainingCallback
    from transformers import AutoTokenizer

    repo, path = snapshot(key)
    mx = set_limits()
    out = out_dir()

    # Training text: chunks of exactly the sequence length, so every step is a full-length step.
    tok = AutoTokenizer.from_pretrained(str(path))
    ids = tok.encode(filler(), add_special_tokens=False)
    data = out / "lora_data" / f"{key}-{seq_len}"
    data.mkdir(parents=True, exist_ok=True)
    width, n_train, n_valid = seq_len - 4, iters + 2, 2
    chunks = [
        tok.decode(ids[(i * width) % (len(ids) - width) :][:width]) for i in range(n_train + n_valid)
    ]
    for name, rows in (("train", chunks[:n_train]), ("valid", chunks[n_train:])):
        with open(data / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for text in rows:
                fh.write(json.dumps({"text": text}) + "\n")

    reports: list[dict] = []

    class Watch(TrainingCallback):
        def on_train_loss_report(self, info: dict) -> None:
            reports.append(
                {
                    "iteration": info.get("iteration"),
                    "train_loss": info.get("train_loss"),
                    "it_per_s": info.get("iterations_per_second"),
                    "tok_per_s": info.get("tokens_per_second"),
                    "peak_gb_reported": info.get("peak_memory"),
                }
            )
            if mx.get_peak_memory() > ABORT_GIB * GIB:
                raise OverBudget(f"peak passed {ABORT_GIB} GiB by iteration {info.get('iteration')}")

        def on_val_loss_report(self, info: dict) -> None:
            if mx.get_peak_memory() > ABORT_GIB * GIB:
                raise OverBudget(f"peak passed {ABORT_GIB} GiB during validation")

    adapters = out / "adapters" / f"{key}-{seq_len}"
    args = dict(lora.CONFIG_DEFAULTS)
    args.update(
        model=str(path),
        train=True,
        data=str(data),
        batch_size=1,
        iters=iters,
        max_seq_length=seq_len,
        grad_checkpoint=True,
        num_layers=num_layers,
        adapter_path=str(adapters),
        steps_per_report=1,
        steps_per_eval=10**9,
        val_batches=1,
        save_every=10**9,
        seed=0,
    )
    status, t0 = "ok", time.time()
    try:
        lora.run(types.SimpleNamespace(**args), training_callback=Watch())
    except OverBudget as err:
        status = f"aborted: {err}"
    except Exception as err:  # the measurement is "does this work at all", so record the reason
        status = f"failed: {type(err).__name__}: {str(err)[:200]}"
    wall = time.time() - t0
    shutil.rmtree(adapters, ignore_errors=True)  # no model comes out of this probe
    peak = mx.get_peak_memory() / GIB
    if status == "ok" and peak > BUDGET_GIB:
        status = "over budget"
    steady = [r["it_per_s"] for r in reports[1:] if r["it_per_s"]] or [
        r["it_per_s"] for r in reports if r["it_per_s"]
    ]
    return {
        "probe": "lora",
        "model": key,
        "repo": repo,
        "revision": path.name,
        "layers": num_layers,
        "size": seq_len,
        "status": status,
        "iters_done": reports[-1]["iteration"] if reports else 0,
        "s_per_step": round(1 / (sum(steady) / len(steady)), 2) if steady else None,
        "peak_gib": round(peak, 2),
        "last_loss": reports[-1]["train_loss"] if reports else None,
        "wall_s": round(wall, 1),
        "settings": f"rank 8, {num_layers} layers, batch 1, grad checkpoint",
    }


# ---------------------------------------------------------------- the queue


def load_results(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def predicted_next(done: list[dict], size: int) -> float | None:
    """Straight line through the last two peaks, read off at the next size."""
    ok = [r for r in done if r["status"] == "ok"]
    if len(ok) < 2:
        return None
    a, b = ok[-2], ok[-1]
    slope = (b["peak_gib"] - a["peak_gib"]) / (b["size"] - a["size"])
    return b["peak_gib"] + slope * (size - b["size"])


def queue(args: argparse.Namespace) -> None:
    out = out_dir()
    results_path = out / "results.jsonl"
    logs = out / "logs"
    logs.mkdir(exist_ok=True)
    plan = [("infer", m, 0, INFER_PROMPTS) for m in MODELS]
    plan += [("lora", m, layers, LORA_SEQ) for m, layers in LORA_SERIES]
    for probe, model, layers, sizes in plan:
        for size in sizes:
            rows = load_results(results_path)
            series = [
                r
                for r in rows
                if r["probe"] == probe and r["model"] == model and r.get("layers", 0) == layers
            ]
            if any(r["size"] == size for r in series):
                continue  # resumable: this configuration is already recorded
            row = {"probe": probe, "model": model, "layers": layers, "size": size}
            if series and series[-1]["status"] != "ok":
                row["status"] = f"skipped: {series[-1]['size']} ended as {series[-1]['status'][:60]}"
            elif (guess := predicted_next(series, size)) is not None and guess > ABORT_GIB:
                row["status"] = f"skipped: predicted peak {guess:.1f} GiB"
            else:
                flag = "--prompt-tokens" if probe == "infer" else "--seq-len"
                cmd = [sys.executable, __file__, f"{probe}-one", "--model", model, flag, str(size)]
                if probe == "lora":
                    cmd += ["--num-layers", str(layers)]
                log = logs / f"{probe}-{model}-L{layers}-{size}.log"
                print(f"[queue] {probe} {model} {size} ...", flush=True)
                try:
                    done = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
                    text = done.stdout + "\n--- stderr ---\n" + done.stderr
                except subprocess.TimeoutExpired as err:
                    done, text = None, f"timeout after {args.timeout}s\n{err.stdout or ''}"
                log.write_text(text, encoding="utf-8")
                hit = re.search(r"^RESULT (\{.*\})$", text, flags=re.M)
                if hit:
                    row = json.loads(hit.group(1))
                else:
                    code = done.returncode if done else "timeout"
                    row["status"] = f"crashed: exit {code}, see {log.name}"
                row.setdefault("layers", layers)
                trainable = re.search(r"Trainable parameters: ([0-9.]+)% \(([0-9.]+)M/([0-9.]+)M\)", text)
                if trainable:
                    row["trainable_pct"] = float(trainable.group(1))
                    row["trainable_m"] = float(trainable.group(2))
                row["command"] = "conda run -n py313 python " + " ".join(
                    ["research/experiments/exp0000_feasibility_probes.py", *cmd[2:]]
                )
            row.update(versions())
            row["recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            with open(results_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
            print(f"[queue] {json.dumps(row)}", flush=True)


def report(_: argparse.Namespace) -> None:
    rows = load_results(out_dir() / "results.jsonl")
    print("### Inference\n")
    print("| model | revision | prompt tokens | prefill tok/s | decode tok/s | peak GiB | status |")
    print("|---|---|---|---|---|---|---|")
    for r in (r for r in rows if r["probe"] == "infer"):
        print(
            f"| {r['model']} | {str(r.get('revision', ''))[:8]} | {r.get('prompt_tokens', r['size'])} "
            f"| {r.get('prefill_tok_s', '')} | {r.get('decode_tok_s', '')} | {r.get('peak_gib', '')} "
            f"| {r['status']} |"
        )
    print("\n### LoRA\n")
    print("| model | revision | LoRA layers | sequence length | s/step | peak GiB | trainable | status |")
    print("|---|---|---|---|---|---|---|---|")
    for r in (r for r in rows if r["probe"] == "lora"):
        trainable = f"{r['trainable_m']}M ({r['trainable_pct']}%)" if "trainable_m" in r else ""
        print(
            f"| {r['model']} | {str(r.get('revision', ''))[:8]} | {r.get('layers', '')} | {r['size']} "
            f"| {r.get('s_per_step', '')} "
            f"| {r.get('peak_gib', '')} | {trainable} | {r['status']} |"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("infer-one")
    one.add_argument("--model", required=True)
    one.add_argument("--prompt-tokens", type=int, required=True)
    one.add_argument("--max-tokens", type=int, default=300)
    one = sub.add_parser("lora-one")
    one.add_argument("--model", required=True)
    one.add_argument("--seq-len", type=int, required=True)
    one.add_argument("--iters", type=int, default=LORA_ITERS)
    one.add_argument("--num-layers", type=int, default=16)
    q = sub.add_parser("queue")
    q.add_argument("--timeout", type=int, default=3600, help="seconds per configuration")
    sub.add_parser("report")
    args = parser.parse_args()
    if args.cmd == "infer-one":
        print("RESULT " + json.dumps(infer_one(args.model, args.prompt_tokens, args.max_tokens)))
    elif args.cmd == "lora-one":
        print("RESULT " + json.dumps(lora_one(args.model, args.seq_len, args.iters, args.num_layers)))
    elif args.cmd == "queue":
        queue(args)
    else:
        report(args)


if __name__ == "__main__":
    main()
