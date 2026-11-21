# Summoning the Oracle to Slay It: Mitigating Look-Ahead Bias in Financial Backtesting with Large Language Models

- **Citation:** Weixian Waylon Li, Mengyu Wang and Tiejun Ma (2026). Preprint (University of
  Edinburgh). arXiv 2605.24564. Version read: v2 (29 August 2026), HTML full text.
- **Link:** https://arxiv.org/abs/2605.24564
- **Stream:** 08, blind replay
- **Verified against source:** yes, 2026-11-19 (HTML of v2 read through a machine extraction
  answering targeted questions, in two windows: characters 0 to 100,000, which hold sections 1 to
  5, the limitations and part of Appendix A, read twice; and 100,000 to 148,198, which hold
  Appendices B to G, read once. Tables 1, 3, 5, 8 and 11 and the Phi-4 and Qwen2.5 rows of Table 2
  covered. Not extracted: Table 4 in full, absolute Sharpe ratios, the values of α_max and α_cap.
  No number was checked against the PDF)

## Question
An LLM asked to trade on a past date may already hold the outcome in its weights. The authors
call this parametric look-ahead bias. Can it be reduced at inference time, with no retraining, so
that a backtest on pre-cutoff history ranks models the way a post-cutoff test does?

## Data
- **Calibration of the memory prompt:** S&P 500 stocks, quarter-end dates 2005 to 2015, forward
  63-trading-day returns; examples with an absolute return under 0.05 dropped; class-balanced and
  capped at 200.
- **In-sample backtest:** 2010 to 2020, before every model's cutoff. **Out-of-sample:** calendar
  2025.
- **Assets:** NVDA, MSFT, AAPL, NFLX, AMZN (mega-cap), POOL (mid-cap), SAM (small-cap); SPY in
  the leaderboard experiment.
- **Agent input:** price-derived summaries only (last close, trailing returns, moving averages,
  volatility, position in the 52-week range, dollar volume). No news, filings or fundamentals.
- **Models:** open-weight, 7 to 14 billion parameters. Five in the main experiments (Phi-4-14B,
  Qwen2.5-14B, Llama-3.1-8B, Starling-7B, DeepSeek-7B-Chat), eleven in the leaderboard
  experiment. Reported cutoffs run from November 2023 to November 2024 (Table 11).
- Delisted firms: not applicable.

## Method
- **Contrast (Eq. 1).** Next-token logits are (1 + α) · M(x_ctx) − α · M(x_prior). The method
  adapts Context-Aware Decoding.
  - Context branch: the full agent prompt, with entity, date and the data summary.
  - Prior branch: the same entity, date and task format with the data removed and the system
    prompt replaced by a memory-activating instruction.
- **Building the prior (section 3.1).** The memory-activating instruction is optimised once per
  model with MIPROv2 (DSPy) to maximise the accuracy of predicting direction from memory alone on
  the calibration set. The seed is "Recall what you know from your training data about this
  financial entity and predict the outcome." For three of the five models the optimiser kept the
  seed unchanged (Appendix B.3).
- **How much to subtract (section 3.2).** α is set per entity and date. A completion probe
  ("After t, s stock went") gives the entropy of the up and down logits. α grows when that
  entropy is below the entity's average over 12 calibration dates, scaled by how much the
  entity's entropy varies across dates, and is clipped. It is designed to fall to zero when the
  model shows no more confidence than usual. The scaling constant uses post-cutoff entropy, so
  the normalisation is transductive.
- **Decoding.** Both branches are run at every token. Greedy decoding hid the effect, because the
  shift rarely changed the top token; the backtests use temperature 1.0 with one seed.
- **Logits.** Required. The paper says the method "requires access to next-token logits".
- **Black-box variants.** Named in the limitations and not run: an API that returns
  log-probabilities for the action tokens could support a paired contrast outside the model; a
  text-only API would need repeated sampling, at higher cost and variance. The paper states that
  "neither black-box variant is evaluated here".
- **Comparison arms in the leaderboard experiment.** Anonymisation (ticker and company name
  replaced by numbered placeholders) and a stronger prompt instruction that calls any use of
  later memory a violation.

## Outcome variable and horizon
Ending value and Sharpe ratio of a long-only single-stock backtest (start $100K, 10 basis points
one-way cost, execution at the next open); change in accuracy on general benchmarks; rank
correlation between the in-sample and the post-cutoff leaderboard.

## Result
Empirical findings. The authors describe the leaderboard figures as observed effect sizes, not
formal inference; backtests use one seed.

- **In-sample correction, mega-caps, mean change in ending value.** Phi-4 −19.1%; Qwen2.5-14B
  −45.4%; Starling-7B −67.1% (the abstract's largest figure); DeepSeek-7B −27.3%; Llama-3.1-8B
  +26.5%, driven by one stock at +115.3%.
- **Out-of-sample, 2025.** Phi-4 0.0% on all five mega-caps: the penalty was zero every day.
  Qwen2.5-14B +1.8% on average, with three of five stocks unchanged. For the two smallest models
  the out-of-sample Sharpe moved by as much as −1.34 and +1.19 on single stocks (Table 8).
- **Leaderboard alignment (Table 5), mean Spearman correlation of Sharpe ranks over 330 subsets
  of 7 of the 11 models.** Baseline +0.779; anonymisation +0.547; stronger instruction +0.482;
  FinCAD +0.846. FinCAD improves the correlation in 10 of 11 leave-one-model-out cases.
- **Cost to general ability (Table 1).** Mean change in benchmark accuracy from +2.2 points
  (Phi-4) to −4.3 points (DeepSeek-7B, with −21.3 on GSM8K).
- **Size of the correction.** Mean in-sample α from 0.23 (Phi-4) to 1.06 (Qwen2.5-14B and
  DeepSeek-7B); it varies widely across stocks within a model.

## Look-ahead and memorisation
The paper's subject. It treats the short post-cutoff window as the only bias-free evaluation and
uses it as the reference: a correction is good if it makes the in-sample ranking agree with the
post-cutoff ranking. It says the method only partly mitigates the bias and that the entropy
signal is a heuristic with no ground truth for its precision or recall.

## What it settles for us
- **Strategy G (debias the output) with a commercial model: not supported, not contradicted.**
  The only evidence for subtracting a memory prior is at the logit level, on open models of 7 to
  14 billion parameters. The authors name the repeated-sampling variant we would need and say
  they did not test it. G stays a hypothesis.
- **The effect lives in the distribution, not in the top answer.** Greedy decoding hid it. A
  black-box version would therefore need probabilities estimated from many samples per branch;
  two modal answers would show nothing. The second sentence is our inference.
- **The prior branch is the plan's "company and date only" call.** A plain instruction to recall
  was as good as an optimised one for three of five models. The closed-book probe of strategy C
  can use the same wording.
- **Correct only where memory shows.** α is zero unless the model is unusually confident from
  name and date alone. This is the logic of strategy C applied to the output, and it suggests
  combining C and G: use the closed-book probe's confidence to decide which episodes need a
  correction or a blinded view. This is our inference.
- **Telling the model not to use later knowledge: contradicted as a mitigation.** The stronger
  instruction lowered agreement with the post-cutoff ranking, from +0.779 to +0.482.
- **Replacing only the name and ticker: contradicted as a mitigation.** It lowered agreement to
  +0.547. This is the weakest form of anonymisation, on price-only inputs, so it says little
  about the plan's levels L2 and above. The paper gives no mechanism for either fall.
- **Reusable.** Rank agreement between a pre-cutoff and a post-cutoff leaderboard as the test of
  any replay strategy, which is the plan's own yardstick.

## Limits
- No model above 14 billion parameters; nothing on frontier or commercial models.
- Inputs are price summaries. Whether the contrast works when the context is a long earnings
  release is not tested.
- One temperature and one seed per condition; several thousand GPU-hours.
- The normalisation uses post-cutoff entropy from the period later evaluated; the inductive
  version is not run.
- The correction lowered arithmetic accuracy sharply for one model, so it is not free.
- Llama-3.1-8B shows no out-of-sample change on any stock and a positive in-sample change; the
  paper does not explain the first.
