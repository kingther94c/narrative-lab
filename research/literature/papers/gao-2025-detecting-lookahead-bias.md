# Detecting Lookahead Bias in LLM Forecasts

- **Citation:** Zhenyu Gao, Wenxi Jiang and Yutong Yan (2025). Working paper, CUHK Business School.
  arXiv 2512.23847. v1 (29 December 2025) was titled "A Test of Lookahead Bias in LLM Forecasts";
  v2 (12 June 2026) carries the present title. Version read: v2, full text.
- **Link:** https://arxiv.org/abs/2512.23847
- **Stream:** 03, look-ahead bias and memorisation
- **Verified against source:** yes, 2026-11-12 (abstract, sections 2.1 and 3, Figure IV, the
  implementation steps, and Tables III to X through a machine summary of the HTML)

## Question
Can a researcher test, at low cost and without retraining, whether an LLM's forecast is
contaminated by what the model already knows about the outcome?

## Data
- Model: Llama-3.3-70B-Instruct, training cutoff December 2023, run locally at temperature 0 with
  the top 20 token log-probabilities.
- Stock news: Bloomberg headlines matched to CRSP common stocks. In sample January 2012 to
  December 2023: 91,357 headline-days, 1,587 firms. Out of sample: 2024, 7,568 headlines.
- Earnings calls: Thomson Reuters StreetEvents transcripts merged with CRSP and Compustat. In
  sample 2006Q1 to 2020Q4: 106,994 firm-quarters, 3,920 firms. Out of sample: calls from 2023Q3 to
  2024Q1, 6,744 firm-quarters.
- Delisted firms: not stated.

## Method
- **Recall query.** For each firm and date the model gets only the company name, ticker and
  target date, and is asked whether the outcome went up or down, with the instruction to answer
  "unknown" if it does not recall. One word is allowed: up, down or unknown.
- **Lookahead Propensity.** LAP = P(up) + P(down), read from the first answer token. The
  directional recall signal is P(up) minus P(down).
- **Validation regression.** Does the recall signal alone predict the outcome among high-LAP
  observations? This shows that memorised outcomes exist.
- **Detection regression.** Outcome on the LLM forecast, LAP, and forecast times LAP. A positive
  interaction indicates that memorised content reaches the forecast. The test is one-sided and
  identifies the sign, not the size.
- **Assumptions (Appendix B.1).** LAP is independent of the true signal and of the outcome
  innovation given controls; the innovation is homoskedastic; transmission is partial; the
  forecast's slope is non-decreasing in LAP.
- **Placebo.** The same regressions on post-cutoff data.
- **Inputs the test needs.** Realised outcomes with entity and date; the model's stated cutoff;
  the forecasts under test; token probabilities at the answer position. Open weights give these
  directly and some commercial APIs expose log-probabilities. Otherwise the authors suggest answer
  frequencies over repeated samples at positive temperature, which they do not test.

## Outcome variable and horizon
Next-trading-day stock return; capital expenditure over assets two quarters ahead.

## Result
Empirical findings, one model.

- Stock news (Table IV, firm and date fixed effects, standard errors clustered by date): forecast
  times LAP 0.162, t = 3.64. The forecast's marginal effect is 0.303% at LAP = 1 and 0.141% at
  LAP = 0. One standard deviation of LAP adds 0.067 percentage points, about 32% of the standalone
  effect.
- Earnings calls (Table VIII, firm and quarter fixed effects, clustered by firm): interaction
  0.512, t = 2.01; one standard deviation of LAP adds about 12% of the standalone effect.
- Validation: the recall signal predicts returns in the high-LAP half (0.306, t = 3.59) and not
  in the low-LAP half (t = -0.33).
- After the cutoff: across 7,806 firm-day recall queries in 2024 the largest LAP is below 0.0001;
  across 6,619 firm-quarter queries it is below 0.00001. The interaction is insignificant
  (t = 1.06 and 1.35) while the forecast itself still predicts (t = 6.47 and 3.44).
- In sample, about 42% of stock firm-days put essentially all mass on "unknown" and about 23%
  are saturated at LAP of 0.95 or more. For earnings calls 96.3% of firm-quarters have LAP below
  0.2.
- **By year (Figure IV).** Mean LAP for stock news is 0.88 in 2020, 0.39 in 2021, 0.18 in 2022,
  0.016 in 2023 and 0.000 in 2024. For capital expenditure it is 0.050 in 2020, 0.025 in 2021,
  0.004 in 2022 and about 0.000004 in 2023. The authors stress the collapse after the cutoff. The
  decline over the two years before it is our reading of the figure, not a claim they make.

## Look-ahead and memorisation
This is the paper's subject. The authors present the test as a diagnostic, not a remedy. They
state that masking identifiers "need not remove the contamination" and recommend restricting
backtests to post-cutoff data. They note that LAP may proxy for how salient a firm is, and use the
post-cutoff placebo to address this.

## What it settles for us
- **Memorisation probe: supported, and its design should change.**
  - Use an entity-and-date-only query with an explicit "unknown" option, and record answer-token
    probabilities. Local models expose them; commercial models need repeated sampling.
  - Recall is already near zero in the last year before the stated cutoff. A probe that compares
    only the quarters on either side of the cutoff will find no gap in a contaminated model. It
    needs quarters several years before the cutoff as a positive control.
  - A per-item propensity allows an interaction test in place of a single before-and-after
    difference.
- **Test documents postdate every cutoff: supported.** Recall vanished after the stated cutoff
  for this model; the pre-cutoff decline suggests a stated cutoff errs on the safe side. This is
  one model, so the buffer rule in `00_master_methodology.md` section 2 stays.
- **Masking is not used: supported** by the authors' argument; they run no masking experiment.
- **Open question.** The test is built for forecasts. Whether recall raises accuracy on an
  extraction task has not been tested by anyone in this stream.
- Reusable: the two recall prompts, the regression specification, the placebo design.
- The paper links a `CLAUDE.md` file that runs the procedure with Claude Code. It was not
  downloaded or opened for this review. The owner should read it before any use.

## Limits
- A single open-weight model; nothing run on a commercial API.
- No analysis by firm size or coverage.
- Capital-expenditure recall is weak everywhere (mean LAP 0.028 in sample), so the earnings-call
  result rests on a small tail.
- Post-cutoff coefficients are scale artefacts because LAP has almost no variance there; only the
  t-statistics are informative.
- Recall-query counts differ slightly from sample sizes (7,806 against 7,568; 6,619 against
  6,744) without explanation.
