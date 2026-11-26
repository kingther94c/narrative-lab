# Retaining by Doing: The Role of On-Policy Data in Mitigating Forgetting

- **Citation:** Chen, H., Razin, N., Narasimhan, K. and Chen, D. (2026). ICML 2026, PMLR 306.
  arXiv 2510.18874. Version read: v2 (December 2025), HTML, main text and Appendix A. Earlier
  version: v1 October 2025.
- **Link:** https://arxiv.org/abs/2510.18874 (HTML: https://arxiv.org/html/2510.18874v2;
  proceedings: https://proceedings.mlr.press/v306/chen26do.html)
- **Stream:** 14b (distillation and training methods for small students)
- **Verified against source:** yes, 2026-11-25, against the v2 HTML, read through an automated page
  reader in two passes; venue from the PMLR listing found by search. Table values as returned; not
  re-keyed from the PDF. Figure-only values not used.

## Question

Why does RL fine-tuning forget prior abilities less than SFT, and which ingredient matters: on-policy
data, the KL penalty, or advantage estimation?

## Data

Target tasks: IFEval (13,000 training prompts), MMLU (12,000), Countdown (10,000). Non-target tasks
for forgetting: MATH, WildJailbreak, WildGuardTest and the other two targets. No financial text.

## Method

- Models: Llama-3.2-1B-Instruct, Llama-3.1-8B-Instruct, Qwen-2.5-1.5B-Instruct,
  Qwen-2.5-7B-Instruct.
- **SFT:** responses from Llama-3.3-70B-Instruct, filtered for correctness (an off-policy, larger
  teacher, as in S1's D3).
- **Self-SFT:** five samples per prompt from the initial model, correct ones kept (as in S1's D2).
- **GRPO:** five rollouts per prompt, KL coefficient 0.05 (0 in an ablation); **REINFORCE** without
  an advantage estimator.
- **Iterative-SFT:** regenerate self data from the current model at the start of each epoch
  ("approximately on-policy").
- Learning rate 1e-4 for the 1B and 1.5B, 5e-6 for the 7B and 8B; two epochs; AdamW, cosine.
- Gain = target-task accuracy increase; drop = mean decrease on non-target tasks.

## Outcome variable and horizon

Target gain and average non-target drop, in accuracy points; KL from the initial policy. No horizon.

## Result

Table 2, drop on non-target tasks (KL from the initial policy), small models:

| Model | Method | IFEval | MMLU | Countdown |
|---|---|---|---|---|
| Llama 1B | SFT (70B teacher) | 26.2 (61.1) | 28.9 (48.4) | 24.2 (1,254.7) |
| Llama 1B | Self-SFT | 6.9 (52.4) | 34.6 (39.3) | 25.3 (796.7) |
| Llama 1B | GRPO | 1.6 (2.6) | 0.3 (4.1) | −0.6 (70.6) |
| Qwen 1.5B | SFT (70B teacher) | 6.2 (47.8) | 11.9 (9.2) | 29.5 (846.6) |
| Qwen 1.5B | Self-SFT | 3.0 (25.0) | 14.0 (3.0) | 19.5 (896.1) |
| Qwen 1.5B | GRPO | 0.6 (1.5) | 0.5 (0.4) | 0.9 (34.9) |

Table 1, gain / drop, 7B and 8B:

| Model | Method | IFEval | MMLU | Countdown |
|---|---|---|---|---|
| Llama 8B | SFT | 25.2 / 27.8 | 11.1 / 38.5 | 25.5 / 36.4 |
| Llama 8B | GRPO | 18.4 / 3.4 | 14.6 / −0.2 | 60.4 / −0.5 |
| Qwen 7B | SFT | 24.2 / 5.6 | 9.4 / 14.6 | 10.4 / 29.2 |
| Qwen 7B | GRPO | 17.0 / 0.2 | 8.4 / 0.2 | 29.2 / −0.3 |

- Empirical finding: SFT forgets more than GRPO in every cell of both tables. Target gain is not
  uniformly lower for GRPO: higher on Countdown (60.4 against 25.5 at Llama 8B), similar on MMLU,
  lower on IFEval (18.4 against 25.2 at Llama 8B).
- Empirical finding: Self-SFT, which uses the model's own correct samples generated once at the
  start, still forgets heavily (up to 34.6 points at 1B); "generating data only from the initial
  policy is not enough".
- Empirical finding: REINFORCE forgets about as little as GRPO, and removing the KL penalty changes
  little, so on-policy sampling, not the KL term or the advantage estimator, carries the effect.
- Empirical finding: Iterative-SFT reaches target accuracy comparable to SFT with "mild to no"
  forgetting (numbers in a figure only, not used). SFT on GRPO's traces trails RL slightly on gain and
  forgets slightly more.
- KL to the initial policy correlates with forgetting at Pearson 0.52, not monotonically for SFT
  against Self-SFT.
- Theory (toy mixtures of Gaussians): RL is mode-seeking and keeps old modes when the initial policy
  is multi-modal; if the initial policy is uni-modal, SFT can forget less.

## Look-ahead and memorisation

Not relevant; contamination not discussed.

## What it settles for us

- The closest forgetting evidence at S1's scale (1B and 1.5B). Off-policy SFT on a larger teacher's
  answers, which is S1's D3, cost 6 to 30 points of non-target accuracy; on-policy training cost under
  2. This matches S1's section A drop (FinQA 38 to 10).
- S1's D2 ("self", generated once) is not the fix: Self-SFT forgot about as much as teacher SFT.
- The useful version for one MLX machine is approximately on-policy: regenerate training data from the
  current student at the start of each round. It needs no student and teacher resident together, so it
  fits 12 GiB by alternating jobs.
- Supports making any S1 training arm report a fixed non-target panel (section A) and the student's
  KL to its starting checkpoint, both measurable without extra data.

## Limits

1B to 8B; three target tasks; RL forgets less partly because it gains less on some tasks; Iterative-
SFT numbers only in figures; no distillation (teacher-logit) arm; one seed reported per cell in the
tables read.
