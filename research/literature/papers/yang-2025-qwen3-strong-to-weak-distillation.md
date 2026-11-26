# Qwen3 Technical Report (Section 4.5, strong-to-weak distillation)

- **Citation:** Yang, A., Li, A., Yang, B., Zhang, B., Hui, B. and 55 others (Qwen Team) (2025).
  Qwen3 Technical Report. arXiv 2505.09388. Version read: v1 (14 May 2025), HTML, Section 4.5 and
  Table 21, plus the small-model rows of the post-training evaluation tables. No venue listed.
- **Link:** https://arxiv.org/abs/2505.09388 (HTML: https://arxiv.org/html/2505.09388v1)
- **Stream:** 14b (distillation and training methods for small students)
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v1 HTML (first
  100,000 of 134,001 characters, which contain Section 4.5 and Table 21), read through an automated
  page reader in two passes. Table values as returned; not re-keyed from the PDF.

## Question

How does the Qwen team build its small models (0.6B to 14B, and 30B-A3B), and is distillation from a
large teacher better than reinforcement learning for them?

## Data

Not stated for the distillation stage beyond "math and code queries" for the Table 21 comparison.
Evaluation: AIME'24, AIME'25, MATH500, LiveCodeBench v5, MMLU-Redux, GPQA-Diamond.

## Method

- Flagship models get a four-stage pipeline (long chain-of-thought cold start, reasoning RL,
  thinking-mode fusion, general RL). Small models do not; they get two distillation phases.
- **Off-policy distillation:** the student is fine-tuned on teacher responses generated in both
  `/think` and `/no_think` modes, which gives it basic reasoning and the mode switch.
- **On-policy distillation:** the student samples its own responses in either mode; it is then
  fine-tuned by "aligning its logits with those of a teacher model (Qwen3-32B or Qwen3-235B-A22B) to
  minimize the KL divergence". The KL direction is not stated in the section read.
- Table 21 starts both arms from the same off-policy-distilled Qwen3-8B checkpoint.

## Outcome variable and horizon

Benchmark accuracy (pass@1, and pass@64 in brackets) and GPU hours. No horizon.

## Result

Table 21 (Qwen3-8B, same starting checkpoint):

| Arm | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-D | GPU hours |
|---|---|---|---|---|---|---|---|
| Off-policy distillation (start) | 55.0 (90.0) | 42.8 (83.3) | 92.4 | 42.0 | 86.4 | 55.6 | - |
| + reinforcement learning | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| + on-policy distillation | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

- Empirical finding: on-policy distillation beats RL on every column at about one tenth of the GPU
  hours. RL leaves pass@64 unchanged; distillation raises it (90.0 to 93.3, 83.3 to 86.7). The
  authors read this as the teacher's logits widening what the student can reach.
- Empirical finding (small models, post-training tables): Qwen3-1.7B thinking 48.3 AIME'24 and 93.4
  MATH-500 against 28.9 and 83.9 for DeepSeek-R1-Distill-Qwen-1.5B; Qwen3-1.7B non-thinking equals
  Qwen2.5-3B-Instruct on MMLU-Redux (64.4). Qwen3-0.6B thinking scores 10.7 on AIME'24 against 50.4
  for an 8B distilled model, so the small-beats-large claim does not hold everywhere.
- One run per arm; no seeds or intervals.

## Look-ahead and memorisation

Not addressed. No overlap check between distillation queries and the math benchmarks is described.

## What it settles for us

- Supports making on-policy logit distillation, not RL, the main lever for a same-family small
  student: it is the recipe the model family itself uses, it wins on accuracy and costs a tenth.
- Hypothesis (not verified; no Qwen3.5 report was found): Qwen3.5-0.8B was probably built the same
  way, so S1's 0.8B already sits at the end of an off-policy plus on-policy distillation pipeline from
  a much larger teacher. A domain stage would be a further round of the same method.
- The comparison is at 8B with a 32B or 235B teacher on math and code. It does not show the gain
  survives at 0.8B with a 4B teacher, on label answers, or outside math and code.
- Needs identical tokenizers, which S1 has (Qwen3.5-4B and 0.8B).

## Limits

Industrial report; one comparison table; no ablation of KL direction, teacher size, or rollout count;
GPU hours for a cluster, not translatable to one MLX machine except as a ratio.
