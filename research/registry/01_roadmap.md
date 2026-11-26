# Roadmap

v2, 2026-11-13. Source: the plan the owner approved on 2026-11-13, kept verbatim in
[`docs/plans/2026-11-13_phase0_plan_v2.md`](../../docs/plans/2026-11-13_phase0_plan_v2.md)
(Chinese). It revises v1 (2026-11-12,
[`docs/plans/2026-11-12_phase0_plan.md`](../../docs/plans/2026-11-12_phase0_plan.md)) in the light
of the literature review, the feasibility probes and the transcript audit. Both build on proposal
v0.1 ([`docs/proposal/v0.1.md`](../../docs/proposal/v0.1.md)). Where this file and the approved
plan differ, the approved plan wins until `changelog.md` records an amendment.
**Start every session here.**

## Where the programme stands

| Track | Status |
|---|---|
| WP0 Repo scaffold | Done 2026-11-12 |
| WP1 Literature review | First pass done 2026-11-13: 86 items triaged, 22 deep notes, `matrix.csv`, `gaps.md`. Closed unless a design decision reopens it. One follow-up: de Kok 2025 needs a full read by someone with journal access |
| WP2 Data audit | Access set up with edgartools on 2026-11-13. Done: transcript audit, hard-event census, guidance census (EXP-0002), full count of guidance pairs (EXP-0003), all in `research/design/data_audit.md`. Open: Item 3.01 split by text, fundamentals as filed, delisting-aware returns, consensus |
| WP3 Feasibility probes | Probes 1 and 2 done as EXP-0000 (`research/design/feasibility.md`). Remaining probes wait on WP2 samples, a download decision and an API key |
| WP4 Labelling pilot | Codebook v1 drafted (`research/design/labeling_codebook.md`). Labelling waits on WP2 samples and the owner's time |
| WP5 Sealed ledger | Waits on WP2. Deadline 2027-01-10 |
| Sub-study S1 | Compressing small models for an earnings exam. Plan frozen 2026-11-15 (`docs/plans/2026-11-15_substudy_s1_plan.md`). Downloads done, company split v1 fixed (EXP-0004), EarningsExam v0 built (EXP-0005: 18,618 test items). S1-a probes done (EXP-0006): block removal, expert slicing and healing at 512 tokens all work; the training excerpt cap must shrink or worked answers stay short. Exam fixed forward as v0.1 (EXP-0008: 15,739 test items, column headings kept). S1-b run (EXP-0007, 2026-11-18): all three S1-c pairs pass the gate, 9B → 4B only at the margin; OLMoE at the floor; test size 5,462 goes to the owner. Exam questions do not ask for a sign on losses, the largest single error for the 4B and 9B (EXP-0009). Exam fixed forward as v0.2 (EXP-0010: a minus sign asked on every question, accounting parentheses read as negative). S1-b rerun (EXP-0011, thinking off, 512 cap): the 4B matches the 9B, so 9B → 4B is dropped; 9B → 0.8B and 4B → 0.8B pass by more than 30 points; 9B at the ceiling on B1; test size 4,794. Owner decisions (2026-11-18): distil 4B → 0.8B only, test set 3,000 items, terse teacher answers within 512 tokens, H8 dropped. Terse probe (EXP-0013): terse 4B answers lose 4 points and still do not fit with 400-token excerpts, so training excerpts are capped at 300 tokens (owner). Design settled by the owner (2026-11-18): two seeds, full fine-tuning of the 0.8B, terse test prompt for trained arms, D4 last and exploratory, H2 as frozen; S1-e to switch to another MoE (survey under way). S1-c run (EXP-0014, 2026-11-20): the 4B's terse answers teach the 0.8B 6.5 points more than its own (H1 supported), but the distilled 0.8B matches the 4B only on lookups (B1 93.8 against 92.9) and falls below the untrained 0.8B on calculations (B2 48.1 against 61.5): it sets up the right expression and gets the division wrong (H2 refuted). LFM2-8B-A1B downloaded as the S1-e MoE candidate. Owner (2026-11-20): B2 next through a calculator arm (student writes the expression, Python evaluates), pre-registered separately; D4 dropped. Calculator experiment pre-registered (EXP-0016, approved 2026-11-21): the distilled 0.8B and the 4B, each with and without the same calculator, on a fresh draw of 3,000 test items; Calculator run (EXP-0016, 2026-11-22, fresh draw): the calculator lifts the distilled 0.8B's B2 by 33 points (45.6 to 79.1) and brings it within 2.6 points of the 4B with the same calculator (86.7 against 89.4; HC2 inconclusive at a 3-point margin): ahead on lookups, 8.8 behind on calculations, where its errors are now reading errors (wrong row, column or periods, a loss's sign), not arithmetic; the calculator costs the 4B 1 to 3 points. Owner (2026-11-22): distil again with the calculator. EXP-0017 pre-registered: the 4B's answers written with the calculator, values masked from the loss, one arm on D3's items and one shifted to margins and losses, tested on EXP-0016's items (no fresh releases are left). Distillation with the calculator run (EXP-0017, 2026-11-23): HD1 to HD3 inconclusive; the two steps together add 3.1 points on B2, by fixing a loss's sign; the 0.8B with the calculator is level with the 4B on lookups and 6 to 8 points behind on calculations, where it reads the wrong column of wide tables (sequential quarter or year to date for the year-ago quarter); section A falls further. The calculator's chained rule handicaps 4C by about 2 points (owner asked why); EXP-0018, a 4B rerun with the inline rule only, drafted. Owner (2026-11-23): AI's value is reasoning, not lookups or arithmetic; a reasoning exam (section R) drafted in `research/design/s1_reasoning_exam.md`, literature streams 13a and 13b. Owner (2026-11-23): EXP-0018 approved; section R decisions all as recommended (R1 + R2 first, excerpts to about 800 tokens, no segments, external probes after a licence check, S1 numbers EXP-0019 then EXP-0050 to 0059). Calculator fixed (EXP-0018, 2026-11-24): with the inline rule only, the 4B with the calculator (4I) scores 90.8 on B2, level with the tool-free 4B (HE1 supported, HE2 non-inferior); 4I is the comparator from here on, and against it the distilled 0.8B with the calculator is 3.3 to 4.0 points behind overall, 8.6 to 11.7 on calculations. Section R items built (EXP-0019, 2026-11-24): test 16,329 base items from 1,548 companies, 40,538 with flip, hold and mirror twins. R-b run (EXP-0050, 2026-11-25): on development R items the 4B scores 82 (with or without the calculator), the untrained 0.8B 56, and the B-distilled 0.8B (C, K2) under 1, because it boxes a number where a label is asked; the R-d gate passes by its rule on that format failure. Against the untrained 0.8B the 4B is 26 points ahead on R (34 on B). No wrong gold; R1.7's question sends every model to "cannot be determined". Hints do not help the 0.8B. R-c's size rule gives about 9,400 base items. Re-plan (owner, 2026-11-26, "全案推荐来"; `research/design/s1_finance_distillation_replan.md`): the rest of the window distils a verifiable analysis framework from the 4B into the released 0.8B through a data factory over training-company releases, with transfer to held-out R families, twins and within-release coherence as the test of a framework; R-c and R-d superseded, C and K2 retired, S1-d and S1-e deferred beyond the window, local open-weight teachers only. EXP-0052 pulls 40,266 training-company releases (2019 to the cutoff, started 2026-11-26); EXP-0051 run: weight averaging does not repair C's and K2's lock (+avg on development only, 20% general and B mix), and on-policy has 20 points of room (F3 stays). Section R v1 built for train and development (EXP-0053; probe EXP-0057 written); data factory steps 1 to 3 written and checked (EXP-0054 to 0056). The re-plan's fine-tuning rate was wrong (about 680 sequences an hour, not 1,260), so SFT sizes are reset in the main pre-registration. Next: the teacher speed check and pilot, the R v1 probe, and the main experiment's pre-registration. S1 may use the MLX machine until 2026-12-15 |
| Sub-study S2 | Replaying history to a commercial-model PM agent without look-ahead. Plan v2 frozen 2026-11-20 (`docs/plans/2026-11-20_substudy_s2_plan.md`); no hypothesis pre-registered. It is the controlled test of GY-0000's condition for bringing masking back, and it sets masking beside other ways of using pre-cutoff history (several noisy views of one episode, selecting episodes the model cannot recall, relative questions, the model as rule writer). Literature pass: `research/literature/streams/08_blind_replay.md`. The commercial part is reopened for S2 only (owner, 2026-11-19). First feasibility run done (EXP-0020, local archives only): the label is "revenue growth accelerates" (base rate 49%, best simple rule 52%); 995 labelled episodes after the cutoff on the training and development side, 37 from the 50 largest companies; 29,606 before it, whose releases are not on the drive. Recall definitions for the attacker and probe created (`.claude/agents/s2-recall-claude-*.md`; they load in a new session). Old releases pulled (EXP-0021: 1,386 press releases, 2019 to 2025). Sanitiser written and tried on 48 development episodes (EXP-0022): its rule attacker finds every company from eight quarters of ratios at the planned noise bound, dates hidden, which is the plan's §16 condition for moving wave 1's weight to strategies C, D and E. Owner, 2026-11-20: pull approved (2019 to 2025); noise fixed at the label's tolerance and the attacker reported, not used as a gate; strategy C first. Closed-book probe run (EXP-0024, 210 calls to Opus through the session): the model recalls next-quarter revenue growth of large and mid-sized companies, often to a tenth of a point, in every period from 2019 to the cutoff, and not after it; strategy C offers those companies nothing. Headless transport built and isolated (EXP-0025, EXP-0027). Blinded views run (EXP-0026, 870 calls): the call leans to the realised outcome on old releases (readout 0.78 against 0.62 on clean ones) and as much when fully blinded; a wrong asserted identity moves it by 11 points. Attacker run (EXP-0028): Opus names the company behind every fully blinded view, from brand, subsidiary and executive names the sanitiser left in, so EXP-0026 tested that sanitiser and not thorough blinding; the attacker is now a gate before any PM arm. Rationale audit (EXP-0029): asked, the model names the company, tags memory and recalls next-quarter growth of old episodes to 0.3 points while declining on clean ones, so one recall question is a cheap per-episode gate; its stated reasons are verbatim and coherent but its chosen document evidence already leans to the remembered outcome, and "text alone" leaves half the gap. Clue-guided removal (EXP-0030): after two rounds the model still names all 90 companies from segments, reporting style and business description, so blinding large companies fails GY-0000's condition. Owner, 2026-11-22: large companies (S&P 500) only. Extract-and-rewrite into a fixed template (EXP-0031, the owner's idea): attacker top-1 falls to 40 to 44%, the leak to about 0.04 (not distinguishable from 0), but clean accuracy falls from 0.77 to 0.63 or 0.53, mostly because guidance stated in dollars had no place in the form. Template v2 (EXP-0032): recognition about 30%, but a leak of 0.07 to 0.08 remains and clean readouts sit near 0.5; revenue guidance is rare in these releases. Pooled, the rewrite briefs cut the leak by about 60% and the clean signal by about 90%. Literature pass on rewrite-based blinding: stream 09 (draft). What makes a clean call right (EXP-0033, existing records): the release adds 0.09 over the company's name alone after the cutoff and nothing before it; memory points the right way 98% of the time before the cutoff and 68% after; right calls rest mostly on next-quarter arithmetic the release already fixes (guidance less the year to date, FX turning, deals annualising) and on comparison-base or one-off effects. Code-only base check (EXP-0034): "the comparison base gets easier" (g(t-3) < g(t-4)) calls 65% of 22,373 episodes and a five-lag logistic 67%, against 52% for EXP-0020's best rule, so the statistical bar is about 0.65; on the clean episodes it matches the model's name-only prior (0.64). Owner, 2026-11-22: agreed to template v3 (code-stated base and guidance arithmetic) and asked for an analysis skill that reads the accounting structure behind the numbers (one-offs, inventory, receivables) and earnings-call language (evasive answers); literature passes done (streams 10 accounting signals, 11 call language, 12 structured prompting; drafts): prompt structure barely moves forecast accuracy and reasons-first adds bias, so the skill is mostly code-stated facts and a quote-checked reader form (`research/design/s2_analyst_skill.md`, draft v0). Accounting screen (EXP-0035, code only): inventory and contract liabilities growing faster than revenue each add about a point to the base logistic (bar about 0.68); RPO, gross margin, one-offs and sector growth add nothing for this label. Owner, 2026-11-22: EXP-0036 approved with four labels and recurrence tagged by line; skill v1 frozen; IR-site survey (12 of 24 S&P 500 sites post full call transcripts, mostly vendor-made). Skill v1 on clean episodes (EXP-0036, 1,118 calls): the raw release with the skill's considerations calls revenue acceleration at 0.72 against 0.59 for code on this quarter; code-stated facts leave revenue undecided and help gross margin, operating margin and net income (+0.01 to +0.03 readout); the facts-and-form brief stops the measured leak but loses 0.05 to 0.09 readout, the third rewrite brief to fail on signal. Call text: 8-K exhibits too rare (EXP-0037/0038); IR sites give 37 of 190 clean companies (EXP-0039); Alpha Vantage's free key, 25 requests a day, collects the clean, next-quarter (Oct to Nov 2026, prospective arm) and old episodes' calls through about 2026-12-09 (EXP-0040 to 0043). Drafts awaiting the owner: EXP-0047 (call pilot on the clean quarter, after about 2026-11-30) and EXP-0048 (prospective arm, sealed before 2027-01-10). S2 uses no MLX time; its scarce resource is Claude usage |
| WP6 Research design v1.0 | Waits for WP1 to WP5 |

The repo is public and `main` has been pushed to `origin` since 2026-11-15. Every finished study
is reported under `reports/`, with instructions to reproduce it.

## North star

Learn what works, for which task, under which data and compute limits, and why: for a specialised
research task, where should capability live, in the weights, the prompt, the retrieved context or
the tools? Financial narrative understanding is the test bed and equity failure detection is the
application. The proposal does not presume alpha, and neither does this roadmap.

Head-to-head results expire with model versions. The asset that lasts is a benchmark that gains a
fresh batch of clean, post-cutoff items every earnings season.

## What Phase 0 has established so far

| Finding | Kind | Where |
|---|---|---|
| No public benchmark labels guidance revisions across consecutive quarters | Hypothesis, not refuted by a targeted search | `research/literature/streams/04_benchmarks.md` |
| No study scores LLM extraction of guidance tuples or revision classes against gold labels | Hypothesis, not refuted | `research/literature/streams/02_llm_signals.md` |
| No head-to-head of prompting, retrieval, fine-tuning and tools on financial narrative tasks, small open-weight against commercial | Hypothesis, not refuted; one candidate paper could not be opened | `research/literature/streams/05_adaptation.md` |
| Changes in disclosure text carry more than levels; dictionary tone is a weak baseline | Empirical finding (literature) | `research/literature/streams/01_text_analysis.md` |
| Numeric EPS guidance is about 5% of forward-looking sentences in earnings releases; under uncertainty firms drop numbers and say more in words | Empirical finding (literature) | `research/literature/papers/bozanic-2018-other-forward-looking-statements.md` |
| Masking leaves 31 to 70% of transcripts re-identifiable and removes signal; recall of pre-cutoff facts fades well before the stated cutoff | Empirical finding (literature) | `research/literature/streams/03_lookahead.md` |
| Whole documents fit for local inference: a 32k-token prompt peaks at 4.75 GiB on Qwen3.5-4B and 6.99 GiB on the 9B | Empirical finding (EXP-0000) | `research/design/feasibility.md` §1 |
| LoRA on Qwen3.5 fits only 512 tokens (4B) or 256 (9B) within 12 GiB; Gemma 4 12B reaches 2,048 and DianJin-R1-7B 4,096 | Empirical finding (EXP-0000) | `research/design/feasibility.md` §2 |
| The Hugging Face transcript set has no credible licence, ends in May 2025 and lacks failed companies | Verified from its card and viewer | `research/design/data_audit.md` §2 |
| The plan's sample-size arithmetic holds if two systems disagree on at most 15% of items | Re-derived | `research/literature/streams/07_statistics.md` |
| Post-cutoff pairs of consecutive earnings releases with numeric guidance in both: about 1,700 to 2,200 if only the later release postdates the cutoff, 800 to 1,000 if both do (as of 2026-11-10) | Counted on all filers; corrected by a 30-item hand check | `research/design/data_audit.md` §8 |

What was known before Phase 0 (ResearchOS results, local model measurements, storage, the public
GitHub repo) is in the v1 plan and in `feature_evidence.md`.

## Amendments to proposal v0.1

From v1, still standing:

1. **Decide first what may be claimed.** L1 is confirmatory. L2 is tested against an anchor. L3 is
   exploratory. See `00_master_methodology.md` §1.
2. **Phase I builds one task family: guidance revision.** Softer constructs enter the benchmark
   only after a labelling pilot shows one annotator can label them reliably.
3. **Phase 0 is three parallel lines plus one deadline**: sealing forecasts before the results that
   follow the 2026 third-quarter reports arrive in mid-January 2027.
4. **Goal B's core evidence comes from a factorial experiment on open-weight models.**
5. **Time, not masking; and a rolling benchmark.**

Deferred, not dropped: tasks on earnings call transcripts, return prediction, internal-
representation analysis, model routing and hybrids, integration into ResearchOS, and a pilot of
the narrative-change task.

## Revisions in v2

Each is traced to its evidence in `research/literature/gaps.md` or
`research/design/feasibility.md`.

1. **The fine-tuning arm changes base model.** ~~Full factorial on Qwen3.5-4B and 9B~~ — STRUCK
   (EXP-0000). The factorial runs on two models with ordinary attention: Qwen2.5-7B-Instruct and
   Gemma 4 12B. Qwen2.5-7B-Instruct needs a download of about 5 GB and the owner's say-so; until
   then only Gemma 4 12B, which is on disk. Its LoRA feasibility was measured on its derivative
   DianJin-R1-7B, which becomes the like-for-like "domain-trained by someone else" reference.
   Qwen3.5-4B and 9B stay, running the 12 cells without fine-tuning, as the commercial models do.
   Training items are capped at 2,048 tokens. The 12 GiB budget stays.
2. **The label scheme.** A revision has two attributes, direction and range width, plus four
   states. Announced withdrawal is separate from silent dropping. Metrics go beyond EPS.
   Qualitative guidance is a core stratum. Minimal pairs get unedited controls. Two baselines are
   added. Details in `research/design/labeling_codebook.md`.
3. **The L2 anchor sits on the outcome.** ~~L2 only where the guidance is numeric~~ — STRUCK
   (Bozanic 2018). Qualitative guidance enters L2 too, checked against the next quarter's as-filed
   figure for the same metric, stratified by the size of the change.
4. **Labelling gates.** ~~Test-retest kappa of at least 0.8 on 100 items~~ — STRUCK (stream 07).
   The gate is on the lower bound of kappa's interval, with raw agreement and AC1 reported beside
   it. A sample of extractions that models found and gold lacks is adjudicated. ~~30 pairs of
   narrative change in the Phase 0 pilot~~ — STRUCK: 30 pairs cannot decide anything; the task gets
   its own 100-pair pilot after Benchmark v0.
5. **Statistics.** Test-set size comes from the pilot's disagreement rate. Confirmatory contrasts
   are named in advance and corrected with Holm. Cluster by company; quarter is a stratum.
   Interactions come from an item-level mixed logit, by stratum. Goal C is tested below the
   ceiling with its power stated. The fine-tuned level is trained on the prompt format of its
   cell. Checkpoint selection and LoRA search count as development evaluations.
6. **Memorisation probe and time stamps.** The probe is redesigned (methodology §9). An item-level
   test of whether recall inflates extraction accuracy is added. Registrations and sealed manifests
   need a push or an external time stamp. Commercial-model results are "clean (vendor-stated
   cutoff)". ~~Chronologically consistent models as a clean reference~~ — STRUCK (stream 03).
7. **Failure tiers.** The four 8-K items stay as the hard tier, counted by sub-item with company
   denominators. Softer tiers are defined for pre-registration. The structured bar is the
   eight-variable hazard model. EXP-0001 states expected event counts.

## Phase 0 — remaining work

Phase 0 trains no model that will be evaluated. Target: design frozen by the end of December
2026, and forecasts sealed before 2027-01-10. Both dates assume the SEC contact string arrives in
the week of 2026-11-16; the 14-day gap between labelling rounds otherwise pushes the freeze into
January.

### WP2 — Data audit

**Research direction.** Establish what data can be had, with what point-in-time and survivorship
properties, under what licence.

**Plan.**

| Need | First choice | What to verify |
|---|---|---|
| Disclosure text: 8-K earnings press releases, 10-Q, 10-K | SEC EDGAR | Acceptance timestamps, exhibit parsing, rate limits |
| Fundamentals as filed | SEC XBRL company facts | First-filed values; handling of restatements |
| Failure events | 8-K items 1.03, 3.01, 4.02, 2.06 | Bulk availability; counts by sub-item, with company denominators |
| Returns including delisted stocks | Open | Coverage and cost. The eight-variable baseline needs daily prices for delisted companies |
| Consensus estimates | Bulk sources are mostly paid | If unavailable, the "earnings downgrade" endpoint becomes realised fundamentals |
| Earnings call transcripts | Done: private secondary layer at most | Post-cutoff transcripts need a paid API ($60 to $149 a month) |

Two censuses decide whether the benchmark is feasible:

- Guidance census: 50 companies by 8 quarters. Count the share of releases with numeric guidance,
  the share with only qualitative guidance, the mix of change types, and each company's updating
  routine.
- Hard-event census: filings of each sub-item after 2026-06-30, with the number of companies as
  denominator.

**Guardrails.** No EDGAR request until the owner has chosen the contact string. Nothing pulled goes
into git.

**Deliverables.** The remaining sections of `research/design/data_audit.md`.

**Gate.** Usable document pairs are counted, not estimated.

### WP3 — Feasibility probes

**Research direction.** Measure what this machine and the candidate models can do before the
design assumes it.

**Plan.**

1. LoRA on Qwen2.5-7B-Instruct at 1k, 2k and 4k tokens, once downloaded.
2. Headroom pilot on 100 document pairs, starting with the qualitative-guidance stratum: keyword
   rules, pair similarity plus dictionary tone change, Qwen3.5-4B and 9B, Gemma 4 12B, DianJin.
   The Claude models are left out for now (owner, 2026-11-14). Pass conditions go into the registry before the run. It also gives the
   disagreement rate that sizes the test set.
3. Memorisation probe, as redesigned in `00_master_methodology.md` §9.
4. Structured-output compliance, verbatim hit rate of evidence quotes, tool-call reliability.
5. DEFERRED (owner, 2026-11-14: the commercial part is set aside for now). Usage per item for the Claude part, and whether the full run fits the owner's subscription or
   needs a scripted path. First check, in a new session: the two no-tool agent definitions load,
   and the subagent reports no tools.

**Guardrails.** One MLX job at a time, within 12 GiB. No model is downloaded without the owner's
say-so. No more than three research agents in parallel: eight at once exhausted the usage
allowance on 2026-11-12.

**Deliverables.** The remaining sections of `research/design/feasibility.md`.

**Gate.** Phase II fits a stated compute and API budget.

### WP4 — Labelling pilot

**Research direction.** Show that one annotator can label guidance revisions reliably.

**Plan.** The owner reviews codebook v1. Then 100 guidance pairs are labelled twice, 14 days
apart, in a different order and blind to the first round.

**Guardrails.** No roster model labels or pre-labels these items. A rule-based parser may propose
tuples.

**Deliverables.** Codebook v1 as revised; both rounds of label files, outside git; agreement
computed by script.

**Gate.** Set before round 1. Suggested: lower bound of the 95% interval for kappa at least 0.7 on
each attribute, and rule-against-human agreement at least 90%.

### WP5 — Sealed ledger

**Research direction.** Bank a prospective data point before the outcome exists.

**Plan.** Freeze the evaluation roster. Sample companies whose 2026 third-quarter press release
gave guidance and whose next earnings release falls after the sealing date. Primary target: the
direction of next quarter's guidance. Descriptive target: a hard event within six months, with the
expected count stated. A fixed zero-shot prompt, pre-registered as EXP-0001.

**Guardrails.** Forecast contents stay on the external drive. The hash manifest is committed and
then pushed or externally time-stamped.

**Gate.** Manifest time-stamped before 2027-01-10; every roster model has a version recorded.

### WP6 — Research design v1.0

**Plan.** Write `research/design/research_design.md` from WP1 to WP5. Write
`docs/proposal/v0.2.md`; v0.1 is not edited.

**Guardrails.** Every decision states its evidence and what result would overturn it.

**Gate.** The benchmark specification is concrete enough to start labelling, and the owner signs
off.

## Design defaults, v2

Hypotheses until the research design confirms or replaces them.

| Decision | Default | Changed in v2 |
|---|---|---|
| Text source | EDGAR: 8-K earnings press releases (Item 2.02, Exhibit 99.1), plus 10-Q and 10-K. Transcripts only as a private second layer | No. The cost is stated: calls add information beyond the release |
| Benchmark v0 | Guidance revision, three sub-tasks: extract guidance tuples; label the revision; minimal pairs with unedited controls | Label scheme revised; controls added |
| Strata | Numeric against qualitative guidance; the company's updating routine; company size | New |
| Unit of analysis | A pair of outlook passages from one company's consecutive releases; whole documents on a robustness subset | No. Whole documents are known to fit for inference |
| Size | Set from the pilot's disagreement rate. Planning value 500 to 800 gold test pairs, valid if two systems disagree on at most 15% of items | Conditional now |
| Splits | Test documents postdate every roster model's cutoff (after 2026-06-30 today); for a pair, the later document must, the earlier may not (both-after subset reported alongside). Training is earlier and company-disjoint. Companies are assigned by split v1 (CIK hash, 60% test / 10% dev / 30% train), shared with sub-study S1 | Pair rule settled 2026-11-14; split v1 fixed 2026-11-15 |
| Gold labels | Tuples entered by the owner, revision labels computed by rule, checked by the owner; test-retest on 100 pairs; an adjudicated sample of unmatched extractions | Gate and adjudication revised |
| Baselines | Keyword outlook rules; pair similarity plus dictionary tone change; a FinBERT-class model; zero-shot local; zero-shot commercial | Two added |
| Method comparison | Full factorial on Qwen2.5-7B-Instruct and Gemma 4 12B: prompt, fine-tuning and tools at two levels, retrieval at three (none, retrieved, correct passage supplied), 24 cells. Qwen3.5-4B, 9B and the commercial models run the 12 cells without fine-tuning. Same development set and evaluation count per method. The fine-tuned level is trained on its cell's prompt format | Base models changed; training format specified |
| Analysis | Named confirmatory contrasts with Holm; item-level mixed logit for interactions, by stratum; clustered by company | Revised |
| Goal C | DEFERRED for now (owner, 2026-11-14). When taken up: non-inferiority of the best frozen local configuration against Claude Opus 5.5 and Sonnet 5.5 (no-tool subagents; the claim is about Claude only), on strata below the ceiling, margin and power stated in advance. DianJin-R1-7B as the domain-trained reference. One configuration re-run at 8-bit | Ceiling and power added |
| Endpoints | Primary: paired accuracy difference on the revision label, clean documents only. Secondary: tuple F1, minimal-pair consistency and false-positive rate, calibration, cost. Exploratory: hard events, sealed Brier | False-positive rate added |
| L2 | Extracted direction, numeric or qualitative, against the next quarter's as-filed figure, stratified by the size of the change, on the full sample | Anchor moved to the outcome |
| Failure definition | Hard tier: four 8-K items by sub-item. Softer tiers: filing-anchored events; a fall in an as-filed profitability-and-leverage composite; twelve-month market-adjusted return including the delisting return. Pre-registered before outcome data is seen | Softer tiers defined |
| Reporting | One contamination label per result; commercial models "clean (vendor-stated cutoff)" | Qualifier added |

## Later phases

| Phase | Content | Gate to the next |
|---|---|---|
| Phase 0 | This roadmap | Research design v1.0 signed off by the owner |
| Phase I | Guidance-revision benchmark and baselines | Label agreement meets its gate; the task separates systems; the same configuration re-run gives the same result |
| Phase II | Factorial experiment and the Goal C test, with cost and latency recorded | Main effects and interactions have intervals; at least one configuration extracts well enough to scale up |
| Phase III | Scale the best one or two configurations to the full sample; anchored L2 tests with 125 to 250 random validation labels; L3 reported as exploratory | Every pre-registered test is reported, whatever its direction |
| Every earnings season | Add a batch of post-cutoff items; seal a new round of forecasts | Ongoing |
| Phase IV | Integration into ResearchOS | Outside this roadmap |

## Open decisions for the owner

In order of urgency.

1. ~~**SEC EDGAR contact string.**~~ Settled 2026-11-13: stored as `EDGAR_IDENTITY` in the conda
   env `nlab`, outside the repo.
2. **Download of `mlx-community/Qwen2.5-7B-Instruct-4bit`.** About 5 GB, Apache-2.0. Without it the
   factorial runs on Gemma 4 12B alone.
3. **Labelling time.** 100 pairs, two rounds of about 7 hours, 14 days apart.
4. **Time stamps (before 2027-01-10).** ~~Repo visibility~~: settled 2026-11-15, public and
   pushed. GitHub's push record now time-stamps registrations and manifests. Still open: whether
   sealed manifests also get a second, external stamp that does not depend on the owner's own
   repository, such as an OpenTimestamps proof committed beside the manifest.
8. **Gold test labels and reproduction.** Gold test labels stay out of git, so that published
   items do not become training data. Then an outside reader cannot re-score a test run. Options:
   publish only hashes; publish a window's gold once every model evaluated on it is superseded;
   or give it out on request. Needed before the first study report.
5. ~~**Commercial API key on this machine.**~~ Settled 2026-11-14: no key. The commercial models
   are Claude Opus 5.5 and Sonnet 5.5, run as no-tool Claude Code subagents
   (`.claude/agents/roster-claude-*.md`). Goal C's claim is limited to Claude. On the same day the
   owner set the commercial part aside for now: Phase 0 runs local models and baselines only, and
   the Claude models join the roster only when the owner reopens it. Reopened for sub-study S2
   only on 2026-11-19; goal C and the Phase 0 pilots stay as they were.
6. **Data budget (not urgent).** Post-cutoff transcripts and delisting-aware daily prices are paid.
7. ~~**Must both releases of a test pair postdate the cutoff?**~~ Settled 2026-11-14: only the
   later one. About 1,700 to 2,200 numeric pairs exist now. Every pair result is also reported on
   the both-after subset (800 to 1,000 pairs now), and the earlier release's memorisation is
   checked; `00_master_methodology.md` §3, `data_audit.md` §8.
9. ~~**S2 data pulls.**~~ Approved 2026-11-20 with filing years 2019 to 2025 (changelog);
   EXP-0021. As proposed: earnings releases from 2019 to 2024 for training and development companies:
   EXP-0020 lists 31,165 that map to a labelled quarter and are not on the drive, and S2 needs
   episodes the models remember well. Proposed: about 1,500, four per company for the 250 largest
   and 500 from the rest (S2 design, decision 4). A second company-facts snapshot
   in December, for the 18% of July-to-September releases whose next quarter is not filed yet.
10. **S2 test-side run (before S2-c).** Claude does not read post-cutoff test items (changelog,
    2026-11-14), but a session that dispatches subagent calls reads what it dispatches. Either an
    exception for S2's confirmatory run or a scripted path that keeps the items out of the
    session.
11. **S2 prospective arm.** Whether to seal calls on the October and November 2026 releases now.
    Their next-quarter labels arrive in February 2027, which would give a second clean quarter
    and separate "period" from "after the cutoff". It could share WP5's sealing.

## Links

All sources are in `research/literature/matrix.csv`: the 86 of the first pass, and for sub-study S2 the 19 rows of stream 08 and the 92 of streams 09 to 12 (merged 2026-11-24). Links the plan cites directly:

- [mlx-community/Qwen2.5-7B-Instruct-4bit](https://huggingface.co/mlx-community/Qwen2.5-7B-Instruct-4bit)
- [Tang, Yao, Zarowin: Once Is Not Enough](https://www.stern.nyu.edu/sites/default/files/assets/documents/Michael%20Tang.pdf)
- [FinanceBench](https://arxiv.org/abs/2311.11944)
- [Finance Agent Benchmark](https://arxiv.org/abs/2508.00828)
- [RAFT](https://arxiv.org/abs/2403.10131)
- [Ovadia et al.: Fine-Tuning or Retrieval?](https://arxiv.org/abs/2312.05934)
- [FinVerBench](https://arxiv.org/abs/2605.29586)
- [Lopez-Lira, Tang: Can ChatGPT Forecast Stock Price Movements?](https://arxiv.org/abs/2304.07619)
