# A Compare-and-contrast Multistage Pipeline for Uncovering Financial Signals in Financial Reports

- **Citation:** Ju, J.-H., Huang, Y.-S., Lin, C.-W., Lin, C., and Wang, C.-J. (2023). Proceedings of the 61st Annual Meeting of the ACL, Volume 1: Long Papers, pp. 14307–14321. Version read: the ACL Anthology PDF (full text, including appendices A to E).
- **Link:** https://aclanthology.org/2023.acl-long.800/ (data and code: https://github.com/cnclabs/codes.fin.highlight)
- **Stream:** 04 Financial NLP benchmarks and data sets
- **Verified against source:** yes, 2026-11-12

## Question

Annual reports repeat most of last year's text. Can the previous year's report serve as a reference
for finding what is new in this year's, and which words carry the change?

## Data

- Text source: Form 10-K filings from the Notre Dame Software Repository for Accounting and
  Finance, 2011 to 2018: 63,336 filings from 12,960 companies. Item 7 (MD&A) only.
- Sample: companies with a report missing in any of the eight years are dropped, leaving 3,849;
  200 of these are sampled at random, giving 1,400 pairs of consecutive-year documents. Firms that
  delisted or listed inside the window are excluded by this filter.
- The paper reports a mean token overlap of about 0.826 between adjacent-year MD&A sections of the
  3,849 companies.
- FINAL data set: 30,000 pseudo-labelled "revised" segment pairs for training; 200 revised and 200
  "mismatched" pairs with human labels for evaluation.
- Licence: none stated. The repository has no licence file and its README still describes it as a
  temporary anonymous repository for review.

## Method

- Segmentation: sentences are split and grouped into segments of one to three sentences.
- Pairing: each target segment is matched to prior-year segments by ROUGE-2, keeping those above
  the largest gap in the ranked scores (usually one to five).
- Pair type, by rule: syntactic similarity is ROUGE-2 and semantic similarity is Sentence-BERT
  cosine. Thresholds are 0.6296 and 0.9011, the medians of each score over the candidate pairs.
  High on both is "insignificant"; high syntactic and low semantic is "revised" (a few words differ
  and the meaning changes); low syntactic is "mismatched".
- Pseudo-labels for training: in a revised pair, every word that changed in the target is positive;
  three times as many other words are sampled as negatives.
- Human labels: three annotators per pair mark the words in the target that are important given the
  reference. Annotators were graduate students in accounting or related fields. The guidelines
  have four rules: changed numbers or objects; opposed descriptions (increased against decreased);
  mark only high-confidence words; new information relative to the reference.
- Agreement: Fleiss' kappa over roughly 12K word-level decisions is 0.71 on revised pairs and 0.60
  on mismatched pairs.
- Model: BERT-base token classifier, warmed up on the contradiction pairs of e-SNLI (183,160
  training pairs), then fine-tuned on the pseudo-labels with soft labels from the warm-up model.

## Outcome variable and horizon

Word-level highlighting quality on the 400 annotated pairs: R-precision against the majority vote
of the three annotators, and Pearson correlation against their mean. No market outcome and no
horizon.

## Result

All four are empirical findings on the union of the two evaluation sets.

- Zero-shot (e-SNLI only): R-Prec 0.7469, PCC 0.6067.
- Pseudo-labels only: 0.6968 and 0.6368. With warm-up plus pseudo-labels: 0.7160 and 0.6555.
- Warm-up plus pseudo-labels plus soft labels: 0.7865 and 0.7290, significant against zero-shot
  (paired t-test, p < 0.05; no interval reported).
- The reference matters: with an empty reference R-Prec falls to 0.4834, with a random segment to
  0.5345. Adding the Loughran-McDonald sentiment words as positives makes results worse (0.6457).
- Domain adaptation helps mismatched pairs more than revised pairs (a PCC gain of about 23% on
  mismatched pairs).

## Look-ahead and memorisation

Not addressed. The models are BERT-base; no LLM is evaluated and no market outcome is predicted.

## What it settles for us

- **Unit of analysis (supports).** A pair of aligned passages from one company's consecutive
  documents is an established unit, and the aligned pairs can be found by rule.
- **Gold labels computed by rule (partly supports, partly warns).** Rule-derived labels on
  near-identical pairs are usable for training, but on their own they did worse than a zero-shot
  model trained on human labels from another domain (0.7160 against 0.7469); they helped only once
  softened. Our rule labels are class labels computed from numbers, which is a different and
  stricter rule, but the pilot should still measure rule-against-human agreement and not assume it.
- **Agreement by pair type (convention to carry over).** Humans agree more on edit-like pairs
  (kappa 0.71) than on pairs where the text was rewritten (0.60). Expect the same split between
  numeric guidance and qualitative guidance, and stratify the agreement report.
- **Hypothesis that no benchmark labels guidance revisions (not refuted).** FINAL is the closest
  public data set for change between consecutive disclosures, but it covers annual MD&A, labels
  important words and not a change class, and has nothing on guidance or on quarterly documents.
- Reuse: the two-score rule for typing pairs (to pre-align outlook passages and to flag boilerplate
  pairs); the four-rule annotation guideline; the 400 annotated pairs as an out-of-domain probe.
  The missing licence must be cleared before any redistribution.

## Limits

- Annual reports only; survivors only; 200 companies.
- Labels are word importance, not a class, so the data cannot train or score a change classifier.
- Thresholds are sample medians, so half of the candidate pairs are "mismatched" by construction.
- Annotators were students, chosen deliberately so that only the report text informed the labels.
- Only the target side is highlighted; no LLM baseline; English only.
