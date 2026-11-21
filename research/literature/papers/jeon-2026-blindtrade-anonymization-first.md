# Can Blindfolded LLMs Still Trade? An Anonymization-First Framework for Portfolio Optimization

- **Citation:** Joohyoung Jeon and Hongchul Lee (2026). arXiv 2603.17692, v1 of 18 March 2026,
  the only version (Korea University; Mirae Asset Securities). The arXiv record says it was
  accepted at the ICLR 2026 Workshop on Advances in Financial AI. Version read: v1, full text.
- **Link:** https://arxiv.org/abs/2603.17692
- **Stream:** 08, blind replay
- **Verified against source:** yes, 2026-11-19 (full text of v1 read as page text from the arXiv
  HTML in the in-app browser: abstract, sections 1 to 7, Appendices A to D with the verbatim
  agent prompts, and Tables 1 to 9. Figures 1 to 7 were read by caption only. Footnote 1 was not
  captured.)

## Question
If tickers and company names are hidden from LLM agents, do their trading signals still carry
information? The authors want performance that cannot come from remembered ticker associations.

## Data
- **Universe:** S&P 500 constituents as of each date, from the EODHD API, 2 January 2020 to
  1 August 2025 (1,403 trading days). Firms that left the index are included while they were
  members.
- **Inputs:** technical indicators computed from prices (moving-average ratios, RSI, MACD, beta,
  value-at-risk) and up to five news headlines per stock, from the 60 business days before the
  decision date.
- **Model:** Gemini 2.5 Flash, accessed September to October 2025. Its knowledge cutoff is not
  stated.

## Method
- **Anonymisation (section 3.2).** Tickers are mapped to synthetic identifiers ("AAPL" becomes
  "STOCK_0026"). In headlines, company, subsidiary, product and person names are replaced using
  the Google Knowledge Graph API.
- **What is not hidden.** Verified fact from the prompts in Appendix C: each agent is given the
  execution date and the data-as-of date, and one agent is given the current macro regime.
  Sector membership is kept for the graph. Numbers are not altered.
- **Cutoff by instruction.** Each prompt says "Your knowledge is strictly limited to information
  available up to {cutoff_date}".
- **Pipeline.** Four agents (momentum, news-event, mean-reversion, risk-regime) score batches of
  15 stocks and give a short reasoning. The scores and an embedding of the reasoning feed a
  graph attention network, and a reinforcement-learning policy picks 20 stocks with no cash,
  rewarded by a differential Sharpe ratio net of 10 basis points per unit of turnover.
- **Splits.** Train 2 January 2020 to 30 September 2024; validation to 31 December 2024; test
  2 January to 1 August 2025 (145 days). An extended test covers 2 January 2024 to 1 August
  2025 (397 days) with training to the end of 2023 and different tuned parameters.
- **Screening.** Agent outputs are kept as features if their rank correlation with 21-day
  forward returns is positive or improves on the raw indicator "on holdout".
- **"Leakage audit" (section 4.4).** The network's prediction scores are shuffled across stocks,
  with everything else unchanged.
- There is no identification test and no arm with the real tickers.

## Outcome variable and horizon
Portfolio Sharpe ratio, cumulative return and drawdown over the test window, with daily
rebalancing. Signal quality is the Spearman rank correlation with returns 21 days ahead.

## Result
Empirical findings.

- **Main test, 2025 to 1 August (Table 2).** Sharpe 1.40 ± 0.22 across 20 seeds; cumulative
  return 32.22% ± 5.21; maximum drawdown -31.66%; volatility 42.34%. SPY: 0.64, 8.52%, -19.00%,
  23.26%. A top-20 portfolio on the raw indicators alone: Sharpe 0.97.
- **Extended test, 2024 to 1 August 2025 (Table 8).** Sharpe 0.69 ± 0.23, below SPY (1.06),
  momentum (1.34), the 20 largest stocks (1.54) and the raw-indicator top 20 (1.69). In 2024
  alone: 0.34 against 1.70 for SPY (Table 9).
- **Signal strength (Table 1).** Rank correlations of the agents' scores with 21-day returns:
  momentum +0.001 (p = 0.58), news-event +0.006, mean-reversion 0.000 (p = 0.97), risk-regime
  +0.011; average +0.005.
- **Ablation.** Without the LLM features the Sharpe ratio falls from 1.40 to 1.14 ± 0.02;
  without the graph, to 0.62 ± 0.50.
- **Shuffle test.** The absolute rank correlation falls from 0.015 to 0.0004 and a simple top-20
  rule goes from a Sharpe of -1.17 to -1.48.
- **Stated by the authors (Appendix A).** "Anonymization effect is not directly validated": no
  comparison of anonymised and raw-ticker inputs was run, and the shuffle test validates "signal
  structure, not anonymization effectiveness". Section 3.2: "We do not claim this blocks all
  leakage".

## Look-ahead and memorisation
- The control is renaming plus an instruction to ignore later knowledge. Neither is tested.
- The model was accessed in autumn 2025 and the data run from 2020 to August 2025. Whether any
  of the test window lies after the model's training data is not addressed.
- The shuffle test shows that the scores are related to returns. A remembered signal would pass
  it as well. Our inference.
- Survivorship is handled by point-in-time index membership.

## What it settles for us
- **Renaming as a blindfold: not addressed.** The paper names the approach and does not test it.
  It gives no support to level L1 of S2 strategy A, and none against it.
- **What a blind-replay design must not copy.** The decision date is in the prompt. The plan's
  hypothesis H2 treats time as the more important thing to hide, and Engelberg et al. (2025)
  find that with only the firm name masked the date of a news article is recovered more often
  than the firm (see our note). A design that hides the ticker and shows the date leaves that
  channel open. Our inference.
- **An instruction is not a cutoff.** Levy (2026) cites Sarkar and Vafa (2024) for the finding
  that many LLMs do not respect knowledge-cutoff directives; see our note on Levy.
- **A shuffle test belongs with sanity checks, not leakage metrics.** S2's leakage measures
  (recognised against unrecognised views of one episode; contradiction tests) ask a different
  question. Our inference.
- **Skill under a blindfold is weak here.** The agents' average rank correlation is 0.005, the
  gain from LLM features is 0.26 of Sharpe in one 145-day window, and the system trails simple
  benchmarks over the longer window. This is in line with Levy's result that little is left once
  recall is unavailable, though here recall was never shown to be blocked. Our reading.
- Nothing reusable beyond the verbatim prompts as an example of a structured-output agent.

## Limits
- A workshop paper with one vendor model and one 145-day test window. The headline result does
  not hold over 397 days.
- No identification test, no raw-ticker arm, no statement of the model's cutoff.
- Features are screened on "holdout" correlations, and the text reports the 2025 correlation for
  one agent. If the screen used the test window, the test is not clean. The paper does not say
  which period the screen used; this is our reading.
- The 20 seeds vary the policy training, not the market sample, so the ± figures are not
  sampling error over time.
- The main and the extended evaluations use different tuned parameters, and their 2025 figures
  differ (Sharpe 1.40 against 1.02).
- Volatility and drawdown are well above the index; the authors accept this.
