# Master methodology

**Status, 2026-11-13.** No method has been validated yet. What follows are the constraints the
programme works under, from the plans approved on 2026-11-12 and 2026-11-13. They are rules of the
road, not findings. Design choices that are still hypotheses live in `01_roadmap.md` under "Design
defaults" until the research design confirms or replaces them. The evidence behind the 2026-11-13
changes is in `../literature/gaps.md` and `../design/feasibility.md`.

## 1. What may be claimed

| Level | Question | Standing |
|---|---|---|
| L1 extraction | Does the system read the document correctly? | Confirmatory |
| L2 economic interpretation | Does the extracted change line up with realised fundamentals? | Tested against an anchor on the outcome: the extracted direction, numeric or qualitative, checked against the next quarter's as-filed figure for the same metric |
| L3 investment prediction | Does it predict returns or failure events? | Exploratory |

Why L3 is exploratory: with a monthly information coefficient of 0.02 and a standard deviation of
0.10, an expected t-statistic of 2 needs about 100 clean months, (2 × 0.10 / 0.02)², and that is
only about 52% power; 80% power needs about 196 months. The clean window grows by 12 months a
year. Hard failure events are rare: fifty clean events put an AUC interval at roughly ±0.08, and at
0.3 to 1.5% a year 800 companies yield two to twelve bankruptcies.

Why the L2 anchor is on the outcome and not on the guidance being numeric: numeric EPS forecasts
are about 5% of forward-looking sentences in earnings releases, and under uncertainty firms drop
numbers and say more in words. A numeric-only sample under-represents firms near failure. Anchored
associations in the literature are weak, so L2 uses the full sample, stratified by the size of the
change.

## 2. Point-in-time protocol

- The only clock is the SEC EDGAR acceptance timestamp. Indexes, retrieval and tools filter on it.
- Fundamentals are the values first filed, not restated ones.
- Evaluated models get no web access. Their inputs come from the frozen corpus.
- The evaluation roster records, for each model, the repo and revision (open weights) or the model
  ID (commercial), the release date, and the knowledge cutoff the vendor states.
- A vendor's stated cutoff is not exact, and recall fades well before it. Use a buffer.
- **Commercial models** (owner's decision, 2026-11-14; set aside for now the same day, so nothing
  below runs until the owner reopens it): Claude Opus 5.5 (`claude-opus-5-5`) and
  Claude Sonnet 5.5 (`claude-sonnet-5-5`), both with a stated reliable-knowledge and training-data
  cutoff of June 2026. They are run as Claude Code subagents from the no-tool definitions in
  `.claude/agents/`: no tools, no CLAUDE.md, a fixed two-line system prompt, effort pinned at
  `high`. Each call is a fresh subagent with one item and no gold. Results are labelled with the
  model ID and "Claude Code subagent, no tools", since the harness differs from a bare API call.

## 3. Contamination labels

Every reported result carries exactly one.

| Label | Meaning | What it supports |
|---|---|---|
| Clean | Documents dated after every roster model's cutoff, or counterfactually edited so the label is known by construction. For a commercial model, written "clean (vendor-stated cutoff)": a closed model cannot be shown leakage-free | Confirmatory claims |
| Bounded | Pre-cutoff documents where the supplied text fixes the label | Reported with the memorisation probe's result; recall may still inflate accuracy and favour large models |
| Contaminated | Pre-cutoff tasks whose answer would differ if the future were known (tone, narrative, forecasts) | An upper bound only |
| Prospective | Forecasts sealed before the outcome exists | Clean, small, descriptive |

To choose between "bounded" and "contaminated", ask whether an analyst's answer would change with
knowledge of what happened next. If it would, the task is not future-invariant.

**Pairs.** A document pair is clean when its later document postdates every roster model's cutoff;
the earlier one may predate it (owner's decision, 2026-11-14). The revision label is fixed by the
later document, which no model can have seen, but the earlier one may be remembered. So every
result on pairs is also reported on the subset where both documents postdate the cutoff, and the
item-level memorisation regression (closed-book recall of the earlier document against open-book
accuracy) is run on the pairs whose earlier document predates it.

Masking is not a route to "clean". Simple masking leaves 31 to 70% of transcripts re-identifiable
(and all 15 large-cap cases in ResearchOS). Rewriting by an LLM lowers that to about 9% but removes
signal, and for guidance it removes the numbers, which are the label.

## 4. Splits

- Test: documents dated after every roster model's cutoff. As of 2026-11-13 that is after
  2026-06-30. For a pair, the later document must be; the earlier may not be (§3).
- Training and development: earlier documents, from companies that do not appear in the test set.
- Adding a model with a later cutoff to the roster moves the test boundary for that model's
  results.

## 5. Gold labels

- Guidance tuples are entered by the owner. Revision labels are computed from the tuples by rule
  and checked by the owner. A rule-based parser may propose tuples.
- No model on the evaluation roster annotates or pre-annotates test items.
- With one annotator, reliability is test-retest: the same items labelled twice, 14 days apart, in
  a different order and blind to the first round.
- The gate is on the lower bound of the interval for kappa, set before round 1. A point estimate
  of 0.8 on 100 items passes a true 0.79 about 45% of the time. Report raw agreement and AC1 beside
  kappa, because one class ("maintained") dominates.
- Single-annotator gold is partial. Each round, a sample of extractions that systems produced and
  gold lacks is adjudicated, and the share found valid is reported.
- Gold test labels stay out of git. A published test set becomes training data for later models.

## 6. Comparing systems

- Compare paired, on the same items. For a 5-point accuracy difference at 80% power, when two
  systems disagree on 15% of items, about 470 items are needed by the normal approximation and
  about 500 by the exact test; at 25% disagreement, 785. The test-set size is set from the
  disagreement rate measured in the headroom pilot.
- Name the confirmatory contrasts in advance and correct them with Holm.
- Intervals come from resampling, clustered by company. Quarter is a stratum, not a cluster: the
  clean window holds two to four quarters.
- Estimate interactions between methods with an item-level mixed logit, and report them by
  difficulty stratum. On the accuracy scale a ceiling makes two helpful methods look like
  substitutes; pooling easy and hard items creates a spurious interaction on the logit scale.
- "Matches" is a non-inferiority claim against a margin set in advance, tested on strata below the
  ceiling, with its power stated at realistic shortfalls. With 800 items and a 5-point margin,
  power is 0.95, 0.83 and 0.59 for true shortfalls of 0, 1 and 2 points.
- Rule-based baselines are run first and set the bar.
- How invalid outputs are scored is fixed before the run.

## 7. Development budget and fine-tuning

- Each method being compared gets the same development set and the same number of development
  evaluations. Checkpoint selection, LoRA hyperparameter search and prompt edits all count.
- Nothing is selected on the test set. Configurations are frozen before the test run.
- A fine-tuned level is trained on the prompt format of the cell it is used in. A cell with
  retrieval trains with the correct passage and distractors. Fine-tuning without context and then
  adding retrieval lowers accuracy by itself.
- Training labels do not come from a roster model where a rule can supply them.

## 8. Pre-registration and time stamps

An experiment's hypothesis, sample, criteria with numeric thresholds, and random seed are written
into `experiment_registry.md` and committed before the run. The verdict cites that commit. A
refutation is a publishable outcome.

A local commit is not an independent time stamp. Registrations and sealed manifests are pushed or
externally time-stamped, in the way the owner decides.

## 9. Memorisation probe

- Give only the company and the fiscal quarter. Ask whether guidance was raised, lowered,
  maintained or "unknown"; a second variant asks for the numeric range.
- Record answer-token probabilities for local models and repeated samples for the Claude models.
- Sample quarters from at least three years before the cutoff to after it, stratified by company
  size. Quarters next to the cutoff show no gap even in a contaminated model.
- Score against a persistence baseline, since guidance changes slowly.
- A null result is a lower bound on memorisation, never evidence of "clean".
- Item-level test: regress open-book extraction correctness on closed-book recall propensity.

## 10. Not claimable

- That masking, open weights or point-in-time retrieval remove look-ahead.
- That results on pre-cutoff documents measure reading and not recall.
- That a commercial model is leakage-free.
- That goal C's result extends beyond Claude. Only one vendor is on the roster.
- That the subagent results equal bare API results. They run through the Claude Code harness.
- That a subset of companies a model failed to recognise is representative. It skews to obscure
  firms.
