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
- **EXP-0020 to EXP-0029** — held for sub-study S2 (`research/design/substudy_s2_blind_replay.md`),
  so that S1 and S2, worked on in separate sessions, do not take the same number. S1 continues
  from EXP-0016.
- **EXP-0020** — S2-a episodes, candidate labels and rule baselines: for the training and
  development companies of split v1, a quarterly series of revenue, operating income and net
  income as first filed (the fourth quarter as the year less nine months), four candidate
  next-quarter labels with their base rates and best simple rules, and a list of the earnings
  releases since 2019 with what is already on the drive. It reads the company-facts snapshot of
  2026-11-14 and the bulk submissions archive of 2026-11-12, pulls nothing and calls no model.
  Test companies are not opened. An engineering measurement with no hypothesis and no verdict.
  Run 2026-11-19, before the S2 design is frozen, as groundwork for its label and pull decisions.
  1,362 of 1,559 companies have a series (36,929 quarters, 6,481 of them derived fourth
  quarters); 31,065 episodes have a next quarter. Next-quarter base rate and best rule: growth
  positive 68% (persistence 80%); growth accelerates, outside a 2-point dead band, 49% (reversal
  52%); operating margin up 53% (persistence 66%); net income up 55% (persistence 64%). Since
  2019 these companies filed 44,629 earnings releases; 33,378 map to a labelled quarter and 4,404
  are on the drive, nearly all from 2026. Dated by release, 995 episodes are after the cutoff (734
  outside the dead band; 37 and 25 for the 50 largest companies by revenue) and 29,606 are before
  it. Three mistagged periods and 40 quarters filed together by late filers are excluded by rule.
  `audit` recomputes 40 growth rates from the archive. Results in the S2 design, §8 and §10;
  outputs in `s2/exp0020/` on the external drive.
- **EXP-0021** — S2-a pull of old earnings releases (S2 plan, decision 4). `draw` picks, by seed
  20261120 and without the network, labelled pre-cutoff releases not on the drive from EXP-0020's
  list, training and development companies only: four in four different filing years for each of
  the 250 largest companies by revenue, one from each of 500 other companies. `fetch` downloads
  their press releases with EXP-0003's choice of document and text extraction; `audit` checks the
  draw reproduces, that no release is post-cutoff or from a test company, and that the texts are
  non-empty. No model is called. An engineering step with no hypothesis and no verdict. Run
  2026-11-20 after the owner's approval, filing years 2019 to 2025: 1,407 releases from 732
  companies (194 top 50, 713 from the 51st to 250th, 500 others; 1,061 training, 346
  development); 228 of the 250 largest companies have candidates, ten of them fewer than four
  years. 1,386 press releases fetched (one after a retry of a 502), 21 filings with no press
  release document; 82 MB, median 50,000 characters. 24 texts lack every earnings word: mostly
  the 8-K cover chosen because its description says "release" (EXP-0003's rule, kept as is),
  a few releases about other news. Later draws exclude them. Outputs in `s2/exp0021/`.
- **EXP-0022** — S2-a sanitiser (S2 plan §5 to §7). `build` writes the eight views of each
  episode, a half-fraction (I = NPSZ) of four switches: names, periods, two-factor scaling, noise
  (each current-period leaf times 1 + e, e ~ U(-0.02, 0.02); totals, differences, growth rates and
  margins found by value re-derived; last digit of other levels redrawn), with a key per view.
  Each view opens with a sheet of ratios from earlier filings: eight quarters of revenue growth,
  operating margin and net margin. `check` tests every view; `fingerprint` is the rule attacker, a
  nearest neighbour over all 1,362 training and development companies' as-filed ratios. No model
  is called. An engineering step with no hypothesis and no verdict. Written 2026-11-20 and not
  yet run for the record. Development runs in the session's scratch space, on 48 training and
  development episodes drawn by seed (8 per cutoff side and size tier) and their 384 views: no
  identity term or calendar year left where the switch is on, no growth rate that loses its sign,
  no percentage touched by scaling. The attacker found the company in 45 of 45 episodes from the
  eight-quarter sheet at the planned bound of 2 points per ratio, with dates hidden; 84% at 4
  points, 49% at 8 points (84% within its top ten), 29% at 16. Exploratory, from the same
  episodes: one quarter of exact ratios finds 80%; one quarter at 2 points finds 22%; two
  quarters at 2 points, 36% (82% within the top ten). Known gaps: segment and product names that
  are common words stay (wave 2); orderings across segments and the position against guidance
  are not yet enforced under noise; numbers in prose without a currency sign or unit are left
  as they are.
- **EXP-0023** — S2-a transport for subagent calls: `emit` (items carry id, agent and prompt
  only, plus a canary), `pending`, `ingest` (a call counts only if its canary returns and the
  harness reports no tool use), `check`, `usage`. Written 2026-11-20; no study call made. Four
  configuration calls the same day (two each to `s2-recall-claude-sonnet-5-5` and
  `-opus-5-5`, then one each to an S2 and a roster definition after the disallowed-tools list
  was extended): every one answered, used no tool, and listed twelve harness tools still
  offered to it (artifacts, plugin and skill search, messaging, worktrees, task stop, the
  hand-back); each cost about 32,000 subagent tokens and 2 to 6 seconds. A definition cannot
  read a file, so a prompt the length of an earnings release (about 13,000 tokens) has to be
  passed through the session verbatim.
- **EXP-0025** — S2-a headless backend (changelog 2026-11-21, rule 7): `run` answers an EXP-0023
  outbox through `claude -p --agent <definition> --tools ""`, three processes at a time, and
  writes the inbox in EXP-0023's format, so the same canary check applies. Agreement check, an
  engineering measurement with no hypothesis, run 2026-11-21: 20 of EXP-0024's 210 closed-book
  prompts, drawn by seed 20261121, asked again headless of `s2-recall-claude-opus-5-5`. All 20
  returned their canary with no tool use; 2,000 tokens a call (3,900 in session), 7.5 seconds.
  Against the truth, each transport names the direction correctly in 17 of 20. The two agree on
  15: four of the five differences are mid-sized and small companies, each transport right in
  two, and the fifth is an after-cutoff prompt (UNKNOWN headless, a wrong guess in session).
  Median gap between the two growth figures 1.0 point (19 pairs). No sign that the transport
  changes the model's answers beyond what one sample per prompt varies; that variation itself,
  5 in 20, means later probes need repeated samples. Outputs in `s2/exp0025/` and
  `s2/dispatch/exp0025_agree/`. **Found afterwards (2026-11-21):** run inside the repository,
  this backend gave the model the project's auto-memory index and CLAUDE.md (see EXP-0027); the
  20 answers here were made with that context. Superseded by EXP-0027.
- **EXP-0027** — S2-a headless backend, isolated (fix forward of EXP-0025). Each call runs from
  an empty directory outside the repository with the definition passed inline, no settings read
  and auto-memory off. Verified 2026-11-21 by asking the model to quote its context: no memory,
  no CLAUDE.md, no tool; what the harness still attaches is one Agent SDK sentence before the
  definition's prompt, the account's e-mail address, today's date, "Assistant knowledge cutoff
  is June 2026" and the working-directory path. About 1,100 tokens of overhead a call. Seven
  calls of EXP-0026 made before the fix (three with EXP-0025, four with a first form of this
  script) are voided and kept in `s2/dispatch/exp0026/voided_*`. Every S2 result from this
  transport is a result for a model that is told the date and its own cutoff.

## Entries

## EXP-0026 — S2-b step 3: which element of blinding removes outcome leakage from the PM's call? (2026-11-21)

### PRE-REGISTRATION
- **Status:** running since 2026-11-21 (owner: "同意"). The script `exp0026_s2b_views.py`,
  with its scoring, was written after approval and before any call. `prepare` drew 60 old and 30
  clean episodes as specified (463 and 82 candidates; none skipped; 870 prompts, 39.6 million
  characters). Baselines before any reply: persistence 0.64 on old and 0.54 on clean episodes,
  reversal 0.36 and 0.46. Transport: EXP-0027, not EXP-0025 (see there).
- **Claim under test:** on old earnings releases of large companies, a PM call by Claude Opus 5.5
  on the raw text leans towards the outcome that happened, more than on releases after the
  cutoff; switching on elements of blinding (names, periods, scaling, noise) removes that lean;
  and asserting a wrong identity on a blinded release brings it back.
- **Why the answer is not obvious:** EXP-0024 shows the model recalls these outcomes when asked
  directly, but recall and its use in a forecast dissociate (`jia-2026`); a release already
  states this quarter's growth, so a good reader may lean the right way without memory; the rule
  attacker identifies every blinded view (EXP-0022), yet the model's memory is far weaker than a
  database; hiding dates left the pre-cutoff advantage in place in one study (`wu-2026`).
- **Sample and scope, fixed here before looking:** seed 20261122. Companies among the 250 largest
  by revenue of the training and development side; episodes outside the 2-point dead band; a
  press release with earnings words and at most 80,000 characters.
  - **Old:** 60 episodes from EXP-0021's pull (filed 2019 to 2025): 30 that accelerate and 30
    that decelerate, half from the top 50 and half from the 51st to 250th, one per company.
  - **Clean:** 30 episodes released after the cutoff (on the drive): 15 and 15, one per company.
  - **Arms.** (a) The eight views of EXP-0022 for all 90 episodes, sigma 0.02, with the ratio
    sheet cut to the two latest quarters (changelog 2026-11-20, item 3): 720 calls. (b)
    Transplant, old episodes only: the fully blinded view with one line added, "This is the
    release of <company> for the quarter ended <date>", naming another top-250 company-quarter
    drawn by seed among those whose realised direction is the opposite of the true one: 60
    calls. (c) No-document prior for all 90: company, ticker and quarter only: 90 calls.
  - Arms (a) and (b) run from `roster-claude-opus-5-5`, arm (c) from
    `s2-recall-claude-opus-5-5`, all headless (EXP-0025), one sample per call, three at a time.
- **Method and baseline:** the prompt asks, after the release, whether year-on-year revenue
  growth of the next quarter will be higher or lower than this quarter's, as `PROBABILITY: <0 to
  100 that it is higher>` and a rationale of at most three sentences. The **readout** is the
  probability given to the direction that happened. Sampling units are episodes; intervals are
  90% bootstrap intervals over episodes (10,000 draws, the seed above). Baselines on the same
  episodes, computed before any reply is read: a constant 0.5, persistence and reversal of the
  last change in growth.
- **Criteria:**
  1. **Leakage on raw text.** Mean readout of the raw view, old minus clean, at least 0.10 with
     its interval above 0.
  2. **Element effects.** For each of the four switches, the mean readout of the four views with
     it on minus the four with it off, on old episodes, minus the same contrast on clean episodes.
     A switch removes leakage if this is at most -0.05 with its interval below 0. H2 of the plan:
     the period's effect is more negative than the name's.
  3. **The fully blinded view.** Old minus clean mean readout of the view with all four on. No
     leakage detected if the interval contains 0; reported with criterion 5's detectable size,
     never as "none".
  4. **Transplant, the positive control.** On old episodes, the probability given to the asserted
     company's direction, transplant minus the fully blinded view, at least 0.10 with its
     interval above 0. If it fails while criterion 1 holds, the readout is reported as unable to
     see memory through a name, and criteria 2 and 3 are not interpreted.
  5. **Smallest detectable effect, before reading** (readout standard deviation taken as 0.30,
     one-sided 5%, 80% power): old against clean (60, 30) about 0.17; a paired contrast within 60
     old episodes about 0.10 if paired differences have standard deviation 0.30.
  6. **Information kept (descriptive).** On the 30 clean episodes: accuracy (probability above 50
     counted as "higher") of the raw view, the fully blinded view and the mean of the seven
     blinded views, beside the baselines. No threshold: 30 episodes detect only gaps near 30
     points.
  - Also reported: the same contrasts with the no-document prior subtracted; results by size
    tier; the share of rationales that name the company or a date in views where it is hidden
    (string match on the key).
- **Contamination label of the result:** old arms contaminated by design (the subject of the
  measurement); clean arms clean (vendor-stated cutoff). No blinded result is called clean.
- **Not in scope:** Sonnet; test-side companies; repeated samples; number edits; the consensus
  call's use in a playbook; sigma other than 0.02; small companies.

### VERDICT
- **Pre-registration commit:** none; the entry was written on 2026-11-21 before any call and is
  uncommitted with this verdict. The scoring code was written before the first call.
- **Run:** 2026-11-21, EXP-0027 transport. 870 calls, all with their canary, none with a tool
  use, every probability parsed; 11.4 million tokens (14,400 per document call). Seven earlier
  calls voided (EXP-0027).
- **Result** (readout: probability given to the direction that happened; 90% intervals):
  1. Leakage on raw text: **holds.** Old 0.778, clean 0.624; difference 0.155 (0.094 to 0.215).
  2. Element effects, old minus clean: names +0.006 (-0.009 to 0.019), periods +0.002 (-0.019 to
     0.022), scaling -0.028 (-0.048 to -0.010), noise +0.016 (-0.001 to 0.034). **No switch
     removes leakage**; none reaches -0.05. H2 holds in sign only and means nothing at this size.
  3. Fully blinded view: old 0.766, clean 0.616; difference 0.150 (0.095 to 0.203). **Leakage
     detected**, as large as on raw text.
  4. Transplant: **holds.** Asserting another company moves the call 0.111 (0.086 to 0.137)
     towards that company's outcome.
  6. Accuracy on clean episodes: raw 0.77, fully blinded 0.80, mean of blinded views 0.70, no
     document 0.63; persistence 0.54. On old episodes: 0.93, 0.93, 0.98, 0.85; persistence 0.64.
  - Also: the no-document prior alone has readout 0.78 on old episodes and 0.53 on clean ones.
    Rationales name the hidden company in 7 of 360 views and give a calendar year in 27 of 360
    where periods are hidden.
- **Failure analysis / slices (exploratory):** the eight views of an old episode give nearly the
  same call (raw and fully blinded correlate 0.95; mean gap 0.06). On old episodes the fully
  blinded call correlates 0.87 with the call made from the company's name and quarter alone, on
  clean ones 0.44, and old calls are as far from 0.5 as the memory-only calls (0.28 against 0.34;
  clean 0.17). No trend by filing year from 2019 to 2025. Where persistence is wrong the blinded
  readout on old episodes is still 0.73. Two readings fit and this run cannot separate them: the
  model recognises the company and quarter from a blinded release (the rule attacker does,
  EXP-0022; common-word segment and product names are left in); or old releases are easier to
  read than the one clean quarter (persistence 0.64 against 0.54), since old and clean differ
  in period as well as in exposure. The criterion-1 and criterion-3 differences carry that
  confound; the within-episode contrasts of criterion 2 do not.
- **Leakage sign-off:** clean arms are clean (vendor-stated cutoff); the model is told the date
  and its cutoff by the transport.
- **Verdict:** criteria 1 and 4 ACCEPT WITH SCOPE LIMIT (Opus 5.5, large companies, this call);
  the claim that these four elements remove the lean is **REJECT**: wave-1 blinding, by code,
  changes the PM's call by less than 3 points of readout while a name alone moves it by 11. H1 of
  the plan (the re-test of GY-0000) is not met by wave 1. Next, to separate the two readings: ask
  the model to name the company and quarter of the fully blinded views (the attacker of plan
  §6), and compare clean and old episodes matched on the persistence baseline.

## EXP-0024 — S2-b step 2: where does the model's recall of outcomes end? (2026-11-20)

### PRE-REGISTRATION
- **Status:** not yet run. Waits on the owner's choice of transport and usage budget (each
  subagent call costs about 32,000 tokens, measured 2026-11-20). Written before any reply exists.
- **Claim under test:** told only a company and a quarter, Claude Opus 5.5 recalls whether the
  next quarter's year-on-year revenue growth rose or fell, for outcomes filed before its
  cutoff, and does not for outcomes filed after it. The question is where, between 2019 and the
  cutoff, that recall fades: strategy C uses the raw text of episodes the model cannot recall.
- **Why the answer is not obvious:** recall of a forecast target is measured for frontier models
  on macro series and headline figures, not on the growth direction of 1,300 companies of every
  size; HindsightBench (`jia-2026`) finds measured cutoffs earlier than vendors' dates; memory of
  small companies may be nil in every period.
- **Sample and scope, fixed here before looking:** `exp0024_s2b_recall_probe.py prepare`, seed
  20261121. EXP-0020's labelled episodes of training and development companies, outside the
  2-point dead band. Seven bins by the date the outcome quarter was first filed (2019-2021,
  2022-2023, 2024, 2025H1, 2025H2, 2026H1 to the cutoff, after the cutoff to 2026-11-11) by three
  size tiers (top 50, 51 to 250, the rest), ten company-quarters per cell, one quarter per
  company per cell: 210 prompts. One sample each from `s2-recall-claude-opus-5-5`, carried by
  EXP-0023; a call counts only with its canary and no tool use.
- **Method and baseline:** the prompt names the company, its ticker and two quarter-end dates,
  shows no document, and accepts UNKNOWN. Scores per bin: answer rate; direction accuracy over
  all prompts (UNKNOWN counts as wrong) and over answered ones; median absolute error of the
  growth figure and the share that beats persistence (this quarter's growth carried forward).
  The baseline for every bin is the after-cutoff bin, which the model cannot have seen: there,
  any accuracy comes from what it knows of the company.
- **Criteria:**
  1. Recall in a bin: direction accuracy over all prompts at least 15 points above the
     after-cutoff bin, with the 90% bootstrap interval of the difference above zero (resampled
     prompts, seed 20261121, 10,000 draws).
  2. Where recall ends: the latest bin before the cutoff that meets criterion 1.
  3. Recall on large companies, the S2-b step 1 question: the top-50 and 51-to-250 tiers pooled
     over the three bins from 2019 to 2024 (60 prompts) against the same tiers after the cutoff
     (20 prompts), by criterion 1. If it fails, the plan's §16 condition "no measurable leakage
     on raw text for this call" is reported as met, at this sample size.
  4. Smallest detectable effect, computed before reading (accuracy near 50%, one-sided 5%, 80%
     power): 30 prompts in a bin against 30 after the cutoff, about 32 points; the three bins
     from 2019 to 2024 pooled (90) against 30, about 26; criterion 3's 60 against 20, about 32.
     A smaller difference is reported as not detected, not as absent.
- **Contamination label of the result:** prompts on outcomes filed before the cutoff probe
  contaminated items by design; the after-cutoff bin is clean (vendor-stated cutoff).
- **Not in scope:** Sonnet (the §12 comparison); repeated samples per prompt (one sample gives
  rates per bin, not a propensity per company-quarter); any document.

### VERDICT
- **Pre-registration commit:** none; the repo has not been committed since. The entry above was
  written, and its arithmetic corrected, before the first call; the scoring code for criteria 1
  to 3 was added after the calls and before any score was computed.
- **Run:** 2026-11-20, owner's go-ahead ("好的"), in-session transport (EXP-0023), three calls in
  flight. 210 prompts and one retry (a reply with its canary in the middle); every call reported
  no tool use. 825,000 subagent tokens in all, 3,900 per call, 5 seconds per call. Prompt names
  were re-cased and the items re-emitted before the first call.
- **Result:** direction accuracy over all prompts, before the cutoff, by bin: 2019-2021 0.77,
  2022-2023 0.87, 2024 0.77, 2025H1 0.93, 2025H2 0.97, 2026H1 0.77; after the cutoff 0.30 (the
  model answers UNKNOWN to 63% there; 9 of its 11 answers are right). Criterion 1 holds in every
  bin (differences 0.47 to 0.67, every 90% interval above 0.27). Criterion 2: recall reaches the
  last bin, 2026H1 (outcomes filed January to June 2026). Criterion 3: the 60 large-company prompts
  of 2019-2024 score 0.90 against 0.30 (difference 0.60, interval 0.42 to 0.77). The growth figure
  is recalled, not inferred: median absolute error for the 50 largest companies 0.06 to 0.23
  points in every bin from 2019 to 2025H2, for the next 200 0.2 to 3.9 points, for the rest 2.6 to
  25 points; after the cutoff the model gives two figures in 30.
- **Failure analysis / slices:** criterion 1 counts UNKNOWN as wrong, so it mixes recall with the
  willingness to answer; the numeric errors settle that the willingness reflects memory. Small
  companies are the exception: direction 0.40 to 0.90 by bin and errors of several points, so
  some old small-company episodes may be usable raw. The format example "7.5%" anchored at least
  one reply, which said so (prompt p0145); kept for comparability, to be replaced in later probes.
  One sample per prompt; 30 per bin.
- **Leakage sign-off:** the after-cutoff bin is clean (vendor-stated cutoff 2026-06-30); the
  replies there say the outcomes are after the model's data.
- **Verdict:** ACCEPT WITH SCOPE LIMIT, for Claude Opus 5.5 and this call. The model recalls the
  next quarter's revenue growth of large and mid-sized companies, nearly to the decimal, for every
  period from 2019 to the cutoff. The plan's §16 condition "recall is saturated for every old
  episode of a large company" is met: strategy C offers those companies nothing before the cutoff,
  and their history depends on blinding (A, B) or on other strategies. The condition "no
  measurable leakage on raw text for this call" is not met.

## EXP-0016 — S1-c calculator: the distilled 0.8B and the 4B, both with a calculator (2026-11-21)

### PRE-REGISTRATION
- **Status:** draft, 2026-11-21, from the owner's decisions of 2026-11-20 and 2026-11-21: a
  calculator, reported apart from tool-free results; a fresh test draw; the calculator at decoding
  only, no retraining; the same calculator for the large and the small model, compared with both
  equipped ("工具要跟大模型和小模型同时都可以使用"), then the remaining errors analysed to choose
  the next step; the calculator recognises written arithmetic, plain or LaTeX, with no change to
  the prompts; small model D3 only; the tool-free 4B also run. Approved by the owner 2026-11-21
  ("批准，开始实现"). Before the commit: the script was written, the calculator checked on
  development items (step 3 below, with its result and the one rule it added) and the test draw
  made (step 2, with its counts and hash). Nothing is run on a test item before the commit is
  pushed. Committed and pushed as `e26d26f`; run 2026-11-21 to 22; verdict below.
- **Claim under test:** EXP-0014 found the distilled 0.8B (D3) matches the 4B on lookups (B1) but
  scores 48.1% on calculations (B2), below the untrained 0.8B: it sets up the right expression and
  gets the arithmetic wrong (EXP-0015). The owner's aim is not the tool itself but whether, with
  the same tools, the small model performs like the large one. HC1: the calculator raises D3's B2
  accuracy. HC2: with the calculator, D3 is non-inferior to the 4B with the calculator, within 3
  points. HC3: the calculator narrows the gap between them.
- **Why the answer is not obvious:** in EXP-0015, 392 of 696 (seed 1) and 402 of 613 (seed 2) of
  D3's wrong B2 answers wrote an expression that evaluates to the gold, which bounds its gain near
  31 points. But that count used a lenient after-the-fact parse; at decoding the expression must
  be caught as it is written, the inserted value (four decimals) is unlike anything D3 saw in
  training and may derail what follows, and the model must still round, sign and box it. The 4B
  already gets 92.5% of B2 right without a tool, so it has less to gain, but it may also lose
  where the calculator interrupts long LaTeX working. If D3's remaining errors are reading errors
  (wrong rows, periods or formulas), no calculator closes HC2.
- **Sample and scope, fixed here before looking:**
  1. **Models.** The two D3 checkpoints EXP-0014 chose on development (`s1/exp0014/dev/
     chosen.json`: D3-s1 and D3-s2, both epoch 2) and Qwen3.5-4B (`32f3e8e`). No training.
  2. **Test draw.** EarningsExam v0.2 test items (post-cutoff releases of test companies) from
     releases (accession numbers) none of whose items is in EXP-0014's draw, so no fact is asked
     twice across the two experiments. Because the calculator idea came from counts on EXP-0014's
     test items, those items are not reused. Target 1,500 B1 and 1,500 B2 items, at most 3 per
     company over the whole draw. Within a section, metrics are taken round robin, each metric's
     items in the order of SHA-256 of `"exp0016-test:" + id`; a metric that runs out passes its
     places to the others of its section, and a section that runs out passes its places to the
     other. If fewer than 3,000 items qualify, all that qualify are used and the count is
     reported. Counts before drafting (no item text): 5,937 items from 1,107 companies qualify,
     about 3,000 under the company cap, mostly second phrasings and held-out metrics, so the draw
     is weighted to unseen templates, unlike EXP-0014's. Every comparison below is within this
     draw. Made by script; items are never shown to Claude. **Made 2026-11-21:** 3,000 items
     (B1 1,650, B2 1,350: B2 ran out and passed 150 places to B1) from 1,101 companies and 1,310
     releases; 370 items on templates seen in EXP-0014's training, 2,630 unseen; no release in
     common with EXP-0014's draw. SHA-256 of the ids in draw order, one per line:
     `251720e6cb4727ed5f1bb37927b1312da5276aeb9bdcfbca16bc653937794460` (`s1/exp0016/
     test_draw.jsonl` on the data drive, ids only).
  3. **Development check**, before the test draw is opened: D3 (both seeds) and the 4B, each with
     the calculator, on the 600 EXP-0007 development items. Parser and insertion bugs may be fixed
     here, on development only; the code is then frozen and committed. Reported before the
     commit: the share of B2 answers with at least one call, for each model. If it is below 50%
     for either model after bug fixes, the owner decides before the commit. No choice is made
     from development accuracy. Claude may read these development answers. **Result,
     2026-11-21.** First run: B2 answers with a call, C 97.5% and 96.7% (seeds 1, 2), 4C 42.5%.
     Of the 138 4C B2 answers with no call, 114 put the arithmetic after the `=` on one line and
     the result on the next (`Label = <arithmetic>`, then `Label \approx`); most of the rest needed
     no arithmetic. That layout is a recognition gap, so the chained rule (method, step 2) was
     added, with 7 parser cases, and all three runs were redone (the first run is kept as
     `dev_v1/`). Second run, final code:

     | | B1 with a call | B2 with a call | calls per B2 answer | B1 acc. (tool-free) | B2 acc. (tool-free) | forced |
     |---|---|---|---|---|---|---|
     | C-s1 | 39.7% | 97.5% | 0.97 | 94.7 (94.4) | 76.7 (45.8) | 0 |
     | C-s2 | 41.4% | 96.7% | 0.97 | 93.9 (93.9) | 75.0 (50.8) | 0 |
     | 4C | 27.5% | 96.7% | 1.55 | 91.9 (93.1) | 87.1 (88.3) | 24 (12) |

     Both models are above 50%, so no owner decision is needed. Read, not acted on (they are
     how the models respond to a correct value, not parser bugs): the 4B often writes a wrong
     expression and the right result (e.g. dividing by 1,000 to turn dollars into millions) and,
     handed the true value of what it wrote, sometimes follows it; in 22 4C answers the chained
     value already includes `\times 100` and the 4B writes `\times 100` after it again. C's
     residual B2 errors are reading errors: a loss shown without its sign, the wrong row or
     column, or a rounded "% Change" copied instead of calculated.
- **Method and baseline:**
  1. Arms, all thinking off, greedy, then EXP-0007's forced answer if no box was written:
     **D3** (tool-free, terse prompt, at most 160 generated tokens, as EXP-0014); **C** (D3 with
     the calculator); **4B** (tool-free, EXP-0011's standard prompt, at most 512 generated tokens,
     as EXP-0014); **4C** (the 4B with the calculator). Prompts are unchanged; neither model is
     told about the calculator.
  2. **Calculator**, the same code for every arm. After each generated token, if the text ends in
     `=` or `\approx`, the stretch before it is taken back to the first character that is not
     part of written arithmetic: digits, `.` `,`, the operators `+ - * / × ÷`, brackets `( )` and
     braces `{ }`, spaces, `$` `%` `\%`, and the LaTeX commands `\frac` `\dfrac` `\times` `\cdot`
     `\div` `\left` `\right` `\,`. If it holds at least two numbers joined by an operator, decoding
     stops. The stretch is cleaned (thousands separators, `$` and `%` removed; `\frac{a}{b}` to
     `(a)/(b)`; `\times`, `\cdot`, `×` to `*`; `\div`, `÷` to `/`; `\left`, `\right` dropped) and
     evaluated by an arithmetic-only parser (no `eval`). On success, a space and the value rounded
     to four decimals, trailing zeros dropped, no separators, are appended and decoding resumes
     from the full text; on failure (no parse, division by zero) nothing is appended. At most 8
     calls per answer. Appended tokens do not count against the generation cap. **Chained rule,
     added on development (step 3):** the 4B writes `$$ \text{Growth} = \frac{a - b}{b} \times
     100 $$` and opens the next line with `$$ \text{Growth} \approx`, so nothing it writes
     before a trigger is arithmetic. When a trigger is the first on its line, follows at most 80
     characters of label, and the previous line ends in `=` or `\approx` followed by nothing but
     written arithmetic (trailing `\\`, `\]`, `\)`, `.` and spaces dropped) that evaluates, that
     value is appended. Each call records which rule fired.
  3. Grading by `exp0010.grade` on the model's own boxed answer. A D3 or C score per item is the
     mean over its two seeds. Intervals: paired, bootstrap over companies, 10,000 resamples, seed
     20261121.
- **Criteria** (new family HC1 to HC3; each reported at α = 0.0125, as EXP-0014):
  1. **HC1:** Δ = C − D3 on B2 items. Supported if Δ ≥ 5.0 points and the one-sided test of
     Δ > 0 rejects at α = 0.0125. Refuted if the upper end of the 97.5% interval is below 5.0.
     Otherwise inconclusive.
  2. **HC2 (the owner's question):** Δ = C − 4C on all items. Non-inferior if the lower end of
     the one-sided 98.75% bound is above −3.0. Refuted if the upper end of the 97.5% interval is
     below −3.0. Otherwise inconclusive.
  3. **HC3:** Δ = (4B − D3) − (4C − C), how much the calculator narrows the gap, on all items.
     Supported if Δ ≥ 3.0 points and the one-sided test of Δ > 0 rejects at α = 0.0125. Refuted
     if the upper end of the 97.5% interval is below 3.0.
- **Error analysis, to choose the next step** (descriptive): every wrong answer of C and 4C is
  sorted by script, in this order, into: no number; no calculator call on a B2 item; the boxed
  value differs from the last inserted value after rounding to the asked decimals (copying or
  rounding); the inserted value is right by magnitude but the sign or unit of the box is wrong;
  wrong setup (the evaluated expression is not the gold). Wrong setups are split further where
  the script can: an operand equal to no number in the excerpt, against operands from the
  excerpt combined in a wrong formula. Claude reads the residual development errors of C and 4C
  (not test) and names patterns the script cannot. Counts only on test.
- **Also reported, descriptive:** every arm by section, metric, seen and unseen template; C − D3
  and 4C − 4B on B1 (the calculator should not hurt lookups); C − 4B, the tool-free comparison of
  EXP-0014's H2; calls per answer and the share of answers with a call; forced and invalid rates;
  seed spread; section A (EXP-0014's 100 items each of FinQA, CFA-Easy and FinanceIQ) for C and
  4C, against D3 and the untrained 0.8B in EXP-0014.
- **Contamination label of the result:** clean. Test items come from releases accepted after
  2026-06-30, from releases EXP-0014 did not use. No model labels a test item; nothing is trained.
- **Not in scope:** retraining with calculator annotations; D1, D2 or the untrained 0.8B with the
  calculator; tools other than the calculator; rerunning EXP-0014's other arms on the new draw.
- **Estimated compute:** development check about 70 minutes (D3 two seeds, 4B); on the test draw,
  4B and 4C about 4 hours each, D3 and C about 1.2 hours each for two seeds; section A about 40
  minutes. About 12 hours.

### VERDICT
- **Pre-registration commit:** `e26d26f` (pushed before any model saw a test item). Run
  2026-11-21 20:15 to 2026-11-22 07:30 by `queue`, every step complete: D3 and C about 35
  minutes a seed, 4B 4.0 hours, 4C 4.2 hours, section A 0.75 hours. Output:
  `s1/exp0016/scores.json`.
- **Result** (3,000 test items of the fresh draw, accuracy %, D3 and C the mean of two seeds;
  intervals 97.5%, company bootstrap, 10,000 resamples):

  | Arm | All | B1 (1,650) | B2 (1,350) | Seen (370) | Unseen (2,630) | Seeds |
  |---|---|---|---|---|---|---|
  | D3 distilled 0.8B | 71.6 | 92.8 | 45.6 | 75.8 | 71.0 | 70.0 / 73.2 |
  | C D3 + calculator | 86.7 | 93.0 | 79.1 | 85.0 | 87.0 | 86.3 / 87.2 |
  | 4B | 91.3 | 91.9 | 90.7 | 86.8 | 92.0 | |
  | 4C 4B + calculator | 89.4 | 90.6 | 87.9 | 84.9 | 90.0 | |

  B2 answers with a call: C 98.7% and 98.3%, 4C 97.9% (1.5 calls each); B1, 37 to 38% and 28%.
  Forced answers: D3 and C at most 0.1%, 4B 2.3%, 4C 3.6%; invalid at most 0.1%.

  1. **HC1 supported.** C − D3 on B2 = +33.4 [30.8, 36.2], one-sided p < 0.0001. The bound of
     about 31 points from EXP-0015 is reached; the inserted values did not derail D3.
  2. **HC2 inconclusive.** C − 4C on all items = −2.6 [−4.4, −0.9]. The point estimate is inside
     the 3-point margin but the lower bound is not, so non-inferiority is not shown; nor is it
     refuted. The difference is not zero: with the same calculator, the small model is still
     behind. By section it is two different stories: on B1 C is ahead, +2.4 [0.5, 4.3]; on B2 it
     is behind, −8.8 [−11.5, −6.1].
  3. **HC3 supported.** (4B − D3) − (4C − C) = +17.1 [15.5, 18.7]: the calculator shrinks the
     gap from 19.7 points to 2.6, partly because it costs the 4B points (below).
- **Also reported:**
  1. **The calculator does not hurt lookups for D3** (C − D3 on B1 +0.2 [0.0, 0.4]) **but costs
     the 4B on both sections:** 4C − 4B = −1.3 [−2.4, −0.2] on B1 and −2.8 [−4.0, −1.7] on B2.
     Against the tool-free 4B (EXP-0014's H2 comparison), C − 4B = −4.6 [−6.3, −2.9].
  2. **By B2 metric**, C against 4C: EPS change 77.6 against 83.0, revenue growth 88.5 against
     86.1, gross margin 77.7 against 97.4, operating margin 71.1 against 94.1, net margin 58.9
     against 92.9 (84 items). C's gap is in the margins, where a row must be divided by revenue;
     on growth it matches the 4B. D3's B2 by metric: 69.5, 22.4, 25.1, 55.6, 46.4.
  3. **Seen and unseen templates:** C scores about the same on unseen (87.0) as on seen (85.0);
     the gain carries to second phrasings and held-out metrics.
  4. **Section A**, 100 items each, C seeds 1 / 2 against D3 in EXP-0014: FinQA 28 / 27 against
     10 / 11, CFA-Easy 20 / 13 against 20 / 13, FinanceIQ 28 / 23 against 28 / 23; 4C 65, 68, 49
     (no tool-free 4B run on section A). The calculator restores much of FinQA, which needs
     arithmetic, but C stays below the untrained 0.8B there (38).
- **Error analysis** (registered categories, test counts; development read by Claude):

  | Wrong answers | C-s1 B2 | C-s2 B2 | 4C B2 | C-s1 B1 | C-s2 B1 | 4C B1 |
  |---|---|---|---|---|---|---|
  | total | 285 | 280 | 164 | 127 | 104 | 155 |
  | no number | 0 | 0 | 2 | 0 | 0 | 2 |
  | no call (B2) / no call, lookup wrong (B1) | 9 | 11 | 21 | 71 | 68 | 64 |
  | copying or rounding | 2 | 4 | 32 | 0 | 0 | 16 |
  | sign or unit of the box | 49 | 52 | 24 | 3 | 1 | 55 |
  | wrong setup: operand not in the excerpt | 0 | 1 | 7 | 28 | 17 | 5 |
  | wrong setup: excerpt operands, wrong formula | 225 | 212 | 78 | 25 | 18 | 13 |

  1. **D3's arithmetic problem is solved; its reading problem is what is left.** About 77% of C's
     wrong B2 answers evaluate an expression built from numbers in the excerpt that is not the
     gold. On development these were the wrong row (gross profit for operating income), the
     wrong column ("$ Change" for the current period) or the wrong pair of periods, more often
     than a wrong formula; the script cannot tell them apart. Another 18% have the right
     magnitude and the wrong sign: the table shows "Loss from operations" as a positive number
     and the model keeps it positive.
  2. **The 4B's losses with the calculator are interaction errors.** Its 32 B2 and 16 B1
     "copying or rounding" errors and 55 B1 "sign or unit" errors are where it wrote an
     expression it would not have evaluated literally (on development, dividing by 1,000 to turn
     dollars into millions while stating the right millions) or wrote `\times 100` after a value
     that already included it, then followed the inserted value.
- **Leakage sign-off:** test items from releases accepted after 2026-06-30 and not used by
  EXP-0014; scripts printed counts and rates only. Claude read development answers only. No
  model labelled a test item; nothing was trained. Clean.
- **Verdict:** HC1 and HC3 supported, HC2 inconclusive. A calculator lifts the distilled 0.8B's
  calculations by 33 points and brings it within 2.6 points of the 4B with the same calculator
  (4.6 of the tool-free 4B): ahead on lookups, 8.8 points behind on calculations. What separates
  them now is reading the table for a calculation (the right row, column and periods, and the
  sign of a loss), not arithmetic. Bolted onto the 4B, the calculator costs it 1 to 3 points,
  because it evaluates what the 4B writes rather than what it means. Next steps go to the owner.

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
