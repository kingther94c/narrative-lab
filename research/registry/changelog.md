# Changelog

Newest first. What changed, why, on what evidence, and what it affects.

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
