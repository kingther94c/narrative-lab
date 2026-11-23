# Are the Financial Reasoning from LLMs Credible? A Real World Test over Long-Horizon Statements (FinIndices)

- **Citation:** Tong, X., Zhang, X., Tang, T., Yang, A., Hu, J., Lin, G., Shi, Z., Zeng, L., Yang,
  B., Zhao, B., Wei, H., Qu, L. and Liu, D. (2026). arXiv 2607.28661. Version read: v1 (22 July
  2026), HTML, main text and Appendices A and B.
- **Link:** https://arxiv.org/abs/2607.28661 (HTML: https://arxiv.org/html/2607.28661v1)
- **Stream:** 13a
- **Verified against source:** yes, 2026-11-23, against the abstract page and the HTML through an
  automated page reader. Appendices C and D (weakness and structure analyses) were seen by title
  only.

## Question

Do LLMs reason over full financial statements, across periods and statement types, or do they
pattern-match when no formula is given?

## Data

- Real statements (balance sheet, income statement, cash flow; consolidated and parent-company) of
  829 listed companies, 384 indices, 28 reporting periods. Chinese Accounting Standards and six-digit
  codes point to Chinese listed firms; the paper does not say "A-share". Delisting not discussed.
- 68,307 instances: train 67,307, dev 360, test 640 (483 Single-Index, 157 Table-Index). Test items
  audited by three experts with majority vote. Uncropped context, mean about 16K tokens.
- Data on Hugging Face (Findata/Finindice); dataset licence not stated in the text read.

## Method

- **Single-Index:** one number, e.g. total invested capital, trailing-twelve-month (TTM) operating
  expenses, standalone-quarter year-on-year growth.
- **Table-Index:** a metric-by-period table (2 to 20 cells, mean 7.75), scored all-or-nothing.
- Capabilities tested: temporal (derive a standalone quarter from year-to-date figures; TTM),
  caliber (match a flow to the average of opening and closing stocks; day-count multipliers),
  domain (definitions).
- Traps: distractor periods and parent-company statements; items with a required statement removed,
  where the right answer is "Insufficient information".
- Hint arm (canonical formulas in the prompt) against no-hint arm.
- Grading automatic: regex extraction, numeric equivalence after the stated rounding. Tolerance not
  stated.

## Outcome variable and horizon

Accuracy. No horizon.

## Result

Test accuracy, Single / Table, with hint and without:

| Model | With hint | Without hint |
|---|---|---|
| Gemini-3.1-Pro (thinking) | 79.61 / 70.70 | 64.90 / 38.22 |
| Claude-Opus-4.8 (thinking) | 78.46 / 65.61 | 65.79 / 38.85 |
| GPT-5.5 (thinking) | 77.29 / 66.88 | 60.91 / 34.18 |
| Qwen3.5-35B-A3B (thinking) | 62.40 / 26.50 | 48.20 / 12.50 |
| DianJin-R1-32B | 41.29 / 11.41 | 32.39 / 5.33 |
| Fin-o1-14B | 28.16 / 2.67 | 18.32 / 1.97 |
| Fin-R1 (7B) | 10.87 / 0.00 | 4.41 / 0.00 |
| Llama-Fin-8B | 10.15 / 0.00 | 4.12 / 0.00 |

- Empirical finding ("knowledge bottleneck"): removing formulas costs frontier models 13 to 17
  points on single values and about 32 points on tables.
- Empirical finding ("structural bottleneck"): models that get single derivations right fall back to
  heuristics on multi-period tables: adjacent-column reads, plain arithmetic in place of an
  accounting adjustment.
- Empirical finding: finance-tuned small models that look strong on FinQA-style tests (Fin-R1,
  Fin-o1) collapse here, even with hints. The appendix flags format brittleness in small models.
- SFT of Qwen3.5-35B-A3B on 6,301 Gemini-distilled trajectories: no-hint +8.54 (47.92 to 56.46)
  single, +3.82 (15.29 to 19.11) table; small gains on five other finance benchmarks.
- General models averaged over three runs with standard deviations; finance models single run.

## Look-ahead and memorisation

Not addressed. Labels are computed from the statements, so recall of outcomes is irrelevant; recall
of formulas is the confound the hint arm controls.

## What it settles for us

- The closest existing design to an S1 "reasoning" step above B2: same raw material (statements),
  labels computed by rule, auto-gradable, yet frontier models are far from ceiling once the formula
  is withheld and several periods must be combined.
- The hint/no-hint contrast separates "knows what to compute" from "can compute"; with a calculator
  in both arms it isolates exactly the skill the owner says code does not supply.
- "Insufficient information" items and distractor periods are cheap to build from EX-99.1 tables
  (prior-year columns, nine-month columns) and test whether the model notices what is missing.
- All-or-nothing table scoring is harsh; per-cell scores should be kept alongside.
- No general model under 35B was tested; whether a 4B and a 0.8B can be told apart on these items
  is open.

## Limits

Chinese GAAP statements; 640 test items; finance models run once; tolerance unstated; context length
(16K) far above an EX-99.1 excerpt.
