# Operationalizing Data Minimization for Privacy-Preserving LLM Prompting

- **Citation:** Jijie Zhou, Niloofar Mireshghallah and Tianshi Li (2025). arXiv 2510.03662 v1,
  4 October 2025 (the only version listed). A search result lists an ICLR 2026 poster page
  (https://iclr.cc/virtual/2026/poster/10007115), not opened; the arXiv page states no venue.
  Version read: v1, HTML.
- **Link:** https://arxiv.org/abs/2510.03662 (HTML read: https://arxiv.org/html/2510.03662v1)
- **Stream:** 09, rewrite blinding (questions 1 and 2)
- **Verified against source:** yes, 2026-11-22 (abstract, formal definition, search method,
  Table 2, the span-recovery audit and the appendix tables on direct prediction, read through a
  machine extraction of the first 100,000 of 167,250 characters of the HTML; Figure 3 not read)

## Question
For a given task and model, what is the least a user must disclose in a prompt for the model to
still do the task, and can models predict that minimum themselves?

## Data
Four datasets: ShareGPT (176 prompts) and WildChat (139), open-ended; MedQA (108) and CaseHOLD
(110), multiple choice. Nine target models from qwen2.5-0.5b to gpt-5, including
claude-3-7-sonnet and claude-sonnet-4.

## Method
- GPT-4o detects sensitive spans (ten categories), groups variants of one entity and writes an
  abstraction for each.
- Each span gets one action: RETAIN, ABSTRACT or REDACT, ordered by privacy.
- Utility: for multiple choice, the answer must be correct in all of five runs (items kept only
  if all nine models were correct on the unmasked input); for open-ended prompts, GPT-4o judges
  whether the minimised response covers the key points of the original response.
- Search: first freeze any span whose redaction and abstraction each break utility alone; then a
  priority-queue tree search from the most protective profile, relaxing one action at a time,
  returns the first profile that passes. Privacy is ordered by a distilled Qwen2.5-7B comparator
  (71% agreement with human labels, 89% on high-consensus items).
- Second experiment: models are asked to predict the minimal profile directly.

## Outcome variable and horizon
Share of spans redacted, abstracted or retained at the minimum; recovery rate of masked spans by
an attacker. No horizon.

## Result
Empirical findings.

- **Stronger models need less (Table 2, open-ended, redact / abstract / retain):** gpt-5
  85.7 / 8.6 / 5.7; gpt-4.1 82.6 / 9.9 / 7.6; claude-sonnet-4 74.8 / 11.2 / 14.0; qwen2.5-7b
  69.9 / 12.0 / 18.1; qwen2.5-0.5b 19.3 / 11.0 / 69.7. On the multiple-choice tasks the large
  models redact 91% to 98% of spans. The trend is not strictly monotone (exaone-deep-32b 60.4%).
- **Redaction protects better than abstraction.** Pooled recovery of masked spans by an
  attacker: 5.6% to 14.9% for abstractions, 2.7% to 7.7% for redactions. On WildChat, Hit@1 for
  names goes from 90.3 to 0.0, geolocation 89.8 to 2.2, occupation 85.4 to 8.0.
- **Models overshare when asked to minimise.** Asked directly, most models prefer abstraction to
  redaction (for example gpt-4.1 on MedQA: 0.20% redact, 98.46% abstract; claude-sonnet-4 on
  MedQA: 0.92% redact, 71.41% retain); gpt-5 and exaone redact more. The authors read this as a
  capability gap: models do not know what information they need for the task.
- **The minimum is model-specific;** the authors conclude that "model-specific predictors are
  needed". No transfer of a minimum from one model to another is reported.

## Look-ahead and memorisation
Not addressed. For the multiple-choice tasks the search oracle uses the correct answer to decide
whether a profile passes, so the minimum is fitted to the label. Verified fact about the method;
the paper does not discuss it as a risk.

## What it settles for us
- **Template design is a data-minimisation search.** Our template (EXP-0031) chose its fields by
  judgement. This paper gives a procedure: start from the most protective brief, relax one field
  at a time, keep the first brief at which the forecast still works. Its findings suggest that a
  strong PM needs fewer fields than a designer would guess, and that redacting a field protects
  better than coarsening it (our reading, transferred from prompts to a structured brief).
- **Do not ask the model which fields it needs.** Models overshare when asked; the minimum must
  be found by measurement.
- **The oracle needs a label, and the label must not be a remembered one.** For S2 the utility
  check must use episodes the PM cannot have memorised (post-cutoff or development episodes),
  otherwise the search keeps fields that help recall, not forecasting (our reading).

## Limits
- Prompts with personal information and short-answer tasks, not forecasts.
- The privacy order rests on a comparator with 71% agreement with humans.
- Open-ended utility is judged by GPT-4o against the model's own unmasked answer.
- Overshare percentages by task are in a figure not read.
