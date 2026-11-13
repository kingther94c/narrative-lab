# Stream 07: statistical method

ψ: share of items where two systems disagree; δ: their accuracy difference. Notes: `../papers/`.

## Re-derivation

1. **470 items: holds asymptotically.** n = (z₀.₉₇₅+z₀.₈)²ψ/δ² = 7.85×0.15/0.0025 = 471. The exact McNemar test needs about 500; ψ = 0.25 needs 785.
2. **800 for ten contrasts: holds** (α = 0.005 gives 799).
3. **100 months: arithmetic holds, at 52% power.** T = (t·σ/IC)². 80% power needs 196 months; t = 3 needs 225, or 369 at 80% power.
4. **AUC ±0.08: holds.** SE² ≈ (2A²/(1+A) − A²)/events when non-events dominate: ±0.074 to ±0.083 for A between 0.5 and 0.8 (simulation: ±0.071).
5. **κ ≥ 0.8: noisy gate.** Six classes, 100 items: SD(κ̂) ≈ 0.045, so a true κ of 0.79 passes 45% of the time. At 30 items: ±0.2 to ±0.3.
6. **Logit scale: half right.** Two methods each adding one logit to a 0.80 base give 0.916, then 0.967: an accuracy-scale interaction of −0.064 from none. Pooling easy and hard items creates a spurious logit interaction of +0.10.
7. **Non-inferiority:** n = (z₀.₉₇₅+z₀.₈)²(ψ−d²)/(0.05−d)² for a true shortfall d. Shortfall 0: 471; 2 points: 1,305. At 800 items power is 0.95, 0.83 and 0.59 for shortfalls of 0, 1 and 2 points.

## What the stream establishes

- Empirical finding: model agreement ≈ 0.41 + 0.58·(lower accuracy) − 0.47δ, so ψ = 0.15 at 80% accuracy, 0.18 at 75%. [card-2020-little-power]
- Empirical finding: across 316 factors the hurdle is t > 3.0; a real out-of-sample test needs future data. [nber.org/papers/w20592]
- Verified fact: prediction-powered intervals are valid for any predictor; they help only when the unlabelled pool far exceeds the labelled set. [angelopoulos-2023-prediction-powered-inference]
- Empirical finding: plug-in regressions on LLM labels are biased; 125 to 250 random validation labels restore coverage. Closed models are not leakage-free by design. [ludwig-2025-llm-econometric-framework]
- Empirical finding: two-way clustered tests over-reject with ten clusters. [nber.org/papers/t0327]
- Convention: κ above 0.8; reproducibility needs independent coders. [aclanthology.org/J08-4004]
- Convention: non-inferiority is an interval against a preset limit. [pubmed 11782062]
- Convention: preregistration needs an independent time stamp. [aclanthology.org/2021.naacl-main.51]
- Open question: preregistration practice in empirical finance (not reached).

## Design defaults

- Paired comparison (470, 800) and size (500 to 800): supported if ψ ≤ 0.15 and the ten contrasts are named; contradicted at ψ ≥ 0.25.
- L3 exploratory: supported.
- Test-retest κ ≥ 0.8: threshold supported; single-annotator stability not addressed; 30 items contradicted.
- Cluster by company: supported. By quarter: contradicted for a two-to-four-quarter test window.
- Logit-scale interactions: not addressed.
- Non-inferiority: method supported; margin size not addressed.
- Git-commit registration: supported in principle; a local commit is not independent.
- Clean label for commercial models: contradicted in part.

## Can prediction-powered inference cut labelling?

Hypothesis: by 20 to 35%. With an annotator right on 80 to 90% of disputed items and a clean pool four times the gold set, I compute 1.4 to 2.0 times the effective sample; reported gains are 20 to 50% [arxiv.org/abs/2403.07008]. Conditions: gold items randomly sampled from the pool; a non-roster annotator; every cell also run on the pool. Phase III regressions need it regardless.

## Changes to the plan

1. Size the test set from the pilot's ψ; 100 pairs only bound n between 250 and 690.
2. Name the confirmatory contrasts; use Holm.
3. Gate reliability on the interval; label 100 narrative pairs.
4. Treat quarter as a stratum.
5. Fit interactions with an item-level mixed logit.
6. State non-inferiority power at realistic shortfalls.
7. Budget 125 to 250 random validation labels for Phase III.
8. Push or externally time-stamp registrations.
