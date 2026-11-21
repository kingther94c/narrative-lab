# MemGuard-Alpha: Limits of Membership Inference for Detecting and Filtering Memorization-Contaminated Signals in LLM-Based Financial Forecasting

- **Citation:** Dip Roy, Rajiv Misra, Sanjay Kumar Singh and Anisha Roy (2026), as listed on the v2
  PDF; the arXiv listing names only Anisha Roy and Dip Roy. Preprint, IIT Patna and others.
  arXiv 2603.26797. v1 is dated 26 March 2026 and v2 24 September 2026. v2 reverses the central
  conclusion of v1. Version read: v2, full text.
- **Link:** https://arxiv.org/abs/2603.26797
- **Stream:** 08, blind replay (S2); triaged earlier in stream 03 from the abstract
- **Verified against source:** yes, 2026-11-19 (the arXiv abstract page for authors and dates; no
  HTML version exists, so the v2 PDF was fetched and its text extracted with the system PDF
  library; all 32 pages read: sections 1 to 9, Tables 1 to 5 and the reference list. Figures 1 to
  13 were read through their captions only. The replication package was not opened.)

## Question
Do membership-inference scores tell a memorised LLM forecast from an unmemorised one at the level of
a single signal, and does filtering signals on such a score improve a portfolio once costs are
applied to every strategy alike?

## Data
- **Models.** Seven open-weight models of 124M to 7B parameters: GPT-2 base, medium and large
  (cutoff October 2019), TinyLlama 1.1B (September 2023), Phi-2 (October 2023), Qwen2.5 3B and 7B
  Instruct (March 2024). All at full precision.
- **Prompts.** 42,800 templated prompts on 50 S&P 100 constituents, dated every fifth trading day
  from January 2019 to June 2024, in three types: price recall, sentiment and forward-looking.
  299,600 prompt-model scores.
- **Signals.** One bullish, neutral or bearish call per model, ticker and date, at temperature 0.7,
  on 277 dates (13,850 prompts per model).
- **Prices.** Yahoo Finance adjusted closes. Financial PhraseBank (pre-2016 news sentences) as a
  pre-cutoff reference corpus.
- Delisted firms: excluded. The 50 stocks were chosen by current index membership, and the authors
  name the survivorship bias.

## Method
- **Five membership-inference scores** from token log-probabilities: loss, Min-K% (K = 20),
  Min-K%++, zlib ratio, and the ratio to a reference model (GPT-2 base).
- **Composite score (MCS).** A logistic regression of in-sample status on the five scores and a
  temporal-proximity feature, the clipped distance between the model's cutoff and the prompt date.
- **Cross-model disagreement (CMMD).** For each stock and date, split the seven models at the
  median composite score into a "clean" and a "tainted" group, trade on the mean signal of the
  clean group, and record the tainted-minus-clean difference.
- **Audit of the detector**, which the authors call the substance of the paper:
  - five evaluation protocols, from scoring on the fitted rows to cross-validation within one
    model with folds grouped by calendar quarter;
  - a fixed-date test: among the models scored on the same prompt, can the scores rank the models
    that had that date in training above those that did not? Run on raw scores and after three
    within-model normalisations (z-score, rank, demeaning by model and prompt type);
  - a near-cutoff test: within one model, restrict to symmetric windows of twelve, nine, six and
    three months around its cutoff.
- **Portfolio test.** Seventeen strategies, 15 bp cost applied to all, a stationary block bootstrap
  on Sharpe differences (10,000 resamples, block length five), regressions on the Fama-French five
  factors plus momentum, a random-partition control and a minimum-detectable-effect calculation.

## Outcome variable and horizon
In-sample against out-of-sample status of a prompt for a model, defined by the model's stated
cutoff; next-day stock return for the portfolios; directional accuracy of the signals.

## Result
Empirical findings. The detection results rest on 299,600 scores; the portfolio results on 277
dates.

- **A cutoff-derived feature recovers a cutoff-defined label by arithmetic.** Temporal proximity
  alone gives ROC-AUC 1.000. Its fitted weight is +62.19 against -0.42 to +0.22 for the five
  scores, and the composite scored on its own fitted rows gives Cohen's d = 18.57. The authors do
  not count this as detection.
- **Without the temporal feature** the five scores reach AUC 0.895 under random five-fold
  cross-validation and 0.868 with folds grouped by quarter; true-positive rate at 1% false
  positives falls from 0.187 to 0.026. Loss and zlib alone, the two that an API with completion
  log-probabilities could supply, reach 0.865.
- **The scores identify the model, not the memory.** At a fixed date, over 33,300 prompt groups,
  raw scores rank in-training models with AUC 0.99 for loss and zlib, 0.86 for Min-K%++ and 0.64
  to 0.67 for the other two. After each of the three within-model normalisations the mean AUC is
  0.487 to 0.537.
- **Within one model** the AUC ranges from 0.29 to 0.93 and five of seven models are below chance.
  The exception, TinyLlama at 0.93, falls to 0.73 after detrending on time, and to 0.79, 0.72,
  0.43 and 0.38 in windows of twelve, nine, six and three months around its cutoff. Phi-2 falls
  from 0.65 to 0.15. Detection is worst where memorised and unmemorised prompts differ only in
  exposure, so the authors attribute the separation to time structure.
- **The reference corpus runs the wrong way for three models.** Loss on Financial PhraseBank is
  lower than on post-cutoff controls for the GPT-2 models and Phi-2 (d = -0.61 to -0.81) and higher
  for both Qwen models and TinyLlama (+0.79, +0.71, +0.07). The two corpora are not matched in
  style.
- **The median split degenerates.** 35% of composite scores equal exactly 1.0 in double precision;
  on 56.7% of stock-date pairs the tainted group is empty and the filter equals the unfiltered
  ensemble.
- **Portfolio (Table 4, net Sharpe).** Equal-weight buy-and-hold 0.96; all seven models unfiltered
  0.22; CMMD with the corrected rank split 0.37; CMMD as published 0.19; threshold filtering 0.30;
  dropping Qwen-7B alone 0.38. CMMD against unfiltered: bootstrap p = 0.016, paired t-test
  p = 0.114. Dropping Qwen-7B: p < 0.001 and p = 0.045. A random split of the models gives -0.02
  (sd 0.05).
- **Factor-adjusted alpha.** CMMD +3.32 bp per day (t = 0.72); unfiltered +0.86 (t = 0.28); the
  market-neutral variant -6.56 (t = -12.85).
- **Clean against tainted, where the split is not degenerate:** 9.58 against 2.01 bp per day
  (paired t = 6.57). CMMD's returns correlate 0.984 with the unfiltered ensemble.
- **Accuracy inside and outside the training window.** Within each model the gap is -0.6 to +4.7
  percentage points and none is distinguishable from zero. The pooled gap is larger because the two
  pools are made of different models (the in-sample pool is 3.4% GPT-2, the out-of-sample pool
  28.8%).
- **Power.** The paired daily difference has mean 2.2 bp and standard deviation 32.5 bp; about 862
  informative days would be needed at 80% power, against 277. The interval excludes Sharpe
  improvements above about +0.27.
- **Corrections to v1.** v1 charged costs to the baselines and not to the proposed method,
  annualised 93 dates that lie about 21 days apart as if consecutive (inflating every Sharpe ratio
  about 4.5 times), and reported a Sharpe of 4.11. The authors withdraw v1's portfolio claims.

## Look-ahead and memorisation
This is the paper's subject. Its own definition of "memorised" is a date before the model's stated
cutoff; the authors accept that this is a proxy, that some in-sample text was never in training,
and that dates near the cutoff may be mislabelled. They state that Gao et al.'s recall propensity
avoids the first failure because it is computed from the answer to a date-only recall query and
uses the cutoff only for a placebo window. They recommend evaluation design over filtering.

## What it settles for us
- **Membership-inference scores as a leakage measure: contradicted.** They also need token
  log-probabilities, which our commercial model does not give. This confirms the stream 03 line and
  gives the reasons.
- **Cross-model disagreement as a leakage measure: contradicted in this form.** Models with
  different cutoffs differ in architecture, corpus, tokeniser and tuning; the "tainted" group here
  was in practice one bearish model. A strategy that compares our PM with an older or
  point-in-time model inherits this confound.
- **Three checks to adopt for any S2 leakage measure** (the authors' cautions, restated for our
  setting; the restatement is ours):
  - never validate a measure against a label that one of its inputs defines. If "recognised" or
    "pre-cutoff" enters the measure, it cannot also be the ground truth;
  - compare within model, and normalise within model before pooling across models;
  - test the measure near the cutoff, where items differ in exposure and little else. A measure
    that separates 2019 from 2025 and fails within a few months of the cutoff is measuring drift.
- **Bounded scores and sample splits.** Check for saturation before splitting a bounded score at a
  median. Relevant if S2 thresholds an attacker confidence or a recall propensity.
- **Detection is not filtering.** A memorised signal can be right; removing it removes a correct
  call. For S2 the parallel is that dropping recognised views changes the sample, and that change
  needs its own control (our inference).
- **Costs and power.** Apply the same cost and scoring rules to every arm; compute the minimum
  detectable effect before reading a difference between arms.
- **Simple baseline first (rule 8): supported.** Dropping the weakest model beat every filter.
- **Open question.** The authors suggest comparing checkpoints of one model trained to different
  cutoffs. Nobody in this note's sources has done it.

## Limits
- Models of at most 7B parameters, three of them GPT-2; nothing on a frontier or commercial model.
- Templated one-line prompts, not disclosures; 50 large caps chosen by current membership.
- The signals are weak: no strategy has significant factor-adjusted alpha, so the filtering null is
  partly a null about the signals.
- "Memorised" is defined by date, so the paper cannot say what a correct detector would score.
- A second version that reverses the first. Section 6.5 still carries a v1 estimate (Cohen's d of
  0.2 to 0.5 for the API variant) that section 6.3 says is superseded, and the text refers to the
  composite score's section by two different numbers.
- The author list differs between the arXiv listing and the PDF.
