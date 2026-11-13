# Changelog

Newest first. What changed, why, on what evidence, and what it affects.

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
