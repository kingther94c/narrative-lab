# Trading-R1: Financial Trading with LLM Reasoning via Reinforcement Learning

- **Citation:** Xiao, Y., Sun, E., Chen, T., Wu, F., Luo, D. and Wang, W. (2025). arXiv 2509.11420
  (Tauric Research; UCLA, University of Washington, Stanford affiliations per summaries). Version
  read: v1 (14 September 2025), the only version listed; HTML, main text and appendix (sections on
  rewards and sample traces), about 200K of 206K characters.
- **Link:** https://arxiv.org/abs/2509.11420 (HTML: https://arxiv.org/html/2509.11420v1)
- **Stream:** 14c
- **Verified against source:** yes, 2026-11-25, against the abstract page and the v1 HTML through
  an automated page reader, in two passes. No number was checked against a typeset PDF.

## Question

Can a 4B model be trained to write a structured, evidence-cited investment thesis from many data
sources and turn it into a buy/sell rating that trades well?

## Data

- Tauric-TR1-DB, about 100K samples; 14 large-cap equities and ETFs (NVDA, MSFT, AAPL, META, AMZN,
  TSLA, JPM, BRK, LLY, JNJ, XOM, CVX, SPY, QQQ); 1 January 2024 to 31 May 2025 (about 354 trading
  days, about 20 sample variations per day and ticker).
- Inputs 20-30K tokens: news (Finnhub, Google News), prices and technical indicators, fundamentals
  (SimFin, SEC filings), insider and analyst sentiment, macro (FRED).
- Labels: EMA-smoothed forward returns over 3, 7 and 15 days, each divided by rolling 20-period
  volatility, combined with weights 0.3/0.5/0.2, cut at asymmetric quantiles into five ratings
  (Strong Buy 15%, Buy 32%, Hold 38%, Sell 12%, Strong Sell 3%). Holding about one week.
- **Reasoning traces by "reverse reasoning distillation":** o3-mini or o4-mini sees the inputs and
  returns only a rating; a planner LLM infers the steps that would lead to it; GPT-4.1-nano expands
  how each data source contributes; the pieces are stitched into a thesis of 6-8K tokens.

## Method

- Qwen3-4B, LoRA SFT then GRPO with a KL penalty, in a three-stage curriculum; each stage is SFT,
  then reinforcement fine-tuning, then rejection-sampled self-distillation.
  - Stage I, structure: reward for 5-7 analysis sections, headers, bullets, bold, tables.
  - Stage II, claims: each bullet scored 0.4 for an opinion of 15-90 words, 0.35 for having a
    quote, 0.25 for having a source.
  - Stage III, decision: a 5x5 asymmetric payoff matrix against the volatility-adjusted label (1.00
    for an exact match, -2.25 for Strong Buy when the label is Strong Sell; -1.5 if no decision).
- Thesis sections in the sample traces: fundamentals, balance sheet, technicals, news, valuation,
  analyst coverage, risk, macro, conclusion; ends with a tagged decision.

## Outcome variable and horizon

Cumulative return, Sharpe ratio, hit rate and maximum drawdown of the rating-driven strategy, about
one-week holding; test window stated as 1 June to 31 August 2024.

## Result

| Ticker | Trading-R1 CR / SR / HR | SFT only | RL only |
|---|---|---|---|
| NVDA | 8.08 / 2.72 / 70.0 | 7.42 / 2.72 / 72.5 | 3.27 / 1.25 / 62.5 |
| AAPL | 5.82 / 1.80 / 63.6 | -2.37 / -1.27 / 45.2 | 4.04 / 1.14 / 57.1 |
| MSFT | 2.38 / 0.87 / 60.4 | -0.24 / -0.64 / 56.1 | -0.18 / -0.81 / 45.7 |
| AMZN | 5.39 / 1.72 / 63.0 | 1.93 / 0.36 / 60.6 | -0.05 / -0.29 / 52.5 |
| META | 5.12 / 0.86 / 50.0 | 2.52 / 0.54 / 55.9 | -0.18 / -0.36 / 44.4 |
| SPY | 3.34 / 1.60 / 64.0 | 1.78 / 0.86 / 58.1 | 1.85 / 1.00 / 67.6 |

- Empirical finding (as reported): the full curriculum beats SFT-only and RL-only on most tickers;
  larger baselines (Qwen3-32B, GPT-4.1, Llama-3.3) win on some ticker-metric pairs (e.g. Qwen3-32B
  Sharpe 2.12 against 1.72 on AMZN).
- Six tickers, one three-month window, no intervals, no transaction costs. The text and table
  disagree on NVDA's Sharpe (1.88 against 2.72).
- **No measurement of thesis quality:** no hallucination rate, no check that quotes exist in the
  inputs, no human or LLM grading. The authors report that hallucination persists in long, noisy
  contexts and that heavy RL erodes the SFT format.

## Look-ahead and memorisation

Claimed handled by using only information up to each trading day. But the stated test window (June
to August 2024) lies inside the stated data window (January 2024 to May 2025), and the paper does
not show it was excluded from training; Qwen3-4B's and the teachers' knowledge cutoffs are not
discussed. Treat the trading results as contaminated or at best bounded.

## What it settles for us

- The only published finance "analyst" model at 4B found by this stream. Its curriculum (structure,
  then evidence-backed claims, then decision) is a usable template for what a framework looks like
  in data: fixed sections, each claim tied to a quoted input and a source, a decision at the end.
- Its rewards check form, not truth: a bullet earns credit for having a quote and a source whether
  or not the quote is in the input or the claim follows. For S1 the analogue must be checkable
  claims (each stated figure or condition verified against XBRL), not formatting counts.
- "Reverse reasoning distillation" (rationale written backwards from a label) is the pattern
  `turpin-2023` and EXP-0029 warn about: a rationale fitted to a known answer. S1 should not write
  traces conditioned on the gold label; it should run the procedure forward and keep traces whose
  checked steps and answer are right.
- Return-based decision rewards are noisy and short-horizon; they are not a substitute for an
  analysis exam.

## Limits

Single version, preprint; six tickers, one window inside the data period; key formulas in
appendices only partly consistent with the main text; no thesis-quality measure; no costs.
