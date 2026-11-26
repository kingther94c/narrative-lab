# Towards Competent AI for Fundamental Analysis in Finance: A Benchmark Dataset and Evaluation (FinAR-Bench)

- **Citation:** Wu, Z., Zou, C., Wang, J., Wang, C., Yang, H. and Shao, Y. (2025). arXiv 2506.07315.
  Version read: v2 (8 November 2025); HTML, main text and appendices (tables 1-8).
- **Link:** https://arxiv.org/abs/2506.07315 (HTML: https://arxiv.org/html/2506.07315v2); code and
  data at https://github.com/SAIFS-AIHub/FinAR-Bench (not opened)
- **Stream:** 14c
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v2 HTML through
  an automated page reader, in two passes. Figures 1 and 2 (task-size curves; scores with formulas
  supplied) were not readable as numbers. No number was checked against a typeset PDF.

## Question

Can financial statement analysis be split into steps whose outputs are each checkable against
filed data, and how do LLMs of different sizes do at each step?

## Data

- 100 companies listed on the Shanghai Stock Exchange, fiscal 2023 with 2022 comparatives; income
  statement, balance sheet, cash flow; given as text converted from XBRL and as PDF pages.
- 13 tasks per company: 6 extraction tasks and 6 indicator tasks at sizes 1, 2, 4, 8, 16, 32 items,
  plus 1 reasoning task. 32 financial items (Table 6), 38 indicators (Table 7: ROE, ROA, gross and
  net margin, debt-to-assets, equity multiplier, current and quick ratios, turnover ratios,
  revenue, profit and operating cash flow growth, expense ratios). No full DuPont decomposition.
- Reasoning: the model marks which of 64 conditions hold (32 pairs, Table 8: trend, e.g. ROE up or
  down; threshold, e.g. growth above or below zero; comparison, e.g. revenue growth against net
  profit growth), then writes an interpretation.
- Split stated as 90 development and 10 test companies (the main text's "1:9" wording conflicts);
  1,170 tasks matches 90 x 13.

## Method

- Tables scored by key matching (Hungarian assignment of row-column keys) with a relative-error
  threshold theta on numbers; main tables use theta = 0 (exact to four decimals).
- Condition table: precision and recall (exact procedure not described; no chance baseline).
- Narrative analysis: pairwise tournament judged by Doubao-1.5, Qwen-Max and Gemini-2.5-Pro, both
  orders, only for large models with logic recall above 60%.
- "Knowledge augmentation" arm: formulas supplied in the prompt.
- 14 models in three size groups (over 100B, over 10B, under 10B); no fine-tuning.

## Outcome variable and horizon

Step accuracy (precision and recall). No horizon.

## Result

Precision / recall, text input:

| Size | Model | Extraction | Indicators (theta 0) | Conditions |
|---|---|---|---|---|
| L | GPT-o1 | 100 / 100 | 34.76 / 34.76 | 86.20 / 86.20 |
| L | DeepSeek-R1 | 100 / 99.93 | 49.31 / 49.31 | 83.83 / 76.28 |
| L | GPT-4o | 98.39 / 98.39 | 34.38 / 34.38 | 63.23 / 63.23 |
| M | QwQ-32B | 98.96 / 98.85 | 35.01 / 34.97 | 77.50 / 75.91 |
| M | R1-Distill-Qwen-14B | 95.33 / 94.51 | 17.67 / 17.47 | 73.00 / 71.74 |
| S | R1-Distill-Llama-8B | 63.64 / 70.57 | 6.91 / 6.70 | 58.09 / 50.69 |
| S | Llama-3.1-8B | 37.81 / 67.22 | 8.46 / 8.40 | 50.19 / 50.19 |
| S | Qwen2.5-7B | 65.66 / 79.79 | 8.70 / 8.82 | 51.92 / 51.89 |
| S | Mistral-7B | 64.45 / 79.13 | 2.37 / 2.40 | n/a |

- **Empirical finding (exact match exaggerates the gap; tolerance matters).** Indicator recall at
  theta 0 / 0.01 / 0.05: GPT-o1 35.26 / 79.76 / 90.56; DeepSeek-R1 49.31 / 76.43 / 88.00; GPT-4o
  34.38 / 63.69 / 75.18; QwQ-32B 34.97 / 67.46 / 79.76; Qwen2.5-7B 8.82 / 35.81 / 46.59; Mistral-7B
  2.40 / 9.38 / 18.93.
- **Empirical finding (small models fail every step).** Untuned models under 10B: extraction
  precision 38-66 against 97-100 for large ones; indicators 35-47% at 5% tolerance against 75-91%;
  condition table about 50-58 against 63-86 (a coin-toss level for binary conditions, our reading).
- **Empirical finding (formulas do not help small models).** Supplying formulas helped medium and
  large models (most DeepSeek-R1, GPT-o1, QwQ-32B) and gave small models "minimal or even
  negative" gains (figure only).
- Extraction holds up as task size grows for large models (over 95% recall at 32 items); small
  models lose 10-20 points.
- PDF input lowers all scores.
- Error propagation is not measured: indicator and reasoning tasks get the raw statements, not the
  model's own extraction.

## Look-ahead and memorisation

Not addressed. Labels are computed from filed statements, so outcome recall does not arise; FY2023
reports predate most evaluated models' cutoffs and could be in pretraining data.

## What it settles for us

- A ready decomposition of "analysis" into steps checkable against filed data without a judge:
  extract line items, compute indicators, mark trend/threshold/comparison conditions, then
  interpret. This is the shape of a checkable framework for S1: R1's templates are single
  conditions; a release-level condition table (all conditions for one release at once) tests
  whether the student applies the whole framework, not one template.
- Grade indicators with a tolerance (1% and 5%) and report exact match separately; theta 0 alone
  turns rounding into failure.
- Matches EXP-0050: formula hints did not help the untrained 0.8B. Small models' bottleneck is
  not missing formulas but extraction and multi-step application.
- The condition table needs a chance baseline (balanced true/false or both members of each pair),
  which the paper omits.

## Limits

Chinese A-shares only; one fiscal year; 10 test companies; scoring of the condition table not
described; judge tournament counts inconsistent; no tuned small models; small numerical
inconsistencies across tables (GPT-o1 indicator 34.76 against 35.26).
