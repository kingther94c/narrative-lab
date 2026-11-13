# Feasibility

Work package 3 of Phase 0; the plan is in [`../registry/01_roadmap.md`](../registry/01_roadmap.md).

**Status, 2026-11-13.** Probes 1 and 2 (long-prompt inference, LoRA) are done as EXP-0000. Probes
3 to 5 (headroom pilot, memorisation probe, structured output and tool calls) wait on sample
documents from the data audit.

## How the numbers were made

- Machine: Apple M6, 32 GB. Environment: conda `py313`, `mlx` 0.32.4, `mlx_lm` 0.32.2.
- Script: `research/experiments/exp0000_feasibility_probes.py`. Every configuration ran in its own
  process, one at a time, with `mx.set_memory_limit(12 GiB)`, `mx.set_cache_limit(1 GiB)` and
  512-token prefill chunks. 12 GiB is the owner's budget for one MLX process
  (`../learning_ai/docs/FINANCE_MODEL_SELECTION.md` §1).
- Reproduce everything with
  `conda run --no-capture-output -n py313 python research/experiments/exp0000_feasibility_probes.py queue`,
  then `... report`. One configuration:
  `... infer-one --model qwen3.5-9b --prompt-tokens 32000` or
  `... lora-one --model qwen3.5-4b --seq-len 512 --num-layers 16`.
- Raw rows and logs: `/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab/probes/exp0000/`
  (`results.jsonl`, `logs/`). Run on 2026-11-12 and 2026-11-13.
- Peak memory is `mx.get_peak_memory()`: active memory, not counting the allocator cache.
- Input text is the zsh manual already on the machine. Content does not matter for speed or
  memory.

Checkpoints, all 4-bit:

| Key | Repo | Revision |
|---|---|---|
| qwen3.5-4b | `mlx-community/Qwen3.5-4B-MLX-4bit` | `32f3e8ecf65426fc3306969496342d504bfa13f3` |
| qwen3.5-9b | `mlx-community/Qwen3.5-9B-MLX-4bit` | `938d8919941c6e7efd3c7150eff7fe9d12afa631` |
| gemma4-12b | `mlx-community/gemma-4-12B-it-4bit` | `73bcf09092aa277861d5a191b989b666f7f32e8f` |
| dianjin-r1-7b | `DianJin/DianJin-R1-7B`, quantised locally by `learning_ai` | local folder `DianJin--DianJin-R1-7B-4bit` |

## 1. Long-prompt inference

Empirical finding. One prompt, greedy decoding, up to 300 generated tokens.

| Model | Prompt tokens | Prefill tok/s | Decode tok/s | Peak GiB |
|---|---|---|---|---|
| Qwen3.5-4B | 4,001 | 1,915.7 | 54.0 | 3.09 |
| Qwen3.5-4B | 8,001 | 1,835.7 | 52.1 | 3.18 |
| Qwen3.5-4B | 16,001 | 1,659.8 | 47.7 | 3.75 |
| Qwen3.5-4B | 32,001 | 1,359.4 | 40.0 | 4.75 |
| Qwen3.5-9B | 4,001 | 1,133.9 | 31.3 | 5.48 |
| Qwen3.5-9B | 8,001 | 1,111.4 | 30.4 | 5.71 |
| Qwen3.5-9B | 16,001 | 1,043.0 | 28.8 | 6.25 |
| Qwen3.5-9B | 32,001 | 908.5 | 25.7 | 6.99 |

Stability: Qwen3.5-4B at 4,001 tokens was run twice, in separate processes. Prefill was 1,904.4
and 1,915.7 tok/s, 0.6% apart; peak memory was 3.09 GiB both times.

## 2. LoRA with `mlx_lm.lora`

Empirical finding. Rank 8, batch size 1, gradient checkpointing, 20 steps, every training example
at the full sequence length. Seconds per step are the sequence length divided by the median
tokens per second that `mlx_lm` printed for steps 3 to 20.

| Model | LoRA layers | Sequence length | Peak GiB | s/step | Within 12 GiB |
|---|---|---|---|---|---|
| Qwen3.5-4B | 16 | 128 | 3.76 | 1.42 | yes |
| Qwen3.5-4B | 16 | 256 | 5.15 | 3.07 | yes |
| Qwen3.5-4B | 16 | 512 | 10.20 | 7.82 | yes |
| Qwen3.5-4B | 16 | 1,024 | not run: predicted 20.3 | | no |
| Qwen3.5-4B | 4 | 128 | 3.72 | 0.76 | yes |
| Qwen3.5-4B | 4 | 256 | 5.07 | 1.56 | yes |
| Qwen3.5-4B | 4 | 512 | 10.10 | 3.53 | yes |
| Qwen3.5-4B | 4 | 1,024 | not run: predicted 20.2 | | no |
| Qwen3.5-9B | 16 | 128 | 6.27 | 1.53 | yes |
| Qwen3.5-9B | 16 | 256 | 7.68 | 3.32 | yes |
| Qwen3.5-9B | 16 | 512 | 12.68 | 8.61 | no |
| Qwen3.5-9B | 4 | 128 | 6.19 | 0.86 | yes |
| Qwen3.5-9B | 4 | 256 | 7.56 | 1.74 | yes |
| Qwen3.5-9B | 4 | 512 | 12.55 | 3.97 | no |
| Gemma 4 12B | 16 | 128 | 6.92 | 0.50 | yes |
| Gemma 4 12B | 16 | 256 | 7.32 | 0.86 | yes |
| Gemma 4 12B | 16 | 512 | 7.91 | 1.82 | yes |
| Gemma 4 12B | 16 | 1,024 | 8.86 | 3.77 | yes |
| Gemma 4 12B | 16 | 2,048 | 11.13 | 8.10 | yes |
| Gemma 4 12B | 16 | 4,096 | not run: predicted 15.7 | | no |
| DianJin-R1-7B | 16 | 128 | 4.60 | 0.34 | yes |
| DianJin-R1-7B | 16 | 256 | 4.81 | 0.66 | yes |
| DianJin-R1-7B | 16 | 512 | 5.13 | 1.37 | yes |
| DianJin-R1-7B | 16 | 1,024 | 5.78 | 2.85 | yes |
| DianJin-R1-7B | 16 | 2,048 | 6.54 | 5.79 | yes |
| DianJin-R1-7B | 16 | 4,096 | 8.64 | 11.76 | yes |
| DianJin-R1-7B | 16 | 8,192 | 12.57 | 26.33 | no |

Trainable parameters at 16 layers: 8.1M on Qwen3.5-4B, 10.8M on Qwen3.5-9B, 10.9M on Gemma 4 12B,
11.5M on DianJin-R1-7B.

One trial outside the queue: Qwen3.5-4B at 1,024 tokens with 16 layers died on its first training
step with `[METAL] Command buffer execution failed: Insufficient Memory`
(`... lora-one --model qwen3.5-4b --seq-len 1024`, 2026-11-12). The machine recovered at once.

Why Qwen3.5 is different (verified by reading
`mlx_lm/models/gated_delta.py`): 24 of the 4B's 32 layers are Gated DeltaNet layers. For inference
`mlx_lm` runs them through a Metal kernel. Training cannot differentiate through that kernel and
uses `gated_delta_ops`, a loop over tokens in which each step produces a new
`[32 heads, 128, 128]` float32 state, 2 MiB, that the backward pass needs. Memory therefore grows
with sequence length in a way ordinary attention does not at these lengths.

## 3. What follows

**Whole documents can be fed for inference.** A 32k-token prompt peaks at 4.75 GiB on the 4B and
6.99 GiB on the 9B. Prefill slows by 29% on the 4B and 20% on the 9B between 4k and 32k tokens;
a 32k document takes about 24 s to read on the 4B and 35 s on the 9B. The default of working on
outlook passages is a choice about fairness and label quality, not something inference forces.

**Qwen3.5 can be LoRA-tuned only on short sequences on this machine.** Within the 12 GiB budget
the 4B reaches 512 tokens and the 9B reaches 256. Training only 4 layers halves the time per step
and leaves the peak unchanged, so fewer layers does not buy longer sequences.

**Models with ordinary attention fine-tune at passage length.** DianJin-R1-7B, a Qwen2.5 base,
reaches 4,096 tokens at 8.64 GiB. Gemma 4 12B reaches 2,048 tokens at 11.13 GiB.

**The design default "full factorial on Qwen3.5-4B and 9B" does not survive as written.** The
fine-tuning factor needs one of these, and the choice belongs in the research design:

1. Run the factorial on a base with ordinary attention. On disk that means Gemma 4 12B, which is
   above the proposal's 4B to 9B range. A general-purpose 7B to 8B model with ordinary attention
   would need a download, which needs the owner's say-so. DianJin-R1-7B is already domain-trained
   and stays a reference, not a base.
2. Keep Qwen3.5 and cap training items at 512 tokens on the 4B, which rules out the 9B and
   constrains how benchmark items are built.
3. Raise the memory budget. This is the owner's decision. At 1,024 tokens the 4B is predicted to
   need about 20 GiB, close to the roughly 25 GiB at which Metal kills the process.
4. Wait for a differentiable kernel in `mlx_lm`. Hypothesis: none is known to be planned.

**Compute budget, estimated.** Assumptions: a 1,500-token prompt and 200 generated tokens per
item, one stream, speeds from section 1.

| Job | Qwen3.5-4B | Qwen3.5-9B |
|---|---|---|
| One item | 1,500 / 1,916 + 200 / 54 ≈ 4.5 s | 1,500 / 1,134 + 200 / 31.3 ≈ 7.7 s |
| 20,000 items (24 cells × about 800 test pairs) | about 25 hours | about 43 hours |

`learning_ai` measured batched decoding at 127 to 144 tok/s on the 4B and 86.6 tok/s on the 9B
(not re-measured here), which would bring these to roughly 10 and 17 hours.

Training time for 6,000 steps (2,000 pairs for three epochs) at the lengths that fit: about 9.7
hours on a DianJin-class 7B at 2,048 tokens, 13.5 hours on Gemma 4 12B at 2,048 tokens, and 13
hours on Qwen3.5-4B at 512 tokens with 16 layers.

## 4. Known defects of this run

- The script's training callback captured no per-step speeds, so `s_per_step` is empty in
  `results.jsonl`. The figures above come from the run logs.
- The LoRA series go beyond what the plan listed (shorter lengths, a 4-layer series, two
  comparison models). The first trial's crash is the reason; the script's docstring records it.
- DianJin-R1-7B has no Hugging Face revision recorded, because the 4-bit copy was made locally.

## Still to do

3. Headroom pilot on 100 document pairs
4. Memorisation probe
5. Structured output, evidence quotes, tool calls
6. API budget for the commercial part
