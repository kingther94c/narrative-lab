# Prompt Engineering Large Language Models' Forecasting Capabilities

- **Citation:** Philipp Schoenegger, Cameron R. Jones, Philip E. Tetlock and Barbara Mellers
  (2025). Working paper, arXiv 2506.01578, v1 of 2 June 2025 (the only version listed). No venue
  stated.
- **Link:** https://arxiv.org/abs/2506.01578
- **Stream:** 12, forecast prompting
- **Verified against source:** yes, 2026-11-22. Full text of v1 read (PDF, text extracted with
  macOS PDFKit): abstract, sections 1 to 4, Tables 1 to 9, Appendix A prompt texts for the
  self-consistency and Bayesian prompts. Figures read by caption only. The OSF pre-registration
  was not opened.

## Question
Do cheap prompt changes improve LLM forecasting accuracy? Study 1 tests 37 single-idea prompts
against a minimal control. Study 2 tests compound prompts, prompts written by vendors' automatic
prompt tools, and prompts from earlier forecasting papers, also on two reasoning models.

## Data
- 100 binary questions sampled from ForecastBench's 2024-12-08 set, resolving in December 2024.
  Sources: DBnomics, FRED, INFER, Manifold, Metaculus, Polymarket, Wikipedia, Yahoo Finance.
  Topics include conflict, economics, weather, elections, culture and technology.
- No company documents. Questions are short; no retrieval.
- Study 1 models: Claude 3.5 Sonnet, Claude 3.5 Haiku, GPT-4o, Llama 3.1 405B, temperature 0,
  at most 2,000 output tokens. Study 2 adds o1 and o1-mini at temperature 1, 4,000 tokens.
- Study 1 kept 3,636 to 3,771 forecasts per model after refusals (GPT-4o refused 4.32%).

## Method
- Control prompt: answer with a probability between 0% and 100%, formatted "Forecast: X%". Each
  treatment adds or changes one element, for example "Approach this question step-by-step,
  explaining your reasoning at each stage" (chain of thought).
- Prompts are classed before data collection by type (unguided reflection, framework,
  information, incentives) and by cognitive mode (analytical, intuitive, reference-based,
  dialectical).
- "Self-Consistency" here is one call that asks for three reasoning paths and the most
  consistent answer. It is not repeated sampling with aggregation.
- Pre-registered primary analysis: per forecast, Brier score of the treatment minus the control's
  for the same question and model; linear mixed model with prompt as fixed effect and random
  intercepts for question and model; estimated marginal means; Benjamini-Hochberg correction.
  Pre-registered secondary analysis: one-sample t-tests of the same differences, ignoring
  clustering.

## Outcome variable and horizon
Brier score of binary questions resolving within about one week to the end of 2024 after the
forecast date.

## Result
Empirical findings unless marked.

- **Base accuracy.** Mean Brier by model in Study 1: Sonnet 0.208, Haiku 0.214, GPT-4o 0.215,
  Llama 0.227. Study 2: o1 0.216, o1-mini 0.217, Sonnet 0.207, GPT-4o 0.208. Reasoning models
  were not more accurate on this set.
- **Study 1, primary model.** No prompt beats the control after correction. The best estimates
  are small: frequency-based reasoning -0.014, base rate first -0.011, chain of thought -0.011,
  step-back -0.011 (all adjusted p = 0.774). Two prompts are worse after correction: Bayesian
  reasoning +0.030 and propose-evaluate-select +0.033 (adjusted p < 0.001).
- **Study 1, secondary t-tests.** Frequency-based reasoning (-0.019, SD 0.114, n = 370), base
  rate first (-0.016) and step-back (-0.015) survive correction. Chain of thought is -0.016 with
  adjusted p = 0.086. Bayesian reasoning (+0.025) and propose-evaluate-select (+0.028) are worse.
- **Personas and aggregation inside one call.** Superforecasting persona (short) -0.001 (primary)
  and -0.006 (secondary), not significant. The one-call self-consistency prompt is +0.009 and
  +0.005, not significant; the authors read its sign as consistent with the harm from
  propose-evaluate-select.
- **Decisiveness.** Bayesian reasoning, propose-evaluate-select and chain of thought moved
  forecasts furthest from 50% (mean absolute distance 0.199, 0.175, 0.172, against 0.134 for the
  control).
- **Study 2.** Under the primary model nothing helps. The best estimates: all
  human-literature elements combined -0.009, frequency-based reasoning plus chain of thought
  -0.008, chain of thought plus "deep breath" -0.006, all elements -0.006, Anthropic and OpenAI
  prompt generators -0.004 and -0.003, superforecasting persona (long) -0.002, Halawi et al.'s
  scratchpad +0.003. A superforecaster-authored conditional odds-ratio prompt from ForecastBench
  is worse: +0.023 (adjusted p = 0.01). Under the t-tests six prompts improve before correction
  (about -0.011 to -0.017) and none after.
- **Reasoning models.** The authors report that effects on o1 and o1-mini were "largely
  identical"; no separate table for them was found in the text read.
- **Authors' conclusion (hypothesis about the field).** Prompt engineering has a minimal to
  nonexistent effect on LLM forecasting; retrieval, fine-tuning, agents or reinforcement learning
  are likelier routes.

## Look-ahead and memorisation
Handled by design: every model's stated training cutoff (October 2023 to July 2024) precedes the
December 2024 resolutions. Cutoffs are vendor-stated, not measured. Between-model comparisons are
avoided because cutoffs differ.

## What it settles for us
- **Expected size of a playbook effect (supports a low prior).** On general questions, single
  instructions move Brier by at most about 0.01 to 0.02 against a base near 0.21, and the moves do
  not survive a clustered, corrected test. Compound prompts that bundle the "good" elements do no
  better. A finance playbook should be expected to add little unless it brings information the
  model does not already use.
- **Base rates are the one element with support.** Reference-class prompts (base rate first,
  frequency-based reasoning) are the most consistent small gains. For S2 the matching element is a
  code-computed base rate of acceleration for the sector and quarter, stated as a sentence.
- **Some structure hurts.** Explicit Bayesian updating, propose-evaluate-select, and an expert
  odds-ratio protocol all raised Brier by 0.02 to 0.03. Elaborate reasoning protocols are not
  neutral and need their own arm.
- **Persona: drop.** The superforecaster persona had no effect.
- **Method to reuse.** Pre-registered per-item paired differences against one control, a
  mixed model with question and model effects, and Benjamini-Hochberg correction across arms. The
  per-item SD of Brier differences (about 0.07 to 0.17) gives a first power figure for S2.

## Limits
- 100 questions only; many are short-horizon data questions (FRED, weather) where reasoning has
  little to work on. No documents, so it does not test a checklist applied to a long text.
- Temperature 0 and one sample per prompt; refusals were dropped, not retried.
- Models are 2024 vintage; Claude Opus 5.5 is not tested.
- Brier only; calibration and resolution are not reported separately.
