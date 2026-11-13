# The Memorization Problem: Can We Trust LLMs' Economic Forecasts?

- **Citation:** Alejandro Lopez-Lira, Yuehua Tang and Mingyin Zhu (2025). Working paper, University
  of Florida. arXiv 2504.14765 (v1 20 April 2025, v2 15 December 2025). Version read: arXiv v2
  (HTML), cross-checked against the full-text PDF dated 20 November 2025 hosted by the American
  Finance Association (https://afajof.org/management/viewp.php?n=201880).
- **Link:** https://arxiv.org/abs/2504.14765
- **Stream:** 03, look-ahead bias and memorisation
- **Verified against source:** yes, 2026-11-12 (abstract, sections 1, 2, 3.3, 5.4, 5.6, 6 and
  Tables 5 and 7 read in the full text; other tables through a machine summary of the HTML)

## Question
Can an LLM's forecasts be trusted for periods inside its training window? Does the model recall
realised economic and financial values, and do prompt instructions or masking stop it?

## Data
- Models: GPT-4o snapshot `gpt-4o-2024-08-06` (training data ends October 2023), temperature 0.
  Llama-3.1-70B-Instruct (cutoff stated as December 2023) in additional analyses.
- Recall targets, January 1990 to February 2025: seven macro series (GDP growth, inflation,
  unemployment, 10-year yield, VIX, housing starts, payrolls); daily S&P 500, DJIA and Nasdaq
  levels; 90,123 Wall Street Journal front-page headlines.
- Stocks: month-end closing prices for the "Magnificent 7" and for 50 stocks per NYSE size
  quintile, resampled each year, from CRSP, January 1990 to December 2024.
- Masking tests: Capital IQ earnings call transcripts, January 2006 to September 2023, and
  RavenPack firm headlines (1,358,737 headlines, 4,391 firms, January 2000 to June 2024), both
  anonymised with the "entity neutering" approach of Engelberg et al. (2025).
- Delisted firms: not stated.

## Method
- Direct elicitation: a closed-book question for one value on one date ("What was the closing
  price of {ticker} on {date}? Provide your best estimate."), with a system message asking for the
  model's best recollection. Variants add the two previous values as context.
- Error and directional accuracy are compared before and after the October 2023 cutoff.
- Fake-cutoff test: the prompt tells the model to ignore information after a chosen date.
- Reconstruction test: the model reads an anonymised text and is asked for the ticker, industry,
  quarter and year.
- Theory: a task is "future-invariant" if the answer would be the same had the model been trained
  only on data up to the task date (Definition 1). Constrained prompts cannot identify that
  counterfactual answer (Proposition 1). Masking is valid only if the masked task is
  future-invariant and still shows skill (Definition 2).

## Outcome variable and horizon
Recall error (mean absolute error or mean absolute percentage error, MAPE), directional or
threshold accuracy, and identification accuracy. There is no forecast horizon; the paper measures
recall.

## Result
All are empirical findings for GPT-4o unless noted. The paper reports no intervals or
t-statistics for these metrics in the parts read.

- Index levels: S&P 500 MAPE 0.61% and directional accuracy 80.58% before the cutoff; 16.87% and
  45.70% after (Table 2).
- Macro: threshold accuracy 94% to 100% before the cutoff and 29% to 59% after (Table 1). GDP
  growth is 96.27% before and 40.00% after (n = 6).
- Headlines: the year is identified for 98.45% of pre-cutoff headline sets and 28.81% of
  post-cutoff ones (Table 3).
- Stocks by size (Table 5, no context, before cutoff): MAPE 11.29% for the largest quintile and
  24.70% for the smallest, with many refusals for small stocks. Over the last ten pre-cutoff years
  MAPE falls to 3.16% (largest) and 15.24% (smallest). After the cutoff MAPE is 23.52% to 97.83%.
- Fake cutoff: told to ignore everything after 2010, the model scores 97.6% threshold accuracy on
  GDP growth before the fake cutoff and 98.0% after it, against 40% after the real cutoff.
- Masked transcripts (Table 7, before cutoff): the firm is identified in 65.77% of large-cap,
  40.78% of mid-cap and 30.90% of small-cap transcripts (n = 593, 586, 466); the year in 44.69%,
  39.93% and 33.26%. For the Magnificent 7 the firm is identified in 85% to 100% of transcripts.
- Masked headline groups (Table 8): firm accuracy 21.13% over 2000 to 2023 (n = 8,714), 70.00% for
  the Magnificent 7, 8.12% for small and mid caps.
- Llama-3.1-70B shows the same pattern with larger errors (section 5.9.3).

## Look-ahead and memorisation
This is the paper's subject. Its control is the post-cutoff window (October 2023 to February
2025), which the authors call small and descriptive. Their rules:

- Any memorisation test gives a lower bound. A positive result is conclusive; a negative one is
  not (Remark 1). Restricting a sample to items the model failed to identify does not fix the
  problem.
- A small post-cutoff sample used as a robustness check has little power. If post-cutoff data are
  informative they should be the primary analysis (Proposition 2).
- Tasks likely to be future-invariant: factual extraction of names, dates and reported numbers;
  structural parsing; objective classification. Not future-invariant: judging importance or
  relevance, sentiment and tone, risks, forecasts, similarity (section 2.1). The authors add that
  even factual extraction "may be contaminated if the model has memorized specific facts".

## What it settles for us
- **Test documents postdate every cutoff: supported.** The conclusion asks for evaluation
  "exclusively" on post-cutoff data, as the primary sample.
- **Masking is not used: supported.** A frontier model re-identified between a third and two
  thirds of entity-neutered transcripts, more for large firms. This is the published source for
  the sentence in `00_master_methodology.md` section 3.
- **Contamination labels: supported, with a refinement.** The future-invariance question ("would
  an analyst's answer differ knowing what happened next?") separates what can be "bounded"
  (extracting stated guidance numbers) from what is "contaminated" on pre-cutoff text (tone,
  narrative change, risk).
- **Memorisation probe: supported.** The elicitation design is the template. Reusable: prompt
  wording (Appendix A), error and directional-accuracy metrics, size strata, a with-context
  variant, counting refusals separately.
- **Open question.** Whether models recall firm guidance or reported fundamentals is not tested;
  the paper covers prices, macro series and headlines.

## Limits
- One main model and one open model; both cutoffs are from 2023.
- Recall of prices and macro series may not carry over to guidance figures, which are less
  repeated in text.
- The transcripts were neutered by the authors' own run of the procedure; Engelberg et al. drop
  texts that stay identifiable, and it is not stated whether that step was applied here.
- Post-cutoff samples are small (5 to 12 observations per stock in Table 4).
