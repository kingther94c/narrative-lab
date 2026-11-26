# Stream 14c: small finance specialists and analyst-style reasoning

Sources checked 2026-11-25, for sub-study S1 (`../../design/substudy_s1_distill_prune.md`,
`../../design/s1_reasoning_exam.md`). 18 rows in `14c_finance_specialists_analyst_reasoning.csv`:
5 deep notes and 13 triaged rows. Deep notes:
`../papers/zhu-2025-dianjin-r1.md`,
`../papers/zhao-2025-agentar-deepfinance-100k.md`,
`../papers/xiao-2025-trading-r1.md`,
`../papers/wu-2025-finar-bench.md`,
`../papers/sugiura-2026-edinet-bench.md`.
Already covered elsewhere and cited, not repeated: Fino1/FinReason (`qian-2025`), Fin-R1
(`liu-2025`), FinIndices (`tong-2026`), XFinBench (`zhang-2025`), CFA Level III (`shetty-2025`),
SECQUE (`benyoash-2025`), the small-model learnability gap (`li-2025`) in stream 13a; FinChain
(`xie-2025`) and the judge literature (`szymanski-2024`, `chandak-2025`, `arora-2025`) in stream
13b; FinCoT (Nitarach et al.), `sprague-2025`, `turpin-2023` and Kim, Muhn and Nikolaev
(`kim-2024`, withdrawn) in stream 12; Phogat et al. 2024 and Huang et al. 2026 (LoRA at
270M-8B) in stream 05; Li et al. 2024 (`li-2024`, GPT as sell-side analyst) in stream 02;
`koijen-2026` in stream 13b. DianJin-R1 and BizFinBench were triaged from abstracts in 13a; this
stream read their HTML. Streams 14a (synthetic-data scale) and 14b (training methods) are written
in parallel and cover the general method; Harsha et al. 2025 (GPT-4o synthetic financial QA for
3.8-14B students) sits in 14a. This stream covers finance specialists only. Not merged into
`../matrix.csv`.

The question. The owner's goal for S1 is a financial application: a small model that reads
disclosures and reasons with logic that forms a coherent analytical framework (the owner's word:
体系), distilled from a larger model's expertise, so that the small model is outstanding in one
domain. EXP-0050 sets the starting point: on 450 development R items the 4B scores 82.0, the
untrained 0.8B 55.9, and the two 0.8B students distilled on B items 0.9 and 0.7, because they box a
number for every item; hints helped only on R1.7 and not the 0.8B. Four questions: what finance
specialists built by distillation gained and failed to carry over; what "analyst framework"
reasoning looks like in data and how open analysis is graded; whether LLM judgements from filings
are checkable against later outcomes; and which finance tasks a small model can be good at.

## What the stream establishes

**1. Finance specialists built from larger models: big in-distribution gains, little transfer**

| Specialist | Student | Teacher and data | Gain where test matches training | Independent or held-out evidence |
|---|---|---|---|---|
| Fin-R1 (`liu-2025`, 13a) | Qwen2.5-7B | DeepSeek-R1 traces, 60K | FinQA 76, ConvFinQA 85 | FinIndices 10.9 / 0.0 (13a); FinEval-KR accuracy 0.42, 17th of 18 models (GPT-3.5-turbo 0.28) |
| Fin-o1 (`qian-2025`, 13a) | 8B, 14B | GPT-4o chains, 9K | average about GPT-4o | FinIndices 28.2 / 2.7 (14B) |
| DianJin-R1 (`zhu-2025`) | Qwen2.5-7B, 32B | DeepSeek-R1 chains; a 72B multi-agent workflow for compliance | 7B: CFLUE 69.4 to 80.3, FinQA 66.7 to 77.7, CCC 55.0 to 94.5 | FinIndices 32B 41.3 / 11.4 (13a); no held-out workflow test |
| Agentar-Fin-R1 | Qwen3-8B, 32B | about 300K synthetic items, unnamed teachers | 8B Finova 54.5 to 63.6 (own benchmark) | none independent |
| ODA-Fin | Qwen3-8B | Qwen3-235B-Thinking, 318K | average 71.5 to 72.1 (SFT), 74.6 (RL) | event-day RankIC 0.072 vs base 0.061; next-day 0.033 vs base 0.052 (Wang et al. 2026) |
| Trading-R1 (`xiao-2025`) | Qwen3-4B | o3-mini/o4-mini ratings, rationale written backwards, 100K | returns on six tickers | test window inside the data window; thesis quality never measured |
| EDINET-Bench SFT (`sugiura-2026`) | Llama-3.2-1B | labels only | fraud AUC 0.66 from tables | earnings direction 0.48-0.52 |
| Huang and Simpson 2026 | BERT-class | GPT-4o synthetic examples | tweet sentiment 77.1 vs teacher 72.8 accuracy | no out-of-domain test |

- **Verified fact (by search, not refuted).** No finance distillation study with a generative
  student below 3.8B was found. The smallest generative students are Phi-3-mini (3.8B) on
  FinQA-type numeric QA (Phogat et al. 2024, stream 05; Harsha et al. 2025, stream 14a) and
  Qwen3-4B for analysis-style output (Trading-R1); below that, only classifiers (a 1B fine-tuned on
  labels in EDINET-Bench; BERT students for sentiment).
- **Empirical finding (in distribution, large).** When the test shares the training sources, 7B
  students gain 10-40 points: DianJin-R1-7B +11 on CFLUE and FinQA and +39.5 on its in-house
  compliance check (`zhu-2025`); PRM-selected SFT data take a 7B from 45.3 to 58.2 on CFLUE
  (Fin-PRM).
- **Empirical finding (on a strong modern base, small).** Distilled-chain SFT on Qwen3-8B moves the
  nine-benchmark average from 71.5 to 72.1 and is below the base on six of nine, FinQA included
  (69.8 against 72.2); training on raw answers without chains drops it to 66.1; RL adds 2.5 to
  74.6, the level of the untuned Qwen3-32B (74.7) (ODA-Fin). Agentar-Fin-R1-8B gains least on
  "complex reasoning" (48.6 to 51.6) and most on agent formatting ("expression" 32 to 63).
- **Empirical finding (no transfer to independent tests).** Finance-tuned 7-14B models collapse on
  FinIndices (13a). On 45,964 10-Q events, finance-tuned models show no reliable next-day return
  advantage; the two Qwen3-8B derivatives beat their base on event-day RankIC (0.070, 0.072 against
  0.061) and fall below it next day (0.034, 0.033 against 0.052); direct EPS forecasts from all 13
  models sit at the 43.4th percentile of analysts (Wang et al. 2026). A newer general base beats an
  older specialist: Qwen3-8B 67.9 against Fin-R1 55.3 and DianJin-R1-7B 63.2 on Agentar's finance
  average (different base generations).
- **Empirical finding (general reasoning does not carry finance skill).** R1-Distill-Qwen-7B scores
  below Qwen2.5-7B-Instruct on all three of DianJin's finance sets (CFLUE 48.4 against 69.4,
  compliance 41.5 against 55.0) while far above it on MATH-500 (`zhu-2025`), repeating 13a.
- **Empirical finding (RL: a few points, sometimes a cost).** +1.5 (compliance) and +4.8 (CFLUE) for
  DianJin-R1-7B but -2.6 on FinQA (Chinese-only RL data); +2.5 average for ODA-Fin; a step-level reward beats an
  outcome-only reward by 3.3 (Fin-PRM); Agentar-Fin-R1 loses 0.4 and 1.6 on MATH-500.
- **Verified fact (what is never measured).** None of the specialist papers read (DianJin-R1,
  Agentar-Fin-R1, ODA-Fin, Trading-R1, Agentar-DeepFinance-100K) measures the quality of the
  reasoning or thesis itself; all report answer accuracy or returns. None reports counts for its
  decontamination step.

**2. What an analyst "framework" looks like in training data**

Four patterns were found, with different evidence behind them.

| Pattern | Example | Evidence | What it checks |
|---|---|---|---|
| Procedure graph run by the teacher, merged into one chain | DianJin-R1 compliance check: guideline -> condition nodes -> outcome; Qwen2.5-72B runs one agent per node; GPT-4o merges node chains when the outcome is right | 7B in one call 94.5 against 72B multi-agent 95.0 (8.15 calls) and 72B single call 55.5 (`zhu-2025`) | Outcome only; nodes not checked separately |
| Staged output: structure -> evidence-backed claims -> decision | Trading-R1 theses: fixed sections, bullets with opinion, quote and source, rating at the end | Returns only; rewards count sections, quotes and sources (`xiao-2025`) | Form, not truth |
| Expert blueprint in the prompt | FinCoT (stream 12) | Qwen3-8B-Base 63.2 to 80.5 on CFA-style questions, most for models without finance post-training | Answer |
| Decomposition into checkable levels | FinAR-Bench: extract 32 items -> compute 38 indicators -> mark 64 trend, threshold and comparison conditions -> interpret (`wu-2025`); FinDeepResearch HisRubric: recognition -> calculation -> abstraction -> interpretation | Small models fail every level (below); frontier scores fall level by level, 59.5 -> 44.6 -> 44.8 -> 20.3 | Each level, mostly by rule up to calculation |

- **Empirical finding (chains are needed where steps combine).** At 7B, training on answers alone
  for hard items falls below the base (Fin-Eva 83.7 to 75.8; with chains 86.0); on held-out slices,
  chains add +29.4 on math, +6.7 on "analysis and interpretation" and +0.5 on classification-like
  NLP (`zhao-2025`). EXP-0050's distilled 0.8B arms are the extreme case of answer-only training.
- **Empirical finding (teacher choice).** The strongest model is not the best chain writer:
  DeepSeek-R1 scores 75.4 on FinQA as a teacher but its 7B student 66.5; QwQ-Plus 73.0 and its
  student 68.8 (`zhao-2025`).
- **Empirical finding (chain length depends on student size).** Long chains beat short ones for a
  7B student (FinQA 68.8 against 65.6, `zhao-2025`), while students up to 3B learn better from short
  chains in maths (`li-2025`, 13a). No finance evidence at 0.8B.
- **Empirical finding (repairing failures).** Reflect-and-rewrite on items with no correct sample
  kept 862 of 1,337 and added +1.74 on FinQA (`zhao-2025`).
- **Hypothesis (synthesis).** A framework, in data, is a fixed procedure whose intermediate outputs
  can each be checked: the DianJin pattern (teacher runs a graph, chains merged) combined with the
  FinAR decomposition (every node's output checkable against filed data). The literature has the
  first without node checks and the second without training.
- **Caution.** Trading-R1 writes the rationale after seeing the rating ("reverse reasoning
  distillation"). That is the rationalisation pattern of `turpin-2023` and EXP-0029: a chain fitted
  to a known answer. Teacher traces for S1 should be generated forward and filtered by checks.

**3. Open-ended financial analysis benchmarks and how far their grades can be trusted**

| Benchmark | Task | Grading | Reliability evidence |
|---|---|---|---|
| FinAR-Bench (`wu-2025`) | Statement analysis in four steps, 100 Chinese firms | Tables by key matching with numeric tolerance; condition table by precision/recall; narrative by an LLM-judge tournament | None reported; exact-match scoring (theta 0) cuts GPT-o1's indicator recall from 90.6 (5% tolerance) to 35.3 |
| FinDeepResearch (Zhu et al.) | Six-section company report, 64 firms, 8 markets, 247 items each | Unnamed LLM judge: binary accuracy, coverage of 3-5 reference claims, LLM-written 10-point criteria; structure by rule | No human-agreement figure; references from LLM majority vote then experts; best 37.9 / 100 |
| BizFinBench | Nine task types, 6,781 Chinese queries | Accuracy on six; GPT-4o judge on three | Judge ablation Spearman 0.31-0.57 (data description), 0.70-0.87 (tool use) |
| Goldsack et al. 2024 | Analyst reports from earnings calls | Three finance postgraduates; three LLM judges | Human-human kappa 0.171 (0.476 merging top labels); judge-human Pearson 0.31-0.51; GPT-4 and Gemini preferred generated reports in 70.8-100% of comparisons while humans preferred analysts' reports 83.3% |
| FinEval-KR | Knowledge vs reasoning attribution | Qwen2.5-72B judge finds first wrong step | 0.92-0.94 agreement with experts on error identification and attribution (a narrow, checkable judgement) |
| SECQUE, CFA Level III, FinRpt and others | (13a, 13b) | Judge vs gold answer; rubric | 0.70-0.75 agreement at best (13a, 13b) |

- **Empirical finding.** Holistic grading of analyst write-ups is unreliable in finance as
  elsewhere: human raters barely agree (kappa 0.171) and LLM judges favour model-written reports.
  Grading is reliable when it checks a narrow, verifiable unit (a figure within tolerance, a
  condition label, a located error).
- **Empirical finding.** Scores drop with the level of analysis: recognition 59.5, calculation
  44.6, abstraction 44.8, interpretation 20.3 for the best agents (FinDeepResearch); open-ended
  analysis is weak for frontier systems before any small model is involved.
- **Gap.** No open-analysis benchmark reports judge agreement for a small model's output against a
  large model's, which is the comparison S1 needs (13b raised the same point).

**4. Judgements checkable against later outcomes**

- **Empirical finding.** From a whole annual report, the sign of next-year profit change is near
  chance for most LLMs (AUC 0.40-0.62), best 0.65 (GPT-5, MCC 0.21); logistic regression on the
  summary table 0.56; a 1B fine-tuned model 0.48-0.52 (`sugiura-2026`). Kim, Muhn and Nikolaev's
  higher figure is withdrawn (stream 12) and Li et al. 2024 found GPT-4 Turbo's EPS forecasts less
  accurate than analysts' (stream 02).
- **Empirical finding.** Restatement-derived fraud labels are learnable from figures: random forest
  0.75, best LLM 0.73 with text, the 1B model 0.66 from tables, falling to 0.54 when narrative text
  is added (`sugiura-2026`). AuditFraudBench builds labels from AAERs and restatements but two of
  its three tasks have a single gold class, and on the third Qwen3-8B (0.505) is level with GPT-5.5
  (0.522).
- **Empirical finding.** Small open models turn 10-Q disclosures into weak but non-zero return
  rankings (event-day RankIC 0.025-0.075; Qwen2.5-7B 0.052), with mixed effects of size; all on
  2001-2024 data with identity masking as the only control (Wang et al. 2026). `koijen-2026` (13b)
  gives the cleanest prospective design.
- **Verified fact (signals that are not revision labels).** Signals used in the sources that S1
  could check without comparing consecutive releases' guidance: next-period as-filed fundamentals
  (EDINET's profit sign; S1's R4 uses next-quarter XBRL); restatement or amendment of the period
  (EDINET's amended reports; on EDGAR, 10-K/A and 8-K Item 4.02 non-reliance notices); SEC
  enforcement releases (AuditFraudBench); announcement-window abnormal returns (`koijen-2026`,
  Wang et al. 2026).
- **Hypothesis (ours).** A further check that stays within one quarter: the 10-Q or 10-K for the
  same period, filed after the release, carries full XBRL with segment detail, and can confirm or
  refute a driver claim made from the release ("growth came mainly from segment X"). It is a later
  document, not a later outcome, so it tests reading, not forecasting.
- **Consequence (our inference).** Outcome-checkable judgements do not separate a 0.8B from a 4B:
  everyone is near chance on direction, and a 1B fine-tuned model is at chance. They can be a
  secondary probe; they cannot show a framework.

**5. What a small model can be good at, and where size or knowledge is the bottleneck**

| Task family | Evidence | Reading |
|---|---|---|
| Closed-label judgement on given facts (attribution, sentiment, rule compliance) | BizFinBench event attribution, Qwen3 1.7B/4B/14B/32B: 77.4 / 83.6 / 84.2 / 83.8; DianJin-R1-7B compliance 94.5; BERT students within 2.2 points of GPT-4o on formal sentiment text and 4.4 above it on tweets (accuracy); AuditFraudBench pattern class 8B = frontier | Saturates by about 4B; distillable in distribution |
| Applying a fixed procedure on a familiar format | DianJin compliance workflow; Phogat et al. (05) 3.8-14B students 71.6-77.6 against GPT-4 77.5 on FinQA (13a) | Distillable, in distribution |
| Numeric chains | BizFinBench numeric 35.8 / 47.4 / 58.2 / 59.6; FinAR indicators at 5% tolerance Qwen2.5-7B 46.6, Mistral-7B 18.9, against 88.0-90.6 | Size-bound; S1 already offloads to a calculator |
| Period and time reasoning (derived quarter, YTD, TTM) | BizFinBench time reasoning 33.4 / 50.0 / 65.8 / 64.6; FinIndices and XFinBench temporal (13a) | Steepest size curve in the sources; EXP-0050 R1.7 at everyone's floor |
| Extraction and entity recognition from varied layouts | BizFinBench entity recognition 11.2 / 25.2 / 50.7 / 49.2; FinAR extraction precision 38-66 (under 10B, untuned) against 97-100 | Size-bound untuned; stream 05 shows extraction is tunable at small sizes in a narrow format |
| Knowing which concept or formula applies | FinEval-KR: knowledge necessary but not sufficient, "apply" lowest for all, smallest finance model lowest knowledge score; FinIndices no-hint drop (13a); FinAR: formulas give small models "minimal or even negative" gains | Knowledge plus application; hints do not rescue small models (as in EXP-0050) |
| Outcome prediction | EDINET earnings 0.48-0.65 for all; BizFinBench stock prediction flat at 48.5-52.3 across sizes | Nobody is good; not a place to show skill |
| Open interpretation and synthesis | FinDeepResearch interpretation 20.3 for frontier agents; CFA Level III essays 8B 38.9 against about 80 (13a) | Bottleneck for all sizes; grading unreliable |

- **Hypothesis (synthesis).** A 0.8B can be made reliable on closed-label judgements over facts it
  is given or has extracted correctly, and on a fixed procedure over a familiar format, with the
  arithmetic done by the calculator. It will be limited by extraction across unfamiliar layouts, by
  period derivation and by multi-period combination, and it will not do open interpretation well.
  This matches EXP-0050's pattern (4B headroom on R1.1, R1.3-R1.5, R1.8; R1.7 at everyone's floor).

## Look-ahead and memorisation across the stream

Specialist papers do not count contamination: DianJin-R1 and ODA-Fin report no check; Agentar-Fin-R1
and Agentar-DeepFinance-100K say overlaps were removed without counts, and both use FinQA for
training and test. Trading-R1's test window lies inside its data window. Benchmarks computing labels
from filed statements (FinAR-Bench, FinDeepResearch up to calculation) avoid outcome recall, not
pretraining exposure. Outcome studies run on pre-cutoff filings: EDINET-Bench tests name-guessing
(at most 0.05) and year trends; Wang et al. 2026 masks identities on one model; AuditFraudBench does
nothing. None is clean under rule 2. S1's design (post-2026-06-30 test releases, company-disjoint
split) is stricter than every source here.

## Design implications for a 0.8B finance-analysis specialist

1. **Make the framework an explicit analysis graph and have the teacher run it.** Nodes for a
   release: (N1) extract the needed line items for both periods; (N2) compute indicators with the
   calculator (margins, growth, point changes, effective tax rate, share-count change); (N3) mark a
   condition table (trend, threshold, comparison; R1's labels are such conditions); (N4) answer by
   citing the conditions; (N5, later) a two-sentence synthesis restricted to marked conditions.
   The 4B, 9B or gpt-oss-20b runs the graph; every node is checked by rule against XBRL; failed
   traces are repaired or dropped; passing traces are merged into one chain for the student
   (`zhu-2025`, `wu-2025`, `zhao-2025`; Fin-PRM for step-level filtering). Generate forward; never
   write a rationale from the gold label (`xiao-2025`, `turpin-2023`).
2. **Never train answer-only; mix answer formats in every batch.** EXP-0050's boxed-number
   collapse, Agentar's answer-only hard items below base, and ODA-Fin's raw-answer SFT (-5.4) all
   point the same way.
3. **Choose the teacher and chain length on the student's dev result.** Compare 4B, 9B and
   gpt-oss-20b traces and long, short and mixed chains by what the 0.8B learns (`zhao-2025`,
   `li-2025`), not by teacher accuracy.
4. **Test a framework, not a template.** Report node accuracy (N1-N3) and answer accuracy separately,
   numbers at 1% and 5% tolerance and exact (`wu-2025`). A framework shows as node accuracy that
   holds on: (a) held-out R1 templates; (b) held-out combinations of trained nodes (train margin
   direction and tax line, test operating leverage and EPS against net income); (c) a held-out node
   (an indicator never asked in training but computable from extracted lines); (d) a release-level
   condition table answered in one pass, when training only asked one condition at a time; (e)
   unseen companies and release layouts, with and without the prose around the tables
   (`sugiura-2026`: text hurt the 1B); (f) the planned flip and hold twins; (g) consistency of the
   answer with the student's own stated conditions (13b). A template learner passes trained
   templates and fails (b)-(d).
5. **Baselines beside every result.** The untuned 0.8B of the same generation (B0, 55.9 on R), the
   4B teacher, code on XBRL, and for any outcome item a classical classifier on the same figures
   (random forest matched the best LLM in `sugiura-2026`).
6. **Keep outcome items secondary.** Use next-quarter as-filed XBRL and restatement events (8-K
   Item 4.02, 10-K/A) as labels, not guidance revisions; expect near-chance results for every model
   (`sugiura-2026`).
7. **RL is optional and small.** If used, reward the rule-checked nodes as well as the answer (an
   analogue of Fin-PRM's +3.3 at no labelling cost) on hard, verifiable, short-answer items (ODA-Fin's
   best cap was 16 answer tokens), and watch untargeted templates for losses (DianJin FinQA -2.6).
8. **No holistic judge.** Any free-text output (R5) is graded claim by claim against rule-checkable
   conditions (Goldsack et al.: kappa 0.171 among human raters; judges prefer model text).
9. **Prior for the result (hypothesis).** Expect the distilled 0.8B to learn N3-N4 (judgements given
   correct figures) close to the teacher, to lag on N1 for unfamiliar layouts and on derived periods,
   and to gain little on open synthesis. Node accuracy that holds on held-out combinations would be
   new evidence; no source tests it.

## Reusable

- FinAR-Bench's 64-condition list (Table 8) and code (GitHub; licence not checked) as a starting
  list for a release-level condition table on US releases; its tolerance-sweep reporting.
- DianJin-R1's workflow-merge recipe (no data released).
- HisRubric's four levels (recognition, calculation, abstraction, interpretation) as a reporting
  frame for S1 results by node.
- EDINET-Bench's design for restatement labels and its classical baselines (code and data public).
- BizFinBench's Qwen3 1.7B-32B curve per task type as a prior for what scale buys.

## Gaps that suggest an experiment

- No finance distillation study with a generative student below 3.8B; none tests whether a distilled
  procedure transfers to held-out templates, combinations or nodes. S1 R-d would be first.
- No specialist paper measures reasoning or thesis quality, or counts contamination.
- No outcome-checkable benchmark on US earnings releases filed after model cutoffs with small models.
- No judge-agreement figure for finance analysis written by small models against large ones.

## Not triaged

Shaffer and Wang (2024), core earnings from 10-Ks (SSRN 4979501): SSRN returned 403; stream 10's
lead stays unverified. RAG-IT (arXiv 2412.08179): abstract seen, three companies, no numbers; not
relied on. Not opened, nothing claimed: XuanYuan-FinX1, LLM Pro Finance Suite (2511.08621),
FinMA/PIXIU, InvestLM, FinTral, FinMaster (2505.13533), Automating Financial Statement Audits
(2506.17282), "Is GPT-OSS All You Need?" (2512.14717), dependency-aware CoT compression for finance
(2609.00413), FinExam-10K (2608.28155), Point-in-Time Encoders for Earnings Calls (2611.14325).

## Limits of this pass

All reads used an automated reader of arXiv or ACL Anthology pages; no number was checked against a
typeset PDF. Several sources contain internal inconsistencies, flagged in the notes and CSV rows
(Agentar data counts, Trading-R1 test window and Sharpe, FinAR split and table values, EDINET
industry total). Wang and Brorsson (2025) could be read only as an abstract (the PDF could not be
parsed), so the one source naming DuPont and Altman Z-score tasks contributes nothing quantitative.
FinDeepResearch was read in its v1 HTML; the current version is v2 (7 January 2026).
