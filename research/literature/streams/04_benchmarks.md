# Stream 04: financial NLP benchmarks and data sets

Twelve items triaged, three read in full; all checked on 2026-11-12. Notes:
`../papers/aavang-2026-kpi-extraction-earnings-calls.md`,
`../papers/ju-2023-final-year-to-year-signals.md`,
`../papers/jiang-2026-rfc-bench-counterfactual-pairs.md`. Other rows: `04_benchmarks.csv`.

## What the stream establishes

1. **No public benchmark labels guidance revisions across consecutive quarters** (hypothesis, not
   refuted). Searched ACL Anthology, arXiv, SSRN and Hugging Face. Nearest misses: Finance Agent
   Benchmark, 69 of 537 questions on guidance against actuals, 50 public
   (https://arxiv.org/abs/2508.00828); EDT, one "Guidance Increase" label on 99 press-wire
   articles (https://arxiv.org/abs/2105.12825); FinBen, 24 tasks, none on guidance
   (https://arxiv.org/abs/2402.12659).
2. **Change between consecutive disclosures has one human-labelled set** (empirical finding):
   FINAL, 400 pairs of 10-K MD&A segments with word highlights and no change class (Ju note).
   Fin-RATE's longitudinal track is annual and LLM-generated (https://arxiv.org/abs/2602.07294).
3. **Minimal pairs exist, for news only** (verified fact): RFC-BENCH, 1,826 pairs. Models score
   45 to 54% on a single paragraph and up to 97.7% when shown both; an 8B model reaches 57.5%
   (empirical finding; Jiang note).
4. **Labelling practice** (convention): two or three annotators with kappa 0.60 to 0.72 (Ju,
   Jiang notes); one expert in two passes, no retest statistic, 18 to 32% of sampled "errors"
   valid (Aavang note); LLM-assigned gold with thin human
   checks (https://arxiv.org/abs/2510.23464); rules reaching F1 0.93 against human gold
   (https://arxiv.org/abs/2402.11728).

## Design defaults

| Default | Verdict | Why |
|---|---|---|
| Benchmark v0, three sub-tasks | Supported | Tuple schema (Aavang) and pair construction (Jiang) have precedents; the change classification is new |
| 500 to 800 gold pairs | Supported, as convention | 537 questions (Finance Agent), 400 pairs (FINAL), 587 chunks (ECB-A) |
| Rule labels, one human, test-retest | Partly supported | Rule labels alone trailed zero-shot (Ju). One human: one precedent, listed by its authors as a limitation. Nobody reports test-retest |
| No existing guidance-revision benchmark | Supported | Point 1 |

## Reusable

- Aavang: guidelines, tuple schema, value matching within 1% (MIT card).
- Numerical-claim earnings-call set (CC BY 4.0): baseline for forward-looking numeric sentences.
- RFC-BENCH constraint lists and two-question validity check (MIT card).
- FINAL's two-score rule for aligning passages (no licence stated).
- Finance Agent's 50 public questions (CC BY 4.0): smoke test.

## Gaps that suggest an experiment

- Label consistency under numbers-only against wording-only edits of disclosures: untested.
- Test-retest agreement of one annotator: unreported; the pilot can supply it.
- Rule-against-human agreement on the change class; qualitative guidance has no precedent.

## Changes to the plan

- Add unedited control pairs and report a false-positive rate: nine of fourteen runs flagged 95
  to 100% of clean statements (https://arxiv.org/abs/2605.29586, abstract only).
- Present pair members separately; score consistency afterwards.
- Pre-register how invalid outputs count; they drive small-model failure (Jiang).
- Expect to lose a fifth of wording-only pairs in checking (Jiang).
- Adjudicate a sample of unmatched extractions; single-annotator gold is partial (Aavang).
- Report raw agreement and AC1 beside kappa; "maintained" will dominate.

Not triaged (cap of twelve): seeds FinQA, ECTSum, FiNER-139, EDGAR-CORPUS. Nothing is claimed
from them.
