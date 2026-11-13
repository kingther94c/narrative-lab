# Large Language Models: An Applied Econometric Framework

- **Citation:** Ludwig, J., Mullainathan, S. and Rambachan, A. (2025). arXiv:2412.07031 (econ.EM), first posted 9 December 2024; also listed as NBER Working Paper 33344 (NBER page not opened). Version read: arXiv v4, 5 December 2025, HTML.
- **Link:** https://arxiv.org/abs/2412.07031
- **Stream:** 07 statistical method (also relevant to stream 03, look-ahead and memorisation)
- **Verified against source:** yes, 2026-11-12 (abstract, sections 3.2, 3.3, 4.2 to 4.4 and 6). The Table 3 figures below were taken from an automated read of the HTML table and were not re-checked digit by digit.

## Question

Under what conditions does using an LLM in empirical economics give valid conclusions, when
the LLM is used (a) to predict outcomes from text and (b) to measure a concept in text for a
downstream regression?

## Data

- Financial news headlines: a public data set of nearly 4 million headlines for 6,000 listed
  companies, 2009 to 2020. The applications use headlines from 2019 (10,000 sampled for the
  memorisation test). Returns 1, 5 and 10 days after publication. Whether delisted firms are
  included is not stated in the passages read.
- Congressional bills: 10,000 bill descriptions with an existing 20-category topic label,
  sponsor party, chamber and an ideology score.
- Models: GPT-3.5-Turbo, GPT-4o, GPT-4o-mini, GPT-5-mini, GPT-5-nano; nine prompt variants per
  model for the headline labels.

## Method

- Prediction problems: a decomposition in which the estimate of predictive performance is
  biased by "training leakage", the overlap between the LLM's training data and the
  researcher's evaluation sample.
- Leakage test: give the model half of a text and ask it to complete the rest; count exact
  reproductions, with and without a prompt that restricts the model to information before a
  date.
- Estimation problems: the LLM label replaces an existing measurement in a regression. The
  plug-in coefficient is biased by the covariance of the LLM's error with the regressors.
- Remedy: label a random subset with the existing procedure (the validation sample), regress
  the LLM's error on the covariates there, and subtract:
  `beta_debiased = beta_plugin - lambda_hat` (their equation 14). Inference by bootstrapping
  both samples.
- Monte Carlo on the bills: 5,000 bills per draw, 250 of them validated, 1,000 draws;
  validation shares from 2.5% (125 bills) to 50% in an appendix.

## Outcome variable and horizon

Headline application: stock returns 1, 5 and 10 days after the headline. Bills: topic label;
passage in each chamber for the prediction exercise.

## Result

- Empirical finding: GPT-4o reproduced 60 of 10,000 headlines exactly from half their text,
  and 344 bill descriptions. With a date-restriction prompt it still reproduced 330 bills and
  73 headlines. The authors conclude that prompt instructions to ignore later information "are
  not reliable solutions to training leakage".
- Verified fact (their argument): if a model's weights were published on a date and the
  evaluation documents were published after it, leakage is zero by construction. "Closed
  models like the GPT family from OpenAI or the Claude family from Anthropic do not permit this
  solution", because the training data is undisclosed and the models may be updated.
- Empirical finding: plug-in regression estimates change with the model and the prompt;
  "different prompts and models can even yield estimates with different signs".
- Empirical finding (Monte Carlo, their Table 3, see the caveat above): 95% intervals around
  plug-in coefficients cover the target in a median 78% to 92% of draws depending on the
  model, and as little as 38% at the fifth percentile of specifications. Debiased coefficients
  cover in about 93% at the median and at least 90% at the fifth percentile.
- Empirical finding: the validation-only estimator always had higher mean squared error than
  the debiased estimator, so the LLM labels add precision once corrected.
- Empirical finding: "validation samples with as few as 125-250 text pieces provided
  substantial benefits in terms of bias and coverage". The right size is a cost and precision
  trade-off, to be set like a survey sample size.

## Look-ahead and memorisation

This is the paper's first condition. Leakage is defined against the evaluation sample, shown
by verbatim completion, and not removed by date-restriction prompts. The design remedy is
open weights (or time-stamped training data) with documents dated after the weights. Closed
models are discouraged for prediction problems.

## What it settles for us

- Supports "time, not masking" and the post-cutoff test split.
- Contradicts, in part, treating a commercial model's results on post-cutoff documents as
  clean by design. For the open-weight roster, clean can be tied to the date the weights were
  published, which is a checkable fact. For commercial models it rests on the vendor's stated
  cutoff and on the snapshot not changing, which is an assumption. The methodology already
  asks for a buffer and a memorisation probe; the label should say which kind of clean it is.
  Stream 03 owns this decision.
- Adds a requirement for Phase III. When the best configuration is scaled to the full sample
  and its labels enter L2 or L3 regressions, plug-in estimates are not valid. A random
  validation sample from the same population is needed, on the order of 125 to 250 labelled
  pairs. The clean gold test set cannot serve, because it is not a random sample of the
  full-period population.
- Supports reporting results across prompts: sensitivity to the prompt is a symptom of
  measurement error, not a nuisance to be tuned away.
- Reusable: the completion test as a memorisation probe for feasibility probe 4.

## Limits

- Two applications. The Monte Carlo is on Congressional bills, not on financial text.
- The existing human or archival label is treated as the target; error in that label is not
  modelled. With one annotator, this is exactly what the test-retest check has to cover.
- The pedagogical case is linear regression with the LLM label as the dependent variable (the
  covariate case is in an appendix).
- No guidance on clustered samples or on multiple testing.
