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
  `results.jsonl`. The figures above come from the run logs. Cause, found on 2026-11-16 in
  EXP-0006: `mlx_lm.lora.run` (0.32.2) replaces the callback it is given with the reporting
  callbacks of its `report_to` setting, which is empty. So the script's check that abandons a
  run past 15 GiB never ran either; only MLX's 12 GiB memory limit applied. Peaks were still
  measured after each run, so the table stands.
- The LoRA series go beyond what the plan listed (shorter lengths, a 4-layer series, two
  comparison models). The first trial's crash is the reason; the script's docstring records it.
- DianJin-R1-7B has no Hugging Face revision recorded, because the 4-bit copy was made locally.

## Still to do

3. Headroom pilot on 100 document pairs
4. Memorisation probe
5. Structured output, evidence quotes, tool calls
6. API budget for the commercial part

## 5. Sub-study S1: EarningsExam v0 yield (EXP-0005)

Script: `research/experiments/exp0005_earnings_exam.py`, run 2026-11-15 (plan:
`docs/plans/2026-11-15_substudy_s1_plan.md` §3). It reads the releases EXP-0003 fetched and SEC's
`companyfacts.zip` of 2026-11-14. An item is kept only when two sources agree: the XBRL value for
the period (first filed in a 10-Q or 10-K from 3 days before to 75 days after the release), and
the same figure in a release table row whose label names the metric, at the table's stated scale.
Gold is the figure as displayed. Tolerance is half a unit of its last displayed digit, 0.15
percentage points for percentages, and half a cent for EPS changes. Excerpts are capped at 400
Qwen3.5 tokens; contact lines (e-mail addresses, phone numbers) are removed.

| Side | Releases used | Releases with items | Items | Companies | Excerpt tokens, median / max |
|---|---|---|---|---|---|
| Train (pre-cutoff, training companies) | 1,118 | 951 | 4,420 | 951 | 365 / 400 |
| Development (development companies) | 1,101 | 930 | 4,392 | 355 | 366 / 400 |
| Test (post-cutoff, test companies) | 4,265 | 3,463 | 18,618 | 1,989 | 372 / 400 |

Why releases gave no items, on the test side: no verified figure 551, no XBRL period 188 (many of
them November releases whose 10-Q was not yet in the snapshot), no company facts 39, excerpt over
budget 24. About a quarter of B1 items (3,041 of 11,753 on the test side) ask for a different
scale from the table's, for example a table in thousands and an answer in millions. Templates are
held out for the test side: gross profit and the gross margin built on it, the net-margin item,
and the second phrasing. Items using any of them make up 10,309 of the 18,618 test items.

**Hand check.** Empirical finding: 30 items, 15 development and 15 training, drawn at random
(seeds 11 and 12), were checked against their excerpts by Claude. All 30 golds are right. That
covers each B1 metric on the train and development sides and each B2 item except the held-out
ones. Seen in the check: GAAP rows standing beside adjusted rows, "attributable" net income beside
total net income, a segment table whose consolidated figure is the last column, and an EPS of
0.00. Test items were not read (changelog, 2026-11-14). Two defects were found and fixed before
this run, on training and development items: excerpts running into the next table, and a
contact e-mail line picked up as a title.

**What it means.** The test pool is about twelve times the planned 1,500 items, so the test set
can be drawn stratified by section, template and filer size, at most a few items per company.
Training has about 4,400 items for arms of about 1,000. S1-b can start once its pre-registration
is written.

## 5a. EarningsExam v0.1 (EXP-0008)

Script: `research/experiments/exp0008_earnings_exam_v0_1.py`, run 2026-11-17. **Defect in v0.**
When an excerpt was over budget, v0 kept the first 8 raw lines of the table header, blank lines
included, and could drop the line naming each column's period. A smoke test for EXP-0007 met an
item with two unlabelled columns and the gold in the second (nCino, prior year shown first). A
rough count found no period label above the data in about 19% of v0 development items; for 0.7%
the gold was not in the first column, so the item could not be answered.

**Fix.** v0.1 imports v0 unchanged and replaces only the excerpt rule. It finds the nearest line
above the needed rows carrying a period label (a year, a quarter label such as 3Q26, or FY26) for
each of the row's first two columns, keeps it and up to two heading lines above it whatever else
is elided, and drops the item if there is none within 60 lines. Gold, tolerance, templates and
item ids are v0's.

| Side | v0 items | v0.1 items | v0.1 companies | Excerpt tokens, median / max |
|---|---|---|---|---|
| Train | 4,420 | 3,805 | 861 | 370 / 400 |
| Development | 4,392 | 3,896 | 331 | 371 / 400 |
| Test | 18,618 | 15,739 | 1,817 | not read |

Items dropped by the new rule: no column heading 800 (train and development) and 2,045 (test);
over budget once the heading is kept 693 and 4,009. Releases giving no item because every excerpt
was too long: 94 train, 359 test. On the test side 8,719 items use held-out templates and 2,672 B1
items need a scale conversion. Every v0.1 development item has a heading line (count only).

**Hand check.** Empirical finding: 16 development items (seed 41), 10 drawn from the 715 whose v0
excerpt had no heading and 6 at random, checked by Claude against their excerpts. All 16 golds are
right and every excerpt shows which column is which period, including prior-year-first tables,
quarter labels (3Q26, 2Q26, 3Q25) and multi-line headings. Seen again: "net income" beside "net
income attributable to common stockholders" (gold is the first, as XBRL's `NetIncomeLoss`), a
known ambiguity left as it is. Test items were not read.

**What it means.** v0.1 supersedes v0 for S1; v0 stays on the drive. The test pool, about ten
times the planned 1,500 items, is still ample. EXP-0007 was amended before its run to draw from
v0.1.

## 6. Sub-study S1: compression probes (EXP-0006)

Script: `research/experiments/exp0006_s1a_compression_probes.py`, run 2026-11-16 (plan §4, S1-a.3
to S1-a.5). mlx 0.32.4, mlx_lm 0.32.2. Calibration text is 64 training-side exam excerpts and
evaluation text another 32, one per release. The losses below are a check that pruning did
something sensible, not a comparison of methods: no healing, a tiny sample, and text the models
may have seen.

**Layer removal on Qwen3.5-4B (S1-a.4).** Empirical finding. Qwen3.5 repeats a block of three
Gated DeltaNet layers and one full-attention layer; stock mlx_lm decides each layer's kind from
its index, so a checkpoint loads only if whole blocks are removed. Blocks were scored by block
influence, 1 − cos(input, output), averaged over tokens; the first and last blocks were never
removed.

| Model | Layers | Parameters (mlx_lm count) | On disk | Evaluation loss (nats/token) | Sample answer |
|---|---|---|---|---|---|
| Unpruned | 32 | 4.21 B | 2.83 GiB (with vision tower) | 1.397 | Coherent |
| Blocks 3 and 6 removed | 24 | 3.31 B | 1.74 GiB | 2.277 | Coherent |
| Blocks 2, 3, 5 and 6 removed | 16 | 2.42 B | 1.27 GiB | 3.176 | Repeats a phrase |

Block influence by block: 0.94, 0.31, 0.25, 0.22, 0.34, 0.26, 0.23, 0.48. Scoring took 20 s.
Every pruned model saved and reloaded with stock mlx_lm and gave the same loss after reloading.
Cached decoding matched a full forward on the argmax at all 8 checked steps, with logit gaps
(0.19 to 0.22) no larger than the unpruned model's own (0.33). Removing a single DeltaNet layer
works in memory once the model's two cached mask indices are corrected; with the stock indices
cached decoding fails. Such a model cannot be written as a stock checkpoint. Peak 5.0 GiB.

So S1-d removes whole blocks, about 0.11 B parameters each, unless a loader that reads
`layer_types` is written. The stock 4B and 2B checkpoints carry a vision tower and the pruned
ones do not, so S1-d compares resident memory and text parameters, not file sizes. The 16-layer
model's degenerate sample shows why healing is part of the recipe.

**Expert removal on OLMoE-1B-7B (S1-a.5).** Empirical finding. On the calibration excerpts every
expert in every layer was routed to at least once. Slicing the router rows and the stacked expert
tensors (weights, scales, biases) to the top 32 experts per layer by REAP gives a stock checkpoint
of 1.94 GiB against 3.63 GiB, resident 2.45 GiB. Checked against the unpruned model with the
removed experts' router logits set to minus infinity, which is the same function: the first MoE
block's output is identical (difference 0), the evaluation loss is identical to four decimals
(3.0467), and over 2,711 tokens the next-token argmax agrees on 2,684 (99.0%). The rest is
half-precision rounding carried through 16 layers: a separate scratch check with a random mask
found the same experts chosen for all 352 tokens and a largest difference of 7.6e-6. The reloaded
checkpoint gives the same numbers. Peak 4.9 GiB.

Evaluation loss with experts masked; the unpruned model's is 2.335:

| Experts removed | REAP | Routing frequency | Random |
|---|---|---|---|
| 25% | 2.398 | 2.346 | 3.079 |
| 50% | 3.047 | 2.786 | 5.264 |

Both criteria beat random by far. Removing a quarter of the experts by routing frequency costs
almost nothing here (2.346 against 2.335), and frequency beats REAP at both ratios on this tiny,
unhealed check. S1-e compares them properly.

**Fine-tuning memory (S1-a.3).** Empirical finding. Batch 1, gradient checkpointing, 10 steps,
every example at full length; LoRA rank 8 on all layers; full fine-tuning trains every
transformer layer with the embeddings frozen.

| Model | Kind | 512 tokens: peak GiB, s/step | 1,024 tokens |
|---|---|---|---|
| Qwen3.5-0.8B | LoRA, 24 layers | 5.42, 6.17 | 14.80 GiB, 17.35 s/step: over budget |
| Qwen3.5-0.8B | Full | 7.17, 6.24 | 14.45 GiB, 16.98 s/step: over budget |
| 4B, 4 blocks removed (16 layers) | LoRA, 16 layers | 9.25, 7.18 | Metal out of memory at about 25 GiB |
| 4B, 2 blocks removed (24 layers) | LoRA, 24 layers | 9.78, 10.69 | Metal out of memory at about 25 GiB |

The 2,048 and 4,096 runs were skipped once 1,024 failed. The two crashes happened before the
first step reported, so the script's 15 GiB abort could not act; MLX's memory limit is not a hard
cap. The first attempt at this series found that `mlx_lm.lora.run` drops the callback it is given
(section 4); the script calls `train_model` directly.

**Room for an answer.** Empirical finding. With the prompt as S1 asks it (excerpt, question,
boxed-answer instruction, thinking off), training prompts run 439 tokens at the median, 469 at the
90th percentile and 491 at most. Share of the 4,420 training items that fit in 512 tokens with an
answer of 32 / 64 / 96 / 128 tokens: 98.1% / 58.3% / 40.9% / 31.7%.

**What it means.**

1. The operations S1-d and S1-e need work on this machine with stock mlx_lm: removing whole
   blocks, slicing experts, saving and reloading, and healing at 512 tokens.
2. Every Qwen3.5 rung trains at 512 tokens and no more. The 0.8B is no better than the 4B: on
   these layers memory follows sequence length and depth, not width. Full fine-tuning of the 0.8B
   fits at 512, so S1-c can use it.
3. The healing fits, so the plan's fallback (switching the ladder to Qwen3) is not triggered.
4. **The plan's rule 4 does not hold as written.** A 400-token excerpt leaves about 70 tokens for
   the answer. That is enough for a boxed answer (D1) but not for the worked answers of D2 and D3.
   Before S1-c is pre-registered the owner chooses: a shorter excerpt cap for training items
   (about 300 tokens would leave roughly 150; not yet measured), worked answers capped near 64
   tokens, or both.
   Test items can keep 400 tokens, since inference is not limited.
