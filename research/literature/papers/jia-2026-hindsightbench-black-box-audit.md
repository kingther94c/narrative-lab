# HindsightBench: A Black-Box Behavioral Audit Protocol for Parametric Hindsight in Time-Indexed LLM Decision Tasks

- **Citation:** Haozhe Jia (2026). Preprint, University College Dublin. arXiv 2607.18867. v1 is
  dated 21 July 2026 and v2 10 August 2026. Version read: v2, full text.
- **Link:** https://arxiv.org/abs/2607.18867
- **Stream:** 08, blind replay (S2)
- **Verified against source:** yes, 2026-11-19 (the arXiv abstract page for authors and dates; the
  arXiv HTML of v2, converted to plain text and read in full: abstract, sections 1 to 9, Table 1
  with all its footnotes, the ethics statement and the reference list. Figures 1 to 3 were read
  through their captions only. The HTML has no appendix. The artefact repository and the companion
  paper, which the author says is not yet public, were not opened.)

## Question
Can someone who deploys a given model on a dated decision task find out, with API access only and
at the cost of a set of probes, whether the model uses what it knows about the period after the
decision date, what triggers that use, where its knowledge ends in practice, and whether the
answers survive the way the model is served?

## Data
- **Panel.** 258 monthly US macro decision nodes: 240 from 2005-01 to 2024-12 and 18 from 2025-01
  to 2026-06. Each node is a snapshot built from ALFRED data vintages, so it holds only what had
  been published by its date.
- **Models.** 15 models from seven vendors (OpenAI, Anthropic, Google, DeepSeek, Alibaba/Qwen,
  Moonshot, Meta), from 1B parameters to frontier API models. They include GPT-5.5, Claude
  Sonnet 5 and Claude Haiku 4.5. Rows are grouped by "training generation" 2024, 2025 and 2026.
- **Second domain.** A reduced 65-date audit on the direction of the 10-year Treasury yield, three
  models, one repetition.
- No company-level data. Delisted firms: not applicable.

## Method
One audit row per model. The collection protocol and the primary estimands were frozen by hash
before any non-development model was called. All rows are plain completions with retrieval and
tools off.

**Carrier task.** Given the macro snapshot as of the decision date, produce eight structured
hypothesis sketches, each with a direction call. Only the structured direction field is scored.

**Four arms, which differ only in the dating information.**
- R, revealed: date and auxiliary context as they are.
- D, date-only: the masked prompt plus the explicit date string.
- M, masked: date removed and date-identifying context scrubbed.
- W, wrong date ("transplant"): the true data relabelled with a date shifted by 66 months. A
  72-month variant that keeps the calendar month controls for seasonality.

**Behavioural readout.** The crisis-calm bearish gap: the share of bearish calls on 11 crisis
months listed in advance (six months of 2008-09 to 2009-02, 2020-03 and 04, 2022-06, 09 and 10)
minus the share on 36 calm months (all of 2013, 2014 and 2017). The crisis list enters only at
analysis time.

**Two memory probes.**
- REC, date recovery: the model sees the masked snapshot and is asked to date it, at
  temperature 0. Scored as exact year-month accuracy, calendar-year accuracy and median absolute
  month offset, before and after the cutoff.
- LAP, outcome recall: a date-only query for the realised outcome, adapted from Gao et al. (2025)
  to a model with no log-probabilities. LAP is the answer frequency over 20 samples at
  temperature 1.0 (10 on the reduced tier). The same samples give a recall hit rate: the share of
  pre-cutoff months whose net recalled direction matches the realised one.

**Six metrics, each with a stated condition under which it is reported.**
1. E2, date trigger: Gap(D) minus Gap(M).
2. E3, transplant: the W generations scored once under the asserted date labels and once under
   the true ones; E3 is the difference between the two gaps.
3. P1, post-cutoff placebo: the D minus M difference in bearish share on post-cutoff dates, where
   there is no memory to trigger. If the measured cutoff falls inside the calendar window, the
   window is recomputed relative to the model's own cutoff.
4. REC, reported only with at least 10 convergent probe answers.
5. Effective cutoff: the last month with LAP above 0.1. Defined only when the recall hit rate is
   above chance.
6. Delta, dissociation: the signal-times-LAP interaction in a correctness regression (HAC, lag 6).
   Undefined when the variance of LAP on the estimation dates is 0.0001 or less.

Also reported: VALID, the share of schema-compliant generations; a sample-parity rule, under which
a contrast is reported only when both of its sides cover the full pre-registered set of dates; and,
added after the freeze, E1 = Gap(R) minus Gap(D), the effect of the date-identifying context once
the date is present.

**Statistics.** Paired bootstrap intervals with 10,000 resamples for arm contrasts. Cross-model
inference is limited to ranking and group contrasts.

## Outcome variable and horizon
The share of bearish direction calls, contrasted between crisis and calm months and between arms.
For the recall probe, the realised direction of the month's outcome. The horizon of the direction
label is not stated in the text read.

## Result
Empirical findings on one task and one panel, unless marked otherwise.

- **Date trigger and transplant.** E2 and E3 are significant in 6 of 6 models of the 2026
  generation, in 4 of 5 of the 2025 cohort, and in 0 of the 3 open-weight 2024 rows where they can
  be measured. Claude Sonnet 5: E2 +0.326 [0.19, 0.46], E3 +0.450 [0.26, 0.64]. Claude Haiku 4.5:
  E2 +0.383 [0.30, 0.47], E3 +0.495 [0.34, 0.64], the largest transplant effect. GPT-5.5: E2
  +0.215 [0.10, 0.33], E3 +0.161 [0.09, 0.23].
- **The asserted date is followed.** In the W arm, the year of the fake date is mentioned in 86%
  to 100% of completions on the most affected rows, and recognisable events of that period in up
  to 77%.
- **Placebo.** P1 lies between -0.073 and +0.066 across rows. No intervals are printed for it.
- **Recall without behavioural use.** Llama 3.1 70B has pre-cutoff LAP 0.854 with a 68% hit rate
  and a measured cutoff equal to Meta's reported one, and no trigger (E2 -0.047 [-0.12, 0.03]).
  Qwen3-30B-A3B shows the same pattern. In a post-freeze cross-tabulation of four models, dates
  with high generic recall show no rise in the trigger; the rise sits where recall coincides with
  crisis months.
- **Behavioural use without date recovery.** Qwen3.6-27B dates the masked snapshot correctly in 9%
  of months and still has E2 +19.3 pp. Haiku 4.5 recovers 20% and has the largest E3. The author's
  summary: what can be elicited, what is recalled and what is behaviourally active are three
  different properties.
- **The interaction coefficient has both signs.** Delta is -0.266 (t = -2.03) for Gemini 2.5 Flash
  and +0.254 (t = 2.99) for Kimi-K2.6. For GPT-5.5, Claude Sonnet 5 and GPT-5.4-mini it is
  undefined because pre-cutoff LAP is saturated (0.999, 1.000, 1.000). GPT-5.5's cell had first
  been printed as +0.065 (t = 2.96) before the variance condition was added.
- **A propensity can be high and empty.** Three small Llama models have pre-cutoff LAP of 0.52 to
  0.95 with hit rates of 43% to 50%, which is chance. Their LAP never collapses, so their
  "cutoffs" are reported as undefined.
- **Which channel leaks differs by model.** E1 is null on 13 of 15 rows. For GPT-5.4-mini it is
  +19.4 pp [11.3, 27.1], above that model's E2 of +14.4 pp: 57% of its 33.8 pp total comes from
  the context and not the date string. A two-arm revealed-against-masked design would have
  assigned all of it to the date.
- **Effective cutoffs.** They span 22 months, 2023-12 to 2025-10, over the twelve rows where they
  are defined. Against the vendor's date, available for seven rows, five are early, one exact and
  one late: GPT-5.5 by six months (2025-06 against 2025-12), both Gemini 2.5 tiers by seven to
  eight, Claude Sonnet 5 by three against its "reliable" tier (2025-10 against 2026-01), Claude
  Haiku 4.5 by four, and GPT-5.4-mini late by one month.
- **A calendar "post-cutoff" window is not clean.** On the calendar window, post-cutoff LAP is
  0.556 for Claude Sonnet 5, 0.414 for GPT-5.4-mini and 0.161 for GPT-5.5. One model "recovers"
  the date of 69% of its post-cutoff probes (11 of 16), but 9 of the 17 months are inside its
  measured memory; on its own window the rate is 38% (3 of 8). The row with 69% in Table 1 is
  Claude Sonnet 5; that identification is our reading of the table.
- **Serving details move the numbers.** The same Qwen3.6-27B weights give E2 +19.3 pp [10.8, 28.5]
  at FP8, +17.2 pp [6.6, 28.0] at AWQ-INT4 and +5.6 pp [-2.3, 13.4] at BF16. Under Kimi-K2.6's
  locked reasoning mode, 256 of 258 date-recovery probes used up a 16,384-token budget without an
  answer. The author also reports, from probe calibration, that compressing a model's thinking
  budget can flip its recall answers outright.
- **Parsing moves the numbers.** A trailing-comma repair recovered 100 generations for one model
  and shifted its E2 by +5.8 pp. A strict probe parser that rejected replies such as
  `{"answer": "unknown"}` voided 25.7% of one Gemini row's answers; re-parsing moved its
  pre-cutoff LAP from 0.337 to 0.430.
- **Sensitivity of the black-box LAP.** Moving the 0.1 threshold between 0.05 and 0.2 moves the
  measured cutoff by at most one month on 9 of 12 rows, and by up to nine months on Kimi-K2.6.
  Doubling to 40 samples moves no cutoff by more than a month on three re-probed rows. Probing at
  temperature 0.3 or 0.7 moves one cutoff by four months. The author concludes that the sampling
  regime, not the number of samples, is the binding convention.
- **Second domain.** On Treasury direction, Haiku 4.5 has E2 +63.2 pp [45.9, 80.0] and E3 +62.9 pp
  [24.6, 98.1]; GPT-5.4-mini's E3 is positive and not significant.
- **Cost.** A full row cost $29.45 for Claude Haiku 4.5 (10.5M tokens), $19.30 for GPT-5.4-mini
  and at least $115 for GPT-5.5.

**Cutoff instructions.** The paper does not test them. It cites Li et al. (2026, arXiv 2601.13717)
for a 52% performance gap between instructed and true ignorance, and Lopez-Lira et al. (2025) for
the failure of instructed forgetting. Its own evidence is the complement: a model follows an
asserted date almost without question. We did not open arXiv 2601.13717.

## Look-ahead and memorisation
This is the paper's subject. Three positions matter here.
- Masking removes the trigger, not the knowledge, so masked-arm estimates are lower bounds.
- A placebo or test window is valid only relative to the cutoff measured on the task at hand, not
  relative to a calendar date or the vendor's statement. The converse is also stated: a date inside
  the memory window is not automatically dangerous.
- An audit row describes single generations. How much of it reaches a decision depends on the
  pipeline around the model.

## What it settles for us
- **Closed-book recall probe: supported, with a better specification.** Repeated sampling at a
  fixed temperature works on API models. Reuse: 20 samples per item; score the hit rate against
  chance as well as the propensity, and report nothing downstream when the hit rate is at chance;
  fix and record the temperature, the thinking setting and the parser, and make the parser accept
  an "unknown" in any reply format.
- **Recall propensity as a moderator: contradicted as a self-check.** The plan requires the leakage
  measure to rise with closed-book recall. Here the interaction has both signs across models,
  recall exists without behavioural use, and on the three frontier models LAP has no variance.
  Check the variance of the propensity on our own items first, and treat a flat or negative
  interaction as uninformative, not as a broken measure.
- **Recognition as the split variable: weakened.** A model's ability to date a masked snapshot does
  not predict whether its calls shift. An attacker's failure to identify a view is therefore weak
  evidence that the view is inert. Hypothesis: the same holds for company identification, which
  this paper does not test.
- **Arms assigned by design: reusable.** The four-arm matrix separates the date string, the
  identifying context and the data. For S2 this suggests fixing which identifying elements each
  view keeps, and contrasting arms, in place of sorting views by what an attacker did.
- **Transplant arm: a measure S2 lacks.** Assert a wrong date, or by extension a wrong identity, on
  true data and test whether the call follows the asserted period. It is a positive control: it
  shows what leakage looks like on our readout when recall is certain to be available. The
  extension to identity is our inference.
- **Post-cutoff placebo of the same contrast: reusable.** The date-minus-masked difference on
  post-cutoff items estimates what the date legitimately adds.
- **Test after every cutoff (rule 2): supported.** Measured cutoffs run earlier than vendor dates
  in five of seven cases, so the stated cutoff errs on the safe side here; one row is a month late,
  so the buffer stays.
- **"Select, do not blind" (strategy C): partly supported.** A window before the vendor cutoff with
  no measurable recall exists for several models, and the probe can locate it.
- **Serving.** Results differ by quantisation and reasoning mode. Our no-tool agent definitions fix
  tools; the reasoning setting should be recorded too.
- **Open question.** Whether any of this carries over from macro snapshots with a crisis-calm
  readout to company fundamentals, where no ex-ante list of "crisis" items exists.
- Claude Opus 5.5 and Sonnet 5.5, the models on our roster, are not among the 15.

## Limits
- One carrier task on one US macro panel; the second domain is a reduced audit of three models.
- The readout depends on a hand-made crisis list and measures direction only, not size or
  calibration.
- Several cells were corrected after the freeze (variance condition, sample parity, parsers); the
  author discloses each, and the number of them shows how fragile the pipeline is.
- The causal account rests on a companion paper that is not public.
- The 2024 "no trigger" result rests on one model, Llama 3.1 70B; generation and corpus period are
  confounded.
- Single author; no independent replication.
- LAP is a 20-sample frequency, and the 0.1 threshold is a convention.
