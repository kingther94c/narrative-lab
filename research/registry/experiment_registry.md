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

## Entries

## EXP-0007 — S1-b headroom: the S1 ladder zero-shot on EarningsExam v0 development items (2026-11-17)

### PRE-REGISTRATION
- **Status:** approved by the owner 2026-11-17 ("Approve, commit, run"). Committed and pushed
  before any model saw a sampled item. Not yet run.
- **Claim under test:** descriptive, not a hypothesis (plan §4, S1-b). How each rung of the S1
  ladder scores zero-shot on B1 lookup and B2 computation; whether the gaps between rungs leave
  anything to distil; and the disagreement rates that size the S1 test set.
- **Why the answer is not obvious:** B1 is reading one row of a table, so the 9B and 4B may sit
  at the ceiling and leave no gap to distil. The 0.8B may sit at the floor on B2. Scale
  conversion (a table in thousands, an answer in millions) affects about a quarter of B1 items
  and may separate the rungs more than the arithmetic does. Thinking may help the small rungs
  more than the large ones, or not at all on items this short.
- **Sample and scope, fixed here before looking:**
  1. Development items of EXP-0005 (`items_dev.jsonl`) from releases accepted after
     2026-06-30: 2,814 items from 350 companies and 597 releases. All seen templates, first
     phrasing (held-out templates exist only on the test side).
  2. Draw of 600 items. B1: 90 each of revenue, operating income, net income and diluted EPS.
     B2: 80 each of revenue growth, operating margin and EPS change. Items are ordered by
     SHA-256 of `"exp0007:" + id` and taken in that order, template by template in round
     robin. An item is skipped if its company already has 2 items in the draw, or its release
     already has an item of the same section. If a template runs out, the rest of its quota goes
     to the other templates of its section in the same order. A count-only dry run on
     2026-11-17 (templates, companies and releases; no model run) fills every quota except
     operating margin, which reaches 78. Its last 2 places go to the other B2 templates; 330
     companies in all. The draw is written to the drive,
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
- **Pre-registration commit:**
- **Result:**
- **Failure analysis / slices:**
- **Leakage sign-off:**
- **Verdict:** descriptive (no ACCEPT / REJECT); gate outcomes recorded per criterion.
