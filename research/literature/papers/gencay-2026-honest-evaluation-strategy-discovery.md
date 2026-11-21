# What survives honest evaluation? Leakage-safe, search-aware assessment of LLM-driven trading strategy discovery

- **Citation:** Eray Gençay (2026). Preprint (independent researcher, Stuttgart). arXiv
  2608.27734. Version read: v1 (27 August 2026), HTML full text.
- **Link:** https://arxiv.org/abs/2608.27734
- **Stream:** 08, blind replay
- **Verified against source:** yes, 2026-11-19 (the whole HTML page of v1 read through a machine
  extraction answering targeted questions, in two passes; sections 3.1 to 3.3, 4.1, 4.4, 4.5, 6.1,
  6.4, 8 and 9 and Table 2 covered; figures not read; no number was checked against the PDF)

## Question
When an LLM agent searches for trading strategies and each candidate is backtested mechanically,
which of its discoveries survive an evaluation that rules out look-ahead in the features and
charges for the number of candidates tried?

## Data
- 453 US large-cap stocks plus SPY, daily bars from Tiingo, 2015 to 2026; the 200 most liquid
  names re-selected every 21 trading days. Design window 2017 to 2021, evaluation window 2022 to
  2025.
- 39 multi-asset ETFs, 2005 to 2026. Design window 2007 to 2016, evaluation window 2017 to 2025.
- Costs: 1 basis point commission, 2 basis points spread, square-root market impact, 50 basis
  points a year to borrow.
- Delisted firms: the universe is a fixed current constituent list with eight delisted names; the
  author says the resulting survivorship bias works against his null result.
- Models: gpt-4.1 (main) and claude-sonnet-5 (replication). No knowledge cutoff is stated.

## Method
- **What the LLM writes.** Declarative plans, not code: typed features, a signal graph
  (arithmetic, comparisons, rolling statistics, lags with non-negative shift only), a weighted
  combination and a portfolio archetype, assembled through tool calls.
- **Leakage-safe by structure.** The agent can select only features from a validated registry.
  Forward-looking features are excluded by a registry flag that drives the tool schema, the
  catalogue the model sees and the server-side validation. Signals use bars to day t and are held
  from day t + 1. A deterministic audit enforces publication delays on external event data.
- **Search-aware.** A trial ledger records every strategy evaluation, each refinement included.
  The Deflated Sharpe Ratio uses the trial count and the dispersion of trial Sharpe ratios; the
  probability of backtest overfitting is estimated by combinatorially symmetric
  cross-validation. An "evaporation curve" plots the best design Sharpe among the first k
  candidates against the threshold at k trials.
- **Holdout.** The search runs on the design window only; the evaluation window is never visible
  to it. What the agent is told about earlier candidates' design-window performance is not
  stated.
- **Leaky oracle.** One planted feature equals tomorrow's return, to test whether the statistics
  catch contaminated information.

## Outcome variable and horizon
Daily-rebalanced portfolio Sharpe ratio on the evaluation window, its Deflated Sharpe Ratio at
the 0.95 level, and the probability of backtest overfitting.

## Result
Empirical findings, scoped by the author to two universes, two models, at most 100 candidates and
five repeated runs.

- **The leaky oracle passes.** Design Sharpe 34.7, evaluation Sharpe 51.5, Deflated Sharpe Ratio
  1.00. Deflation corrects for selection among honest backtests and has no way to detect a
  contaminated information set.
- **gpt-4.1, 102 trials.** Best design Sharpe 1.69; evaluation Sharpe 0.18 with an interval
  spanning zero; Deflated Sharpe Ratio 0.86, below 0.95. Buy and hold had an evaluation Sharpe of
  0.60. The threshold reached 1.21.
- **claude-sonnet-5, 100 proposals.** Design Sharpe 0.44; evaluation Sharpe −0.33; Deflated
  Sharpe Ratio 0.18; probability of overfitting 0.51.
- **Five repeated gpt-4.1 runs.** All converged on a volatility-breakout family; all were
  profitable out of sample; none survived deflation (0.15 to 0.29).
- **ETFs.** SPY and equal-weight buy and hold are certified. The agent's discovery had an
  evaluation Sharpe of −0.23 and a probability of overfitting of 0.80.
- The author's conclusion: the discovered strategies are real programs with real out-of-sample
  returns, and none is yet distinguishable from luck at the recorded search intensity.

## Look-ahead and memorisation
Look-ahead in features and data timing is prevented by construction. Memorisation by the LLM is
not addressed: the page does not discuss the models' training data or cutoffs, whether the
evaluation windows postdate them, or whether the proposals repeat published anomalies.

## What it settles for us
- **Strategy E needs three controls that the plan does not yet list.**
  - A closed rule vocabulary over as-first-filed features, so that a rule cannot refer to
    anything dated after the episode.
  - A ledger of every rule or playbook version scored against history, with the verdict charged
    for the count. The plan's "development budget" becomes a number.
  - A stopping rule: stop when the threshold rises faster than the best candidate.
- **Statistics do not detect leakage: supported.** A feature with tomorrow's return passes
  deflation. The same holds for hindsight carried in the model's weights, so the test of
  strategy E has to be the clean post-cutoff set. The second sentence is our inference.
- **Prior for strategy E: low.** With look-ahead closed off and trials counted, no LLM-written
  strategy beat luck and buy and hold was certified. Rule 8 (simple baselines first) applies to
  playbooks as it does to models.
- **Convergence.** Repeated runs of one model proposed the same family. Several runs of one
  model are not independent draws; rule diversity needs different prompts or models. The second
  sentence is our inference.
- **Open question.** Whether a rule-writing LLM chooses rules it knows worked in the design
  period. Nothing here tests it. A design for S2: compare the gap between pre-cutoff and
  post-cutoff performance of LLM-written rules with the same gap for pre-specified baseline
  rules.

## Limits
- One author, no code released on the page; prompts are not shown.
- Price-based features only in the headline runs; news and fundamental features were excluded.
- The task is return prediction with daily bars, not the direction of fundamentals.
- Two models, default temperature; the abstract says the oracle also passes the overfitting
  test, and the body reports only the Deflated Sharpe Ratio for it.
