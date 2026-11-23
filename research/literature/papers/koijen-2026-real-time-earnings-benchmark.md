# Assessing the Benefits of Optimized Agentic AI Systems for Asset Pricing

- **Citation:** Ralph S. J. Koijen and Bradford Levy (2026). NBER Working Paper 35431, July 2026;
  also BFI Working Paper 2026-100 and CEPR DP 21674. Version read: BFI PDF of July 2026.
- **Link:** https://www.nber.org/papers/w35431 (PDF read:
  https://bfi.uchicago.edu/wp-content/uploads/2026/07/BFI_WP_2026-100.pdf)
- **Stream:** 13b, reasoning item design (outcome-grounded labels without look-ahead). Stream 08
  listed "Koijen and Levy 2026" as not opened; this is the first read.
- **Verified against source:** yes, 2026-11-23. NBER abstract page, and the PDF's sections 1 to 4
  read through a crude local text extraction (equations partly garbled; tables read through the
  text that describes them). The NBER conference slides could not be extracted.

## Question
How well can AI systems explain same-day stock returns around earnings announcements, scored in
real time so that neither training data nor optimisation can carry look-ahead?

## Data
1,849 US earnings events in the fourth calendar quarter of 2025 (October to December), all 12
Fama-French industries. Expected announcement dates, consensus and actual EPS from a commercial
calendar provider; conference-call transcripts from S&P Capital IQ; daily prices from a market
data vendor. Robustness with I/B/E/S and Capital IQ prices. Delisted firms: not stated (with a
one-day return label it matters little; our reading).

## Method
- Benchmark: a submission is one scalar prediction per event; score is the R-squared (and the
  increment over controls such as the earnings surprise) from a cross-sectional regression of
  the one-day market-adjusted abnormal return on the prediction. Returns and surprises are
  converted to within-quarter percentile ranks to curb outliers. Event day is the announcement
  day or the next trading day for after-close releases.
- Real-time protocol: prompts, context and model parameters are fixed before each
  announcement; transcripts are passed to the models as soon as available and predictions are
  collected within a fixed window. Information learned earlier in the quarter may be used later
  in it.
- Models: Gemini 2.5 Flash-Lite, GPT-5 nano, Claude Opus 4.5 (no web access). Prompt optimisation
  (GEPA) and rule-book context building (ACE) trained on the first half of the quarter (1,032
  events) and evaluated on the second (817). 99% bootstrap intervals.

## Outcome variable and horizon
One-day abnormal return around the announcement, as a percentile rank.

## Result
Empirical findings.

- **Baseline.** The earnings surprise alone gives R-squared 5.0%.
- **LLMs add to the surprise.** Opus 4.5 on the full transcript: 10.9% alone [0.08, 0.15], 14.3%
  with the surprise [0.10, 0.18]. Gemini 2.5 Flash-Lite 7.5% and GPT-5 nano 7.1% alone. The
  surprise coefficient falls only from 0.219 to about 0.18 when the LLM prediction is added.
- **Summaries keep most of it for the strong model only.** Opus summaries about 28 times shorter:
  Opus 9.3% alone, 13.0% with surprise; GPT-5 nano falls from 7.1% to 3.0%.
- **Optimisation helps out of sample, modestly.** GEPA on Gemini: 10.5% to 12.8%, overlapping
  intervals; the optimiser mostly removed a mean bias ("good is priced in"). ACE on Opus: 14.1%
  to 17.1% [0.12, 0.24] on the late half.
- **A rule book written by the big model transfers to small ones.** With the Opus-built rule
  book: Haiku 4.5 11.7%, Sonnet 4.5 12.1%, Opus at low effort 13.9%, against 14.1% for Opus at
  high effort without it.

## Look-ahead and memorisation
The design's main point. Every event postdates every model's training cutoff, the prompt is
frozen before the event, and labels arrive after the prediction. One model processed transcripts
with a short delay; the authors rely on the vendor's stated cutoff (August 2025) and the absence
of web access. Optimisation uses only events earlier in the same quarter.

## What it settles for us
- **The cleanest outcome label for "reasoning about a release" is the market's reaction scored
  prospectively, against the earnings surprise as baseline.** It answers the owner's question
  "does the model understand what matters in the release?" with a label no one has to write.
  Status for S1: the design transfers; S1 has no price data yet (open question).
- **The effect sizes set expectations for power.** Even the best system explains under a fifth of
  cross-sectional variance; the gap between Opus and GPT-5 nano was about 4 points of R-squared
  on 1,849 events with wide intervals. A 0.8B-against-4B comparison on a few hundred S1 test
  releases would be underpowered on this label (our inference). It suits a secondary, quarterly
  prospective section, not the primary S1 metric.
- **Summaries and rule books distil across model sizes.** The rule-book transfer to Haiku is the
  context-level analogue of S1's distillation; it supports testing a small model with the large
  model's distilled guidance as an arm (hypothesis for S1).
- **Rank-transform and regress on the baseline**: a reusable scoring convention for any S1
  outcome item.

## Limits
- One quarter, three base models; future versions promised.
- The input is the call transcript, not the 8-K press release; results for the press release
  alone are not reported.
- Prompt optimisation results have overlapping intervals; the ACE gain is on a single split.
- The R-squared target rewards ranking events, not a calibrated forecast.
- Uses licensed transcripts and vendor data that this project cannot redistribute.
