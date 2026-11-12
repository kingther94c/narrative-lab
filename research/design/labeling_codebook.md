# Labelling codebook

Status: not started. Work package 4 of Phase 0; the plan is in
[`../registry/01_roadmap.md`](../registry/01_roadmap.md).

No model on the evaluation roster labels or pre-labels test items. Label files are kept outside
git.

## To define

1. The item: a pair of outlook passages from one company's consecutive earnings press releases.
2. The guidance tuple: metric, period, low, high, basis (GAAP or non-GAAP, constant currency and
   so on).
3. The change class: raised, maintained, lowered, narrowed, withdrawn or no longer mentioned,
   initiated. The class is computed from the tuples by rule; the annotator checks it.
4. Qualitative guidance, such as "toward the low end of the range": how it is recorded.
5. Edge cases: a changed metric definition, a changed fiscal period, a pre-announcement between
   quarters.
6. The pilot: 100 guidance pairs and 30 narrative-change pairs, each labelled twice, 14 days
   apart.
7. Agreement: how test-retest kappa and rule-versus-human agreement are computed, and the
   thresholds.
