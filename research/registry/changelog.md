# Changelog

Newest first. What changed, why, on what evidence, and what it affects.

## 2026-11-26 — S1 factory: shorter sequences, smaller sizes, plain 4B teacher (owner-approved)

- **What:** the owner approved three changes to the re-plan on 2026-11-26 ("全安推荐", meaning
  "all as recommended"):
  1. Training sequences at most 640 tokens (excerpts about 300 tokens, short teacher chains); F2
     at 2,000 and 8,000 factory examples, one epoch each, in place of 5,000 and 20,000.
  2. Teacher: the plain 4B, batched, arithmetic checked afterwards, in place of 4I; arm T is the
     4B.
  3. The 20% general data: half GSM8K training problems with the released 0.8B's own correct
     answers, half B training items with the 4B's standard answers; no download.
  R1.4 and R1.5 stay held out. Recorded as a dated decision in the re-plan's §4.5.
- **Why:** EXP-0058 measured full fine-tuning at about 405 sequences an hour at 640 tokens and
  262 at 768, and 896 tokens passed the 12 GiB budget; factory items as built ran about 1,300
  tokens. EXP-0056's pilot showed the plain 4B, batched, keeps 52% of samples at about 1,070
  samples an hour, against an untested batched calculator loop for 4I. EXP-0050 scored the 4B
  and 4I level on R (82.0 and 82.2).
- **Evidence:** `s1/exp0058/speed.json`; `s1/exp0056/speed/` and `pilot/verify_report.json`.
- **Assets affected:** re-plan §4.1, §4.2 and §4.5 (superseded where they differ); the main
  pre-registration (EXP-0059) sets exact counts and rules.

## 2026-11-26 — S1 re-plan diagnostics run (EXP-0051); factory steps built; fine-tuning rate corrected

- **What:** EXP-0051 ran (verdict in the registry). By its registered rules: weight averaging
  does not repair C's and K2's lock (best R 25.9 against B0's 55.9), so "+avg" is reported on
  development only and 20% general and B items are mixed into F1 to F3; B0's pass@8 exceeds its
  greedy score by 20 points on the open templates, so F3 stays. Section R v1's builder
  (EXP-0053; escape clause reworded on every template, R1.8 limited to margins within ±100%)
  built train and development items; its probe (EXP-0057) is written, not run. Data factory
  steps 1 to 3 (EXP-0054 to 0056) are written and checked on the releases fetched so far.
- **Correction:** the re-plan's fine-tuning rate (1,260 examples an hour) is wrong; EXP-0017's
  logs give about 680 sequences an hour at 512 tokens, and full fine-tuning at 1,024 tokens
  needs 14.45 GiB, over the 12 GiB budget. The SFT sizes and sequence lengths are reset in the
  main pre-registration (noted in the re-plan, §4.5).
- **Evidence:** `s1/exp0051/scores.json`; EXP-0017's `train_log.json` files; `feasibility.md`.
- **Assets affected:** registry (EXP-0051 verdict; EXP-0053 to 0057); re-plan §4.5; experiments
  README.

## 2026-11-26 — S1 re-plan: distilling financial analysis into the 0.8B (owner-approved)

- **What:** the owner asked (2026-11-25) whether a larger model's way of reading a release and
  reasoning about it can be distilled into a small model that is strong in this one domain
  (verbatim in the re-plan doc), and approved the re-plan on 2026-11-26: "全案推荐来". The four
  decisions, each as recommended:
  1. The rest of S1's window (to 2026-12-15) goes to `research/design/s1_finance_distillation_replan.md`.
     The 4B with the calculator writes step-verified analysis chains over training-company
     releases; students start from the released 0.8B (arms P0, P2B, F1 answers only, F2 chains
     at two sizes, F3 on-policy, +avg). "A framework, not a template" is tested by held-out R
     families, held-out combinations, twins, within-release coherence and a whole-release
     condition table, graded by rule. R-c and R-d as drafted are superseded, C and K2 retired,
     S1-d (layer pruning) and S1-e (expert pruning) deferred beyond the window.
  2. EDGAR pull of training-company earnings releases, 2019 to the cutoff, approved (EXP-0052).
  3. Local open-weight teachers only: Qwen3.5-4B, with the 9B as a pilot.
  4. Two diagnostics before any training (EXP-0051, pre-registered).
- **Evidence:** EXP-0050 (C and K2 learned one answer shape, not a skill) and literature streams
  14a to 14c (61 papers screened, 15 read closely): variety of tasks rather than volume cures
  format specialisation, a close teacher beats a strong one below 3B, on-policy data limits
  forgetting, step-verified chains distil a procedure (DianJin-R1), and below 3.8B nothing is
  known for finance.
- **Assets affected:** re-plan doc (approved); S1 roadmap row; reasoning exam design §6;
  registry (EXP-0051 pre-registration, EXP-0052); experiments README; literature streams 14a to
  14c and their deep notes (not yet merged into `matrix.csv` and `gaps.md`).

## 2026-11-25 — S1 reasoning exam: R-b run (EXP-0050)

- **What:** the five arms on 450 development R base items and 837 twins, with and without hints.
  Plain R score: 4B 82.0, 4I 82.2, untrained 0.8B 55.9, C 0.9, K2 0.7.
- **Finding:** the distilled 0.8B checkpoints box a number on 291 and 300 of the 300 label
  items, in the layout they were trained on, so the R-d gate (4I − K2 = 81.5) passes on format,
  not reasoning. Against the untrained 0.8B the 4B is 26 points ahead on R and 34 on B. No wrong
  gold; R1.7 is at every arm's floor because its escape clause reads as "not stated". Hints help
  the 4B on R1.7 only and do not help the 0.8B. R-c's size rule gives about 9,400 base items.
- **Why it matters:** R-c cannot use C and K2 as trained (floor on every template), and an R-d
  run would need a control for learning the answer format.
- **Assets affected:** registry (EXP-0050 verdict); S1 roadmap row; reasoning exam design §6;
  experiments README. Owner decisions pending: R-c's arms, size and template fixes; R-d.

## 2026-11-24 — S1 reasoning exam: R-b pre-registered (EXP-0050)

- **What:** the headroom step of section R, written as a pre-registration with its script
  (`exp0050_s1r_headroom.py`) and its development draw: 450 base items (50 per template, labels
  balanced as far as the pool allows, 202 companies) and their 837 twins, in three conditions
  (plain, with a one-line hint, twins). Five arms: the 4B with and without the calculator, the
  untrained 0.8B, C and K2. Not yet run.
- **Why:** the owner asked for it after R-a ("A"). R-b decides whether R-d (distillation on R)
  is worth proposing, flags templates whose gold may be wrong, and sizes R-c's test.
- **Decision rules fixed before any model runs:** R-d is put to the owner only if 4I − K2 is at
  least 5 points on the plain R score with its 95% interval above 0 (on B development items the
  same gap is 1.5); a template is checked by hand if the 4B scores below 60 on it or every arm
  misses more than 20% of it; R-c's size comes from the disagreement rate, with the owner
  deciding if it passes 3,000 base items.
- **One change to the prompts:** "final number" becomes "final answer" in each arm's B
  instruction, since most R items want a label.
- **Assets affected:** registry (EXP-0050); S1 roadmap row; reasoning exam design §6; experiments
  README.

## 2026-11-24 — S2: EXP-0048's A1 forecasts made and sealed (interim)

- **What:** 180 A1 forecasts on the October and November 2026 releases (every canary present,
  every probability readable). At the owner's word ("好的") an interim seal before the final one:
  EDGAR was checked for later earnings 8-Ks, 8 companies with a second filing on the same
  September quarter were dropped by the registered rule, and the SHA-256 manifest of the 172
  remaining forecasts is committed in `research/registry/seals/exp0048_manifest.json` (hashes
  only; the forecasts stay on the drive). The push is the time stamp: the December-quarter
  outcomes do not exist yet.
- **Next:** A1C once the October and November calls are collected (about 2026-12-08), then the
  final seal before 2027-01-10.
- **Assets affected:** experiment registry (EXP-0048); `research/registry/seals/`.

## 2026-11-24 — S1 reasoning exam: section R items built (EXP-0019, step R-a)

- **What:** nine multi-fact templates (R1.1 to R1.9) and their twins, generated from the
  EarningsExam releases under the same two-source rule, with 800-token excerpts. Test: 16,329
  base items from 1,548 companies, 40,538 with twins; dev 4,289 (295 companies); train 3,352
  (621). Claude read about 20 train and dev items and found no wrong gold; test counts only.
- **Departures from the design draft:** flip twins swap the two years in the column headings
  (every column stays consistent) instead of editing one figure and its totals; R1.4 does not
  verify the diluted share count.
- **Why it matters:** every template has at least 260 test companies, more than the design's
  target of 1,500 items from 400 companies; labels are unbalanced, so sampling per template is
  fixed in the next pre-registration. Excerpts reach 800 tokens (median 676 on test), so the
  memory check for a 1,024-token training sequence stays a precondition of R-d.
- **Assets affected:** S1 roadmap row; the reasoning exam design (§6); the next step, R-b
  (headroom on dev), to be pre-registered.

## 2026-11-24 — Owner: EXP-0047 and EXP-0048 approved; Loughran-McDonald dictionary downloaded

- **What:** the owner approved the call pilot (EXP-0047) and the prospective arm (EXP-0048), the
  download of a word list for code-scored tone, and committing ("呃，批准，并且资料下载，然后呃也可以
  交替", the last word read as 提交, commit).
- **Download:** Loughran-McDonald Master Dictionary 1993-2025 (CSV, updated March 2026), from the
  link on sraf.nd.edu (a Google Drive file); 9.1 MB, 86,553 words with sentiment flags; SHA-256
  e2d1328682bab7d2187684fb9f5420bb730401c9eefc00daf835edd203f4859d. Stored on the drive at
  `corpora/lexicons/loughran_mcdonald/`, not in git. The page states the lists are free for
  academic research and asks for a licence for commercial use; the owner is told.
- **How it is applied:** EXP-0047 criterion 7 (exploratory, pre-registered before any call text
  is scored): tone of management's prepared remarks against the release, and negative and
  uncertainty shares in management's answers.
- **Assets affected:** experiment registry (EXP-0047, EXP-0048).
- **Same day, after the approval:** EXP-0047's script written (`prepare --dry`: A is EXP-0036's
  A1 prompt verbatim in 58 of 58); it runs when the clean collection ends (about 2026-11-30).
  EXP-0048: the code facts take guidance from EXP-0036's reader, so the reader runs first (at
  most 552 calls instead of 368, recorded before any call); four episodes without release text
  dropped (180 remain); the November series already holds all 180 September quarters, so no
  wait for the December snapshot; reader stage started (180 calls). EXP-0049 (December
  snapshot and series, approved 2026-11-20) written for label coverage. Literature: S2's
  streams 09 to 12 (92 rows) merged into `matrix.csv`.
- **Collection, 2026-11-24 (12:42 local):** 23 requests, all full transcripts. The name test
  flagged two right ones (FNF's possessive, Wabtec's brand name); EXP-0060 fixes the test, and
  EXP-0045's documents rebuilt on it give 76 clean episodes with a full call (from 53). EXP-0050
  to 0059 are S1's, so S2 continues at EXP-0060.
- **Owner, same day ("1 递交 2 学术研究"):** commit the second batch; narrative-lab is academic
  research, so the Loughran-McDonald lists' free academic licence applies.

## 2026-11-24 — S1-c calculator fixed (EXP-0018): the 4B with the calculator is level with the 4B without it on calculations

- **What:** the 4B rerun with the calculator's inline rule only (4I), on EXP-0016's 3,000 test
  items, after a reproduction gate (50 of 50 identical). B2 90.8% against 4C's 87.9% (HE1
  supported, +3.0 [+1.9, +4.1]) and the tool-free 4B's 90.7% (HE2 non-inferior). The B2 items
  lost to the doubled ×100 fall from 41 to 0. The 1.3-point cost on lookups stays: the 4B writes
  unit conversions it does not mean, and the calculator evaluates them.
- **Why it matters:** 4I replaces 4C as S1's 4B-with-calculator comparator. Against it, the
  distilled 0.8B with the calculator is 3.3 (K2) to 4.0 (C) points behind overall and 8.6 to 11.7
  behind on calculations; EXP-0016's and EXP-0017's gaps of 2.6 and 2.0 were flattered by the
  bug (secondary re-analyses; the registered verdicts stand).
- **Assets affected:** S1 roadmap row; the comparator for the reasoning exam (section R).

## 2026-11-23 — S2: daily run unblocked; call texts in one form; drafts of the call pilot and the prospective arm

- **What:** the owner asked that the daily scheduled run need no permission prompt and that work
  go on meanwhile ("能不能怎么改一下，让我们它可以不需要经过确认权限确认……看看还有什么其他可以做的
  啊，不要干等着"). The first scheduled run (16:27 local) had stopped on two prompts and sent
  nothing. The two exact commands are now allowed in the project's local Claude Code settings
  (`.claude/settings.local.json`, kept out of git through `.git/info/exclude`); the task's prompt
  asks for exactly those strings. A hand run at 13:40 UTC was refused by Alpha Vantage: its count
  runs by UTC day or a rolling 24 hours, which the 08:20 UTC schedule fits.
- **Done meanwhile:** EXP-0045 puts call text from both sources into one form (58 clean documents,
  Q&A found in every full transcript); EXP-0046 fixes EXP-0043's next-quarter targets, which had
  taken the quarter before (found before any request; 184 October-November releases, all on the
  drive). Drafts for the owner: EXP-0047 (does the call add to the release, clean quarter, about
  450 calls) and EXP-0048 (prospective arm, sealed before 2027-01-10).
- **Assets affected:** experiment registry (EXP-0044 to 0048); S2 call module.

## 2026-11-23 — Owner: a reasoning exam for S1 (section R), and EXP-0018 approved

- **What:** the owner holds that lookups and arithmetic are what code already does and that an
  LLM's value is in the analyst's logic ("AI 的主要贡献应该是在于这个逻辑思考上面"). Two
  literature streams (13a on financial reasoning benchmarks, 13b on item design) and a design
  draft (`research/design/s1_reasoning_exam.md`) followed. The owner took every recommended
  option: multi-fact calls with rule gold (R1) and twin items (R2) first, a descriptive forecast
  batch (R4) and claim-by-claim analysis (R5) later; excerpts up to about 800 tokens; no
  segments in v1; FinIndices and XFinBench after a licence check; S1 numbers EXP-0019, then
  EXP-0050 to EXP-0059. EXP-0018, the 4B rerun with the calculator's inline rule only, approved
  after EXP-0017's verdict.
- **Why it matters:** S1's question widens from reading and calculating to combining facts. The
  calculator must be fair to the 4B before R is measured with it on, hence EXP-0018 first.
- **Assets affected:** S1 roadmap row; registry Reserved (EXP-0050 to 0059 held for S1); S1 plan
  rule 4 (the 400-token cap) for R items only.

## 2026-11-23 — S1-c calculator distillation (EXP-0017): new labels fix a loss's sign, not the reading

- **What:** the 0.8B distilled again from the 4B's answers written with the calculator, inserted
  values masked from the loss: K1 on D3's items, K2 shifted to operating margins and negative
  answers, two seeds each, tested with the calculator on EXP-0016's 3,000 items. K1 86.8%, K2
  87.4%, against C 86.7%, 4C 89.4% and the tool-free 4B 91.3%. HD1 (K1 − C on B2 +1.4), HD2
  (K2 − K1 on B2 +1.7) and HD3 (K2 − 4C −2.0 [−3.7, −0.2]) all inconclusive. Together the two
  steps add 3.1 points on B2 (K2 − C, p = 0.0007), about the losses whose sign C dropped (C 41
  and 43, K2 1 and 3).
- **Why it matters:** with the same calculator the 0.8B is level with the 4B on lookups and 6 to
  8 points behind on calculations. What is left is reading the right column of a wide table:
  on development the model takes the sequential quarter or the year-to-date columns instead of
  the same quarter a year earlier. Changing the labels did not touch it, and the off-target exams
  (section A) fall further. EXP-0018's analysis found 4C handicapped by the calculator's chained
  rule (about 2 points), so HD3 is easier for the 0.8B than it looks; against the tool-free 4B
  K2 is −3.9 [−5.6, −2.3].
- **Assets affected:** S1 roadmap row; EXP-0018 (its re-analyses use K2's test files); the S1
  reasoning exam draft (`research/design/s1_reasoning_exam.md`), where reading periods across
  columns is template R1.7.

## 2026-11-23 — Owner: Alpha Vantage's free key for call transcripts

- **What:** after EXP-0039's low yield (37 of 190), the owner offered a free-tier Alpha Vantage
  key ("此外我会给你free tier alpha vantage api （25 use per day in US timzeone）") and asked
  for a look at a tool he called "GLOOM CLI" ("GLOOM CLI看起来可能可以直接下载，去试试").
- **Evidence:** Alpha Vantage's documentation lists `EARNINGS_CALL_TRANSCRIPT` (any quarter
  since 2010Q1, by symbol and fiscal quarter) without the "Premium" mark its paid endpoints
  carry. One reply to the documentation's own demo request (IBM, 2024Q1, demo key, none of
  the owner's quota) came back as 37 speaker turns, about 51,000 characters, each turn with
  speaker, title, text and a sentiment score; it carries no call date. No tool called "GLOOM
  CLI" was found by web search; the owner is asked for its name or address.
- **How it is applied:** EXP-0040 (registry, Reserved): one request per clean episode, at most
  25 a US Eastern day, the key in the `nlab` environment as `ALPHA_VANTAGE_API_KEY` set by the
  owner, never in git or a log; replies on the drive only (rule 12).
- **Assets affected:** S2 call module (sample size); experiment registry (EXP-0040 to 0049 held
  for S2).
- **Owner, same day:** gave the key and asked that it be kept locally, unencrypted, out of git
  ("不需要加密，保存在本地，不要git进去"). Stored as `ALPHA_VANTAGE_API_KEY` in the `nlab`
  environment's own settings (outside the repository); the scripts read it from there.
- **First day (EXP-0040, 0041; 25 requests on 2026-11-22 US Eastern):** 15 usable transcripts
  for 16 clean episodes, all among the 250 largest; 14 of the 19 companies without IR text had
  one. Two defects found and fixed forward: EXP-0040's fetch did not pause after validation nor
  skip a repeat (Tesla asked twice); EXP-0041's retry under the calendar year returned the
  previous fiscal year's call for Modine and Flex, caught by reading the opening lines (void).
  EXP-0042 adds a year test and drops retries. Call text now covers 53 of 197 clean episodes.
- **Owner, same day ("都好的"):** yes to collecting the 60 old episodes' calls and the October
  and November 2026 calls of the clean companies (the prospective arm), to a daily scheduled
  run, and to committing. EXP-0043 widens the targets (clean, then 183 next-quarter calls,
  then the old 60; 407 requests left, about 16 days at 25 a day).
- **Same day, later:** Alpha Vantage's daily count does not reset at US Eastern midnight (a
  request at 00:40 Eastern was refused), and its limit message quotes the key, which EXP-0043
  wrote into the drive ledger; redacted at once, and EXP-0044 scrubs it after every run. Daily
  scheduled task "narrative-lab-av-transcripts-daily" at 16:20 local time (08:20 UTC).

## 2026-11-23 — Owner: IR-site transcripts may be used; count 8-K exhibits first; date a call by its release

- **What:** the owner's answers to the IR survey's open points: vendor-copyright transcripts on
  companies' IR sites may be used ("我们完全可以使用官网上的这个供应商版权的 transcript"); count the
  company-written 8-K exhibits first ("可以先从这边数一下八K的附件"); past calls first, dated by
  the release they follow ("我们先看过去的……earning call 一般都是紧跟着这个 earning release 的，所以我们
  可以先用这个去定时间").
- **How it is applied:** transcript files stay on the drive and never enter git (rule 12); a call
  is matched to the earnings release it follows and takes that release's date, with a call dated
  more than three days after its release flagged for a look. The exhibit count is EXP-0037 (cached
  index pages, no network) and EXP-0038 (the exhibits EXP-0037 could not label, 500 largest
  companies only).
- **Assets affected:** data audit §2; skill v1 Part D; S2 plan (call module).
- **Result of the exhibit count (EXP-0037, EXP-0038, same day):** 17 of the 498 largest training
  and development companies furnish call text with any cached earnings 8-K (under 2% of filings;
  8 of the 190 companies in EXP-0036's clean episodes). Too few for a call module; IR-site
  transcripts are the source.
- **Owner, same day ("开始"):** approved collecting IR-site call text for the 190 companies of
  EXP-0036's clean episodes (EXP-0039; about 90 files expected, under 100 MB, drive only) and
  installing `pdfminer.six` in the `nlab` environment to read the PDFs. The question of also
  collecting the 60 old episodes' calls was left open.
- **Collection result (EXP-0039, same day):** 37 of the 190 companies post a full transcript of
  the July or August 2026 call on their IR site or file host (one more only as an 8-K exhibit,
  included), 42 any call text; 53 sites refused the fetch tool and were left alone. Far below the
  survey's half: the survey leaned to the largest companies, and S2's clean companies run to
  rank 500. The call experiment on 38 clean episodes can show only large effects.

## 2026-11-23 — EXP-0036: code facts help the earnings-side calls, not revenue; the brief fails

- **What:** EXP-0036 run (1,118 Opus calls, headless, every canary present). On 197 clean
  episodes the raw release with skill v1's considerations calls revenue acceleration at 0.72
  (code baseline 0.59 on this quarter). Code-stated facts: revenue undecided (+0.006 readout);
  gross margin +0.013, operating margin +0.032, net income +0.013, all passing
  Benjamini-Hochberg at q = 0.10. The facts-and-form brief stops the measured leak (old minus
  clean 0.02) but loses 0.05 to 0.09 readout on every label and is recognised in half the old
  episodes: not a replay input. Exploratory: the reader's "does not recur" tags point the way the
  owner expected (a one-off lift is followed by deceleration in 10 of 12 tags), on few tags.
- **Shortfalls of the frozen script:** criterion 4's interval and the reliability part of Brier
  were not computed; reported as such.
- **Why it matters:** the PM beats code on clean episodes, and facts in code help exactly where
  the model has to find a year-ago base itself (margins, net income). Blinding by rewrite has now
  failed three times (EXP-0031, 0032, 0036) at the same place: signal lost.
- **Assets affected:** experiment registry (EXP-0036 results); S2 analyst skill (Part A earns
  its place for earnings labels); roadmap S2 row.

## 2026-11-22 — IR-site survey: half of 24 S&P 500 companies post full call transcripts

- **What:** at the owner's request, 24 S&P 500 investor-relations sites checked by reading pages
  only (`research/design/s2_ir_transcript_survey.md`). 12 post full transcripts, 3 prepared
  remarks or CFO commentary only, 9 nothing beyond release, slides and webcast. 14 of the 15 that
  post text have it for the July to September 2026 call, so the clean window is covered where text
  exists. Company-written text is sometimes furnished as an 8-K exhibit (NVIDIA's CFO commentary,
  Netflix's letter), with an EDGAR timestamp; vendor transcripts are not.
- **Caveats:** most transcripts are vendor-made (FactSet CallStreet, LSEG, S&P Global) and carry
  the vendor's copyright; posting on an IR site grants no reuse right; collection needs per-site
  adapters, a PDF extractor and a dating rule; coverage is self-selected.
- **Open for the owner:** whether internal research use of such files is acceptable (they would
  stay on the drive, never in git, rule 12); whether to count company-written 8-K exhibits first.
- **Assets affected:** data audit §2; skill v1 Part D.

## 2026-11-22 — Owner: EXP-0036 approved; one-off versus recurring across lines; IR survey

- **What:** the owner approved EXP-0036 at the proposed scale (about 1,100 calls); asked that the
  recurring-or-one-off question cover more than earnings ("不仅仅是盈利 很多方面我们都想看是不是可持续还是
  单次性的 加上"), so EXP-0036 asks four probabilities (revenue acceleration, gross margin,
  operating margin, net income) and its reader tags what recurs by line; asked to check whether
  companies' websites carry past call text ("看看他们网站上有没有既往text") before any transcript
  purchase; agreed to freeze skill v1 without tuning ("同意").
- **Assets affected:** EXP-0036 pre-registration; S2 analyst skill (v1 frozen for EXP-0036);
  data audit §2 (an IR-site survey under way).

## 2026-11-22 — EXP-0035: inventory and contract liabilities add about a point to the base

- **What:** on 22,373 as-filed episodes, inventory growing faster than revenue (+1.0 point of
  accuracy) and contract liabilities growing faster than revenue (+0.7) add to EXP-0034's
  five-lag logistic; together with the other items the bar moves from 0.675 to 0.683 (250
  largest: 0.669 to 0.676, interval reaching zero). RPO, gross margin, non-operating income and
  sector growth add nothing for this label. For earnings-side labels nothing moves accuracy.
- **Why it matters:** the accounting structure carries a small, real signal for the S2 label that
  code can state in a blinded brief; the bar a PM call must clear is about 0.68.
- **Assets affected:** S2 analyst skill draft (Part A4); baselines of EXP-0036 onward.

## 2026-11-22 — Owner: an analysis skill for the S2 PM, built from the literature

- **What:** the owner agreed to template v3 (comparison base and guidance arithmetic computed by
  code and stated in the brief) and asked for more: a reusable analysis "skill" that makes the PM
  read the structure behind the numbers, from an accounting view and from earnings-call language.
  In the owner's words: "你光看这种 headline number、EPS 是涨，但里面是不是可以持续的呢？……比如说今年
  买了某一个股票，然后这个股票 IPO 了赚了钱，像这种东西是不可持续的"; "能不能细节到它这个 inventory
  到底是变快了还是变慢了……从 accounting 的角度去看，其实具体 number 后面有没有什么帮助"; and on calls,
  "它这些 speech 它的这个用词啊、遣词造句啊……尤其是在回答问题的时候……有没有就是规避一些问题啊". The
  owner expects most calls to stay mean reversion or trend following and wants to know what can
  be added on top: "我们希望在这个基础上去找到它能不能额外的去多一些信息".
- **Done:** three literature passes started (streams 10 accounting signals, 11 call language, 12
  structured prompting for forecasts). Census of the 90 EXP-0026 releases: 78 carry a balance
  sheet, 57 mention inventory, 71 receivables, 23 deferred revenue or contract liabilities, 27
  backlog, orders or remaining performance obligations, 20 organic growth.
- **Why it matters:** EXP-0033 found clean calls right for reasons fixed in the release; the
  skill asks whether more of that can be read out, beyond the comparison base (EXP-0034).
- **Assets affected:** S2 plan §6 (inputs) and §8 (labels; earnings-quality items bear more on an
  earnings label than on the revenue label); the transcript data decision (data audit §2).

## 2026-11-22 — EXP-0034: the comparison base calls 65% of acceleration episodes

- **What:** on EXP-0020's as-filed series, "next quarter accelerates if its year-ago quarter grew
  less than this quarter's year-ago quarter" is right on 65% of 22,373 episodes (66% for the 50
  largest companies); a five-quarter logistic regression 67%. EXP-0020 reported 52% as the best
  simple rule because it tried only persistence and reversal; its entry carries a note.
- **Why it matters:** (a) the label is not rule-proof, so the statistical baseline for S2 calls
  is about 0.65, not 0.52 to 0.54; (b) on clean episodes the model's no-document prior (0.64)
  matches the rule, so much of "knowing the company" may be the comparison base, which a blinded
  brief can carry if code computes and states it.
- **Assets affected:** S2 plan §8 and §10 (label rationale, baselines); EXP-0026 to 0033
  verdicts that cite persistence 0.54 as the baseline; the next rewrite template.

## 2026-11-22 — EXP-0033: post-cutoff calls are right for arithmetic reasons, not for the name

- **What:** on the 30 clean episodes, the release adds +0.094 [0.054, 0.132] readout over the
  company name alone (old episodes: nothing). The evidence behind right calls is mostly the next
  quarter's arithmetic that the release already fixes: guidance against year to date, changes
  known to enter or leave next quarter, comparison base and one-offs. Memory is right 68% of the
  time after the cutoff (98% before); wrong calls lean on generic mean reversion and on memory.
- **Why it matters:** it says what a replay input must carry to be worth learning from, and the
  templates of EXP-0031/0032 carried little of it.
- **Assets affected:** the next rewrite template; S2 plan §6.

## 2026-11-22 — EXP-0032: template v2 hides more but still leaks and keeps little signal

- **What:** dropping segment shares lowers recognition to about 30%, but a leak of 0.07 to 0.08
  is detected (pooled over EXP-0031 and 0032's four brief arms: 0.06) and clean readouts stay
  near 0.5. The guidance fix changed nothing because revenue guidance is in only 4 to 6 of the
  90 releases; EXP-0031's verdict, which said about 30, is corrected.
- **Why it matters:** rewriting cuts the leak by about 60% and the clean signal by about 90% on
  these companies; part of the raw signal on clean episodes is knowledge of the company itself.
  Literature pass on rewrite-based blinding written the same day (stream 09, draft, not merged
  into the matrix).
- **Assets affected:** S2 plan §6; EXP-0031 verdict (correction); next templates.

## 2026-11-22 — EXP-0031: rewriting into a fixed template hides most companies but loses the signal

- **What:** the owner's extract-and-rewrite idea, on EXP-0026's 90 large-company episodes: a
  reader fills a fixed form from the raw release, code verifies the quotes and renders one
  template. The attacker names the company in 40 to 44% (from 100%), with median confidence 25 to
  30; the old-minus-clean leak falls from 0.155 to about 0.04, within noise of 0. Clean accuracy
  falls from 0.77 to 0.63 (with the reader's judgements) or 0.53 (facts only).
- **Why it matters:** first S2 transformation that breaks recognition of large companies; its
  loss of signal traces to the form (guidance in dollars had no place; segment shares identify),
  so a second template is the next step. Scope set by the owner the same day: large companies
  (S&P 500) only.
- **Assets affected:** S2 plan §6 (sanitiser levels L3 and L4); EXP-0032, if run, uses the same
  episodes.

## 2026-11-22 — S1-c calculator run (EXP-0016): with the same calculator, the 0.8B is 2.6 points behind the 4B

- **What:** EXP-0014's distilled 0.8B (D3) and the 4B, each with and without a calculator that
  evaluates the arithmetic they write, on 3,000 fresh test items. The calculator lifts D3's
  calculations (B2) from 45.6% to 79.1% (HC1 supported) and overall from 71.6% to 86.7%; the 4B
  scores 91.3% without it and 89.4% with it. C − 4C = −2.6 [−4.4, −0.9]: inside the 3-point
  margin at the point estimate but not at the bound (HC2 inconclusive). The gap shrinks by 17.1
  points (HC3 supported). A second, "chained" recognition rule was added on development, before
  the commit, for the 4B's layout.
- **Why it matters:** the owner's question was whether, with the same tools, the small model
  performs like the large one. On lookups it does (and better); on calculations it is 8.8 points
  behind, and what is left is reading (the right row, column and periods, the sign of a loss),
  not arithmetic. A calculator that evaluates what the 4B writes, not what it means, costs the
  4B 1 to 3 points.
- **Assets affected:** S1 roadmap row; the choice of S1's next step (to the owner).

## 2026-11-22 — EXP-0030: removing the attacker's clues does not hide large companies

- **What:** three attacks on EXP-0026's fully blinded views with two rounds of removing every term
  the attacker cited (about 1,470 terms a round, 1% of the text each time): Opus names all 90
  companies every round, old and clean. Its clues move from people and brands to segment
  structure, reporting style and what the business does.
- **Why it matters:** GY-0000's condition for bringing masking back fails for large and
  mid-sized companies when tested by direct removal; the identifying content is the content a
  forecast needs. Moves S2's weight further toward strategies C, D and E (plan §16).
- **Assets affected:** S2 plan §6 and §16; GY-0000 (evidence, not a change of rule); the term
  catalogue on the drive for a later code-only replacement (owner, 2026-11-21).

## 2026-11-22 — EXP-0029: asking detects recognition; stated reasons do not show the cause

- **What:** on EXP-0026's texts, Opus asked for structured reasons names the company (95 to
  100%), tags memory in 97% of old answers and, asked outright, recalls next-quarter growth of old
  episodes to a median 0.3 points while declining on clean ones. Its quotes are verbatim and its
  reasons agree with its call, yet the document evidence it selects leans toward the remembered
  outcome, and "judge from the text alone" removes only about half of the old-minus-clean gap.
- **Why it matters:** a one-call recall question is a cheap per-episode gate for replay; neither
  self-reported reasons nor an instruction to ignore memory removes the leak.
- **Assets affected:** S2 plan §7 (auditor role); EXP-0030 and later replay arms.

## 2026-11-21 — EXP-0028: every "fully blinded" view is recognised; the sanitiser was not blind

- **What:** asked to name the company behind EXP-0026's fully blinded views, Opus is right on
  the first guess in 90 of 90, with the exact quarter in 89. The blinded texts still hold
  executive, subsidiary and brand names and unscaled counts; two defects of EXP-0022 let them
  through (a too-loose test for common words; narrow patterns for people), and its `check` looked
  only for the company's own name.
- **Why it matters:** EXP-0026's result is explained (the model knew the company in every view)
  and limited: it tests EXP-0022's sanitiser, not thorough blinding. The attacker becomes a gate
  before any PM arm, as in the owner's original pipeline (2026-11-18).
- **Assets affected:** EXP-0022 (to be fixed forward), EXP-0026's verdict (scope note added),
  S2 plan §6 and §7.

## 2026-11-21 — EXP-0026 run: code-only blinding does not change the PM's call

- **What:** 870 calls to Opus, all valid. On old large-company releases the PM's call leans
  towards what happened (readout 0.78 against 0.62 on clean releases), and the fully blinded view
  leans as much (0.77 against 0.62). None of the four switches moves the call by 3 points; a
  wrong name asserted on a blinded release moves it by 11. The registry has the verdict.
- **Why it matters:** wave 1's blinding (pseudonyms, relative periods, scaling, noise at the
  label's tolerance) fails the re-test of GY-0000 as built. Whether that is recognition through
  the blinding or easier old periods is open; the next step is the attacker on blinded views.
- **Assets affected:** S2 plan H1, H2 (not supported), §16; EXP-0026.

## 2026-11-21 — S2: the headless transport leaked session context; isolated (EXP-0027); EXP-0026 started

- **What:** EXP-0026 (blinded views, transplant, prior; 870 calls) is pre-registered and, with
  the owner's go-ahead ("同意"), running. Its first calls came back in Chinese. Cause: `claude -p`
  run inside the repository hands the model the project's auto-memory index (the owner's name,
  "Chinese replies") and the repository's CLAUDE.md, whatever the agent definition says. EXP-0027
  replaces EXP-0025's backend: an empty working directory outside the repository, the definition
  inline, no settings, auto-memory off. Seven calls made before the fix are voided and kept.
- **What remains, by the model's own quotation of its context:** an Agent SDK sentence, the
  account's e-mail address, today's date, the statement of its knowledge cutoff, and the
  working-directory path. These need an API key to remove and are recorded as properties of the
  transport. In particular the model under evaluation knows the date and its cutoff.
- **Assets affected:** EXP-0025's agreement check (made with the leaked context; its conclusion,
  that the two transports give the same accuracy, is unchanged but now carries that caveat);
  EXP-0026; rule 7's headless path, which from here on means EXP-0027's command. Not checked: what
  in-session subagents receive beyond their definition (EXP-0024's replies were in English).

## 2026-11-21 — S2: commercial models may be called headless from a script (rule 7)

- **What:** for sub-study S2, the no-tool agent definitions may be run by a script through the
  Claude Code command line, one fresh process per item:
  `claude -p --agent <definition> --tools "" --strict-mcp-config --no-session-persistence
  --output-format json`, the prompt on standard input. AGENTS.md rule 7 says so. The in-session
  subagent path stays valid. The owner had the command line installed (2.1.330, official
  installer, checksum verified) and logged in on 2026-11-21, and said "好" to the plan.
- **Why:** a subagent cannot read a file, so a prompt the length of an earnings release (about
  13,000 tokens) would pass through the session twice per call; and the session reads what it
  dispatches, which rules out test-side items (S2 plan, decision 5).
- **Evidence (configuration checks, 2026-11-21, no study item):** headless, both
  `s2-recall-claude-sonnet-5-5` and `roster-claude-opus-5-5` report no tool at all (in-session
  subagents report twelve harness tools); the served model matches the definition; overhead is
  about 1,400 tokens a call against 3,900 in session. The system prompt opens with one fixed
  sentence of the Agent SDK before the definition's own text; it cannot be removed and is
  recorded as a property of the transport.
- **Assets affected:** AGENTS.md rule 7; EXP-0025 (the headless backend and its agreement check
  against EXP-0024); S2 plan decision 5, for which this is the scripted path.

## 2026-11-20 — S1-c run (EXP-0014): the teacher helps, but the 0.8B cannot do the arithmetic

- **What:** EXP-0014 ran in full (2026-11-18 22:07 to 2026-11-20 19:12): labels, six training
  runs (D1 to D3, two seeds, two epochs), 3,000 test items for eight configurations, section A.
  Slices in EXP-0015. D3 (taught by the 4B) scores 74.6% against 68.1% for D2 (taught by itself),
  58.9% for D1 (gold only), 60.3% for the untrained 0.8B and 92.7% for the 4B. H1 supported
  (+6.5 [5.0, 8.0]); H2 refuted (−18.2 [−20.0, −16.3]); H3 holds as registered; section A falls
  (FinQA 38% to 10–11% for D3).
- **Why it matters:** the distilled 0.8B matches the 4B on lookups (B1 93.8 against 92.9) but
  scores 48.1% on calculations (B2), below the untrained 0.8B's 61.5%. Most of its wrong B2
  answers set up the right expression and get the division wrong: the terse one-line format the
  owner chose to fit 512 tokens removes the working the student needs.
- **Owner's decisions (2026-11-20, multiple choice):** B2 is to be addressed with a calculator: a
  new arm in which the student writes the expression and Python evaluates it, pre-registered
  separately and reported apart from the tool-free results ("让模型调用计算器"). D4 is dropped: it
  distils the same one-line text and does not address the arithmetic ("不做 D4").
- **Assets affected:** registry EXP-0014 verdict, EXP-0015; roadmap S1 row; experiments README.

## 2026-11-20 — S2-b step 2 run (EXP-0024): Opus recalls next-quarter growth up to its cutoff

- **What:** the closed-book probe, pre-registered as EXP-0024, run with the owner's go-ahead: 210
  prompts to `s2-recall-claude-opus-5-5` through the session (EXP-0023), about 825,000 subagent
  tokens. Before the cutoff the model names the direction of next-quarter revenue growth correctly
  77% to 97% of the time in every bin from 2019 to 2026H1, against 30% after it; for the 50
  largest companies it recalls the growth figure itself to a median 0.06 to 0.23 points. Every
  pre-registered criterion of recall holds, up to the last bin before the cutoff.
- **Why it matters:** two of the plan's §16 conditions are settled. Leakage on raw text for this
  call is large, so S2 has something to remove. Recall is saturated for large and mid-sized
  companies in every old period, so strategy C (use what the model cannot recall) offers them
  nothing; only small companies leave some room. Wave 1's weight returns to measuring blinded
  views (A, B) with the transplant and element effects, which need prompts the length of a
  release.
- **Assets affected:** S2 plan §11 (S2-b steps 1 and 2 answered for Opus), §16; registry EXP-0024.

## 2026-11-20 — S2: pull approved; the plan's fingerprint condition met, and the response

The owner (2026-11-20, verbatim): "同意1 和2， 4不用测忽视". Item 1 was the pull, item 2 the
response below, item 4 the Chinese reading copy of the design, which stays out of git (ignored
locally).

- **What (1), decision 4 of the S2 plan:** the pull of old earnings releases is approved, with
  filing years 2019 to 2025 rather than the plan's 2019 to 2024. 2025 is where recall is expected
  to fade (`gao-2025`, stream 03), and the releases on the drive start in 2026. Drawn by seed in
  EXP-0021: 1,407 releases from 732 training and development companies. The December
  company-facts snapshot of the same decision is approved with it.
- **What (2), the condition in plan §16** ("the rule fingerprint already finds every noised
  view"): met in EXP-0022's development runs. From eight quarters of ratios the nearest-neighbour
  attacker finds 45 of 45 companies at the planned bound of 2 points, dates hidden; one quarter
  of exact ratios finds 80%. The response, amending plan §7 item 5 and §11:
  1. The rule attacker no longer sets the noise bound. The bound is fixed at the label's
     tolerance (0.02 on levels, 2 points on a ratio). Its job is to break recall of exact
     figures, the effect Levy (2026) measured, not to make a company unrecognisable. The
     attacker's hit rate is reported with every view as the floor of identifiability.
  2. The blinded views stay as measured arms (§5, §9 unchanged): what matters is whether the
     model uses what it remembers, and a database attacker is far stronger than a model's memory.
  3. How many quarters of ratios a view shows becomes a factor of S2-c's numeric treatment.
  4. Wave 1's weight moves to strategy C first: S2-b step 2, the closed-book probe on the last
     quarters before the cutoff, which needs no pull, runs before steps 1 and 3. D stays as a
     label variant; E waits for wave 2 as planned.
- **Why:** the owner's decision on the recommendation of 2026-11-20.
- **Assets affected:** S2 plan §7, §11 and §15 (decision 4 settled); EXP-0021 (run), EXP-0022;
  roadmap open decision 9.
- **Also found the same day (EXP-0023):** the "no tools" of the agent definitions does not hold
  in this harness. Subagents from both the roster and the S2 definitions report twelve harness
  tools still offered (artifacts, plugin and skill search, messaging, worktrees, task stop, the
  hand-back); none can read files or the web. The disallowed-tools list of all four definitions
  now names eleven of them (the hand-back is how a subagent returns its answer); a recheck in this
  session still listed them, so either edits load only in a new session or these tools cannot be
  withdrawn by name. Until that is settled, EXP-0023 counts a call only when the harness reports
  that it used no tool. Every subagent call costs about 32,000 tokens before its prompt, which
  sets S2's scale (plan §14).

## 2026-11-20 — Sub-study S2 frozen (v2); its recall definitions created

- **What:** the owner approved S2 design v2 ("同意"). The text is kept verbatim in
  `docs/plans/2026-11-20_substudy_s2_plan.md`; the design file's status line and decision 7 are
  the only edits to it. The two no-tool definitions approved on 2026-11-19 are created:
  `.claude/agents/s2-recall-claude-opus-5-5.md` and `s2-recall-claude-sonnet-5-5.md`. They match
  the roster definitions (model, effort `high`, no CLAUDE.md, the same disallowed tools) except
  for one sentence of the system prompt: "Use anything you know as well as the text in the
  message" in place of "Answer only from the text in the message". Whether they load with no
  tools is checked by `s2a_dispatch check` before any S2 call.
- **Why:** S2-a starts after the freeze.
- **Assets affected:** S2 only. Decisions 4 to 6 of the design (pulls, the test-side run, the
  prospective arm) stay open.

## 2026-11-19 — Sub-study S2 drafted: replaying history without look-ahead

- **What:** a second sub-study, drafted in `research/design/substudy_s2_blind_replay.md` and not
  frozen. A commercial-model PM agent is to learn from pre-cutoff episodes without using what the
  model remembers of their outcomes. S2 compares ways of doing that: masking with numeric noise,
  several noisy views of one episode, selecting episodes the model cannot recall, relative
  questions, and the model as a writer of rules that code applies. The first call studied is the
  direction of next-quarter fundamentals. Three rule changes come with it, approved by the owner
  on 2026-11-19:
  1. S2 is the controlled re-test of GY-0000. AGENTS.md rule 2 and the graveyard entry say so;
     rule 2 is unchanged for the main benchmark and S1.
  2. The commercial part, set aside on 2026-11-14, is reopened for S2 only (roadmap decision 5,
     methodology §2).
  3. S2's attacker and closed-book recall probe run from separate no-tool agent definitions,
     `.claude/agents/s2-recall-claude-*.md`, to be created in S2-a (AGENTS.md rule 7, methodology
     §2).
- **Why:** the owner's request of 2026-11-18, quoted in the draft. Clean post-cutoff data covers
  one labelled quarter; an agent that is to learn from experience needs more history than that.
- **Evidence:** ResearchOS's masking runs (all 15 large caps identifiable; GY-0000). Levy (2026):
  randomising the last digit of each financial-statement item takes GPT-4's earnings-direction
  accuracy from 0.60 to 0.51, chance, while boosted trees lose 0.4 points. The roster system
  prompt says "Answer only from the text in the message", which would bias an attacker towards
  "cannot tell".
- **Literature:** a new stream, `research/literature/streams/08_blind_replay.md` with its CSV: 13
  deep notes in `papers/` and 6 triaged rows; `matrix.csv` now has 105 rows. It changed the draft
  from v1 to v2 on the same day. Leakage is measured by arms assigned by design (what each view
  of an episode shows), a wrong-identity arm as positive control and a post-cutoff placebo, and
  no longer by what an attacker recognised (HindsightBench). Subtracting memory at the output is
  dropped as a strategy: it needs logits. The rule-writer strategy gains three controls and a
  low prior. Spot check: a fresh reviewer re-opened three papers for eight claims; all were
  supported in substance; the count "five of seven" for early cutoffs and one pair of figures in
  the MemTrial note (+0.127 against +0.082 with dates hidden) were not found in the parts
  re-read, and the design does not rest on either figure.
- **Feasibility:** EXP-0020, an engineering run on local archives (registry, Reserved). Among
  four candidate labels only "revenue growth accelerates" leaves a simple rule nothing (base rate
  49%, best rule 52%). 995 labelled episodes are after the cutoff, 37 of them from the 50 largest
  companies; 29,606 are before it, and their releases are not on the drive. Experiment numbers
  EXP-0020 to EXP-0029 are held for S2 so that the S1 and S2 sessions do not collide.
- **Assets affected:** AGENTS.md rules 2 and 7; methodology §2; roadmap status table, open
  decisions 5 and 9 to 11 and the source count; graveyard GY-0000; the experiment registry and
  `research/experiments/README.md`. Nothing of the main programme's or S1's: S2 uses no MLX time
  and no Benchmark v0 gold. No S2 hypothesis is pre-registered, nothing has been pulled from
  EDGAR, no model has been called and no agent definition has been created.

## 2026-11-18 — S1-e: LFM2-8B-A1B downloaded as the candidate MoE

- **What:** of three MoE models surveyed (LFM2-8B-A1B, Moonlight-16B-A3B-Instruct,
  Phi-mini-MoE-instruct; all fit 12 GiB at 4 bits, run on mlx_lm 0.32 and predate the cutoff), the
  owner chose LFM2-8B-A1B (Liquid AI; 8.3B parameters, 1.5B active, 32 experts with 4 routed; LFM
  Open licence v1.0). The `mlx-community/LFM2-8B-A1B-4bit` snapshot `3266a85` (4.86 GiB of weights) is downloaded
  to the external drive, approved 2026-11-18.
- **Why:** OLMoE-1B-7B is at the floor on the exam. OLMoE's own card reports GSM8K 72, so public
  scores do not predict this exam; LFM2 is checked zero-shot on the 600 development items after
  S1-c before S1-e is designed around it.
- **Assets affected:** S1-e and H8; the S1 plan's ladder (§2).

## 2026-11-18 — S1-c pre-registered (EXP-0014); MoE survey for S1-e

- **What:** EXP-0014 pre-registers S1-c for the one pair 4B → 0.8B: arms D0 to D3 (D4 last, if time
  allows), two seeds, full fine-tuning, a 3,000-item test draw (1,360 companies, at most 3 items per
  company), training items rebuilt at 300-token excerpts (3,596 items). Approved by the owner with
  one plan amendment: every arm trains on the same number of items, each drawn from its own kept
  answers. A survey of downloadable MoE models for S1-e (no download) is reported to the owner.
- **Why:** the owner's decisions of 2026-11-18 and the EXP-0011 and EXP-0013 results.
- **Evidence:** the EXP-0014 entry.
- **Assets affected:** S1-c runs on the MLX machine for about two to three days.

## 2026-11-18 — Owner decisions on S1-c's design and on S1-e

- **What:** chosen by the owner from options:
  1. S1-e continues with a different MoE: OLMoE-1B-7B is at the floor. Claude surveys MoE models
     that can be downloaded and fit the 12 GiB budget; any download needs the owner's approval.
     (gpt-oss-20b, already on disk, was offered and not chosen.)
  2. D4 (logit distillation) moves to the end of S1-c, run only if time allows before 2026-12-15,
     and is exploratory. H1 compares D3 with D2.
  3. Two seeds per trained arm, not three (S1-c estimated at about 60 hours instead of 85).
  4. A trained 0.8B is tested with the terse prompt it was trained on; D0 keeps the standard prompt.
  5. The 0.8B student is fully fine-tuned, not LoRA (7.2 GiB at 512 tokens, EXP-0006).
  6. H2 stays as frozen: the best distilled 0.8B non-inferior to zero-shot 4B within 3 points.
  No preference on order: Claude drafts the S1-c pre-registration first.
- **Why:** the EXP-0011 and EXP-0013 results, and the MLX machine's S1 window to 2026-12-15.
- **Assets affected:** the S1-c pre-registration and the S1 plan's compute table.

## 2026-11-18 — Terse teacher probe (EXP-0013); training excerpts capped at 300 tokens

- **What:** asked for a terse worked answer, the 4B scores 89.0% against 93.0% with the standard
  prompt (−4.0, interval [−7.9, −0.3]) and writes a median 53 tokens, but only 37% of its correct
  answers fit a 512-token training sequence. The pre-stated adoption rule fails. The owner chose
  from options: rebuild S1-c training items with a 300-token excerpt cap (about 96% of correct
  terse answers would fit) and label them with the terse prompt, keeping only correct answers.
- **Why:** the prompt, median 488 tokens with a 373-token excerpt, fills the sequence; shortening
  answers alone cannot make room.
- **Evidence:** `research/design/feasibility.md` §7; `s1/exp0013/scores.json` on the drive.
- **Assets affected:** S1-c training items (a 300-token excerpt cap on the train side only; test
  excerpts stay at 400) and the S1-c pre-registration, which records the train/test length gap.

## 2026-11-18 — Owner decisions for the S1-c pre-registration

- **What:** chosen by the owner from options after EXP-0011:
  1. S1-c distils one pair, 4B → 0.8B. 9B → 0.8B also passed the gate but is not run: the 4B is
     as accurate on this exam and labels about twice as fast.
  2. The S1 test set is 3,000 items, which detects about 3.8 points at the registered α and power
     (4,794 would detect 3).
  3. Training items keep 400-token excerpts; the teacher is asked for a terse worked answer (the
     row, the computation, the box), and only correct answers that fit 512 tokens are kept. A small
     development probe first checks the 4B's accuracy holds when terse.
  4. H8 is dropped from S1: OLMoE-1B-7B, the only MoE that fits, is at the floor on both sections.
     The expert-slicing results of EXP-0006 stay as engineering findings.
- **Why:** EXP-0011 verdict; evaluation time before the MLX machine is released on 2026-12-15.
- **Assets affected:** the S1 plan's confirmatory set (H8 removed) and the S1-c pre-registration,
  which records these as amendments to the frozen plan.

## 2026-11-18 — S1-b rerun (EXP-0011): the 4B matches the 9B; 9B → 4B dropped from S1-c

- **What:** on EarningsExam v0.2, thinking off with a 512-token cap, B1 / B2 accuracy: 0.8B
  59 / 54, 2B 79 / 58, 4B 93 / 88, 9B 96 / 87, OLMoE 14 / 8. Every Qwen3.5 rung gained 6 to 18
  points on EXP-0007. 9B → 4B fails the gate (+2.5, interval [−0.5, 5.5] on B1; −1.7 on B2) and is
  dropped from S1-c; 9B → 0.8B and 4B → 0.8B pass by more than 30 points. The 9B is at the ceiling
  on B1. The S1 test size is 4,794, within the pool, above 3,000. EXP-0012 slices the responses.
- **Why:** EXP-0007 measured the exam's sign defect and its 256-token cap as much as the models.
- **Evidence:** the EXP-0011 verdict; `s1/exp0011/scores.json` and `slices.json` on the drive.
- **Assets affected:** EXP-0011's gates replace EXP-0007's for S1-c. Owner decisions before the
  S1-c pre-registration: the teacher (9B or 4B for the 0.8B), the test size, the training excerpt
  cap given correct answers of about 250 tokens, and H8 with OLMoE at the floor.

## 2026-11-18 — EarningsExam v0.2 (EXP-0010); S1-b rerun pre-registered (EXP-0011)

- **What:** v0.2 appends `Use a minus sign for a negative value (a loss or a decrease).` to every
  question and grades a boxed figure in parentheses as negative. Ids, excerpts and gold are
  v0.1's. EXP-0011, pre-registered and approved, reruns S1-b thinking off on the same 600 ids from v0.2, with a
  512-token cap; its gates would replace EXP-0007's.
- **Why:** owner's decisions of 2026-11-18, chosen from options: the sign sentence on every
  template (not only those that can be negative), parentheses read as negative, rerun thinking off
  only, cap 512 (EXP-0007: 256).
- **Evidence:** the EXP-0007 verdict and EXP-0009 slices; `research/design/feasibility.md` §5b.
- **Assets affected:** v0.2 supersedes v0.1 for S1 (the S1-b rerun, and the S1-c test draw and
  training items). v0 and v0.1 stay on the drive.

## 2026-11-18 — S1-b run (EXP-0007): all three S1-c pairs pass the gate; signs need fixing

- **What:** EXP-0007 ran as pre-registered on 600 post-cutoff development items of EarningsExam
  v0.1. Thinking off, B1 / B2 accuracy: 0.8B 50 / 37, 2B 62 / 43, 4B 84 / 72, 9B 90 / 68,
  OLMoE 15 / 10. All three S1-c pairs pass the distillation gate; 9B → 4B only on B1 and at the
  margin (+5.3, interval [1.7, 9.0]). OLMoE is at the floor on both sections. The S1 test size
  comes out at 5,462 (H1/H2) without OLMoE's stand-in, above 3,000 and above the test pool at 3
  items per company, so it goes to the owner. EXP-0009 slices the same responses.
- **Why:** step S1-b of the S1 plan; gates S1-c.
- **Evidence:** the EXP-0007 verdict; `s1/exp0007/scores.json` and `slices.json` on the drive.
- **Found on the way:** 178 of the 600 golds are negative, and only the EPS-change question tells
  the model to use a minus sign. A dropped sign is the largest single error for the 4B and the
  9B, and `parse_number` reads accounting negatives such as `(1,234)` as positive. The 9B → 4B
  pass survives reading parentheses as negative and fails if signs are ignored. Correct teacher
  answers are long (11 to 13% within 128 tokens), and thinking never closes within 2,048 tokens.
- **Assets affected:** the S1-c pre-registration, which needs owner decisions on the test size,
  the sign wording and parsing, the thinking-off cap, and the training excerpt cap or answer
  length. H8 has no usable stand-in while OLMoE sits at the floor.

## 2026-11-17 — EarningsExam v0.1 (EXP-0008); EXP-0007 amended to use it

- **What:** EXP-0008 rebuilds the exam with the v0 generator and one changed rule: an excerpt
  always keeps the table's column-heading line, and an item without one is dropped. 3,805 train,
  3,896 development and 15,739 test items. The EXP-0007 pre-registration is amended before its run:
  its 600 items are drawn from v0.1 development items, by the same rules (318 companies). The v0
  draw is archived, unused. Nothing else in EXP-0007 changes.
- **Why:** the owner's "Fix first, then run": S1 first measures the models on correct items.
  Deliberately noisy or defective items are a possible later sub-study, not part of S1 (owner,
  2026-11-17).
- **Evidence:** `research/design/feasibility.md` §5a; 16 of 16 hand-checked development golds
  right, 10 of them items whose v0 excerpt had lost its heading.
- **Assets affected:** v0.1 supersedes v0 for S1 (S1-b, and the S1-c test draw and training items).
  v0 stays on the drive.

## 2026-11-17 — EXP-0007 held before its run: excerpts can lose their column headings

- **What:** a smoke test of the EXP-0007 script, on pre-cutoff development items outside the
  draw, found an EarningsExam v0 item whose excerpt shows two unlabelled columns: the elision
  removed the line naming the periods, and the gold sits in the second column. A rough count
  (a year, month or quarter label above the first data row): about 19% of development items have
  none, 13% of B1 and 6% of B2. For most the gold is in the first column, so a model can answer
  by the usual layout. For 29 development B1 items (0.7%) it is not, and the item cannot be
  answered. Training items are alike. The 30-item hand check of EXP-0005 did not meet such a case.
- **Why:** found by Claude while checking the scoring path.
- **Evidence:** the smoke item `nCino, Inc.`, net income for the quarter to 2026-04-30, gold
  confirmed by XBRL, excerpt with no period line. The count is a heuristic, not yet checked
  by hand.
- **Assets affected:** EXP-0007 is pre-registered and its draw made, but no model has seen a
  drawn item. The run waits for the owner: run it as registered, or fix the generator forward
  (a new script that always keeps the column-heading lines) and amend the pre-registration's
  sample before the run.

## 2026-11-17 — S1-b pre-registered (EXP-0007)

- **What:** the pre-registration for the S1 headroom run, in the experiment registry. It covers
  600 post-cutoff development items (B1 360, B2 240, at most 2 per company), five models with
  thinking off and the four Qwen3.5 models with thinking on for 300 of them, the forced-answer cue
  at the cap, and scoring by each item's own tolerance. Gates: the 5-point distillation gate per
  S1-c pair, and ceiling and floor per section. Also the formula that sizes the S1 test set, and
  answer lengths to inform the training excerpt cap.
- **Why:** the owner's "Commit, push, draft", then "Approve, commit, run".
- **Evidence:** plan §3 to §5, feasibility §6, learning_ai `FINANCE_MODEL_SELECTION.md` §8.1.
- **Assets affected:** binding for the S1-b run; S1-c's pairs, sections and test size follow its
  gates.

## 2026-11-16 — S1-a compression probes (EXP-0006)

- **What:** EXP-0006 tested the operations S1-c to S1-e rely on. Layer removal on Qwen3.5-4B
  works by whole blocks (three DeltaNet layers and one attention layer) and saves as a stock
  checkpoint. Expert slicing on OLMoE-1B-7B gives the same function as masking the removed
  experts. LoRA and full fine-tuning of the 0.8B, and LoRA on the pruned 4B, fit at 512 tokens
  and not at 1,024.
- **Why:** step S1-a of the frozen plan, after the owner's "Commit, push, go on".
- **Evidence:** `research/design/feasibility.md` §6.
- **Assets affected:** the plan's rule 4 assumed a 400-token excerpt leaves room for a short
  worked answer; it leaves about 70 tokens. The excerpt cap for training items or the length of
  worked answers must be chosen before S1-c is pre-registered. S1-d removes whole blocks. The
  Qwen3 fallback is not triggered. Separately, the cause of EXP-0000's missing step speeds was
  found: `mlx_lm.lora.run` drops the callback it is given (feasibility §4).

## 2026-11-15 — Sub-study S1 plan frozen; EarningsExam v0 built (EXP-0005)

- **What:** the S1 plan v2 is approved and copied verbatim to
  `docs/plans/2026-11-15_substudy_s1_plan.md`. It carries three defaults the owner accepted.
  Thinking is off in trained arms and both modes are measured in S1-b. B3 guidance reading is
  left out of v0. S1 may use the MLX machine until 2026-12-15, after which WP5 has priority until
  EXP-0001 is sealed. EXP-0005 built the exam: 4,420 train, 4,392 development and 18,618 test items.
- **Why:** the owner's "Freeze and start".
- **Evidence:** `research/design/feasibility.md` §5. 30 of 30 hand-checked train and development
  golds are right. Test items were not read.
- **Assets affected:** the S1 design document is now the frozen plan; later changes come here.
  Next are the S1-a probes and the S1-b pre-registration.

## 2026-11-15 — Repo public and pushed; studies reported with reproduction instructions

- **What:** `main` was pushed to the public `origin` (first push, at `8bef4f1`), after a scan
  that found no secrets or licensed text. AGENTS.md rule 13 now says the repo is public and is
  the programme's record; pushes happen only when the owner asks. Rule 4, methodology §8 and the
  ledger README now treat GitHub's push record, not the commit date, as the time stamp. A new
  `reports/` folder sets the format for study reports: findings, what they do not show, and a
  step-by-step guide to reproducing them, with inputs listed by public ID and hash. The README,
  the roadmap (with an S1 row in the status table) and the S1 draft point to it.
- **Why:** the owner confirmed the repo is public and asked for the push. The owner also said
  the repo will host a series of studies, whose results must be reported with instructions for
  reproducing them.
- **Evidence:** none needed; scope decisions.
- **Assets affected:** roadmap decision 4 narrows to whether sealed manifests need a second,
  external stamp. New decision 8: gold test labels stay out of git, so an outside reader cannot
  re-score a test run; how to square that with reproduction must be settled before the first
  report. Commit author metadata carries the owner's own git e-mail address; it is now public.

## 2026-11-15 — Company split v1 fixed

- **What:** `research/experiments/split_v1.py` assigns every company by a salted SHA-256 of its
  CIK: 60% test, 10% development, 30% training. Co-registrants are grouped under their smallest
  CIK. It is frozen and shared by Benchmark v0 and sub-study S1. Methodology §4, the roadmap's
  splits default and the S1 draft cite it.
- **Why:** the owner's decision to fix the split now with a CIK hash. The 60% test share was
  proposed by Claude, against the 50% example given when the owner was asked: clean test pairs
  are the scarce resource, while training draws on years of earlier releases. The share is fixed
  only from today. Nothing has used it yet, so a different share now would cost nothing.
- **Evidence:** EXP-0004 (`data_audit.md` §8a): 2,356 / 399 / 1,160 companies, balanced by filer
  size. About 1,020 to 1,320 corrected numeric test pairs with the later release after the
  cutoff, and 480 to 620 with both after.
- **Assets affected:** every future sample draws through split v1. The both-after test subset
  falls short of 785 pairs until the next season.

## 2026-11-14 — Sub-study S1 drafted; its downloads and EDGAR pulls approved

- **What:** `research/design/substudy_s1_distill_prune.md` (draft v2) plans a sub-study on
  compressing small models for an earnings exam. It covers distillation down the Qwen3.5 ladder
  (9B → 4B → 0.8B), structured pruning of the 4B to about 2B, and expert pruning of a small MoE.
  It is scored on an auto-graded exam built from 8-K releases with rule-and-XBRL gold. Approved
  and started: `mlx-community/Qwen3.5-2B-MLX-4bit`, `mlx-community/OLMoE-1B-7B-0125-Instruct-4bit`,
  one C4 validation shard, and SEC's bulk `companyfacts.zip`, all on the external drive.
- **Why:** the owner's request to start the sub-study, to work from small models, and approval of
  the downloads ("全部批准").
- **Evidence:** S1-a.2 found the Qwen3.5 tokenizers give identical ids, so logit distillation is
  possible. Their chat templates default to opposite thinking modes, so every run sets thinking
  explicitly.
- **Assets affected:** none of the main programme's. S1 must not use Benchmark v0 test gold. Its
  GPU-heavy work waits for the EXP-0001 sealing. The plan is not frozen, and no S1 experiment is
  pre-registered.

## 2026-11-14 — Commercial part set aside for now

- **What:** goal C and every commercial-model run are deferred. Phase 0 (headroom pilot,
  memorisation probe, sealed forecasts) runs local models and baselines only. The no-tool agent
  definitions and the rules for them stay in place, unverified, for when the owner reopens it.
- **Why:** the owner's decision.
- **Evidence:** none needed; a scope choice.
- **Assets affected:** roadmap WP3 items 2 and 5, design default "Goal C", methodology §2. The
  rule that Claude does not label or read post-cutoff test items stays, since Claude may join the
  roster later.

## 2026-11-14 — Commercial models: Claude Opus 5.5 and Sonnet 5.5 as no-tool subagents

- **What:** the commercial side of the roster is Claude Opus 5.5 and Claude Sonnet 5.5, run as
  Claude Code subagents from two no-tool agent definitions in `.claude/agents/` (model ID pinned,
  effort `high`, CLAUDE.md omitted, every tool denied, a two-line system prompt). AGENTS.md rule 7,
  `00_master_methodology.md` §2 and §10, and the roadmap updated.
- **Why:** the owner's decision; it replaces the API key (open decision 5).
- **Evidence:** the Claude models overview lists a June 2026 reliable-knowledge and training-data
  cutoff for both, inside the 2026-06-30 boundary. The Claude Code subagent docs say a custom
  subagent gets only its own system prompt, can pin a full model ID, can skip CLAUDE.md, and loses
  any tool listed in `disallowedTools`. A scan of small open-weight releases since June found none
  that beats the local roster within this machine's limits; releases after the cutoff would move
  the test boundary, so none was added.
- **Not yet verified:** that the definitions load and the subagent really has no tools. Agent
  definitions load at session start, so the check runs first in the next session.
- **Assets affected:** goal C is limited to Claude. The scale of the full run against the owner's
  usage limits is open (WP3 item 5).

## 2026-11-14 — Pair rule for clean test documents

- **What:** a test pair is clean when its later release postdates every roster model's cutoff; the
  earlier release may predate it. Every pair result is also reported on the subset where both
  postdate it, and the earlier release's memorisation is checked item by item.
- **Why:** the owner's decision (roadmap open decision 7).
- **Evidence:** `research/design/data_audit.md` §8: about 1,700 to 2,200 numeric pairs under this
  rule against 800 to 1,000 if both releases had to postdate the cutoff.
- **Assets affected:** `00_master_methodology.md` (contamination labels), roadmap design defaults
  (splits). EXP-0001 and the test-set draw follow this rule.

## 2026-11-13 — Full count of post-cutoff guidance pairs

- **What:** EXP-0003 fetched every earnings release filed after the cutoff (to 2026-11-10) and
  each company's last one before it, 11,073 filings, and counted pairs of consecutive releases with
  keyword rules v2. Results in `research/design/data_audit.md` §8.
- **Why:** the owner chose the full count over working on Item 3.01 first; WP2's gate is that
  usable pairs are counted, not estimated.
- **Evidence:** about 1,700 to 2,200 pairs with numeric guidance in both releases if only the later
  release must postdate the cutoff; 800 to 1,000 if both must. The EXP-0002 extrapolation (1,300 to
  2,800) was in range. Rules v2 over-call words-only guidance by about half, so that stratum still
  needs hand labels.
- **Assets affected:** none built yet. Open decision 7 added to the roadmap (one or both releases
  after the cutoff).

## 2026-11-13 — SEC EDGAR access and first censuses

- **What:** edgartools 5.62.1 installed in the conda env `nlab` (pinned in
  `requirements-nlab.txt`); the owner's SEC identity set there as an environment variable.
  EXP-0002 ran the hard-event census and the guidance census; results in
  `research/design/data_audit.md`.
- **Why:** the owner chose edgartools as the access route and supplied the identity.
- **Evidence:** Item 3.01 runs at 14 to 17% of the earnings-release universe a year, so it is not a
  failure event until split by text (that most are curable deficiency notices is an inference). Releases with guidance in words only are about 8%, so the
  qualitative stratum of plan v2 is thin and needs redefining. The pool of post-cutoff guidance
  pairs is estimated at 1,300 to 2,800 so far.
- **Assets affected:** none built yet. Plan v2's revision 2 (qualitative stratum) and revision 7
  (hard tier) need amending in the research design.

## 2026-11-13 — Plan revised to v2 after the literature review, probes and transcript audit

- **What:** roadmap rewritten as v2 from the plan the owner approved on 2026-11-13
  (`docs/plans/2026-11-13_phase0_plan_v2.md`). Seven revisions: the fine-tuning arm moves from
  Qwen3.5 to models with ordinary attention; the label scheme gets two attributes and four states;
  the L2 anchor moves to the outcome; the labelling gate is on kappa's interval; the statistics are
  tightened; the memorisation probe is redesigned and time stamps must be external; softer failure
  tiers are defined. `00_master_methodology.md` updated to match. Labelling codebook v1 drafted.
- **Why:** the owner asked for a review and replan once the literature review was done.
- **Evidence:** `research/literature/gaps.md` (86 items triaged, 22 deep notes, five-row spot
  check); `research/design/feasibility.md` (EXP-0000: Qwen3.5 LoRA fits only 512 tokens on the 4B
  and 256 on the 9B within 12 GiB); `research/design/data_audit.md` §2 (transcript set: no credible
  licence, ends May 2025, failed companies missing).
- **Struck:** full factorial on Qwen3.5-4B and 9B; L2 only where guidance is numeric; kappa of at
  least 0.8 on 100 items as the reliability gate; the 30-pair narrative-change pilot;
  chronologically consistent models as a clean reference.
- **Assets affected:** none built yet. EXP-0001's design changes before it is registered.

## 2026-11-12 — Programme started; Phase 0 plan approved

- **What:** repo scaffolded. Proposal v0.1 stored verbatim in `docs/proposal/v0.1.md`. The Phase 0
  plan the owner approved stored verbatim in `docs/plans/2026-11-12_phase0_plan.md`. Roadmap v1
  written from it.
- **Why:** the proposal names literature review and research design as the next step, ahead of any
  fine-tuning.
- **Evidence:** a read-only survey of ResearchOS, learning_ai and RE_search; a quick literature
  check (links in the roadmap); an independent design pass that reached the same corpus, first
  task and comparison design.
- **Amendments to proposal v0.1:** five, listed in the roadmap. Proposal v0.2 folds them in at the
  end of Phase 0.
- **Assets affected:** none yet.
