# Consistency Checks for Language Model Forecasters

- **Citation:** Daniel Paleka, Abhimanyu Pallavi Sudhir, Alejandro Alvarez, Vineeth Bhat, Adam
  Shen, Evan Wang and Florian Tramèr (2024). arXiv 2412.18544; v2 of 10 January 2025 (v1, 24
  December 2024), "Submitted to ICLR 2025". Version read: v2, HTML.
- **Link:** https://arxiv.org/abs/2412.18544 (HTML read: https://arxiv.org/html/2412.18544)
- **Stream:** 13b, reasoning item design (grading without ground truth). Stream 08 triaged this
  paper from its abstract; this note is the full read.
- **Verified against source:** yes, 2026-11-23. Abstract page and HTML main text through part of
  Appendix D (first 100,000 of 211,285 characters) via a machine extraction. The frequentist
  metric's derivation and the later appendices were not read.

## Question
Can a forecaster be scored now, before its questions resolve, by checking whether its
probabilities on logically related questions cohere, and does that score track eventual accuracy?

## Data
Base questions: 242 verified Metaculus and Manifold questions resolving 1 May to 15 August 2024;
a subset of 1,000 of 2,621 questions generated from news (NewsAPI) resolving July to August 2024,
resolutions checked with a search API at under 5% error; 1,000 synthetic questions resolving in
2028. A small pool of LLM forecasters (gpt-4o, gpt-4o-mini, o1-preview and others).

## Method
- Ten checks on tuples of questions: negation, paraphrase, consequence, and, or, and-or, but,
  conditional, double conditional, expected evidence (for example F(P) + F(not P) = 1;
  F(P) F(Q|P) = F(P and Q)). Tuples written by gpt-4o from base questions; about 2,000 candidate
  combinations scored for relevance and the top 200 per check kept; another LLM call rejects
  tuples that break the intended logic.
- Two violation metrics: arbitrage (guaranteed profit of a trader against the forecasts treated
  as prices of a log market maker) and a frequentist deviation from a Monte Carlo null. A check
  fails at a violation of 0.01 or more.
- ArbitrageForecaster: a wrapper that enforces consistency on chosen checks.

## Outcome variable and horizon
Violation rate per check; Pearson correlation across forecasters between violation and Brier
score on resolved questions; horizons of weeks (resolved sets) and to 2028.

## Result
Empirical findings.

- **Some checks track accuracy, others do not.** Correlation with Brier score (scraped,
  arbitrage metric): conditional 0.92, double conditional 0.78, and 0.68, negation 0.60,
  paraphrase 0.57; or 0.14, and-or 0.20. On news-derived questions the conditional check stays
  at 0.71 but negation turns negative (-0.36). Aggregate: 0.62 (arbitrage) and 0.85
  (frequentist) on scraped questions.
- **For comparison, MMLU error correlates 0.55 and 0.38 with Brier score**, and the authors note
  that part of any correlation is that better models are better at everything.
- **Forcing consistency does not buy accuracy.** The wrapper improves consistency on the checks it
  enforces and nothing else; no reliable gain in Brier score. The authors warn that consistency
  can be met without improving ground truth.

## Look-ahead and memorisation
Designed around it: base questions resolve after the forecasters' cutoffs, and the consistency
score needs no resolution at all. The authors note that Brier scores depend on training cutoffs,
which confounds model comparisons.

## What it settles for us
- **Consistency is a cheap diagnostic, not a target.** For S1, related questions on the same
  release (for example "did gross margin rise?", "did cost of revenue grow faster than
  revenue?") must cohere; the violation rate can be scored with no outcome label. The
  conditional-style checks, where one answer constrains another, carried the signal here;
  symmetric checks such as negation were unstable (empirical finding; transfer to S1 is a
  hypothesis).
- **Do not train the student on consistency alone.** The wrapper result says a model can learn to
  be consistent without being right, so a consistency score must sit beside an accuracy score.
- **Generated tuples need a logic check.** The authors used an LLM to reject malformed tuples;
  for S1 the tuples can be built by rule from the gold figures, which removes that error source.

## Limits
- Few forecasters, so a correlation across models rests on a handful of points.
- Binary questions only; the 0.01 threshold is a chosen hyperparameter.
- Several question counts are inconsistent across sections (900, 1,000, 3,000 for the 2028 set).
- Forecasting questions about world events, not financial statements.
