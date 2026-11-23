# Fin-R1: A Large Language Model for Financial Reasoning through Reinforcement Learning

- **Citation:** Liu, Z., Guo, X., Yang, Z., Lou, F., Zeng, L., Niu, J., Li, M., Qi, Q., Liu, Z.,
  Han, Y., Cheng, D., Chen, R., Wang, H., Feng, X., Wang, H. J., Shi, C. and Zhang, L. (2025).
  arXiv 2503.16252. Version read: v3 (18 December 2025), HTML, main text and appendix. Versions:
  v1 20 March 2025 to v5 19 March 2026; v4 and v5 not read. No venue listed.
- **Link:** https://arxiv.org/abs/2503.16252 (HTML: https://arxiv.org/html/2503.16252v3)
- **Stream:** 13a
- **Verified against source:** yes, 2026-11-23, against the abstract page and the v3 HTML (two
  passes through an automated page reader). Table values as returned; not re-keyed from the PDF.

## Question

Can a 7B model trained by distillation from DeepSeek-R1 and then GRPO reach the financial reasoning
level of much larger models?

## Data

- Fin-R1-Data: 60,091 Chinese and English items. About half basic business knowledge, a quarter
  advanced business knowledge, plus professional knowledge and financial code. Sources include
  FinQA (8.28K reduced to 2.95K), ConvFinQA (14.12K to 7.63K), Finance-Instruct-500K, FinanceIQ,
  Ant-Finance and a closed set built from a Chinese university's finance postgraduate entrance exam.
- DeepSeek-R1 (671B) writes reasoning and answers; Qwen2.5-72B-Instruct filters them (exact match
  for objective answers, LLM judgement for subjective ones; reasoning scored on seven criteria).
- No period or universe; no licence terms stated for the data (access marked open or closed).

## Method

Qwen2.5-7B-Instruct. SFT on the distilled traces, then GRPO with a binary format reward and a binary
accuracy reward judged by Qwen2.5-Max. Evaluation on FinQA, ConvFinQA, Ant_Finance, TFNS (sentiment
classification) and a 10% split of Finance-Instruct-500K, up to 1,000 random questions each, graded
by an LLM judge following JudgeLM (judge for evaluation not named).

## Outcome variable and horizon

Judge-scored accuracy on a 100-point scale. No horizon.

## Result

Table 1 (FinQA, ConvFinQA, Ant_Finance, TFNS, Finance-Instruct-500K, average):

| Model | Size | FinQA | ConvFinQA | Ant | TFNS | FI-500K | Avg |
|---|---|---|---|---|---|---|---|
| DeepSeek-R1 | 671B | 71.0 | 82.0 | 90.0 | 78.0 | 70.0 | 78.2 |
| Qwen2.5-32B-Instruct | 32B | 72.0 | 78.0 | 84.0 | 77.0 | 58.0 | 73.8 |
| R1-Distill-Qwen-32B | 32B | 70.0 | 72.0 | 87.0 | 79.0 | 54.0 | 72.4 |
| Qwen2.5-7B-Instruct | 7B | 60.0 | 66.0 | 85.0 | 68.0 | 49.0 | 65.6 |
| R1-Distill-Qwen-7B | 7B | 55.0 | 62.0 | 71.0 | 60.0 | 42.0 | 58.0 |
| Fin-R1 | 7B | 76.0 | 85.0 | 81.0 | 71.0 | 62.9 | 75.2 |

- Empirical finding: Fin-R1 tops FinQA and ConvFinQA, the two sets whose training splits fed its
  data, and trails DeepSeek-R1 by 7 to 9 points on the other three. It is below its own base on
  Ant_Finance (81 against 85).
- Empirical finding: DeepSeek's general reasoning distillation into 7B and 14B Qwen models scores
  below the plain instruct models at the same size (58.0 against 65.6; 66.2 against 71.4).
- Ablation (Table 2): base 65.6; GRPO only 67.8 (outputs sometimes incoherent); SFT only 71.9;
  SFT then GRPO 75.2.
- No intervals, seeds or tests; up to 1,000 items per set gives about ±3 points per cell.

## Look-ahead and memorisation

Not addressed. FinQA and ConvFinQA appear in both training sources and evaluation; the paper does
not say which split was evaluated or whether overlap was checked.

## What it settles for us

- The "7B close to DeepSeek-R1" claim rests on in-distribution numeric QA plus Chinese knowledge
  questions; it is not evidence on analytical judgement.
- Independent tests do not support transfer: Fin-R1 scores 10.87% and 0.00% on FinIndices with
  formula hints (`tong-2026`), and drops below its base on DocMath long-context tasks
  (`qian-2025`).
- Supports two S1 defaults: SFT on teacher traces does most of the work, GRPO adds a few points;
  general "thinking" distillation is not a free gain in finance.
- Reusable: the two-reward GRPO recipe (format plus judged accuracy), if S1 adds an RL arm.

## Limits

LLM judge throughout (training reward and evaluation); in-distribution evaluation; no held-out
task type; one size.
