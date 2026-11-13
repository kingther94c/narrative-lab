# With Little Power Comes Great Responsibility

- **Citation:** Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K. and Jurafsky, D. (2020). Proceedings of EMNLP 2020, pp. 9263-9274. Version read: the ACL Anthology paper (main text) and arXiv 2010.06595v1 (appendices).
- **Link:** https://aclanthology.org/2020.emnlp-main.745/ (appendices: https://arxiv.org/abs/2010.06595)
- **Stream:** 07 statistical method
- **Verified against source:** yes, 2026-11-12 (abstract page, main text and Appendices C and E.2)

## Question

How much statistical power do typical NLP evaluations have, and how should a researcher size a
test set before comparing two models?

## Data

No disclosure text. Three bodies of evaluation data:

- GLUE: test-set predictions from 10 high-performing models, giving 270 pairwise comparisons on
  the binary-choice accuracy tasks; 119 accuracy comparisons and 57 claims of improvement
  collected by hand from 14 papers.
- SQuAD 2.0: pairwise agreement between leaderboard submissions on validation and test data.
- Human evaluation: a survey of EMNLP 2019 papers; machine translation test sets for BLEU.

Delisting is not applicable.

## Method

- Power is estimated by simulation: define a generative process, draw many data sets, run the
  planned test on each, and count the share that reject with the right sign (their Figure 2).
- For accuracy on paired data the test is McNemar's, which uses only the items where the two
  models disagree. The simulation needs two inputs: the accuracy difference and the agreement
  rate P_a (share of items on which both models are right or both are wrong).
- Three ways to get those inputs: paired predictions on validation data; a regression on
  historical results; a default prior when nothing else is available.
- Minimum detectable effects use the exact unconditional version of McNemar's test (Suissa and
  Shuster 1991), with a normal approximation for the largest data set.

## Outcome variable and horizon

Power, and the minimum detectable accuracy difference at 80% power and alpha 0.05. No horizon.

## Result

- Empirical finding: agreement between models is predictable. On GLUE,
  `overlap = 0.41 + 0.58 * min_acc - 0.47 * acc_diff` (their equation 2; 270 comparisons,
  R-squared 0.966; coefficient standard errors 0.019, 0.021 and 0.028).
- Empirical finding: agreement and accuracy differences on validation data predict those on
  test data almost exactly (r = 0.99 for both, SQuAD 2.0).
- Empirical finding: the minimum detectable effect is 5.26 points on WNLI (147 items), 1.62 on
  MRPC (1,725) and 1.02 on SST-2 (1,821), while the mean reported improvements on those tasks
  are 1.72, 0.63 and 0.57. Only 46% of the surveyed comparisons would have had adequate power.
- Worked example (their Appendix C): 500 items, a 2-point difference and 90% agreement. They
  report power of about a quarter; the normal approximation I ran gives 0.29.
- Empirical finding: test sets of 2,000 sentences have about 75% power to detect 1 BLEU point.
- Convention they recommend: run the power analysis before the evaluation, and size a new
  test set from the minimum detectable effect.

## Look-ahead and memorisation

Not addressed. The paper only notes that validation results are a fair guide to test results if
validation performance was not inflated by training on the validation data.

## What it settles for us

- Supports the paired comparison default. With disagreement rate psi = 1 - P_a and accuracy
  difference delta, the normal approximation is n = (z_alpha/2 + z_beta)^2 * psi / delta^2.
  At psi = 0.15 and delta = 0.05 this is 471; the plan says about 470.
- Supports psi = 0.15 as a starting value, conditionally. Their regression gives a
  disagreement rate of 0.150 when the weaker system is at 80% accuracy and the gap is 5 points,
  0.178 at 75% and 0.208 at 70%. A 17-point gap from a 75% base (the size of the local versus
  commercial gap in the 150-question screening) gives 0.235.
- Supports taking psi from the headroom pilot. A 100-pair pilot estimates psi = 0.15 only
  to within 0.08 to 0.22, which puts the required n between 250 and 690.
- Reusable: the simulation recipe and the authors' notebooks (linked from the paper).

## Limits

- The agreement regression comes from fine-tuned models of similar architecture on binary
  tasks, mostly above 90% accuracy. The authors say the outcomes "are biased toward a higher
  range of accuracy values and may not be a perfect prior". Applying it to a six-class task at
  75 to 80% accuracy, or to factorial cells that differ by design (no retrieval versus the
  correct passage supplied), is extrapolation.
- One contrast at a time: no multiplicity correction and no clustering of items.
- Nothing on non-inferiority or on interactions.
