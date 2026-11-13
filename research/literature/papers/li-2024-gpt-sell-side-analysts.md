# The Promise and Peril of Generative AI: Evidence from GPT as Sell-Side Analysts

- **Citation:** Li, E. X., Shen, M., Tu, Z. and Zhou, D. (2024). Working paper, arXiv 2412.01069. Version read: v2, 22 October 2025 (first draft 25 June 2023).
- **Link:** https://arxiv.org/abs/2412.01069
- **Stream:** 02, LLMs extracting financial signals
- **Verified against source:** yes, 2026-11-12, against the full text of arXiv v2 (PDF, text extracted by script).

## Question

When does GPT forecast earnings accurately from an earnings press release, and can observable features of how it processed the release flag unreliable output?

## Data

Earnings press releases from 8-K filings on EDGAR, Item 2.02, for the four quarters before and the four after 30 April 2023, the knowledge cutoff of GPT-4 Turbo. Universe: the intersection of Compustat, CRSP and I/B/E/S, 68,514 announcements; 49,192 with full text; 1,000 randomly drawn firms with at least one quarter on each side of the cutoff; 7,216 with an I/B/E/S GAAP forecast; 7,114 with a GPT forecast (3,530 before, 3,584 after). 329,333 sentences.

The narrative given to the model runs from the start of the release to the forward-looking disclaimer, with tables removed. Ten standardised financial statements are supplied separately.

Delisted firms: not stated. A firm needs data on both sides of the cutoff, so firms that disappeared before it are out.

## Method

GPT-4 Turbo with a plain, non-technical prompt and three tasks: pick the three sentences most informative for future earnings and justify each; compute three non-EPS metrics from the statements, showing the calculation; forecast the direction and value of one-year-ahead GAAP and non-GAAP EPS, with a confidence score from 0 to 1.

Analysis: a sentence-level linear probability model of which sentences are picked, with press-release fixed effects; firm-quarter regressions of absolute forecast error on processing features, a post-cutoff indicator, size, analyst following, and industry and fiscal-quarter fixed effects. Robustness: GPT-4o, a CFA-style chain-of-thought prompt, non-GAAP EPS, a one-quarter horizon.

## Outcome variable and horizon

Absolute error of the one-year-ahead GAAP EPS forecast, scaled by the prior day's price; the same minus the analyst consensus error; directional accuracy.

## Result

All are empirical findings.

- **What GPT attends to.** It picks 5.8% of sentences. A sentence that contains a forecast (5.4% of all sentences) is 18.2 points more likely to be picked (t = 29.97). Moving from the start of a release to its end lowers the probability by about 11 points (t = -40.73). Longer sentences are favoured. The pattern is stable across size, analyst-following and cutoff subsamples.
- **Accuracy.** Mean absolute error 0.076, median 0.025, standard deviation 0.141. GPT minus analysts: mean 0.035 (0.033 before the cutoff, 0.038 after). The 25th percentile is -0.001, so GPT beats the consensus in more than a quarter of cases.
- **After the cutoff.** The post-cutoff indicator is +0.010 on absolute error (t = 3.10).
- **Direction.** 49.3% when inferred from the numeric forecast and 47.7% when asked directly, against 71.1% for analysts. The authors report that they could not reproduce the finding of Kim, Muhn and Nikolaev (2024) that an LLM beats analysts on direction.
- **Numeric reasoning.** One standard deviation more overlap between GPT's chosen metrics and those analysts forecast goes with 0.013 lower error, 16.8% of the mean; 5.6% of the mean once size and analyst following are controlled.
- **Confidence.** Mean 0.685. It tracks some drivers of accuracy and does not fall after the cutoff.

## Look-ahead and memorisation

The sample design is the control: releases are drawn symmetrically around the model's cutoff and every regression carries a post-cutoff indicator. The authors name a "time-traveler's advantage" for pre-cutoff documents. The GPT-4o replication is acknowledged to have a shorter post-cutoff window and more look-ahead risk. No masking and no memorisation probe.

## What it settles for us

- **Text source (supports).** 8-K Item 2.02 releases can be pulled from EDGAR at scale and cut at the forward-looking disclaimer. The cutting rule is reusable.
- **Splits by cutoff (supports).** Forecast error rises after the cutoff while stated confidence does not, so calibration must be measured on clean documents.
- **Extraction confirmatory, interpretation anchored (supports).** The model finds guidance sentences reliably and forecasts direction at coin-flip level. Locating a statement and interpreting it economically are separable, which is the split between our L1 and L2.
- **Evidence quotes (qualifies).** Selection is biased toward early and long sentences, and the paper checks that picked sentences were actually used only through word clouds of the model's rationale. Our verbatim-match check should also record where in the passage each quote sits.
- **Unit of analysis (partly supports).** Forecast-bearing sentences are 5.4% of a release, so a passage-level unit loses little. Nothing here compares consecutive releases.
- **Reusable.** The sampling frame (random firms by eight quarters around a cutoff) as a template for a bounded-versus-clean comparison; a "sentence contains a forecast" flag as a rule baseline.

## Limits

- A forecasting study. There are no gold labels for which sentences are guidance or for any extracted value.
- One model family.
- The analyst benchmark needs I/B/E/S coverage, so uncovered small firms are excluded.
- How the forecast flag is computed is not described in the text read.
- Associations only; the authors disclaim causal claims.
