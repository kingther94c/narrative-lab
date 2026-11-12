# Master methodology

**Status, 2026-11-12.** No method has been validated yet. What follows are the constraints the
programme adopted at its start, from the plan approved on 2026-11-12. They are rules of the road,
not findings. Design choices that are still hypotheses live in `01_roadmap.md` under "Design
defaults" until Phase 0 confirms or replaces them.

## 1. What may be claimed

| Level | Question | Standing |
|---|---|---|
| L1 extraction | Does the system read the document correctly? | Confirmatory |
| L2 economic interpretation | Does the extracted change line up with realised fundamentals? | Only where a numeric anchor exists, such as a stated direction checked against as-filed figures |
| L3 investment prediction | Does it predict returns or failure events? | Exploratory |

Why L3 is exploratory: with a monthly information coefficient of 0.02 and a standard deviation of
0.10, a t-statistic of 2 needs about 100 clean months, (2 × 0.10 / 0.02)², and the clean window
grows by 12 months a year. Hard failure events are rare: fifty clean events put an AUC interval at
roughly ±0.08.

## 2. Point-in-time protocol

- The only clock is the SEC EDGAR acceptance timestamp. Indexes, retrieval and tools filter on it.
- Fundamentals are the values first filed, not restated ones.
- Evaluated models get no web access. Their inputs come from the frozen corpus.
- The evaluation roster records, for each model, the repo and revision (open weights) or the model
  ID (commercial), the release date, and the knowledge cutoff the vendor states.
- A vendor's stated cutoff is not exact. Use a buffer and the memorisation probe.

## 3. Contamination labels

Every reported result carries exactly one.

| Label | Meaning | What it supports |
|---|---|---|
| Clean | Documents dated after every roster model's cutoff, or counterfactually edited so the label is known by construction | Confirmatory claims |
| Bounded | Pre-cutoff documents where the supplied text fixes the label | Reported with the memorisation gap; recall still inflates accuracy and favours large models |
| Contaminated | Pre-cutoff tasks whose label depends on later information | An upper bound only |
| Prospective | Forecasts sealed before the outcome exists | Clean, small, descriptive |

Masking is not a route to "clean". In ResearchOS all 15 large-cap cases stayed identifiable after
redaction, and the literature reports the same for masked earnings call transcripts.

## 4. Splits

- Test: documents dated after every roster model's cutoff. As of 2026-11-12 that is after
  2026-06-30.
- Training and development: earlier documents, from companies that do not appear in the test set.
- Adding a model with a later cutoff to the roster moves the test boundary for that model's
  results.

## 5. Gold labels

- Labels are anchored in numbers or filings and checked by the owner.
- No model on the evaluation roster annotates or pre-annotates test items.
- With one annotator, reliability is test-retest: the same items labelled twice, 14 days apart.
- Gold test labels stay out of git. A published test set becomes training data for later models.

## 6. Comparing systems

- Compare paired, on the same items. For a 5-point accuracy difference at 80% power, when two
  systems disagree on 15% of items, about 470 items are needed; about 800 after correcting for ten
  contrasts.
- Intervals come from resampling. Cluster by company, and by quarter for panels.
- Each method being compared gets the same development set and the same number of development
  evaluations. Configurations are frozen before the test run.
- Estimate interactions between methods on the logit scale and by difficulty stratum. On the
  accuracy scale a ceiling makes two helpful methods look like substitutes.
- "Matches" is a non-inferiority claim against a margin set in advance, not a failure to find a
  difference.
- A rule-based baseline is run first and sets the bar.

## 7. Pre-registration

An experiment's hypothesis, sample, criteria with numeric thresholds, and random seed are written
into `experiment_registry.md` and committed before the run. The verdict cites that commit. A
refutation is a publishable outcome.

## 8. Not claimable

- That masking, open weights or point-in-time retrieval remove look-ahead.
- That results on pre-cutoff documents measure reading and not recall.
- That a subset of companies a model failed to recognise is representative. It skews to obscure
  firms.
