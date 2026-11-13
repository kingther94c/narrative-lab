# Prediction-Powered Inference

- **Citation:** Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I. and Zrnic, T. (2023). arXiv:2301.09633. Version read: v4, 9 November 2023. Secondary sources report a journal version in Science (2023); that page was not opened.
- **Link:** https://arxiv.org/abs/2301.09633
- **Stream:** 07 statistical method
- **Verified against source:** yes, 2026-11-12 (abstract, sections 1 to 3, Table 2, Appendix G.1)

## Question

Given a few gold-standard labels and many machine predictions, how can one build confidence
intervals that are valid whatever the quality of the predictor, and narrower than those from
the gold labels alone when the predictor is good?

## Data

No disclosure text. Six applications: protein structure (AlphaFold predictions), galaxy
morphology (Galaxy Zoo 2), gene expression, Amazon deforestation (1,596 gold labels), and two
census analyses (health insurance, income). Delisting is not applicable.

## Method

- Setting: n labelled pairs (X, Y), N unlabelled X with N much larger than n, and a prediction
  rule f that is independent of both samples.
- The naive estimate treats predictions as labels. The "rectifier" is the average prediction
  error measured on the labelled sample, and it is subtracted.
- For a mean: `theta_PP = mean_N f(X) - mean_n (f(X) - Y)`, with 95% interval
  `theta_PP +/- 1.96 * sqrt(var(f - Y)/n + var(f)/N)`. The classical interval is
  `mean_n Y +/- 1.96 * sqrt(var(Y)/n)`.
- The same construction is given for quantiles and for linear and logistic regression
  coefficients, with extensions to covariate shift (known density ratio), label shift and
  finite populations.

## Outcome variable and horizon

Interval width, and the number of labelled examples needed to reject a stated null at the 95%
level. No horizon.

## Result

- Verified fact (their claim, proved in the paper): the intervals are valid "without making any
  assumptions on the machine-learning algorithm that supplies the predictions". The labelled
  and unlabelled samples are assumed to be i.i.d. draws from one distribution.
- Empirical finding (their Table 2), labelled examples needed, prediction-powered versus
  classical: 316 versus 799 (proteomics); 189 versus 449 (galaxies); 764 versus 900 (gene
  expression); 21 versus 35 (deforestation); 5,569 versus 6,653 (health insurance); 177 versus
  282 (income). The saving ranges from 15% to 60%.
- Empirical finding: treating predictions as labels gave intervals that missed the true value
  in every application.
- Verified fact (Appendix G.1): the method is not always better. The interval is tighter only
  if `var(f)/N + var(f - Y)/n < var(Y)/n`. In their words, "if N is about n one should not
  expect prediction-powered inference to help". For a binary outcome with prevalence 0.5 the
  predictor's error rate must be under 25%; with prevalence 0.1, under about 9.5%.

## Look-ahead and memorisation

Not addressed. One consequence follows from the validity result (my inference, not the
paper's): a predictor that has memorised some labels cannot bias the estimate, because the
rectifier is measured on gold labels. It can only change how much precision is gained.

## What it settles for us

- Gold labels. The method could cut human labelling for accuracy estimates, under conditions.
  Applying their Appendix G.1 formula to a correctness indicator with mean 0.8: the plain
  estimator helps only if the model-based correctness indicator is wrong on fewer than about
  17% of items.
- My calculation for a paired accuracy difference (psi = 0.15, delta = 0.05), using the
  variance-minimising weight on the prediction term (the tuned variant applied in Boyeau et al.
  2024, arXiv 2403.07008): effective sample size is multiplied by `1 / (1 - rho^2 * N/(N+n))`,
  where rho is the correlation between the gold-based and annotator-based per-item difference.
  If the annotator is right on 80% of the items where the two systems disagree and N = 4n, the
  multiplier is 1.4 in the worst case (a wrong annotator sides with the other system); at 90%
  it is 2.0; at 70% it is 1.15.
- Conditions the design would have to meet: the gold items are a random sample of the same
  clean pool as the unlabelled items (or have known sampling weights, which matters if hard
  strata are over-sampled); the annotator is fixed in advance and is not a roster model, per
  `00_master_methodology.md` section 5; every evaluated system is also run on the unlabelled
  pool, which multiplies inference by about (N + n)/n.
- Phase III. When extracted labels become variables in L2 or L3 regressions on the full
  sample, this is the method (or the debiasing in `ludwig-2025-llm-econometric-framework.md`)
  that keeps the intervals valid.
- Reusable: the authors' Python package `ppi_py` (named in Boyeau et al. 2024).

## Limits

- Main results are asymptotic and for convex estimation problems. The non-asymptotic versions
  need bounded outcomes.
- Gains need N much larger than n. The clean, post-cutoff pool in this project is finite: two
  earnings seasons as of 2026-11-12.
- The basic estimator can be worse than the classical one with a weak predictor.
- Label-shift intervals are conservative and depend on the rarest class. This matters for a
  six-class change label with rare classes.
- No treatment of clustered samples.
