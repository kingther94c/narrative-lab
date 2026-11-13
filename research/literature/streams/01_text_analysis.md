# Stream 01: financial text analysis before LLMs

Twelve papers triaged, three deep-read; all rows of `01_text_analysis.csv` verified 2026-11-12.

## What the stream establishes

- **Empirical finding.** Changes carry more than levels. Year-over-year dissimilarity of 10-K and 10-Q text predicts returns (five-factor alpha 0.34 to 0.51% a month, t 2.5 to 3.4), lower earnings and more bankruptcies, incremental to size, value, momentum, SUE and dictionary tone change (`cohen-2020-lazy-prices.md`).
- **Empirical finding.** Dictionary tone levels are weak: R² near 2.5% for 10-K filing returns, no significant long-short alpha ([Loughran and McDonald 2011](https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_loughran-mcdonald-je-2011.pdf)). Press-release optimism is associated with future ROA ([Davis et al. 2012](https://api.openalex.org/works/doi:10.1111/j.1911-3846.2011.01130.x)).
- **Empirical finding.** Guidance is updated routinely: nearly 90% of annual EPS forecasters update, about a quarter of updates repeat the range, and regular updaters raise more often than they cut (`tang-2025-forecast-updates.md`).
- **Empirical finding.** Numeric earnings forecasts are about 5% of forward-looking sentences in 8-K earnings releases; 37% of releases carry an I/B/E/S forecast. Other forward-looking statements matter as much per standard deviation, and rise with uncertainty while numeric forecasts fall (`bozanic-2018-other-forward-looking-statements.md`).
- **Empirical finding.** Firms that stop guiding had weaker prior performance; some announce it, some stop quietly ([Chen et al. 2011](https://econpapers.repec.org/RePEc:eee:jaecon:v:51:y:2011:i:1-2:p:134-150)). Good-news forecasts move prices only with verifiable supporting statements ([Hutton et al. 2003](https://econpapers.repec.org/RePEc:bla:joares:v:41:y:2003:i:5:p:867-890)).
- **Convention.** Guidance labels come from commercial databases that under-record qualitative and non-EPS guidance (Bozanic and Tang notes). Bundled guidance news must be conditioned on the earnings surprise ([Rogers and Van Buskirk 2013](https://econpapers.repec.org/RePEc:eee:jaecon:v:55:y:2013:i:1:p:43-65)).
- **Open question.** No triaged paper classifies guidance changes from press-release text.

## Design defaults

- **Guidance revision first: supported.** Revisions are frequent, persistent by firm and informative to analysts (Tang note; [Hirst et al. 2008](https://api.openalex.org/works/doi:10.2308/acch.2008.22.3.315)).
- **Press releases plus 10-Q and 10-K: supported.** Guidance sits in the release (Bozanic note); the change signal is in filings (Cohen note). Omitting transcripts has a cost: calls add information beyond the release ([Matsumoto et al. 2011](https://repub.eur.nl/pub/25721)) and carry documented features ([Hassan et al. 2019](https://www.nber.org/papers/w24029); [Gow et al. 2021](https://econpapers.repec.org/RePEc:bla:joares:v:59:y:2021:i:4:p:1349-1384)).
- **Tone and confidence deferred: supported.** Tone is a weak baseline; nothing here solves single-annotator labelling.
- **Numeric anchor only: partly contradicted.** Under uncertainty firms drop numeric forecasts and say more qualitatively, so numeric-only samples under-represent firms near failure (Bozanic note).

## Gaps

- Does a model's change label add to Jaccard similarity plus dictionary tone change on the same pair?
- Change-class census by updating routine, against Tang's rates.
- Consecutive-quarter against year-over-year pairing (Cohen pairs year over year).

## Do not redo

Dictionary tone against returns; text similarity against returns; analyst reaction to guidance updates.

## Changes to the plan

1. Split announced "withdrawn" from "no longer mentioned"; add rules for temporary suspensions and quarterly-to-annual switches.
2. Define the class for a range that both narrows and shifts.
3. Stratify the test set by each firm's updating routine.
4. Let the tuple's metric cover revenue, margin and capital expenditure.
5. Add two baselines: keyword outlook rules and pair similarity.
6. If WRDS is available, check tuples against I/B/E/S Guidance.
