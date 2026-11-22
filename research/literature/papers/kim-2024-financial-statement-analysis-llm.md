# Financial Statement Analysis with Large Language Models

- **Citation:** Kim, A., Muhn, M. and Nikolaev, V. (2024). Working paper, arXiv 2407.17866. Version
  read: v2, 10 November 2024 (HTML, first and second halves). v3 (20 February 2025) withdraws the
  paper: a co-author found inconsistencies in the data and analyses (stream 02 row).
- **Link:** https://arxiv.org/abs/2407.17866v2 (HTML: https://arxiv.org/html/2407.17866v2)
- **Stream:** 10, accounting signals (streams 02 and 08 hold triaged rows for the same paper)
- **Verified against source:** yes, 2026-11-22, against the v2 HTML. The appendix prompt and the
  example output are images and were not read; Figure 7 frequencies were not read.

**Status: withdrawn. Its results carry no weight as evidence. This note records its method only,
because S2 needs a prompt for ratio analysis and this is the best-known one.**

## Question

Can GPT-4, given only standardised, anonymised financial statements, predict the direction of next
year's earnings as well as analysts and trained models?

## Data

Compustat annual data, fiscal 1968 to 2021: "150,678 firm-year observations from 15,401 distinct
firms" (quoted). The model sees "two years of balance sheet and three years of income statement
data" (quoted), in Compustat's balancing-model layout, with no firm name, no dates (years relabelled
t, t-1, t-2), no MD&A and no industry information. No cash flow statement.

## Method

gpt-4-0125-preview. Chain-of-thought prompt (Section 3.1 and Figure 1): the model takes "the role
of a financial analyst"; it is told to (i) identify notable changes in financial statement items,
(ii) compute key financial ratios, stating the formula first (no fixed list of ratios), (iii)
"provide economic interpretations of the computed ratios", and (iv) synthesise and predict whether
earnings increase or decrease next year, with a rationale paragraph, a magnitude (large, moderate,
small) and a confidence score from 0 to 1. Benchmarks: a naive model, analyst consensus at one,
three and six months, stepwise logit and neural networks on 59 ratios (Ou and Penman) trained on
rolling five-year windows.

## Outcome variable and horizon

Sign of the change in next year's EPS; one fiscal year.

## Result (as reported in v2; withdrawn)

- Reported: CoT GPT 60.31% accuracy (F1 63.45%) on the full sample; analysts 52.71% at one month,
  55.95% at three, 56.58% at six; stepwise logit 52.94%; neural network 60.45%; simple prompt
  without CoT 52.33%.
- Reported: the model's ratio analysis most often refers to operating margin, then asset and
  inventory turnover and the current ratio; its rationales mention growth, liquidity, operating
  profitability and efficiency (Figure 7, read through the prose only).
- Reported: an ANN on embeddings of the generated text reaches about 59%; statements plus text
  63.16%.
- Another team could not reproduce the directional advantage over analysts: GPT-4 Turbo direction
  48 to 49% against analysts' 71% (`li-2024`, stream 02).

## Look-ahead and memorisation

Names and years removed. Asked to guess, the model names the firm 0.07% of the time and the year
2.95% (0.09% and 1.01% with CoT, Table 6). Out-of-sample test on fiscal 2022 statements predicting
2023 earnings, after the April 2023 training cutoff: 58.96% (ANN 59.10%). The authors kept text out
because text "is much more difficult to anonymize, potentially introducing look-ahead bias". Stream
08 (`levy-2026`) already notes that failing to name the firm does not show the episode is clean.

## What it settles for us

- Nothing about effect sizes: withdrawn.
- A usable prompt skeleton for an accounting-structure skill: changes first, ratios with formulas,
  interpretation, then the call. The ratios it gravitated to (margin, turnover, liquidity) are the
  textbook set; for a revenue label they need to be replaced by the leading indicators in stream
  10's checklist (backlog, deferred revenue, inventory mix, units times rate).
- The "simple prompt" arm did no better than chance-like baselines (52%). A free-form "analyse the
  statements" instruction should not be assumed to add signal; any skill must be tested against
  the code baseline (0.65 in EXP-0034).

## Limits

Withdrawn. Annual horizon, earnings sign, all Compustat firms. The prompt text itself (appendix) was
not read.
