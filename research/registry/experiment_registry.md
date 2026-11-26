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
- **EXP-0019** — EarningsExam section R v0 generator, step R-a of the S1 reasoning exam
  (`research/design/s1_reasoning_exam.md`; owner, 2026-11-23: decisions D1 to D5 as recommended;
  2026-11-24: "开始"). `exp0019_s1r_build.py`. An engineering measurement with no hypothesis and
  no verdict; no model run. It reuses EarningsExam's releases, sides, parser, XBRL period and
  two-source rule (every figure shown in a labelled row at the table's scale and equal to XBRL's
  first-filed value; prior-year figures in the same row and equal to XBRL's prior-year value), adds
  seven line items (cost of revenue, R&D, SG&A, total operating expenses, total costs and
  expenses, income before taxes), and raises the excerpt budget to 800 tokens (D2). Templates
  R1.1 to R1.9 and twins (flip by swapping the two years in the column headings; hold by an added
  employee-count row; mirror by swapping the question's subjects), with every rule as written in
  the script's docstring. Two departures from the design: the flip twin swaps the period labels
  instead of editing one figure and its totals (that cannot be done reliably in raw release
  text; a swap keeps every column consistent), and R1.4 uses EPS and net income without
  verifying the diluted share count. Every R question ends with the same "cannot be determined"
  sentence, whatever the gold.
  Run 2026-11-24 (fixed rule and swap cases pass). Claude read about 20 train and development
  items across every template and twin kind and found no wrong gold; two fixes were made before
  the test side was built (growth questions now say a smaller decline counts as faster growth;
  the hold row moved from a random position, where it could split a subtotal, to the end of the
  table). Yield, base items (companies), with twins in all:

  | Side | Base items | Companies | Releases | All items with twins |
  |---|---|---|---|---|
  | train | 3,352 | 621 | 621 | 8,814 |
  | dev | 4,289 | 295 | 713 | 10,903 |
  | test (counts only) | 16,329 | 1,548 | 2,654 | 40,538 |

  Test base items by template: R1.1 2,923 (975 companies), R1.2 1,203 (733), R1.3 520 (323),
  R1.4 376 (260), R1.5 684 (465), R1.6 617 (382), R1.7 4,487 (1,252), R1.8 1,916 (828), R1.9
  3,603 (1,204). Labels are unbalanced (test R1.1: expanded 1,597, contracted 998, flat 328; R1.2:
  both rose 707 of 1,203; R1.6: R&D 28 of 617), so balanced sampling per template is fixed in the
  pre-registration that uses them. Test excerpts: median 676 tokens, 90th percentile 791. The
  main losses, of 4,265 test releases: a figure not found in a labelled row at XBRL's value
  (revenue 919, net income 1,070, income before taxes 1,064), losses
  in either year (R1.4, R1.5), excerpts over 800 tokens or without a column heading (R1.1 loses
  1,403 candidates on test), heading years not symmetric (no flip twin; 349 for R1.1 on test).
  The identity checker found no twin to reject; on base excerpts it applies to about 40% and
  fails on 4%, all parser artefacts in the cases read (footnote markers read as −1, a component
  line matched before the total), not gold errors, since gold rows are matched to XBRL. Output
  `s1/exam_r_v0/items_{train,dev,test}.jsonl`, `yield_*.json`; SHA-256 of the test ids in file
  order `a281dcf6b9e9d3d54ad7633b1619ea41620601cfdc113df5c56f26f56a415c96`.
- **EXP-0030 to EXP-0039** — held for sub-study S2 as well (2026-11-21; the first block is used up).
- **EXP-0020 to EXP-0029** — held for sub-study S2 (`research/design/substudy_s2_blind_replay.md`),
  so that S1 and S2, worked on in separate sessions, do not take the same number. S1 continues
  from EXP-0016.
- **EXP-0020** — (Added 2026-11-22: EXP-0034 finds a comparison-base rule, g(t-3) < g(t-4), right
  on 65% of acceleration episodes; "best simple rule 52%" below holds only for the rules tried.)
  S2-a episodes, candidate labels and rule baselines: for the training and
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
- **EXP-0037** — S2-a census of company-written text furnished with earnings 8-Ks (owner,
  2026-11-23: "可以先从这边数一下八K的附件"). Reads the filing index pages already cached on the
  drive for the training and development companies' earnings 8-Ks (EXP-0020's release list); no
  network, no model. For each filing, every exhibit other than the press release EXP-0003's rule
  picks, XBRL files and graphics is classed by its description and file name (rules fixed in the
  script before the run): call commentary (prepared remarks, CFO commentary, shareholder letter,
  script, transcript), presentation, supplemental financial data, other, unlabelled. Counts of
  filings and companies by class, before and after the cutoff, for the 500 largest companies and
  the rest. An engineering measurement with no hypothesis and no verdict; it decides whether a
  pull of index pages for the full 2019 to 2025 history of the companies that furnish commentary
  is worth asking for. Run 2026-11-23: 5,764 index pages found (2,486 for the 500 largest
  companies, 498 of them). Named call commentary is rare: 13 of the 498 largest companies (12 of
  1,047 others), e.g. Edison International's prepared remarks every quarter; but 1,208 of the
  extra exhibits carry no description beyond "EX-99.2" and file names cut to 25 characters, so
  the count is a lower bound. Output `s2/exp0037/census.json`.
- **EXP-0038** — S2-a census, second step (fix forward of EXP-0037's unlabelled exhibits; within
  the owner's approval of 2026-11-23 to count 8-K exhibits). For the 500 largest training and
  development companies only, fetches from EDGAR each EX-99 exhibit that EXP-0037 left
  unlabelled (one request each, about 400 to 500, through edgartools with the contact string
  from `EDGAR_IDENTITY`) and classes it by its text with rules fixed in the script before the run:
  transcript, prepared remarks or script, CFO commentary, shareholder letter, presentation,
  supplemental financial data, another press release, other; PDFs are counted, not read. Thirty
  exhibits drawn by seed are checked by hand against the rules. Exhibits stay on the drive. An
  engineering measurement with no hypothesis and no verdict. Run 2026-11-23: 552 fetched, 7 PDFs
  (Constellation Brands) counted. Classes: other 205, presentation 172, supplemental financial
  data 104, another press release 63, transcript 4, shareholder letter 3, prepared remarks 1. Hand
  check of 30: 21 right; the 9 wrong are all confusions among presentation, supplement, press
  release and other; none is call text missed or call text claimed. All 8 exhibits classed as
  call text read by hand: 7 right (FTI Consulting furnishes its FactSet call transcript, three
  quarters of 2026; DoorDash and Opendoor letters; an L3Harris investor letter), 1 wrong (a
  Flutter press release, classed transcript). A scan of the other 545 texts for call markers found
  no missed call text. Joined with EXP-0037 and the Flutter exhibit dropped: 17 of the 498 largest
  companies (16 company groups; Edison International files under two CIKs) furnish call text in
  at least one of their cached earnings 8-Ks, in 26 of 1,520 pre-cutoff and 17 of 966
  post-cutoff filings: prepared remarks or scripts (Edison International, Terex, Philip Morris,
  Starbucks, Snap, Match Group, Seagate), shareholder letters (Etsy, DoorDash, Warner Bros.
  Discovery, Maplebear, Unity, Opendoor, L3Harris), CFO commentary (Columbia Sportswear),
  transcripts (FTI Consulting). 8 of the 190 companies in EXP-0036's clean episodes are among
  them. Output `s2/exp0038/census.json`. Reading (ours): 8-K exhibits carry call text for about 3%
  of large companies, too few for a call module; IR-site transcripts (about half the companies,
  `research/design/s2_ir_transcript_survey.md`) are the source.
- **EXP-0039** — S2-a collection of earnings-call text from company IR sites for EXP-0036's clean
  episodes (owner, 2026-11-23: "开始", approving the plan put to him the same day). Scope: the 190
  companies of EXP-0036's 197 clean episodes; for each, the call that followed the clean-window
  release. Subagents (at most three at a time, batches of about 24 companies) look only on the
  company's own IR site and the hosts it links its files from, return file addresses and stop at
  any refusal (403, bot check); no third-party transcript site, no log-in. The script downloads
  the files to the drive (never git, rule 12), extracts text (pdfminer.six for PDFs), reads the
  call date and producer from the first page and flags a call dated more than one day before or
  three days after its release (owner's dating rule). An engineering collection with no
  hypothesis and no verdict; the experiment that uses the text is pre-registered separately.
  First pass, 2026-11-23 (eight batches; from batch 4 on, the subagents had to open the IR
  results or events page before saying "none found"): of 190 companies, 29 found, 5 prepared
  remarks or letter only, 103 none found, 53 refused (HTTP 403). 42 files downloaded (13 MB, one
  address 404): 31 companies with a full transcript, every one with Q&A markers, 36 with any call
  text; producers seen: FactSet CallStreet 11, S&P Global 4, ViaVid 3, LSEG 2, the rest
  unstated. Every dated file is the July or August 2026 call, 1 day before to 1 day after its
  release; every undated one names the right company and quarter. Batch 2 searched less (no page
  opened for 11 companies) and 39 negatives elsewhere rest on pages built by JavaScript or
  addresses that did not resolve; these 56 are rechecked in the built-in browser (found_9). LCI
  Industries' transcript and Terex's prepared remarks exist only as 8-K exhibits.
  Browser recheck, same day: 5 more transcripts (W. R. Berkley, Northern Oil & Gas, OPENLANE,
  Lincoln Electric, Lincoln National) and Palantir's letter, whose page renders its text by
  script and gave none; no page showed a bot check. LCI's transcript taken from its 8-K exhibit
  (Item 7.01, filed 2026-08-07). Final: 37 companies with a full transcript (38 clean episodes;
  Stride's call belongs to one of its two releases), 42 with any call text; 18 of the transcript
  companies are among the 250 largest; producers seen FactSet CallStreet 12, S&P Global 6, LSEG
  3, ViaVid 3. 53 companies refused the fetch tool (28%) and were left alone. Output
  `s2/exp0039/summary.json`, `extracted.jsonl`, `texts/`.
- **EXP-0040 to EXP-0049** — held for sub-study S2 as well (2026-11-23; the block EXP-0030 to
  EXP-0039 is used up). S1 continues from EXP-0019 and skips S2's blocks.
- **EXP-0050 to EXP-0059** — held for sub-study S1 (owner, 2026-11-23, decision D5 of
  `research/design/s1_reasoning_exam.md`: S1 takes the next free block after S2's). S1 uses
  EXP-0019 first, then this block for the reasoning exam (section R); S2 continues from EXP-0060.
- **EXP-0040** — S2-a collection of earnings-call transcripts from Alpha Vantage for EXP-0036's
  clean episodes (owner, 2026-11-23: "此外我会给你free tier alpha vantage api （25 use per day in
  US timzeone）"). Scope: the 197 clean episodes (190 companies); one request to
  `EARNINGS_CALL_TRANSCRIPT` per episode, for the fiscal quarter that the company's own 10-Q or
  10-K reporting the episode's quarter labels (`fy`, `fp` in the company-facts snapshot of
  2026-11-14; `FY` read as the fourth quarter). Order, fixed before any request: three
  validation episodes among the 38 with an IR transcript from EXP-0039 (drawn by seed 20261125:
  one whose fiscal quarter is the calendar quarter, two whose fiscal quarter is not, where there
  are such), then the 159 episodes without an IR transcript by revenue rank, then the other 35
  with one. At most 25 requests a US Eastern day, counted in a local ledger, 15 seconds apart;
  a reply that reports the request limit stops the run and is not recorded as data. The key is
  read from `ALPHA_VANTAGE_API_KEY` in the `nlab` environment, set there by the owner; it never
  enters git, a log or a printed line. Raw replies stay on the drive (rule 12). Checks on every
  reply: full transcript = at least 10 speaker turns and 5,000 characters; the company's name or
  ticker in the first 5,000 characters; the ordinal quarter named most often in the first 6,000
  characters equals the requested fiscal quarter; question-and-answer markers. Where an IR
  transcript exists, the share of Alpha Vantage's word 8-grams found in the IR text; 0.5 or more
  counts as the same call. Stop rule: if two of the three validation episodes fail the quarter
  check or the same-call check, no further request is made and the owner is told. Alpha Vantage
  states no call date; the call takes its release's date (owner's dating rule of 2026-11-23),
  and a date printed in the text, if any, is flagged when it falls outside one day before to
  three days after the release. Not in scope without the owner's word: the 60 old episodes and
  the October and November 2026 calls. About eight days at 25 a day. An engineering collection
  with no hypothesis and no verdict; the experiment that uses the text is pre-registered
  separately. Output `s2/exp0040/`. `targets` built 2026-11-23, before any request, after two
  fixes to the first draft: a quarter ending in the first days of July (52/53-week years) is the
  calendar second quarter (the quarter end moved back 15 days), and Stride's IR call covers both
  of its releases for the same quarter. Result: 197 episodes, 187 distinct requests (five
  companies filed two releases for one quarter); three subsidiary filers with no listed ticker
  of their own (Novelis, Evergy Kansas Central, Oklahoma Gas & Electric) are left out; 23
  episodes have a fiscal quarter other than the calendar one. Validation draw: Coupang 2026Q2
  (calendar), Modine 2027Q1 and Stride 2026Q4 (fiscal).
  **Run 2026-11-22 (US Eastern), with a defect:** `fetch` neither paused after the validation
  episodes nor dropped a request already sent in the same run, so it went past the validation
  stage before `check` and asked for Tesla's call twice; stopped by hand after 20 requests.
  Validation: Coupang and Stride pass (quarter named; 8-gram share in the IR text 0.72 and 0.60);
  Modine comes back empty. One failure of three, so the stop rule does not apply. Of the 17
  requests past validation, 12 distinct full transcripts (Apple, Tesla, Sunoco, General
  Dynamics, World Kinect, Philip Morris, CRH, US Foods, Amphenol, Cummins, RGA, Union Pacific),
  every one naming the company and with question-and-answer markers; empty for Energy Transfer,
  SUNC, Plains GP and Flex. Flags read by hand: General Dynamics opens with "Second Quarter
  2026" but names "first quarter" more often in the first 6,000 characters (rule's false
  alarm); Apple's flagged date is the quarter end ("quarter ended June 27, 2026"), not the
  call. Modine and Flex, both empty, are the two whose fiscal-year label runs ahead of the
  calendar year. Fixed forward in EXP-0041.
- **EXP-0041** — S2-a Alpha Vantage collection, fix forward of EXP-0040 (same scope, targets,
  ledger and daily limit; output in `s2/exp0040/`). Changes, written after EXP-0040's 20
  requests and before any further one: (1) a request sent in this run is not sent again, and
  the run pauses after the validation stage; (2) for an episode whose fiscal-year label runs
  ahead of the calendar year of its quarter end (nine episodes, e.g. Modine 2027Q1 for the
  quarter ending June 2026) and whose fiscal-label request came back empty, one more request
  with the calendar year of the quarter end and the fiscal quarter number (Modine 2026Q1);
  Modine and Flex are asked first, and if both come back empty no other episode is retried;
  a retry counts only if its quarter check and name check pass; (3) the quarter check reads
  the first quarter named in the first 600 characters (the operator's or host's opening line)
  and falls back to EXP-0040's most-frequent rule only when the opening names none; both
  results are reported. Duplicate requests are counted once in the results.
  **Run 2026-11-22 (US Eastern), 5 requests (25 that day with EXP-0040's 20):** both retries
  returned a transcript and passed the quarter-number check, but read by hand both are the
  wrong year: "Modine's First Quarter Fiscal 2026" and "Flex's First Quarter Fiscal 2026" are
  the calls on the quarters ending June 2025; the episodes need fiscal 2027's first quarter.
  Modine's retry shares 0.03 of its 8-grams with Modine's 2026 IR transcript (same-call bar
  0.5). The check had no year test, so the retry rule would have let a year-old call in. Both
  retries are void; Alpha Vantage labels these companies by their own fiscal year, and its
  empty reply means it has not got the call. Also McDonald's (full transcript) was flagged
  "name missing" because "McDonald's" carries an apostrophe the name test did not strip. The
  other three requests: McDonald's and Global Partners full, Freddie Mac empty. Fixed forward
  in EXP-0042.
- **EXP-0042** — S2-a Alpha Vantage collection, second fix forward (same scope, targets, ledger,
  limit and folder as EXP-0040; written after EXP-0041's run and before any further request).
  (1) No retry with another quarter label for any episode; EXP-0041's two retries are void.
  (2) A year test joins the quarter test: the first year printed in the first 600 characters
  must equal the fiscal year asked for (`fy`); if the opening prints no year, the year printed
  most often in the first 6,000 characters is used; a transcript is usable only if company,
  quarter and year all pass and it is full. (3) The name test strips apostrophes from both the
  name and the text. Everything else as in EXP-0041 (no request sent twice; the opening line
  read first for the quarter).
  **Check of the first day's replies, 2026-11-23 (before any EXP-0042 request):** 22 of 187
  distinct requests made; 16 full transcripts, 15 usable by every test (16 episodes, all among
  the 250 largest; Tesla's two releases share one call); 6 empty (Modine and Flex, both
  fiscal-ahead; Energy Transfer, SUNC, Plains GP, Freddie Mac). Stride fails only the year test
  (its opening prints no year and the fallback picks 2018), but shares 0.60 of its 8-grams with
  Stride's 2026 IR transcript, so it is the right call; it has the IR text either way. With
  EXP-0039's IR transcripts, 53 of 197 clean episodes now have call text (33 among the 250
  largest). Of the 19 companies without IR text asked so far, 14 have a full transcript.
- **EXP-0043** — S2-a Alpha Vantage collection, scope widened (owner, 2026-11-23: "都好的", to
  the questions on the 60 old episodes and the October and November 2026 calls, and to a daily
  scheduled run). One self-contained script replaces EXP-0042's fetch and check; same ledger,
  limit (25 a US Eastern day), folder and tests as EXP-0042 (full; company; quarter from the
  opening line; fiscal year; no retry under another label; no request sent twice). Targets in
  `targets_all.jsonl`, asked in this order: (1) EXP-0040's 197 clean rows, unchanged; (2)
  "next": for each clean company with a ticker, the following fiscal quarter (Q4 rolls to Q1
  of the next fiscal year), where its next earnings release (quarter end 60 to 120 days after
  the clean one) is already in EXP-0020's release list, filed by 2026-11-11 (183 of 187); the
  other four wait for the December submissions snapshot; by revenue rank; dated by that
  release; (3) "old": EXP-0036's 60 old episodes (2019 to 2025), fiscal labels from the company
  facts as in EXP-0040, current tickers, by rank (one has no ticker). `targets` run 2026-11-23:
  429 distinct requests in all, 407 still to make, finished around 2026-12-09. The "next" calls feed the prospective arm, whose forecasts are sealed before each
  company's following release (pre-registered separately, with EXP-0001); the "old" calls are
  pre-cutoff and contaminated by definition. Training and development companies only. One
  change to the tests, from EXP-0042's Stride case: a full Alpha Vantage text that passes the
  same-call test against the company's IR transcript counts as usable even when the year test
  fails, since the IR file names and dates the call. **Run 2026-11-23 05:40 UTC:** the first
  request was refused with Alpha Vantage's limit message, though US Eastern midnight had
  passed: its day is not the Eastern day (the 25 requests of 2026-11-22 Eastern were sent
  04:30 to 04:40 UTC, so its count runs by Pacific day, UTC day or a rolling 24 hours). The
  limit message quotes the key, and the script wrote it into the drive ledger; that line was
  redacted by hand the same minute. Fixed forward in EXP-0044.
- **EXP-0044** — S2-a Alpha Vantage collection, third fix forward (EXP-0043 unchanged in
  scope, order and tests). `fetch` runs EXP-0043's fetch and then replaces any occurrence of
  the key in the ledger with "***"; before it starts it does the same, so nothing the server
  echoes stays in a log. The daily run is a scheduled task at 16:20 local time (UTC+8, 08:20
  UTC): after Pacific midnight and 24 hours from the previous run, so it fits a Pacific day, a
  UTC day or a rolling window; a refusal stops the run and costs one ledger line.
  **2026-11-23 13:40 UTC:** a run by hand was refused again, after Pacific midnight: Alpha
  Vantage counts by UTC day or a rolling 24 hours, both of which the 08:20 UTC run fits. The
  scrub removed the key the refusal quoted. The scheduled run of 08:27 UTC the same day sent no
  request: it stopped on Claude Code's permission prompt; the two commands are now allowed in
  the project's local settings (not in git).
- **EXP-0045** — S2-a call texts in one form (engineering; no model, no network). For every
  EXP-0043 target with call text (clean, next and old stages), one document: Alpha Vantage's
  text where it passed EXP-0043's tests, else EXP-0039's IR transcript (clean stage only), else
  EXP-0039's prepared remarks, CFO commentary or letter, marked partial. Alpha Vantage turns are
  rendered as "[name, title]: text" without its sentiment scores; the questions-and-answers part
  starts at the operator turn before the first turn whose title names an analyst. IR text loses
  lines of vendor boilerplate (copyright, page numbers, vendor headers) and a closing disclaimer;
  its questions-and-answers part starts at a section heading ("Question and Answer", "Questions
  and Answers") or else at the operator's first-question line. Each document records its source,
  whether it is partial, the length of each part and a token estimate (characters / 4).
  `check` counts documents by stage and source, the share with a question-and-answers part,
  boilerplate left over, and prints ten documents' openings drawn by seed 20261126 for a hand
  check. Rebuilt as collection goes on. Whether raw call text reaches the PM is decided per
  experiment: skill v1 Part D gives none on replayed (old) history. Output `s2/exp0045/`, drive
  only (rule 12).
  Development builds, 2026-11-23 (the first three on the drive, superseded): IR files that came
  out of the PDF as a few lines of thousands of characters lost whole lines to the boilerplate
  rule (Omnicom and LCI emptied); fixed by removing the phrases inside lines over 300 characters.
  Also added before the record build: NFKC (ligatures), spaced headings ("Q U E S T I O N S"),
  four more phrases that open the Q&A searched after the first 15% of the text, and a fallback
  for files that hold the Q&A session only (Hershey, Snap). Record build the same day: 58
  documents for clean episodes (18 Alpha Vantage, 35 IR transcripts, 5 partial); every full
  transcript has a Q&A part; no boilerplate left; median 13,300 tokens, largest 26,100.
- **EXP-0046** — S2-a fix forward of EXP-0043's next-quarter targets. EXP-0043's code took the
  release whose quarter ended 60 to 120 days *before* the clean quarter (the arguments of
  `exp0005.days` reversed), so its 183 "next" rows carry the April-to-June 2026 releases'
  dates, accessions and quarter ends; their Alpha Vantage labels (the following fiscal
  quarter) were right. Found before any next-stage request. This script rewrites
  `targets_all.jsonl` with the next rows rebuilt the intended way (quarter end 60 to 120 days
  after; 184 of 187, missing MWH, ARXS, BAM), keeps the clean and old rows and their order, and
  saves EXP-0043's file as `targets_all_exp0043.jsonl`. EXP-0044's daily fetch reads the
  rewritten file.
- **EXP-0049** — S2-a December company-facts snapshot and series (approved by the owner
  2026-11-20 with decision 4 of the S2 plan, "同意1 和2"). `fetch` downloads SEC's bulk
  `companyfacts.zip` (about 1.3 GiB) to `edgar/xbrl/companyfacts-<date>.zip` with the contact
  string from `EDGAR_IDENTITY`, in early December, and records its size and SHA-256. `series`
  rebuilds EXP-0020's quarterly series (same code, first filing of each quarter, training and
  development companies only) from it into `s2/exp0049/series.jsonl`. `compare` counts, for
  EXP-0048's episodes, how many September quarters the new series has that the November one
  lacked, and lists any quarter whose first-filed values differ between the two (they should
  not). Not needed for EXP-0048's build (the November series already has all 180 September
  quarters); kept for label coverage of smaller filers and the later December-quarter labels.
  No model; an engineering step with no hypothesis.
- **EXP-0060 to EXP-0069** — held for sub-study S2 (2026-11-24; EXP-0050 to 0059 are S1's).
- **EXP-0060** — S2-a name test v2 for the Alpha Vantage replies (fix forward of EXP-0042's test,
  used by EXP-0043/0044's `check`). The 2026-11-23 batch flagged two right transcripts as
  "name missing": Fidelity National Financial, whose call opens "welcome to FNF's Second
  Quarter" (EXP-0042 strips apostrophes, so "FNF's" became "fnfs"), and Westinghouse Air
  Brake, whose call says "Wabtec". The name test now passes if the name word or a ticker
  appears in the first 5,000 characters of either the apostrophe-stripped text or the text with
  possessive 's removed, or if an alias from `s2/exp0060/aliases.json` does; an alias is added
  only after the opening line is read by hand, and the file keeps that line beside it. Everything
  else is EXP-0043's check. `check` writes `s2/exp0040/checked_v4.jsonl`; `calls` runs
  EXP-0045's build on it (same output folder). The daily fetch is unchanged.
- **EXP-0052** — S1 pull of the training companies' earnings releases, 2019 to the cutoff, for the
  re-plan's data factory (`research/design/s1_finance_distillation_replan.md` §4.1; owner,
  2026-11-26, decision 2: "全案推荐来"). `exp0052_s1f_release_pull.py`. An engineering step with no
  hypothesis and no model. Targets: 8-Ks with Item 2.02 in the bulk submissions archive
  (2026-11-12; recent and overflow files), filed on or after 2019-01-01 and accepted on or before
  2026-06-30, of companies on the split v1 "train" side under both EXP-0005's group map and one
  rebuilt from every earnings 8-K in the archive; one copy per accession. The press release is
  chosen as EXP-0003 chose it and parsed to text with edgartools; at most 4 requests a second,
  identity from `EDGAR_IDENTITY`. XBRL company facts are already on the drive and not pulled.
  Targets (2026-11-26): 40,266 releases from 1,862 companies, 5,076 to 5,741 a year for 2019 to
  2025 and 2,529 for 2026. The design's "at least 30,301" counted recent files only; overflow
  files and companies that no longer file add the rest. Texts go to `edgar/releases_train/`
  (outside git), the log and counts to `s1/exp0052/`. Fetch started 2026-11-26 13:39, about
  1.4 releases a second.
- **EXP-0053** — S1 section R v1 builder, the re-plan's "R test builder fix" (re-plan §4.3,
  approved 2026-11-26). `exp0053_s1r_build_v1.py`. An engineering step with no hypothesis and no
  model: EXP-0019's builder, imported unchanged, with two changes. (1) The escape clause, on every
  template: v0 "If the excerpt does not give enough information to answer, answer
  \boxed{cannot be determined}." becomes "If the answer can neither be read from the excerpt nor
  worked out from its figures, answer \boxed{cannot be determined}." EXP-0050's verdict floated
  dropping the clause from R1.7 alone; that would make the clause's presence a cue for R1.9's
  gold, so the wording changes everywhere instead. (2) R1.8 keeps an item only if the margin is
  within ±100% in both years. Ids hash "Rv1|…", so no v1 id equals a v0 id. Output
  `s1/exam_r_v1/`. Claude reads train and development items only; test counts only.
  Train and development built 2026-11-26 (checks pass). Only R1.8 changes: train 527 → 487
  base items (44 dropped by the margin rule), development 594 → 545 (56 dropped); every other
  template's count and label mix equals v0's. Read: one development R1.7 and one R1.8 item, new
  clause in place. Test side not built yet. Validity probe planned before the test side is used (in the main experiment's
  pre-registration): the 4I and the released 0.8B on development R1.7 and R1.9 v1 items, to see
  that R1.7 leaves the floor and R1.9 does not fall.
- **EXP-0054** — S1 data factory step 1: verified fact sheets of EXP-0052's releases.
  `exp0054_s1f_sheets.py`. An engineering step with no hypothesis and no model. Section R v1's
  builder (EXP-0053) is run over each training-company release with text, so every figure in a
  sheet passed the two-source rule (a labelled table row at XBRL's first-filed value, prior year
  in the same row at XBRL's prior-year value). A sheet keeps the period, the verified figures with
  their rows and columns, and the gold, steps and needed rows of each R template the builder
  could make; no question text and no excerpt, so the factory's own questions do not reuse R's
  wording. Runs on the releases fetched so far and again with `--resume` once EXP-0052 is done.
  Output `s1/exp0054/` (outside git). First run 2026-11-26 on the 6,872 releases fetched by
  then (234 companies; texts are fetched in company order): 5,068 with at least one verified
  figure, 3,718 with at least one R-template item; about 24 releases a second.
- **EXP-0055** — S1 data factory step 2: varied training items from EXP-0054's sheets.
  `exp0055_s1f_items.py`. An engineering step with no hypothesis and no model; every item is a
  training company's before the cutoff, so Claude reads them. Diluted EPS and income before
  taxes appear in no item (R1.4 and R1.5 held out, the re-plan's example; the main
  pre-registration may change this, which would mean a new script). Twelve kinds under fixed
  quotas (extract, growth, margin level, margin change, margin direction, co-movement, faster or
  slower, true-or-false claim, biggest or smallest mover, derived period, cannot be determined,
  whole-release condition table), golds by section R's rules over more line items and pairs.
  Eight lead-ins, four comparison phrases, line names including the release's own row label
  (not one containing "margin"), four option sets, four escape clauses (R's own not among them,
  nor R's lead-ins) and four answer formats (\boxed{} 40%, "Answer:" line 25%, JSON 20%, one
  sentence 15% for label items). Pool of 30,000, ranked, at most three items per release and
  30 per company. Trial of 3,000 on the first run's sheets (2026-11-26): every quota filled,
  189 companies, 2,639 distinct phrasing skeletons; about 20 items read, golds right after three
  fixes (literal doubled braces in two format lines, a row labelled "Gross margin" used as the
  name of gross profit, one ungrammatical question). The full pool waits for EXP-0052.
- **EXP-0056** — S1 data factory step 3: teacher chains over EXP-0055's pool, verified by rule.
  `exp0056_s1f_chains.py`. `check` (no model) passes 15 grading and arithmetic cases. A chain
  is kept only if it finished, its final answer read in the item's format is right, every
  calculation EXP-0018's inline rule finds shows the value the calculator computes (to the
  precision written; a ratio may be written as a percentage), and each needed row has its
  current or prior-year figure quoted; up to two distinct chains per item. Proposed teacher for
  the main pre-registration: the released 4B without the calculator, sampled in batches,
  thinking off, after a short procedure instruction the student never sees (EXP-0050: 4B 82.0
  and 4I 82.2 on R plain; batching needs uninterrupted decoding, so arithmetic is checked
  afterwards rather than during decoding). Before the pre-registration: `speed` (16 pool items
  at batch 1, 8 and 16) and a pilot `generate` of 200 items × 4 samples on the trial pool, to
  `s1/exp0056/pilot/`, for throughput and the keep rate by kind. Engineering only, training
  items only; neither output is used for training.
  Speed (2026-11-26, 16 items, cap 768): batch 1 348 samples an hour (51.4 tokens/s, 3.3 GiB),
  batch 8 837 (136.6, 6.6 GiB), batch 16 1,074 (166.5, 7.2 GiB; one batch only). Pilot
  (17:49 to 18:45, batch 8): 800 samples, 564 generated tokens each on average; 416 samples
  (52%) pass all four checks; 169 of 200 items (85%) have a kept chain, 293 chains kept. One
  fix after reading failures: the arithmetic check rejected the 4B's drift in the fifth or sixth
  significant digit of long divisions (1017/6659 written 0.152724) and read dates (3/21/2020) as
  divisions; it now allows 0.01% and skips date-shaped expressions (19 cases pass; the
  remaining rejections read were real, e.g. −5.29% for −5.31%). About 15 failed answers read:
  teacher errors (the year-ago column taken for the previous quarter, the JSON format ignored,
  another row's figure); one suspicious gold (cost of revenue +167.7%) checked against the
  release and right (the year-ago quarter predates a merger). Pass rate by kind: margin level
  77%, mover 69%, margin direction 65%, claim 63%, faster or slower 56%, extract 54%, margin
  change 51%, growth 50%, cannot be determined 47%, co-movement 46%, derived 18%, table 3%. The
  last two, and a third of extract and cannot-be-determined samples, mostly run out of the 768
  tokens (table 34 of 36 samples): the procedure instruction makes the 4B work through every
  figure. Prompt plus chain is about 1,300 tokens, against 512 in EXP-0014 and EXP-0017; see the
  main pre-registration for the sequence budget.
- **EXP-0057** — S1 validity probe of section R v1's escape clause, development items only.
  `exp0057_s1r_v1_probe.py`. Descriptive with a decision rule, so pushed before it runs (as
  EXP-0051). The v1 counterparts of EXP-0050's 50 R1.7 and 50 R1.9 development base items (all
  100 matched; excerpts identical; 22 R1.7 items ask in thousands where v0 asked in millions
  or the reverse, because R1.7 draws the unit at random and R1.8's drops moved the draw order)
  with EXP-0050's prompt, cap, grader and arms 4B, 4I and B0. Rule: the wording is kept if the
  better of 4B and 4I reaches at least 50 on R1.7 (10 in EXP-0050) and neither falls by more than
  10 points on R1.9 against its EXP-0050 score on the same items; otherwise a new builder
  rewords it before any test item is built. About 35 minutes. Not yet run.
- **EXP-0058** — S1 full fine-tuning speed and memory of the 0.8B at 640, 768 and 896 tokens.
  `exp0058_s1f_sft_speed.py`. An engineering step with no hypothesis: EXP-0014's setup exactly
  (every block trained, embeddings frozen, AdamW 1e-5 with warm-up, batch 1, gradient
  checkpointing, prompt masked), 40 steps a length on EXP-0056's pilot chains cut or repeated to
  the target length, the first 10 steps dropped; stops at a length whose peak passes 12 GiB. The
  feasibility probe had only 512 and 1,024 tokens (7.17 and 14.45 GiB, 6.24 and 16.98 s a
  step). Run 2026-11-26 after the pilot: 640 tokens 8.90 s a step (about 405 sequences an
  hour), 8.69 GiB; 768 tokens 13.76 s (about 262 an hour), 10.43 GiB; 896 tokens passed 12 GiB
  (12.30) at step 5 and stopped. So a training sequence must stay at or under about 768 tokens
  in the 12 GiB budget, and at 640 it costs 1.4 times a 512-token step.

## Entries

## EXP-0051 — S1 re-plan diagnostics: weight averaging and the 0.8B's sampling ceiling (2026-11-26)

### PRE-REGISTRATION
- **Status:** draft, 2026-11-26. Asked for by the owner on 2026-11-26 ("全案推荐来": decision 4 of
  `research/design/s1_finance_distillation_replan.md` §5, run the two diagnostics now). Before
  the commit: the script is written (`exp0051_s1f_diagnostics.py`) and `check` passes. Averaging
  at a = 0 equals the released 0.8B and at a = 1 equals K2, tensor by tensor (maximum difference 0).
  At a = 1 it reproduces K2's EXP-0050 response on the first R item and EXP-0017's on the first B
  item. One batch of 8 samples takes 9.4 seconds at 6.1 GiB and is reproduced by its seed. No
  other item has been run. Approved by the owner 2026-11-26 ("a": commit, push, run).
- **Claim under test:** descriptive, not a hypothesis (re-plan §4.4). Two questions that set the
  main experiment's arms before it is pre-registered:
  1. Is the format lock of C and K2 (EXP-0050: a number boxed on label items, R under 1) cheap to
     repair by averaging their weights with the released model, without losing what they learned
     on B?
  2. How much better than its greedy answer does the released 0.8B get when sampled? On-policy
     distillation at 0.6B stays below the starting student's pass@n in all 27 settings of Li et
     al. 2026 (`research/literature/papers/li-2026-on-policy-distillation-small-scale.md`), so this
     bounds what F3 can add without off-policy data.
- **Why the answer is not obvious:** averaging is the best forgetting trade-off among the methods
  compared at 3B (stream 14b §2), but C and K2 were fully fine-tuned and their R failure is a
  learned output format, which may survive at any a that keeps their B gain. Sampling may only
  add guessing on label items, which is why the ceiling is read on the open templates.
- **Sample and scope, fixed here:**
  1. **Items.** EXP-0050's 450 plain development R base items (draw hash
     `4e7f3b2f…6258`) and EXP-0007's 600 B development items (v0.2). No twin, hint, test or new
     item.
  2. **Diagnostic 1, averaged arms**, in this order: K2 at a = 0.25, 0.5, 0.75 and C at a = 0.5,
     with W = (1 − a)·W_base + a·W_trained over every tensor in the checkpoint (EXP-0014's D3-s1
     and EXP-0017's K2-s1, the chosen epochs), computed in float32 and stored in the checkpoint's
     dtype. On R exactly as C and K2 in EXP-0050 (terse instruction with "final answer", inline
     calculator, 512 tokens, forced answer, greedy). On B exactly as C and K2 on B (terse
     instruction, inline calculator, 160 tokens, forced answer, greedy).
  3. **Diagnostic 2, samples.** The released 0.8B as B0 in EXP-0050 (standard instruction with
     "final answer", no tool, 512 tokens, forced answer greedy), 8 samples per R base item at
     temperature 0.7 and top-p 0.95 (EXP-0014's sampling), seed 20261126 plus the item's index,
     one batch of 8 per item (`mlx_lm.batch_generate`). 3,600 responses.
  4. **References already on disk:** B0, C, K2 and 4I plain R responses (EXP-0050); B0, C and K2
     B responses (EXP-0011, EXP-0016, EXP-0017). Their scores: R 55.9, 0.9, 0.7, 82.2; B 57.2,
     87.5, 89.3.
- **Method and grading:** EXP-0050's `grade_r` and R score (the mean over templates of balanced
  accuracy for labels, accuracy otherwise); B by `exp0010.grade`. 95% intervals by company
  bootstrap, 10,000 resamples, seed 20261124 (EXP-0050's), shared by every arm so differences are
  paired. For samples: per item, the share of the 8 that are right; pass@8 (any right); maj@8
  (the most frequent answer, ties to the earliest sample), each put through the same R score.
  For label templates the chance pass@8, 1 − (1 − 1/m)^8, is shown beside it.
- **Decision rules** (not hypothesis tests):
  1. **Repair.** An averaged arm repairs the lock if its R score is at least B0's minus 5 points
     and its B accuracy at least its source checkpoint's minus 3 points. If any arm does, "+avg"
     is a full arm of the main experiment (tested with the others), and the general and B items
     mixed into F1 to F3 are set at 10%. If none does, "+avg" is reported on development only, and
     the mix is set at 20%.
  2. **Room for on-policy.** On the open templates (R1.7, R1.8, R1.9: a number or "cannot be
     determined", no options to guess), let room = B0's pass@8 − B0's greedy score. If room is at
     least 10 points, F3 stays in the plan as designed and F2's checkpoint gets the same check
     before F3 starts. If it is below 10, F3 is the first arm cut (it already is) and the owner is
     told that this evidence points against it before any on-policy code is written.
- **Also reported, descriptive:** each arm by template; the share of label items whose box holds a
  number; forced rates and generated tokens; for samples, mean@8 and maj@8 against greedy for
  every template and B0's pass@8 on the open templates against 4I's greedy score there; seconds
  per batch (the data factory's speed estimate). Claude reads development responses to explain
  the numbers.
- **Contamination label of the result:** clean. Development companies, releases accepted after
  2026-06-30; the released checkpoint predates that date, C and K2 were trained only on
  pre-cutoff releases of training companies; no model labels any item.
- **Not in scope:** test items, twins, hints, other values of a, averaging the 4B, a second seed,
  thinking on, any training.
- **Estimated compute:** averaged arms at most B0's 4.3 seconds an R item and about 1 second a B
  item: at most 45 minutes each, 3 hours for four; samples about 10 seconds a batch, 1.3 hours.
  About 4 to 4.5 hours, one MLX job. EXP-0052's network pull runs beside it and uses no MLX.

### VERDICT
- **Pre-registration commit:** `e6fd926` (pushed before any arm ran). Run 2026-11-26 15:32 to
  17:43 by `queue`, every arm complete (450 R and 600 B responses each; 3,600 samples). 2.2 hours
  against 4 to 4.5 estimated: averaged arms about 15 minutes each, samples 8.34 seconds a batch
  of 8. Output: `s1/exp0051/scores.json`.
- **Result, averaging** (R: mean over the nine templates, development base items, plain; B:
  accuracy on the 600 B development items; 95% intervals, company bootstrap as EXP-0050; the
  averaged arms run as C and K2 ran in EXP-0050, terse prompt and inline calculator):

  | Arm | R | R − B0 | B | B − source | Label items boxing a number |
  |---|---|---|---|---|---|
  | B0: 0.8B as released | 55.9 [51.5, 60.2] | — | 57.2 | — | 0% |
  | K2 (a = 1, EXP-0050) | 0.7 | −55.2 | 89.3 | — | 100% |
  | K2@0.75 | 2.7 [1.3, 4.3] | −53.2 [−57.8, −48.3] | 90.5 | +1.2 [−0.5, +2.8] | 91.7% |
  | K2@0.5 | 25.9 [22.1, 30.1] | −30.0 [−35.8, −23.7] | 85.0 | −4.3 [−7.1, −1.7] | 15.0% |
  | K2@0.25 | 25.8 [22.0, 29.7] | −30.1 [−35.7, −24.3] | 74.2 | −15.2 [−19.1, −11.4] | 0% |
  | C@0.5 | 22.6 [19.4, 25.8] | −33.3 [−38.6, −28.0] | 83.5 | −4.0 [−6.4, −1.7] | 34.0% |

  By template (K2@0.25 / K2@0.5 / C@0.5): R1.1 50.2 / 29.8 / 27.9; R1.2 26.8 / 19.6 / 13.5;
  R1.3 26 / 52 / 40; R1.4 38 / 48 / 44; R1.5 28 / 52 / 48; R1.6 43.2 / 12.1 / 0; R1.7 2 / 6 / 6;
  R1.8 18 / 14 / 24; R1.9 0 / 0 / 0.
- **Result, sampling B0** (8 samples an item at temperature 0.7, top-p 0.95; greedy = EXP-0050's
  plain run): open templates (R1.7, R1.8, R1.9) greedy 42.0, pass@8 62.0 [57.8, 65.9], 4I's
  greedy 65.3. By template, greedy / mean@8 / maj@8 / pass@8 (4I): R1.7 2 / 1 / 0 / 4 (10); R1.8
  56 / 32.5 / 46 / 82 (88); R1.9 68 / 68.2 / 96 / 100 (98). On the label templates pass@8 is 92 to
  100, at or under chance pass@8 (90 to 99.6), so it says nothing there, as expected. Over all
  templates: greedy 55.9, mean@8 47.3, maj@8 59.0. 30.6% of samples reached 512 tokens without a
  box and took the forced answer; 404 generated tokens a sample on average.
- **Decision rules:**
  1. **Repair: no arm repairs.** The best R score of an averaged arm is 25.9 (K2@0.5), 30 points
     under B0 (the rule asks for at most 5), and the one arm that holds B (K2@0.75, +1.2) keeps
     the lock (R 2.7). So "+avg" is reported on development only, and the general and B items
     mixed into F1 to F3 are set at 20%.
  2. **Room for on-policy: 20 points, so F3 stays.** pass@8 − greedy on the open templates =
     62.0 − 42.0 = 20.0 (at least 10). F2's checkpoint gets the same check before F3 starts. The
     room is below the teacher (62.0 against 65.3) and lies on R1.8 and R1.9; R1.7 has none (4
     against 2), which is the wording problem EXP-0057 probes.
- **Also reported, read from development responses:**
  1. **Averaging brings back the label words, not the reasoning.** On R1.9 every averaged arm
     boxes a figure from a nearby row in K2's "Row; Column; Calculation" layout and never answers
     "cannot be determined" (0 of 50 each). On label items the box holds a label word again (0 to
     34% numbers, against 97 to 100% for C and K2), but mostly the same one: K2@0.5 boxes
     "expanded" on 30 of 50 R1.1 items. Between a = 0.25 and 0.5 the R score does not move (25.8,
     25.9) while B gains 11 points; above 0.5 R collapses. Averaging trades B for R along one line
     rather than undoing format specialisation.
  2. **B0's errors on R1.9 are unstable.** Majority over 8 samples lifts R1.9 from 68 to 96: the
     released 0.8B usually knows when a figure is absent but does not say so every time.
  3. **Sampling at 0.7 costs accuracy** (mean@8 47.3 against greedy 55.9), and 30.6% of samples
     run out of tokens, so on-policy rounds need a longer cap or a terser student prompt.
- **Not established:** the comparison with B0 mixes weights and prompt (averaged arms used the
  terse prompt, B0 the standard one), as registered; no averaged arm was run with B0's prompt.
  One seed of each source checkpoint.
- **Contamination label:** clean.
- **Consequences:** the main pre-registration mixes 20% general and B items into F1 to F3, keeps
  F3 (subject to F2's own check) and reports "+avg" on development only. No general instruction
  data is on disk; its source is a choice for that pre-registration.

## EXP-0050 — S1 reasoning exam, step R-b: headroom on development section R items (2026-11-24)

### PRE-REGISTRATION
- **Status:** draft, 2026-11-24. The owner asked for R-b's pre-registration after EXP-0019 was
  committed ("A"). Before the commit: the script is written (`exp0050_s1r_headroom.py`), its
  checks pass (15 grader cases, 6 figure-matching cases, and EXP-0018's 22 parser cases), the draw
  is made (ids only, no model run), and `score` was dry-run on synthetic responses in a scratch
  folder. No model is run before the owner approves and the commit is pushed. Approved by the
  owner 2026-11-24 ("A": approve, commit, push, run).
- **Claim under test:** descriptive, not a hypothesis (design §6, step R-b). On development items
  of section R: how far the distilled 0.8B is behind the 4B when the task needs several facts and
  a rule rather than one lookup or one calculation; whether a one-line hint closes that distance;
  how each model handles the twins; whether any template's gold looks wrong; and how large R-c's
  test must be. R-c's hypotheses are written from this run.
- **Why the answer is not obvious:**
  - On B development items the gap is small: 4I − K2 = 1.5 points (90.8 against 89.3, the
    responses already on disk). R items need two to six figures, and the 0.8B's main B error is
    reading the wrong column, which R makes it do several times per item.
  - The distilled 0.8B arms were trained to box one number. R mostly asks for a label, so C and
    K2 may lose to format rather than to reasoning; the untrained 0.8B (B0) shows that cost.
  - Hints may help the small model most, or not at all (design §7).
  - The 4B itself may be weak on some templates. That is either a gold problem or a ceiling for
    R-d's teacher, and only reading answers tells which.
- **Sample and scope, fixed here before looking:**
  1. **Items.** Section R v0 development items (EXP-0019, `exam_r_v0/items_dev.jsonl`) from
     releases accepted after 2026-06-30 (3,017 base items). Question phrasing p1 only (as B's
     development items); p2 is kept for R-c.
  2. **Draw.** 50 base items per template, nine templates. Items are ordered by SHA-256 of
     `"exp0050:" + id` and taken in round robin over the gold label (label templates) or the
     variant (R1.7, R1.8, R1.9), so labels are as balanced as the pool allows. An item is
     skipped if its company already has 2 items of the template or its release already has one.
     Result (made 2026-11-24, no model run): 450 base items from 202 companies, every template 50,
     40 to 48 companies each; R1.6 has 7 R&D golds (all the pool allows after the caps). SHA-256 of
     the base ids in draw order `4e7f3b2fe9e12ef38135cfac7cdcedf9279b0023078a6d5115a247ffbb916258`.
  3. **Conditions.** *plain*: the 450 base items. *hint*: the 400 base items of R1.1 to R1.8, with
     `Hint: <the template's hint>` after the question (R1.9 has none). *twin*: every twin of the
     base items, no hint: 237 flip, 450 hold, 150 mirror; SHA-256 of their ids
     `43c233e4b245dee036acfb3265b1216f93a44e35165d7cb41aa2f49e0d7661e2`. 1,687 responses per arm.
- **Method and baseline:**
  1. **Arms**, the S1 checkpoints already on the drive, no download:
     - **4B**: Qwen3.5-4B (4-bit, EXP-0014's revision), no tool;
     - **4I**: the 4B with EXP-0018's calculator, inline rule only;
     - **B0**: Qwen3.5-0.8B as released, no tool;
     - **C**: EXP-0014's D3-s1 (its chosen epoch) with the calculator, inline rule only;
     - **K2**: EXP-0017's K2-s1 (its chosen epoch) with the calculator, inline rule only.
     One seed per distilled arm. The chained rule is off for every arm (it never fired for the
     0.8B; EXP-0018).
  2. **Prompts.** The arm's own instruction from B, with "final number" changed to "final answer":
     4B, 4I and B0 `Reason briefly, then give the final answer in \boxed{}.`; C and K2 the terse
     instruction with the same change. No other change.
  3. **Decoding.** Thinking off, greedy, at most 512 generated tokens for every arm (inserted
     values free), then EXP-0007's forced answer if no box was written. One MLX job, within
     12 GiB. Run order B0, C, K2, 4B, 4I; within an arm plain, hint, twin.
  4. **Grading** by rule (`grade_r`). Labels: the last box, normalised (LaTeX text commands,
     case and punctuation removed), must equal one option, or contain exactly one option as a
     phrase; anything else is invalid and wrong. "cannot be determined" anywhere in the box is that
     answer. Numbers: EXP-0010's `read_number` and the item's tolerance.
  5. **Score.** Per template: balanced accuracy (the mean of the per-label accuracies) for label
     templates, accuracy for R1.7, R1.8 and R1.9. The R score is the mean over templates. Raw
     accuracy is reported beside it.
  6. **Baselines.** Chance (one over the number of options; a constant answer scores the same
     balanced accuracy) and the majority class, per label template. Code on XBRL scores 100 by
     construction.
  7. **Intervals.** 95%, bootstrap over companies, 10,000 resamples, seed 20261124. Every arm and
     both sections share the same resamples, so differences are paired.
  8. **B reference.** Each arm's responses on the 600 B development items, already on disk, graded
     by `exp0010.grade`: 4B and B0 from EXP-0011, 4I from EXP-0016's run made before the chained
     rule existed, C from the same EXP-0016 run, K2 from EXP-0017's development run of its chosen
     epoch. Their caps were B's (160 tokens for C and K2, 256 for B0, 512 for the 4B).
- **Criteria** (decision rules, not hypothesis tests):
  1. **R-d gate.** R-d (distillation on R) is put to the owner only if 4I − K2 on the plain R
     score is at least 5.0 points and the 95% interval lies above 0. Otherwise it is not proposed,
     and R-c is run as the main result.
  2. **Item validity.** A template is flagged if the better of 4B and 4I scores below 60 on it,
     or if more than 20% of its base items are wrong for all five arms. Claude reads up to 10 such
     items per flagged template, with their responses, and sorts them into wrong gold, ambiguous
     question, or model error. A template with a wrong gold is fixed forward by a new builder
     before R-c and stays out of R-c until then.
  3. **Ceiling and floor** (S1 plan §3, rule 7). A template on which a model scores above 95 or
     below 20 is dropped from that model's contrasts in R-c.
  4. **R against B.** For 4I − K2, 4I − C and 4B − B0: the gap on R (plain), the gap on B, and
     their difference, with intervals. Descriptive; it sets R-c's hypothesis and its margin. The R
     score is balanced and B's is plain accuracy, so the raw-accuracy gap on R is shown too.
  5. **R-c size.** For 4I − K2 and 4I − C: d, the share of plain base items on which the two
     disagree on correctness, and DE, the company-bootstrap variance of the paired difference over
     its independent variance. n = DE × (z(1 − 0.0125/2) + z(0.80))² × d / 0.03². The larger n is
     R-c's number of base test items. If it is above 3,000, the owner decides before R-c is
     pre-registered (the 4B arms cost about 7 seconds an item).
- **Also reported, descriptive:**
  - every arm by template and condition; the hint gain (hint − plain, R1.1 to R1.8) with
    intervals;
  - twins: accuracy on each kind; on flip twins, the share answered right when the base was
    right; on hold twins, the share with the same answer as the base; on mirror twins, the
    contradiction rate (the same label for both questions);
  - step accuracy on plain base items: the share of the step chain's figures that appear in the
    response (as shown, or divided or multiplied by 1,000), and right answers written with
    figures missing;
  - forced and invalid rates, the share of responses with a calculator call, generated tokens,
    and the share of responses longer than 160 tokens (the distilled arms' B cap);
  - seconds per item, hours, peak memory.
  Claude reads development responses (all of them are development) to explain the gaps.
- **Contamination label of the result:** clean. Development companies, releases accepted after
  2026-06-30; the released checkpoints predate that date, and the distilled ones were trained
  only on pre-cutoff releases of training companies; no model labels any item.
- **Not in scope:** test items (R-c); the p2 phrasing; a second seed of C and K2; thinking on;
  a code baseline that reads the release text through the B parser (deferred to R-c, where it is
  reported beside the models); section A; any training.
- **Estimated compute:** from B development timings (4B 4.7 s an item at 465 prompt tokens, B0
  2.7 s, C and K2 0.7 s) scaled to R's longer excerpts: 4B and 4I about 3.3 hours each, B0 about
  1.6 hours, C and K2 about half an hour each. About 9 hours in all.

### VERDICT
- **Pre-registration commit:** `43cb4f5` (pushed before any arm ran). Run 2026-11-24 18:00 to
  2026-11-25 04:10 by `queue`, every arm complete (1,687 responses each). 10.1 hours of
  generation, against 9 estimated (B0 2.1, C 0.5, K2 0.5, 4B 3.3, 4I 3.7); peak 3.5 GiB. Output:
  `s1/exp0050/scores.json`.
- **Result** (plain R score: mean over the nine templates of balanced accuracy or accuracy, %;
  95% intervals, company bootstrap, 10,000 resamples; B = the arm's accuracy on B development
  items, from disk):

  | Arm | R, plain | Raw accuracy | Hint − plain (R1.1–R1.8) | B |
  |---|---|---|---|---|
  | B0: 0.8B as released | 55.9 [51.5, 60.2] | 55.8 | +1.9 [−3.8, +7.7] | 57.2 |
  | C: D3-s1 + calculator | 0.9 [0.2, 1.8] | 0.9 | +0.2 [−0.7, +1.3] | 87.5 |
  | K2: K2-s1 + calculator | 0.7 [0.0, 1.5] | 0.7 | −0.5 [−1.3, 0.0] | 89.3 |
  | 4B, no tool | 82.0 [79.3, 84.6] | 82.0 | +8.5 [+4.7, +12.1] | 91.2 |
  | 4I: 4B + calculator | 82.2 [79.5, 84.9] | 82.2 | +11.0 [+7.6, +14.3] | 90.8 |

  By template, plain (B0 / 4B / 4I; C and K2 are 0 on every template but R1.7, where they score 8
  and 6): R1.1 margin direction 63.6 / 89.7 / 91.8; R1.2 operating leverage 52.4 / 100 / 100;
  R1.3 cost against sales 68 / 84 / 82; R1.4 EPS against net income 66 / 80 / 82; R1.5 tax line
  50 / 92 / 88; R1.6 biggest mover 77.4 / 100 / 100; R1.7 derived period 2 / 10 / 10; R1.8
  margin change 56 / 84 / 88; R1.9 not answerable 68 / 98 / 98.
- **Criteria:**
  1. **R-d gate: passes by its rule, but the gap is format, not reasoning.** 4I − K2 = 81.5
     [78.9, 84.2], above 5.0 with the interval above 0, so R-d is put to the owner. But C and K2
     put a number in the box on 291 and 300 of the 300 label base items (73.0% and 73.6% of all
     their responses are invalid). Every response keeps the layout they were trained on (`Row;
     Column; Calculation; \boxed{number}`): on R1.8 they box a margin level instead of its change,
     on R1.9 a figure instead of "cannot be determined" (0 of 50). Distillation on B fixed the
     0.8B into one answer shape; the hint does not move it. The gate number therefore measures
     that, and says nothing about how far a small model is behind on reasoning. The untrained
     0.8B is the reasoning reference: 4B − B0 = 26.1 [20.9, 31.4] (registered pair); 4I − B0 =
     26.3 (exploratory).
  2. **Item validity: R1.7 flagged; no wrong gold found.** R1.7 is flagged on both counts (best
     of 4B and 4I 10.0; 43 of 50 base items wrong for all five arms). Ten of the 43 were read with
     4I's plain and hint responses: 0 wrong gold (each gold is the year-to-date total minus the
     quarter shown, equal to the XBRL fact for the earlier period), 9 ambiguous question, 1 model
     error. In the 9 the 4B answers "cannot be determined" because no column shows the asked
     period: it reads the escape clause, which R1.7 shares with R1.9, as "not stated" rather
     than "not derivable". With the hint it does the subtraction (80 and 82 on the template). The
     model error takes the year-ago quarter for the first quarter. Over all 50 R1.7 items the 4B
     answers "cannot be determined" on 41 (4I 40, B0 31). With no wrong gold, no fix-forward is
     required by the rule. Not flagged but read as well: R1.4's 5 all-wrong items (golds right;
     the 4I reads another EPS column in 3, inverts the comparison of two declines in 1, writes no
     box in 1) and R1.8's 4 (golds right by arithmetic; 3 are companies with almost no revenue,
     e.g. revenue of $1.6 million against an operating loss of $149 million, where the gold
     change is −3,684.8, −874.2 or +11,995.6 points and the 4I drops the ×100; the fourth reads
     another period column).
  3. **Ceiling and floor.** R1.7 is at the floor for every arm. R1.2, R1.6 and R1.9 are at the
     ceiling for 4B and 4I. C and K2 are at the floor on all nine templates, so in their present
     form they have no template left for R-c's contrasts. B0's only floor is R1.7. For 4B and 4I
     against B0, R-c would keep R1.1, R1.3, R1.4, R1.5 and R1.8.
  4. **R against B** (gap on R plain; gap on B; R − B):
     - 4I − K2: 81.5 [78.9, 84.2] (raw 81.6); 1.5 [−1.5, 4.5]; 80.0 [76.2, 83.9].
     - 4I − C: 81.3 [78.7, 83.9] (raw 81.3); 3.3 [0.0, 6.6]; 78.0 [73.9, 82.1].
     - 4B − B0: 26.1 [20.9, 31.4] (raw 26.2); 34.0 [29.7, 38.2]; −7.9 [−14.5, −1.2].
     For the two untrained models R does not widen the gap that B shows. B0's B score was made
     under a 256-token cap and its R score under 512, which favours B0 on R.
  5. **R-c size: above 3,000, so the owner decides.** 4I − K2: d 0.820, DE 0.92, n 9,357. 4I − C:
     d 0.818, DE 0.92, n 9,349. The rule sizes a test for a 3-point difference, and d is high
     because the distilled arms fail on format. Exploratory, for the owner's decision: 4I − B0
     d 0.353, DE 1.10, n 4,796 (4B − B0 n 5,165). The 4B arms take 7 to 8 seconds an item.
- **Also reported:**
  1. **Hints help the 4B on one template only.** Almost all of the hint gain is R1.7 (4I 10 →
     80). Without R1.7 (exploratory) the gain is +2.6 for 4I, −0.6 for 4B and −1.0 for B0. The
     hint costs B0 16 points on R1.8 (56 → 40) and the 4B 8 (84 → 76). Design §7's working
     hypothesis (hints keep the 0.8B close to the 4B) gets no support.
  2. **Twins.** On flip twins (years swapped) the share right when the base was right: 4I 77.9,
     4B 78.8, B0 49.7. Hold twins (an employee row added), same answer as the base: 4I 92.2, 4B
     91.6, B0 71.3. Mirror twins (subjects swapped), the same label given to both: 4I 15.3%, 4B
     17.3%, B0 38.0%. B0's answers follow the figures about half the time; the 4B's flip accuracy
     is 13 points under its base accuracy (76.4 against 89.9).
  3. **Steps.** Share of the step chain's figures written in the response: 4I 88.2%, 4B 87.7%,
     B0 59.2%, C 31.8%, K2 35.1%. Right answers with a figure missing: B0 101 of 217, 4B 40 of
     320, 4I 36 of 321. About half of B0's right labels are not backed by the figures.
  4. **Operations.** Forced: B0 20.6%, 4B 9.5%, 4I 7.6%, C 2.5%, K2 0.5%. Invalid: B0 2.5%, 4B
     0.7%, 4I 0.5% (C and K2 above). With a calculator call: 4I 72.4%, C 94.8%, K2 94.3%. Median
     generated tokens: B0 407, 4B 367, 4I 350, C 69, K2 67; over 160 tokens: 4B and 4I 99.0%, B0
     97.5%. Seconds per item: B0 4.55, C 1.08, K2 0.98, 4B 7.06, 4I 7.98.
- **Leakage sign-off:** development items only; no model labelled an item; Claude read
  development items and responses only. Clean.
- **Verdict:** the R-d gate passes by its rule, but the 81-point gap is the distilled 0.8B
  failing to give a label at all, not failing to reason: distillation on B left it able to box
  one number and nothing else. The question R-b was meant to answer is better put against the
  untrained 0.8B: the 4B is 26 points ahead on R, against 34 on B. R gives the 4B real headroom on
  five of nine templates (R1.1, R1.3, R1.4, R1.5, R1.8, 80 to 92); R1.2, R1.6 and R1.9 are at its
  ceiling. R1.7's golds are right, but its question sends every model to "cannot be determined";
  as worded it is at the floor and drops out of R-c. Hints do not help the small model. R-c's size
  rule gives about 9,400 base items, so the owner decides before R-c is written. Owner decisions
  needed before R-c or R-d: (a) R-c's arms (C and K2 as trained score at the floor everywhere;
  B0 is the small model with a reasoning score); (b) whether R1.7 is reworded by a new builder
  (no escape clause on R1.7) and R1.8 restricted to margins a reader would use; (c) R-c's size;
  (d) whether R-d is proposed, and if so with a control that separates learning the answer
  format from learning to reason.

## EXP-0048 — S2 prospective arm: sealed calls on the October and November 2026 releases (2026-11-23)

### PRE-REGISTRATION
- **Status:** approved by the owner 2026-11-24 ("呃，批准"); not yet run, no call made. The
  forecasts are made once the next-stage collection is done (about 2026-12-08) and sealed before
  2027-01-10. **Progress 2026-11-24:** reader on the 180 releases done (180 replies, every canary
  present, none unparsed); code facts built from the November series (current-quarter growth
  missing in 16 of 180, as 23 of 257 in EXP-0036, by the same "number shown in the release"
  rule); A1 forecasts (180 calls) made the same day: every canary present, every probability
  readable (gross margin NA in 42, operating margin NA in 4). A1C waits for the calls.
  **Interim seal, 2026-11-24 09:38 UTC** (owner: "好的"): `seal` dropped 8 companies that filed
  another earnings 8-K after the release used (TSLA, PRU, TEX, UWMC, AVNT, NOG, JKHY, SSP, all
  2026-10-21 to 11-06: second filings on the same September quarter, not December-quarter
  results; dropped because the rule counts any later Item 2.02); 172 A1 forecasts sealed;
  manifest `research/registry/seals/exp0048_manifest.json` (forecasts file SHA-256 311201b0...).
  The final seal, with A1C, follows the call collection.
- **Claim under test:** on a quarter whose outcome does not yet exist anywhere, (1) the PM with
  the release and code facts (EXP-0036's A1) beats the code baseline, as it did on the July and
  August releases; (2) the call adds to it, as EXP-0047 asks on the clean quarter. A second clean
  quarter also separates "after the cutoff" from "this particular quarter" (roadmap item 11).
- **Why the answer is not obvious:** EXP-0036's clean quarter is one quarter; its edge over code
  (0.72 against 0.59) may belong to that quarter's conditions.
- **Sample, fixed here before looking:** EXP-0046's 184 "next" episodes (training and
  development companies; the release after each clean one, filed 2026-10-01 to 2026-11-11, all
  on the drive). A1 for all; A1C where EXP-0045 holds a full call document at sealing time.
- **Calls:** A1 and A1C exactly as EXP-0047 (same skill block, questions and transport), one item
  per call. EXP-0036's code facts take guidance from its reader's form, so EXP-0036's reader (R)
  runs first on the 184 releases and the facts are built from its replies, as in EXP-0036; at
  most 552 calls (added 2026-11-24, before any call, once the dependence was found). The facts
  are built from EXP-0020's November series: it already holds the September quarter's first
  filing for all 180 companies (large filers file 10-Qs within 40 days). A1 runs once the reader
  is in; A1C once the October and November calls are collected. Code baseline: EXP-0036's
  per-label logistic models, refitted only on outcomes filed before 2026-11-12.
  Episodes whose release text is not on the drive are dropped (2026-11-24, before any call: the
  first `prepare_r` stopped on the first of them): REGN, VG, FG (filed 2026-10-05 to 10-07,
  likely not the full earnings release) and JAZZ; 180 remain.
- **Sealing:** forecasts stay on the drive; a manifest of SHA-256 hashes (one per forecast file,
  plus the prompt and skill hashes) is committed and pushed before 2027-01-10 and before the
  first next release of any company in the sample; a company that reports before the push is
  dropped and listed. Sealed together with EXP-0001 if that is ready.
- **Labels:** L1 to L4 as EXP-0036, from the first filing of the December 2026 quarter (a company
  facts snapshot after the 10-K season, about March 2027).
- **Criteria (scored once, after labels exist):** 1. A1 minus code baseline, L1, accuracy and
  Brier, 90% bootstrap intervals (episodes, seed 20261127). 2. A1C minus A1, paired, L1 (primary
  of the call question on this quarter), L2 to L4 with Benjamini-Hochberg q = 0.10. 3. The
  same differences on EXP-0036's clean quarter beside these, descriptive.
- **Contamination label of the result:** prospective.
- **Not in scope:** test companies (Claude does not read post-cutoff test items; a scripted path
  would be needed); price reactions.

## EXP-0047 — S2-b: does the earnings call add to the release? Clean-quarter pilot (2026-11-23)

### PRE-REGISTRATION
- **Status:** approved by the owner 2026-11-24 ("呃，批准"); not yet run, no call made. Runs
  once the clean stage of the Alpha Vantage collection is done (about 2026-11-30). Script
  `exp0047_s2b_call_pilot.py` written 2026-11-24; `prepare --dry` on the 58 documents then
  available: A is EXP-0036's A1 prompt verbatim in 58 of 58; prompts about 14,700 tokens (A),
  27,900 (A1C) and 27,300 (reader), medians.
- **Claim under test:** (1) adding the call (prepared remarks and Q&A, EXP-0045's document) to
  EXP-0036's A1 prompt raises the PM's readout on clean episodes; (2) exploratory: skill v1 Part D
  features read from the call relate to next-quarter outcomes.
- **Why the answer is not obvious:** the release already holds the numbers and most guidance;
  the call adds outlook talk and answers under questioning, which the literature finds
  informative (stream 11: `druz-2020`, `bochkay-2020`), but a prompt of 30,000 to 40,000 tokens
  may dilute rather than add (stream 12), and EXP-0036's code facts moved the revenue call by
  only +0.006.
- **Sample, fixed here before looking:** EXP-0036's 197 clean episodes that have a full call
  document (not partial) in EXP-0045 at the run; now 53, expected about 150. Partial documents
  (prepared remarks or letters only, 5 now) are run and reported apart.
- **Calls (Opus through EXP-0027's isolated headless transport, one item per call):**
  - A1, re-run: EXP-0036's A1 prompt unchanged, so that both arms come from one run.
  - A1C: A1 plus, after the release, "The earnings call (transcript):" and the call document.
  - RC, reader on the call (PM definition, no probability asked): Part D form, each answer with
    a quote checked against the text: D1 management more downbeat than the release's numbers /
    in line / more upbeat; D2 extreme negative words used by management (quotes); D3 answers that
    read as scripted (share of answers); D4 analysts' tone (negative / neutral / positive); D5
    direct refusals to answer (count, with quotes).
  About 450 calls at about 150 episodes.
- **Labels:** L1 to L4 as EXP-0036 (L1 primary).
- **Criteria (readout = probability on the realised direction; 90% intervals from 10,000
  bootstrap draws of episodes, seed 20261128):**
  1. Primary, L1: A1C minus A1, paired. "Helps" if the interval is above 0, "hurts" if below,
     otherwise undecided.
  2. L2 to L4: the same, Benjamini-Hochberg across the three (q = 0.10).
  3. Accuracy and Brier of A1, A1C and the code baseline, per label.
  4. Run-to-run noise: A1 here against EXP-0036's A1 on the same episodes (agreement and mean
     absolute probability difference), descriptive.
  5. Slices, descriptive: source (Alpha Vantage, IR file), size (250 largest or not).
  6. Exploratory: D1 and D2 against the L1 and L4 outcomes; D5 against the spread of the PM's
     probabilities.
  7. Exploratory, scored by code with the Loughran-McDonald Master Dictionary 1993-2025 (owner,
     2026-11-24; file SHA-256 e2d13286...4859d): words upper-cased and matched whole; tone =
     (positive - negative) / words. "Gloom beyond the release" = tone of management's prepared
     remarks minus tone of the release text; also the negative and uncertainty shares of
     management's answers in the Q&A (Alpha Vantage documents, where speakers are labelled).
     Each against the L1 and L4 outcomes (difference in outcome rates between the lowest and the
     highest third) and against A1C minus A1 per episode; reported beside the reader's D1 and D2.
     No threshold; nothing from it feeds the primary.
- **Contamination label of the result:** clean (vendor-stated cutoff).
- **Power:** at about 150 episodes a paired difference of about 0.03 is detectable; at the 53
  available now, about 0.06.
- **Not in scope:** old (replayed) episodes: skill v1 Part D gives no raw call text there, since
  style re-identifies the company (their code-scored tone may be added later as a feature).

## EXP-0036 — S2-b: code-stated facts, the analyst skill, and a blinded brief, on clean episodes (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Owner, 2026-11-22: approved at the proposed scale; asked that the
  question of what recurs and what is one-off cover more than earnings ("不仅仅是盈利 很多方面我们都
  想看是不是可持续还是单次性的 加上"); agreed to freeze skill v1 from the literature without tuning.
- **Claim under test:** (1) facts computed by code and stated as sentences (comparison base,
  reference rates, guidance arithmetic, inventory and contract liabilities against revenue, the
  margins' own year-ago bases) raise the PM's readout on clean episodes over the raw release
  alone; (2) a brief made only of those facts and a quote-checked reader form (skill v1, Part B)
  keeps that signal while hiding the company and leaking less on old episodes.
- **Why the answer is not obvious:** prompt structure rarely helps forecasts (stream 12); the
  facts duplicate numbers already in the release; EXP-0031/0032's briefs lost most of the signal.
- **Sample, fixed here before looking:** clean: every post-cutoff episode of the 500 largest
  training and development companies with a label, a release on the drive, under 80,000
  characters and EXP-0026's earnings filter: 197 (82 of them among the 250 largest; EXP-0026's 30
  clean episodes are among them). Old: EXP-0026's 60 old episodes.
- **Labels (owner's point 2):** L1 revenue acceleration (EXP-0020, 2-point dead band; primary);
  L2 gross margin up year on year next quarter; L3 operating margin up year on year next quarter;
  L4 net income up year on year next quarter. Dead bands: 0.25 margin points for L2 and L3, 2% of
  the year-ago amount for L4. All from as-filed company facts, first filing of each quarter.
- **Calls (Opus through EXP-0027's isolated headless transport, one item per call):**
  - R, reader (PM definition), raw release: fills skill v1's form (EXP-0032's form plus what
    recurs and what does not, by line, exit rate, inventory and channel, management language);
    no probability asked. 257 calls.
  - A0, raw release + skill v1's considerations block (identical in A0, A1 and B) + the four
    questions, probabilities first, then at most four sentences. 257.
  - A1, A0 plus the code facts. 257.
  - B, code facts plus the code-rendered form only, no release text. 257.
  - Attacker on B (EXP-0028's question): the 60 old and EXP-0026's 30 clean episodes. 90.
  Code facts use only filings made before the release, plus current-quarter values whose number
  appears in the release text; growth in whole percent, margins to one decimal.
- **Code baselines:** per label, a logistic regression fitted on episodes whose outcome was filed
  before 2026-07-01 (L1: EXP-0035's combined model; L2 to L4: own persistence, g(t) .. g(t-4) and
  the label's own year-ago base); for clean episodes these are point in time.
- **Criteria (readout = probability on the realised direction; 90% intervals from 10,000
  bootstrap draws of episodes, seed 20261131):**
  1. Primary, L1, clean: A1 minus A0 paired readout. "Helps" if the interval is above 0; "hurts"
     if below; otherwise undecided.
  2. L1, clean: B minus A1 paired readout. "Retains" if the estimate is at least -0.03 and the
     interval's lower end above -0.10; "loses" if the interval is below 0; otherwise undecided.
  3. B's leak: old minus clean readout (no leak detected if the interval spans 0); attacker top-1
     on B ("stopped" at most 0.20, "not stopped" at least 0.50). B is a usable replay input if
     not "not stopped", no leak detected, and not "loses".
  4. Each arm's old-minus-clean gap is reported; A1 must not raise the gap over A0 by more than
     0.05 (interval of the difference).
  5. Against code, clean: accuracy and Brier of A0, A1, B, the code baseline, and the average of
     each arm's probability with the code baseline's (equal weights, fixed here).
  6. L2 to L4, clean: criteria 1, 2 and 5 repeated, reported with Benjamini-Hochberg across the
     three labels (q = 0.10), as secondary.
  7. Exploratory: does the reader's tag "does not recur next quarter" on a line predict that line's
     next-quarter year-on-year change in the opposite direction?
  Calibration (mean probability, Brier and its reliability part) is reported per arm and label.
- **Contamination label of the result:** clean (vendor-stated cutoff) for the clean episodes;
  contaminated for the old ones, which serve only to measure leaks.
- **Power:** with about 197 clean episodes the paired readout difference is detectable at about
  0.03 to 0.04; prompt-placement effects of the size in stream 12 are not.
- **Not in scope:** placement variants of the checklist; call transcripts (owner asked for an IR
  survey first); tuning the skill.

### RESULTS
- **Run:** 2026-11-22 to 2026-11-23, Opus through EXP-0027's headless transport, three workers;
  1,118 calls (R 257, A0 257, A1 257, B 257, attacker 90), every canary present, no reader reply
  unparsed, every A0 probability readable (gross margin NA in 61, operating margin NA in 6).
  Skill block hash 638f5e7f2a783553. Reader form: 1,117 recurrence entries kept (one dropped for
  a quote not found), exit rate stated in 15 releases, inventory or channel in 43; code facts:
  comparison base 241, revenue reference rate 238, inventory 121, contract liabilities 58,
  guidance 26 next quarter and 67 full year, rest of year 56. Clean revenue base rate 104 of 197
  accelerate (0.53). Output `s2/exp0036/score.json`.
- **Criterion 1 (L1 revenue, clean, A1 minus A0, paired):** +0.006 [-0.003, +0.016], n 197:
  **undecided**. The code facts did not measurably move the revenue call.
- **Criterion 2 (L1, clean, B minus A1, paired):** -0.059 [-0.072, -0.046]: **loses**.
- **Criterion 3 (B as a replay input):** B's old-minus-clean readout +0.021 [-0.025, +0.067], no
  leak detected; attacker top-1 on B 0.42 [0.33, 0.51] of 90 (old 0.50, clean 0.27):
  **undecided**. Not a usable replay input, because it loses the signal.
- **Criterion 4 (old minus clean, L1):** A0 +0.122 [+0.082, +0.161], A1 +0.100 [+0.061, +0.140],
  B +0.021. A1's gap minus A0's: -0.022. The frozen script reports this difference as a point
  estimate only; the interval named in the criterion was not computed.
- **Criterion 5 (against code, clean, L1):** accuracy / Brier: A0 0.72 / 0.177, A1 0.75 / 0.173,
  B 0.66 / 0.214, code baseline 0.59 / 0.239 (n 182; readout 0.53). Averaging with code lowers
  each arm (A1 + code 0.71 / 0.197). 250 largest, readout: A0 0.594, A1 0.592, B 0.537, code
  0.514. On this clean quarter the code baseline, 0.68 out of fold before the cutoff (EXP-0035),
  falls to 0.59; the model's lead over code is one quarter's and may not generalise.
- **Criterion 6 (secondary labels, clean; Benjamini-Hochberg, q = 0.10, all three pass):**
  - L2 gross margin: A1 minus A0 +0.013 [+0.001, +0.026], n 110, p 0.072; B minus A1 -0.047
    [-0.062, -0.032]; accuracy / Brier A0 0.79 / 0.153, A1 0.87 / 0.139, B 0.75 / 0.171, code
    0.75 / 0.188.
  - L3 operating margin: +0.032 [+0.018, +0.046], n 149, p < 0.0001 (no draw at or below 0); B
    minus A1 -0.059 [-0.076, -0.043]; A0 0.78 / 0.157, A1 0.79 / 0.140, B 0.76 / 0.174, code 0.76 /
    0.179.
  - L4 net income: +0.013 [+0.002, +0.023], n 180, p 0.040; B minus A1 -0.088 [-0.102, -0.073];
    A0 0.82 / 0.148, A1 0.82 / 0.140, B 0.67 / 0.196, code 0.71 / 0.182.
  - A1's old-minus-clean gap minus A0's: gross margin +0.018, operating margin -0.044, net income
    +0.001 (point estimates).
- **Calibration:** mean probability of "yes", clean, A0 / A1 / B: revenue 0.42 / 0.42 / 0.42
  against a base rate of 0.53; gross margin 0.52 / 0.52 / 0.53; operating margin 0.54 / 0.55 /
  0.54; net income 0.60 / 0.60 / 0.58. The frozen script does not split Brier into its
  reliability part, which the pre-registration named.
- **Criterion 7 (exploratory, clean; reader tags, counted per tag, not per episode; share of
  "yes" next quarter):** revenue raised this quarter by an effect tagged "does not recur" 0.17 (12
  tags), lowered and "does not recur" 0.82 (11), raised and "recurs" 0.51 (51), lowered and
  "recurs" 0.54 (13). Operating costs (sign turned to the margin): margin lowered, "does not
  recur" 0.69 (16), lowered, "recurs" 0.44 (16), raised, "does not recur" 0.40 (5), raised,
  "recurs" 0.64 (11). Gross margin and net income cells have 2 to 10 tags each.
- **Reading (ours):** on 197 clean episodes Opus reading the raw release with skill v1's
  considerations calls revenue acceleration at 0.72, against 0.59 for the code baseline on this
  quarter and in line with EXP-0026's raw view (0.77 on 30 clean); without a no-skill arm the
  level cannot be credited to the skill. Code-stated facts did not move the revenue call but
  improved all three earnings-side calls, most for operating margin (+0.03 readout, Brier 0.157
  to 0.140), where they give the margin's own year-ago base and reference rate. The brief made of
  facts and form only stops the measured leak (gap 0.02) but loses 0.05 to 0.09 of readout on
  every label and is still recognised half the time on old episodes, so it fails as a replay
  input, like EXP-0031 and EXP-0032's briefs. The reader's tags of what does not recur point the
  way the owner expected (a one-off lift is followed by deceleration in 10 of 12 tags, a one-off
  drag by acceleration in 9 of 11), on few tags and without an interval; a pre-registered test
  needs more clean episodes or a feature built from the tags.

## EXP-0035 — S2-a: do as-filed accounting items add to the comparison base? (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Follows the owner's request of 2026-11-22 for an analysis skill that
  reads the accounting structure behind the numbers (changelog), and literature stream 10 (draft),
  whose checklist ranks backlog/RPO, deferred revenue, inventory, gross margin and receivables as
  candidate leads of sales, all tested on annual data and none against a comparison-base baseline.
- **Claim under test:** some balance-sheet and margin items, as first filed, predict next
  quarter's revenue acceleration beyond EXP-0034's five-lag logistic (R3, 0.675).
- **Why the answer is not obvious:** the evidence is annual, mostly on small and mid-sized firms,
  and does not control for the year-ago comparison base, which already explains much of the label;
  stream 10 finds no post-announcement drift after revenue surprises for large firms.
- **Kind:** code only, on EXP-0020's as-filed company facts (training and development companies);
  no model, no pull. Script `exp0035_s2a_accounting_screen.py`.
- **Sample, fixed here before looking:** EXP-0034's 22,373 episodes (five quarters of as-filed
  growth, outside the 2-point dead band); reported on all and on the 250 largest companies.
  Point in time: each item for quarter t is the value in the filing that first reports quarter t
  (or earlier), and its year-ago value as first filed. The decision time is therefore that 10-Q or
  10-K, a few weeks after the release; the release carries the same balance sheet in 78 of
  EXP-0026's 90 releases.
- **Features, fixed here (growth gaps clipped to [-1, 1], margin changes to [-0.5, 0.5]):**
  F1 inventory growth minus revenue growth (year on year); F2 receivables growth minus revenue
  growth; F3 contract liabilities or deferred revenue growth minus revenue growth; F4 remaining
  performance obligations growth minus revenue growth; F5 gross margin change; F6 SG&A growth
  minus revenue growth; F7 operating margin change; F8 change in non-operating income (pre-tax
  less operating income) over revenue; F9 sector growth: median g(t) of other companies with the
  same two-digit SIC and calendar quarter, as filed by the focal filing date (at least five
  peers); F10 g(t) minus F9. The first concept a company tags is used, in the order in the script.
- **Method and baseline:** R3 with EXP-0034's company folds (seed 20261129). For each feature, R3
  and R3 plus the feature are fitted on the same episodes (those where the feature exists) and
  scored out of fold. Combined model: R3 plus all ten, a missing feature set to 0 with a missing
  indicator. Increments in log loss and accuracy, 90% intervals from 2,000 bootstrap draws of
  companies (seed 20261130).
- **Criteria:**
  1. Per feature, all episodes: "adds" if the log-loss increment's bootstrap p-value survives
     Benjamini-Hochberg at q = 0.10 across the ten features and the accuracy increment is not
     negative; otherwise "nothing found".
  2. Combined model, 250 largest companies: "worth stating in the brief" if accuracy rises by at
     least 1.0 point over R3 with a 90% interval above 0; "no material gain" if the interval's
     upper end is below 1.0 point; otherwise undecided.
  3. Exploratory, no decision: the same screens for EXP-0020's earnings-side labels (next
     quarter's operating margin up year on year; net income up year on year) on the same
     episodes, base = logistic on the label's own persistence, g(t) .. g(t-4) and F7.
- **Contamination label of the result:** not applicable (no model).
- **Not in scope:** items only in words (backlog, bookings, organic growth, price and volume,
  guidance), inventory components, cash-flow accruals, any model call.

### RESULTS
- **Run:** 2026-11-22, no model call; 22,373 episodes (4,637 among the 250 largest companies).
  Coverage, all / 250 largest: inventory 0.60 / 0.65, receivables 0.73 / 0.73, contract
  liabilities 0.46 / 0.45, RPO 0.16 / 0.21, gross margin 0.65 / 0.63, SG&A 0.48 / 0.59, operating
  margin 0.85 / 0.80, non-operating 0.76 / 0.76, sector 0.76 / 0.67. Output
  `s2/exp0035/result.json`.
- **Criterion 1 (per feature, all episodes; accuracy gain over R3 on the episodes with the item,
  90% interval; sign of the coefficient):**
  - **Adds:** F1 inventory gap +1.0 point [+0.6, +1.5] on 13,513 (250 largest: +0.8 [-0.1, +1.8]),
    positive: inventory growing faster than revenue goes with acceleration; F3 contract
    liabilities gap +0.7 [+0.2, +1.2] on 10,298 (250 largest: +1.0 [-0.1, +2.1]), positive; F2
    receivables gap, log loss only, accuracy +0.1 [-0.2, +0.4] (250 largest +0.6 [-0.1, +1.3]),
    positive, not the negative sign a pull-forward reading predicts; F6 SG&A gap, log loss only,
    accuracy +0.1 (250 largest -1.2 [-2.0, -0.4]); F7 operating margin change +0.3 [+0.0, +0.5].
  - **Nothing found:** F4 RPO (3,646 episodes), F5 gross margin, F8 non-operating income, F9
    sector growth, F10 growth against the sector.
- **Criterion 2 (combined, 250 largest):** accuracy 0.669 to 0.676, +0.7 points [-0.3, +1.6]:
  **undecided**. On all episodes 0.675 to 0.683, +0.8 [+0.4, +1.2]; log loss improves in both.
- **Exploratory, earnings-side labels:** combined accuracy gains are nil (operating margin up
  -0.04 points all, +0.2 for the 250 largest; net income up +0.2 and +0.3), with small log-loss
  gains. The one item in the owner's example, a rise in non-operating income, has the expected
  sign for net income (coefficient -0.69: a quarter lifted by non-operating income is less often
  followed by a year-on-year rise) and improves log loss (+0.0009 [+0.0003, +0.0016]), but moves
  accuracy by less than 0.2 points.
- **Reading (ours):** two balance-sheet leads, inventory and contract liabilities growing faster
  than revenue, add about one point of accuracy to the comparison-base logistic, in line with
  stream 10 (raw materials and work in process lead sales; deferred revenue leads sales growth);
  among the 250 largest the gain has the same size but the interval reaches zero. The statistical
  bar for an S2 call rises to about 0.68. These items are worth stating in a brief as sentences
  (skill draft, Part A4); none is large, so their value to the PM has to be shown on clean
  episodes, not assumed. One-off items matter for earnings, as the owner expected, but in this
  code-only form they barely move direction calls.

## EXP-0034 — S2-a: does the comparison base alone predict acceleration? (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Follows from EXP-0033 (right post-cutoff calls lean on the comparison
  base); within the owner's request of the same day to find what makes post-cutoff calls right.
- **Kind:** code only, on EXP-0020's as-filed series (training and development companies); no
  model, no pull. Script `exp0034_s2a_base_effect.py`.
- **Label:** EXP-0020's: next quarter's year-on-year growth minus this quarter's, outside a
  2-point dead band. g(t-k) is year-on-year growth k quarters before this one, as first filed.
- **Rules, fixed here before looking:**
  R1 reversal (EXP-0020's best, 52%): accelerates if growth fell last quarter.
  R2 comparison base: accelerates if g(t-3) < g(t-4), i.e. next quarter is compared against a
  weaker year-ago quarter than this one was (two-year growth held constant).
  R3 logistic regression on g(t), g(t-1), g(t-2), g(t-3), g(t-4), five-fold cross-validation
  grouped by company, seed 20261129.
- **Reported:** accuracy of each rule outside the dead band on all episodes with the needed
  quarters; on episodes among the 250 largest companies; and on EXP-0026's 90 episodes (60 old,
  30 clean), beside EXP-0026's raw-view and no-document calls on the same episodes.
- **Known limits:** derived fourth quarters (year less nine months) carry their own noise;
  rules see no text.

### RESULTS
- **Run:** 2026-11-22, no model call. 22,373 episodes outside the dead band with five quarters of
  as-filed growth known at the time (1,205 companies); base rate 0.493.
- **Accuracy, all / 250 largest (4,637) / 50 largest (1,031):** R1 reversal 0.520 / 0.498 /
  0.500; **R2 comparison base 0.652 [0.647, 0.658] / 0.653 / 0.657**; R3 logistic 0.675 [0.670,
  0.680] / 0.669 / 0.661. R3's coefficients (fold 1, on intercept, g(t) .. g(t-4)): 0.23, -1.38,
  0.26, -0.23, -1.85, 1.07: next quarter accelerates when this quarter's growth and the year-ago
  next quarter's growth are low and this quarter's year-ago growth is high.
- **On EXP-0026's episodes (those with five known quarters):** old 56: R2 0.68, R3 0.71 (model
  raw 0.95, prior 0.86); clean 28: R2 0.64, R3 0.57, model raw 0.75, no-document prior 0.64.
- **Reading (ours):** the label is far from rule-proof: the year-ago comparison base alone calls
  65% of episodes, the same for the largest companies. EXP-0020's "best simple rule 52%" holds
  only for the rules it tried. On clean episodes the model's no-document prior (0.64) is no
  better than R2 (0.64), so what EXP-0032 called "knowledge of the company" may largely be the
  comparison base, which code can state without naming anyone. EXP-0032's arm s4 gave the PM the
  four earlier quarters and its clean readout did not move (+0.005): the PM did not do this
  arithmetic from a table; it has to be done by code and stated.

## EXP-0033 — S2-b: what makes a post-cutoff call right? (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Asked for by the owner on 2026-11-22 (dictated): "去看一看 cut off 之后的
  这些判断，这些预测，尤其是看那个预测准确的和预测不准确的，归因一下，然后看看能不能从这里面找到他们预测正确究竟的
  是什么原因，不应该是说因为这个公司才预测正确的，对于我们要看未来的信息。"
- **Kind:** slices of existing records, no new model call. Script
  `exp0033_s2b_clean_attribution.py`. Descriptive; no hypothesis, so no verdict threshold.
- **Data:** EXP-0026's 30 clean episodes (outcome after the cutoff), with the 60 old episodes as
  contrast: EXP-0026's raw-view call and no-document prior (name and quarter only); EXP-0029's
  structured answers on the raw and the fully blinded view (evidence items with source, direction,
  weight and verbatim quote) and its flip question.
- **Classification, fixed here before looking:** each DOCUMENT item by its quote, by keyword rule,
  first match wins: (1) guidance and outlook (guidance, outlook, expect, anticipate, forecast,
  target, "full year", "next quarter", "second half", "will"); (2) orders, backlog and pipeline
  (backlog, bookings, orders, book-to-bill, pipeline, remaining performance obligations, deferred
  revenue, awards, subscribers); (3) announced changes (acquisition, divestiture, spin-off, price
  increase, launch); (4) otherwise, this quarter's results. Categories 1 to 3 are
  "forward-looking". The rule is checked by hand on 25 items drawn by seed 20261128, agreement
  reported.
- **Slices:**
  1. Document against company: on clean episodes, raw-view call right or wrong crossed with the
     no-document prior right or wrong; paired readout raw minus prior.
  2. Evidence accuracy: for each source (DOCUMENT, GENERAL, MEMORY) and each DOCUMENT category,
     items' count, weight share, and the weighted share pointing the way that happened; clean and
     old, raw and blinded view.
  3. Right against wrong calls (EXP-0029 A, clean): weight share of forward-looking DOCUMENT
     items, of current-results items and of MEMORY items.
  4. Category of the item named as the one that would flip the answer, in right and wrong calls.
  5. Examples: for every clean episode, the top-weighted item of the raw-view answer, saved for
     reading.
- **Known limits:** 30 clean episodes; stated reasons are not causes (EXP-0029); the rule is
  crude. A causal test (removing forward-looking sentences and re-asking) is not in scope.
- **Added after the hand check, before the slices were read:** the rule agrees with my reading on
  19 of 25 items; all 6 disagreements are forward-looking items filed as "this quarter's
  results" (guidance printed as a table row, "Organic growth4: +2% to +4%"; a guidance sentence
  quoted without its verb; a homebuilder's backlog). An exploratory second rule also files an
  item as forward-looking when the model's claim speaks of guidance, outlook, full year,
  backlog, pipeline, bookings or orders. Both are reported.

### RESULTS (descriptive)
- **Run:** 2026-11-22, no model call.
- **1. Document against company (clean, raw view against the no-document prior):** both right 17,
  document right and prior wrong 6, document wrong and prior right 2, both wrong 5. Readout raw
  minus prior +0.094 [0.054, 0.132]. Old episodes: -0.002 [-0.042, 0.042]: the document adds
  nothing there to what the model remembers.
- **2. Evidence (clean, raw view; quote rule / claim rule):** this quarter's results carry 0.63 /
  0.54 of the weight, 0.68 / 0.66 of it pointing the way that happened; forward-looking items
  0.15 / 0.24 of the weight, 0.63 / 0.68 right; MEMORY 0.14, 0.68 right; GENERAL 0.09, 0.56
  right. Old episodes: MEMORY 0.98 right, GENERAL 0.89, this quarter's results 0.83. Called from
  one kind of evidence alone, clean: this quarter's results 0.73 (n 30), MEMORY 0.70 (20),
  forward-looking 0.58 (12) / 0.56 (16), GENERAL 0.52 (21). Blinded view, clean: results 0.86,
  MEMORY 0.74, forward 0.62 / 0.63, GENERAL 0.39.
- **3. Right against wrong calls (clean, raw; 23 right, 7 wrong):** weight on forward-looking
  items 0.17 against 0.06 (quote rule), 0.26 against 0.13 (claim rule); on MEMORY 0.11 against
  0.21; on this quarter's results 0.63 against 0.61.
- **4. Flip item (clean, quote rule):** right calls: this quarter's results 16, MEMORY 3,
  guidance 2, orders 1, announced changes 1; wrong calls: results 4, MEMORY 2, announced changes 1.
- **5. Reading the top item of each right clean call (my hand coding, exploratory):** 12 of 23
  are consequences already set by the time of the release: full-year guidance minus the first
  half, implying the second half (4); a known change that will be in next quarter and not this
  one, or the reverse: currency turning from tailwind to headwind, businesses sold during the
  quarter, a contract term ending, a plant back at full output, a quarter-end exit rate above
  the average, new customer load coming online (7); a larger backlog (1). 7 are comparison-base
  effects or one-offs that will not recur (an extreme quarter, investment gains inflating
  growth, last year's oil price), 2 of them taken from memory of the year-ago quarter, which was
  public at the time. 4 are trends in growth. In 6 of the 7 wrong calls revenue accelerated and
  the model said it would not; their top items are generic rules ("some reversion toward the
  lower trend is likely", "a clear deceleration that tends to persist"), a misread acquisition
  effect, and guidance that the company then beat.
- **Reading (ours):** after the cutoff, the document adds to what the name alone gives, and the
  right calls rest mostly on arithmetic of the next quarter that the release already fixes
  (guidance against year to date, known changes, comparison base), not on statements of
  sentiment and not on memory, which is right 68% of the time after the cutoff against 98%
  before. The wrong calls lean on generic mean-reversion and on memory. EXP-0031/0032's
  templates lacked most of this arithmetic: no comparison base, no implied rest-of-year growth,
  no flag for effects that change between this quarter and the next.

## EXP-0032 — S2-b: the rewrite template, version 2 (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Owner's go-ahead 2026-11-22 ("同意，开始做吧"). Script
  `exp0032_s2b_rewrite_v2.py`.
- **Claim under test:** EXP-0031's loss of signal came from its form, not from rewriting as such;
  a form that carries guided revenue (as growth) and drops segment shares keeps recognition low
  and the leak undetectable while recovering the signal.
- **Changes from EXP-0031, and only these:** (a) the reader also copies guided revenue amounts
  as printed, with their unit and a quote; code converts them to growth against the year-ago
  period as first filed (next quarter: the quarter three before this one; full year: the four
  quarters of the last completed fiscal year, or, after a fourth-quarter release, of the year
  just reported) and drops a conversion outside -50% to +100%; stated growth guidance is used
  as before when present. (b) Segments keep growth and order, not share. (c) Two ratio sheets:
  arm s2, EXP-0026's (two earlier quarters); arm s4, four earlier quarters, noised the same way.
  The brief is the FULL form (EXP-0031 found the judgements added no leak).
- **Sample and scope, fixed here before looking:** EXP-0026's 90 episodes. 90 reader calls (PM
  definition, raw release) and 360 short calls: attacker and PM on arms s2 and s4. About 2.5
  million tokens, through EXP-0027.
- **Method and baseline:** as EXP-0031 (readout, old minus clean, 90% bootstrap, seed
  20261127, EXP-0030's hit rule). Baselines on the same episodes: EXP-0026 raw view, EXP-0031
  FULL (attacker 0.444, leak 0.039, clean accuracy 0.63).
- **Criteria (each arm):**
  1. Attacker top-1: stopped at most 0.20, not stopped at least 0.50.
  2. Leak: no leak detected if the 90% interval of old minus clean includes 0.
  3. Signal: clean readout minus raw view, paired: retains if at least -0.03 with the interval
     above -0.10; loses if the interval is below 0. Also against EXP-0031 FULL, paired.
  4. Guidance coverage: briefs with next-quarter revenue guidance (stated or implied); target
     at least 25 of 90 (a rough text search found about 30 releases with a range).
  5. Sheet: s4 minus s2 on attacker top-1 and on clean readout, paired.
  An arm is **usable** for the next step if criterion 1 is not "not stopped", criterion 2 finds
  no leak and criterion 3 is not "loses".
- **Known limits:** as EXP-0031; 30 clean episodes; the implied guidance compares a guided figure
  with the year-ago figure as first filed, which may differ from the company's own basis.
- **Contamination label of the result:** old contaminated by design; clean clean (vendor-stated
  cutoff).
- **Not in scope:** a reader without outcome memory; more clean episodes; D.

### VERDICT
- **Run:** 2026-11-22, EXP-0027 transport, 450 calls, no failures, no tool use. All 90 forms
  parsed.
- **Results** (arm s2 / arm s4):
  1. Attacker top-1: 0.311 [0.233, 0.389] / 0.289 [0.211, 0.367], undecided (EXP-0031 FULL on
     the same episodes: 0.444); median confidence 20 / 21. Old 0.38 / 0.33, clean 0.17 / 0.20;
     the 50 largest 0.46 / 0.40, the rest 0.22 / 0.22.
  2. Leak: 0.069 [0.019, 0.119] / 0.082 [0.028, 0.135]: detected in both.
  3. Signal: clean readout minus raw, paired, -0.116 [-0.165, -0.069] / -0.111 [-0.143,
     -0.078], loses; against EXP-0031 FULL -0.025 [-0.046, -0.008] / -0.020 [-0.051, 0.012].
     Clean accuracy 0.60 / 0.53; mean clean readout 0.507 / 0.513, i.e. near 0.5.
  4. Guidance coverage: next quarter 5 of 90 (target 25: fails); full year 18 (EXP-0031: 15).
  5. Sheet: s4 minus s2, attacker top-1 -0.022 [-0.111, 0.067], clean readout 0.005 [-0.020,
     0.034]; four earlier quarters change neither.
  Neither arm is usable.
  Exploratory, across EXP-0031 and EXP-0032 on the same episodes: mean readout old / clean is
  raw 0.778 / 0.624, fully blinded 0.766 / 0.616, EXP-0031 FULL 0.572 / 0.533, FACTS 0.553 /
  0.508, s2 0.576 / 0.507, s4 0.595 / 0.513. Leak pooled over the four brief arms: 0.059 [0.012,
  0.105]. The leak of s2 exceeds EXP-0031 FULL's by 0.030 [0.007, 0.054], paired, mostly
  because clean readouts fell. On old episodes the attacker missed, the readout is still 0.56 /
  0.59 against clean 0.51.
- **Failure analysis:** (a) criterion 4's target rested on my text search in EXP-0031's
  verdict, which mostly matched reported results ("Fourth quarter net revenue was $13.8
  billion, down 6%"), not guidance; a search for guidance phrasing finds revenue guidance in
  about 4 to 6 of the 90 releases, and the reader found it in 6. Revenue guidance is rare in
  these press releases, so its absence is not what costs the signal. EXP-0031's verdict is
  corrected below. (b) A midpoint-and-band format ("$7.90 billion ± $200 million", Micron) has
  no printed low or high; the form's "exactly as printed" left it empty. (c) Dropping segment
  shares lowered recognition by about 13 points.
- **Verdict:** REJECT for template v2 as a usable input. Recognition is lower (about 30%), but a
  leak of 0.06 to 0.08 remains, which EXP-0031's interval had not excluded, and the brief keeps
  almost no signal on clean episodes (readout about 0.51, against 0.62 raw). Read together, the
  rewrite briefs cut the leak by about 60% (0.155 to about 0.06) and the clean signal by about
  90% (0.12 above 0.5 to about 0.01).
- **What this suggests (our reading, for the owner):** on these companies the content that
  predicts next-quarter acceleration and the content that identifies the company overlap; the
  no-document prior alone (name and quarter) reaches 0.63 clean accuracy, so part of what the
  raw release offers on clean episodes is knowledge of the company, which a live PM agent will
  have. The leak left among unrecognised old episodes points at the reader's choices or at the
  PM knowing more than the single-sample attacker shows. 30 clean episodes are too few to
  measure retention: 82 clean large-company episodes exist on the training and development side.

## EXP-0031 — S2-b: extract, then rewrite into a fixed template (2026-11-22)

### PRE-REGISTRATION
- **Status:** not yet run. Asked for by the owner on 2026-11-22 (dictated, in part): "先有一层去读，
  然后把他觉得预测需要的东西全都拿出来，然后完全重写一个 input，作为下一层的输入 … 你 identify 一些关键的要影响
  预测的 dimension，这些 dimension 应该是一些数字或者是一些描述，你保留这些，然后其他的东西给它全都给重写掉。你看看
  这样的效果怎么样？" The owner also set S2's scope: large companies (S&P 500) only.
- **Claim under test:** a release reduced to a fixed form of forecast-relevant facts and rendered
  by code in one template for every company (a) no longer lets the attacker name the company and
  (b) keeps the forecast signal; and with both, the old-minus-clean leak disappears.
- **Why the answer is not obvious:** EXP-0030 showed the attacker works from segment structure,
  reporting style and business description, all of which a fixed template removes; but the
  reader sees the raw release, knows the company and, for old episodes, the outcome, and can put
  that knowledge into its choices; and the remaining numbers (growth, segment shares, guidance)
  may still single out a large company.
- **Sample and scope, fixed here before looking:** EXP-0026's 90 episodes (60 old, 30 clean, all
  among the 250 largest companies). Script `exp0031_s2b_rewrite.py`.
  1. Reader: one call per episode to the PM definition (its instruction: answer only from the
     text) with the raw release: a JSON form of 11 percentages, 3 menu choices, up to 4 forward
     indicators and 4 unnamed segments, 3 judgements (demand, pricing, outlook tone) and up to 4
     next-quarter effects from a menu, each fact with a verbatim quote.
  2. Code keeps a number only if its quote is found in the release and the number is in its
     quote (or the reader marks it computed); keeps a choice or effect only with a found quote;
     rounds percentages to whole numbers; renders two briefs in one fixed English template:
     FACTS (verified facts and the sector) and FULL (FACTS plus the three judgements and the
     effects). No word of the reader's reaches a brief except menu entries. The ratio sheet is
     the one of EXP-0026's fully blinded view (noised, relative periods).
  3. Attacker (`s2-recall-claude-opus-5-5`, EXP-0028's question, wording adapted to a summary) on
     FULL and on FACTS; PM (EXP-0026's question) on FULL and on FACTS.
  450 calls, about 2.5 million tokens, through EXP-0027.
- **Method and baseline:** readout = probability given to the realised direction; leak = old
  minus clean; 90% bootstrap over episodes, seed 20261126. Baselines on the same episodes:
  EXP-0026 raw view (leak 0.155; clean accuracy 0.77; prior 0.63; persistence 0.54) and
  EXP-0028/0030 (attacker 90 of 90). Hit rule: EXP-0030's (folded case and punctuation).
- **Criteria:**
  1. Attacker top-1 over all 90, FULL and FACTS separately: stopped if at most 0.20, not stopped
     if at least 0.50. Also old against clean and by size tier.
  2. Leak, FULL and FACTS separately: no leak detected if the 90% interval of old minus clean
     includes 0; reported beside EXP-0026's raw 0.155.
  3. What the judgements add: leak of FULL minus leak of FACTS (the reader's judgements are where
     knowledge of the outcome can enter without a quote).
  4. Signal kept, FULL and FACTS separately: clean readout of the brief minus the raw view's,
     paired over the 30 clean episodes. Retains if the estimate is at least -0.03 and the interval
     lies above -0.10; loses if the interval lies below 0; otherwise undecided. Clean accuracy
     beside raw, prior and persistence.
  5. Extraction: share of episodes with each main fact (reported and organic growth, next-quarter
     and full-year guidance, segments, forward indicators); facts dropped by kind of failure.
  6. Exploratory: demand judgement (+1 strong or improving, -1 softening or weak, else 0), up
     minus down episodes, old against clean.
- **Known limits, stated before the run:** 30 clean episodes give wide intervals on criterion 4;
  one sample per call; the reader is the same model as the PM and the attacker; whole-number
  rounding is the only noise on the brief's own numbers.
- **Contamination label of the result:** old episodes contaminated by design; clean episodes
  clean (vendor-stated cutoff).
- **Not in scope:** a reader without memory of the outcome (a local model, or a reader that sees
  only the blinded view); coarser templates; D (paired comparisons), which follows.

### VERDICT
- **Run:** 2026-11-22, EXP-0027 transport, 450 calls, 2.6 million tokens. One attacker call
  (FACTS, episode 17) was refused by the API's safeguards classifier and answered on one retry;
  no canary failures, no tool use. All 90 forms parsed.
- **Results** (FULL / FACTS):
  1. Attacker top-1: 0.444 [0.356, 0.533] / 0.400 [0.311, 0.489], undecided (EXP-0028: 1.00);
     median confidence 25 / 30 (97). Old 0.517 / 0.483, clean 0.300 / 0.233; the 50 largest
     0.571 / 0.486, the rest 0.364 / 0.345. Exact quarter: old 0.50 / 0.43, clean 0.20 / 0.03.
  2. Leak: 0.039 [-0.010, 0.089] / 0.045 [-0.006, 0.095]; no leak detected in either (raw view
     on the same episodes: 0.155 [0.096, 0.217]). The intervals do not exclude a leak of up to
     about 0.09.
  3. Judgements add nothing measurable: FULL minus FACTS leak -0.006.
  4. Signal lost: clean readout minus raw, paired, -0.091 [-0.140, -0.043] / -0.116 [-0.162,
     -0.071], loses in both. Clean accuracy 0.63 / 0.53 against raw 0.77, no-document prior
     0.63, persistence 0.54.
  5. Extraction: reported growth in 0.92 of briefs, segments 0.81, forward indicators 0.53,
     organic growth 0.28, operating-margin change 0.27, full-year revenue guidance 0.17,
     next-quarter revenue guidance 0.06. Of 775 numbers offered with a found quote, 29 were
     dropped because the number was not in its quote.
  6. Demand judgement, up minus down episodes: old +0.30 [0.03, 0.57], clean -0.13 [-0.47,
     0.20].
  Exploratory: on old episodes the PM's readout is 0.595 / 0.589 where the attacker named the
  company and 0.547 / 0.519 where it did not, against clean 0.533 / 0.508: what leak remains
  sits mostly in the recognised episodes.
- **Failure analysis:** (a) the attacker's clues on recognised episodes (read on six) are the
  unnamed segments' revenue shares ("a three-segment split near 72/22/6"; "consumables about 80%,
  then seasonal, home products and apparel"), margin profiles and the size of a stated
  divestiture effect. It recognises old episodes more often than clean ones, which fits
  recognition by remembered figures. (b) The signal loss has a visible cause: releases state
  guidance mostly as dollar ranges, which the form had no place for, so next-quarter guidance
  reached 5 briefs. (Corrected after EXP-0032: the text search behind "about 30 of the 90
  releases" matched mostly reported results; revenue guidance is in about 4 to 6 of them, so
  missing guidance does not explain the loss.) Other content the PM reads in the raw release (tables, the
  narrative) has no field at all.
- **Verdict:** partial. The fixed template does what name-removal could not: recognition falls
  from 90 of 90 to about 40% with low confidence, and the leak falls from 0.155 to an amount the
  test cannot tell from zero. But the brief as built keeps too little: clean accuracy falls to
  the no-document prior (FULL) or a coin (FACTS). Not usable yet; both failures point to the
  template, not to the idea.
- **Next (owner's line, template v2):** take guidance as dollar levels and let code convert them
  to growth against the year-ago quarter as first filed (EXP-0020's series), so no level reaches
  the brief; coarsen segment shares (or drop them) and keep segment growth; add organic growth
  and margins from code where the series has them. Measure the same four quantities on the
  same episodes.

## EXP-0030 — S2-b: does redaction guided by the attacker's own clues stop it? (2026-11-21)

### PRE-REGISTRATION
- **Status:** not yet run. Owner's go-ahead given 2026-11-21 ("第二点的话，我也同意你的建议"); the
  owner adds that the clues collected here are to feed a later, code-only replacement of names,
  people and the like ("积累多了之后，我们再回来优化使用代码方法的这种替换 … 这都是后面的 plan").
- **Claim under test:** if the attacker lists the words that gave a company away and code
  removes them, a fresh attacker no longer names the company.
- **Why the answer is not obvious:** EXP-0028's clues are mostly names a list can remove, but
  some are descriptions ("a warehouse club with twelve-week quarters") and a company's segment
  structure; an earlier loop of this kind in a sibling project still left large companies
  recognised (S2 plan, evidence 2).
- **Sample and scope, fixed here before looking:** the fully blinded views of EXP-0026's 90
  episodes. Three attacks through EXP-0027 with `s2-recall-claude-opus-5-5`: EXP-0028's prompt
  plus up to 20 terms copied from the text, each tagged PERSON, BRAND, PLACE, NUMBER, EVENT or
  OTHER. After attacks 1 and 2, code replaces every occurrence of each listed term (and a
  person's last name) with a placeholder. An episode whose company is not among the three
  guesses leaves the loop and counts as a miss in later rounds. At most 270 calls, about 4.3
  million tokens.
- **Method and baseline:** hit rule of EXP-0028; 90% bootstrap over episodes, seed 20261125.
  Baseline: EXP-0028, 90 of 90.
- **Criteria:**
  1. Top-1 hit rate at the third attack over all 90 episodes: stopped if at most 0.20, not
     stopped if at least 0.50. Also old against clean and the 50 largest against the rest.
  2. The first attack repeats EXP-0028 (top-1 at least 0.90).
  3. Cost of the removals: median share of characters replaced per round.
  4. Share of listed terms found verbatim, and the terms by kind: the catalogue the owner asked
     for.
- **Known limits, stated before the run:** one attack per text, so a single miss can be chance;
  no PM call is made on the redacted texts, so what the removals cost the forecast is not
  measured here; the attacker and the helper that lists terms are the same model.
- **Contamination label of the result:** a recognition measure, not a forecast.
- **Not in scope:** a code-only sanitiser built from the catalogue (later, per the owner);
  rewriting by a model; Sonnet.
- **Deviation, 2026-11-22, before any reply of round 1 was read:** the hit rule also matches
  the company's name after folding case and punctuation, because EXP-0029 showed EXP-0028's rule
  scoring "HP Inc.", "C.H. Robinson" and "PG&E" as misses. Here a false miss would drop an
  episode from the loop and flatter criterion 1.

### VERDICT
- **Run:** 2026-11-22, EXP-0027 transport, 270 calls (three rounds of 90), all with their canary
  and no tool use; 3.9 million tokens.
- **Results:**
  1. Top-1 hit rate at the third attack: 90 of 90 (old 60 of 60, clean 30 of 30, the 50 largest
     and the rest alike). Not stopped. Median confidence fell from 97 to 95 to 93.
  2. The first attack repeats EXP-0028: 90 of 90.
  3. Each removal replaced a median 1.0% of the characters (0.95%, 0.99%; the third list 1.06%).
  4. Terms listed per round: 1,480, 1,468, 1,454; found verbatim 0.98, 0.97, 0.95. By kind, the
     mix moves from names to descriptions: PERSON 129, 19, 8; BRAND 172, 70, 33; OTHER 744,
     1,037, 1,126. Exact quarter: old 1.00 every round; clean 0.93, 0.83, 0.83.
- **Failure analysis:** none of the transport. The round-3 clues (read on seven episodes) are
  segment names and structure ("Individual Retirement, Group Retirement, Life Insurance and
  Institutional Markets"), the company's own reporting style ("Adjusted EBITDA Margin by Business
  Type", "Analysis of Change"), what the company does ("designing, installing, repairing and
  maintaining energy and communications infrastructure"), regulatory markers ("NI 51-101",
  "Sci-Tech Innovation Board") and dated events (an IPO, a COVID-quarter exit from Latin America).
  A few names a 20-term list had not yet reached also survived ("Fortitude Re", "Arcosa").
- **Verdict:** ACCEPT "not stopped". For large and mid-sized companies, removing the words an
  attacker cites does not hide the company: after two removals it still names every one, from
  what the business is and how it reports. This is GY-0000's condition (block a fresh guesser
  on large companies without deleting what the task needs) tested by direct removal, and it
  fails: what identifies these companies is the content a forecaster needs. Clean episodes are
  recognised as well as old ones, so recognising the company needs no memory of the outcome;
  whether recognition turns into outcome knowledge is EXP-0029's per-episode recall question.
- **Consequences:** (a) the term catalogue (4,402 terms, by kind, on the drive) is what the owner
  asked to collect for a later code-only replacement; it says that replacing people and brands is
  necessary and far from sufficient; (b) blinding large companies is not a route to usable replay
  history; the plan's §16 condition for moving weight to strategies C, D and E holds more firmly;
  (c) for small companies, where recall is weaker (EXP-0024 covers only the 250 largest), the
  same loop may end differently and is untested.

## EXP-0029 — S2-b: can the model's own stated reasons show where its call comes from? (2026-11-21)

### PRE-REGISTRATION
- **Status:** owner's go-ahead given 2026-11-21 ("我同意第一点"), after this entry was written;
  started the same day. Script `exp0029_s2b_rationale_audit.py`.
- **Owner's request (2026-11-21, dictated, in part):** "盲化之后，和盲化之前，我们就从各个角度去不断的去问他
  问题。比如说你为什么要这样做，你的原因是什么？要求他有一些结构化的表示，然后他这样的判断必须要能够符合他最终的
  这个判断 … 能不能在这里面去看出来它到底是不是猜到了这个公司，还是 … 在这个原来的数据上有 linkage 出现了".
- **Claim under test:** an audit of the model's stated reasons can tell a call made from the text
  from one helped by knowing the company or the outcome. Ground truth is in hand: on these 90
  episodes the call leans to the realised outcome on old releases (EXP-0026) and the model can
  name the company behind every view (EXP-0028).
- **Why the answer is not obvious:** stated reasons need not be the causes of an answer; the PM
  definition tells the model to use only the text, so it may neither use nor admit memory; or
  it may say plainly that it knows the company.
- **Sample and scope, fixed here before looking:** EXP-0026's 90 episodes (60 old, 30 clean),
  raw view and fully blinded view as built, the same texts. Three calls per text through
  EXP-0027, Opus only: A, 180 calls to the PM definition, the question of EXP-0026 with three to
  six evidence items first (source DOCUMENT, GENERAL or MEMORY; direction; weight 1 to 5; a
  verbatim quote; a claim), then the company it believes it is reading, then the probability.
  B, up to 180 calls to the PM definition with no document, only A's DOCUMENT quotes that code
  finds verbatim in the text. C, 180 calls to the recall definition with the text and A's
  reply: company, quarter, the growth the next quarter went on to show, the probability from the
  text alone and from everything it knows, and which item would flip the answer. About 540
  calls and 6 million tokens.
- **Method and baseline:** readout = probability given to the realised direction; leakage = old
  minus clean, 90% bootstrap over episodes, seed 20261124. Each criterion is reported for the
  raw and the blinded view separately. EXP-0026's readouts on the same texts are the baseline.
- **Criteria:**
  1. *The leak under the structured format.* A's old-minus-clean readout. It reproduces if at
     least 0.10 with the interval above 0. If not, asking for reasons first changed the call,
     which is a finding, and criteria 3 and 5 are then descriptive only.
  2. *Does the answer admit recognition?* Share of A's COMPANY lines that name the company
     (EXP-0028's hit rule). Blinded view: reveals if at least 0.80, conceals if at most 0.20.
  3. *Do MEMORY tags account for the leak?* Share of old answers with a MEMORY item; and the
     old-minus-clean readout among answers with none. Self-report accounts for the leak if that
     gap is under half of criterion 1's; it does not if the gap is at least 0.10 with the
     interval above 0. Reported if at least 20 old answers have no MEMORY item.
  4. *Do the reasons hold together?* Share of quotes found verbatim (flagged under 0.90); share
     of answers whose weighted evidence points the way of the probability; and the
     old-minus-clean gap of the weighted evidence itself, all items and DOCUMENT items only.
  5. *Do the cited passages carry the leak?* B's old-minus-clean readout. Inside the cited
     passages if at least half of A's gap on the same items with the interval above 0; outside
     them if B's interval includes 0 while A's does not.
  6. *Knowledge of the outcome when asked.* Share of C replies that give a next-quarter growth
     figure, how often it lies on the realised side of the reported quarter's growth, and its
     median error, old against clean (clean is the placebo: the outcome postdates the cutoff).
     Linkage: A's readout on old episodes where the recalled direction is right, minus the rest,
     if each group has at least 10.
  7. *Does asking to set memory aside remove the leak?* Old-minus-clean readout of C's
     text-only probability. Removed if the estimate is under 0.05 and the interval includes 0.
- **Known limits, stated before the run:** C is a new call, so it reports what the model can
  know about the text, not what call A used. B loses the tables, so its level is not comparable
  with A's, only its old-minus-clean gap. The blinded view is not blind (EXP-0028).
- **Contamination label of the result:** old episodes contaminated by design; the clean group
  is clean (vendor-stated cutoff) and serves as placebo.
- **Not in scope:** edits to the text that test the stated reasons (a second round, after this
  one shows which reasons are cited); Sonnet; repeated samples; a repaired sanitiser.

### VERDICT
- **Run:** 2026-11-21 to 22, EXP-0027 transport, 540 calls (180 A, 180 B, 180 C), all with their
  canary and no tool use; 5.8 million tokens. Stage A was cut by the account's usage limit after
  29 calls and resumed; failed calls were never recorded, so nothing was answered twice.
- **Results** (old minus clean readout, 90% interval; raw view / fully blinded view):
  1. Leak under the structured format: 0.236 [0.175, 0.298] / 0.179 [0.124, 0.234], against
     EXP-0026's 0.155 / 0.150 on the same texts. Reproduces; reasons-first made the call lean
     further toward the realised outcome, not less.
  2. The COMPANY line names the company in 0.95 of old (1.00 by hand, see failure analysis)
     and 1.00 of clean answers in both views; never UNKNOWN. Reveals, under a definition that says to use only the text.
  3. A MEMORY item appears in 0.97 of old answers in both views (clean: 0.67 raw, 0.90 blinded).
     Only 2 old answers have none, so the gap without MEMORY items cannot be computed. Read by
     hand, many old MEMORY items state the next quarter's result outright ("as I recall,
     third-quarter 2021 revenue fell only about 1%"); clean ones speak of the current quarter or
     the industry.
  4. Quotes found verbatim: 0.99 / 0.99. Weighted evidence points the way of the probability in
     every answer with a direction. The evidence itself carries the leak: weighted lean of all
     items 0.219 [0.136, 0.305] / 0.147 [0.068, 0.227]; DOCUMENT items only 0.175 [0.087, 0.268]
     / 0.084 [0.007, 0.163].
  5. Call from the cited quotes alone (B): 0.170 [0.120, 0.221] / 0.079 [0.027, 0.131], against
     A's 0.236 / 0.179. Raw view: inside the cited passages (at least half of A's gap). Blinded
     view: neither rule holds (under half, interval above 0); partly inside.
  6. Asked outright (C), the model gives a next-quarter growth figure for 0.97 / 0.98 of old
     episodes, on the realised side in 0.98 / 0.95 of them, median error 0.30 / 0.35 points. For
     clean episodes it declines in 0.97 / 0.93. It names every company, old and clean. The
     linkage contrast cannot be computed: only 3 / 4 old episodes lack a right recall.
  7. "Judged from the text alone" (C): 0.137 [0.079, 0.194] / 0.115 [0.063, 0.165]; "using
     everything": 0.307 / 0.271. Not removed: the instruction halves the gap and leaves the rest.
  Exploratory: the item C names as the one that would flip the answer is the top-weighted item
  in 0.96 / 0.97 of answers.
- **Failure analysis:** none of the transport. The hit rule (EXP-0028's) scores three old
  episodes as misses in each view whose COMPANY line is right by hand: "HP Inc." (name forms under
  four letters are skipped), "C.H. Robinson" (key spells "C. H."), "PG&E" (key "Pg&E"). Read by
  hand, criterion 2 is 60 of 60 old in both views. The rule needs punctuation- and case-folding
  before it is reused.
- **Verdict:** ACCEPT, with a split answer to the owner's question. As a detector of recognition
  and outcome knowledge, asking works and is cheap: on old releases the model names the company,
  tags its memory and, asked, recalls next-quarter growth to a third of a point; on clean ones it
  says it does not know. As an audit of the call's cause, the stated reasons are not enough:
  they are verbatim and coherent, yet the document evidence the model chooses and weighs already
  leans toward the outcome it remembers, and asking it to set memory aside leaves about half the
  gap. The leak runs through which true sentences get picked, which no quote check catches.
- **Consequences:** (a) a recall question (C's NEXT_GROWTH) is a per-episode gate that costs one
  call: an episode whose outcome the model can state is not usable as replay; (b) "ignore what
  you know" instructions are not a fix; (c) the edit test this entry left out (change or remove
  the top-weighted DOCUMENT evidence and see whether the call follows) is the next step of the
  audit line, since the flip item is identified in 96% of answers.

## EXP-0028 — S2-b: does the model recognise the company behind a fully blinded release? (2026-11-21)

### PRE-REGISTRATION
- **Status:** not yet run. Owner's go-ahead for this step given 2026-11-21.
- **Claim under test:** EXP-0026 left two readings of why the fully blinded view leans to the
  realised outcome as much as the raw text. Reading 1: the model recognises the company and
  quarter through the blinding. Reading 2: it does not, and old releases are easier to read.
- **Why the answer is not obvious:** the rule attacker identifies every view from ratios
  (EXP-0022), but it holds a database; rationales named the hidden company in 7 of 360 views.
- **Sample and scope, fixed here before looking:** the fully blinded view (names, periods,
  scaling and noise on) of EXP-0026's 90 episodes, the same texts. One call each to
  `s2-recall-claude-opus-5-5` through EXP-0027: 90 calls, about 1.4 million tokens.
- **Method and baseline:** the prompt says names, dates and figures may have been replaced, and
  asks for three company guesses, the quarter end (year and month) and a confidence. A guess is
  a hit if it holds the company's ticker or one of its name forms (the key of EXP-0022). Chance
  is below 1% (1,362 companies). Intervals: 90% bootstrap over episodes, seed 20261123.
- **Criteria:**
  1. Top-1 hit rate on the 60 old episodes. Reading 1 is supported if it is at least 0.50,
     reading 2 if it is at most 0.20; between the two, undecided.
  2. The same on the 30 clean episodes: recognising a company needs no memory of the outcome,
     so a similar rate is expected under reading 1.
  3. On old episodes, EXP-0026's fully blinded readout for recognised (top-1) minus unrecognised
     episodes, with its interval; reported only if each group has at least 10 episodes.
  4. Year named within one of the true year, and the exact quarter end, old and clean.
- **Contamination label of the result:** a recognition measure, not a forecast; old texts are
  contaminated by design.
- **Not in scope:** partial blinding; Sonnet; a line-up; repeated samples.

### VERDICT
- **Pre-registration commit:** none; written minutes before the run, uncommitted with it.
- **Run:** 2026-11-21, EXP-0027 transport, 90 calls, all with their canary and no tool use.
- **Result:** the first guess names the company in 60 of 60 old and 30 of 30 clean fully blinded
  views (median confidence 97 and 95), and the exact quarter end in 60 of 60 and 29 of 30.
  Criterion 1: reading 1, recognised. Criterion 3 cannot be computed: no episode is unrecognised.
- **Failure analysis:** the clues the model cites are in the blinded text. Checked on three
  episodes: the company's own name is gone, but executives ("Benioff", "Roberts"), subsidiaries
  and brands ("Slack" 20 times, "Peacock" 11, "Avanade", "Duck Creek") and unscaled counts
  ("774,000" people) remain. Two causes in EXP-0022: its test for "a common English word" strips
  up to four trailing letters, so "MuleSoft" passes as "mule"; and people are found only next to
  a title in one of three patterns. Brand names that are dictionary words (Slack, Sky, Peacock)
  were a known gap. `check` tested only the company's own name forms and so reported no residue.
- **Verdict:** ACCEPT reading 1. EXP-0026's "fully blinded" view was not blind: its verdict
  stands for the sanitiser as built and says nothing about what thorough name-blinding would do.
  The attacker should have run before the PM calls, as the owner's original pipeline has it; from
  here it is a gate: no view goes to a PM arm until the attacker's hit rate on it is known.

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
- **Added after EXP-0028 (2026-11-21):** the model names the company behind every fully blinded
  view, from brand, subsidiary and executive names the sanitiser left in. Reading 1 holds, and
  the REJECT above is a verdict on EXP-0022's sanitiser, not on name-blinding as such.

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

## EXP-0018 — S1-c calculator, inline rule only: a fair 4B-with-calculator comparator (2026-11-23)

### PRE-REGISTRATION
- **Status:** draft, 2026-11-23. The owner asked why the calculator costs the 4B points
  (EXP-0016: 4C − 4B = −1.3 on B1, −2.8 on B2) and chose to fix the calculator and rerun the 4B
  once EXP-0017 has finished ("修好后重跑"). Approved by the owner 2026-11-23 after EXP-0017's
  verdict ("一 A": approve and commit). Before the commit: the script is
  written (`exp0018_s1c_calculator_inline.py`), its parser cases pass (22 of 22: EXP-0016's inline
  cases unchanged, every chained case now finds nothing), and its scoring was dry-run with 4C's
  test responses standing in for 4I (it reproduces EXP-0016's 4C − 4B figures). No model is run
  before approval, and nothing on a test item before the commit is pushed. EXP-0017's K2 test
  files now exist, so the K2 − 4I re-analysis is computed. Committed and pushed as `45a2899`;
  run 2026-11-23 to 24; verdict below.
- **What was found, post hoc, on EXP-0016's responses.** Claude read the 25 development items
  where 4C and the tool-free 4B disagree. On test, the same comparison was made by program,
  counts only, with the detectors that `mechanisms()` in this experiment's script fixes; its
  `score` recomputes them for 4C, so the counts can be reproduced.
  - 4C against 4B, item by item: B1 43 lost, 22 gained; B2 44 lost, 6 gained.
  - **B2:** 41 of the 44 lost items show the same pattern. A chained call evaluates a line ending
    in `\times 100`, so the value is already a percentage. The 4B then multiplies it by 100
    again, for example 198.9% written as 19,888.9%.
  - The chained rule was added on development to raise the 4B's call rate. On development it
    lowered 4C's B2 accuracy from 89.2 (inline rule only, `dev_v1`) to 87.1; the tool-free 4B
    scores 88.3.
  - **B1:** 40 of the 43 lost items contain a call on a literally wrong unit conversion the 4B
    wrote itself, such as `51,018,000 / 1,000 =`. Tool-free, it writes the right figure after
    the wrong expression. 38 of the 43 add a rounding step after a value is inserted.
  - **The 0.8B:** the chained rule never fired (0 of 3,000 test responses for C-s1 and for
    C-s2, 0 of 600 on development).
  - **Why not a narrower fix:** of 758 chained calls on lines ending in `\times 100`, 384 were
    followed by the 4B multiplying by 100 again and 374 were not. Neither stripping nor keeping
    the factor is right for both, so the chained rule is switched off.
- **Claim under test:** HE1: without the chained rule, the calculator no longer costs the 4B its
  B2 points against 4C. HE2: with the inline rule alone, the 4B with the calculator is
  non-inferior to the tool-free 4B on B2. The literal-conversion cost on B1 is the 4B's own and is
  not addressed; it is reported.
- **Why the answer is not obvious:**
  - Development is small: 240 B2 items, of which 4C lost 6 and gained 3 against the 4B. The
    inline-only run there (`dev_v1`) was ahead by 0.9 on B2, but that is within noise.
  - Switching off the chained rule means fewer calls. On development, B2 calls fell from 96.7% to
    42.5%, so more of the 4B's own arithmetic is back, and that may cost what the fix gains.
  - The B2 test items are mostly the second phrasing (p2); development has only p1.
- **Sample and scope, fixed here before looking:**
  1. **Model.** Qwen3.5-4B, the revision of EXP-0014; no new download.
  2. **Arm.** **4I**: the 4B with EXP-0016's calculator, inline rule only. Same standard prompt,
     greedy, thinking off, at most 512 generated tokens (inserted tokens free), forced answer as
     in EXP-0016. Everything except the rule is EXP-0016's code, imported.
  3. **Test items.** EXP-0016's draw: 3,000 items, SHA-256 of the ids in draw order
     `251720e6cb4727ed5f1bb37927b1312da5276aeb9bdcfbca16bc653937794460`. Comparators are EXP-0016's
     responses for 4B, 4C and C (s1, s2), and EXP-0017's K2 (s1, s2) once scored. None is rerun.
     Section A: EXP-0014's 100 items each of FinQA, CFA-Easy and FinanceIQ.
  4. **Reproduction gate**, before any test item: 4I on the first 50 development items must
     reproduce `dev_v1/4C.jsonl` (made by EXP-0016's code before the chained rule existed) in at
     least 48 of 50 responses, character for character. Otherwise the run stops and the owner
     decides.
- **Criteria** (new family HE; α = 0.0125, as EXP-0014, EXP-0016 and EXP-0017; paired;
  bootstrap over companies, 10,000 resamples, seed 20261123):
  1. **HE1:** Δ = 4I − 4C on B2. Supported if the one-sided test of Δ > 0 rejects (p < 0.0125).
     Refuted if the upper end of the 97.5% interval is at or below 0. Otherwise inconclusive.
  2. **HE2:** Δ = 4I − 4B on B2. Non-inferior if the lower end of the 97.5% interval is above
     −1.5 points (about half the cost EXP-0016 measured). Refuted if the upper end is below −1.5.
     Otherwise inconclusive.
  3. **Mechanisms, descriptive.** Items lost and gained against the tool-free 4B, for 4C and 4I,
     by section and by the four detectors in the script: x100 twice; literal unit conversion;
     extra rounding; cap hit with the answer forced. Fixed here as written in the script.
- **Also reported, descriptive:**
  - 4I − 4B and 4I − 4C on all items and on B1.
  - 4I by section and metric; call rates; forced and invalid rates; EXP-0016's error categories.
  - Section A.
  - **Re-analyses, labelled secondary:** EXP-0016's HC2 with 4I in place of 4C (C − 4I), and
    EXP-0017's HD3 with 4I (K2 − 4I). Both are reported beside the pre-registered verdicts and
    never replace them.
- **What follows from it:** if HE1 holds, 4I becomes S1's 4B-with-calculator comparator from here
  on, including the planned reasoning section (`research/design/s1_reasoning_exam.md`). If not,
  S1 reports against the tool-free 4B.
- **Contamination label of the result:** clean (post-cutoff test companies; no model labels any
  item). Test items reused from EXP-0016 and EXP-0017; this design was chosen after seeing
  EXP-0016's test counts and its development answers, never a test item.
- **Not in scope:**
  - a prompt line telling the 4B that the calculator evaluates exactly what it writes, which
    would address the B1 cost (a possible follow-up);
  - rerunning the 0.8B arms, which the chained rule never touched;
  - a new chained rule;
  - new items.
- **Estimated compute:** reproduction gate about 10 minutes; test about 4.2 hours (4C took 4 h 12 m
  on the same items); section A about 10 minutes. About 4.5 hours, after EXP-0017.

### VERDICT
- **Pre-registration commit:** `45a2899` (pushed before 4I saw a test item). Run 2026-11-23 21:34
  to 2026-11-24 02:18 by `queue`, every step complete: reproduction gate 4 minutes, test 4.1
  hours, section A 35 minutes. Output: `s1/exp0018/scores.json`.
- **Reproduction gate passed:** 50 of 50 development responses identical to `dev_v1/4C.jsonl`,
  character for character (gate 48).
- **Result** (EXP-0016's 3,000 test items, accuracy %; intervals 97.5%, company bootstrap,
  10,000 resamples):

  | Arm | All | B1 (1,650) | B2 (1,350) |
  |---|---|---|---|
  | 4B, no tool | 91.3 | 91.9 | 90.7 |
  | 4C: 4B + calculator, both rules | 89.4 | 90.6 | 87.9 |
  | 4I: 4B + calculator, inline rule only | 90.7 | 90.6 | 90.8 |

  1. **HE1 supported.** 4I − 4C on B2 = +3.0 [+1.9, +4.1], one-sided p < 0.0001. Without the
     chained rule the calculator no longer costs the 4B its B2 points.
  2. **HE2 non-inferior.** 4I − 4B on B2 = +0.1 [−0.2, +0.6]; the lower end is above −1.5.
  3. **Mechanisms**, items against the tool-free 4B: on B2, 4C lost 44 and gained 6 (x100 twice
     in 41 of the 44 lost); 4I lost 2 and gained 4, none with x100 twice. On B1, 4I and 4C are
     identical item for item (the chained rule never fired there): lost 43, gained 22; literal
     unit conversion in 40 of the 43 lost, extra rounding in 38.
- **Also reported:**
  1. 4I − 4B on all items −0.6 [−1.3, 0.0], on B1 −1.3 [−2.4, −0.2]: the B1 cost is the 4B's own
     (it writes a conversion it does not mean), not addressed here. 4I − 4C on all items +1.3
     [+0.9, +1.8], on B1 0.0.
  2. **The fix is in revenue growth:** by B2 metric, 4I (4C, 4B): revenue growth 94.7 (86.1,
     95.0), net margin 95.2 (92.9, 95.2), operating margin 94.1 (94.1, 92.8), gross margin 97.4
     (97.4, 97.4), EPS change 83.4 (83.0, 83.2).
  3. **4I calls the calculator on 47.4% of B2 items** (4C 97.9%; 0.59 calls each against 1.5).
     On the other half the 4B's layout is not caught by the inline rule and it does its own
     arithmetic, as the pre-registration expected; that costs nothing here.
  4. Forced 2.3%, invalid 0.1% (4B 2.3 and 0.1, 4C 3.6 and 0.1). B2 errors of 4I: no call 57,
     wrong setup from excerpt numbers 48, copying or rounding 7, operand not in the excerpt 6,
     sign or unit 4, no number 2. Section A: FinQA 66, CFA-Easy 68, FinanceIQ 50 (4C 65, 68, 49).
  5. **Re-analyses, secondary** (they never replace the pre-registered verdicts): EXP-0016's HC2
     with 4I, C − 4I = −4.0 [−5.7, −2.2] on all items, −11.7 [−14.3, −9.2] on B2 (registered: C −
     4C −2.6). EXP-0017's HD3 with 4I, K2 − 4I = −3.3 [−4.9, −1.7] on all items, −8.6 [−11.1,
     −6.2] on B2 (registered: K2 − 4C −2.0). Both stay inconclusive by their own margins of −3.0,
     but the point estimates now lie beyond the margin.
- **Leakage sign-off:** no model labelled a test item; scripts printed counts and rates only;
  Claude read development responses only. Clean.
- **Verdict:** HE1 supported, HE2 non-inferior. With the chained rule off, the 4B with the
  calculator matches the tool-free 4B on calculations (90.8 against 90.7) and keeps a 1.3-point
  cost on lookups that comes from its own writing. 4I is S1's 4B-with-calculator comparator from
  here on. Against it, the distilled 0.8B with the calculator is 3.3 to 4.0 points behind
  overall and 8.6 to 11.7 behind on calculations; the earlier gaps of 2.0 to 2.6 were flattered
  by the bug.

## EXP-0017 — S1-c calculator distillation: the 4B's answers with the calculator, and more margins and losses (2026-11-22)

### PRE-REGISTRATION
- **Status:** draft, 2026-11-22, from the owner's decisions of that day after EXP-0016: distil
  again with the calculator ("带计算器重新蒸馏"); the values the calculator inserts are left out
  of the training loss; the shift towards margin and loss items is a separate arm; the test items
  are EXP-0016's (a fresh draw was the first choice, but only 145 test items in 38 releases are
  left once EXP-0014's and EXP-0016's releases are removed). Approved by the owner 2026-11-22
  ("批准开始实现"). Before the commit: the script was written (`exp0017_s1c_calc_distillation.py`),
  the masking checked and the label smoke run made (step 4 below, with results). Nothing is run
  on a test item before the commit is pushed. Committed and pushed as `b9f97cd`; run 2026-11-22
  to 23; verdict below.
- **Claim under test:** EXP-0016 found that with the same calculator the distilled 0.8B (C) is
  2.6 points behind the 4B (4C) overall, ahead on lookups (B1) and 8.8 points behind on
  calculations (B2). Its wrong B2 answers now evaluate a wrong expression built from excerpt
  numbers (about 77%: on development, the wrong row, column or periods) or drop the sign of a
  loss (about 18%). D3 was trained on the 4B's tool-free terse answers, which do the arithmetic
  in the text, and on a random 1,850 of 3,457 usable items, of which 6.4% are operating margins
  and 31.3% have a negative answer. HD1: training on the 4B's answers written with
  the calculator, values masked, raises B2 accuracy with the calculator. HD2: at the same number
  of items, a training set shifted towards margins and negative answers raises it further. HD3
  (the owner's question): that model is non-inferior to the 4B with the calculator.
- **Why the answer is not obvious:** the calculator removes the arithmetic, not the reading.
  Labels written with the calculator change how the arithmetic is written, not which row is read,
  so HD1 may find nothing; it may also help, because the teacher no longer spends its terse
  answer on a long division and its expressions become the target. Masking the inserted values
  means the student never sees a loss on them, which matches use but gives fewer trained tokens.
  At a fixed 1,850 items, more margins and losses means fewer of everything else, which may cost
  B1 or EPS change. Two B2 metrics (gross margin, net margin) are held out of training by the
  exam's design, so HD2 can reach them only by transfer from operating margins. And the test
  items are EXP-0016's, on which C and 4C were scored: this direction was chosen from that run's
  error counts and from development answers, not from any test item, but it was chosen after
  seeing those counts.
- **Sample and scope, fixed here before looking:**
  1. **Models.** Student Qwen3.5-0.8B and teacher Qwen3.5-4B, the revisions of EXP-0014. No new
     download.
  2. **Training items.** EXP-0014's 3,596 training items (training companies, pre-cutoff,
     300-token excerpts), with their exam templates. No new item is built.
  3. **Test items.** EXP-0016's draw: 3,000 items, SHA-256 of the ids in draw order
     `251720e6cb4727ed5f1bb37927b1312da5276aeb9bdcfbca16bc653937794460`. C, 4C, D3 and 4B are not
     rerun: their EXP-0016 responses, made by the same calculator code, are the comparators,
     paired on the same items. Section A: EXP-0014's 100 items each of FinQA, CFA-Easy and
     FinanceIQ.
  4. **Checks before the commit**, on training items only (Claude may read them): (a) the
     masking: on 20 labels with a call, the masked tokens are exactly the inserted values; (b) a
     label smoke run of the teacher with the calculator on 100 training items, reporting the
     share correct on the first attempt and the share of B2 labels with a call. If under 50% of
     B2 labels have a call, the owner decides before the commit. **Results, 2026-11-22:** (a) on
     20 labels with a call, the masked tokens decode to exactly the inserted values, 20 of 20; with
     nothing masked, the masked loss equals mlx_lm's default loss on the same batch (0.212184 on
     93 tokens), and three training steps run. (b) 100 training items (the first 100 in the order
     of SHA-256 of `"exp0017-smoke:" + id`): 94% correct on the first attempt (EXP-0014's terse
     labels: 3,270 of 3,596, 91%), 99% on some attempt; B2 labels with a call on the first attempt
     94.4% (34 of 36), B1 21.9%. 1.4 seconds an item, peak 3.0 GiB. No owner decision is needed.
     The smoke run is kept apart (`labels_smoke/`) and not used for training.
- **Method and baseline:**
  1. **Labels.** The 4B answers every training item with EXP-0014's terse prompt, thinking off,
     at most 160 generated tokens, with EXP-0016's calculator (same code, both rules; inserted
     tokens do not count against the cap). As in EXP-0014: greedy first, then up to three samples
     (temperature 0.7, top-p 0.95, seeds 1 to 3); the first correct attempt is kept; dropped if
     none is correct, if it names a year after the item's period, or if prompt and answer pass
     512 tokens.
  2. **Masking.** The answer is tokenised in pieces split at each inserted value; the tokens of
     each inserted value (the space and the number) get no loss. The prompt gets no loss, as in
     EXP-0014. Everything else the teacher wrote, including the `=` before each value and the
     text after it, is trained.
  3. **Arms**, each trained twice (seeds 1, 2), N = 1,850 items, the size of EXP-0014's D3:
     **K1** takes D3's 1,850 items where the new label is kept, then fills from the other kept
     items in the order of SHA-256 of `"exp0017:K1:" + id`. **K2** takes, from the kept items,
     every operating-margin item, then every item whose gold is negative (any metric), then fills
     in K1's order up to 1,850. If margins and negatives pass 1,850, they are taken in K1's order.
     The composition of both sets (by metric, sign and section) is reported. Before labelling,
     1,260 of the 3,596 training items are operating margins or have a negative gold, so K2
     should hold about 1,200 of them; D3's set holds 119 operating margins (6.4%) and 579
     negative answers (31.3%), 33% B2.
  4. **Training** as EXP-0014's D3: full fine-tuning of every block, embeddings frozen, AdamW,
     learning rate 1e-5 with 50 warm-up steps and cosine decay, batch 1, sequences up to 512
     tokens, 2 epochs, a checkpoint at each epoch; the epoch is chosen on the 600 development items
     by accuracy with the calculator, as EXP-0014 chose by tool-free accuracy.
  5. **Evaluation**, every arm with the calculator, as C in EXP-0016: terse prompt, greedy,
     thinking off, at most 160 generated tokens, then EXP-0007's forced answer if no box was
     written. Grading by `exp0010.grade`. An arm's score per item is the mean over its two seeds.
     Intervals: paired, bootstrap over companies, 10,000 resamples, seed 20261122.
- **Criteria** (new family HD1 to HD3; each at α = 0.0125, as EXP-0014 and EXP-0016):
  1. **HD1:** Δ = K1 − C on B2. Supported if Δ ≥ 3.0 points and the one-sided test of Δ > 0
     rejects. Refuted if the upper end of the 97.5% interval is below 3.0. Otherwise
     inconclusive.
  2. **HD2:** Δ = K2 − K1 on B2. Supported if Δ ≥ 3.0 points and the one-sided test of Δ > 0
     rejects. Refuted if the upper end of the 97.5% interval is below 3.0. Otherwise
     inconclusive.
  3. **HD3 (the owner's question):** Δ = K2 − 4C on all items. Non-inferior if the lower end of
     the one-sided 98.75% bound is above −3.0. Refuted if the upper end of the 97.5% interval is
     below −3.0. Otherwise inconclusive.
- **Also reported, descriptive:** every arm by section, metric, seen and unseen template; K1 −
  4C; K2 − K1 and K1 − C on B1 (the shift should not cost lookups); operating margin (trained)
  against gross and net margin (held out); EXP-0016's error categories for K1 and K2 against C,
  with the dropped sign of a loss counted separately; label yield per attempt and the share of
  labels with a call; training loss; forced and invalid rates; seed spread; section A for K1 and
  K2 against C. Claude reads K2's development errors; counts only on test.
- **Contamination label of the result:** clean. The teacher labels training items only (training
  companies, pre-cutoff); no model labels a test item. Test items are reused from EXP-0016, as
  stated above.
- **Not in scope:** more training items or a new data pull; logit distillation; training without
  the mask, or on all 3,457 usable items (each a possible follow-up); tools other than the
  calculator; changing the prompts; rerunning C, 4C, D3 or 4B.
- **Estimated compute:** labels about 1.5 hours (3,596 items at 1.4 seconds, from the smoke
  run); four training runs of about 5 hours each; development about 1 hour (8 checkpoints); test
  about 35 minutes a run, 2.3 hours; section A about 30 minutes. About 25 hours.

### VERDICT
- **Pre-registration commit:** `b9f97cd` (pushed before any model saw a test item). Run
  2026-11-22 12:51 to 2026-11-23 15:45 by `queue`, every step complete: labels 1.5 hours,
  training 5.4 to 5.6 hours a run (peak 8.1 GiB), development 14 minutes a run, test 34 minutes a
  run, section A 3 to 4 minutes a run. Output: `s1/exp0017/scores.json`.
- **Labels and sets.** 3,596 training items: correct on the first attempt 3,317, on a later one
  209, none 70; 33 dropped for passing 512 tokens and 16 for naming a later year; 3,477 kept. K1
  takes 1,847 of D3's 1,850 items (611 B2, 119 operating margins, 579 negative golds); K2 holds
  all 1,225 priority items (703 B2, 228 operating margins, 1,082 negative golds) and has 159
  revenue items against K1's 314. Epochs chosen on development: K1-s1 2, K1-s2 1, K2-s1 2,
  K2-s2 1 (development 87.7, 87.3, 89.3, 89.3; D3 with the calculator was not run on
  development).
- **Result** (EXP-0016's 3,000 test items, accuracy %, two-seed means; C, 4C and 4B are
  EXP-0016's responses; intervals 97.5%, company bootstrap, 10,000 resamples):

  | Arm | All | B1 (1,650) | B2 (1,350) | Seen | Unseen | Seeds (all) |
  |---|---|---|---|---|---|---|
  | C: D3 + calculator | 86.7 | 93.0 | 79.1 | 85.0 | 87.0 | 86.3 / 87.2 |
  | K1: calculator labels, masked | 86.8 | 91.9 | 80.4 | 83.0 | 87.3 | 87.6 / 85.9 |
  | K2: K1 + margins and losses | 87.4 | 91.7 | 82.2 | 83.4 | 88.0 | 88.2 / 86.6 |
  | 4C: 4B + calculator | 89.4 | 90.6 | 87.9 | 84.9 | 90.0 | |
  | 4B, no tool | 91.3 | 91.9 | 90.7 | 86.8 | 92.0 | |

  Forced answers at most 0.2%, invalid 0.0% for K1 and K2. B2 answers with a call 97 to 99%, as
  C.

  1. **HD1 inconclusive.** K1 − C on B2 = +1.4 [−0.7, +3.5], one-sided p = 0.076. Below the
     3-point bar, but the interval reaches past it, so not refuted.
  2. **HD2 inconclusive.** K2 − K1 on B2 = +1.7 [−0.4, +3.9], p = 0.034. Same reading.
  3. **HD3 inconclusive.** K2 − 4C on all items = −2.0 [−3.7, −0.2]. The lower bound is below
     −3.0, so non-inferiority is not shown; the upper bound is above −3.0, so it is not refuted.
     The difference is not zero. By section: B1 +1.1 [−0.8, +3.0], B2 −5.7 [−8.4, −3.0].
- **Also reported:**
  1. **The two steps together do help B2:** K2 − C on B2 = +3.1 [+0.9, +5.4], p = 0.0007; on
     all items +0.7 [−0.6, +2.0]. B1 drops slightly: K1 − C = −1.1 [−2.2, +0.1], K2 − K1 = −0.3
     [−1.6, +1.1]. K1 − 4C on all items = −2.6 [−4.3, −0.9], as C.
  2. **Against the tool-free 4B** (post hoc, same bootstrap; the comparison that does not depend
     on the calculator's bug, below): K2 − 4B = −3.9 [−5.6, −2.3] on all items, −0.2 [−2.0,
     +1.6] on B1, −8.5 [−11.0, −6.0] on B2. K1 − 4B: −4.6, +0.1, −10.2.
  3. **By B2 metric**, K2 against C (4C): operating margin, trained and up-weighted, 89.2 against
     71.1 (94.1); net margin, held out, 84.0 against 58.9 (92.9; 84 items); gross margin, held
     out, 74.4 against 77.7 (97.4); EPS change 78.4 against 77.6 (83.0); revenue growth 87.5
     against 88.5 (86.1). The gain is in the margins whose row is often a loss; gross margin,
     never negative, does not move.
  4. **The dropped sign of a loss is gone:** wrong B2 answers that give the gold's magnitude with
     the wrong sign, C 41 and 43, K1 3 and 2, K2 1 and 3.
  5. **Section A**, 100 items each, seeds 1 / 2: FinQA K1 25 / 21, K2 27 / 20 (C 28 / 27);
     CFA-Easy K1 37 / 12, K2 10 / 9 (C 20 / 13); FinanceIQ K1 23 / 14, K2 11 / 19 (C 28 / 23).
     Untrained 0.8B (EXP-0014's D0): 38, 36, 27. Distilling again costs more of the off-target
     exams, most for K2.
- **Error analysis** (registered categories, B2 test counts; development read by Claude):

  | Wrong B2 answers | C-s1 | C-s2 | K1-s1 | K1-s2 | K2-s1 | K2-s2 |
  |---|---|---|---|---|---|---|
  | total | 285 | 280 | 245 | 283 | 230 | 251 |
  | no call | 9 | 11 | 9 | 19 | 16 | 10 |
  | copying or rounding | 2 | 4 | 5 | 14 | 10 | 11 |
  | sign or unit of the box | 49 | 52 | 15 | 18 | 6 | 11 |
  | wrong setup: operand not in the excerpt | 0 | 1 | 1 | 0 | 0 | 1 |
  | wrong setup: excerpt operands, wrong formula | 225 | 212 | 215 | 232 | 198 | 218 |

  1. **What the new labels fixed is the sign; what is left is the reading.** Sign or unit
     errors fall from about 50 to 6 to 18; wrong setups from excerpt numbers stay at 198 to 232,
     about 85% of what is wrong. B1 lookups wrong without a call rise from 71 and 68 (C) to 80 to
     118.
  2. **On development** (K2-s1 epoch 2 and K2-s2 epoch 1, 64 wrong answers each, 36 and 46 of
     them B2), Claude read 12 wrong B2 answers of K2-s1 and four excerpts. The common failure is
     the column, not the row or the formula: in a table with five quarterly columns, or a quarter
     beside a sequential quarter and nine- or six-month columns, the model takes the sequential
     quarter (Q3 2026 against Q2 or Q1 2026) or the year-to-date columns instead of the same
     quarter a year earlier. Others: the three-month column for a fiscal-year question; two
     columns in different units (millions in one, thousands in the other). EPS change accounts
     for 20 and 23 of the 36 and 46 wrong B2 answers.
- **The comparator is handicapped.** After this run was set up, the owner asked why the
  calculator costs the 4B points; the analysis (EXP-0018's pre-registration) found that the
  chained rule hands the 4B a value already multiplied by 100 and the 4B multiplies again in
  about half of those calls, which neither 0.8B arm ever triggers. A rough count puts 4C about
  2 points too low on all items and 3 on B2. HD3 and K1 − 4C are therefore easier for the 0.8B than they look;
  the tool-free 4B, above, is the fairer reference until EXP-0018 has run.
- **Leakage sign-off:** the teacher labelled training items only (training companies,
  pre-cutoff); test items are EXP-0016's, reused as stated; scripts printed counts and rates
  only. Claude read development answers and training labels only. Clean.
- **Verdict:** HD1, HD2 and HD3 all inconclusive. Labels written with the calculator, values
  masked, and a set shifted towards margins and losses together raise the 0.8B's calculations by
  3.1 points (K2 − C), about the number of losses whose sign C dropped; neither step alone
  clears the 3-point bar. The distilled 0.8B with the calculator is 2.0 points behind the 4B
  with the calculator and 3.9 behind the tool-free 4B: level on lookups, 6 to 8 points behind on
  calculations. What is left is reading the right column of a wide table (the same quarter a year
  earlier, not the sequential quarter or the year to date), which no change of labels has
  touched, and the off-target exams fall further. Next steps go to the owner.

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
