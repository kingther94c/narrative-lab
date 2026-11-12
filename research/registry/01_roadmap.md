# Roadmap

v1, 2026-11-12. Source: the plan the owner approved on 2026-11-12, kept verbatim in
[`docs/plans/2026-11-12_phase0_plan.md`](../../docs/plans/2026-11-12_phase0_plan.md) (Chinese),
which builds on proposal v0.1 ([`docs/proposal/v0.1.md`](../../docs/proposal/v0.1.md)). Where this
file and the approved plan differ, the approved plan wins until `changelog.md` records an
amendment. **Start every session here.**

## Where the programme stands

| Track | Status |
|---|---|
| WP0 Repo scaffold | Done 2026-11-12. Committed locally, not pushed |
| WP1 Literature review | Not started |
| WP2 Data audit | Waiting on the SEC contact string, except the transcript-licence part |
| WP3 Feasibility probes | Not started |
| WP4 Labelling pilot | Waiting on WP2 samples and the owner's time |
| WP5 Sealed ledger | Waiting on WP2. Deadline 2027-01-10 |
| WP6 Research design v1.0 | Waits for WP1 to WP5 |

## North star

Learn what works, for which task, under which data and compute limits, and why: for a specialised
research task, where should capability live, in the weights, the prompt, the retrieved context or
the tools? Financial narrative understanding is the test bed and equity failure detection is the
application. The proposal does not presume alpha, and neither does this roadmap.

Head-to-head results expire with model versions. The asset that lasts is a benchmark that gains a
fresh batch of clean, post-cutoff items every earnings season.

## What we know going in (2026-11-12)

| Area | Fact | Source | Consequence |
|---|---|---|---|
| ResearchOS results | Runs used 15 or 21 earnings cases; the trained-versus-untrained Brier intervals all span zero (for example -0.008 [-0.021, +0.006] and -0.004 [-0.023, +0.011]) | `../Foundry/ResearchOS/runs/2026-10-first-real-run/README.md`, `../Foundry/ResearchOS/runs/2026-10-smallbank-run/README.md` | Sample size is the first constraint |
| ResearchOS perspectives | Guidance and expectations gap ended on top; "management tone added least". Mean pairwise correlation of the seven perspectives was 0.855 read together and 0.387 read in isolation | Same, and `../Foundry/ResearchOS/runs/2026-10-perspectives-run/README.md` | First task is guidance; extract each feature on its own |
| ResearchOS masking | "Every one of the 15 masks ended identifiable"; abstraction left eight of eight identifiable. The working guard is the knowledge cutoff, 2026-06-30 | `../Foundry/ResearchOS/runs/2026-10-first-real-run/README.md` | No masking; test on post-cutoff documents |
| ResearchOS data † | Documents were fetched per case from the web and are not stored on this machine; transcripts came from roic.ai and Motley Fool; no consensus source was reachable for small caps | ResearchOS run notes | Bulk data needs another source; transcripts are the hard part |
| Local models † | `py313` has `mlx_lm` 0.32.2. On the external drive: Qwen3.5-4B, Qwen3.5-9B, Gemma 4 12B, DianJin-R1-7B (finance-tuned), gpt-oss-20b. Ollama is not installed | `../learning_ai/learnai/openweights.py` | Phase 0 installs nothing; MLX is the only local runtime |
| Measured and unmeasured † | Qwen3.5-9B: prefill about 1,130 tok/s, decode about 31 tok/s, measured only up to about 2.4k prompt tokens. MLX LoRA has never been run | `runs/finbench/*/*.meta.json` on the external drive | Long-prompt inference and LoRA memory are the two largest unknowns |
| Finance baseline † | 150-question screening: local models 73 to 77%, Claude reference 92% | `../learning_ai/docs/FINANCE_MODEL_SELECTION.md` §3 | A starting number for the local-versus-commercial gap |
| Model timeline | Qwen3.5 small models released 2026-03-02; Gemma 4 released 2026-04-02; ResearchOS uses 2026-06-30 as the cutoff for Opus 5.5 | Links at the end; ResearchOS run notes | Documents after 2026-06-30 are clean for the local models and Opus 5.5: two earnings seasons so far |
| Storage | 128 GB free on the internal disk; 1.8 TB external drive mounted | `df`, 2026-11-12 | Models, data and run outputs go on the external drive |
| GitHub | `kingther94c/narrative-lab` is public and empty | `gh repo view`, 2026-11-12 | The owner decides visibility before the first push |

† Reported by a read-only survey of the sibling repos on 2026-11-12 and not re-read line by line.
Check the cited file before relying on the figure. The other rows were checked against the cited
file.

A quick literature check, which is not the review, added four points:

- Chronologically consistent small models exist (ChronoBERT / ChronoGPT, yearly vintages 1999 to
  2024). The proposal's statement that no convenient point-in-time general LLM exists holds for
  strong models; a clean but weak reference model is available.
- Masking is not enough, which matches ResearchOS: GPT-4o re-identified a firm from a fully masked
  earnings call transcript, and other work gives a formal test based on a memorisation proxy and
  reports that memorisation inflates apparent predictive power.
- No widely used public benchmark was found that labels guidance revisions or narrative shifts
  across consecutive quarters.
- No head-to-head empirical study was found of prompting, RAG, fine-tuning and tools on small
  open-weight versus commercial models for financial narrative tasks.

The last two are hypotheses about gaps. WP1 confirms or refutes them.

## Five amendments to proposal v0.1

1. **Decide first what may be claimed.** L1 is confirmatory. L2 is tested only where a numeric
   anchor exists. L3 is exploratory. The reasoning is statistical power; see
   `00_master_methodology.md` §1.
2. **Phase I builds one task family: guidance revision.** Its labels can be computed from numbers
   and checked by one person; the data is all on EDGAR and covers the small caps where failures
   happen; an upbeat headline over a cut or silently dropped metric is failure detection in
   miniature. Tone, confidence shift and management-versus-analyst divergence have no ground truth
   a single annotator can supply, so L1 on them would measure agreement with a teacher model. They
   enter the benchmark only after a labelling pilot shows one annotator can label them reliably.
3. **Phase 0 is three parallel lines plus one deadline.** The design is constrained by what the
   literature has answered, what data can be had, and what this machine can run. The deadline is
   sealing: results for the quarter after the 2026 third-quarter reports start arriving in
   mid-January 2027. EDGAR documents are permanent; the window before the outcome is not.
4. **Goal B's core evidence comes from a factorial experiment on open-weight models.** Commercial
   fine-tuning is absent or opaque and cannot be compared on the same base model. Commercial
   models run the design without the fine-tuning factor, as a capability reference. LoRA
   feasibility on 32 GB is therefore a precondition of Goal B and is measured in Phase 0.
5. **Time, not masking; and a rolling benchmark.** Test documents postdate every roster model's
   cutoff. Otherwise recall inflates accuracy and favours large models, which biases Goal C.

Deferred, not dropped: tasks on earnings call transcripts, return prediction, internal-
representation analysis, model routing and hybrids, and integration into ResearchOS. They are
re-prioritised once Phases I and II have results.

## Phase 0 — Literature review and research design

Phase 0 trains no model that will be evaluated. Target: design frozen by the end of December 2026.

WP1, WP2 and WP3 do not depend on each other. WP6 waits for all the others.

### WP1 — Literature review

**Research direction.** Find out what is already answered, so the first benchmark and experiments
aim at real gaps.

**Plan.** Seven streams, each tied to the design decision it settles:

| Stream | Question it must answer | Seeds |
|---|---|---|
| Financial text analysis before LLMs | Which narrative features have documented predictive power, for which outcome, how large; which baselines must be beaten | Loughran–McDonald 2011; Cohen–Malloy–Nguyen 2020; Hassan et al. 2019 |
| LLMs extracting financial signals | What LLMs add over dictionaries and FinBERT; how others evaluated | Lopez-Lira–Tang 2023; Kim–Muhn–Nikolaev 2024; Jha et al. 2024 |
| Look-ahead and memorisation | Which evaluation protocol holds up | He et al. 2025 ✓; Glasserman–Lin 2023 ✓; Lopez-Lira–Tang–Zhu 2025 ✓; Gao–Jiang–Yan 2025 ✓ |
| Financial NLP benchmarks | What can be reused, what is missing, how others labelled | FinanceBench; FinQA; FinBen; arXiv 2510.03195 ✓; arXiv 2510.23464 ✓ |
| Comparing adaptation methods | How to compare fairly; known confounds | Ovadia et al. 2023; Balaguer et al. 2024; Li et al. 2023 ✓ |
| Distress and failure prediction | How failure is operationalised; base rates; structured baselines | Altman 1968; Beneish 1999; Campbell–Hilscher–Szilagyi 2008 |
| Statistical method | Multiple testing; valid inference from LLM labels | Harvey–Liu–Zhu 2016; Angelopoulos et al. 2023 |

✓ means checked against the paper's abstract on 2026-11-12. The other seeds are from memory and
are verified before they enter the review.

Per stream: search, triage 10 to 15, deep-read 3 to 5.

**Guardrails.** Every citation has a working link and is checked against the source. Stop at about
50 triaged papers, or when two consecutive batches change no design decision.

**Deliverables.** About 20 notes in `research/literature/papers/`, `matrix.csv`, `gaps.md`.

**Gate.** Every design default below is marked supported, contradicted or not addressed by the
literature, with a note cited for each.

### WP2 — Data audit

**Research direction.** Establish what data can actually be had, with what point-in-time and
survivorship properties, under what licence.

**Plan.**

| Need | First choice | What to verify |
|---|---|---|
| Disclosure text: 8-K earnings press releases, 10-Q, 10-K | SEC EDGAR | Acceptance timestamps, exhibit parsing, rate limits |
| Earnings call transcripts | Hugging Face `kurry/sp500_earnings_transcripts` | Whether provenance and licence hold up, truncation, whether removed index members are included |
| Fundamentals as filed | SEC XBRL company facts | First-filed values; handling of restatements |
| Failure events | 8-K items 1.03 (bankruptcy), 3.01 (delisting notice), 4.02 (non-reliance on prior financials), 2.06 (material impairment) | Bulk availability; base rates |
| Returns including delisted stocks | Open. Free sources usually drop delisted tickers; whether the IBKR daily closes ResearchOS used cover them is unverified | Coverage and cost. If unavailable, L3 uses survivors only and says so |
| Consensus estimates | Bulk sources are mostly paid | If unavailable, the "earnings downgrade" endpoint becomes realised fundamentals |

Two censuses decide whether the benchmark is feasible:

- Guidance census: 50 companies by 8 quarters. Count the share of press releases with numeric
  guidance and the mix of change types.
- Hard-event census: how many of each of the four 8-K items were filed after 2026-06-30.

Each source gets one small sample pull (tens of documents, stored on the external drive).

**Guardrails.** No EDGAR request until the owner has chosen the contact string. Nothing pulled goes
into git.

**Deliverables.** `research/design/data_audit.md`: coverage and defect rate per source, the two
censuses, a go / no-go per candidate task and per outcome variable, storage estimate, licence
notes.

**Gate.** Usable document pairs are counted, not estimated.

### WP3 — Feasibility probes

**Research direction.** Measure what this machine can do before the design assumes it.

**Plan.** Grouped by model, queued overnight, one job at a time.

1. Long-prompt inference: Qwen3.5-4B and 9B at 4k, 8k, 16k and 32k prompt tokens: prefill speed,
   decode speed, peak memory.
2. LoRA: `mlx_lm.lora` on the 4B and 9B at sequence lengths 1k, 2k, 4k and 8k on public text: peak
   memory, seconds per step, and whether the Qwen3.5 layers accept LoRA.
3. Headroom pilot: on 100 document pairs compare a rule baseline, Qwen3.5-4B, 9B, Gemma 4 12B,
   DianJin and a commercial model. Pass conditions are written into the registry before the run:
   the rule baseline is clearly behind and the best model is not at the ceiling. If the 4B already
   exceeds 90%, move to a harder stratum. The pilot also gives the disagreement rate between
   systems for the power estimate.
4. Memorisation probe: ask each model, closed-book, for a company's guidance in a given quarter;
   compare accuracy before and after its cutoff.
5. Structured-output compliance, verbatim hit rate of evidence quotes, and tool-call reliability.

**Guardrails.** Run in `py313`. Download no model. The LoRA runs are engineering measurements and
produce no model that is evaluated. Budget for the commercial part is estimated from what
ResearchOS recorded (about $0.16 to $0.22 per case) and measured in the pilot.

**Deliverables.** `research/design/feasibility.md`: tables with the command, model repo and
revision for every number, and what follows for benchmark size, compute hours and API budget.

**Gate.** Phase II fits a stated compute and API budget.

### WP4 — Labelling pilot

**Research direction.** Show that one annotator can label the task reliably, and find out whether a
softer task can be labelled at all.

**Plan.**

- The codebook defines the guidance tuple (metric, period, low, high, basis) and the change class
  (raised, maintained, lowered, narrowed, withdrawn or no longer mentioned, initiated).
- The change class is computed from the tuples by rule and checked by the owner.
- 100 guidance pairs are labelled twice, 14 days apart.
- 30 pairs of "cross-quarter narrative change" are labelled the same way.

**Guardrails.** No roster model labels or pre-labels these items. The commercial baseline is likely
a Claude model, so Claude does not produce gold labels.

**Deliverables.** `research/design/labeling_codebook.md`; both rounds of label files kept outside
git; agreement computed by script.

**Gate.** Suggested thresholds: test-retest kappa of at least 0.8, and rule-versus-human agreement
of at least 90%. If the narrative-change pairs miss the same thresholds, that task stays out of
Benchmark v0.

### WP5 — Sealed ledger

**Research direction.** Bank a prospective data point before the outcome exists.

**Plan.**

- Freeze the evaluation roster: Hugging Face repo and revision for local models, model ID for
  commercial ones.
- Sample: companies whose 2026 third-quarter press release gave numeric guidance and whose next
  earnings release falls after the sealing date.
- Targets: direction of next quarter's guidance; whether a hard event occurs within six months.
- A fixed zero-shot prompt, registered as EXP-0001 and pre-registered first.

**Guardrails.** Forecast contents are stored on the external drive. Git gets the hash manifest
only. Layout follows ResearchOS: seal first, reveal later.

**Deliverables.** `research/ledger/` manifest; the EXP-0001 pre-registration.

**Gate.** Manifest committed before 2027-01-10; every roster model has a version recorded.

### WP6 — Research design v1.0

**Research direction.** Turn the evidence from WP1 to WP5 into decisions.

**Plan.** Write `research/design/research_design.md`: data sources and sample, Benchmark v0
specification, splits, the design of the method comparison, endpoints and power per level, the
pre-registered failure definition, point-in-time rules. Move the hard rules into
`00_master_methodology.md`. Write `docs/proposal/v0.2.md`; v0.1 is not edited.

**Guardrails.** Every decision states its evidence and what result would overturn it.

**Gate.** The benchmark specification is concrete enough to start labelling, and the owner signs
off.

### Suggested cadence

- Week of 2026-11-16: WP0 done; WP1 and WP2 started; roster frozen.
- By end of November: first labelling round.
- Mid-December: second labelling round; probes finished.
- End of December: research design v1.0 to the owner.
- Before 2027-01-10: zero-shot forecasts on the third-quarter sample sealed.

## Design defaults

These are hypotheses, written down so the literature review and the data audit have something to
aim at. Phase 0 confirms or replaces each one.

| Decision | Default | What would overturn it |
|---|---|---|
| Text source | EDGAR: 8-K earnings press releases (Item 2.02, Exhibit 99.1), plus 10-Q and 10-K. Transcripts only as a private second layer | The transcript licence audit passes and quality is good |
| Benchmark v0 | Guidance revision, three sub-tasks: extract guidance tuples; classify the change; minimal pairs in which only the numbers or only the wording were edited, so the label is known by construction. Includes a stratum of qualitative guidance such as "toward the low end of the range" | The census finds too few releases with guidance, or the literature already has a reusable benchmark of this kind |
| Unit of analysis | A pair of outlook passages from one company's consecutive press releases. Whole documents only on a robustness subset | Probes show whole-document inference and training are comfortable |
| Size | 500 to 800 gold test pairs across at least 400 companies. Training pairs labelled by rule, from earlier periods and other companies | The pilot's disagreement rate changes the power estimate |
| Splits | Test documents postdate every roster model's cutoff (after 2026-06-30 today). Training is earlier and company-disjoint | A model with a later cutoff joins the roster |
| Method comparison | Full factorial on Qwen3.5-4B and 9B: prompt, fine-tuning and tools at two levels each, retrieval at three (none, retrieved, correct passage supplied), 24 cells, every test item through every cell. Same development set and same number of development evaluations per method. Interactions on the logit scale and by difficulty stratum | The LoRA probe fails; then fine-tuning moves to a smaller model |
| Goal C | Non-inferiority test of the best frozen local configuration against each commercial model, margin set in advance (suggested 5 points), with cost and latency per thousand items. DianJin-R1-7B as the "domain-trained by someone else" reference. The 4B re-run at 8-bit to bound the quantisation effect | None stated |
| Endpoints | Primary: paired accuracy difference on the change class, clean documents only. Secondary: tuple F1, minimal-pair consistency, calibration, cost. Exploratory: association with hard events; Brier score of sealed forecasts | None stated |
| Failure definition | The hard-event tier is fixed now as the four 8-K items. Other tiers are pre-registered before outcome data is seen | The literature offers a better operationalisation |
| Reporting | Every result carries one contamination label: clean, bounded, contaminated or prospective | None stated |

## Later phases

| Phase | Content | Gate to the next |
|---|---|---|
| Phase 0 | This roadmap | Research design v1.0 signed off by the owner |
| Phase I | Guidance-revision benchmark and baselines: rules, a FinBERT-class model, zero-shot local, zero-shot commercial | Label agreement meets its threshold; the task separates systems; the same configuration re-run gives the same result |
| Phase II | Factorial experiment and the Goal C non-inferiority test, with cost and latency recorded | Main effects and interactions have intervals; at least one configuration extracts well enough to scale up |
| Phase III | Scale the best one or two configurations to the full sample; anchored L2 tests; L3 reported as exploratory | Every pre-registered test is reported, whatever its direction |
| Every earnings season | Add a batch of post-cutoff items; seal a new round of forecasts | Ongoing |
| Phase IV | Integration into ResearchOS | Outside this roadmap |

## Open decisions for the owner

In order of urgency.

1. **SEC EDGAR contact string (this week).** EDGAR's fair-access policy requires a contact email
   or name in the request header. The data audit, the labelling pilot and the sealing all depend on
   it.
2. **Labelling time (first round by end of November).** 100 guidance pairs plus 30 narrative-change
   pairs, about 8 to 9 hours a round, two rounds 14 days apart. The full benchmark is about 35 to
   55 hours. Whether that is realistic sets the benchmark's size.
3. **Repo visibility (before the first push).** It is public now. Private is suggested while
   hypotheses and notes are in progress. If it stays public, hash manifests can still be committed
   and forecast contents, gold test labels and licensed text stay outside.
4. **Commercial API key on this machine (before sealing).** The headroom pilot and the commercial
   part of the sealed forecasts need one.
5. **Data access and budget.** Whether institutional data such as WRDS is available, or paid
   sources for transcripts and delisting-aware prices are acceptable. This sets what the data audit
   looks at.

## Links checked on 2026-11-12

- [Chronologically Consistent Large Language Models (He, Lv, Manela, Wu)](https://arxiv.org/html/2502.21206v3)
- [Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis (Glasserman, Lin)](https://arxiv.org/pdf/2309.17322)
- [The Memorization Problem: Can We Trust LLMs' Economic Forecasts? (Lopez-Lira, Tang, Zhu)](https://arxiv.org/html/2504.14765v2)
- [A Test of Lookahead Bias in LLM Forecasts (Gao, Jiang, Yan)](https://arxiv.org/html/2512.23847v1)
- [MemGuard-Alpha](https://arxiv.org/pdf/2603.26797.pdf)
- [Are ChatGPT and GPT-4 General-Purpose Solvers for Financial Text Analytics? (Li et al.)](https://arxiv.org/pdf/2305.05862)
- [LLM as extractor, embedding as ruler (arXiv 2510.03195)](https://arxiv.org/html/2510.03195v5)
- [Stance detection on 10-K and earnings call sentences (arXiv 2510.23464)](https://arxiv.org/abs/2510.23464v1)
- [ACL 2026 industry track: SEC and earnings call KPI extraction sets](https://aclanthology.org/2026.acl-industry.100.pdf)
- [kurry/sp500_earnings_transcripts](https://huggingface.co/datasets/kurry/sp500_earnings_transcripts/blob/f3ded372da8d18dc6ad98955c4558e34b5fe6d45/README.md)
- [Qwen3.5-9B release information](https://artificialanalysis.ai/models/releases/qwen3-5-9b)
- [Gemma 4 release coverage](https://thenextweb.com/news/google-gemma-4-open-models-apache-2-launch)
- [Fine-Tuning on Mac: LoRA and QLoRA with MLX](https://insiderllm.com/guides/fine-tuning-mac-lora-mlx/)
