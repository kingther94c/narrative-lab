"""EXP-0006: S1-a probes for sub-study S1. Can this machine remove layers, remove experts and fine-tune
the small rungs, within the owner's 12 GiB budget?

An engineering measurement with no hypothesis (plan: research/design/substudy_s1_distill_prune.md
section 4, S1-a.3 to S1-a.5). It answers whether the operations S1-c to S1-e rely on work at all.
It does not compare compression methods: the calibration and evaluation text here is a handful of
training-side exam excerpts, so any loss it prints is a sanity check that pruning did something
sensible, not a result.

  layers   S1-a.4. Qwen3.5-4B: score each 4-layer block (three Gated DeltaNet layers and one
           full-attention layer) by block influence, 1 - cos(input, output), on calibration
           excerpts. Remove the 2 and the 4 lowest-scoring blocks, never the first or last block,
           so the pattern stays valid and the checkpoint loads with stock mlx_lm. Check that
           cached decoding matches a full forward, save, reload and check again. Also removes one
           DeltaNet layer alone, to show what finer removal would need.
  experts  S1-a.5. OLMoE-1B-7B: route calibration excerpts and record, per layer and expert, the
           routing count and the REAP score (mean router weight times expert output norm over the
           tokens routed to it). Slice the router rows and the stacked expert tensors down to the
           top half by REAP and check the sliced model against the unpruned model with the
           removed experts' router logits set to minus infinity, which is the same function.
           Save, reload, check again. Losses at 25% and 50% for REAP, frequency and random.
  train    S1-a.3. Peak memory and time per step of mlx_lm LoRA and full fine-tuning: Qwen3.5-0.8B
           (LoRA at 512 to 4,096 tokens, full at 512 to 2,048), and LoRA on the 4B with 2 or 4
           blocks removed. A series stops at the first configuration over budget.
  fit      CPU only: how many training items leave room for an answer within 512 tokens.
  queue    runs layers, experts, then each train configuration, one process at a time; then
           deletes the pruned checkpoints, so no model comes out of this probe.
  report   prints the tables.

Run::

    conda run --no-capture-output -n py313 python research/experiments/exp0006_s1a_compression_probes.py queue
    conda run --no-capture-output -n py313 python research/experiments/exp0006_s1a_compression_probes.py report

Rules it keeps: one MLX job at a time; 12 GiB budget, abort at 15; nothing is downloaded (models
are read from their snapshot folders on the external drive); outputs go to the drive; only
training-side exam excerpts are read (pre-cutoff releases of training companies).
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
import types
from pathlib import Path

GIB = 2**30
BUDGET_GIB = 12.0
ABORT_GIB = 15.0
CACHE_LIMIT_GIB = 1.0
SEED = 0
N_CALIB, N_EVAL, N_CHECK = 64, 32, 8

DRIVE = Path("/Volumes/Seagate Backup Plus Drive/DATA")
HF = DRIVE / "huggingface"
NLAB = DRIVE / "narrative_lab"
ITEMS = NLAB / "s1" / "exam_v0" / "items_train.jsonl"
OUT = NLAB / "s1" / "probes" / "exp0006"
PRUNED = OUT / "pruned"
RESULTS = OUT / "results.jsonl"

SNAPSHOTS = {
    "qwen3.5-0.8b": "models--Qwen--Qwen3.5-0.8B",
    "qwen3.5-4b": "models--mlx-community--Qwen3.5-4B-MLX-4bit",
    "olmoe-1b-7b": "models--mlx-community--OLMoE-1B-7B-0125-Instruct-4bit",
}
BLOCK = 4  # full_attention_interval: layers 4k..4k+2 are DeltaNet, 4k+3 is full attention
REMOVE_BLOCKS = (2, 4)  # 32 -> 24 layers (about 3B) and 32 -> 16 layers (about 2B)
EXPERT_RATIOS = (0.25, 0.50)
TRAIN_ITERS = 10
TRAIN_SERIES = (
    # (model key, fine-tune type, layers trained, sequence lengths)
    ("qwen3.5-0.8b", "lora", 24, (512, 1_024, 2_048, 4_096)),
    ("qwen3.5-0.8b", "full", 24, (512, 1_024, 2_048)),
    ("qwen3.5-4b-minus4", "lora", 16, (512, 1_024, 2_048)),
    ("qwen3.5-4b-minus2", "lora", 24, (512, 1_024)),
)


# ---------------------------------------------------------------- shared


def need_drive() -> None:
    if not DRIVE.is_dir():
        sys.exit(f"{DRIVE} is not mounted; refusing to fall back to the internal disk")
    OUT.mkdir(parents=True, exist_ok=True)


def model_path(key: str) -> Path:
    if key.startswith("qwen3.5-4b-minus"):
        path = PRUNED / key
        if not path.is_dir():
            sys.exit(f"{path} missing; run the layers probe first")
        return path
    snaps = sorted((HF / SNAPSHOTS[key] / "snapshots").glob("*"))
    if len(snaps) != 1:
        sys.exit(f"{key}: expected one snapshot on the drive, found {len(snaps)}; nothing is downloaded")
    return snaps[0]


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


def record(row: dict) -> None:
    row = {"when": time.strftime("%Y-%m-%dT%H:%M:%S"), **versions(), **row}
    with open(RESULTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    print(json.dumps(row, indent=1))


def excerpts() -> tuple[list[dict], list[dict]]:
    """Training-side items, one per release, in a fixed hashed order: calibration, then evaluation."""
    by_release: dict[str, dict] = {}
    with open(ITEMS, encoding="utf-8") as fh:
        for line in fh:
            item = json.loads(line)
            assert item["side"] == "train" and not item["post_cutoff"]
            by_release.setdefault(item["accession"], item)
    order = sorted(by_release.values(), key=lambda r: hashlib.sha256(r["id"].encode()).hexdigest())
    return order[:N_CALIB], order[N_CALIB : N_CALIB + N_EVAL]


def token_batches(tok, items: list[dict]) -> list:
    import mlx.core as mx

    return [mx.array(tok.encode(it["excerpt"]))[None] for it in items]


def mean_nll(model, batches) -> float:
    import mlx.core as mx
    import mlx.nn as nn

    total, count = 0.0, 0
    for ids in batches:
        logits = model(ids[:, :-1]).astype(mx.float32)
        loss = nn.losses.cross_entropy(logits, ids[:, 1:], reduction="sum")
        mx.eval(loss)
        total += loss.item()
        count += ids.shape[1] - 1
    return round(total / count, 4)


def cache_check(model, ids, tail: int = 8) -> dict:
    """Prefill all but the last ``tail`` tokens, decode them one at a time with the cache, and
    compare each step's logits with the full forward at the same position."""
    import mlx.core as mx
    from mlx_lm.models.cache import make_prompt_cache

    full = model(ids).astype(mx.float32)
    cache = make_prompt_cache(model)
    n = ids.shape[1] - tail
    model(ids[:, :n], cache=cache)
    worst, agree = 0.0, 0
    for t in range(n, ids.shape[1]):
        step = model(ids[:, t : t + 1], cache=cache).astype(mx.float32)[0, -1]
        ref = full[0, t]
        mx.eval(step, ref)
        worst = max(worst, mx.abs(step - ref).max().item())
        agree += int(mx.argmax(step).item() == mx.argmax(ref).item())
    return {"max_abs_logit_diff": round(worst, 4), "argmax_agree": f"{agree}/{tail}"}


def answer_sample(model, tok, item: dict, max_tokens: int = 48) -> str:
    from mlx_lm import generate

    messages = [{"role": "user", "content": f"{item['excerpt']}\n\n{item['question']} "
                 "Put the final number in \\boxed{}."}]
    prompt = tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False,
                                     enable_thinking=False)
    return generate(model, tok, prompt, max_tokens=max_tokens, verbose=False).strip()


def dir_gib(path: Path) -> float:
    return round(sum(p.stat().st_size for p in path.rglob("*.safetensors")) / GIB, 2)


def n_params(model) -> int:
    from mlx_lm.utils import get_total_parameters

    return int(get_total_parameters(model))


# ---------------------------------------------------------------- S1-a.4 layers


def text_model(model):
    return model.language_model.model if hasattr(model, "language_model") else model.model


def block_influence(model, batches) -> tuple[list[float], list[float]]:
    """Mean over tokens of 1 - cos(input, output), for each layer and each 4-layer block."""
    import mlx.core as mx
    from mlx_lm.models.base import create_attention_mask, create_ssm_mask

    tm = text_model(model)
    layers = tm.layers
    per_layer = [0.0] * len(layers)
    per_block = [0.0] * (len(layers) // BLOCK)
    n_tok = 0

    def one_minus_cos(a, b):
        a, b = a.astype(mx.float32), b.astype(mx.float32)
        cos = (a * b).sum(-1) / (mx.linalg.norm(a, axis=-1) * mx.linalg.norm(b, axis=-1) + 1e-6)
        return (1 - cos).sum()

    for ids in batches:
        h = tm.embed_tokens(ids)
        fa_mask, ssm_mask = create_attention_mask(h, None), create_ssm_mask(h, None)
        block_in = h
        for i, layer in enumerate(layers):
            out = layer(h, mask=ssm_mask if layer.is_linear else fa_mask, cache=None)
            per_layer[i] += one_minus_cos(h, out).item()
            h = out
            if (i + 1) % BLOCK == 0:
                per_block[i // BLOCK] += one_minus_cos(block_in, h).item()
                block_in = h
            mx.eval(h)
        n_tok += ids.shape[1]
    return [round(x / n_tok, 4) for x in per_layer], [round(x / n_tok, 4) for x in per_block]


def probe_layers(_: argparse.Namespace) -> None:
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.utils import load_config, save

    need_drive()
    set_limits()
    src = model_path("qwen3.5-4b")
    calib, evals = excerpts()
    model, tok = load(str(src))
    cal_b, eval_b = token_batches(tok, calib), token_batches(tok, evals)
    check_ids = eval_b[0]
    tm = text_model(model)
    original = list(tm.layers)
    assert [l.is_linear for l in original] == [(i + 1) % BLOCK != 0 for i in range(len(original))]

    t0 = time.time()
    per_layer, per_block = block_influence(model, cal_b)
    base = {
        "probe": "layers", "step": "unpruned", "model": "qwen3.5-4b", "revision": src.name,
        "layers": len(original), "params": n_params(model), "eval_nll": mean_nll(model, eval_b),
        "score_s": round(time.time() - t0, 1), "layer_influence": per_layer,
        "block_influence": per_block, **cache_check(model, check_ids),
        "sample": answer_sample(model, tok, evals[0]),
    }
    record(base)

    candidates = sorted(range(1, len(per_block) - 1), key=lambda b: per_block[b])
    for k in REMOVE_BLOCKS:
        drop = sorted(candidates[:k])
        kept = [l for i, l in enumerate(original) if i // BLOCK not in drop]
        tm.layers = kept
        row = {
            "probe": "layers", "step": f"minus{k}", "removed_blocks": drop, "layers": len(kept),
            "params": n_params(model), "eval_nll": mean_nll(model, eval_b),
            **cache_check(model, check_ids), "sample": answer_sample(model, tok, evals[0]),
        }
        # Save with stock mlx_lm and reload: the pattern is still DeltaNet x3 then attention.
        cfg = load_config(src)
        tc = cfg.get("text_config", cfg)
        tc["num_hidden_layers"] = len(kept)
        if "layer_types" in tc:
            tc["layer_types"] = [t for i, t in enumerate(tc["layer_types"]) if i // BLOCK not in drop]
        dst = PRUNED / f"qwen3.5-4b-minus{k}"
        shutil.rmtree(dst, ignore_errors=True)
        save(dst, src, model, tok, cfg, donate_model=False)
        reloaded, _ = load(str(dst))
        row.update(disk_gib=dir_gib(dst), reload_eval_nll=mean_nll(reloaded, eval_b),
                   reload_cache=cache_check(reloaded, check_ids))
        del reloaded
        gc.collect()
        mx.clear_cache()
        record(row)

    # Finer removal: drop one DeltaNet layer (index 1). The model's cached path finds its masks
    # through fixed indices (first DeltaNet layer, first attention layer = 3); after the removal
    # index 3 is a DeltaNet layer, so decoding with a cache must be checked both ways.
    tm.layers = [l for i, l in enumerate(original) if i != 1]
    row = {"probe": "layers", "step": "minus-one-deltanet", "layers": len(tm.layers)}
    try:
        row["cache_stock_indices"] = cache_check(model, check_ids)
    except Exception as err:
        row["cache_stock_indices"] = f"failed: {type(err).__name__}: {str(err)[:160]}"
    tm.fa_idx = next(i for i, l in enumerate(tm.layers) if not l.is_linear)
    tm.ssm_idx = next(i for i, l in enumerate(tm.layers) if l.is_linear)
    row["cache_patched_indices"] = cache_check(model, check_ids)
    row["note"] = ("stock config cannot express this pattern (is_linear comes from the layer index); "
                   "saving it would need a loader that reads layer_types")
    record(row)
    record({"probe": "layers", "step": "peak", "peak_gib": round(mx.get_peak_memory() / GIB, 2)})


# ---------------------------------------------------------------- S1-a.5 experts

MOE = {"keep": None, "stats": None}


def moe_call(self, x):
    """OlmoeSparseMoeBlock.__call__ with an optional expert mask and statistics."""
    import mlx.core as mx

    B, L, D = x.shape
    x_flat = x.reshape(-1, D)
    logits = self.gate(x_flat)
    if MOE["keep"] is not None:
        logits = mx.where(MOE["keep"][self.layer_idx], logits, -mx.inf)
    weights = mx.softmax(logits, axis=1, precise=True)
    k = self.top_k
    idx = mx.stop_gradient(mx.argpartition(-weights, kth=k - 1, axis=-1)[..., :k])
    scores = mx.take_along_axis(weights, idx, axis=-1)
    if self.norm_topk_prob:
        scores = scores / scores.sum(axis=-1, keepdims=True)
    y = self.switch_mlp(x_flat, idx)
    if MOE["stats"] is not None:
        E = weights.shape[-1]
        hot = (idx[..., None] == mx.arange(E)).astype(mx.float32)
        norms = mx.linalg.norm(y.astype(mx.float32), axis=-1)
        st = MOE["stats"][self.layer_idx]
        st["count"] = st["count"] + hot.sum((0, 1))
        st["reap"] = st["reap"] + (hot * (scores.astype(mx.float32) * norms)[..., None]).sum((0, 1))
        mx.eval(st["count"], st["reap"])
    y = (y * scores[..., None]).sum(axis=-2)
    return y.reshape(B, L, D)


def load_olmoe():
    from mlx_lm import load
    from mlx_lm.models import olmoe

    olmoe.OlmoeSparseMoeBlock.__call__ = moe_call
    model, tok = load(str(model_path("olmoe-1b-7b")))
    for i, layer in enumerate(model.model.layers):
        layer.mlp.layer_idx = i
    return model, tok


def keep_mask(rank: list[list[int]], n_keep: int, n_exp: int):
    import mlx.core as mx

    rows = []
    for order in rank:
        kept = set(order[:n_keep])
        rows.append([e in kept for e in range(n_exp)])
    return mx.array(rows)


def slice_experts(model, keep_rows) -> None:
    import mlx.core as mx

    for i, layer in enumerate(model.model.layers):
        idx = mx.array([e for e, k in enumerate(keep_rows[i]) if k], dtype=mx.int32)
        block = layer.mlp
        mods = [block.gate, block.switch_mlp.gate_proj, block.switch_mlp.up_proj,
                block.switch_mlp.down_proj]
        for m in mods:
            for name in ("weight", "scales", "biases", "bias"):
                v = getattr(m, name, None) if name in m else None
                if v is not None:
                    setattr(m, name, v[idx])
        block.num_experts = int(idx.shape[0])
    mx.eval(model.parameters())


def probe_experts(_: argparse.Namespace) -> None:
    import mlx.core as mx
    import numpy as np
    from mlx_lm import load
    from mlx_lm.utils import load_config, save

    need_drive()
    set_limits()
    src = model_path("olmoe-1b-7b")
    calib, evals = excerpts()
    model, tok = load_olmoe()
    cal_b, eval_b = token_batches(tok, calib), token_batches(tok, evals)
    check_b = eval_b[:N_CHECK]
    n_layers, n_exp = len(model.model.layers), model.args.num_experts
    gc.collect()
    mx.clear_cache()
    resident = round(mx.get_active_memory() / GIB, 2)

    MOE["stats"] = [{"count": mx.zeros(n_exp), "reap": mx.zeros(n_exp)} for _ in range(n_layers)]
    t0 = time.time()
    for ids in cal_b:
        mx.eval(model(ids))
    score_s = round(time.time() - t0, 1)
    count = [np.array(s["count"]) for s in MOE["stats"]]
    reap = [np.array(s["reap"]) / np.maximum(c, 1) for s, c in zip(MOE["stats"], count)]
    MOE["stats"] = None
    rank = {
        "reap": [list(np.argsort(-r, kind="stable")) for r in reap],
        "frequency": [list(np.argsort(-c, kind="stable")) for c in count],
        "random": [random.Random(SEED + i).sample(range(n_exp), n_exp) for i in range(n_layers)],
    }
    never = [int((c == 0).sum()) for c in count]
    record({
        "probe": "experts", "step": "unpruned", "model": "olmoe-1b-7b", "revision": src.name,
        "experts": n_exp, "params": n_params(model), "resident_gib": resident,
        "eval_nll": mean_nll(model, eval_b), "score_s": score_s, "never_routed_per_layer": never,
        **cache_check(model, check_b[0]), "sample": answer_sample(model, tok, evals[0]),
    })

    losses = {}
    for ratio in EXPERT_RATIOS:
        n_keep = int(n_exp * (1 - ratio))
        for crit, order in rank.items():
            MOE["keep"] = keep_mask(order, n_keep, n_exp)
            losses[f"{crit}-{int(ratio * 100)}"] = mean_nll(model, eval_b)
    MOE["keep"] = None
    record({"probe": "experts", "step": "masked-losses", "eval_nll": losses})

    # Slice the top half by REAP and check it against the masked unpruned model.
    n_keep = n_exp // 2
    mask = keep_mask(rank["reap"], n_keep, n_exp)
    MOE["keep"] = mask
    ref = [model(ids).astype(mx.float32) for ids in check_b]
    # The same check on one layer: the first MoE block on the real hidden states of one excerpt.
    # Over the whole model, half-precision rounding is amplified layer by layer, so the
    # full-model comparison alone cannot tell a slicing error from rounding.
    blk = model.model.layers[0]
    h = model.model.embed_tokens(check_b[0])
    x0 = blk.post_attention_layernorm(h + blk.self_attn(blk.input_layernorm(h), "causal", None))
    layer_ref = blk.mlp(x0).astype(mx.float32)
    mx.eval(ref, x0, layer_ref)
    MOE["keep"] = None
    keep_rows = np.array(mask).tolist()
    slice_experts(model, keep_rows)
    model.args.num_experts = n_keep
    gc.collect()
    mx.clear_cache()
    layer_diff = mx.abs(blk.mlp(x0).astype(mx.float32) - layer_ref).max()
    layer_check = {"activation_dtype": str(x0.dtype), "max_abs_diff": layer_diff.item(),
                   "relative": (layer_diff / mx.abs(layer_ref).max()).item()}

    def compare(m) -> dict:
        worst, agree, total = 0.0, 0, 0
        for ids, r in zip(check_b, ref):
            out = m(ids).astype(mx.float32)
            mx.eval(out)
            worst = max(worst, mx.abs(out - r).max().item())
            agree += (mx.argmax(out, -1) == mx.argmax(r, -1)).sum().item()
            total += ids.shape[1]
        return {"max_abs_logit_diff": round(worst, 4), "argmax_agree": f"{agree}/{total}"}

    row = {"probe": "experts", "step": "sliced-reap-50", "experts": n_keep, "params": n_params(model),
           "resident_gib": round(mx.get_active_memory() / GIB, 2), "layer0_vs_masked": layer_check,
           "vs_masked": compare(model),
           "eval_nll": mean_nll(model, eval_b), **cache_check(model, check_b[0]),
           "sample": answer_sample(model, tok, evals[0])}
    cfg = load_config(src)
    cfg["num_experts"] = n_keep
    dst = PRUNED / "olmoe-reap-50"
    shutil.rmtree(dst, ignore_errors=True)
    save(dst, src, model, tok, cfg, donate_model=False)
    reloaded, _ = load(str(dst))
    for i, layer in enumerate(reloaded.model.layers):
        layer.mlp.layer_idx = i
    row.update(disk_gib=dir_gib(dst), disk_gib_unpruned=dir_gib(src), reload_vs_masked=compare(reloaded))
    record(row)
    shutil.rmtree(dst, ignore_errors=True)
    record({"probe": "experts", "step": "peak", "peak_gib": round(mx.get_peak_memory() / GIB, 2)})


# ---------------------------------------------------------------- S1-a.3 train


class OverBudget(RuntimeError):
    pass


def np_seed(seed: int) -> None:
    import numpy as np

    np.random.seed(seed)


def probe_train(args: argparse.Namespace) -> None:
    from mlx_lm import lora
    from mlx_lm.tuner.callbacks import TrainingCallback
    from transformers import AutoTokenizer

    need_drive()
    mx = set_limits()
    key, kind, n_layers, seq = args.model, args.kind, args.layers, args.seq
    path = model_path(key)

    # Text: training-side excerpts joined and cut into chunks of exactly the sequence length.
    tok = AutoTokenizer.from_pretrained(str(path))
    calib, evals = excerpts()
    ids = tok.encode("\n\n".join(it["excerpt"] for it in calib + evals), add_special_tokens=False)
    data = OUT / "train_data" / f"{key}-{seq}"
    data.mkdir(parents=True, exist_ok=True)
    width, n_train = seq - 4, TRAIN_ITERS + 2
    chunks = [tok.decode(ids[(i * width) % (len(ids) - width):][:width]) for i in range(n_train + 2)]
    for name, rows in (("train", chunks[:n_train]), ("valid", chunks[n_train:])):
        with open(data / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for text in rows:
                fh.write(json.dumps({"text": text}) + "\n")

    reports: list[dict] = []

    class Watch(TrainingCallback):
        def on_train_loss_report(self, info: dict) -> None:
            reports.append({"iteration": info.get("iteration"), "it_per_s": info.get("iterations_per_second"),
                            "train_loss": info.get("train_loss")})
            if mx.get_peak_memory() > ABORT_GIB * GIB:
                raise OverBudget(f"peak passed {ABORT_GIB} GiB by iteration {info.get('iteration')}")

    adapters = OUT / "adapters" / f"{key}-{kind}-{seq}"
    cfg = dict(lora.CONFIG_DEFAULTS)
    cfg.update(model=str(path), train=True, data=str(data), fine_tune_type=kind, batch_size=1,
               iters=TRAIN_ITERS, max_seq_length=seq, grad_checkpoint=True, num_layers=n_layers,
               adapter_path=str(adapters), steps_per_report=1, steps_per_eval=10**9, val_batches=1,
               save_every=10**9, seed=SEED)
    status, t0 = "ok", time.time()
    try:
        # Not lora.run: in mlx_lm 0.32.2 it replaces the callback it is given with the reporting
        # callbacks of `report_to` (None here), so the watch and its abort check never ran. That
        # was also the cause of EXP-0000's missing per-step speeds.
        ns = types.SimpleNamespace(**cfg)
        np_seed(ns.seed)
        model, tokenizer = lora.load(ns.model)
        train_set, valid_set, _ = lora.load_dataset(ns, tokenizer)
        lora.train_model(ns, model, train_set, valid_set, Watch())
    except OverBudget as err:
        status = f"aborted: {err}"
    except Exception as err:
        status = f"failed: {type(err).__name__}: {str(err)[:200]}"
    shutil.rmtree(adapters, ignore_errors=True)
    peak = mx.get_peak_memory() / GIB
    if status == "ok" and peak > BUDGET_GIB:
        status = "over budget"
    steady = [r["it_per_s"] for r in reports[1:] if r["it_per_s"]]
    record({"probe": "train", "model": key, "revision": path.name, "kind": kind, "layers": n_layers,
            "size": seq, "status": status, "iters_done": reports[-1]["iteration"] if reports else 0,
            "s_per_step": round(1 / (sum(steady) / len(steady)), 2) if steady else None,
            "peak_gib": round(peak, 2), "last_loss": reports[-1]["train_loss"] if reports else None,
            "wall_s": round(time.time() - t0, 1),
            "settings": f"{kind}, rank 8 if LoRA, {n_layers} layers, batch 1, grad checkpoint, embeddings frozen"})


def probe_fit(_: argparse.Namespace) -> None:
    """CPU only: how many training items leave room for an answer inside the 512 tokens that
    Qwen3.5 training fits, with the prompt as S1 asks it (thinking off)."""
    import numpy as np
    from transformers import AutoTokenizer

    need_drive()
    tok = AutoTokenizer.from_pretrained(str(model_path("qwen3.5-0.8b")))
    n = []
    with open(ITEMS, encoding="utf-8") as fh:
        for line in fh:
            it = json.loads(line)
            msg = [{"role": "user", "content": f"{it['excerpt']}\n\n{it['question']} "
                    "Put the final number in \\boxed{}."}]
            text = tok.apply_chat_template(msg, add_generation_prompt=True, tokenize=False,
                                           enable_thinking=False)
            n.append(len(tok.encode(text, add_special_tokens=False)))
    n = np.array(n)
    record({"probe": "fit", "items": int(len(n)), "prompt_median": int(np.median(n)),
            "prompt_p90": int(np.percentile(n, 90)), "prompt_max": int(n.max()),
            "share_fitting_512": {b: round(float((n + b <= 512).mean()), 3) for b in (32, 64, 96, 128)}})


# ---------------------------------------------------------------- queue and report


def load_results() -> list[dict]:
    if not RESULTS.exists():
        return []
    return [json.loads(line) for line in RESULTS.read_text().splitlines() if line.strip()]


def run_child(*argv: str) -> None:
    subprocess.run([sys.executable, __file__, *argv], check=False)


def queue(args: argparse.Namespace) -> None:
    need_drive()
    done = load_results()
    if not any(r["probe"] == "layers" and r.get("step") == "peak" for r in done):
        run_child("layers")
    if not any(r["probe"] == "experts" and r.get("step") == "peak" for r in done):
        run_child("experts")
    for key, kind, n_layers, seqs in TRAIN_SERIES:
        for seq in seqs:
            prior = [r for r in load_results() if r["probe"] == "train" and r["model"] == key
                     and r["kind"] == kind]
            if any(r["size"] == seq for r in prior):
                continue
            if any(r["status"] != "ok" for r in prior):
                record({"probe": "train", "model": key, "kind": kind, "layers": n_layers, "size": seq,
                        "status": "skipped: a shorter sequence failed or went over budget"})
                continue
            ok = sorted((r for r in prior if r["status"] == "ok"), key=lambda r: r["size"])
            if len(ok) >= 2:  # straight line through the last two peaks, as in EXP-0000
                a, b = ok[-2], ok[-1]
                guess = b["peak_gib"] + (b["peak_gib"] - a["peak_gib"]) / (b["size"] - a["size"]) * (seq - b["size"])
                if guess > ABORT_GIB:
                    record({"probe": "train", "model": key, "kind": kind, "layers": n_layers, "size": seq,
                            "status": f"skipped: predicted peak {guess:.1f} GiB"})
                    continue
            run_child("train", "--model", key, "--kind", kind, "--layers", str(n_layers), "--seq", str(seq))
    if not args.keep:
        shutil.rmtree(PRUNED, ignore_errors=True)
        shutil.rmtree(OUT / "train_data", ignore_errors=True)


def report(_: argparse.Namespace) -> None:
    rows = load_results()
    for r in rows:
        if r["probe"] in ("layers", "experts", "fit"):
            print(json.dumps({k: v for k, v in r.items() if k not in ("when", "layer_influence")}))
    print("\n| model | kind | layers | seq | s/step | peak GiB | status |\n|---|---|---|---|---|---|---|")
    for r in rows:
        if r["probe"] == "train":
            print(f"| {r['model']} | {r['kind']} | {r['layers']} | {r['size']} | {r.get('s_per_step', '')} "
                  f"| {r.get('peak_gib', '')} | {r['status']} |")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("layers").set_defaults(fn=probe_layers)
    sub.add_parser("experts").set_defaults(fn=probe_experts)
    sub.add_parser("fit").set_defaults(fn=probe_fit)
    t = sub.add_parser("train")
    t.add_argument("--model", required=True)
    t.add_argument("--kind", choices=("lora", "full"), required=True)
    t.add_argument("--layers", type=int, required=True)
    t.add_argument("--seq", type=int, required=True)
    t.set_defaults(fn=probe_train)
    q = sub.add_parser("queue")
    q.add_argument("--keep", action="store_true", help="keep the pruned checkpoints")
    q.set_defaults(fn=queue)
    sub.add_parser("report").set_defaults(fn=report)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
