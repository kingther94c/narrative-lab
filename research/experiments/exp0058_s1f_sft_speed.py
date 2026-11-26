"""EXP-0058: full fine-tuning speed and memory of the 0.8B at the factory's sequence lengths (S1 re-plan).

The re-plan's fine-tuning rate was wrong (about 680 sequences an hour at 512 tokens, not 1,260;
correction in its §4.5), and the feasibility probe measured only 512 and 1,024 tokens (7.17 and
14.45 GiB). This measures the lengths a shortened factory item would have, with EXP-0014's exact
setup (every block trained, embeddings frozen, AdamW at 1e-5 with warm-up, batch 1, gradient
checkpointing, prompt masked), so the main pre-registration can set sizes from measurements.
An engineering step with no hypothesis.

Sequences are EXP-0056's pilot chains (training companies only) with their item prompts, cut or
repeated to exactly the target length (the loss covers the chain part), 40 steps a length; the
first 10 steps are dropped as warm-up. The run stops at a length whose peak passes 12 GiB.

    conda run --no-capture-output -n py313 python research/experiments/exp0058_s1f_sft_speed.py run --lengths 640,768,896
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exp0014_s1c_distillation as D14  # noqa: E402  (frozen; the training setup)
import exp0056_s1f_chains as X56  # noqa: E402  (frozen; the pilot chains)

S = D14.S
OUT = X56.E.DRIVE / "s1" / "exp0058"
STEPS, DROP = 40, 10


def sequences(tok, length: int, n: int) -> list[tuple[list[int], int]]:
    items = {i["id"]: i for i in X56.pool(200)}
    rows = [json.loads(l) for l in open(X56.OUT / "pilot" / "kept.jsonl", encoding="utf-8")]
    out = []
    for r in rows:
        p = tok.apply_chat_template([{"role": "user", "content": items[r["id"]]["prompt"]}], add_generation_prompt=True,
                                    tokenize=False, enable_thinking=False)
        pt, ct = tok.encode(p), tok.encode(r["response"]) + [tok.eos_token_id]
        seq = (pt + ct * (1 + length // max(1, len(ct))))[:length]
        out.append((seq, min(len(pt), length - 64)))
        if len(out) == n:
            break
    return out


def run(a):
    import mlx.core as mx
    import mlx.optimizers as optim
    import numpy as np
    from mlx_lm import load
    from mlx_lm.tuner.callbacks import TrainingCallback
    from mlx_lm.tuner.trainer import TrainingArgs, train

    OUT.mkdir(parents=True, exist_ok=True)
    res = []
    for length in [int(x) for x in a.lengths.split(",")]:
        mx.set_memory_limit(int(S.BUDGET_GIB * S.GIB))
        mx.set_cache_limit(S.GIB)
        mx.reset_peak_memory()
        np.random.seed(1)
        mx.random.seed(1)
        model, tok = load(str(S.model_path(D14.STUDENT)))
        model.freeze()
        for layer in model.layers:
            layer.unfreeze()
        data = D14.Seqs([{"tokens": t, "offset": o} for t, o in sequences(tok, length, STEPS)])
        sched = optim.join_schedules([optim.linear_schedule(1e-8, D14.LR, D14.WARMUP),
                                      optim.cosine_decay(D14.LR, 1000)], [D14.WARMUP])
        log = []

        class Watch(TrainingCallback):
            def on_train_loss_report(self, info):
                log.append({"iteration": info.get("iteration"), "its": info.get("iterations_per_second"),
                            "peak": mx.get_peak_memory() / S.GIB})
                if mx.get_peak_memory() > S.BUDGET_GIB * S.GIB:
                    raise RuntimeError("over budget")

        args = TrainingArgs(batch_size=1, iters=STEPS, steps_per_report=5, steps_per_eval=10**9, steps_per_save=10**9,
                            max_seq_length=length, adapter_file=str(OUT / "scratch.safetensors"), grad_checkpoint=True)
        t0, err = time.time(), None
        try:
            train(model, optim.AdamW(learning_rate=sched), data, None, args=args, training_callback=Watch())
        except RuntimeError as e:
            err = str(e)
        steady = [r["its"] for r in log if r["iteration"] and r["iteration"] > DROP and r["its"]]
        sps = 1 / (sum(steady) / len(steady)) if steady else None
        row = {"length": length, "steps": len(log) * 5, "s_per_step": round(sps, 2) if sps else None,
               "sequences_per_hour": round(3600 / sps) if sps else None,
               "peak_gib": round(mx.get_peak_memory() / S.GIB, 2), "wall_s": round(time.time() - t0), "error": err}
        res.append(row)
        print(json.dumps(row), flush=True)
        del model
        if err:
            break
    (OUT / "speed.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (OUT / "scratch.safetensors").unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(required=True)
    r = sub.add_parser("run"); r.add_argument("--lengths", default="640,768,896"); r.set_defaults(fn=run)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
