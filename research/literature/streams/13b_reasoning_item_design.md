# Stream 13b: how to build and grade reasoning items

Sources checked 2026-11-23, for sub-study S1 (`../../design/substudy_s1_distill_prune.md`).
Notes are in `../papers/`; all 25 rows are in `13b_reasoning_item_design.csv`: 8 deep reads and
17 triaged rows (abstracts, plus Section 4 of V-FiLLM). Seven deep notes are new; the eighth
paper (CFA Level III) was deep-read by stream 13a at the same time, so its note is
`shetty-2025-cfa-level-iii-evaluation` and this stream adds only the per-model grader gaps.
Stream 13a also triages FinChain (`xie-2025`, read in full here) and Patel et al. 2025. Stream
13a covers which financial reasoning benchmarks exist and the small-against-large evidence; this
stream covers only how items are built and graded. Streams 03, 08 and 09 already cover look-ahead, blinding and
memorisation; this synthesis cites them rather than repeating them. Existing notes used here:
`lanham-2023`, `turpin-2023`, `sprague-2025`, `halawi-2024`, `levy-2026`, `jiang-2026`,
`kim-2024` (withdrawn; method only).

The question: EarningsExam B1 (lookup) and B2 (computation) test what plain code already does.
The owner wants items that test trend judgement, combining several facts, and financial logic,
and asks how to write such items so that the results can be trusted. "Trusted" here means four
things: the gold is right, the item cannot be answered from memory, the grade agrees with what an
expert would give, and a right answer reflects the reasoning the item claims to test.

## What the stream establishes

**1. Generating items that test procedure rather than recall**

- **Convention.** Write each item as a template with typed slots, validity conditions and the
  answer computed from the slots; instantiate many times. GSM-Symbolic (100 templates by 50
  instances), FinChain (290 executable finance templates, each printing its own gold step chain),
  V-FiLLM (computation trees over table cells), functional MATH (`mirzadeh-2024`, `xie-2025`;
  triaged: Srivastava et al. 2024, Larsen et al. 2026). EarningsExam B2 already follows this
  pattern.
- **Empirical finding.** The same template gives very different scores across instantiations:
  best and worst of 50 datasets differ by more than 12 points for a 9B model, and for 21 of 25
  models the original benchmark score sits more than one standard deviation above the variant
  mean (`mirzadeh-2024`). Functional snapshots of MATH show "reasoning gaps" of 58% to 80%
  (Srivastava et al., abstract).
- **Empirical finding.** Changing numbers hurts more than changing names; each extra required
  clause hurts small models much more than frontier ones (Llama3-8B 74.6 to 12.3 with two added
  clauses; GPT-4o 94.9 to 88.0); an irrelevant clause cuts accuracy by up to 65%
  (`mirzadeh-2024`). In finance tables, corrupting cells the question does not use drops accuracy
  by up to 47 points, and a unit or scale shift takes one 31B model from 98.4 to 3.0 (V-FiLLM,
  Section 4).
- **Empirical finding.** Counterfactual variants that change a task's default rules leave models
  above chance but consistently worse (Wu et al. 2024, abstract).
- **Verified fact (from stream 08).** On financial statements, recall keys on exact numerals:
  perturbing digits removes an LLM's apparent skill at predicting earnings direction
  (`levy-2026`). For S1 this cuts both ways: perturbation is the contamination control, and an
  item a model answers only on unperturbed numbers is a recall item.
- **Verified fact (from stream 04).** Contrastive minimal pairs exist for financial news; models
  do far better when shown both members than one (`jiang-2026`). Present pair members separately
  and score consistency afterwards.
- **Empirical finding.** Mirrored comparison pairs ("is X larger than Y" and "is Y larger than
  X") expose rationalised answers: up to 13% of pairs contradictory in production models, under
  0.4% for frontier reasoning models (Arcuschin et al. 2026, abstract).
- **Empirical finding.** Logical consistency across related questions can be scored with no
  gold; the conditional-type checks correlated up to 0.92 with eventual Brier score across
  forecasters, negation-type checks were unstable, and forcing consistency did not improve
  accuracy (`paleka-2024`).
- **Gap.** No paper found builds judgement items (direction, driver, ranking) from real earnings
  releases with gold computed from as-filed structured data. FinChain and V-FiLLM are synthetic;
  FinForge uses LLM-generated questions with human validation (abstract).

**2. Outcome-grounded items**

- **Empirical finding.** The cleanest published design scores predictions in real time: prompts
  frozen before each earnings announcement, the label (one-day abnormal return, as a
  within-quarter percentile rank) arrives afterwards, and the score is the R-squared increment
  over the earnings surprise. On 1,849 Q4 2025 announcements the surprise alone gives 5.0%, Opus
  4.5 on call transcripts 14.3% with the surprise, and 17.1% with an optimised rule book
  (`koijen-2026`).
- **Empirical finding.** A rule book written by the large model raised small models close to the
  large one (Haiku 4.5 11.7% against Opus 14.1%) (`koijen-2026`).
- **Convention.** Dynamic benchmarks keep labels clean by asking only about events unresolved at
  submission (ForecastBench, abstract; `paleka-2024`). Pre-cutoff outcome benchmarks with
  imbalanced labels report misleadingly high accuracy (FinCall-Surprise, abstract).
- **From streams 03, 08, 09 (not repeated):** test only after every cutoff; masking does not hide
  large firms; a null recall probe is a lower bound. Nothing in this pass changes those defaults.
- **Our inference.** Outcome labels are noisy: even the best system explains under a fifth of
  return variance. Such a section can rank a frontier model against a nano model on about 1,850
  events with wide intervals; it will not resolve a three-point gap between S1's 0.8B and 4B on a
  few hundred test releases.

**3. Grading open-ended analysis**

- **Empirical finding.** On general chat, a strong judge agrees with humans over 80% of the time,
  about as often as humans agree with each other (Zheng et al. 2023, abstract). In expert
  domains the figure drops: judge-expert 60% to 68% against expert-expert 72% to 75%, and the
  judge sides with lay users (76% to 80%) and with longer answers (`szymanski-2024`).
- **Empirical finding.** In finance, a GPT-4.1 rubric grader on CFA Level III essays was 5.6
  points harsher than one certified human grader on average, with 70.4% exact agreement, and its
  bias varied by the model graded, from -3.3 to +14.1 points (`shetty-2025-cfa-level-iii-evaluation`).
- **Empirical finding.** Judge severity varies widely across judges and shifts with every model
  version; judge-human correlations on essays .47 to .56 (Sunkavalli 2026, abstract). Swapping
  response order flipped a pairwise comparison (Wang et al. 2023, abstract).
- **Empirical finding.** Grading improves sharply when the judge has something specific to check.
  With a reference answer, a 1.7B matcher reaches Scott's pi 0.97 on maths against 0.72 for a
  frontier judge without one, and small matchers reach human-human agreement on MMLU-Pro and
  GPQA; multiple choice scores 0.26 and can often be answered from the options alone
  (`chandak-2025`). With item-specific binary criteria graded one at a time, GPT-4.1 matches the
  typical physician (macro F1 0.709; physicians agree 55% to 75%), while a nano grader drops to
  0.58 (`arora-2025`). Splitting text into atomic claims and checking each gives automated error
  under 2% for biographies (FActScore, abstract).
- **Verified fact.** Finance report benchmarks (FinRpt, Deep FinResearch Bench, FinReasoning)
  score analyses on rubrics that separate data accuracy, claim verifiability and insight; their
  abstracts report no agreement with human experts.

**4. Process quality**

- **Empirical finding.** Final answers and reasoning chains diverge: in FinChain, DeepSeek-R1's
  step score is 51.22 and its final-answer score 28.97, GPT-4.1's 65.34 and 84.66 (our reading;
  different scales). Similarity-based step metrics agree only moderately with experts (best
  Spearman 0.655 on 100 responses; BERTScore 0.287) (`xie-2025`).
- **Empirical finding.** Learned step verifiers do not generalise beyond the data they were built
  on; prompted critics do better (ProcessBench, abstract). Process supervision does beat outcome
  supervision for training (Lightman et al. 2023, abstract).
- **From stream 12 (not repeated):** reasoning is often post hoc for items the model can answer
  directly and gets more so as models grow (`lanham-2023`); stated reasons can omit what drove the
  answer (`turpin-2023`); reasoning helps mainly on symbolic steps, code more so
  (`sprague-2025`).
- **Our inference.** For S1, the reliable process checks are the ones with a gold: the
  intermediate figures a model states (checkable against the template's printed step chain) and
  whether the answer changes when the facts change (perturbation dependence). Text-similarity of
  reasoning and LLM judgement of "reasoning quality" are the weakest options.

## What the evidence says about LLM judges, in one paragraph

A model judge is reliable when it checks something specific against a reference: equivalence of
a short answer, or whether one stated criterion is met. It is unreliable when it gives a
holistic score or a preference: it rewards length, depends on order and version, and its bias
differs by whose answer it grades. The last point matters most for S1: the comparison is between
a distilled 0.8B and its 4B teacher, whose styles differ, and a judge whose bias depends on style
could create or hide a three-point gap by itself. Agreement must be measured against the
human-human ceiling for the same items, and in S1's case that ceiling is the owner's own
test-retest agreement. Under rule 6 no roster model may grade items whose gold it sees, and small
graders are worse; so any judge is a pinned, non-roster model validated on an owner-graded
sample, or a rule.

## Design defaults

- **Rule 2, clean tests only: supported.** Every outcome-grounded design that claims to be
  free of look-ahead tests only after the cutoff (`koijen-2026`, ForecastBench). Template
  regeneration adds protection against memorised items but does not replace the post-cutoff
  rule: perturbed pre-cutoff text is still recognisable (streams 08, 09).
- **Rule 8, simple baselines first: supported and sharpened.** For judgement items the baseline
  is code that applies the same rule to extracted figures; an LLM's value is shown only where it
  beats that baseline on raw release text, or on outcome items where the rule is unknown.
- **S1 design rule 3, held-out templates: supported** (`mirzadeh-2024`; Srivastava et al.).
  Add held-out variant types (numbers-only, irrelevant line, extra required fact).
- **S1 design rule 5, boxed answer with a tolerant numeric grader: supported** for numbers;
  extend to categorical answers (direction, segment name, ranking) graded by exact match after
  normalisation (`chandak-2025`).
- **S1 design rule 6, bootstrap clustered by company: supported; add clustering by template**
  (`mirzadeh-2024`).
- **Excluded by S1 design rule 1:** guidance-revision labels. Outcome items below must not use
  Benchmark v0's revision gold.
- **Contamination labels: unchanged.** Template items on post-cutoff releases are clean; the same
  templates on pre-cutoff releases are bounded at best.

## A menu of item families for an S1 reasoning exam

All families use the existing machinery: EX-99.1 excerpts, figures verified by two sources (rule
parser and as-filed XBRL), company split v1, a 400-token excerpt cap, boxed answers. Cost is
relative to building B2.

**F1. Multi-fact judgement calls (direction, driver, ranking).**
- *Tests:* combining two to four facts under a stated financial rule: is margin expanding or
  contracting and is cost growth or revenue growth the cause; is growth accelerating against the
  prior quarter; which segment contributed most to the change in operating income; rank the
  contributions to EPS growth (revenue, margin, share count, tax rate); did the GAAP to non-GAAP
  gap widen.
- *Generation:* templates over verified current, prior-quarter and prior-year figures in the
  release; the gold is computed by rule, with a materiality band (for example "flat" within 0.5
  percentage points) fixed before generation; the template prints its intermediate figures as the
  step chain (`xie-2025`). Vary the number of required facts as the difficulty axis
  (`mirzadeh-2024`).
- *Grading:* exact match on a short categorical answer; stated intermediate figures checked
  against the step chain within the numeric tolerance; answer accuracy and step accuracy reported
  separately.
- *Contamination:* as B1/B2: clean on post-cutoff releases.
- *Cost:* low; new templates only. Caveat for the owner: each answer is code-computable once the
  figures are extracted. What it tests is whether the model picks the right facts from prose and
  tables and applies the rule, which is where small models fail as facts are added. The
  code-on-XBRL baseline must be reported beside it.

**F2. Counterfactual twins and invariance controls (built on F1).**
- *Tests:* whether the judgement follows the numbers. For each F1 item: a flip twin (one figure
  changed, with dependent totals recomputed so the statements still add up, so that the correct
  answer changes) and a hold twin (an irrelevant line inserted, a figure the question does not use
  changed, or units restated; the answer must not change). Mirrored comparisons ("A larger than
  B?" and "B larger than A?") and conditional consistency sets ("margin up?" with "costs grew
  slower than revenue?") on the same release.
- *Generation:* by rule from the F1 template; twins shown in separate calls (`jiang-2026`).
- *Grading:* accuracy on each member plus pair scores: flip rate on flip twins, stability on hold
  twins, contradiction rate on mirrored pairs and consistency sets (`paleka-2024`, Arcuschin et
  al.). Consistency is a diagnostic and never a training target.
- *Contamination:* low, since perturbed figures are not in any training data; the original-
  against-twin gap doubles as a recall probe on pre-cutoff releases (`levy-2026`).
- *Cost:* low once F1 exists; doubles or triples model calls. Risk: an edit that breaks an
  accounting identity creates a wrong gold; a checker of identities is required.

**F3. Outcome-grounded calls, scored prospectively.**
- *Tests:* judgement where no rule gives the answer: from this quarter's release (and the prior
  one), will next quarter's reported revenue growth (or operating margin) be higher or lower than
  this quarter's; optionally the rank of the announcement-day abnormal return within the quarter.
- *Generation:* items are written from post-cutoff releases as they arrive; labels come from the
  next quarter's as-filed XBRL (or prices) once filed.
- *Grading:* Brier score or AUC for directions, rank correlation or R-squared increment for
  returns, always against baselines (persistence; seasonal random walk; earnings surprise)
  (`koijen-2026`). Balanced metrics because labels are imbalanced.
- *Contamination:* clean by construction (prospective). Must not touch Benchmark v0 revision
  gold.
- *Cost:* item generation is cheap; the cost is time (one quarter per label batch) and power.
  Returns need a price source the project does not have yet. Expected to separate frontier from
  small models, not the 0.8B from the 4B (our inference from the effect sizes).

**F4. Short analysis graded claim by claim against a generated rubric.**
- *Tests:* integration and prioritisation in free text: "In three sentences, what changed most
  this quarter and what does it imply for next quarter?"
- *Generation:* for each release, a rubric of binary criteria generated from the gold figures:
  positive criteria (names the largest change; states its direction correctly), negative criteria
  (any stated figure off by more than the tolerance; any direction contradicted by the data; a
  claim about a quantity not in the excerpt) (`arora-2025`, FActScore).
- *Grading:* claims extracted and checked one at a time, by rule where the claim is numeric and by
  a pinned non-roster judge where it is verbal; the forward-looking sentence scored only through
  F3 labels or left ungraded. Judge validated on an owner-graded sample (about 200 criteria),
  agreement reported against the owner's test-retest rate, separately for each evaluated arm
  (`shetty-2025-cfa-level-iii-evaluation`). Length controlled or capped (`szymanski-2024`).
- *Contamination:* as B1/B2 for the facts; low for the free text.
- *Cost:* highest: judge calls, owner time for validation, and a residual risk that the judge's
  bias differs between the student and the teacher. A cheaper proxy is to convert the rubric into
  unique-answer questions (F1) and grade by matching (`chandak-2025`).

**Cross-cutting: a process check on every family.** Log the reasoning; check stated figures
against the step chain; measure answer dependence with the flip and hold twins and, for a subset,
by truncating or corrupting the reasoning and re-asking (`lanham-2023`). Report where right
answers come with wrong stated figures.

**Suggested order (judgement).** F1 with F2 first: cheap, auto-graded, clean, and aimed at the
skill a distilled student is most likely to lose. F3 starts collecting now because its labels
take a quarter to arrive, and is reported as prospective and secondary. F4 only after F1 and F2
show a gap worth explaining.

## Gaps

- No published benchmark builds judgement items from real earnings releases with as-filed gold;
  F1 and F2 would be new.
- No study measures whether an LLM judge's bias differs between a distilled student and its
  teacher; the CFA result (bias varies by graded model) says it can.
- No study tests numbers-only perturbation with statements kept internally consistent on real
  filings (stream 08 found the same gap for blinding).
- No outcome-grounded study uses the 8-K press release alone, rather than the call transcript, as
  input.
- Expert-expert (or owner test-retest) agreement on finance analysis criteria is unmeasured.

## Limits of this pass

- Seven of the eight deep reads used machine extractions of arXiv HTML, partly truncated (stated
  in each note);
  `koijen-2026` was read through a crude local text extraction of the PDF, and its slides could
  not be read. No number was checked against a typeset PDF.
- Triaged rows rest on abstracts (V-FiLLM also Section 4). The per-matcher agreement values of
  `chandak-2025` are in a figure not read.
- Not opened, nothing claimed: Prometheus and other trained judge models; G-Eval; RusFinChain
  (arXiv 2607.01388); Ivanova et al. on the statistics of GSM-Symbolic; the full texts of the
  finance report benchmarks; LiveBench and other contamination-limited dynamic benchmarks.
- Benchmarks of financial reasoning as such (FinQA, TAT-QA, FinanceBench and others) are left to
  stream 13a.
