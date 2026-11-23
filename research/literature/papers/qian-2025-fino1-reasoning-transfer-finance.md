# Fino1: On the Transferability of Reasoning-Enhanced LLMs and Reinforcement Learning to Finance

- **Citation:** Qian, L., Zhou, W., Wang, Y., Peng, X., Yi, H., Zhao, Y., Huang, J., Xie, Q. and Nie,
  J.-Y. (2025). arXiv 2502.08127. Version read: v3 (14 June 2025), HTML full text. Earlier
  versions: v1 12 February 2025, v2 28 March 2025.
- **Link:** https://arxiv.org/abs/2502.08127 (HTML: https://arxiv.org/html/2502.08127v3)
- **Stream:** 13a, financial reasoning benchmarks and small-versus-large evidence
- **Verified against source:** yes, 2026-11-23, against the abstract page and the v3 HTML, read
  through an automated page reader answering targeted questions. Table values are as it returned
  them; not re-keyed from the PDF.

## Question

Do general "reasoning" models (o1, DeepSeek-R1, QwQ) carry their gains over to financial tasks,
and can a small model trained on financial chain-of-thought (CoT) data plus RL match them?

## Data

- **Evaluation set, FinReason (Table 2):** FinQA 1,100 items (tables and text, about 1.1K tokens);
  DocMath-Eval SimpLong 100 (one long table, about 4.3K tokens); DocMath-Eval CompLong 300 (several
  tables, about 40K tokens); XBRL-Math 90 (equations over XBRL concepts). All four have numeric
  answers. Licences: MIT for the first three, CDLA-Permissive 2.0 for XBRL-Math.
- **Training set, FinCoT:** 9,186 CoT-annotated QA pairs (7,686 SFT, 1,500 RL) from seven QA sets
  (FinQA, ConvFinQA, DocFinQA, TAT-QA, EconLogicQA, DocMath-Eval, BizBench-QA). GPT-4o writes and
  verifies the reasoning, with feedback loops. Questions Llama-3.1-8B already answers correctly are
  dropped (difficulty filter).
- No period, universe or delisting information; these are public QA sets built on old filings.

## Method

- Fin-o1-8B and Fin-o1-14B on Qwen3 backbones (the 14B backbone is presumed, not named). SFT then
  GRPO; PPO and DPO compared. GRPO reward mixes accuracy, a "logic" term, format (0.1) and a length
  term for long contexts. Weights not given.
- 29 models evaluated zero-shot, temperature 0, 1,024 output tokens.
- Grading: numeric answer extracted (TheoremQA style) and compared with the gold answer; the paper
  says it uses an LLM-as-judge rather than exact match. Judge model not identified.

## Outcome variable and horizon

Accuracy on numeric answers. No horizon.

## Result

Accuracy in percent (FinQA, SimpLong, XBRL-Math, CompLong, average), Table 3:

| Model | FinQA | SimpLong | XBRL-Math | CompLong | Avg |
|---|---|---|---|---|---|
| Fin-o1-14B | 74.18 | 55.00 | 87.78 | 27.33 | 61.07 |
| Fin-o1-8B | 73.03 | 56.00 | 84.44 | 26.33 | 59.95 |
| Qwen3-14B | 64.33 | 49.00 | 86.67 | 24.00 | 56.00 |
| Qwen3-8B | 62.11 | 46.00 | 83.33 | 17.67 | 52.28 |
| GPT-4o | 72.49 | 60.00 | 72.22 | 39.33 | 61.01 |
| DeepSeek-R1 | 65.13 | 53.00 | 86.67 | 38.67 | 60.87 |
| DeepSeek-V3 | 73.20 | 53.00 | 76.67 | 42.33 | 61.30 |
| Qwen2.5-72B | 73.38 | 59.00 | 67.78 | 14.67 | 53.71 |
| Llama-3.1-8B | 54.13 | 34.00 | 62.22 | 14.30 | 41.16 |

- Empirical finding: tuning lifts the 8B backbone by about 11 points on FinQA, 10 on SimpLong, 9 on
  CompLong and 1 on XBRL-Math. The average of the tuned 8B and 14B models lands next to GPT-4o and
  DeepSeek-R1.
- Empirical finding: the gap to frontier models stays on the longest, multi-table task (CompLong
  26 to 27 against 39 to 42). The average hides it.
- Empirical finding: general reasoning tuning does not carry over. QwQ-32B averages 52.92 against
  56.17 for Qwen2.5-32B-Instruct. Earlier finance reasoning models (Fin-R1, DianJin-R1-7B) beat
  their base on FinQA but fall below it on SimpLong (37 and 35 against 41) and CompLong (13.67 and
  14.67 against 17.67).
- Ablation (Table 4, Qwen3-8B): SFT on plain QA 51.92; SFT on all CoT 56.28; on filtered CoT
  58.58; plus PPO 58.10; plus DPO 54.49; plus GRPO 59.95. Most of the gain is the CoT SFT; GRPO
  adds about 1.4 points.
- No intervals, seeds or tests. On 100 SimpLong items a 95% interval is about ±10 points (my
  calculation), so the SimpLong ordering means little.
- Inconsistencies: the text gives Fin-o1-8B an average of 58.58, the table 59.95 (58.58 is the SFT
  ablation); the Limitations section says training used FinQA alone, Section 2 lists seven sets.

## Look-ahead and memorisation

Not addressed. FinQA feeds both FinCoT and FinReason, and DocMath-Eval subsets feed both; the paper
does not say the evaluation items were excluded from training. GPT-4o is teacher, verifier and
possibly judge.

## What it settles for us

- "Financial reasoning" in this line of work means numeric QA over tables. FinReason has no
  judgement, direction or synthesis item. It is S1 B2 territory, not the reasoning the owner means.
- Supports the S1-c result pattern: CoT distillation from a stronger model closes most of a small
  model's gap on in-distribution numeric tasks; RL adds little after SFT.
- Warns that the closing is task-local: on long multi-table context the tuned models stay far
  behind. An S1 reasoning exam should report held-out task types separately, not an average.
- General-purpose reasoning distillation can hurt on finance (QwQ against its base). Do not assume a
  "thinking" variant of the student or teacher is better on financial items.
- Reusable: the difficulty filter (drop items the student already solves) and XBRL-Math as a small
  equation-style probe.

## Limits

Numeric answers only; train-test overlap unexamined; one run per cell; judge unnamed; sizes 8B and
14B, far above the 0.8B S1 student.
