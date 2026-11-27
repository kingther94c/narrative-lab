# Gap analysis

Work package 1 of Phase 0, first pass, 2026-11-13. Built from the seven stream syntheses in
`streams/` and the notes in `papers/`. The evidence matrix is `matrix.csv`.

## What was read

- 86 papers and data sets triaged across seven streams; 22 have a deep note in `papers/`.
- 82 rows were checked against the source. Four could not be opened and carry no claim: Chen,
  Kelly and Xiu 2022; Sarkar 2024 (StoriesLM); Çağlayan et al. 2025 (IEEE 11207079); Altman 1968.
- Spot check, 2026-11-13: five verified rows drawn at random (seed 20261113) were re-opened. All
  five matched their source. One wording was loose and is corrected in `streams/02_llm_signals.md`:
  the Lopez-Lira and Tang Sharpe ratio of 1.22 is for January to May 2024, not for 2024.

## Gaps and the experiments they suggest

| Gap | Evidence that it is a gap | Candidate experiment |
|---|---|---|
| No public benchmark labels guidance revisions across consecutive quarters | Stream 04 searched ACL Anthology, arXiv, SSRN and Hugging Face to refute this and could not. Nearest: Finance Agent Benchmark (69 of 537 questions on guidance against actuals), EDT (one "Guidance Increase" label on 99 articles), FinBen (24 tasks, none on guidance) | Benchmark v0 |
| No study scores LLM extraction of guidance tuples or revision classes against gold labels | Stream 02: four targeted searches. Studies validate by downstream association, not against labels. The one exception found, de Kok 2025 on non-answers, was read from its abstract only | Benchmark v0, sub-tasks 1 and 2 |
| No head-to-head of prompting, retrieval, fine-tuning and tools on financial narrative tasks, small open-weight against commercial | Stream 05 could not refute it. Nearest cover one or two factors: Phogat 2024, FinanceBench, FinLoRA 2025. One candidate (IEEE 11207079) could not be opened | The Phase II factorial, with intervals |
| Whether recall of pre-cutoff facts inflates accuracy on an extraction task | Stream 03: the literature tests forecasting, not extraction | Regress open-book extraction correctness on closed-book recall propensity, item by item |
| Label consistency under numbers-only against wording-only edits of disclosures | Stream 04: minimal pairs exist for news only (RFC-BENCH) | Benchmark v0, sub-task 3 |
| Test-retest agreement of a single annotator | Stream 04: nobody reports it; one precedent for single-expert gold lists it as a limitation | The labelling pilot |
| Does a model's change label add to text similarity plus dictionary tone change on the same pair | Stream 01: Lazy Prices shows similarity and tone change already carry signal | Two extra baselines in Phase I |
| An LLM-extracted signal against the eight-variable hazard model for failure | Stream 06: no paper read tests it | Exploratory, Phase III |
| Text evidence on distress comes from 10-Ks; earnings press releases are untested | Stream 06 | Exploratory, Phase III |
| Joint against separate extraction of features, scored on accuracy | Stream 02: single-question prompts are usual; nobody compares | A secondary experiment after the factorial |

## Already answered: do not redo

| Question | Answered by | What we take from it |
|---|---|---|
| Does dictionary tone predict returns | Loughran and McDonald 2011: R² near 2.5%, no significant long-short alpha | Tone level is a weak baseline, not a target |
| Does change in disclosure text predict returns | Cohen, Malloy and Nguyen 2020: five-factor alpha 0.34 to 0.51% a month, incremental to tone change | Changes carry more than levels; pair similarity is a baseline to beat |
| Do analysts react to guidance updates | Tang, Yao and Zarowin; Hirst et al. 2008 | Guidance revisions are frequent and informative; no need to show it again |
| Dictionary against transformer on sentence sentiment | Huang, Wang and Yang 2023; Bisharat and Hean 2026: an open-weight model ties FinBERT and a commercial model at 92 to 94% | Sentence sentiment is at ceiling and separates no systems |
| Does headline sentiment predict next-day returns | Lopez-Lira and Tang: Sharpe ratio fell from 6.54 (2021Q4) to 1.22 (January to May 2024); unprofitable at 20 bp | Not a contribution; shows decay |
| Does masking remove look-ahead | Lopez-Lira, Tang and Zhu 2025; Wu et al. 2025: 31 to 70% of transcripts re-identified; masking removes signal even after the cutoff | No masking |
| Fine-tuning against in-context learning at equal model size | Mosbach et al. 2023: alike once model and examples are equal | Earlier verdicts were confounded by size and checkpoint selection |

## Design defaults against the literature

One row per default in `../registry/01_roadmap.md`. "Feasibility" refers to
`../design/feasibility.md`; "audit" to `../design/data_audit.md`.

| Default | Verdict | Notes cited |
|---|---|---|
| Text source: EDGAR press releases plus 10-Q and 10-K; transcripts a private second layer | Supported, at a stated cost | Guidance sits in the release (Bozanic 2018); the change signal is in filings (Cohen 2020). Calls add information beyond the release (Matsumoto et al. 2011). The audit finds the Hugging Face transcript set unusable for clean tests or a failure sample |
| Benchmark v0: guidance revision, three sub-tasks | Supported, with changes to the label scheme | Tang 2025; Aavang 2026 (tuple schema); Jiang 2026 (pair construction). Changes: see the next section |
| Numeric anchor as the route to L2 | Partly contradicted | Numeric EPS forecasts are about 5% of forward-looking sentences and an I/B/E/S forecast sits in 37% of releases; under uncertainty firms drop numeric forecasts and say more in words (Bozanic 2018). A numeric-only sample under-represents firms near failure |
| Unit: pairs of outlook passages | Not addressed directly | Forecasts are sparse in releases (Li 2024, Jha 2024), which favours passages. Feasibility shows whole documents also fit |
| Size: 500 to 800 gold test pairs | Supported if two systems disagree on at most 15% of items | Card et al. 2020 give 15% at 80% accuracy; at 25% a single contrast needs 785. Precedents: 537 questions, 400 pairs, 587 chunks (stream 04) |
| Splits: test after every cutoff; training earlier and company-disjoint | First part supported; second part not addressed | Lopez-Lira 2025; Gao 2025 |
| Gold labels: rule-computed, one human, test-retest | Partly supported | Rules reach F1 0.93 against human gold on numeric claims, but rule labels alone trailed a zero-shot model in Ju 2023. Single-expert gold missed 18 to 32% of valid items in Aavang 2026. A kappa gate of 0.8 on 100 items passes a true 0.79 about 45% of the time; 30 items cannot test it (stream 07) |
| Method comparison: full factorial on Qwen3.5-4B and 9B, three retrieval levels, equal development budget | Design supported; base model contradicted by feasibility | FinanceBench used the same three retrieval levels. Feasibility: Qwen3.5 LoRA fits only 512 tokens (4B) or 256 (9B) within 12 GiB. New confound: fine-tuning without retrieved context and then adding retrieval lowered accuracy in RAFT and Ovadia 2023 |
| Interactions on the logit scale, by difficulty stratum | Not addressed; arithmetic supports it with a caveat | Stream 07: pooling easy and hard items creates a spurious logit interaction, so fit an item-level mixed logit |
| Commercial models run without the fine-tuning factor | Supported, reason amended | Vendor fine-tuning exists but is opaque and on another base (stream 05) |
| Goal C as non-inferiority with a 5-point margin | Method supported; margin and power need stating | At 800 items power is 0.95, 0.83 and 0.59 for true shortfalls of 0, 1 and 2 points. Near a ceiling any margin passes (FinLoRA: 97 to 99% for all systems) |
| Endpoints: L1 confirmatory, L2 anchored, L3 exploratory | Supported; L3 is weaker than stated | 100 clean months give a t of 2 at only 52% power; 80% power needs 196 months (stream 07). Label accuracy and economic association come apart (Bisharat 2026) |
| Failure definition: four 8-K items as the hard tier | Supported with caveats | Items 2.06, 3.01 and 4.02 carry negative price reactions (Lerman and Livnat 2010). Item 3.01 includes curable deficiencies and voluntary transfers; 2.06 exempts impairments concluded while preparing a periodic report; 1.03(b) is plan confirmation; 4.02 was 35% of restatements by 2012 |
| Reporting: four contamination labels | Supported as convention | Add the future-invariance question (Lopez-Lira 2025). "Clean" for a closed commercial model rests on the vendor's stated cutoff and is an assumption (Ludwig et al. 2025) |
| Memorisation probe: closed-book recall before and after the cutoff | Supported; the design must change | Recall fades well before the stated cutoff (Gao 2025: 0.88 for 2020, 0.016 for 2023, cutoff December 2023), so adjacent quarters show no gap even in a contaminated model |
| No masking | Supported, reason refined | LLM rewriting cuts re-identification to 9% (Wu 2025), so "masked text stays identifiable" is not always true. The stronger reason here: masking removes the numbers, and the numbers are the label |
| Pre-registration by git commit | Supported in principle | A local commit is not an independent time stamp (stream 07) |
| Point-in-time models as a clean reference | Contradicted for extraction | Downloadable, but at most 1.55B parameters, 2,048 tokens of context, latest vintage 2024 (stream 03) |

## Changes these findings ask of the plan

**Benchmark and labels**

1. Record direction and width as two attributes of a revision, so a range that both shifts and
   narrows has a defined label.
2. Split announced "withdrawn" from "no longer mentioned"; add rules for temporary suspensions and
   for a switch between quarterly and annual guidance. Keep "no guidance stated" as its own class.
3. Let the tuple's metric cover revenue, margin and capital expenditure, not only EPS.
4. Treat the qualitative-guidance stratum as central. It is where firms near failure are and where
   systems should separate; start the headroom pilot there.
5. Stratify the test set by each company's updating routine. Expect "maintained" to dominate:
   about a quarter of annual EPS updates repeat both width and midpoint.
6. Minimal pairs: add unedited control pairs and report a false-positive rate; show the members of
   a pair separately and score consistency afterwards; pre-register how invalid outputs count;
   expect to lose about a fifth of wording-only pairs in checking.
7. Add two baselines: keyword outlook rules, and pair similarity plus dictionary tone change.
8. Log the position of every evidence quote; model-chosen sentences skew early and long.

**Labelling**

9. Gate reliability on the interval of kappa, and report raw agreement and AC1 beside it.
10. Adjudicate a sample of unmatched extractions, since single-annotator gold is partial.
11. A 30-pair pilot of the narrative-change task cannot decide anything. Label 100 or defer it.
12. Prediction-powered inference may cut human labelling by 20 to 35% (hypothesis). Phase III
    needs 125 to 250 random validation labels in any case.

**Method comparison**

13. Choose a base model on which fine-tuning fits at passage length (feasibility).
14. Define the training prompt of the fine-tuned level: train with supplied and distractor
    passages where the cell uses retrieval.
15. Count checkpoint selection, LoRA search and prompt edits as development evaluations. Never
    select on the test set.
16. Name the confirmatory contrasts in advance and use Holm. Size the test set from the pilot's
    disagreement rate.
17. Cluster by company; treat quarter as a stratum.
18. Run Goal C on strata below the ceiling and state its power at shortfalls of 1 and 2 points.

**Validity**

19. Redesign the memorisation probe: company and fiscal quarter only; an "unknown" option;
    answer-token probabilities for local models and repeated samples for commercial ones; quarters
    from at least three years before the cutoff to after it; strata by company size; a persistence
    baseline. A null result is a lower bound, never "clean".
20. Push or externally time-stamp registrations and sealed manifests.
21. Mark commercial-model results "clean (vendor-stated cutoff)".

**Failure tiers**

22. Run the hard-event census by sub-item with company denominators, and state expected event
    counts in EXP-0001: at 0.3 to 1.5% a year, 800 companies yield two to twelve bankruptcies.
23. Softer tiers to pre-register: filing-anchored events (auditor going-concern paragraph,
    completed delisting for cause, any restatement, an impairment charge in as-filed figures); a
    fall in an as-filed profitability-and-leverage composite; a twelve-month market-adjusted
    return including the delisting return.
24. The structured bar a text signal must beat is the eight-variable hazard model of Campbell,
    Hilscher and Szilagyi 2008, which needs daily prices for delisted companies.

## Corrections to the seed list and wording

- Kim, Muhn and Nikolaev 2024, "Financial statement analysis with large language models" (arXiv
  2407.17866), was withdrawn by its authors in February 2025. Remove it from the seeds.
- Gao, Jiang and Yan is now titled "Detecting Lookahead Bias in LLM Forecasts" (v2, June 2026).
- Tang, Yao and Zarowin was published in 2025 under a changed title; the note rests on the 2015
  working paper.
- `00_master_methodology.md` §3 should rest the no-masking rule on information loss.
- The roadmap's "commercial fine-tuning is absent or opaque" should read "opaque".

## Limits of this pass

- Read from abstracts only: de Kok 2025 (the one study scoring an LLM extraction against labels,
  worth a full read by a person), Siano 2025, Huang, Wang and Yang 2023, Shumway 1997, Brown et al.
  2020, Beneish 1999, Piotroski 2000, White 2000, FinanceBench, FinVerBench.
- Several deep notes rest on working-paper versions; each note says which.
- Not triaged, to stay within twelve per stream: FinQA, ECTSum, FiNER-139, EDGAR-CORPUS, the FinGPT
  benchmark paper. Nothing is claimed from them.
- Not reached: pre-registration practice in empirical finance.
- A pointer left for a later pass: Costello, Levy and Nikolaev, "Uncovering Information: Can AI
  Tell Us Where to Look?" (December 2024 draft), which trains LLMs with fixed knowledge cutoffs.
- The streams ran with a cap of three deep notes each after a usage interruption. The stop rule
  (two consecutive batches that change no design decision) was not reached; this is a first pass.

## Stream 08, added 2026-11-19 for sub-study S2

Built from `streams/08_blind_replay.md`: 19 rows, 13 with a deep note. The first-pass sections
above are unchanged.

**Gaps and the experiments they suggest**

| Gap | Experiment in S2 |
|---|---|
| No study blinds a text while keeping its numbers usable; the method that reaches chance replaces every number with a placeholder | Views that rename, scale with two factors and add bounded noise, with statements kept adding up (S2-b, step 3) |
| Numeric noise is tested on bare tables only | The same noise on earnings releases, against a rule attacker and a model attacker (H3) |
| No company-level leakage measure with arms assigned by design | Eight views per episode, a wrong-identity arm, and the same contrasts after the cutoff (S2-b) |
| Nobody has tested an LLM that is handed computed ratios on blinded statements | The blinded PM against a logistic baseline on clean episodes (H6) |
| Hindsight carried by a rewriting or lesson-writing model is untested | Wave 2: a blind lesson writer, with the playbook ablated (S2-d) |
| No audit covers Claude Opus 5.5 or Sonnet 5.5 | The closed-book probe on both (S2-a, S2-b step 1) |

**Already answered: do not redo**

- Renaming alone does not hide a text (`engelberg-2025`).
- Instructions to ignore later knowledge do not work (`li-2026`; `lopez-lira-2025`).
- Membership-inference scores, cross-model disagreement and performance decay are not usable
  leakage measures here (`roy-2026`, `benhenda-2026`, `wu-2026`).
- Output-side subtraction of memory needs logits (`li-2026`, `merchant-2025`).

**Design defaults against the literature**

- Test after every cutoff: supported; measured cutoffs mostly run early (`jia-2026`).
- No masking for the main benchmark: supported.
- Simple baselines first: supported (`levy-2026`, `wu-2026`, `roy-2026`, `gencay-2026`).
- The memorisation probe of methodology §9: supported, with repeated samples, a hit-rate gate and
  demeaning by entity and period. Its item-level regression on recall propensity is weakened:
  the propensity may be saturated on a frontier model.

## Streams 13a to 14c, added 2026-11-26 for sub-study S1

Built from `streams/13a_financial_reasoning_benchmarks.md`, `13b_reasoning_item_design.md`,
`14a_synthetic_data_small_specialists.md`, `14b_distillation_methods_small_students.md` and
`14c_finance_specialists_analyst_reasoning.md`: 112 rows, 30 with a deep note. A paper read by two
streams keeps a row in each, as before (11 such rows; the CFA Level III paper has one note,
`shetty-2025-cfa-level-iii-evaluation`, shared by 13a and 13b). The sections above are unchanged.

**Gaps and the experiments they suggest**

| Gap | Experiment in S1 |
|---|---|
| No benchmark of trend, driver or direction judgements on US earnings releases with rule labels (13a, 13b) | Section R, built from as-filed tables with XBRL-checked gold (EXP-0019; R v1, EXP-0053) |
| No model below 1.5B in any financial reasoning benchmark read; no finance distillation study with a student below 3.8B (13a, 14c) | The 0.8B against the 2B and the 4B on R (EXP-0050; EXP-0059) |
| No test of whether reasoning gains from distillation survive a change of item family, combination or node (13a, 14a, 14c) | R1.4 and R1.5 held out of the factory; twins (EXP-0059, HF2) |
| No test of whether task and answer-format variety undoes a small student's single-template lock-in (14a) | C and K2 locked (EXP-0050); F1 against F2 on varied items (EXP-0059, HF1) |
| Unknown effect of a teacher's wrong answers on a student trained on label items (14a) | Chains kept only when the answer and every checked calculation are right (EXP-0056, EXP-0070) |
| No weight-averaging study below 3B; no quantified replay ratio for sub-3B students (14b) | Averaging C and K2 with the released 0.8B (EXP-0051: no repair); 20% general data (EXP-0059) |
| No on-policy distillation or RL study on label or analytical items below 1.5B; none from a 4-bit teacher's logits (14b) | Room measured by sampling (EXP-0051: pass@8 20 points above greedy); F3 left to its own pre-registration |
| Judge-human agreement on finance analysis measured on at most 124 answers; none for small models' text (13a, 13b, 14c) | Not taken up: every S1 item is graded by rule |

**Already answered: do not redo**

- Finance-tuned models' gains have not survived a change of format (`tong-2026`, `qian-2025`).
- Do not assume a larger or "thinking" teacher helps a small student; choose the teacher and the
  chain length by what the student learns (`li-2025`, `zhao-2025`; 13a point 5, 14c point 3).
- Write rationales forward from the document, never from the gold label (`xiao-2025`,
  `turpin-2023`; 14c point 1).
- Holistic LLM judges are unreliable for finance analysis (14c; 13b on judge bias by graded model).

**Design defaults against the literature**

- Many task kinds and answer formats per release, quotas fixed before generation: supported (14a
  points 1 and 2); S1's factory does this (EXP-0055).
- Tens of thousands of examples rather than millions, sizes measured at more than one level:
  supported (14a point 3); S1 trains at 2,000 and 8,000 because of the machine (EXP-0058).
- Short chains, a sentence or two of rationale before the answer: supported (14a point 4).
- The 4B rather than the 9B as teacher, the 9B as a pilot only: supported (14a point 5; 14b point 3).
- General data kept in the mix and its price reported: supported (14a point 7; 14b point 2).
- Rule-checked chains, forward from the release (DianJin-R1's recipe): supported (14c point 1).
- RL as a comparison arm at most: supported (13a, 14b point 4, 14c point 7); out of scope before
  2026-12-15.
- Checkpoints chosen on development R only: supported (14b point 5).

**Limits of these streams**

- Most evidence on synthetic data and distillation is mathematics and code with verifiable
  answers; finance evidence is numeric QA and sentiment at 3.8B and above (14a).
- Teachers in the literature are far stronger relative to their students than a local 4B is to
  section R (14a).
- Full texts were read through automated extraction; several tables came out scrambled, and no
  number was re-keyed from a typeset PDF (13b, 14a).
