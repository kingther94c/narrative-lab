# EDINET-Bench: Evaluating LLMs on Complex Financial Tasks using Japanese Financial Statements

- **Citation:** Sugiura, I., Ishida, T., Makino, T., Tazuke, C., Nakagawa, T., Nakago, K. and Ha, D.
  (2026). ICLR 2026 (poster); arXiv 2506.08762. Version read: v2 (5 March 2026, "Accepted to ICLR
  2026"); HTML, main text and appendix tables.
- **Link:** https://arxiv.org/abs/2506.08762 (HTML: https://arxiv.org/html/2506.08762v2)
- **Stream:** 14c
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v2 HTML through
  an automated page reader. Table 6 rows for Claude 3.5 Haiku, o4-mini, Kimi-K2 and Llama 3.3 70B
  not read. No number was checked against a typeset PDF.

## Question

Can LLMs reading a whole annual report do analyst tasks whose labels come from later events
(accounting fraud, next-year profit direction), better than simple classifiers on the figures?

## Data

- Japanese annual reports (EDINET), April 2014 to April 2025; 41,691 reports (about 4,000
  companies, 10 years).
- **Fraud:** 6,712 amended reports; Claude 3.7 Sonnet judged from the amendment reasons whether
  fraud was involved (cue terms such as 不適切会計, 粉飾決算); 668 positives, all reviewed by hand
  (under 5% unrelated); 700 non-fraud companies sampled at random. After parsing: 534 fraud, 555
  non-fraud; train 865, test 224 (122 fraud / 102 not); company-disjoint.
- **Earnings:** 1,000 random companies, one consecutive-year pair each; label = whether profit
  attributable to owners of the parent rises next fiscal year. Time split: fiscal years starting on
  or before 1 January 2020 train (549), later test (451; 294 up / 157 down).
- **Industry:** 16 merged sector classes (not used here).

## Method

- Zero-shot, one report per item (about 30K tokens), system prompt "You are a financial analyst",
  three input settings: summary table; summary plus balance sheet, cash flow and P&L; plus narrative
  text. Temperature 0; LLM scores are the mean of three runs.
- Llama-3.2-1B fine-tuned on the train split (no hyperparameters given).
- Classical baselines on the same tables: logistic regression, random forest, XGBoost.

## Outcome variable and horizon

Fraud (restatement-derived, horizon undefined); sign of next-year profit change (one year).
ROC-AUC and MCC.

## Result

ROC-AUC (summary / plus statements / plus text):

| Model | Fraud | Earnings direction |
|---|---|---|
| Claude 3.5 Sonnet | 0.64 / 0.63 / 0.73 | 0.54 / 0.55 / 0.52 |
| Claude 3.7 Sonnet | 0.59 / 0.58 / 0.67 | 0.55 / 0.58 / 0.61 |
| GPT-5 | 0.56 / 0.62 / 0.67 | 0.58 / 0.62 / 0.65 |
| GPT-4o | 0.59 / 0.61 / 0.69 | 0.40 / 0.41 / 0.41 |
| DeepSeek-R1 | 0.54 / 0.56 / 0.63 | 0.43 / 0.46 / 0.44 |
| Llama-3.2-1B SFT | 0.61 / 0.66 / 0.54 | 0.52 / 0.52 / 0.48 |
| Logistic regression | 0.68 / 0.59 / 0.57 | 0.56 / 0.51 / 0.51 |
| Random forest | 0.75 / 0.75 / 0.73 | 0.54 / 0.53 / 0.52 |

- **Empirical finding.** Next-year profit direction is near chance for most models; best GPT-5
  0.65 (MCC 0.21) with full inputs; several frontier models are below 0.5.
- **Empirical finding.** On fraud, the best LLM (Claude 3.5 Sonnet with text, 0.73, MCC 0.32) does
  not beat a random forest on the summary table (0.75, MCC 0.38).
- **Empirical finding (small fine-tuned model).** The 1B SFT model reaches 0.66 on fraud from tables
  but falls to 0.54 when narrative text is added; earnings 0.48-0.52.
- **Empirical finding.** Narrative text helped most closed models on fraud (+0.08 to +0.10) and hurt
  DeepSeek-V3, Llama 3.3 70B and the 1B model.
- Qualitative: models flag red flags (profit up while operating profit down, investment gains)
  on non-fraud firms too, and some cite the auditor's name; logistic regression leans on size.

## Look-ahead and memorisation

Partly addressed. Company-name prediction from tables is at most 0.05 accuracy; fraud accuracy does
not drop for recent fiscal years (GPT-4o, Claude 3.5 Sonnet). Model knowledge cutoffs not stated;
the authors note that a clean test needs reports filed after every cutoff. The earnings test years
(2020 on) are before most evaluated models' cutoffs, so the earnings result is bounded at best; a
near-chance score under possible recall makes the negative result stronger, not weaker.

## What it settles for us

- Outcome-checkable judgements from filings are hard even for frontier models (AUC 0.5-0.65 for
  next-year profit direction) and a 1B fine-tuned model is at chance. This supports keeping S1's
  outcome items (R4) secondary and descriptive; they will not carry a 0.8B-against-4B comparison.
- Restatement-derived labels are a verifiable signal that is not a guidance-revision label. On EDGAR
  the analogue is an 8-K Item 4.02 non-reliance notice or a 10-K/A restatement after the release;
  rare events, so they suit a probe, not a training target.
- Supports rule 8: a tree model on a few summary figures matches the best LLM on fraud; any S1
  outcome item needs that baseline beside it.
- Narrative text can hurt a small model: S1 excerpts should be tested with and without the prose
  around the tables.

## Limits

Japanese filings; fraud labels LLM-made from amendment text with partial manual review; non-fraud
group sampled from all filers (size confound); small tests (224, 451); one 1B SFT model with
undisclosed training; zero-shot only; cutoffs not stated.
