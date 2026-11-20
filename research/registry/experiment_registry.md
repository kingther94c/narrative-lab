# Experiment registry

Newest first. Every experiment is a script in `research/experiments/`, an entry here, and data that
can be regenerated.

## Entry format

```
## EXP-NNNN — <title> (YYYY-MM-DD)

### PRE-REGISTRATION
- **Status:** not yet run. Committed before the run.
- **Claim under test:**
- **Why the answer is not obvious:**
- **Sample and scope, fixed here before looking:**
- **Method and baseline:**
- **Criteria:** numbered, each with a numeric pass / refute threshold and the random seed.
- **Contamination label of the result:** clean / bounded / contaminated / prospective.
- **Not in scope:**

### VERDICT
- **Pre-registration commit:**
- **Result:**
- **Failure analysis / slices:**
- **Leakage sign-off:**
- **Verdict:** ACCEPT / ACCEPT WITH SCOPE LIMIT / MONITOR / REJECT
```

## Reserved

- **EXP-0000** — Feasibility probes: long-prompt inference and LoRA memory on this machine. An
  engineering measurement, so it has no hypothesis and no verdict; results go to
  `research/design/feasibility.md`. Run 2026-11-12/13: inference fits whole documents; LoRA on
  Qwen3.5 is limited to short sequences by its Gated DeltaNet layers.
- **EXP-0001** — Sealed zero-shot forecasts on 2026 third-quarter earnings releases. To be
  pre-registered and sealed before 2027-01-10. Primary target: the direction of next quarter's
  guidance. Descriptive target: a hard event within six months; the pre-registration states the
  expected count (at 0.3 to 1.5% a year, 800 companies yield two to twelve bankruptcies). The
  manifest needs a push or an external time stamp.
- **EXP-0002** — SEC EDGAR censuses for the data audit: hard events and earnings releases from
  the bulk submissions archive, and a rule-based guidance census of 400 releases from 50
  companies. An engineering measurement with no hypothesis and no verdict; results in
  `research/design/data_audit.md` §4 and §7. Run 2026-11-13.
- **EXP-0003** — Full count of post-cutoff guidance pairs: every earnings 8-K filed after the
  cutoff (to 2026-11-10) and each company's last one before it, flagged by keyword rules v2 and
  corrected by a 30-item hand check of pre-cutoff releases. An engineering measurement with no
  hypothesis and no verdict; results in `research/design/data_audit.md` §8. Run 2026-11-13.
- **EXP-0004** — Census of company split v1 (`split_v1.py`) on the EXP-0003 universe. It uses
  filing metadata and rule flags only. An engineering measurement with no hypothesis and no
  verdict; results in `research/design/data_audit.md` §8a. Run 2026-11-15.
- **EXP-0005** — EarningsExam v0 generator for sub-study S1 (step S1-a.1): auto-graded B1 lookup and
  B2 computation items from 8-K releases, with gold confirmed by XBRL company facts. An engineering
  measurement with no hypothesis and no verdict; results in `research/design/feasibility.md` §5.
  Run 2026-11-15.
- **EXP-0006** — S1-a probes for sub-study S1 (steps S1-a.3 to S1-a.5): removing 4-layer blocks
  from Qwen3.5-4B, slicing experts out of OLMoE-1B-7B, and LoRA and full fine-tuning memory for
  Qwen3.5-0.8B and the pruned 4B. Calibration and evaluation text is training-side exam excerpts
  only. An engineering measurement with no hypothesis and no verdict; results in
  `research/design/feasibility.md` §6. Run 2026-11-16.
- **EXP-0008** — EarningsExam v0.1: the EXP-0005 generator with an excerpt rule that always
  keeps the table's column-heading line, and drops an item when no such line is found. Fixes
  forward the v0 defect found while preparing EXP-0007. An engineering measurement with no
  hypothesis and no verdict; results in `research/design/feasibility.md` §5a. Run 2026-11-17.

- **EXP-0010** — EarningsExam v0.2: v0.1 items with one sentence asking for a minus sign
  appended to every question, and a grader that reads accounting parentheses as negative. Owner's
  decisions of 2026-11-18. An engineering measurement with no hypothesis and no verdict; results
  in `research/design/feasibility.md` §5b. Run 2026-11-18.
- **EXP-0012** — Slices of the EXP-0011 responses: the pre-registered filer-size slice its score
  step left out, and the exploratory error kinds of EXP-0009 under the v0.2 grader. Read-only, no
  model run; results in the EXP-0011 verdict. Run 2026-11-18.
- **EXP-0013** — Terse teacher probe for S1-c: the 4B on 300 pre-cutoff v0.2 development items
  (none in the S1-b draw), EXP-0011's prompt against one asking for a terse worked answer, thinking
  off, cap 512. Adoption rule fixed before the run: terse is adopted if its accuracy is no more
  than 3.0 points below standard on the same items and at least 70% of its correct answers fit a
  512-token training sequence. An engineering measurement with no hypothesis. Run 2026-11-18:
  not adopted. Terse 89.0% against standard 93.0% (−4.0 [−7.9, −0.3]); 37% of correct terse
  answers fit, because the prompt, not the answer, fills the sequence. Results in
  `research/design/feasibility.md` §7; the owner chose terse answers with 300-token training
  excerpts.
- **EXP-0015** — Slices of the EXP-0014 responses: the pre-registered template and filer-size
  slices, invalid rates, training loss curves and label yields its score step left out, and an
  exploratory check of wrong B2 answers (does the student's own one-line expression evaluate to
  the gold?). Read-only, no model run, counts only; results in the EXP-0014 verdict. Run
  2026-11-20.

## Entries

## EXP-0014 — S1-c: distilling Qwen3.5-4B into Qwen3.5-0.8B on EarningsExam v0.2 (2026-11-18)

### PRE-REGISTRATION
- **Status:** approved by the owner 2026-11-18 ("批准并全部开跑"), with the amendment on training
  items below. Committed and pushed before any model saw a test item, with the test draw's hash.
  Before the commit, and with no model run: the training items were built (rule 1) and the test
  draw made (rule 5). The first draw, at most 2 items per company, gave only 2,740 items (counts
  seen, no item text); the cap was raised to 3, within the pool the owner sized the test set by,
  and the draw redone. The first draw is archived, unused.
- **Claim under test:** confirmatory H1 and H2 of the S1 plan (§4, S1-c), for the one pair the
  owner kept, 4B → 0.8B. H1: training the 0.8B on the 4B's worked answers beats training it on its
  own (the teacher adds something beyond fine-tuning on the task). H2: the best distilled 0.8B is
  non-inferior to the zero-shot 4B within 3 points. Secondary H3 (shorter answers at no loss);
  descriptive H4 (what is given up on section A).
- **Why the answer is not obvious:** in S1-b (EXP-0011) the 4B leads the 0.8B by about 34 points
  on both sections. Rejection-sampling fine-tuning on the student's own answers (D2) often closes
  much of such a gap on a narrow task, so the teacher's increment over D2 may be small. H2 asks a
  model five times smaller to close nearly all of it. Terse labels (EXP-0013) cost the 4B 4 points,
  and training excerpts are shorter than test excerpts (300 against 400 tokens).
- **Amendments to the frozen S1 plan, all by the owner on 2026-11-18** (changelog): one pair,
  4B → 0.8B (9B → 4B failed the gate; 9B → 0.8B passed but is not run); two seeds, not three; full
  fine-tuning; D4 last and exploratory; a 3,000-item test set; 300-token training excerpts with
  terse labels; trained arms tested with the terse prompt. **One amendment proposed here, for
  approval, approved by the owner 2026-11-18:** the plan says each arm trains on "the same items,
  same count". D2 and D3 keep only
  correct answers, and the items the 0.8B answers correctly are the easier ones, so a common item
  set would remove the items where a teacher can add most. Proposed: the same count N for every
  arm, each arm drawing its N from its own kept items.
- **Sample and scope, fixed here before looking:**
  1. **Training items.** EarningsExam v0.2 rules applied to the training side with a 300-token
     excerpt cap (EXP-0008's excerpt rule with `MAX_TOKENS = 300`, then EXP-0010's question
     sentence): pre-cutoff releases of training companies only. Items whose needed rows do not fit
     300 tokens are dropped and counted. Built before any label was generated: 3,596 items from
     842 companies (no column heading 445 dropped, over budget 544), excerpts median 282 tokens.
  2. **Labels**, thinking off, one user turn with the terse prompt of EXP-0013, at most 160
     generated tokens. Up to 4 attempts per item and model: the first greedy, then up to 3 sampled
     (temperature 0.7, top-p 0.95, seeds 1 to 3); the first attempt graded correct by
     `exp0010.grade` is kept. A label is also dropped if the training sequence (chat-templated
     prompt + answer + end token) exceeds 512 tokens, or if it names a year later than the item's
     period end. D3 labels from Qwen3.5-4B (`32f3e8e`); D2 labels from Qwen3.5-0.8B (`2fc0636`).
  3. **N** = the smaller of the D2 and D3 kept counts, rounded down to a multiple of 50. Each arm
     draws N items in the order of SHA-256 of `"exp0014:" + arm + ":" + id`.
  4. **Development set:** the 600 items of the EXP-0007 draw from v0.2 (as EXP-0011). Each trained
     run is evaluated on it at the end of epochs 1 and 2, and the better checkpoint is kept (two
     development evaluations per run, the same for every arm). Ties go to epoch 1.
  5. **Test set:** 3,000 v0.2 test items, all from post-cutoff releases of test companies, at most 3
     per company (see Status). Seen templates (first phrasing of the seven development templates): 2,400, of
     which B1 4 × 360 and B2 3 × 320. Unseen templates (second phrasing, or the held-out metrics
     gross profit, gross margin and net margin): 600, of which B1 300 and B2 300, round robin over
     the unseen templates of each section. Items are ordered by SHA-256 of `"exp0014-test:" + id`;
     a short template's quota goes to the others of its section and kind (seen or unseen), as in
     EXP-0007. The draw is made by script and its items are never shown to Claude. Made 2026-11-18:
     3,000 items, 1,360 companies, 2,400 seen (operating margin short at 275; eps change 343,
     revenue growth 342 after redistribution); SHA-256 of the ids in draw order
     `8e6adfc4b300bc553e942cf5c9758fd416cc68061bf4b2a58ef1829c070dddfe`.
- **Method and baseline:**
  1. Arms (0.8B student unless stated): **D0** zero-shot, standard prompt of EXP-0011, cap 512 —
     for the 0.8B and for the 4B (H2's comparator). **D1** gold only: target `\boxed{gold}`, gold
     written at the precision shown in the excerpt. **D2** self: the 0.8B's own kept terse answers.
     **D3** teacher: the 4B's kept terse answers. **D4** (exploratory, only if time allows before
     2026-12-15): D3's text with a top-20 logit-distillation loss from the 4B, mixed 50/50 with
     cross-entropy; its training loop is checked against a reference on 10 items before use.
  2. Training: full fine-tuning of Qwen3.5-0.8B (bf16), sequence 512, batch 1, gradient
     checkpointing, AdamW, learning rate 1e-5 with 50 warm-up steps and cosine decay, 2 epochs,
     loss on answer tokens only. Two seeds (1, 2) per trained arm. Within 12 GiB.
  3. Trained arms are tested with the terse prompt they were trained on, thinking off, at most 160
     generated tokens, then EXP-0007's forced answer. D0 as EXP-0011. Greedy decoding.
  4. Grading by `exp0010.grade`. A trained arm's score per item is the mean over its two seeds.
  5. Intervals: paired, bootstrap over companies, 10,000 resamples, seed 20261118.
  6. A speed check of 100 training steps precedes the runs. If one run would exceed 8 hours,
     epochs drop to 1 for every arm, decided before any development evaluation.
- **Criteria** (B test, all 3,000 items; family H1, H2, H5, H8 Holm-corrected at the end of S1;
  this verdict reports each at α = 0.0125, the strictest step):
  1. **H1:** Δ = D3 − D2. Supported if Δ ≥ 3.0 points and the one-sided test of Δ > 0 rejects at
     α = 0.0125. Refuted if the upper end of the 97.5% interval is below 3.0. Otherwise
     inconclusive.
  2. **H2:** Δ = best distilled 0.8B − D0 4B, where "best distilled" is D3, or D4 if it was run
     and scores higher on the development set. Non-inferior if the lower end of the one-sided
     98.75% bound is above −3.0. Refuted if the upper end of the 97.5% interval is below −3.0.
  3. **H3 (secondary):** D3's median generated tokens at most half of D0 0.8B's, with D3's accuracy
     no more than 2 points below D0 0.8B's.
  4. **H4 (descriptive):** accuracy change against D0 on section A: 100 items each of FinQA,
     CFA-Easy and FinanceIQ (`learnai.finbench.load_problems(100, seed=20261118)`), thinking off,
     cap 512, for D0, D2 and D3.
  5. **Also reported:** every arm by section, seen and unseen templates, filer size and template;
     forced and invalid rates; seed spread; training loss curves; label yields per model and
     attempt.
- **Contamination label of the result:** clean. Test items come from releases accepted after
  2026-06-30, after both models' release. The teacher sees only pre-cutoff training excerpts. No
  model labels a test item.
- **Not in scope:** 9B as a teacher; LoRA; thinking on; S1-d and S1-e; any change to the exam.
- **Estimated compute:** training 6 runs of about 4 to 6 hours; labels about 3 hours; test and
  development evaluation about 12 hours; section A about 3 hours. About 45 to 55 hours, plus about
  15 for D4.

### VERDICT
- **Pre-registration commit:** `13adbd2` (pushed before any label was generated). Run 2026-11-18
  22:07 to 2026-11-20 19:12 by `queue`, every step complete: labels 4 hours, six training runs of
  4.6 to 5.4 hours (peak 7.4 to 8.1 GiB), test 8.4 hours, section A 0.6 hours. The speed check
  (5.54 s a step, 5.7 hours for two epochs) kept 2 epochs. Outputs: `s1/exp0014/scores.json`;
  template, filer size, loss curves, label yields and error slices in `s1/exp0014/slices.json`
  (EXP-0015).
- **Labels and sets.** The 4B answered 3,270 of 3,596 training items correctly on its first
  (greedy) attempt and 92 on none; the 0.8B 1,308 first, 1,286 on none. Kept after the 512-token
  and later-year checks: D3 3,457, D2 1,875, D1 3,596, so N = 1,850. Median answer tokens: D3 50,
  D2 51, D1 9. Development chose epoch 2 for every run except D2 seed 2 (epoch 1).
- **Result** (3,000 test items, accuracy %, trained arms the mean of two seeds; intervals 97.5%,
  company bootstrap, 10,000 resamples):

  | Arm | All | B1 (1,740) | B2 (1,260) | Seen (2,400) | Unseen (600) | Median tokens | Seeds |
  |---|---|---|---|---|---|---|---|
  | D0 0.8B zero-shot | 60.3 | 59.5 | 61.5 | 60.4 | 60.2 | 239 | |
  | D0 4B zero-shot | 92.7 | 92.9 | 92.5 | 91.8 | 96.3 | | |
  | D1 gold only | 58.9 | 87.5 | 19.4 | 61.1 | 49.9 | | 52.8 / 65.0 |
  | D2 self | 68.1 | 86.4 | 42.7 | 69.4 | 62.7 | | 72.3 / 63.9 |
  | D3 teacher | 74.6 | 93.8 | 48.1 | 76.3 | 67.7 | 53 | 72.9 / 76.3 |

  Forced answers 0 to 0.1% for trained arms (3.6% and 1.7% for D0); invalid at most 0.5%.

  1. **H1 supported.** D3 − D2 = +6.5 [5.0, 8.0], one-sided p < 0.0001: B1 +7.4 [5.8, 8.9], B2
     +5.4 [2.6, 8.2]. The interval resamples companies, not seeds; with two seeds, D3's worse seed
     (72.9) is 0.6 points above D2's better one (72.3), and D2's seeds differ by 8.4 points.
  2. **H2 refuted.** D3 − D0 4B = −18.2 [−20.0, −16.3]. On B1 the distilled 0.8B matches the 4B,
     +0.9 [−0.8, 2.7]; on B2 it is 44.5 points below [−47.6, −41.4].
  3. **H3 supported as registered**: D3's median 53 generated tokens against 239 for D0 0.8B, and
     14.3 points more accurate overall. But on B2 D3 is 13.4 points *below* the untrained 0.8B.
  4. **H4.** Section A, 100 items each, accuracy %: 

     | | FinQA | CFA-Easy | FinanceIQ |
     |---|---|---|---|
     | D0 0.8B | 38 | 36 | 27 |
     | D2 seeds 1 / 2 | 6 / 25 | 32 / 22 | 28 / 29 |
     | D3 seeds 1 / 2 | 10 / 11 | 20 / 13 | 28 / 23 |

     The trained models answer everything in the terse style (median 27 to 87 generated tokens
     against 371 to 474 for D0); FinQA, which needs arithmetic, falls most.
- **Failure analysis / slices** (EXP-0015; template and filer size pre-registered, the rest
  exploratory):
  1. **B2 fails in the arithmetic, not the reading.** Of D3's wrong B2 answers, 392 of 696 (seed
     1) and 402 of 613 (seed 2) write a one-line expression that, evaluated, gives the gold: the
     right rows, columns and formula, then a wrong quotient. Claude read D3's development answers
     and saw the same: correct operands, a division done in one step and off by one to several
     points. D2's answers rarely write an evaluable expression (13 and 19 of this kind). The terse
     format gives the 4B room to divide in one line; the 0.8B cannot.
  2. **By B2 metric**, D0 0.8B against D3 (seeds 1 / 2): EPS change 36.5 against 72.5 / 75.1 (a
     subtraction, which training improves); revenue growth 70.8 against 26.6 / 21.4; operating
     margin 76.7 against 43.7 / 60.7; gross margin 64.0 against 20.9 / 38.4; net margin 73.3
     against 29.1 / 57.0 (divisions, which it worsens).
  3. **Unit and sign errors** nearly vanish after training (D3: 11 and 10 unit errors, 4 and 1
     dropped signs, against 80 and 33 for D0 0.8B). D2 seed 2 keeps 146 unit errors.
  4. **Filer size:** no consistent pattern in any trained arm (D3 71.5 to 78.0 across bands).
  5. **Seeds.** Spread is large for D1 (12.2 points) and D2 (8.4) and smaller for D3 (3.4).
     Final training loss: D3 0.09 and 0.19, D2 0.28 and 0.25, D1 0.21 and 0.12.
- **Leakage sign-off:** test items from releases accepted after 2026-06-30, never shown to Claude:
  scripts printed counts and rates only. The teacher labelled pre-cutoff training items only; no
  model labelled a test item. Claude read development answers and four section A answers (public
  benchmark). No roster model labelled gold. Clean.
- **Verdict:** H1 supported: the 4B's worked answers teach the 0.8B 6.5 points more than its own
  do, on both sections. H2 refuted: the distilled 0.8B matches the 4B on lookups (B1) but not on
  calculations (B2), where it falls below the untrained 0.8B. Terse labels move the reading of the
  table and the format to the student but compress away the arithmetic it needs. H3 holds as
  registered; H4 shows general finance ability lost. D4 (logit distillation of the same terse
  text) would not address the arithmetic. What to try for B2 goes to the owner.

## EXP-0011 — S1-b rerun: the S1 ladder thinking off on EarningsExam v0.2, 512-token cap (2026-11-18)

### PRE-REGISTRATION
- **Status:** drafted 2026-11-18 from the owner's decisions of that day (sign instruction on every
  template, parentheses read as negative, rerun thinking off only, cap 512). Approved by the owner
  2026-11-18 ("Approve, commit, push, run"). Committed and pushed before any model saw a drawn
  v0.2 item. Run 2026-11-18; verdict below.
- **Claim under test:** descriptive, as EXP-0007. The S1 ladder's zero-shot scores, gates, test-set
  size and answer lengths when the sign is asked for, accounting negatives are read, and answers
  have room to finish. Its outcomes replace EXP-0007's for S1-c.
- **Why the answer is not obvious:** EXP-0009 bounds the sign effect but cannot say what a model
  does when asked: the 9B → 4B gate passed with parentheses read as negative and failed with signs
  ignored. A longer cap may raise every rung, or mostly the 9B, whose forced answers scored 60%
  against 95% for finished ones.
- **Sample and scope, fixed here before looking:** the 600 items of the EXP-0007 draw, same ids and
  order (SHA-256 `0ee6dbfd…a6c570`), taken from EarningsExam v0.2 (EXP-0010). Only the question
  sentence differs from EXP-0007; `prepare` checks the ids, gold and excerpts are equal. The
  models have seen these items once, in EXP-0007; nothing was trained between the runs.
- **Method and baseline:** EXP-0007's method, run by its code (`exp0011_s1b_headroom_v0_2.py`
  imports it), with three changes: items from v0.2; grading by `exp0010.grade`; thinking off only,
  at most 512 generated tokens, then the forced answer of at most 48 tokens as before. Models and
  revisions, prompt, greedy decoding, intervals (company bootstrap, 2,000 resamples, seed
  20261117) and run order (0.8B, 2B, 4B, 9B, OLMoE) as EXP-0007. Estimated 4 to 6 hours.
  Baseline: EXP-0007 thinking off, regraded with the old grader for the comparison.
- **Criteria** (thinking off):
  1. **Distillation gate:** as EXP-0007 criterion 1, for 9B → 4B, 9B → 0.8B and 4B → 0.8B.
  2. **Ceiling and floor:** as EXP-0007 criterion 2.
  3. **Test-set size:** as EXP-0007 criterion 3, same formula and stand-ins. A stand-in whose
     model is at the floor on both sections is reported but not used for the size. If the size is
     above 3,000 or above the test pool at 3 items per company (5,451), the owner decides.
  4. **Answer length:** for the 9B and 4B, median and 90th percentile of generated tokens, and the
     share of correct answers finishing within 64, 128 and 256 tokens.
  5. Also reported, descriptive: per model and section, the change from EXP-0007; accuracy on
     negative-gold items; forced and invalid rates; accuracy by template and filer size.
- **Contamination label of the result:** clean, as EXP-0007.
- **Not in scope:** thinking on; test items; training; any further change to the exam.

### VERDICT
- **Pre-registration commit:** `10dcbd9` (pushed before the run). Run 2026-11-18 14:50 to 18:10,
  all five runs complete (600 items each): 28, 22, 47, 84 and 19 minutes. `prepare` confirmed the
  ids, gold and excerpts equal EXP-0007's. Outputs: `s1/exp0011/scores.json`; filer size and error
  kinds in `s1/exp0011/slices.json` (EXP-0012).
- **Result** (thinking off, 512-token cap, accuracy % with 95% company-bootstrap interval; change
  from EXP-0007 in brackets after it):

  | Model | B1 (n 360) | B2 (n 240) | Negative gold (n 178) | B1 scale conversion | Forced |
  |---|---|---|---|---|---|
  | Qwen3.5-0.8B | 59.4 [54.1, 64.8] (+9.2) | 53.8 [47.6, 60.5] (+16.7) | 41.6 | 34.0 | 3.5% |
  | Qwen3.5-2B | 79.2 [75.1, 83.4] (+16.9) | 57.5 [51.4, 63.8] (+15.0) | 62.9 | 67.9 | 4.2% |
  | Qwen3.5-4B | 93.1 [90.5, 95.6] (+8.6) | 88.3 [84.2, 92.1] (+16.7) | 87.1 | 82.1 | 2.0% |
  | Qwen3.5-9B | 95.6 [93.6, 97.5] (+5.8) | 86.7 [82.3, 90.8] (+18.3) | 87.6 | 94.3 | 2.7% |
  | OLMoE-1B-7B | 13.6 [10.0, 17.1] (−1.1) | 7.9 [4.6, 11.6] (−2.1) | 5.1 | 2.8 | 8.2% |

  Invalid (no number) at most 0.5%. Peak memory 1.9 to 5.7 GiB.

  1. **Distillation gate: 9B → 4B fails; the two pairs into the 0.8B pass.** 9B → 4B: +2.5
     [−0.5, 5.5] on B1 and −1.7 [−6.5, 3.5] on B2. 9B → 0.8B: +36.1 [30.4, 41.6] and +32.9
     [25.7, 39.6]. 4B → 0.8B: +33.6 [28.2, 39.3] and +34.6 [28.0, 41.2]. By the rule of EXP-0007
     criterion 1, 9B → 4B is dropped from S1-c.
  2. **Ceiling and floor.** The 9B is above 95% on B1 (95.6), so B1 is dropped from the 9B's S1
     tests. OLMoE is below 20% on both sections, as before. No other rung is at either bound.
  3. **Test-set size: the owner decides.** H1/H2 (4B against 0.8B): d = 0.383, DE = 1.01,
     n = 4,794. H5 (4B against 2B): d = 0.267, DE = 0.97, n = 3,193. H8 (OLMoE against the 4B)
     n = 9,890, reported but not used: OLMoE is at the floor on both sections. The size is 4,794:
     above 3,000, within the test pool at 3 items per company (5,451).
  4. **Answer length.** The 9B writes a median 242 generated tokens (90th percentile 381) and the
     4B 242 (384). Of their correct answers, none finishes within 64 tokens, 7.1% (9B) and 12.4%
     (4B) within 128, and 57.8% and 62.3% within 256.
- **Failure analysis / slices** (EXP-0012; filer size pre-registered, the rest exploratory):
  1. **The sign fix worked.** Dropped minus signs fell from 49 to 2 errors for the 4B and from 52
     to 2 for the 9B; negative-gold accuracy rose from 52 to 87% for both. Together with the
     longer cap, every Qwen3.5 rung gained 6 to 18 points. EXP-0007's 9B → 4B pass was an
     artefact of signs and the cap.
  2. **The cap.** Forced answers fell from 35 to 40% of items to 2 to 4%. Most correct answers
     need more than 128 tokens with thinking off.
  3. **Filer size**, large accelerated / accelerated / non-accelerated or smaller: 0.8B 61 / 53 /
     53, 2B 72 / 76 / 68, 4B 94 / 86 / 89, 9B 92 / 92 / 93. The small-filer gap of EXP-0007
     closed for the 4B and the 9B, which suggests it came mostly from losses.
  4. **What the 9B still gets wrong** (48 items, read by Claude against the 4B's answers): about 9
     are rounding (a whole-number percentage where one decimal place was asked, or a figure
     converted to millions and rounded); the rest are wrong rows, periods or arithmetic. The 4B
     gets 32 of the 48 right. EPS change is the weakest template for every rung (0.8B 26%,
     4B 79%, 9B 86%). A few B2 golds are extreme (operating margins in the thousands of percent, revenue
     growth below −100%), from companies with almost no revenue; they are correct but odd.
  5. **OLMoE** did not gain: it is at the floor through reasoning, not format.
- **Leakage sign-off:** development items from releases accepted after 2026-06-30 only; no test
  item opened. Claude read development answers to classify errors. No roster model labelled gold.
- **Verdict:** descriptive. With the sign asked and room to answer, the 4B matches the 9B on this
  exam: 9B → 4B fails the gate and is dropped from S1-c; 9B → 0.8B and 4B → 0.8B pass by more than
  30 points. The 9B is at the ceiling on B1 and OLMoE at the floor on both sections. The S1 test
  size of 4,794, and the training excerpt cap given answers of about 250 tokens, go to the owner.

## EXP-0007 — S1-b headroom: the S1 ladder zero-shot on EarningsExam v0 development items (2026-11-17)

### PRE-REGISTRATION
- **Status:** approved by the owner 2026-11-17 ("Approve, commit, run"). Committed and pushed
  before any model saw a sampled item. **Amended 2026-11-17, before the run** (owner: "Fix first,
  then run"): items come from EarningsExam v0.1 (EXP-0008) instead of v0, because v0 excerpts
  could lose the line naming each column's period. Only the item source, the pool and the draw
  change; every other rule stands. The v0 draw is archived on the drive, unused. Run
  2026-11-17/18; verdict below.
- **Claim under test:** descriptive, not a hypothesis (plan §4, S1-b). How each rung of the S1
  ladder scores zero-shot on B1 lookup and B2 computation; whether the gaps between rungs leave
  anything to distil; and the disagreement rates that size the S1 test set.
- **Why the answer is not obvious:** B1 is reading one row of a table, so the 9B and 4B may sit
  at the ceiling and leave no gap to distil. The 0.8B may sit at the floor on B2. Scale
  conversion (a table in thousands, an answer in millions) affects about a quarter of B1 items
  and may separate the rungs more than the arithmetic does. Thinking may help the small rungs
  more than the large ones, or not at all on items this short.
- **Sample and scope, fixed here before looking:**
  1. Development items of EarningsExam v0.1 (EXP-0008, `exam_v0_1/items_dev.jsonl`) from
     releases accepted after 2026-06-30: 2,496 items from 324 companies and 553 releases. All
     seen templates, first phrasing (held-out templates exist only on the test side). (Before the
     amendment: EXP-0005, 2,814 items from 350 companies.)
  2. Draw of 600 items. B1: 90 each of revenue, operating income, net income and diluted EPS.
     B2: 80 each of revenue growth, operating margin and EPS change. Items are ordered by
     SHA-256 of `"exp0007:" + id` and taken in that order, template by template in round
     robin. An item is skipped if its company already has 2 items in the draw, or its release
     already has an item of the same section. If a template runs out, the rest of its quota goes
     to the other templates of its section in the same order. The amended draw (2026-11-17, no
     model run): B1 revenue 89, operating income 88, net income 92, diluted EPS 91; B2 revenue
     growth 87, operating margin 66, EPS change 87; 318 companies; SHA-256 of the ids in draw
     order `0ee6dbfd29a3f6a10bcb459a2ea20389830ddc76b22a6e0e30b5749d77a6c570`. The draw is
     written to the drive,
     with its item ids hashed into the registry entry's verdict.
  3. The first 300 items of the draw, in draw order, form the thinking subset.
- **Method and baseline:**
  1. Models, each pinned to its snapshot on the external drive: Qwen3.5-0.8B (bf16,
     `2fc0636`), Qwen3.5-2B (4-bit, `93760be`), Qwen3.5-4B (4-bit, `32f3e8e`), Qwen3.5-9B
     (4-bit, `938d891`), OLMoE-1B-7B-0125-Instruct (4-bit, `e238441`). gpt-oss-20b is not run;
     plan §2 keeps it for after S1-e.
  2. Prompt, one user turn: the excerpt, a blank line, the question, then
     `Reason briefly, then give the final number in \boxed{}.` No system prompt, no examples.
  3. Thinking off: every model. Qwen3.5 with `enable_thinking=false`. OLMoE has no thinking
     mode and runs this condition only. At most 256 generated tokens.
  4. Thinking on: the four Qwen3.5 models, on the 300-item thinking subset, with
     `enable_thinking=true`. At most 2,048 generated tokens.
  5. Forced answer (learning_ai `FINANCE_MODEL_SELECTION.md` §8.1). If the cap is reached with no
     box after the reasoning, append `\n\n**Final answer:** \boxed{`, preceded by `\n</think>`
     when still thinking, and let the model write at most 48 more tokens. Forced answers are
     scored like the others, and their rate is reported.
  6. Greedy decoding, one sequence at a time, mlx 0.32.4 and mlx_lm 0.32.2. One MLX job at a
     time, within 12 GiB.
  7. Scoring. Take the last `\boxed{}` after the reasoning, or in the forced continuation, and
     read its number with `learnai.finbench.parse_number`. Correct when the number is within
     the item's `tolerance.abs` of gold. A percent sign is ignored, since gold for percentages
     is in percent units. Words of scale are ignored, so an answer in the wrong unit is wrong;
     the unit is part of the task. No box, or no number in it, is wrong. That rate is reported
     per model and mode.
  8. Intervals: bootstrap over companies, 2,000 resamples, seed 20261117. For gaps, both models
     are resampled together.
  9. Run order: thinking off for all five models (0.8B, 2B, 4B, 9B, OLMoE), then thinking on
     (0.8B, 2B, 4B, 9B). Estimated 6 to 12 hours.
- **Criteria** (all on thinking off, the mode S1-c trains in; thinking on is reported beside them):
  1. **Distillation gate (plan §4).** An S1-c pair goes ahead if the teacher leads the student
     by at least 5.0 points on B1 or on B2, and the 95% interval of the gap lies above 0. The
     pairs are 9B → 4B, 9B → 0.8B and 4B → 0.8B. Pairs that fail are dropped from S1-c; if all
     three fail, S1-c does not run as planned and the plan is revisited.
  2. **Ceiling and floor (plan §3, rule 7).** A section is dropped from a model's S1 tests if
     that model scores above 95% (ceiling) or below 20% (floor) on it.
  3. **Test-set size.** For each pair behind a confirmatory contrast (H1, H2, H5, H8) that
     S1-b can stand in for, d is the share of items on which the two models disagree on
     correctness. The stand-ins: 4B against 0.8B for H1 and H2; 4B against 2B for H5; OLMoE
     against the dense rung nearest its resident memory for H8. Test size is
     n = DE × (z(1 − 0.0125/2) + z(0.80))² × d / 0.03², with α = 0.05/4 for Holm at its
     strictest. DE is the clustering design effect, measured on the draw as the ratio of the
     company-bootstrap to the independent variance of the paired difference. The largest n over
     the pairs is the S1 test size. If it is above 3,000, or above what the test pool allows at
     3 items per company, the owner decides before S1-c is pre-registered.
  4. **Answer length, for the open S1-c choice** (feasibility §6). For the 9B and the 4B with
     thinking off: the median and 90th percentile of generated tokens, and the share of their
     correct answers that finish within 64 and within 128 tokens. Descriptive.
  5. Also reported, descriptive: accuracy per model, mode, section and template, with
     intervals; accuracy by filer size and on scale-conversion items; tokens per answer;
     forced-answer and invalid rates; wall time per item.
- **Contamination label of the result:** clean. Every item comes from a release accepted after
  2026-06-30. The Qwen3.5 checkpoints and OLMoE-0125 were released before that date, and for
  open weights the release date bounds the training cutoff.
- **Not in scope:** test items (not read, not drawn here; the S1 test draw belongs to S1-c's
  pre-registration); section A off-target exams (their baselines are D0 in S1-c); gpt-oss-20b;
  any training or pruning; held-out templates. The S1 excerpt-cap choice for training items is
  informed by criterion 4 but not made here.

### VERDICT
- **Pre-registration commit:** `8e2db31` (pushed before the run), amended in `0943e3a` (pushed
  before the run). Run 2026-11-17 20:58 to 2026-11-18 12:16, all nine runs in the registered
  order, complete (600 items thinking off, 300 thinking on). Draw SHA-256 as registered. Outputs:
  `s1/exp0007/scores.json`; slices from the same raw responses in `s1/exp0007/slices.json`
  (EXP-0009).
- **Result** (thinking off, accuracy % with 95% company-bootstrap interval):

  | Model | B1 (n 360) | B2 (n 240) | B1 scale conversion (n 106) | Forced | Peak GiB | s / item |
  |---|---|---|---|---|---|---|
  | Qwen3.5-0.8B | 50.3 [45.0, 55.6] | 37.1 [30.8, 43.5] | 19.8 | 36% | 2.1 | 2.6 |
  | Qwen3.5-2B | 62.2 [57.2, 67.6] | 42.5 [35.9, 48.4] | 31.1 | 39% | 1.9 | 1.9 |
  | Qwen3.5-4B | 84.4 [80.8, 88.0] | 71.7 [65.6, 77.3] | 65.1 | 35% | 3.2 | 4.5 |
  | Qwen3.5-9B | 89.7 [86.7, 92.7] | 68.3 [62.3, 74.0] | 81.1 | 40% | 5.6 | 7.3 |
  | OLMoE-1B-7B | 14.7 [11.1, 18.6] | 10.0 [6.4, 13.8] | 0.0 | 55% | 4.2 | 1.6 |

  Thinking on (300-item subset; B1 n 172, B2 n 128): 0.8B 58.1 / 44.5, 2B 61.6 / 46.1, 4B
  78.5 / 68.0, 9B 89.0 / 84.4. Invalid (no number) at most 0.7% in any run.

  1. **Distillation gate: all three pairs pass.** 9B → 4B passes on B1 only, at the margin:
     +5.3 [1.7, 9.0]; on B2 the 4B leads, −3.3 [−9.2, 2.3]. 9B → 0.8B: +39.4 [34.0, 44.7] on
     B1, +31.2 [24.5, 37.9] on B2. 4B → 0.8B: +34.2 [28.7, 39.7] and +34.6 [27.6, 41.6].
  2. **Ceiling and floor.** No Qwen3.5 rung is at the ceiling or the floor on either section.
     OLMoE is below 20% on both, so both sections are dropped from its S1 tests.
  3. **Test-set size: above both limits; the owner decides before S1-c.** H1/H2 (4B against
     0.8B): d = 0.393, DE = 1.12, n = 5,462. H5 (4B against 2B): d = 0.317, DE = 1.09,
     n = 4,270. H8 (OLMoE against the 4B, the dense rung nearest its 4.2 GiB): d = 0.678,
     n = 8,893. The largest is 8,893, but OLMoE is at the floor on both sections (criterion 2),
     so its stand-in measures nothing; without it the largest is 5,462. Both are above 3,000 and
     above the test pool at 3 items per company (1,817 × 3 = 5,451).
  4. **Answer length.** Thinking off, the 9B writes a median 216 tokens (90th percentile 256, the
     cap) and the 4B 234 (256). Of their correct answers, none finishes within 64 tokens; 11.3%
     (9B) and 13.4% (4B) finish within 128. The prompt asks for brief reasoning; the models do
     not keep to it.
  5. Thinking on, every run hits the 2,048 cap: thinking never closed in 100% of 0.8B and 2B
     items, 96% of 4B and 95% of 9B items, so thinking-on scores are answers forced after 2,048
     tokens of thought. Run times: 23, 18, 42, 73 and 16 minutes thinking off; 117, 88, 195 and
     346 minutes thinking on.
- **Failure analysis / slices** (EXP-0009; the filer-size slice is the pre-registered one and was
  left out of the score step, the rest are exploratory):
  1. **Filer size**, thinking off, large accelerated (325 items) / accelerated (66) /
     non-accelerated or smaller (176): 0.8B 51 / 44 / 38, 2B 61 / 62 / 45, 4B 86 / 76 / 71,
     9B 86 / 83 / 74, OLMoE 17 / 14 / 7. Smaller filers are harder for every rung.
  2. **Signs.** Gold is negative in 178 of the 600 items (losses, declines, negative margins).
     Only the EPS-change template tells the model to use a minus sign; the loss and growth
     questions do not. A dropped minus sign is the largest single error for the 4B and the 9B:
     49 of the 4B's 124 wrong answers and 52 of the 9B's 113. On negative-gold items they score
     52%. Thinking on, the 4B drops the sign on 79% of negative items, often after debating the
     sign convention in its reasoning. Some answers are written in accounting form,
     `(1,234)` or `-(5.6)`, which `parse_number` reads as positive: 3 to 15 boxed answers per
     Qwen3.5 rung (25 for OLMoE) open with a parenthesis.
  3. **Sign rule sensitivity of the gate.** Reading accounting parentheses as negative: 9B → 4B
     +5.6 [1.7, 9.4] on B1, still passing. Counting |answer| = |gold| as right (an upper bound on
     what a sign instruction could recover): 9B → 4B +4.7 [1.4, 8.1] on B1 and −1.2 on B2,
     failing, and the 9B reaches 95.3% on B1, over the ceiling. The two pairs into the 0.8B pass
     under every rule by 30 points or more. The 9B → 4B pass is therefore fragile: it turns on
     how signs are asked and read.
  4. **The 256-token cap.** A third of thinking-off answers are forced. Forced answers score far
     below finished ones (9B 60% against 95%; 4B 59% against 91%), so the cap lowers every
     rung's score and may compress the 9B → 4B gap.
  5. **Units.** On B1 items that need a scale conversion the rungs spread widely (0.8B 20%,
     4B 65%, 9B 81%); a wrong unit by a factor of 1,000 is 2 to 26 errors per model.
  6. **Thinking on against off, same 300 items:** 0.8B +12.8 points on B1 and +0.7 on B2; 2B
     +1.1 / −0.8; 4B −4.6 / −3.9; 9B +0.6 / +11.7. Thinking helps the 9B on computation and the
     0.8B on lookup, and hurts the 4B, mostly through signs.
  7. **OLMoE** is at the floor through poor reasoning rather than format: it boxes a number in
     99% of items, and none of its 106 scale-conversion answers is right. In the responses read it
     adds up rows that were not asked for and mixes units.
- **Leakage sign-off:** every drawn item is a development item from a release accepted after
  2026-06-30; no test item was opened. Claude read development responses and questions to check
  the grader and classify errors, which the protocol allows. No roster model labelled any gold.
  The run used the pinned snapshots and nothing left the machine.
- **Verdict:** descriptive. Gates as pre-registered: all three S1-c pairs pass (9B → 4B at the
  margin and fragile to the sign rule); OLMoE's sections are dropped at the floor; the test-set
  size goes to the owner. Before S1-c the exam needs a decision on signs (a minus-sign instruction
  in every template whose gold can be negative, and accounting parentheses read as negative) and
  on the thinking-off cap.
