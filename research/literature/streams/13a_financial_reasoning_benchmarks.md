# Stream 13a: financial reasoning benchmarks, and whether small models close the gap

Sources checked 2026-11-23, for sub-study S1 (`../../design/substudy_s1_distill_prune.md`). 26 rows
in `13a_financial_reasoning_benchmarks.csv`: 7 deep notes and 19 triaged rows. Deep notes:
`../papers/qian-2025-fino1-reasoning-transfer-finance.md`,
`../papers/liu-2025-fin-r1-financial-reasoning-rl.md`,
`../papers/tong-2026-finindices-long-horizon-statements.md`,
`../papers/zhang-2025-xfinbench.md`,
`../papers/shetty-2025-cfa-level-iii-evaluation.md`,
`../papers/benyoash-2025-secque.md`,
`../papers/li-2025-small-models-learnability-gap.md`.
Already covered elsewhere and cited, not repeated: FinanceBench, Finance Agent Benchmark, Fin-RATE,
FinBen, FinVerBench (stream 04); Phogat et al. 2024 and FinLoRA (stream 05); FinCoT (Nitarach et
al.), "Reasoning or Overthinking" and Sprague et al. (stream 12); Kim, Muhn and Nikolaev 2024
(withdrawn; note in `../papers/`) and Li et al. 2024 (stream 02). Stream 13b (how to build and grade
items) is written separately; this stream covers what exists and the evidence. Stream 13b wrote its
own notes on the same CFA Level III paper (grading angle) and on FinChain, in parallel; the two
Shetty notes should be reconciled at merge. Not merged into `../matrix.csv`.

The question: S1's student (Qwen3.5-0.8B distilled from Qwen3.5-4B, both with a calculator) is
within about 3 points of the teacher on EarningsExam B1 (lookup) and B2 (computation). The owner
holds that lookup and arithmetic are what code already does; the value of an LLM is judging trends,
combining several pieces of information and financial logic. Can a 0.8B-4B model match a larger one
on that, and how would it be tested?

## What the stream establishes

**1. Most "financial reasoning" benchmarks are numeric QA under another name**

- **Verified fact.** The evaluation sets behind the finance reasoning-model papers are numeric:
  FinReason (FinQA, DocMath SimpLong and CompLong, XBRL-Math) in `qian-2025`; FinQA and ConvFinQA
  plus a sentiment set and Chinese knowledge questions in `liu-2025`; FinanceReasoning (2,238
  numeric problems, graded within 0.2%), FinChain (2,900 templated computations), BizBench and
  DocFinQA (FinQA questions over 123K-word filings) in the triaged rows. "Reasoning" here means
  choosing and chaining formulas over a table, which is S1 B2 with longer inputs.
- **Empirical finding.** Frontier models are near ceiling on the short-context versions:
  o1 with program-of-thought 89.1% on FinanceReasoning's Hard set; GPT-4o 83.2% rising to 91.6%
  when given a formula library (Tang et al. 2025). Remaining difficulty comes from long context
  (DocFinQA, CompLong) or from withholding the formula (below).
- **Consequence for us (hypothesis).** Adding another FinQA-style section to EarningsExam would
  measure the same skill S1-c already distilled.

**2. Where the reasoning the owner means is tested, and how**

Six task families go beyond lookup and arithmetic. Grading mode in brackets.

| Family | Examples (rows) | What it tests | Grading |
|---|---|---|---|
| Multi-period and cross-statement computation without the formula | FinIndices (`tong-2026`); XFinBench temporal reasoning (`zhang-2025`) | Derive a standalone quarter from year-to-date, TTM, match flows to average stocks, pick the right period among distractors | Auto (numeric) |
| Knowledge and judgement statements | XFinBench true/false and 3-option MCQ (temporal, forecasting, scenario planning); CFA L1-L3 MCQ (`shetty-2025`, Patel 2025, Yao 2025, Mahfouz 2024); EconNLI causal pairs; FinDVer claim verification | Is this statement about a scenario, cause or trend correct | Auto (choice); needs chance correction |
| Recognising missing information | FinIndices "Insufficient information" items; RealFin (premises removed) | Whether the model notices it cannot answer | Auto (abstain or option choice) |
| Analyst-style open questions on filings | SECQUE (trend, ratio, risk, insight; `benyoash-2025`); FinanceQA (assumptions, conventions); Finance Agent Benchmark and Fin-RATE (stream 04) | Comparing periods or firms, interpreting ratios, explaining risk | LLM judge against a gold answer |
| Written synthesis | CFA Level III essays (`shetty-2025`; Mahfouz 2024) | Recommend and justify a portfolio decision | Rubric, LLM judge plus human grader |
| Outcome prediction | Earnings direction from statements (Kim et al., withdrawn; Shu 2025 thesis); FinTradeBench hybrid questions | Call next year's EPS direction or combine fundamentals with price signals | Auto (realised label), but noisy and exposed to recall |

- **Empirical finding.** Multiple choice saturates first. CFA Level III MCQ top scores cluster at
  71-75% while essays spread from 39 to 83 (`shetty-2025`); Patel et al. (2025) report frontier
  models passing all three levels.
- **Empirical finding.** The auto-gradable families that still separate frontier models from
  experts are temporal and multi-period ones: XFinBench temporal reasoning 59.1 (o1-preview)
  against 79.5 (experts); FinIndices tables 70.7% with formula hints and 38.2% without for the best
  model.
- **Gap (verified by search, not refuted).** No benchmark found asks trend, direction or "what drove
  the change" questions about US earnings releases (8-K EX-99.1) with labels fixed by rule. The
  nearest are FinIndices (Chinese statements, numeric targets), SECQUE (10-K/10-Q, judge-graded) and
  FINAL (stream 04, annual MD&A changes).

**3. Small against large: the gap closes in distribution and reopens out of it**

- **Empirical finding (closing).** On FinQA-type tasks a tuned 4B-14B model reaches the large model:
  Phogat et al. (stream 05), 3.8B-14B students at 71.6-77.6 against GPT-4 77.5 on FinQA; Fin-o1-8B
  and 14B average 60.0 and 61.1 against GPT-4o 61.0 (`qian-2025`); Fin-R1 (7B) tops FinQA (76) and
  ConvFinQA (85) above DeepSeek-R1 (`liu-2025`). Each of these trained on the same data sets'
  training splits, and none checked overlap with the evaluation items.
- **Empirical finding (reopening).** On harder or unfamiliar formats the same models fall away.
  FinIndices with formula hints: Fin-R1 10.9% single and 0.0% tables, Fin-o1-14B 28.2% and 2.7%,
  against 77-80% and 66-71% for frontier models (`tong-2026`). DocMath CompLong: Fin-o1 26-27
  against 39-42 (`qian-2025`). FinChain: finance-tuned 7-8B models do no better than plain
  Qwen2.5-7B-Instruct (final-answer 65.4) and drop sharply on Advanced templates.
- **Empirical finding (judgement and synthesis).** Where no tuning was applied, 8B models sit far
  below: Llama-3.1-8B 38.9 against about 80 on human-graded CFA Level III essays (`shetty-2025`);
  0.48 against 0.69 for GPT-4o on SECQUE (`benyoash-2025`); 11.7 against 59.1 on XFinBench temporal
  reasoning and 22.3 against 60.1 on scenario planning (`zhang-2025`). BizFinBench puts Qwen3-1.7B
  and a 3B model last on extraction and calculation (Lu et al. 2025).
- **Empirical finding (general reasoning does not transfer).** DeepSeek's R1 distillation into
  Qwen-7B scores 58.0 against 65.6 for the plain instruct model on Fin-R1's finance suite
  (`liu-2025`); QwQ-32B 52.9 against 56.2 for Qwen2.5-32B (`qian-2025`). Stream 12 records the same
  for sentiment (chain of thought not helping).
- **Empirical finding (what the training recipe buys).** CoT SFT gives most of the gain; RL adds 1
  to 3 points after it (Fin-o1 +1.4; Fin-R1 +3.3; GRPO alone +2.2 with incoherent outputs). Yue et
  al. (2025) find RL with verifiable rewards bounded by the base model's pass@k, while distillation
  can add new behaviour. Plain SFT on finance data can cost 3-4 points of prior ability (Hayrapetyan
  et al. 2026).
- **Empirical finding (comparable domain, the most relevant to a 0.8B student).** In math, Qwen2.5
  students up to 3B learn better from short chains of thought than from long ones, and up to 1.5B
  better from a small teacher than a 72B one; a 1:4 long-to-short mix helps at 3B
  (`li-2025`). The authors attribute part of the gap to missing domain knowledge.
- **Hypothesis (synthesis of the above).** What transfers to a small model by distillation is
  procedure on a familiar format: which cells to read, which formula to apply, how to lay out the
  answer. What does not transfer is the knowledge of which computation a situation calls for when
  no hint is given (FinIndices no-hint drops; XFinBench terminology gains from retrieval; Yao et al.
  2025 naming knowledge gaps), and holding several periods and metrics at once (FinIndices
  structural bottleneck). Judgement and synthesis have no small-model distillation study at all.
- **Earnings direction, specifically.** No credible small-against-large evidence. Kim et al. is
  withdrawn and Li et al. (stream 02) could not reproduce it. The only small-model test found
  (Shu 2025, a master's project) reports F1 of 63-68 for 1.5B models on imbalanced labels with no
  majority-class baseline, against baselines copied from the withdrawn paper. Khaybullina (2026)
  shows that in five of six 0.5B-7.6B models, commentary tone and price momentum move the forecast
  more than the EPS surprise does.

**4. Which task types grade themselves**

| Task type | Auto-gradable? | Caveat from the literature |
|---|---|---|
| Numeric answer from text and tables (FinQA family, FinIndices) | Yes, with a tolerance | Tolerance varies 0.2% to 5%; all-or-nothing tables are harsh; LLM answer extraction is common (Fino1, Fin-R1, FinanceReasoning) |
| Step-level computation trace (FinChain) | Yes, by alignment to executable templates | Only for templated computations |
| True/false, MCQ, causal pair, claim verdict | Yes | Chance rates 50% and 33%; MCQ saturates for frontier models |
| Abstain on missing information | Yes | Needs balanced answerable and unanswerable items |
| Direction of a realised outcome | Yes, label from data | Noisy target; exposed to recall; F1 on imbalanced classes misleads (Shu 2025) |
| Open analytical answer against a gold answer | LLM judge | Best panel 0.75 three-class agreement on 124 answers; partial credit unreliable (`benyoash-2025`) |
| Essay, recommendation, synthesis | Rubric plus judge | Judge and one human identical on about 70% of questions, human 5.6 points higher (`shetty-2025`) |

## Look-ahead and memorisation across the stream

Not addressed by any reasoning-model paper read. Train-test overlap is the more pressing issue:
FinQA, ConvFinQA and DocMath feed training and evaluation in `qian-2025` and `liu-2025` with no
check. FinIndices and FinChain avoid outcome recall by computing labels from the input, and FinChain
regenerates instances from templates. XFinBench withholds test answers. CFA studies rely on
paywalled mock exams. Outcome-prediction tasks (earnings direction) carry the full recall problem
documented in streams 03 and 08.

## Design implications for an S1 reasoning exam

Named here "R" to avoid clashing with the struck B3 (guidance reading).

1. **Build the main R section from the same EX-99.1 tables, on the FinIndices pattern.** Items whose
   answer is fixed by the release but whose computation is not named: standalone fourth quarter from
   full-year minus nine-month columns; trailing-twelve-month figures; margin change in basis points
   across both periods shown; which segment contributed most to growth; whether EPS growth came from
   net income or share count; whether operating margin expanded while revenue fell. Add distractor
   columns (prior year, year to date) and "cannot be determined from this excerpt" items. Run each
   item with and without a formula sheet, with the calculator in both arms: the no-hint gap measures
   "knows what to compute", the part the owner says code does not supply. Labels by rule, so B1/B2's
   two-source verification carries over.
2. **Add a judgement subsection in auto-gradable formats.** True/false statements and three- or
   four-option questions about direction and drivers ("revenue grew mainly because of segment X",
   "the margin decline is explained by the one-off charge"), with gold fixed by the table, scored
   chance-corrected. Build tone-controlled pairs (same numbers, positive or negative commentary)
   since small models follow tone over numbers (Khaybullina 2026; stream 04 RFC-BENCH). Report MCC
   or balanced accuracy, never F1 alone.
3. **Keep rubric-graded synthesis small and validated.** A short set of SECQUE- or CFA Level III-style
   questions ("summarise the quarter's drivers and risks") can show whether the 0.8B is far behind
   the 4B where the literature says gaps are largest, but grading agreement in the best cases is
   0.70-0.75. Stream 13b should set the human-agreement check; these items should not carry the
   primary S1 result.
4. **Treat outcome prediction as a separate, secondary probe.** Next-quarter direction from a release
   is auto-gradable but noisy and exposed to recall; it overlaps S2. If used, compare against a code
   baseline (persistence, majority class) on post-cutoff releases.
5. **Distillation design for R.** Use the 4B teacher's short answers as well as thinking traces, and
   test a mix (`li-2025`); do not assume a larger or "thinking" teacher helps a 0.8B student. Expect
   an RL arm to add a few points at most. Hold out item families (train on some R families, test on
   others) because finance-tuned models' gains have not survived a change of format (`tong-2026`,
   `qian-2025`). Report R separately from B1/B2 and by family.
6. **Prior for the result (hypothesis).** Expect the 0.8B to keep near-parity on rule-labelled R items
   with a formula sheet, to fall behind without one and on multi-period tables, and to fall furthest
   behind on judged synthesis. If the gap without hints is small, that is new evidence; no paper
   tests models below 1.5B on these task types.

## Reusable

- FinIndices test items and the hint/no-hint protocol (Hugging Face, licence to check).
- XFinBench validation split (1,000 items) for temporal reasoning and scenario planning, auto-graded.
- SECQUE (565 questions, Hugging Face) and its judge thresholds as a reference point for 13b.
- FinChain templates and ChainEval for step-level grading of computations.
- XBRL-Math (90 items, CDLA-Permissive 2.0) as a small equation probe.

## Gaps that suggest an experiment

- No benchmark of trend, driver or direction judgements on US earnings releases with rule labels
  (point 2): the R section would be the first.
- No model below 1.5B in any reasoning benchmark read; no distillation study on judgement or
  synthesis items in finance.
- No test of whether reasoning gains from distillation survive a change of item family.
- Rubric-graded financial analysis has judge-human agreement measured on at most 124 answers.

## Not triaged

FinEval (Chinese knowledge MCQ), FinanceMATH, TAT-QA and ConvFinQA themselves, Agentar-Fin-R1,
FinSearchComp, FLAME, CFLUE, FinMME and multimodal sets. Nothing is claimed from them.
