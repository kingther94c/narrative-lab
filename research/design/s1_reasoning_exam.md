# S1 reasoning exam (section R): design draft

Status: **design draft, 2026-11-23; the owner took every recommended option in §9 the same day
("D 全按推荐"). Nothing here is pre-registered; each step that tests a hypothesis gets its own
registry entry.**
Sources: literature streams 13a (`../literature/streams/13a_financial_reasoning_benchmarks.md`)
and 13b (`../literature/streams/13b_reasoning_item_design.md`), and the S1 plan
(`substudy_s1_distill_prune.md`). Numbers in examples are made up.

## 1. The question

So far S1 tests two skills: reading one figure (B1) and doing one calculation (B2). With a
calculator, the distilled 0.8B is within about 3 points of the 4B (EXP-0016). The owner's point (2026-11-23) is that both
skills are things code already does. What an LLM could add is the analyst's logic: working out
*what* to compute, combining several facts, judging direction and cause, and saying what the
quarter means. The question for section R:

> Does a small model keep up with a larger one when the task is reasoning over a release rather
> than reading or arithmetic, and does distillation carry that skill down?

The literature does not answer this for models below 1.5B (13a). Where small finance models
have been tested outside the format they were tuned on, they fall far behind frontier models. On
FinIndices, with formulas given, a tuned 7B scores 11% on single values and 0% on tables, against
about 79% and 70% for frontier models (`tong-2026`).

## 2. What "reasoning" means here, in testable terms

Four abilities, each with a check that does not depend on trusting the model's prose:

| Ability | What code cannot supply | Check |
|---|---|---|
| Knowing what to compute | The question names the goal, not the formula | Same item with and without a formula sheet; the gap is the measure |
| Combining several facts under a financial rule | Picking the right two to four figures out of a real table and applying the rule | Categorical answers fixed by rule; step figures checked |
| Following the numbers rather than the story | Changing the conclusion when, and only when, the facts change | Flip and hold twins |
| Judgement with no rule | What happens next quarter | Prospective labels, against persistence baselines |

The calculator stays on in every arm, so arithmetic is not what is measured.

**An honest caveat.** Every item with a rule-made gold can be answered by code, once someone has
extracted the figures and written the rule. A code baseline on XBRL scores 100% by construction.
Rule-made items therefore test whether the model can do that analyst's work from raw release text,
with no one naming the rule. Only the prospective family (R4) and open analysis (R5) test
judgement that no rule gives. They are also the noisiest and dearest to grade.

## 3. Item families

All families reuse the EarningsExam machinery:
- EX-99.1 excerpts;
- figures verified by two sources (the rule parser and as-filed XBRL);
- company split v1;
- boxed answers;
- clustering by company.

Test items come from post-cutoff releases of test companies. As in B, Claude never reads test
items.

### R1. Multi-fact calls (primary)

Each item needs two to four verified figures and a rule fixed before generation. Answers are
short labels or numbers. Candidate templates, all within what company facts can verify:

| Template | Example question (made-up numbers) | Gold | Facts |
|---|---|---|---|
| R1.1 margin direction | Did operating margin expand, contract or stay flat (within 0.5 points) year on year? | label from two margins | 4 |
| R1.2 operating leverage | Revenue and operating income: did both rise, both fall, or move apart? | 4 labels | 4 |
| R1.3 cost against sales | Did operating expenses grow faster or slower than revenue? | label | 4 |
| R1.4 EPS against net income | Did diluted EPS grow faster or slower than net income, and so did the share count help or hurt? | label | 4 (diluted shares verified) |
| R1.5 tax line | Did net income grow faster than pre-tax income? | label | 4 |
| R1.6 biggest mover | Which of gross profit, R&D and SG&A changed most in dollars year on year? | line name | 6 |
| R1.7 derived period | The release shows six months and the second quarter. What was first-quarter revenue? | number, XBRL Q1 confirms | 2 |
| R1.8 margin change in points | By how many percentage points did gross margin change? | number | 4 |
| R1.9 not answerable | Asks for a figure or period that the excerpt does not contain | "cannot be determined" | — |

- **Difficulty.** The number of facts required is the difficulty axis. Accuracy falls fastest
  for small models as facts are added (`mirzadeh-2024`).
- **Distractors.** Excerpts keep their year-to-date and prior-year columns as distractors.
- **Step chain.** Each template prints the step chain (the figures used and the intermediates),
  so figures the model states can be checked against it (`xie-2025`).
- **Hint protocol.** Number templates (R1.7, R1.8) and two label templates run in two arms: with
  a one-line formula sheet and without one. The calculator is on in both.
- **Grading.** Exact match after normalisation for labels; the B tolerance for numbers.
  - Scores are chance-corrected for labels (balanced accuracy, or Cohen's kappa against gold),
    never raw accuracy alone.
  - A label item also reports "step accuracy": whether the figures the model wrote match the step
    chain. Right answers that come with wrong figures are counted separately. EXP-0016 showed the
    4B often writes the wrong conversion and answers correctly anyway.
- **Not in v1:**
  - Segment items need dimensional XBRL, which company facts do not carry, so they fail the
    two-source rule (decision D3).
  - Non-GAAP items have no XBRL source at all.
  - The "accelerating or not" template needs the previous release's figures. Those come from a
    pre-cutoff release, so the item would only be bounded for contamination. It is held for v2.

### R2. Twins (primary diagnostic, built on R1)

**Flip twin.** Change one figure that the answer depends on and recompute the dependent totals,
so that the statement still adds up and the right answer changes.

**Hold twin.** Make an edit the answer does not depend on. Options:
- insert an irrelevant line;
- change a figure the question does not use;
- restate the units.

**Mirrored pairs.** Ask "A > B?" and "B > A?".

**Scoring.** Each twin is scored on its own. Pair scores are:
- the flip rate on flip twins;
- stability on hold twins;
- the contradiction rate on mirrored pairs.

**Rules.**
- Each twin is shown in a separate call.
- Edited statements are rebuilt from the figures. An identity checker (gross profit = revenue −
  cost; operating income = gross profit − operating expenses; net income consistent with EPS ×
  shares within rounding) rejects any twin that breaks an identity.
- **Why it matters:** one irrelevant clause costs models up to 65% on GSM-Symbolic, and corrupted
  unused cells cost up to 47 points on V-FiLLM (13b).
- **Bonus:** on pre-cutoff releases, the gap between the original item and its twin doubles as a
  recall probe.

### R3. External probes (off-target, like section A)

FinIndices (hint and no-hint protocol) and the XFinBench validation split (temporal reasoning,
scenario planning; auto-graded) as fixed outside references.
- Both are public and pre-cutoff, so they are treated as contaminated. They are used only to
  measure change from each model's own baseline.
- Using them needs a download and a licence check (decision D4).

### R4. Prospective calls (secondary; start collecting now)

**The question.** From a release, will next quarter's year-on-year revenue growth (or operating
margin) be higher or lower than this quarter's?

**Labels.** Labels come from the next quarter's as-filed XBRL.

**Data available now.** The current company-facts snapshot (2026-11-14) already holds the third
quarter for most companies with a second-quarter release in the test pool. So one batch of
second-quarter-to-third-quarter items could be built now, and each later quarter adds one batch.

**Scoring.** Brier score and balanced accuracy against two baselines: persistence (no change)
and the seasonal random walk.

**Power.** The expected effects are small (`koijen-2026`), so R4 is unlikely to separate the
0.8B from the 4B. It is reported as prospective and secondary.

**Boundary.** It must not touch Benchmark v0's revision gold (S1 design rule 1). It also sits
close to S2's ground, so S2 should be consulted before it is built.

### R5. Short analysis graded claim by claim (later)

**The prompt.** "In three sentences: what changed most this quarter, and what does it imply?"

**Grading.**
- A rubric of yes/no criteria is generated from the gold figures:
  - names the largest change;
  - gets its direction right;
  - no stated figure is off by more than the tolerance;
  - no claim is made about a figure absent from the excerpt.
- Numeric claims are checked by rule. Verbal claims go to a pinned judge that is not a roster
  model.
- The judge is validated against about 200 criteria graded by the owner, separately for each
  model compared.

**Why it waits.**
- On CFA essays, the judge's bias changed by up to 17 points depending on which model was graded
  (`shetty-2025-cfa-level-iii-evaluation`), more than the gap S1 measures.
- Open-ended judges agree with experts only 60–68% of the time (13b).
- So R5 is built only if R1 and R2 show a gap worth explaining.

## 4. Baselines reported beside every R result

- Chance, and majority class, for labels.
- Code on XBRL figures: 100% on R1 by construction. Reported so that no one reads R1 as beyond
  code.
- Code on the release text through the B1 parser: what a pipeline gets with no LLM at all.
- The 4B, tool-free and with the calculator, as the upper rung. The calculator interface is fixed
  first; see §8.
- For R4: persistence and the seasonal random walk.

## 5. Size and statistics

- **Size.** About 1,500 R1 base items from at least 400 companies, plus their twins, gives about
  3 points of detectable difference on paired items (S1 plan §3 rule 6).
- **Bootstrap.** Clustered by company and by template (13b adds the template level).
- **Template spread.** Several generated variants per template, reported as a spread
  (`mirzadeh-2024`: more than 12 points between variant sets for one 9B model).
- **Held-out families.** Some R1 templates appear only on test. Distillation gains in finance
  have not survived a change of format (`tong-2026`, `qian-2025`).

## 6. The steps, in order

| Step | What | Machine | Rough cost |
|---|---|---|---|
| R-a | Build R1, R2 and R1.9 for train, dev and test. Report yield per template, verification failures and identity-checker rejections. Engineering only, no hypothesis | CPU | 1–2 days of work |
| R-b | Headroom: 4B (with and without calculator), the 0.8B base, C, and EXP-0017's best arm, on dev R items, with and without hints, plus twins | MLX | about 6–10 h |
| R-c | Pre-registered test: is the 0.8B–4B gap on R larger than on B? Does it widen without hints and on twins? | MLX | about 10 h |
| R-d | Distillation on R: 4B-written labels on train R items, held-out families on test, short and mixed reasoning chains (`li-2025`) | MLX | about 20–25 h |
| R-e | R4 batch 1 (second quarter to third quarter), descriptive, against baselines | CPU + MLX | about 4 h |

**R-a done** (EXP-0019, 2026-11-24): test 16,329 base items from 1,548 companies (40,538 with
twins), dev 4,289 from 295, train 3,352 from 621; every template has at least 260 test
companies. Flip twins swap the two years in the column headings rather than edit one figure
(registry entry for why). Yield per template and losses in the registry.

**R-b done** (EXP-0050, 2026-11-25): 450 development base items, 50 per template, plus 837
twins; five arms. Plain R score: 4B 82.0, 4I 82.2, untrained 0.8B (B0) 55.9, C 0.9, K2 0.7. C and
K2 box a number on 291 and 300 of 300 label items: distillation on B left them one answer shape,
so the R-d gate (4I − K2 = 81.5) passes on format, not reasoning. 4B − B0 = 26.1 on R against
34.0 on B. Headroom for the 4B on R1.1, R1.3, R1.4, R1.5 and R1.8; R1.2, R1.6 and R1.9 at its
ceiling; R1.7 at everyone's floor (golds right, but the shared escape clause sends models to
"cannot be determined"). Hints help only on R1.7, and not the 0.8B (§7's hint hypothesis
unsupported). R-c's size rule gives about 9,400 base items, so the owner decides R-c's arms, size
and template fixes before it is written.

**R-c and R-d superseded** (owner, 2026-11-26, "全案推荐来"): the rest of S1's window goes to the
distillation re-plan in `s1_finance_distillation_replan.md`. Section R stays the exam; its test
items are used there after a new builder rewords R1.7 and limits R1.8 to sensible margins. C and
K2 are retired as arms.

The MLX machine is S1's until 2026-12-15. R-a to R-c fit in that window. R-d fits only if R-b
shows a gap worth closing.

## 7. Working hypotheses (to be fixed in R-c's pre-registration, not now)

These follow from the literature, with no data of our own yet:
- **Hints.** With hints, the 0.8B stays close to the 4B on R1. Without hints, it falls behind.
- **Twins.** Hold stability is lower for the 0.8B than for the 4B, and lower again after
  distillation on B items alone.
- **Step accuracy.** It lags answer accuracy for both models. EXP-0016 found the 4B writing wrong
  steps and right answers.

## 8. Dependency: the calculator

R runs with the calculator on, so the interface must be fair to both models first. EXP-0016's
chained rule hands the 4B a value that already carries ×100 when the 4B expects the fraction. This
accounts for 41 of the 44 B2 items the calculator cost the 4B on test. The rerun pre-registered as
EXP-0018 fixes the comparator before R-b.

## 9. Decisions for the owner

Decided 2026-11-23, every recommended option ("D 全按推荐"): **D1** R1 + R2, R4 batch 1
descriptive, R5 later; **D2** excerpt cap raised to about 800 tokens for R items, with a memory
check of a 1,024-token training sequence before R-d; **D3** no segments in v1; **D4** licence
check first, then download FinIndices and XFinBench if the licences allow research use; **D5**
S1 takes EXP-0019, then the block EXP-0050 to EXP-0059 (registry, Reserved).

Licence check for D4 (2026-11-23, web pages only, nothing downloaded):
- **XFinBench:** MIT (Hugging Face `Zhihan/XFinBench` and the GitHub LICENSE), not gated; 4,235
  items (validation 1,000, test 3,235), about 9.5 MB; test answers released 2026-02-04; the
  source of the questions is not stated. Downloaded with the owner's go-ahead ("下载"),
  2026-11-24: revision `9eb2a9d985e7a30de55b21de84eba176961453e0`, 9.5 MB, on the drive at
  `narrative_lab/external/xfinbench/` (not in git). SHA-256:
  `test_set.csv` `693ce71a283245cdf324e47bfd33af0714029f73683e8e2d9890528c4f9e5b8e`,
  `validation_set.csv` `c5769cef57e5b4a6f4d7f2edb789d64ad9b4aaba99924fd16d5704407bbce119`,
  `knowledge_bank.csv` `4ca105835c62d8148d9ec20953f6b3ef650ce8dfbfcb1bd375d06a590385d62c`.
  Contents, counts only for test: validation 1,000 (true/false 435, calculation 396, multiple
  choice 169; 22 with a figure); test 3,235 (1,360, 1,283, 592; 124 with a figure), every row
  with its answer. Capability tags on test: terminology 1,736, temporal reasoning 558, numerical
  modelling 444, scenario planning 134, forecasting 116, the rest two tags. Claude read four
  validation items: textbook-style statements and questions (monetary economics, inventory
  policy, futures trading), not company filings. So XFinBench is an out-of-format probe of
  general financial reasoning, like section A, not a test of reading a release; its temporal
  reasoning, scenario and forecasting tags are the parts closest to section R.
- **FinIndices:** no licence stated (Hugging Face `Findata/Finindice`, empty README, no code
  repository found); 640 test rows, 27.8 MB, answers public; the statements are Chinese A-share
  companies'. With no licence, it is not downloaded; it could only be cited, or the authors
  asked.

The options as put to the owner:

- **D1. Families in v1:** R1 + R2 (recommended), with R4 batch 1 descriptive and R5 later.
- **D2. Excerpt cap:** R1 items need two to three tables (the income statement, sometimes the
  share count), so the 400-token cap (S1 plan rule 4) probably has to rise to about 800. This
  means a 1,024 training sequence for the 0.8B in R-d, which needs a memory check within 12 GiB.
- **D3. Segments:** leave them out of v1 (recommended), or pull dimensional XBRL from 10-Q
  instance documents (a new data pull).
- **D4. External probes:** download FinIndices and XFinBench after a licence check, or skip R3.
- **D5. Experiment numbers:** S1 has EXP-0018 and 0019 left before S2's range. R needs about five
  numbers.

## 10. Risks

- **Yield.** Four-fact items need four verified figures in one excerpt. Yield may fall well below
  B2's; R-a measures it before anything else is decided.
- **Twin realism.** Edited releases may look odd to a model. Hold twins control for that, but only
  partly.
- **Label imbalance.** Most companies grow revenue, for example. Chance correction and balanced
  sampling per template are fixed in R-a.
- **The caveat in §2 stands.** R1 and R2 test the analyst's logic in checkable form, not judgement
  beyond rules. If the owner's question is mainly about judgement, R4 and R5 carry it, at higher
  cost and with less power.
